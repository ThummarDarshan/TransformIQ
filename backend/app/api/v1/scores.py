import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.config.database import get_db
from app.auth.deps import get_current_user, verify_project_access
from app.models.user import User
from app.models.project import Project
from app.models.planning import TransformationScore
from app.schemas.project import ApiResponse
from app.ai.orchestrator import orchestrator

router = APIRouter(prefix="/scores", tags=["Transformation Score Engine"])

@router.get("/project/{project_id}", response_model=ApiResponse)
async def get_score(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    project = await verify_project_access(project_id, current_user, db)
    s_res = await db.execute(select(TransformationScore).filter(TransformationScore.project_id == project.id))
    score = s_res.scalars().first()
    
    if not score:
        return await calculate_score(project.id, current_user, db)
        
    return ApiResponse(
        success=True,
        data={
            "overall_score": score.overall_score,
            "ai_readiness": score.ai_readiness,
            "automation_potential": score.automation_potential,
            "data_readiness": score.data_readiness,
            "business_impact": score.business_impact,
            "technical_feasibility": score.technical_feasibility,
            "implementation_readiness": score.implementation_readiness,
            "key_drivers": score.key_drivers,
            "key_blockers": score.key_blockers,
            "strategic_recommendations": score.strategic_recommendations,
            "disclaimer": score.disclaimer
        }
    )

@router.post("/project/{project_id}/calculate", response_model=ApiResponse)
async def calculate_score(
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
    
    result = await orchestrator.generate_score(context_data)
    
    # Save score
    s_res = await db.execute(select(TransformationScore).filter(TransformationScore.project_id == project.id))
    score = s_res.scalars().first()
    if not score:
        score = TransformationScore(
            id=str(uuid.uuid4()),
            project_id=project.id,
            overall_score=result["overall_score"],
            ai_readiness=result["ai_readiness"],
            automation_potential=result["automation_potential"],
            data_readiness=result["data_readiness"],
            business_impact=result["business_impact"],
            technical_feasibility=result["technical_feasibility"],
            implementation_readiness=result["implementation_readiness"],
            key_drivers=result["key_drivers"],
            key_blockers=result["key_blockers"],
            strategic_recommendations=result["strategic_recommendations"]
        )
        db.add(score)
    else:
        score.overall_score = result["overall_score"]
        score.ai_readiness = result["ai_readiness"]
        score.automation_potential = result["automation_potential"]
        score.data_readiness = result["data_readiness"]
        score.business_impact = result["business_impact"]
        score.technical_feasibility = result["technical_feasibility"]
        score.implementation_readiness = result["implementation_readiness"]
        score.key_drivers = result["key_drivers"]
        score.key_blockers = result["key_blockers"]
        score.strategic_recommendations = result["strategic_recommendations"]
        
    await db.commit()
    return ApiResponse(success=True, data=result, message="Transformation readiness score calculated successfully")
