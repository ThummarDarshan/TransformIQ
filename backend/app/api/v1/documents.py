import os
import uuid
import shutil
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.config.database import get_db
from app.config.settings import settings
from app.auth.deps import get_current_user, require_project_permission, get_user_project_role, record_audit_log
from app.auth.permissions import Permission, has_permission
from app.models.user import User
from app.models.project import Project, Document, DocumentChunk, BusinessContext
from app.schemas.project import ApiResponse
from pydantic import BaseModel
from app.documents.extractor import extract_text_from_file, extract_text_from_url, chunk_text

router = APIRouter(prefix="/documents", tags=["Documents"])

class IngestUrlRequest(BaseModel):
    project_id: str
    url: str

@router.get("/project/{project_id}", response_model=ApiResponse)
async def list_project_documents(
    project_id: str,
    project: Project = Depends(require_project_permission(Permission.DOCUMENT_VIEW)),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Document).filter(Document.project_id == project.id).order_by(Document.created_at.desc()))
    docs = result.scalars().all()
    
    data = []
    for d in docs:
        data.append({
            "id": d.id,
            "filename": d.filename,
            "file_type": d.file_type,
            "file_size": d.file_size,
            "summary": d.summary,
            "status": d.status,
            "created_at": d.created_at
        })
    return ApiResponse(success=True, data=data, message=f"Found {len(data)} documents")

@router.get("/{document_id}", response_model=ApiResponse)
async def get_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    doc_res = await db.execute(select(Document).filter(Document.id == document_id))
    doc = doc_res.scalars().first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        
    role = await get_user_project_role(doc.project_id, current_user, db)
    if not role or not has_permission(role, Permission.DOCUMENT_VIEW):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied: You do not have permission to view this document.")
        
    return ApiResponse(
        success=True,
        data={
            "id": doc.id,
            "project_id": doc.project_id,
            "filename": doc.filename,
            "file_type": doc.file_type,
            "file_size": doc.file_size,
            "summary": doc.summary,
            "status": doc.status,
            "created_at": doc.created_at
        }
    )

@router.post("/ingest-url", response_model=ApiResponse)
async def ingest_url_document(
    payload: IngestUrlRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    project_id = payload.project_id
    url = payload.url.strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid URL format. URL must start with http:// or https://"
        )
        
    extracted_text, pages = extract_text_from_url(url)
    chunks = chunk_text(extracted_text)
    
    doc_id = str(uuid.uuid4())
    summary = f"Scraped & indexed {len(extracted_text)} characters across {len(chunks)} contextual chunks from Web/BRD URL: {url}"
    
    document = Document(
        id=doc_id,
        project_id=project_id,
        filename=url,
        file_type="url",
        file_size=len(extracted_text.encode('utf-8')),
        storage_path=url,
        extracted_text=extracted_text,
        summary=summary,
        status="PROCESSED"
    )
    db.add(document)
    
    for idx, c in enumerate(chunks):
        chunk_obj = DocumentChunk(
            id=str(uuid.uuid4()),
            document_id=doc_id,
            chunk_index=idx,
            content=c,
            page_number=1,
            metadata_json={"source": url, "chunk_index": idx}
        )
        db.add(chunk_obj)
        
    # Update project business context
    ctx_res = await db.execute(select(BusinessContext).filter(BusinessContext.project_id == project_id))
    ctx = ctx_res.scalars().first()
    if ctx:
        current_summary = ctx.summary or ""
        ctx.summary = f"{current_summary}\n\nWeb URL Context ({url}):\n{extracted_text[:400]}..."
        
    await record_audit_log(
        db=db,
        user=current_user,
        action="INGEST_URL_DOCUMENT",
        resource_type="DOCUMENT",
        resource_id=doc_id,
        project_id=project_id,
        details=f"{current_user.full_name} ingested URL context from {url}",
        request=request
    )
    
    await db.commit()
    
    return ApiResponse(
        success=True,
        data={
            "id": doc_id,
            "filename": url,
            "file_type": "url",
            "file_size": len(extracted_text.encode('utf-8')),
            "chunks_count": len(chunks),
            "summary": summary
        },
        message="Web URL reference content analyzed and indexed into AI context successfully"
    )

@router.post("/upload/{project_id}", response_model=ApiResponse)
@router.post("/upload", response_model=ApiResponse)
async def upload_document(
    project_id: Optional[str] = None,
    request: Request = None,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    pid = project_id or request.query_params.get("project_id")
    if not pid:
        raise HTTPException(status_code=400, detail="Missing project_id parameter")
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_ext = os.path.splitext(file.filename)[1].lower().replace('.', '')
    if file_ext not in ["pdf", "docx", "pptx", "txt", "doc", "ppt", "md"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format. Please upload PDF, Word, PowerPoint, or text files."
        )
        
    saved_filename = f"{pid}_{str(uuid.uuid4())[:8]}_{file.filename}"
    saved_path = os.path.join(settings.UPLOAD_DIR, saved_filename)
    
    with open(saved_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    file_size = os.path.getsize(saved_path)
    extracted_text, pages = extract_text_from_file(saved_path, file.filename)
    chunks = chunk_text(extracted_text)
    
    doc_id = str(uuid.uuid4())
    summary = f"Extracted {len(extracted_text)} characters across {len(chunks)} contextual chunks from {file.filename}."
    
    document = Document(
        id=doc_id,
        project_id=pid,
        filename=file.filename,
        file_type=file_ext,
        file_size=file_size,
        storage_path=saved_path,
        extracted_text=extracted_text,
        summary=summary,
        status="PROCESSED"
    )
    db.add(document)
    
    for idx, c in enumerate(chunks):
        chunk_obj = DocumentChunk(
            id=str(uuid.uuid4()),
            document_id=doc_id,
            chunk_index=idx,
            content=c,
            page_number=1,
            metadata_json={"source": file.filename, "chunk_index": idx}
        )
        db.add(chunk_obj)
        
    # Update project business context
    ctx_res = await db.execute(select(BusinessContext).filter(BusinessContext.project_id == project_id))
    ctx = ctx_res.scalars().first()
    if ctx:
        current_summary = ctx.summary or ""
        ctx.summary = f"{current_summary}\n\nDocument Grounding ({file.filename}):\n{extracted_text[:400]}..."
        
    await record_audit_log(
        db=db,
        user=current_user,
        action="UPLOAD_DOCUMENT",
        resource_type="DOCUMENT",
        resource_id=doc_id,
        project_id=project_id,
        details=f"{current_user.full_name} uploaded {file.filename} ({file_size} bytes)",
        request=request
    )
    
    await db.commit()
    
    return ApiResponse(
        success=True,
        data={
            "id": doc_id,
            "filename": file.filename,
            "file_type": file_ext,
            "file_size": file_size,
            "chunks_count": len(chunks),
            "summary": summary
        },
        message="Document uploaded and processed into AI context successfully"
    )
