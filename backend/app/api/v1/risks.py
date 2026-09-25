import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.config.database import get_db
from app.auth.deps import get_current_user, verify_project_access
from app.models.user import User
from app.models.project import Project
from app.models.planning import Risk
from app.schemas.project import ApiResponse
from app.ai.orchestrator import orchestrator

router = APIRouter(prefix="/risks", tags=["Risk Assessment Engine"])

@router.get("/project/{project_id}", response_model=ApiResponse)
async def get_risks(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    project = await verify_project_access(project_id, current_user, db)
    r_res = await db.execute(select(Risk).filter(Risk.project_id == project.id))
    risks = r_res.scalars().all()
    
    if not risks:
        return await generate_risks(project.id, current_user, db)
        
    return ApiResponse(
        success=True,
        data={
            "summary": f"Risk assessment identified {len(risks)} project risks across Technical, AI, Security, and Adoption categories.",
            "total_risks": len(risks),
            "risks": [{
                "id": r.id,
                "category": r.category,
                "title": r.title,
                "description": r.description or r.title,
                "probability": r.probability,
                "impact": r.impact,
                "severity": r.severity,
                "mitigation_strategy": r.mitigation_strategy,
                "owner": r.owner,
                "status": r.status
            } for r in risks]
        }
    )

@router.post("/project/{project_id}/generate", response_model=ApiResponse)
async def generate_risks(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    project = await verify_project_access(project_id, current_user, db)
    
    context_data = {
        "name": project.name,
        "industry": project.industry,
        "business_problem": project.business_problem,
        "business_objective": project.business_objective
    }
    
    result = await orchestrator.generate_risks(context_data)
    
    # Clear existing
    old_risks = await db.execute(select(Risk).filter(Risk.project_id == project.id))
    for ork in old_risks.scalars().all():
        await db.delete(ork)
        
    for rk in result.get("risks", []):
        title = rk.get("risk_title") or rk.get("title", "Project Risk")
        mitigation = rk.get("mitigation") or rk.get("mitigation_strategy", "Standard mitigation protocols")
        probability = rk.get("likelihood") or rk.get("probability", "MEDIUM")
        impact = rk.get("impact", "HIGH")
        db.add(Risk(
            id=str(uuid.uuid4()),
            project_id=project.id,
            category=rk.get("category", "Operational"),
            title=title,
            description=rk.get("description", title),
            probability=probability,
            impact=impact,
            severity="HIGH" if impact == "HIGH" or probability == "HIGH" else "MEDIUM",
            mitigation_strategy=mitigation,
            owner=rk.get("owner", "Project Lead")
        ))
        
    await db.commit()
    return ApiResponse(success=True, data=result, message="Risks matrix generated successfully")
