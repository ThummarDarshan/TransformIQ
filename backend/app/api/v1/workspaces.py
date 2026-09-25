import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.config.database import get_db
from app.auth.deps import get_current_user
from app.models.user import User, Organization, Workspace
from app.schemas.project import WorkspaceCreate, WorkspaceResponse, OrganizationCreate, OrganizationResponse, ApiResponse

ws_router = APIRouter(prefix="/workspaces", tags=["Workspaces"])
org_router = APIRouter(prefix="/organizations", tags=["Organizations"])

# Organizations
@org_router.get("", response_model=ApiResponse)
async def list_organizations(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Organization))
    orgs = result.scalars().all()
    return ApiResponse(
        success=True,
        data=[OrganizationResponse.model_validate(o).model_dump() for o in orgs]
    )

@org_router.post("", response_model=ApiResponse)
async def create_organization(req: OrganizationCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    org_id = str(uuid.uuid4())
    org = Organization(
        id=org_id,
        name=req.name,
        slug=f"org-{org_id[:8]}",
        industry=req.industry,
        size=req.size,
        owner_id=current_user.id
    )
    db.add(org)
    await db.commit()
    await db.refresh(org)
    return ApiResponse(success=True, data=OrganizationResponse.model_validate(org).model_dump())

# Workspaces
@ws_router.get("", response_model=ApiResponse)
async def list_workspaces(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Workspace))
    workspaces = result.scalars().all()
    return ApiResponse(
        success=True,
        data=[WorkspaceResponse.model_validate(w).model_dump() for w in workspaces]
    )

@ws_router.post("", response_model=ApiResponse)
async def create_workspace(req: WorkspaceCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    ws = Workspace(
        id=str(uuid.uuid4()),
        name=req.name,
        description=req.description,
        organization_id=req.organization_id
    )
    db.add(ws)
    await db.commit()
    await db.refresh(ws)
    return ApiResponse(success=True, data=WorkspaceResponse.model_validate(ws).model_dump())
