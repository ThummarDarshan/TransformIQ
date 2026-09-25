import uuid
from datetime import datetime
from typing import Optional, List, Union
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.config.database import get_db
from app.auth.security import decode_access_token
from app.models.user import User, UserRole, Organization, Workspace, ProjectMember
from app.models.project import Project
from app.models.collaboration import AuditLog
from app.auth.permissions import Permission, ROLE_PERMISSIONS, has_permission

security_scheme = HTTPBearer(auto_error=False)

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials are required.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: str = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed token payload.",
        )
        
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account does not exist or has been deactivated.",
        )
    return user

async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Enforces ADMIN role for platform & governance APIs."""
    if current_user.role != UserRole.ADMIN.value and current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required to access this resource."
        )
    return current_user

async def get_user_project_role(
    project_id: str,
    user: User,
    db: AsyncSession
) -> Optional[str]:
    """Resolves the user's role for a specific project, checking ownership and membership."""
    if user.role in [UserRole.ADMIN.value, "ADMIN"]:
        return UserRole.ADMIN.value
    
    # 1. Check explicit project membership
    mem_res = await db.execute(
        select(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user.id
        )
    )
    membership = mem_res.scalars().first()
    if membership:
        return membership.role
        
    # 2. Check if user is the organization/workspace owner of the project
    proj_res = await db.execute(select(Project).filter(Project.id == project_id))
    project = proj_res.scalars().first()
    if not project:
        return None

    ws_res = await db.execute(select(Workspace).filter(Workspace.id == project.workspace_id))
    ws = ws_res.scalars().first()
    if ws:
        org_res = await db.execute(select(Organization).filter(Organization.id == ws.organization_id))
        org = org_res.scalars().first()
        if org and org.owner_id == user.id:
            return UserRole.PROJECT_OWNER.value
            
    # 3. Fallback to system role
    return user.role

async def _resolve_project(project_id: str, current_user: User, db: AsyncSession) -> Optional[Project]:
    if project_id == "default":
        if current_user.role in [UserRole.ADMIN.value, "ADMIN"]:
            proj_res = await db.execute(select(Project).order_by(Project.created_at.desc()))
            return proj_res.scalars().first()
        else:
            member_res = await db.execute(
                select(ProjectMember.project_id).filter(ProjectMember.user_id == current_user.id)
            )
            member_pids = member_res.scalars().all()
            if member_pids:
                proj_res = await db.execute(
                    select(Project).filter(Project.id.in_(member_pids)).order_by(Project.created_at.desc())
                )
                return proj_res.scalars().first()
            elif current_user.role in [UserRole.PROJECT_OWNER.value, UserRole.MANAGER.value]:
                proj_res = await db.execute(select(Project).order_by(Project.created_at.desc()))
                return proj_res.scalars().first()
            else:
                proj_res = await db.execute(select(Project).order_by(Project.created_at.desc()))
                return proj_res.scalars().first()
    else:
        proj_res = await db.execute(select(Project).filter(Project.id == project_id))
        return proj_res.scalars().first()

async def verify_project_access(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Project:
    """Verifies that the current user has access to the given project."""
    project = await _resolve_project(project_id, current_user, db)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project initiative not found."
        )
    role = await get_user_project_role(project.id, current_user, db)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. You are not a member of this project or organization."
        )
    return project

def require_project_permission(permission: Union[Permission, str]):
    """
    Dependency generator enforcing project-level permissions and tenant isolation.
    """
    async def permission_checker(
        project_id: str,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> Project:
        project = await _resolve_project(project_id, current_user, db)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project initiative not found."
            )
            
        role = await get_user_project_role(project.id, current_user, db)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. You are not a member of this project or organization."
            )
            
        perm_key = permission.value if isinstance(permission, Permission) else permission
        if not has_permission(role, perm_key):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: Action requires '{perm_key}', your project role is '{role}'."
            )
            
        return project
        
    return permission_checker

async def record_audit_log(
    db: AsyncSession,
    user: User,
    action: str,
    resource_type: str,
    resource_id: str,
    project_id: Optional[str] = None,
    organization_id: Optional[str] = None,
    details: Optional[str] = None,
    old_value: Optional[str] = None,
    new_value: Optional[str] = None,
    request: Optional[Request] = None
):
    """Utility to persist immutable governance audit log entries."""
    ip_addr = request.client.host if request and request.client else "127.0.0.1"
    
    log = AuditLog(
        id=str(uuid.uuid4()),
        user_id=user.id,
        user_name=user.full_name,
        action=action,
        project_id=project_id,
        details=details or f"{action} executed on {resource_type} {resource_id}",
        ip_address=ip_addr,
        created_at=datetime.utcnow()
    )
    db.add(log)
    await db.flush()
    return log
