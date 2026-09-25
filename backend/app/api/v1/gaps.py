import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.config.database import get_db
from app.auth.deps import get_current_user, require_project_permission, record_audit_log
from app.auth.permissions import Permission
from app.models.user import User
from app.models.project import Project
from app.models.transformation import Gap
from app.schemas.project import ApiResponse
from app.ai.orchestrator import orchestrator

router = APIRouter(prefix="/gaps", tags=["8-Dimension Gap Analysis"])

@router.get("/project/{project_id}", response_model=ApiResponse)
async def get_gaps(
    project_id: str,
    project: Project = Depends(require_project_permission(Permission.GAP_ANALYSIS_VIEW)),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    gap_res = await db.execute(select(Gap).filter(Gap.project_id == project.id))
    gaps = gap_res.scalars().all()
    
    context_data = {
        "name": project.name,
        "industry": project.industry,
        "business_problem": project.business_problem,
        "business_objective": project.business_objective
    }
    
    if not gaps:
        result = await orchestrator.generate_gap_analysis(context_data)
        for g in result["gaps"]:
            db.add(Gap(
                id=str(uuid.uuid4()),
                project_id=project.id,
                category=g["category"],
                title=g["title"],
                current_state=g["current_state"],
                desired_state=g["desired_state"],
                severity=g["severity"],
                impact=g["impact"],
                root_cause=g["root_cause"],
                recommended_action=g["recommended_action"]
            ))
        await db.commit()
        return ApiResponse(success=True, data=result, message="8-Dimension gaps auto-populated")
        
    crit = len([g for g in gaps if g.severity == "CRITICAL"])
    high = len([g for g in gaps if g.severity == "HIGH"])
    med = len([g for g in gaps if g.severity in ["MEDIUM", "LOW"]])
    
    return ApiResponse(
        success=True,
        data={
            "summary": f"8-Dimension assessment for {project.name} in {project.industry}.",
            "total_gaps_count": len(gaps),
            "critical_count": crit,
            "high_count": high,
            "medium_count": med,
            "gaps": [{
                "id": g.id,
                "category": g.category,
                "title": g.title,
                "current_state": g.current_state,
                "desired_state": g.desired_state,
                "severity": g.severity,
                "impact": g.impact,
                "root_cause": g.root_cause,
                "recommended_action": g.recommended_action
            } for g in gaps]
        }
    )

@router.post("/project/{project_id}/generate", response_model=ApiResponse)
async def generate_gaps(
    project_id: str,
    request: Request,
    project: Project = Depends(require_project_permission(Permission.GAP_ANALYSIS_RUN)),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    context_data = {
        "name": project.name,
        "industry": project.industry,
        "business_problem": project.business_problem,
        "business_objective": project.business_objective
    }
    
    result = await orchestrator.generate_gap_analysis(context_data)
    
    # Clear & Save Gaps
    existing_gaps = await db.execute(select(Gap).filter(Gap.project_id == project.id))
    for eg in existing_gaps.scalars().all():
        await db.delete(eg)
        
    for g in result["gaps"]:
        db.add(Gap(
            id=str(uuid.uuid4()),
            project_id=project.id,
            category=g["category"],
            title=g["title"],
            current_state=g["current_state"],
            desired_state=g["desired_state"],
            severity=g["severity"],
            impact=g["impact"],
            root_cause=g["root_cause"],
            recommended_action=g["recommended_action"]
        ))
        
    await record_audit_log(
        db=db,
        user=current_user,
        action="GENERATE_GAP_ANALYSIS",
        resource_type="GAP_ANALYSIS",
        resource_id=project.id,
        project_id=project.id,
        details=f"{current_user.full_name} ({current_user.role}) executed 8-dimension gap analysis for {project.name}",
        request=request
    )
        
    await db.commit()
    return ApiResponse(success=True, data=result, message="8-dimension gap analysis generated successfully")
