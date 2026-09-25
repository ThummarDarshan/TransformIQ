import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.config.database import get_db
from app.auth.deps import get_current_user
from app.models.user import User, Organization, Workspace, ProjectMember, UserRole
from app.models.project import Project
from app.schemas.project import WorkspaceCreate, WorkspaceResponse, OrganizationCreate, OrganizationResponse, ApiResponse

ws_router = APIRouter(prefix="/workspaces", tags=["Workspaces"])
org_router = APIRouter(prefix="/organizations", tags=["Organizations"])

# Organizations
@org_router.get("", response_model=ApiResponse)
async def list_organizations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Lists organizations accessible to the current user (tenant isolation)."""
    if (current_user.role or "").upper() == UserRole.ADMIN.value:
        result = await db.execute(select(Organization))
        orgs = result.scalars().all()
    else:
        # Get organizations owned by user
        result = await db.execute(select(Organization).filter(Organization.owner_id == current_user.id))
        orgs = list(result.scalars().all())
        
        # Also include orgs where user is an active project member
        mem_projs = await db.execute(
            select(Project.workspace_id).join(ProjectMember, ProjectMember.project_id == Project.id).filter(ProjectMember.user_id == current_user.id)
        )
        ws_ids = mem_projs.scalars().all()
        if ws_ids:
            ws_orgs = await db.execute(select(Workspace.organization_id).filter(Workspace.id.in_(ws_ids)))
            org_ids = set(ws_orgs.scalars().all())
            existing_ids = {o.id for o in orgs}
            for oid in org_ids:
                if oid not in existing_ids:
                    o_res = await db.execute(select(Organization).filter(Organization.id == oid))
                    found = o_res.scalars().first()
                    if found:
                        orgs.append(found)

    return ApiResponse(
        success=True,
        data=[OrganizationResponse.model_validate(o).model_dump() for o in orgs]
    )

@org_router.post("", response_model=ApiResponse)
async def create_organization(
    req: OrganizationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    org_id = str(uuid.uuid4())
    org = Organization(
        id=org_id,
        name=req.name.strip(),
        slug=f"org-{org_id[:8]}",
        industry=req.industry.strip() if req.industry else "Enterprise Services",
        size=req.size,
        owner_id=current_user.id
    )
    db.add(org)
    await db.commit()
    await db.refresh(org)
    return ApiResponse(
        success=True,
        data=OrganizationResponse.model_validate(org).model_dump(),
        message="Organization created successfully"
    )

# Workspaces
@ws_router.get("", response_model=ApiResponse)
async def list_workspaces(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Lists workspaces accessible to the current user (tenant isolation)."""
    if (current_user.role or "").upper() == UserRole.ADMIN.value:
        result = await db.execute(select(Workspace))
        workspaces = result.scalars().all()
    else:
        # Get organizations owned by user
        org_res = await db.execute(select(Organization.id).filter(Organization.owner_id == current_user.id))
        owned_org_ids = org_res.scalars().all()
        
        ws_res = await db.execute(select(Workspace).filter(Workspace.organization_id.in_(owned_org_ids)))
        workspaces = list(ws_res.scalars().all())
        
        # Include workspaces where user is a project member
        mem_projs = await db.execute(
            select(Project.workspace_id).join(ProjectMember, ProjectMember.project_id == Project.id).filter(ProjectMember.user_id == current_user.id)
        )
        member_ws_ids = set(mem_projs.scalars().all())
        existing_ws_ids = {w.id for w in workspaces}
        for ws_id in member_ws_ids:
            if ws_id not in existing_ws_ids:
                single_ws = await db.execute(select(Workspace).filter(Workspace.id == ws_id))
                found = single_ws.scalars().first()
                if found:
                    workspaces.append(found)

    return ApiResponse(
        success=True,
        data=[WorkspaceResponse.model_validate(w).model_dump() for w in workspaces]
    )

@ws_router.post("", response_model=ApiResponse)
async def create_workspace(
    req: WorkspaceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Verify user owns the target organization or is admin
    if (current_user.role or "").upper() != UserRole.ADMIN.value:
        org_res = await db.execute(
            select(Organization).filter(Organization.id == req.organization_id, Organization.owner_id == current_user.id)
        )
        if not org_res.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You do not own or administer this organization."
            )

    ws = Workspace(
        id=str(uuid.uuid4()),
        name=req.name.strip(),
        description=req.description,
        organization_id=req.organization_id
    )
    db.add(ws)
    await db.commit()
    await db.refresh(ws)
    return ApiResponse(
        success=True,
        data=WorkspaceResponse.model_validate(ws).model_dump(),
        message="Workspace created successfully"
    )
