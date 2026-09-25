import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.config.database import get_db
from app.auth.deps import get_current_user, verify_project_access
from app.models.user import User
from app.models.project import Project
from app.models.collaboration import Comment, Version, AuditLog, Notification, Approval
from app.schemas.project import ApiResponse

router = APIRouter(prefix="/collaboration", tags=["Team Collaboration & Governance"])

class CommentCreate(BaseModel):
    section: str
    content: str
    mentions: List[str] = []

@router.get("/project/{project_id}/comments", response_model=ApiResponse)
async def list_comments(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    project = await verify_project_access(project_id, current_user, db)
    res = await db.execute(select(Comment).filter(Comment.project_id == project.id).order_by(Comment.created_at.desc()))
    comments = res.scalars().all()
    
    data = []
    for c in comments:
        u_res = await db.execute(select(User).filter(User.id == c.author_id))
        user = u_res.scalars().first()
        data.append({
            "id": c.id,
            "author_id": c.author_id,
            "author_name": user.full_name if user else "Team Member",
            "section": c.section,
            "content": c.content,
            "mentions": c.mentions,
            "resolved": c.resolved,
            "created_at": c.created_at
        })
    return ApiResponse(success=True, data=data)

@router.post("/project/{project_id}/comments", response_model=ApiResponse)
async def create_comment(
    project_id: str,
    req: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    project = await verify_project_access(project_id, current_user, db)
    
    now = datetime.utcnow()
    comment = Comment(
        id=str(uuid.uuid4()),
        project_id=project.id,
        author_id=current_user.id,
        section=req.section,
        content=req.content,
        mentions=req.mentions,
        resolved=False,
        created_at=now
    )
    db.add(comment)
    
    # Audit log
    db.add(AuditLog(
        id=str(uuid.uuid4()),
        project_id=project.id,
        user_id=current_user.id,
        user_name=current_user.full_name,
        action="POSTED_COMMENT",
        details=f"Commented on {req.section}: {req.content[:60]}...",
        created_at=now
    ))
    
    await db.commit()
    return ApiResponse(
        success=True,
        data={
            "id": comment.id,
            "author_id": current_user.id,
            "author_name": current_user.full_name,
            "section": comment.section,
            "content": comment.content,
            "mentions": comment.mentions,
            "resolved": comment.resolved,
            "created_at": now.isoformat()
        },
        message="Comment posted successfully"
    )

@router.get("/project/{project_id}/approvals", response_model=ApiResponse)
async def list_approvals(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    project = await verify_project_access(project_id, current_user, db)
    res = await db.execute(select(Approval).filter(Approval.project_id == project.id).order_by(Approval.created_at.desc()))
    approvals = res.scalars().all()
    return ApiResponse(
        success=True,
        data=[{
            "id": a.id,
            "artifact_type": a.artifact_type,
            "status": a.status,
            "requested_by": a.requested_by,
            "reviewed_by": a.reviewed_by,
            "comments": a.comments,
            "decision_date": a.decision_date,
            "created_at": a.created_at
        } for a in approvals]
    )

class ApprovalRequest(BaseModel):
    project_id: str
    artifact_type: str = "FINAL_BLUEPRINT"
    decision: str = "APPROVED"
    comments: Optional[str] = "Approved by Manager"

@router.post("/approvals", response_model=ApiResponse)
async def create_or_update_approval(
    req: ApprovalRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    project = await verify_project_access(req.project_id, current_user, db)
    
    appr = Approval(
        id=str(uuid.uuid4()),
        project_id=project.id,
        artifact_type=req.artifact_type,
        status=req.decision,
        requested_by=current_user.full_name or current_user.email,
        reviewed_by=current_user.full_name or current_user.email,
        comments=req.comments,
        decision_date=datetime.utcnow()
    )
    db.add(appr)
    
    # Audit log
    db.add(AuditLog(
        id=str(uuid.uuid4()),
        project_id=project.id,
        user_id=current_user.id,
        user_name=current_user.full_name,
        action=f"APPROVAL_{req.decision}",
        details=f"{current_user.full_name} set {req.artifact_type} approval status to {req.decision}: {req.comments}"
    ))
    
    await db.commit()
    return ApiResponse(
        success=True,
        data={
            "id": appr.id,
            "project_id": appr.project_id,
            "artifact_type": appr.artifact_type,
            "status": appr.status,
            "reviewed_by": appr.reviewed_by,
            "comments": appr.comments
        },
        message="Approval processed successfully"
    )

@router.get("/project/{project_id}/versions", response_model=ApiResponse)
async def list_versions(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    project = await verify_project_access(project_id, current_user, db)
    res = await db.execute(select(Version).filter(Version.project_id == project.id).order_by(Version.version_number.desc()))
    versions = res.scalars().all()
    
    return ApiResponse(
        success=True,
        data=[{
            "id": v.id,
            "version_number": v.version_number,
            "artifact_type": v.artifact_type,
            "change_summary": v.change_summary,
            "author_name": v.author_name,
            "created_at": v.created_at
        } for v in versions]
    )

@router.get("/project/{project_id}/audit-logs", response_model=ApiResponse)
async def list_audit_logs(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    project = await verify_project_access(project_id, current_user, db)
    res = await db.execute(select(AuditLog).filter(AuditLog.project_id == project.id).order_by(AuditLog.created_at.desc()).limit(25))
    logs = res.scalars().all()
    
    return ApiResponse(
        success=True,
        data=[{
            "id": l.id,
            "user_name": l.user_name or "System AI",
            "action": l.action,
            "details": l.details,
            "created_at": l.created_at
        } for l in logs]
    )

@router.get("/notifications", response_model=ApiResponse)
async def get_notifications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(select(Notification).filter(Notification.user_id == current_user.id).order_by(Notification.created_at.desc()).limit(15))
    notifs = res.scalars().all()
    return ApiResponse(
        success=True,
        data=[{
            "id": n.id,
            "title": n.title,
            "message": n.message,
            "type": n.type,
            "link": n.link,
            "is_read": n.is_read,
            "created_at": n.created_at
        } for n in notifs]
    )
