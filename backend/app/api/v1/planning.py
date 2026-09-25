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
from app.models.planning import Roadmap, Estimate
from app.schemas.project import ApiResponse
from app.ai.orchestrator import orchestrator

router = APIRouter(prefix="/planning", tags=["Implementation Planning & Estimation"])

@router.get("/project/{project_id}", response_model=ApiResponse)
async def get_planning(
    project_id: str,
    project: Project = Depends(require_project_permission(Permission.PLANNING_VIEW)),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    rm_res = await db.execute(select(Roadmap).filter(Roadmap.project_id == project.id))
    roadmap = rm_res.scalars().first()
    
    est_res = await db.execute(select(Estimate).filter(Estimate.project_id == project.id))
    estimate = est_res.scalars().first()
    
    context_data = {
        "name": project.name,
        "industry": project.industry,
        "business_problem": project.business_problem,
        "business_objective": project.business_objective
    }

    # Auto-generate if not yet seeded/generated for this project
    if not roadmap:
        plan_data = await orchestrator.generate_planning(context_data)
        roadmap = Roadmap(
            id=str(uuid.uuid4()),
            project_id=project.id,
            name=plan_data.get("name", f"Roadmap for {project.name}"),
            phases=plan_data.get("phases", []),
            total_duration_weeks=plan_data.get("total_duration_weeks", 16)
        )
        db.add(roadmap)
        await db.commit()
        await db.refresh(roadmap)

    if not estimate:
        est_data = await orchestrator.generate_estimates(context_data)
        estimate = Estimate(
            id=str(uuid.uuid4()),
            project_id=project.id,
            total_estimated_hours=est_data.get("total_estimated_hours", 1120),
            total_estimated_cost=est_data.get("total_estimated_cost", 138500.0),
            currency=est_data.get("currency", "USD"),
            duration_months=est_data.get("duration_months", 4),
            roles_breakdown=est_data.get("roles_breakdown", est_data.get("role_breakdown", [])),
            infrastructure_cost=est_data.get("infrastructure_cost_monthly", est_data.get("infra_cost_monthly", 650.0)),
            ai_api_cost_monthly=est_data.get("ai_api_cost_monthly", 420.0),
            assumptions=est_data.get("assumptions", []),
            confidence_level=est_data.get("confidence_level", "HIGH"),
            disclaimer=est_data.get("disclaimer", "AI-generated preliminary estimate. Validated estimates require detailed technical discovery.")
        )
        db.add(estimate)
        await db.commit()
        await db.refresh(estimate)
        
    wbs = []
    if roadmap and roadmap.phases:
        for p in roadmap.phases:
            for t in p.get("tasks", []):
                wbs.append({
                    "id": str(uuid.uuid4()),
                    "phase_name": p.get("phase_name", "Phase"),
                    "title": t if isinstance(t, str) else t.get("title", "Task"),
                    "description": f"Implementation deliverable for {p.get('phase_name', '')}",
                    "assigned_role": "Engineering & Architecture",
                    "estimated_hours": 40,
                    "status": "PLANNED"
                })
                
    response_data = {
        "roadmap": {
            "name": roadmap.name if roadmap else f"Roadmap for {project.name}",
            "total_duration_weeks": roadmap.total_duration_weeks if roadmap else 16,
            "phases": roadmap.phases if roadmap else []
        },
        "estimate": {
            "total_estimated_hours": estimate.total_estimated_hours if estimate else 1120,
            "total_estimated_cost": estimate.total_estimated_cost if estimate else 138500.0,
            "currency": getattr(estimate, "currency", "USD") or "USD",
            "duration_months": estimate.duration_months if estimate else 4,
            "roles_breakdown": estimate.roles_breakdown if estimate else [],
            "infrastructure_cost_monthly": getattr(estimate, "infrastructure_cost", 650.0) or 650.0,
            "ai_api_cost_monthly": getattr(estimate, "ai_api_cost_monthly", 420.0) or 420.0,
            "assumptions": getattr(estimate, "assumptions", []) or [],
            "confidence_level": getattr(estimate, "confidence_level", "HIGH") or "HIGH",
            "disclaimer": getattr(estimate, "disclaimer", "AI-generated preliminary estimate. Validated estimates require detailed technical discovery.") or "AI-generated preliminary estimate. Validated estimates require detailed technical discovery."
        },
        # Legacy backwards compatibility keys
        "roadmap_phases": roadmap.phases if roadmap else [],
        "total_duration_weeks": roadmap.total_duration_weeks if roadmap else 16,
        "wbs_tasks": wbs
    }

    return ApiResponse(
        success=True,
        data=response_data
    )

@router.post("/project/{project_id}/generate", response_model=ApiResponse)
async def generate_planning(
    project_id: str,
    request: Request,
    project: Project = Depends(require_project_permission(Permission.PLANNING_GENERATE)),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    context_data = {
        "name": project.name,
        "industry": project.industry,
        "business_problem": project.business_problem,
        "business_objective": project.business_objective
    }
    
    plan_result = await orchestrator.generate_planning(context_data)
    est_result = await orchestrator.generate_estimates(context_data)
    
    phases = plan_result.get("phases", plan_result.get("roadmap_phases", []))
    total_weeks = plan_result.get("total_duration_weeks", 16)
    plan_name = plan_result.get("name", f"Roadmap for {project.name}")
    
    # Save Roadmap
    rm_res = await db.execute(select(Roadmap).filter(Roadmap.project_id == project.id))
    roadmap = rm_res.scalars().first()
    if not roadmap:
        roadmap = Roadmap(
            id=str(uuid.uuid4()),
            project_id=project.id,
            name=plan_name,
            phases=phases,
            total_duration_weeks=total_weeks
        )
        db.add(roadmap)
    else:
        roadmap.name = plan_name
        roadmap.phases = phases
        roadmap.total_duration_weeks = total_weeks
        
    # Save Estimate
    est_res = await db.execute(select(Estimate).filter(Estimate.project_id == project.id))
    estimate = est_res.scalars().first()
    
    roles = est_result.get("roles_breakdown", est_result.get("role_breakdown", []))
    total_hours = est_result.get("total_estimated_hours", 1120)
    total_cost = est_result.get("total_estimated_cost", 138500.0)
    dur_months = est_result.get("duration_months", 4)
    infra_cost = est_result.get("infrastructure_cost_monthly", est_result.get("infra_cost_monthly", 650.0))
    ai_cost = est_result.get("ai_api_cost_monthly", 420.0)
    assump = est_result.get("assumptions", [])
    conf = est_result.get("confidence_level", "HIGH")
    disc = est_result.get("disclaimer", "AI-generated preliminary estimate. Validated estimates require detailed technical discovery.")

    if not estimate:
        estimate = Estimate(
            id=str(uuid.uuid4()),
            project_id=project.id,
            total_estimated_hours=total_hours,
            total_estimated_cost=total_cost,
            currency=est_result.get("currency", "USD"),
            duration_months=dur_months,
            roles_breakdown=roles,
            infrastructure_cost=infra_cost,
            ai_api_cost_monthly=ai_cost,
            assumptions=assump,
            confidence_level=conf,
            disclaimer=disc
        )
        db.add(estimate)
    else:
        estimate.total_estimated_hours = total_hours
        estimate.total_estimated_cost = total_cost
        estimate.duration_months = dur_months
        estimate.roles_breakdown = roles
        estimate.infrastructure_cost = infra_cost
        estimate.ai_api_cost_monthly = ai_cost
        estimate.assumptions = assump
        estimate.confidence_level = conf
        estimate.disclaimer = disc
        
    await record_audit_log(
        db=db,
        user=current_user,
        action="GENERATE_PLANNING",
        resource_type="PLANNING_ROADMAP",
        resource_id=project.id,
        project_id=project.id,
        details=f"{current_user.full_name} generated implementation plan and roadmap",
        request=request
    )
        
    await db.commit()

    response_data = {
        "roadmap": {
            "name": roadmap.name,
            "total_duration_weeks": roadmap.total_duration_weeks,
            "phases": roadmap.phases
        },
        "estimate": {
            "total_estimated_hours": estimate.total_estimated_hours,
            "total_estimated_cost": estimate.total_estimated_cost,
            "currency": getattr(estimate, "currency", "USD") or "USD",
            "duration_months": estimate.duration_months,
            "roles_breakdown": estimate.roles_breakdown,
            "infrastructure_cost_monthly": getattr(estimate, "infrastructure_cost", 650.0) or 650.0,
            "ai_api_cost_monthly": getattr(estimate, "ai_api_cost_monthly", 420.0) or 420.0,
            "assumptions": getattr(estimate, "assumptions", []) or [],
            "confidence_level": getattr(estimate, "confidence_level", "HIGH") or "HIGH",
            "disclaimer": getattr(estimate, "disclaimer", "AI-generated preliminary estimate. Validated estimates require detailed technical discovery.") or "AI-generated preliminary estimate. Validated estimates require detailed technical discovery."
        },
        "roadmap_phases": roadmap.phases,
        "total_duration_weeks": roadmap.total_duration_weeks
    }

    return ApiResponse(
        success=True,
        data=response_data,
        message="Implementation roadmap and estimation generated successfully"
    )
