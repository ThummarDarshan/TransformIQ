import os
import re
import uuid
import shutil
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.config.database import get_db
from app.config.settings import settings
from app.auth.deps import get_current_user, require_project_permission, get_user_project_role, record_audit_log, verify_project_access
from app.auth.permissions import Permission, has_permission
from app.auth.rate_limiter import rate_limit
from app.models.user import User
from app.models.project import Project, Document, DocumentChunk, BusinessContext
from app.models.provenance import SourceEvidence, SourceType
from app.schemas.project import ApiResponse
from pydantic import BaseModel, Field
from app.documents.extractor import extract_text_from_file, extract_text_from_url, chunk_text, chunk_document_with_metadata

router = APIRouter(prefix="/documents", tags=["Documents & Knowledge Ingestion"])

ALLOWED_EXTENSIONS = {"pdf", "docx", "pptx", "txt", "doc", "ppt", "md"}

class IngestUrlRequest(BaseModel):
    project_id: str
    url: str = Field(..., min_length=4, max_length=2000)

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

@router.delete("/{document_id}", response_model=ApiResponse)
async def delete_document(
    document_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    doc_res = await db.execute(select(Document).filter(Document.id == document_id))
    doc = doc_res.scalars().first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        
    role = await get_user_project_role(doc.project_id, current_user, db)
    if not role or not has_permission(role, Permission.DOCUMENT_DELETE):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied: You do not have permission to delete this document.")

    # Secure cleanup of stored file
    if doc.storage_path and not doc.storage_path.startswith("http"):
        abs_upload_dir = os.path.abspath(settings.UPLOAD_DIR)
        abs_file_path = os.path.abspath(doc.storage_path)
        # Prevent arbitrary path deletion
        if abs_file_path.startswith(abs_upload_dir) and os.path.exists(abs_file_path):
            try:
                os.remove(abs_file_path)
            except Exception:
                pass

    await record_audit_log(
        db=db,
        user=current_user,
        action="DELETE_DOCUMENT",
        resource_type="DOCUMENT",
        resource_id=doc.id,
        project_id=doc.project_id,
        details=f"{current_user.full_name} deleted document '{doc.filename}'",
        request=request
    )

    await db.delete(doc)
    await db.commit()

    return ApiResponse(
        success=True,
        data={"deleted": True, "id": document_id},
        message="Document and knowledge chunks removed successfully"
    )

@router.post("/ingest-url", response_model=ApiResponse)
async def ingest_url_document(
    payload: IngestUrlRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _limiter: None = Depends(rate_limit("website_ingest", settings.WEBSITE_INGEST_RATE_LIMIT_PER_MINUTE))
):
    project_id = payload.project_id
    
    # 1. Authorize project upload permission
    role = await get_user_project_role(project_id, current_user, db)
    if not role or not has_permission(role, Permission.DOCUMENT_UPLOAD):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You do not have permission to ingest web resources into this project."
        )

    url = payload.url.strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid URL format. URL must start with http:// or https://"
        )
        
    # Extract text with structured per-page metadata
    extracted_text, pages = extract_text_from_url(url)
    if extracted_text.startswith("URL Security Block:"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=extracted_text
        )

    # Count existing source evidence to give clean sequential source codes (e.g. SRC-001, SRC-002)
    ev_count_res = await db.execute(select(SourceEvidence).filter(SourceEvidence.project_id == project_id))
    existing_ev_count = len(ev_count_res.scalars().all())

    structured_chunks = chunk_document_with_metadata(
        full_text=extracted_text,
        pages_or_slides=pages,
        chunk_size=settings.RAG_CHUNK_SIZE,
        overlap=settings.RAG_CHUNK_OVERLAP,
        source_prefix="SRC"
    )
    
    doc_id = str(uuid.uuid4())
    summary = f"Scraped & indexed {len(extracted_text)} characters across {len(structured_chunks)} contextual chunks from Web/BRD URL: {url}"
    
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
    
    for idx, sc in enumerate(structured_chunks):
        chunk_id = str(uuid.uuid4())
        chunk_code = f"SRC-{(existing_ev_count + idx + 1):03d}"
        
        chunk_obj = DocumentChunk(
            id=chunk_id,
            document_id=doc_id,
            chunk_index=idx,
            content=sc["content"],
            page_number=sc.get("page_number", 1),
            metadata_json={
                "source": url,
                "source_code": chunk_code,
                "chunk_index": idx,
                "section_heading": sc.get("section_heading", "Web Ingestion")
            }
        )
        db.add(chunk_obj)
        
        # Canonical Source Evidence
        evidence = SourceEvidence(
            id=str(uuid.uuid4()),
            source_code=chunk_code,
            project_id=project_id,
            document_id=doc_id,
            chunk_id=chunk_id,
            document_name=url,
            source_type=SourceType.WEB_URL.value,
            page_number=sc.get("page_number", 1),
            section_heading=sc.get("section_heading", "Web Content"),
            paragraph_number=sc.get("paragraph_number", idx + 1),
            start_offset=sc.get("start_offset", 0),
            end_offset=sc.get("end_offset", len(sc["content"])),
            exact_text=sc["exact_text"],
            source_url=url,
            metadata_json={"url": url, "chunk_index": idx}
        )
        db.add(evidence)
        
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
            "chunks_count": len(structured_chunks),
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
    db: AsyncSession = Depends(get_db),
    _limiter: None = Depends(rate_limit("upload", settings.UPLOAD_RATE_LIMIT_PER_MINUTE))
):
    pid = project_id or request.query_params.get("project_id")
    if not pid:
        raise HTTPException(status_code=400, detail="Missing project_id parameter")

    # Verify project permissions
    role = await get_user_project_role(pid, current_user, db)
    if not role or not has_permission(role, Permission.DOCUMENT_UPLOAD):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You do not have permission to upload documents to this project."
        )

    # Sanitize and validate filename & extension
    raw_filename = file.filename or "uploaded_document.pdf"
    base_name = os.path.basename(raw_filename)
    # Remove dangerous traversal or non-alphanumeric characters
    clean_filename = re.sub(r'[^a-zA-Z0-9._-]', '_', base_name)
    file_ext = os.path.splitext(clean_filename)[1].lower().replace('.', '')
    
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '.{file_ext}'. Please upload PDF, Word, PowerPoint, or text files."
        )

    abs_upload_dir = os.path.abspath(settings.UPLOAD_DIR)
    os.makedirs(abs_upload_dir, exist_ok=True)
    
    # Store with secure UUID prefix to prevent collisions and path traversal
    saved_filename = f"{uuid.uuid4().hex}_{clean_filename}"
    saved_path = os.path.join(abs_upload_dir, saved_filename)
    
    # Enforce stream read size limit
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    bytes_read = 0
    
    try:
        with open(saved_path, "wb") as buffer:
            while True:
                chunk = await file.read(64 * 1024)  # 64 KB chunks
                if not chunk:
                    break
                bytes_read += len(chunk)
                if bytes_read > max_bytes:
                    buffer.close()
                    if os.path.exists(saved_path):
                        os.remove(saved_path)
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"File size exceeds maximum allowed limit of {settings.MAX_UPLOAD_SIZE_MB}MB."
                    )
                buffer.write(chunk)
    except HTTPException:
        raise
    except Exception as e:
        if os.path.exists(saved_path):
            os.remove(saved_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to securely save uploaded file: {str(e)}"
        )

    # Validate file contents and magic byte signatures
    extracted_text, pages = extract_text_from_file(saved_path, clean_filename)
    if extracted_text.startswith("Document processing security block:"):
        if os.path.exists(saved_path):
            os.remove(saved_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=extracted_text
        )

    # Count existing source evidence to give clean sequential source codes (e.g. SRC-001, SRC-002)
    ev_count_res = await db.execute(select(SourceEvidence).filter(SourceEvidence.project_id == pid))
    existing_ev_count = len(ev_count_res.scalars().all())

    structured_chunks = chunk_document_with_metadata(
        full_text=extracted_text,
        pages_or_slides=pages,
        chunk_size=settings.RAG_CHUNK_SIZE,
        overlap=settings.RAG_CHUNK_OVERLAP,
        source_prefix="SRC"
    )
    
    doc_id = str(uuid.uuid4())
    summary = f"Extracted {len(extracted_text)} characters across {len(structured_chunks)} contextual chunks from {clean_filename}."
    
    document = Document(
        id=doc_id,
        project_id=pid,
        filename=clean_filename,
        file_type=file_ext,
        file_size=bytes_read,
        storage_path=saved_path,
        extracted_text=extracted_text,
        summary=summary,
        status="PROCESSED"
    )
    db.add(document)
    
    # Map extension to SourceType
    src_type_map = {
        "pdf": SourceType.DOCUMENT_PDF.value,
        "docx": SourceType.DOCUMENT_DOCX.value,
        "doc": SourceType.DOCUMENT_DOCX.value,
        "pptx": SourceType.DOCUMENT_PPTX.value,
        "ppt": SourceType.DOCUMENT_PPTX.value,
        "txt": SourceType.DOCUMENT_TXT.value,
        "md": SourceType.DOCUMENT_TXT.value
    }
    stype = src_type_map.get(file_ext, SourceType.DOCUMENT_PDF.value)

    for idx, sc in enumerate(structured_chunks):
        chunk_id = str(uuid.uuid4())
        chunk_code = f"SRC-{(existing_ev_count + idx + 1):03d}"
        
        chunk_obj = DocumentChunk(
            id=chunk_id,
            document_id=doc_id,
            chunk_index=idx,
            content=sc["content"],
            page_number=sc.get("page_number", 1),
            metadata_json={
                "source": clean_filename,
                "source_code": chunk_code,
                "chunk_index": idx,
                "page_number": sc.get("page_number", 1),
                "section_heading": sc.get("section_heading")
            }
        )
        db.add(chunk_obj)
        
        # Create canonical SourceEvidence
        evidence = SourceEvidence(
            id=str(uuid.uuid4()),
            source_code=chunk_code,
            project_id=pid,
            document_id=doc_id,
            chunk_id=chunk_id,
            document_name=clean_filename,
            source_type=stype,
            page_number=sc.get("page_number", 1),
            section_heading=sc.get("section_heading", f"Page {sc.get('page_number', 1)} Content"),
            paragraph_number=sc.get("paragraph_number", idx + 1),
            start_offset=sc.get("start_offset", 0),
            end_offset=sc.get("end_offset", len(sc["content"])),
            exact_text=sc["exact_text"],
            metadata_json={"filename": clean_filename, "file_ext": file_ext, "chunk_index": idx}
        )
        db.add(evidence)
        
    # Update project business context
    ctx_res = await db.execute(select(BusinessContext).filter(BusinessContext.project_id == pid))
    ctx = ctx_res.scalars().first()
    if ctx:
        current_summary = ctx.summary or ""
        ctx.summary = f"{current_summary}\n\nDocument Grounding ({clean_filename}):\n{extracted_text[:400]}..."
        
    await record_audit_log(
        db=db,
        user=current_user,
        action="UPLOAD_DOCUMENT",
        resource_type="DOCUMENT",
        resource_id=doc_id,
        project_id=pid,
        details=f"{current_user.full_name} uploaded {clean_filename} ({bytes_read} bytes) with {len(structured_chunks)} source evidence citations",
        request=request
    )
    
    await db.commit()
    
    return ApiResponse(
        success=True,
        data={
            "id": doc_id,
            "filename": clean_filename,
            "file_type": file_ext,
            "file_size": bytes_read,
            "chunks_count": len(structured_chunks),
            "summary": summary
        },
        message="Document uploaded, validated, and processed into AI context successfully with traceable source citations"
    )
