import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.config.database import get_db
from app.auth.deps import get_current_user, verify_project_access
from app.models.user import User
from app.models.project import Project
from app.models.planning import SimulationScenario
from app.schemas.ai_payloads import SimulationRequest, SimulationResponse
from app.schemas.project import ApiResponse
from app.ai.orchestrator import orchestrator

router = APIRouter(prefix="/simulations", tags=["What-If Simulator"])

@router.get("/project/{project_id}", response_model=ApiResponse)
async def list_simulations(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    project = await verify_project_access(project_id, current_user, db)
    sim_res = await db.execute(select(SimulationScenario).filter(SimulationScenario.project_id == project.id).order_by(SimulationScenario.created_at.desc()))
    sims = sim_res.scalars().all()
    
    data = [{
        "id": s.id,
        "scenario_name": s.scenario_name,
        "automation_level": s.automation_level,
        "team_size": s.team_size,
        "budget": s.budget,
        "timeline_months": s.timeline_months,
        "ai_adoption_level": s.ai_adoption_level,
        "projected_effort_hours": s.projected_effort_hours,
        "projected_cost": s.projected_cost,
        "projected_timeline_months": s.projected_timeline_months,
        "expected_roi_percentage": s.expected_roi_percentage,
        "efficiency_gain_percentage": s.efficiency_gain_percentage,
        "risk_level": s.risk_level,
        "simulation_insights": s.simulation_insights,
        "created_at": s.created_at
    } for s in sims]
    
    return ApiResponse(success=True, data=data, message=f"Found {len(data)} simulation scenarios")

@router.post("/project/{project_id}/run", response_model=ApiResponse)
async def run_simulation(
    project_id: str,
    req: SimulationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    project = await verify_project_access(project_id, current_user, db)
    
    result = await orchestrator.run_what_if_simulation(req.model_dump())
    
    # Save scenario to DB
    scenario = SimulationScenario(
        id=str(uuid.uuid4()),
        project_id=project.id,
        scenario_name=result.get("scenario_name", f"{req.ai_adoption_level} AI Adoption ({req.automation_level}% Auto)"),
        automation_level=result.get("automation_level", req.automation_level),
        team_size=result.get("team_size", req.team_size),
        budget=result.get("budget", req.budget),
        timeline_months=result.get("timeline_months", req.timeline_months),
        ai_adoption_level=result.get("ai_adoption_level", req.ai_adoption_level),
        projected_effort_hours=result.get("projected_effort_hours", req.timeline_months * 160 * req.team_size),
        projected_cost=result.get("projected_cost", req.budget),
        projected_timeline_months=result.get("projected_timeline_months", float(req.timeline_months)),
        expected_roi_percentage=result.get("expected_roi_percentage", 250.0),
        efficiency_gain_percentage=result.get("efficiency_gain_percentage", 75.0),
        risk_level=result.get("risk_level", "LOW"),
        simulation_insights=result.get("simulation_insights", [])
    )
    db.add(scenario)
    await db.commit()
    
    return ApiResponse(success=True, data=result, message="Simulation scenario calculated and saved")

