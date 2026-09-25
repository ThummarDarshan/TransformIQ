import uuid
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Body, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.config.database import get_db
from app.auth.deps import get_current_user, require_project_permission, record_audit_log
from app.auth.permissions import Permission
from app.models.user import User
from app.models.project import Project
from app.models.architecture import ArchitectureComponent, ArchitectureConnection
from app.schemas.project import ApiResponse
from app.ai.orchestrator import orchestrator

router = APIRouter(prefix="/architecture", tags=["Solution Architecture Builder"])

@router.get("/project/{project_id}", response_model=ApiResponse)
async def get_architecture(
    project_id: str,
    project: Project = Depends(require_project_permission(Permission.ARCHITECTURE_VIEW)),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    comp_res = await db.execute(select(ArchitectureComponent).filter(ArchitectureComponent.project_id == project.id))
    comps = comp_res.scalars().all()
    
    conn_res = await db.execute(select(ArchitectureConnection).filter(ArchitectureConnection.project_id == project.id))
    conns = conn_res.scalars().all()
    
    context_data = {
        "name": project.name,
        "industry": project.industry,
        "business_problem": project.business_problem,
        "business_objective": project.business_objective
    }
    
    if not comps:
        result = await orchestrator.generate_architecture(context_data)
        for c in result.get("components", []):
            db.add(ArchitectureComponent(
                id=c["id"],
                project_id=project.id,
                name=c["name"],
                layer=c["layer"],
                tech_stack=c["tech_stack"],
                description=c["description"],
                responsibilities=c.get("responsibilities", []),
                position_x=c.get("position_x", 100.0),
                position_y=c.get("position_y", 100.0)
            ))
        for cn in result.get("connections", []):
            db.add(ArchitectureConnection(
                id=str(uuid.uuid4()),
                project_id=project.id,
                source_component_id=cn["source"],
                target_component_id=cn["target"],
                protocol=cn["protocol"],
                data_payload=cn.get("data_payload"),
                is_async=cn.get("is_async", False)
            ))
        await db.commit()
        return ApiResponse(success=True, data=result, message="Architecture auto-populated")
        
    synth = await orchestrator.generate_architecture(context_data)
    
    return ApiResponse(
        success=True,
        data={
            "hld_overview": synth.get("hld_overview") or f"High-Level Architecture for {project.name}.",
            "deployment_model": synth.get("deployment_model") or "Multi-Zone Cloud Native Container Architecture.",
            "security_boundaries": synth.get("security_boundaries") or [
                "Public Ingress protected by TLS 1.3 Termination",
                "API Gateway with JWT validation and Rate Limiting per tenant",
                "Encrypted database and storage with customer-managed keys"
            ],
            "data_flow_summary": synth.get("data_flow_summary") or "Client -> API Gateway -> Core Service -> AI Engine -> PostgreSQL Database.",
            "components": [{
                "id": c.id,
                "name": c.name,
                "layer": c.layer,
                "tech_stack": c.tech_stack,
                "description": c.description,
                "responsibilities": c.responsibilities,
                "position_x": c.position_x,
                "position_y": c.position_y
            } for c in comps],
            "connections": [{
                "id": cn.id,
                "source": cn.source_component_id,
                "target": cn.target_component_id,
                "protocol": cn.protocol,
                "data_payload": cn.data_payload,
                "is_async": cn.is_async
            } for cn in conns],
            "lld_services": synth.get("lld_services", [
                {"name": "CoreService", "purpose": "Handles business logic and orchestration."},
                {"name": "AuthService", "purpose": "Handles JWT authentication and RBAC guards."},
                {"name": "StorageService", "purpose": "Manages transactional state and persistence."}
            ])
        }
    )

@router.post("/project/{project_id}/generate", response_model=ApiResponse)
async def generate_architecture(
    project_id: str,
    request: Request,
    project: Project = Depends(require_project_permission(Permission.ARCHITECTURE_GENERATE)),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    context_data = {
        "name": project.name,
        "industry": project.industry,
        "business_problem": project.business_problem,
        "business_objective": project.business_objective
    }
    
    result = await orchestrator.generate_architecture(context_data)
    
    # Clear existing
    old_comps = await db.execute(select(ArchitectureComponent).filter(ArchitectureComponent.project_id == project.id))
    for oc in old_comps.scalars().all():
        await db.delete(oc)
        
    old_conns = await db.execute(select(ArchitectureConnection).filter(ArchitectureConnection.project_id == project.id))
    for ocn in old_conns.scalars().all():
        await db.delete(ocn)
        
    for c in result.get("components", []):
        db.add(ArchitectureComponent(
            id=c["id"],
            project_id=project.id,
            name=c["name"],
            layer=c["layer"],
            tech_stack=c["tech_stack"],
            description=c["description"],
            responsibilities=c.get("responsibilities", []),
            position_x=c.get("position_x", 100.0),
            position_y=c.get("position_y", 100.0)
        ))
        
    for cn in result.get("connections", []):
        db.add(ArchitectureConnection(
            id=str(uuid.uuid4()),
            project_id=project.id,
            source_component_id=cn["source"],
            target_component_id=cn["target"],
            protocol=cn["protocol"],
            data_payload=cn.get("data_payload"),
            is_async=cn.get("is_async", False)
        ))
        
    await record_audit_log(
        db=db,
        user=current_user,
        action="GENERATE_ARCHITECTURE",
        resource_type="ARCHITECTURE",
        resource_id=project.id,
        project_id=project.id,
        details=f"{current_user.full_name} ({current_user.role}) generated solution architecture for {project.name}",
        request=request
    )
        
    await db.commit()
    return ApiResponse(success=True, data=result, message="Architecture generated successfully")

@router.post("/project/{project_id}/save-layout", response_model=ApiResponse)
async def save_architecture_layout(
    project_id: str,
    layout_data: List[Dict[str, Any]] = Body(...),
    project: Project = Depends(require_project_permission(Permission.ARCHITECTURE_EDIT)),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    comp_res = await db.execute(select(ArchitectureComponent).filter(ArchitectureComponent.project_id == project.id))
    comps = {c.id: c for c in comp_res.scalars().all()}
    
    for item in layout_data:
        c_id = item.get("id")
        pos = item.get("position", {})
        if c_id in comps and isinstance(pos, dict):
            if "x" in pos:
                comps[c_id].position_x = float(pos["x"])
            if "y" in pos:
                comps[c_id].position_y = float(pos["y"])
                
    await db.commit()
    return ApiResponse(success=True, data={"saved_count": len(layout_data)}, message="Architecture layout saved successfully")

