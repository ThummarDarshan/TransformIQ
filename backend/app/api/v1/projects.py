import uuid
import re
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Body, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel, EmailStr
from app.config.database import get_db
from app.auth.deps import get_current_user, require_project_permission, get_user_project_role, record_audit_log
from app.auth.permissions import Permission, has_permission
from app.models.user import User, Workspace, ProjectMember, Organization, UserRole
from app.models.project import Project, ProjectStatus, BusinessContext
from app.models.planning import TransformationScore
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, ApiResponse
from app.ai import orchestrator

router = APIRouter(prefix="/projects", tags=["Projects"])

class AddMemberRequest(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None
    role: str = UserRole.MEMBER.value

@router.get("", response_model=ApiResponse)
async def list_projects(
    workspace_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Admin can view all projects in the system/org
    if current_user.role in [UserRole.ADMIN.value, "ADMIN"]:
        query = select(Project)
        if workspace_id:
            query = query.filter(Project.workspace_id == workspace_id)
        result = await db.execute(query.order_by(Project.created_at.desc()))
        projects = result.scalars().all()
    else:
        # Get projects where user is explicitly a member or belongs to workspace/org
        member_projs_res = await db.execute(
            select(ProjectMember.project_id).filter(ProjectMember.user_id == current_user.id)
        )
        allowed_ids = set(member_projs_res.scalars().all())
        
        query = select(Project)
        if workspace_id:
            query = query.filter(Project.workspace_id == workspace_id)
        result = await db.execute(query.order_by(Project.created_at.desc()))
        all_projs = result.scalars().all()
        
        # If user is in default workspace or project member
        projects = [p for p in all_projs if p.id in allowed_ids or current_user.role in [UserRole.PROJECT_OWNER.value, UserRole.MANAGER.value]]
        
    data = []
    for p in projects:
        score_res = await db.execute(select(TransformationScore).filter(TransformationScore.project_id == p.id))
        score = score_res.scalars().first()
        p_dict = ProjectResponse.model_validate(p).model_dump()
        p_dict["overall_score"] = score.overall_score if score else 0
        p_dict["ai_readiness"] = score.ai_readiness if score else 0
        data.append(p_dict)
        
    return ApiResponse(
        success=True,
        data=data,
        message=f"Found {len(data)} projects"
    )

@router.post("", response_model=ApiResponse)
async def create_project(
    req: ProjectCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    slug = re.sub(r'[^a-z0-9]+', '-', req.name.lower()).strip('-') + f"-{str(uuid.uuid4())[:6]}"
    project_id = str(uuid.uuid4())
    
    # Set workspace if not provided
    ws_id = req.workspace_id
    if not ws_id or ws_id == "default-ws":
        ws_res = await db.execute(select(Workspace))
        ws = ws_res.scalars().first()
        if not ws:
            # Create default workspace
            org_res = await db.execute(select(Organization))
            org = org_res.scalars().first()
            if not org:
                org = Organization(
                    id=str(uuid.uuid4()),
                    name="TransformIQ Enterprise",
                    slug="transformiq-enterprise",
                    owner_id=current_user.id
                )
                db.add(org)
                await db.flush()
                
            ws = Workspace(
                id=str(uuid.uuid4()),
                name="Default Transformation Workspace",
                organization_id=org.id
            )
            db.add(ws)
            await db.flush()
        ws_id = ws.id
        
    project = Project(
        id=project_id,
        name=req.name,
        slug=slug,
        description=req.description,
        workspace_id=ws_id,
        status=ProjectStatus.DISCOVERY.value,
        industry=req.industry,
        organization_size=req.organization_size,
        business_objective=req.business_objective,
        business_problem=req.business_problem,
        current_systems=req.current_systems,
        expected_outcome=req.expected_outcome,
        constraints=req.constraints,
        budget=req.budget,
        timeline_months=req.timeline_months
    )
    db.add(project)
    
    # Add creator as PROJECT_OWNER
    member = ProjectMember(
        id=str(uuid.uuid4()),
        project_id=project_id,
        user_id=current_user.id,
        role=UserRole.PROJECT_OWNER.value
    )
    db.add(member)
    
    # Create initial business context
    ctx = BusinessContext(
        id=str(uuid.uuid4()),
        project_id=project_id,
        summary=f"Project {req.name} in {req.industry} targeting {req.business_objective}."
    )
    db.add(ctx)
    
    await record_audit_log(
        db=db,
        user=current_user,
        action="CREATE_PROJECT",
        resource_type="PROJECT",
        resource_id=project_id,
        project_id=project_id,
        details=f"{current_user.full_name} created project '{project.name}' in {project.industry}",
        request=request
    )
    
    await db.commit()
    await db.refresh(project)
    
    return ApiResponse(
        success=True,
        data=ProjectResponse.model_validate(project).model_dump(),
        message="Project created successfully"
    )

@router.get("/{project_id}", response_model=ApiResponse)
async def get_project_details(
    project_id: str,
    project: Project = Depends(require_project_permission(Permission.PROJECT_VIEW)),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    score_res = await db.execute(select(TransformationScore).filter(TransformationScore.project_id == project.id))
    score = score_res.scalars().first()
    
    user_role = await get_user_project_role(project.id, current_user, db)
    
    p_dict = ProjectResponse.model_validate(project).model_dump()
    p_dict["overall_score"] = score.overall_score if score else 0
    p_dict["ai_readiness"] = score.ai_readiness if score else 0
    p_dict["automation_potential"] = score.automation_potential if score else 0
    p_dict["current_user_project_role"] = user_role or current_user.role
    
    return ApiResponse(
        success=True,
        data=p_dict,
        message="Project details retrieved"
    )

@router.get("/{project_id}/members", response_model=ApiResponse)
async def list_project_members(
    project_id: str,
    project: Project = Depends(require_project_permission(Permission.PROJECT_VIEW)),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    members_res = await db.execute(
        select(ProjectMember).filter(ProjectMember.project_id == project.id)
    )
    members = members_res.scalars().all()
    
    data = []
    for m in members:
        user_res = await db.execute(select(User).filter(User.id == m.user_id))
        u = user_res.scalars().first()
        if u:
            data.append({
                "membership_id": m.id,
                "user_id": u.id,
                "email": u.email,
                "full_name": u.full_name,
                "project_role": m.role,
                "system_role": u.role,
                "joined_at": m.created_at
            })
            
    return ApiResponse(success=True, data=data, message=f"Found {len(data)} project members")

@router.post("/{project_id}/members", response_model=ApiResponse)
async def add_project_member(
    project_id: str,
    payload: AddMemberRequest,
    request: Request,
    project: Project = Depends(require_project_permission(Permission.TEAM_MANAGE)),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    target_user = None
    if payload.user_id:
        u_res = await db.execute(select(User).filter(User.id == payload.user_id))
        target_user = u_res.scalars().first()
    elif payload.email:
        u_res = await db.execute(select(User).filter(User.email == payload.email))
        target_user = u_res.scalars().first()
        
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User account not found to add as member.")
        
    # Check if already member
    existing_res = await db.execute(
        select(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == target_user.id
        )
    )
    existing = existing_res.scalars().first()
    if existing:
        existing.role = payload.role.upper()
        member_obj = existing
    else:
        member_obj = ProjectMember(
            id=str(uuid.uuid4()),
            project_id=project_id,
            user_id=target_user.id,
            role=payload.role.upper()
        )
        db.add(member_obj)
        
    await record_audit_log(
        db=db,
        user=current_user,
        action="ASSIGN_PROJECT_MEMBER",
        resource_type="PROJECT_MEMBER",
        resource_id=target_user.id,
        project_id=project_id,
        details=f"{current_user.full_name} assigned {target_user.email} as {payload.role.upper()} on project {project.name}",
        request=request
    )
    
    await db.commit()
    return ApiResponse(
        success=True,
        data={"user_id": target_user.id, "email": target_user.email, "role": payload.role.upper()},
        message=f"{target_user.full_name} added to project with role {payload.role.upper()}"
    )

@router.delete("/{project_id}", response_model=ApiResponse)
async def delete_project(
    project_id: str,
    request: Request,
    project: Project = Depends(require_project_permission(Permission.PROJECT_DELETE)),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await record_audit_log(
        db=db,
        user=current_user,
        action="DELETE_PROJECT",
        resource_type="PROJECT",
        resource_id=project_id,
        project_id=project_id,
        details=f"{current_user.full_name} deleted project {project.name}",
        request=request
    )
    await db.delete(project)
    await db.commit()
    return ApiResponse(
        success=True,
        message="Project deleted successfully"
    )
