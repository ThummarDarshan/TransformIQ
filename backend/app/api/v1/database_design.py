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
from app.models.design import DatabaseEntity
from app.schemas.project import ApiResponse
from app.ai.orchestrator import orchestrator

router = APIRouter(prefix="/database", tags=["Database & Data Model Design"])

@router.get("/project/{project_id}", response_model=ApiResponse)
async def get_database_design(
    project_id: str,
    project: Project = Depends(require_project_permission(Permission.DATABASE_VIEW)),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    ent_res = await db.execute(select(DatabaseEntity).filter(DatabaseEntity.project_id == project.id))
    ents = ent_res.scalars().all()
    
    context_data = {
        "name": project.name,
        "industry": project.industry,
        "business_problem": project.business_problem,
        "business_objective": project.business_objective
    }
    
    if not ents:
        result = await orchestrator.generate_database_design(context_data)
        for e in result.get("entities", []):
            db.add(DatabaseEntity(
                id=str(uuid.uuid4()),
                project_id=project.id,
                name=e["name"],
                description=e["description"],
                fields=e["fields"],
                relationships=e.get("relationships", [])
            ))
        await db.commit()
        return ApiResponse(success=True, data=result, message="Database design auto-populated")
        
    synth = await orchestrator.generate_database_design(context_data)
    
    return ApiResponse(
        success=True,
        data={
            "overview": synth.get("overview") or f"Normalized Relational Schema & Vector Store for {project.name}. Optimized for PostgreSQL 16 + pgvector.",
            "entities": [{
                "id": e.id,
                "name": e.name,
                "description": e.description,
                "fields": e.fields,
                "relationships": e.relationships
            } for e in ents],
            "sql_ddl": synth.get("sql_ddl") or "\n\n".join([f"-- Table: {e.name}\nCREATE TABLE {e.name.lower()} (\n" + ",\n".join([f"    {f['name']} {f['type'].upper()}{' PRIMARY KEY' if f.get('is_primary') else ''}" for f in e.fields]) + "\n);" for e in ents])
        }
    )

@router.post("/project/{project_id}/generate", response_model=ApiResponse)
async def generate_database_design(
    project_id: str,
    request: Request,
    project: Project = Depends(require_project_permission(Permission.DATABASE_GENERATE)),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    context_data = {
        "name": project.name,
        "industry": project.industry,
        "business_problem": project.business_problem,
        "business_objective": project.business_objective
    }
    
    result = await orchestrator.generate_database_design(context_data)
    
    # Clear existing
    old_ents = await db.execute(select(DatabaseEntity).filter(DatabaseEntity.project_id == project.id))
    for oe in old_ents.scalars().all():
        await db.delete(oe)
        
    for e in result.get("entities", []):
        db.add(DatabaseEntity(
            id=str(uuid.uuid4()),
            project_id=project.id,
            name=e["name"],
            description=e["description"],
            fields=e["fields"],
            relationships=e.get("relationships", [])
        ))
        
    await record_audit_log(
        db=db,
        user=current_user,
        action="GENERATE_DATABASE_DESIGN",
        resource_type="DATABASE_DESIGN",
        resource_id=project.id,
        project_id=project.id,
        details=f"{current_user.full_name} generated relational PostgreSQL schema with {len(result['entities'])} entities",
        request=request
    )
        
    await db.commit()
    return ApiResponse(success=True, data=result, message="Database design generated successfully")
