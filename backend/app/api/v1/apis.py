import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.config.database import get_db
from app.auth.deps import get_current_user, require_project_permission, record_audit_log
from app.auth.permissions import Permission
from app.models.user import User
from app.models.project import Project
from app.models.design import ApiEndpoint
from app.schemas.project import ApiResponse
from app.ai.orchestrator import orchestrator

router = APIRouter(prefix="/apis", tags=["API Contract & Specification"])

@router.get("/project/{project_id}", response_model=ApiResponse)
async def get_api_catalog(
    project_id: str,
    project: Project = Depends(require_project_permission(Permission.API_VIEW)),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    api_res = await db.execute(select(ApiEndpoint).filter(ApiEndpoint.project_id == project.id))
    apis = api_res.scalars().all()
    
    context_data = {
        "name": project.name,
        "industry": project.industry,
        "business_problem": project.business_problem,
        "business_objective": project.business_objective
    }
    
    if not apis:
        result = await orchestrator.generate_api_design(context_data)
        for a in result.get("endpoints", []):
            db.add(ApiEndpoint(
                id=str(uuid.uuid4()),
                project_id=project.id,
                path=a["path"],
                method=a["method"],
                summary=a["summary"],
                description=a["description"],
                request_schema=a.get("request_body"),
                response_schema=a.get("response_body"),
                auth_required=a.get("auth_required", True)
            ))
        await db.commit()
        return ApiResponse(
            success=True,
            data={
                "openapi_version": "3.0.3",
                "api_name": result.get("api_title", f"{project.name} Microservices API"),
                "endpoints_count": len(result.get("endpoints", [])),
                "endpoints": result.get("endpoints", [])
            },
            message="API catalog auto-populated"
        )
        
    synth = await orchestrator.generate_api_design(context_data)
    
    return ApiResponse(
        success=True,
        data={
            "openapi_version": "3.0.3",
            "api_name": synth.get("api_title") or f"{project.name} Microservices API",
            "endpoints_count": len(apis),
            "endpoints": [{
                "id": a.id,
                "path": a.path,
                "method": a.method,
                "summary": a.summary,
                "description": a.description,
                "request_schema": a.request_schema,
                "response_schema": a.response_schema,
                "auth_required": a.auth_required
            } for a in apis]
        }
    )

@router.post("/project/{project_id}/generate", response_model=ApiResponse)
async def generate_api_catalog(
    project_id: str,
    request: Request,
    project: Project = Depends(require_project_permission(Permission.API_GENERATE)),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    context_data = {
        "name": project.name,
        "industry": project.industry,
        "business_problem": project.business_problem,
        "business_objective": project.business_objective
    }
    
    result = await orchestrator.generate_api_design(context_data)
    
    # Clear existing
    old_apis = await db.execute(select(ApiEndpoint).filter(ApiEndpoint.project_id == project.id))
    for oa in old_apis.scalars().all():
        await db.delete(oa)
        
    for a in result.get("endpoints", []):
        db.add(ApiEndpoint(
            id=str(uuid.uuid4()),
            project_id=project.id,
            path=a["path"],
            method=a["method"],
            summary=a["summary"],
            description=a["description"],
            request_schema=a.get("request_body"),
            response_schema=a.get("response_body"),
            auth_required=a.get("auth_required", True)
        ))
        
    await record_audit_log(
        db=db,
        user=current_user,
        action="GENERATE_API_CATALOG",
        resource_type="API_CATALOG",
        resource_id=project.id,
        project_id=project.id,
        details=f"{current_user.full_name} generated OpenAPI specifications with {len(result.get('endpoints', []))} endpoints",
        request=request
    )
        
    await db.commit()
    return ApiResponse(
        success=True,
        data={
            "openapi_version": "3.0.3",
            "api_name": result.get("api_title", f"{project.name} Microservices API"),
            "endpoints_count": len(result.get("endpoints", [])),
            "endpoints": result.get("endpoints", [])
        },
        message="API catalog generated successfully"
    )
