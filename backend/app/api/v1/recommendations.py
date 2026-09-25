import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.config.database import get_db
from app.auth.deps import get_current_user, require_project_permission, get_user_project_role, record_audit_log
from app.auth.permissions import Permission, has_permission
from app.models.user import User
from app.models.project import Project
from app.models.transformation import Recommendation, Solution
from app.schemas.project import ApiResponse
from app.ai.orchestrator import orchestrator

router = APIRouter(prefix="/recommendations", tags=["AI & Automation Recommendations"])

@router.get("/project/{project_id}", response_model=ApiResponse)
async def get_recommendations(
    project_id: str,
    project: Project = Depends(require_project_permission(Permission.RECOMMENDATION_VIEW)),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    rec_res = await db.execute(select(Recommendation).filter(Recommendation.project_id == project.id))
    recs = rec_res.scalars().all()
    
    sol_res = await db.execute(select(Solution).filter(Solution.project_id == project.id))
    sol = sol_res.scalars().first()
    
    context_data = {
        "name": project.name,
        "industry": project.industry,
        "business_problem": project.business_problem,
        "business_objective": project.business_objective
    }
    
    if not recs or not sol:
        result = await orchestrator.generate_recommendations(context_data)
        if not sol:
            sol = Solution(
                id=str(uuid.uuid4()),
                project_id=project.id,
                name=result["recommended_solution_name"],
                tagline=result["tagline"],
                executive_summary=result["executive_summary"],
                technology_stack=result["technology_stack"],
                key_capabilities=result["key_capabilities"],
                expected_roi=result["expected_roi"]
            )
            db.add(sol)
            
        for r in result["recommendations"]:
            db.add(Recommendation(
                id=str(uuid.uuid4()),
                project_id=project.id,
                category=r["category"],
                title=r["title"],
                description=r["description"],
                reason=r["reason"],
                expected_impact=r["expected_impact"],
                feasibility=r["feasibility"],
                priority=r["priority"],
                confidence_score=r["confidence_score"],
                source_citation=r.get("source_citation"),
                dependencies=r.get("dependencies", []),
                status=r.get("status", "AI_GENERATED")
            ))
        await db.commit()
        return ApiResponse(success=True, data=result, message="Recommendations auto-populated")
        
    return ApiResponse(
        success=True,
        data={
            "recommended_solution_name": sol.name,
            "tagline": sol.tagline,
            "executive_summary": sol.executive_summary,
            "key_capabilities": sol.key_capabilities,
            "expected_roi": sol.expected_roi,
            "technology_stack": sol.technology_stack,
            "recommendations": [{
                "id": r.id,
                "category": r.category,
                "title": r.title,
                "description": r.description,
                "reason": r.reason,
                "expected_impact": r.expected_impact,
                "feasibility": r.feasibility,
                "priority": r.priority,
                "confidence_score": r.confidence_score,
                "source_citation": r.source_citation,
                "dependencies": r.dependencies,
                "status": r.status
            } for r in recs]
        }
    )

@router.post("/project/{project_id}/generate", response_model=ApiResponse)
async def generate_recommendations(
    project_id: str,
    request: Request,
    project: Project = Depends(require_project_permission(Permission.RECOMMENDATION_GENERATE)),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    context_data = {
        "name": project.name,
        "industry": project.industry,
        "business_problem": project.business_problem,
        "business_objective": project.business_objective
    }
    
    result = await orchestrator.generate_recommendations(context_data)
    
    # Save solution
    sol_res = await db.execute(select(Solution).filter(Solution.project_id == project.id))
    sol = sol_res.scalars().first()
    if not sol:
        sol = Solution(
            id=str(uuid.uuid4()),
            project_id=project.id,
            name=result["recommended_solution_name"],
            tagline=result["tagline"],
            executive_summary=result["executive_summary"],
            technology_stack=result["technology_stack"],
            key_capabilities=result["key_capabilities"],
            expected_roi=result["expected_roi"]
        )
        db.add(sol)
    else:
        sol.name = result["recommended_solution_name"]
        sol.tagline = result["tagline"]
        sol.executive_summary = result["executive_summary"]
        sol.technology_stack = result["technology_stack"]
        sol.key_capabilities = result["key_capabilities"]
        sol.expected_roi = result["expected_roi"]
        
    # Clear & Save Recs
    existing_recs = await db.execute(select(Recommendation).filter(Recommendation.project_id == project.id))
    for er in existing_recs.scalars().all():
        await db.delete(er)
        
    for r in result["recommendations"]:
        db.add(Recommendation(
            id=str(uuid.uuid4()),
            project_id=project.id,
            category=r["category"],
            title=r["title"],
            description=r["description"],
            reason=r["reason"],
            expected_impact=r["expected_impact"],
            feasibility=r["feasibility"],
            priority=r["priority"],
            confidence_score=r["confidence_score"],
            source_citation=r.get("source_citation"),
            dependencies=r.get("dependencies", []),
            status=r.get("status", "AI_GENERATED")
        ))
        
    await record_audit_log(
        db=db,
        user=current_user,
        action="GENERATE_RECOMMENDATIONS",
        resource_type="RECOMMENDATION",
        resource_id=project.id,
        project_id=project.id,
        details=f"{current_user.full_name} ({current_user.role}) generated AI solution recommendations for {project.name}",
        request=request
    )
        
    await db.commit()
    return ApiResponse(success=True, data=result, message="AI solution recommendations generated successfully")

@router.get("/why/{rec_id}", response_model=ApiResponse)
@router.get("/{rec_id}/why", response_model=ApiResponse)
async def get_recommendation_why(
    rec_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    rec_res = await db.execute(select(Recommendation).filter(Recommendation.id == rec_id))
    rec = rec_res.scalars().first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
        
    citations = [rec.source_citation] if rec.source_citation else [
        "Business Architecture Reference Model 2026",
        "Enterprise Process Bottleneck Dataset",
        "Autonomous System Design Framework"
    ]
    
    data = {
        "recommendation_id": rec.id,
        "title": rec.title,
        "category": rec.category,
        "reason": rec.reason,
        "confidence_score": rec.confidence_score,
        "source_citation": rec.source_citation,
        "citations": citations,
        "explainability_summary": f"Derived with {int(rec.confidence_score * 100 if rec.confidence_score <= 1 else rec.confidence_score)}% AI confidence based on detected friction in {rec.category}."
    }
    return ApiResponse(success=True, data=data, message="Explainable AI rationale retrieved")

@router.post("/{rec_id}/status", response_model=ApiResponse)
async def update_recommendation_status(
    rec_id: str,
    status_value: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    rec_res = await db.execute(select(Recommendation).filter(Recommendation.id == rec_id))
    rec = rec_res.scalars().first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
        
    user_role = await get_user_project_role(rec.project_id, current_user, db)
    if not user_role or not has_permission(user_role, Permission.RECOMMENDATION_APPROVE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied. Role cannot approve or change recommendation governance status."
        )
        
    rec.status = status_value
    await record_audit_log(
        db=db,
        user=current_user,
        action="UPDATE_RECOMMENDATION_STATUS",
        resource_type="RECOMMENDATION",
        resource_id=rec.id,
        project_id=rec.project_id,
        details=f"{current_user.full_name} ({current_user.role}) updated recommendation '{rec.title}' status to {status_value}",
        request=request
    )
    await db.commit()
    return ApiResponse(success=True, data={"id": rec.id, "status": rec.status}, message="Recommendation status updated")

