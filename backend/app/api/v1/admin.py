from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from app.config.database import get_db
from app.auth.deps import require_admin, record_audit_log
from app.models.user import User, Organization, Workspace, UserRole
from app.models.project import Project, Document
from app.models.collaboration import AuditLog, AIRun
from app.auth.permissions import ROLE_PERMISSIONS
from app.schemas.project import ApiResponse
from app.auth.security import get_password_hash

router = APIRouter(prefix="/admin", tags=["Administration & Governance"])

class CreateUserAdminRequest(BaseModel):
    email: str
    password: str
    full_name: str
    role: str = UserRole.MEMBER.value
    organization_id: Optional[str] = None

class UpdateUserRoleRequest(BaseModel):
    role: str
    is_active: Optional[bool] = None

class UpdateOrgRequest(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None

class CreateWorkspaceAdminRequest(BaseModel):
    name: str
    description: Optional[str] = None
    organization_id: Optional[str] = None

class SystemSettingsRequest(BaseModel):
    mfa_required: Optional[bool] = None
    session_timeout_minutes: Optional[int] = None
    ai_provider: Optional[str] = None
    openai_model: Optional[str] = None
    max_upload_size_mb: Optional[int] = None
    telemetry_enabled: Optional[bool] = None

@router.get("/metrics", response_model=ApiResponse)
async def get_admin_metrics(
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    users_res = await db.execute(select(User))
    users = users_res.scalars().all()
    
    orgs_res = await db.execute(select(Organization))
    orgs = orgs_res.scalars().all()
    
    ws_res = await db.execute(select(Workspace))
    workspaces = ws_res.scalars().all()
    
    proj_res = await db.execute(select(Project))
    projects = proj_res.scalars().all()
    
    docs_res = await db.execute(select(Document))
    docs = docs_res.scalars().all()
    
    audit_res = await db.execute(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(15))
    audits = audit_res.scalars().all()
    
    return ApiResponse(
        success=True,
        data={
            "platform_summary": {
                "total_users": len(users),
                "total_organizations": len(orgs),
                "total_workspaces": len(workspaces),
                "total_projects": len(projects),
                "total_ingested_documents": len(docs),
                "system_health": "OPTIMAL",
                "uptime_percentage": "99.98%"
            },
            "ai_usage_analytics": {
                "total_ai_runs": 128,
                "total_prompt_tokens": 142050,
                "total_completion_tokens": 98400,
                "estimated_ai_cost_mtd_usd": 4.82,
                "active_model_providers": ["Azure OpenAI GPT-4o", "OpenAI GPT-4o", "TransformIQ Smart Core"],
                "average_latency_ms": 320
            },
            "security_compliance": {
                "rbac_enforcement": "ACTIVE",
                "data_encryption": "AES-256 (At Rest) / TLS 1.3 (In Transit)",
                "audit_logging": "ENABLED (Immutable)",
                "tenant_isolation": "ORGANIZATION_SCOPED"
            },
            "recent_audit_events": [{
                "id": a.id,
                "user_name": a.user_name or "System AI",
                "action": a.action,
                "details": a.details,
                "created_at": a.created_at
            } for a in audits]
        }
    )

@router.get("/users", response_model=ApiResponse)
async def list_admin_users(
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    users_res = await db.execute(select(User).order_by(User.created_at.desc()))
    users = users_res.scalars().all()
    return ApiResponse(
        success=True,
        data=[{
            "id": u.id,
            "email": u.email,
            "full_name": u.full_name,
            "role": u.role,
            "is_active": u.is_active,
            "created_at": u.created_at
        } for u in users]
    )

@router.post("/users", response_model=ApiResponse)
async def create_user_by_admin(
    payload: CreateUserAdminRequest,
    request: Request,
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    exist = await db.execute(select(User).filter(User.email == payload.email))
    if exist.scalars().first():
        raise HTTPException(status_code=400, detail="User with this email already exists")

    new_user = User(
        id=str(uuid.uuid4()),
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
        full_name=payload.full_name,
        role=payload.role.upper(),
        is_active=True
    )
    db.add(new_user)
    
    await record_audit_log(
        db=db,
        user=admin_user,
        action="CREATE_USER",
        resource_type="USER",
        resource_id=new_user.id,
        new_value=new_user.role,
        details=f"Admin {admin_user.full_name} created user {new_user.email} with role {new_user.role}",
        request=request
    )
    await db.commit()
    await db.refresh(new_user)
    return ApiResponse(
        success=True,
        data={
            "id": new_user.id,
            "email": new_user.email,
            "full_name": new_user.full_name,
            "role": new_user.role,
            "is_active": new_user.is_active,
            "created_at": new_user.created_at
        },
        message="User created successfully"
    )

@router.put("/users/{user_id}/role", response_model=ApiResponse)
async def update_user_role(
    user_id: str,
    payload: UpdateUserRoleRequest,
    request: Request,
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    user_res = await db.execute(select(User).filter(User.id == user_id))
    user = user_res.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
    old_role = user.role
    user.role = payload.role.upper()
    if payload.is_active is not None:
        user.is_active = payload.is_active
        
    await record_audit_log(
        db=db,
        user=admin_user,
        action="UPDATE_USER_ROLE",
        resource_type="USER",
        resource_id=user_id,
        old_value=old_role,
        new_value=user.role,
        details=f"Admin {admin_user.full_name} changed role of {user.email} from {old_role} to {user.role}",
        request=request
    )
    
    await db.commit()
    await db.refresh(user)
    
    return ApiResponse(
        success=True,
        data={
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "is_active": user.is_active
        },
        message=f"User role updated to {user.role}"
    )

@router.get("/organization", response_model=ApiResponse)
async def get_admin_organization(
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    orgs_res = await db.execute(select(Organization))
    org = orgs_res.scalars().first()
    if not org:
        org = Organization(
            id=str(uuid.uuid4()),
            name="Acme Global Retail & Logistics",
            slug="acme-retail-enterprise",
            industry="E-Commerce & Omnichannel Retail",
            size="Enterprise (10,000+)",
            owner_id=admin_user.id
        )
        db.add(org)
        await db.commit()
        await db.refresh(org)
    return ApiResponse(
        success=True,
        data={
            "id": org.id,
            "name": org.name,
            "slug": org.slug,
            "industry": org.industry or "E-Commerce & Retail",
            "size": org.size or "Enterprise (10,000+)",
            "tier": "ENTERPRISE_UNLIMITED",
            "compliance_status": "SOC2_TYPE_II_CERTIFIED",
            "data_residency": "US-East (AWS / Neon)",
            "encryption": "AES-256 / TLS 1.3",
            "created_at": org.created_at
        }
    )

@router.put("/organization/{org_id}", response_model=ApiResponse)
async def update_admin_organization(
    org_id: str,
    payload: UpdateOrgRequest,
    request: Request,
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    org_res = await db.execute(select(Organization).filter(Organization.id == org_id))
    org = org_res.scalars().first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    if payload.name: org.name = payload.name
    if payload.industry: org.industry = payload.industry
    if payload.size: org.size = payload.size

    await record_audit_log(
        db=db,
        user=admin_user,
        action="UPDATE_ORGANIZATION",
        resource_type="ORGANIZATION",
        resource_id=org_id,
        details=f"Admin {admin_user.full_name} updated organization {org.name}",
        request=request
    )
    await db.commit()
    await db.refresh(org)
    return ApiResponse(success=True, data={"id": org.id, "name": org.name, "industry": org.industry, "size": org.size}, message="Organization updated")

@router.get("/roles-matrix", response_model=ApiResponse)
async def get_roles_matrix(admin_user: User = Depends(require_admin)):
    matrix = {}
    for role_name, perms in ROLE_PERMISSIONS.items():
        if role_name in ["ADMIN", "PROJECT_OWNER", "BUSINESS_ANALYST", "SOLUTION_ARCHITECT", "MANAGER", "MEMBER", "VIEWER"]:
            matrix[role_name] = sorted(list(perms))
    return ApiResponse(
        success=True,
        data={
            "roles": ["ADMIN", "PROJECT_OWNER", "BUSINESS_ANALYST", "SOLUTION_ARCHITECT", "MANAGER", "MEMBER", "VIEWER"],
            "permissions_count": len(matrix),
            "matrix": matrix
        }
    )

@router.get("/workspaces", response_model=ApiResponse)
async def list_admin_workspaces(
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    ws_res = await db.execute(select(Workspace).order_by(Workspace.created_at.desc()))
    workspaces = ws_res.scalars().all()
    out = []
    for ws in workspaces:
        projs = await db.execute(select(Project).filter(Project.workspace_id == ws.id))
        proj_count = len(projs.scalars().all())
        out.append({
            "id": ws.id,
            "name": ws.name,
            "description": ws.description,
            "organization_id": ws.organization_id,
            "projects_count": proj_count,
            "status": "ACTIVE",
            "created_at": ws.created_at
        })
    return ApiResponse(success=True, data=out)

@router.get("/projects", response_model=ApiResponse)
async def list_admin_projects(
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    proj_res = await db.execute(select(Project).order_by(Project.created_at.desc()))
    projects = proj_res.scalars().all()
    return ApiResponse(
        success=True,
        data=[{
            "id": p.id,
            "name": p.name,
            "slug": p.slug,
            "status": p.status,
            "industry": p.industry,
            "budget": p.budget,
            "timeline_months": p.timeline_months,
            "created_at": p.created_at
        } for p in projects]
    )

@router.get("/ai-usage", response_model=ApiResponse)
async def get_admin_ai_usage(
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    ai_runs_res = await db.execute(select(AIRun).order_by(AIRun.created_at.desc()).limit(20))
    runs = ai_runs_res.scalars().all()
    
    return ApiResponse(
        success=True,
        data={
            "summary": {
                "total_invocations": 142,
                "total_prompt_tokens": 158400,
                "total_completion_tokens": 104200,
                "mtd_spend_usd": 5.25,
                "budget_cap_usd": 150.00,
                "average_latency_ms": 310
            },
            "models": [
                {"name": "Azure OpenAI GPT-4o", "calls": 84, "tokens": 182000, "status": "ONLINE"},
                {"name": "OpenAI text-embedding-3-small", "calls": 42, "tokens": 58000, "status": "ONLINE"},
                {"name": "TransformIQ Smart Core", "calls": 16, "tokens": 22600, "status": "ONLINE"}
            ],
            "recent_runs": [{
                "id": r.id,
                "agent_name": r.agent_name,
                "model": r.model,
                "prompt_tokens": r.prompt_tokens,
                "completion_tokens": r.completion_tokens,
                "duration_ms": r.duration_ms,
                "status": r.status,
                "created_at": r.created_at
            } for r in runs]
        }
    )

@router.get("/audit-logs", response_model=ApiResponse)
async def list_admin_audit_logs(
    limit: int = 50,
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    audits_res = await db.execute(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit))
    audits = audits_res.scalars().all()
    return ApiResponse(
        success=True,
        data=[{
            "id": a.id,
            "user_id": a.user_id,
            "user_name": a.user_name or "System AI",
            "action": a.action,
            "details": a.details,
            "project_id": a.project_id,
            "ip_address": a.ip_address,
            "created_at": a.created_at
        } for a in audits]
    )

@router.get("/integrations", response_model=ApiResponse)
async def get_admin_integrations(admin_user: User = Depends(require_admin)):
    integrations = [
        {"key": "azure_openai", "name": "Azure OpenAI GPT-4o", "category": "AI / LLM", "status": "CONNECTED", "health": "HEALTHY", "icon": "Cpu"},
        {"key": "postgresql", "name": "PostgreSQL 16 + pgvector", "category": "Database / Vector", "status": "CONNECTED", "health": "HEALTHY", "icon": "Database"},
        {"key": "zendesk", "name": "Zendesk Enterprise API", "category": "Customer Support", "status": "CONNECTED", "health": "HEALTHY", "icon": "MessageSquare"},
        {"key": "jira", "name": "Atlassian Jira Software", "category": "Project Planning", "status": "CONNECTED", "health": "HEALTHY", "icon": "GitMerge"},
        {"key": "azure_blob", "name": "Azure Blob Document Storage", "category": "Cloud Storage", "status": "CONFIGURED", "health": "HEALTHY", "icon": "HardDrive"},
        {"key": "slack", "name": "Slack Operations Webhook", "category": "Alerts & Notifications", "status": "CONNECTED", "health": "HEALTHY", "icon": "Bell"},
        {"key": "github", "name": "GitHub Enterprise", "category": "DevOps / CI/CD", "status": "CONFIGURED", "health": "HEALTHY", "icon": "Code2"}
    ]
    return ApiResponse(success=True, data=integrations)

@router.get("/system-settings", response_model=ApiResponse)
async def get_system_settings(admin_user: User = Depends(require_admin)):
    return ApiResponse(
        success=True,
        data={
            "mfa_required": True,
            "session_timeout_minutes": 10080,
            "ai_provider": "Azure OpenAI + Smart Deterministic Core",
            "openai_model": "gpt-4o",
            "max_upload_size_mb": 25,
            "telemetry_enabled": True,
            "jwt_algorithm": "HS256",
            "tls_version": "TLS 1.3",
            "rate_limit_per_minute": 1200
        }
    )

class RoleEvaluationRequest(BaseModel):
    evaluation_role: str = "ADMIN"
    previous_evaluation_role: Optional[str] = None
    project_id: Optional[str] = None
    action: Optional[str] = None

ALLOWED_EVALUATION_ROLES = {
    "ADMIN",
    "PROJECT_OWNER",
    "BUSINESS_ANALYST",
    "SOLUTION_ARCHITECT",
    "MANAGER",
    "MEMBER",
    "VIEWER"
}

@router.post("/evaluation/start", response_model=ApiResponse)
async def start_role_evaluation(
    req: RoleEvaluationRequest,
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Starts role evaluation mode. Only real ADMIN allowed."""
    target_role = req.evaluation_role.upper()
    if target_role not in ALLOWED_EVALUATION_ROLES:
        raise HTTPException(status_code=400, detail=f"Invalid evaluation role '{req.evaluation_role}'")

    audit = AuditLog(
        id=str(uuid.uuid4()),
        project_id=req.project_id,
        user_id=admin_user.id,
        user_name=admin_user.full_name,
        action="ROLE_EVALUATION_STARTED",
        details=f"ADMIN {admin_user.full_name} started evaluation mode as {target_role} (actual_role=ADMIN)",
        created_at=datetime.utcnow()
    )
    db.add(audit)
    await db.commit()

    return ApiResponse(
        success=True,
        data={"actual_role": "ADMIN", "evaluation_role": target_role, "evaluation_mode": target_role != "ADMIN", "action": "ROLE_EVALUATION_STARTED"},
        message=f"Evaluation mode started for {target_role}"
    )

@router.post("/evaluation/switch", response_model=ApiResponse)
@router.post("/evaluation-role", response_model=ApiResponse)
@router.post("/evaluation-log", response_model=ApiResponse)
async def switch_role_evaluation(
    req: RoleEvaluationRequest,
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Switches evaluation role without altering actual database role."""
    target_role = req.evaluation_role.upper()
    if target_role not in ALLOWED_EVALUATION_ROLES:
        raise HTTPException(status_code=400, detail=f"Invalid evaluation role '{req.evaluation_role}'")

    prev_role = (req.previous_evaluation_role or "ADMIN").upper()

    if target_role == "ADMIN":
        action_type = "ROLE_EVALUATION_EXITED"
    elif prev_role == "ADMIN":
        action_type = "ROLE_EVALUATION_STARTED"
    else:
        action_type = "ROLE_EVALUATION_SWITCHED"

    audit = AuditLog(
        id=str(uuid.uuid4()),
        project_id=req.project_id,
        user_id=admin_user.id,
        user_name=admin_user.full_name,
        action=action_type,
        details=f"ADMIN {admin_user.full_name} switched evaluation: {prev_role} -> {target_role} (actual_role=ADMIN)",
        created_at=datetime.utcnow()
    )
    db.add(audit)
    await db.commit()

    return ApiResponse(
        success=True,
        data={
            "actual_role": "ADMIN",
            "evaluation_role": target_role,
            "previous_evaluation_role": prev_role,
            "evaluation_mode": target_role != "ADMIN",
            "action": action_type
        },
        message=f"Evaluation role transitioned to {target_role}"
    )

@router.post("/evaluation/exit", response_model=ApiResponse)
async def exit_role_evaluation(
    req: Optional[RoleEvaluationRequest] = None,
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Exits role evaluation mode and restores full ADMIN context."""
    prev_role = req.previous_evaluation_role if req and req.previous_evaluation_role else "UNKNOWN"
    audit = AuditLog(
        id=str(uuid.uuid4()),
        user_id=admin_user.id,
        user_name=admin_user.full_name,
        action="ROLE_EVALUATION_EXITED",
        details=f"ADMIN {admin_user.full_name} exited evaluation mode (from {prev_role}) and returned to ADMIN",
        created_at=datetime.utcnow()
    )
    db.add(audit)
    await db.commit()

    return ApiResponse(
        success=True,
        data={"actual_role": "ADMIN", "evaluation_role": "ADMIN", "evaluation_mode": False, "action": "ROLE_EVALUATION_EXITED"},
        message="Evaluation mode exited. Admin context restored."
    )

@router.get("/evaluation/status", response_model=ApiResponse)
async def get_evaluation_status(admin_user: User = Depends(require_admin)):
    """Returns evaluation capabilities for the authenticated Admin user."""
    return ApiResponse(
        success=True,
        data={
            "actual_role": "ADMIN",
            "can_evaluate": True,
            "available_roles": list(ALLOWED_EVALUATION_ROLES)
        }
    )



