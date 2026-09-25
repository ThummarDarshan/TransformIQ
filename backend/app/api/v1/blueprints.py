import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Body, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.config.database import get_db
from app.auth.deps import get_current_user, require_project_permission, record_audit_log
from app.auth.permissions import Permission
from app.models.user import User
from app.models.project import Project, ProjectStatus
from app.models.transformation import Gap, Recommendation, Solution
from app.models.architecture import ArchitectureComponent, WorkflowNode
from app.models.design import DatabaseEntity, ApiEndpoint, Wireframe
from app.models.planning import Roadmap, Estimate, Risk, TransformationScore
from app.models.collaboration import Approval, AuditLog, Version
from app.schemas.project import ApiResponse

router = APIRouter(prefix="/blueprints", tags=["Master Blueprint & Governance"])

@router.get("/project/{project_id}", response_model=ApiResponse)
@router.post("/project/{project_id}/generate", response_model=ApiResponse)
async def get_master_blueprint(
    project_id: str,
    project: Project = Depends(require_project_permission(Permission.BLUEPRINT_VIEW)),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    score_res = await db.execute(select(TransformationScore).filter(TransformationScore.project_id == project.id))
    score = score_res.scalars().first()
    
    gaps_res = await db.execute(select(Gap).filter(Gap.project_id == project.id))
    gaps = gaps_res.scalars().all()
    
    sol_res = await db.execute(select(Solution).filter(Solution.project_id == project.id))
    sol = sol_res.scalars().first()
    
    recs_res = await db.execute(select(Recommendation).filter(Recommendation.project_id == project.id))
    recs = recs_res.scalars().all()
    
    comps_res = await db.execute(select(ArchitectureComponent).filter(ArchitectureComponent.project_id == project.id))
    comps = comps_res.scalars().all()
    
    nodes_res = await db.execute(select(WorkflowNode).filter(WorkflowNode.project_id == project.id))
    nodes = nodes_res.scalars().all()
    
    ents_res = await db.execute(select(DatabaseEntity).filter(DatabaseEntity.project_id == project.id))
    ents = ents_res.scalars().all()
    
    apis_res = await db.execute(select(ApiEndpoint).filter(ApiEndpoint.project_id == project.id))
    apis = apis_res.scalars().all()
    
    wfs_res = await db.execute(select(Wireframe).filter(Wireframe.project_id == project.id))
    wfs = wfs_res.scalars().all()
    
    rm_res = await db.execute(select(Roadmap).filter(Roadmap.project_id == project.id))
    roadmap = rm_res.scalars().first()
    
    est_res = await db.execute(select(Estimate).filter(Estimate.project_id == project.id))
    estimate = est_res.scalars().first()
    
    risks_res = await db.execute(select(Risk).filter(Risk.project_id == project.id))
    risks = risks_res.scalars().all()
    
    app_res = await db.execute(select(Approval).filter(Approval.project_id == project.id, Approval.artifact_type == "BLUEPRINT"))
    approval = app_res.scalars().first()
    
    blueprint_payload = {
        "project_id": project.id,
        "project_name": project.name,
        "industry": project.industry,
        "generated_at": datetime.utcnow().strftime("%B %d, %Y - %H:%M UTC"),
        "executive_summary": sol.executive_summary if sol else (project.business_problem or "Comprehensive digital transformation blueprint."),
        "business_problem": project.business_problem,
        "objectives": [project.business_objective] if project.business_objective else [
            f"Automate end-to-end processing for {project.name} in {project.industry}.",
            "Reduce operational turnaround latency by >75%.",
            "Ensure 99.9% compliance with enterprise SLA standards."
        ],
        "transformation_score": {
            "overall_score": score.overall_score if score else 88,
            "ai_readiness": score.ai_readiness if score else 91,
            "automation_potential": score.automation_potential if score else 88,
            "data_readiness": score.data_readiness if score else 76,
            "business_impact": score.business_impact if score else 94,
            "technical_feasibility": score.technical_feasibility if score else 89,
            "implementation_readiness": score.implementation_readiness if score else 85,
            "disclaimer": "AI-assisted assessment based on project inputs and enterprise artifacts."
        },
        "key_gaps": [{
            "id": g.id,
            "category": g.category,
            "title": g.title,
            "current_state": g.current_state,
            "desired_state": g.desired_state,
            "severity": g.severity,
            "impact": g.impact,
            "recommended_action": g.recommended_action
        } for g in gaps[:6]],
        "recommended_solution": {
            "name": sol.name if sol else project.name,
            "tagline": sol.tagline if sol else "AI-Powered Enterprise Suite",
            "expected_roi": sol.expected_roi if sol else "340% ROI in 12 Months",
            "technology_stack": sol.technology_stack if sol else {"Core": ["React", "FastAPI", "PostgreSQL", "Gemini 3.5 Flash Lite"]},
            "key_capabilities": sol.key_capabilities if sol else ["Intelligent Ingestion", "Automated Workflows", "Telemetry Dashboard"],
            "recommendations_count": len(recs)
        },
        "architecture_summary": {
            "components_count": len(comps),
            "layers": list(set([c.layer for c in comps if c.layer])) if comps else ["Client", "AI Engine", "Database"],
            "deployment": "Multi-Zone Kubernetes / Docker Swarm on Azure Container Apps / Render"
        },
        "process_summary": {
            "nodes_count": len(nodes),
            "cycle_time_current": "Multi-Day Manual Baseline",
            "cycle_time_projected": "Real-Time Sub-Minute Processing",
            "efficiency_gain": "75%+ Reduction"
        },
        "database_summary": {
            "entities_count": len(ents),
            "tables": [e.name for e in ents]
        },
        "api_summary": {
            "endpoints_count": len(apis),
            "version": "1.0.0",
            "spec": "OpenAPI 3.0"
        },
        "ux_summary": {
            "wireframes_count": len(wfs),
            "target_personas": ["Executive Leadership", "Operations Specialists"]
        },
        "roadmap_summary": {
            "total_duration_weeks": roadmap.total_duration_weeks if roadmap else 16,
            "phases_count": len(roadmap.phases) if roadmap and roadmap.phases else 4
        },
        "estimate_summary": {
            "total_hours": estimate.total_estimated_hours if estimate else 1120,
            "total_cost": estimate.total_estimated_cost if estimate else 138500.0,
            "duration_months": estimate.duration_months if estimate else 4,
            "currency": "USD"
        },
        "risks_summary": {
            "total_risks": len(risks),
            "mitigations_active": True
        },
        "approval_status": approval.status if approval else "UNDER_REVIEW",
        "reviewed_by": approval.reviewed_by if approval else None,
        "decision_date": approval.decision_date if approval else None
    }
    
    return ApiResponse(success=True, data=blueprint_payload, message="Master transformation blueprint retrieved")

@router.post("/project/{project_id}/approve", response_model=ApiResponse)
async def approve_blueprint(
    project_id: str,
    request: Request,
    action: str = Body(..., embed=True), # APPROVE or REJECT
    comments: str = Body("", embed=True),
    project: Project = Depends(require_project_permission(Permission.BLUEPRINT_APPROVE)),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    new_status = "APPROVED" if action.upper() == "APPROVE" else "REJECTED"
    
    app_res = await db.execute(select(Approval).filter(Approval.project_id == project.id, Approval.artifact_type == "BLUEPRINT"))
    approval = app_res.scalars().first()
    
    if not approval:
        approval = Approval(
            id=str(uuid.uuid4()),
            project_id=project.id,
            artifact_type="BLUEPRINT",
            status=new_status,
            requested_by=current_user.full_name,
            reviewed_by=current_user.full_name,
            comments=comments,
            decision_date=datetime.utcnow()
        )
        db.add(approval)
    else:
        approval.status = new_status
        approval.reviewed_by = current_user.full_name
        approval.comments = comments
        approval.decision_date = datetime.utcnow()
        
    project.status = ProjectStatus.APPROVED.value if new_status == "APPROVED" else ProjectStatus.ANALYSIS.value
    
    # Create Version Snapshot
    version_count_res = await db.execute(select(Version).filter(Version.project_id == project_id))
    ver_count = len(version_count_res.scalars().all())
    
    ver = Version(
        id=str(uuid.uuid4()),
        project_id=project_id,
        artifact_type="MASTER_BLUEPRINT",
        version_number=ver_count + 1,
        change_summary=f"Blueprint {new_status} by {current_user.full_name}. Notes: {comments or 'Standard review'}",
        author_name=current_user.full_name,
        snapshot_json={"status": new_status, "timestamp": datetime.utcnow().isoformat()}
    )
    db.add(ver)
    
    await record_audit_log(
        db=db,
        user=current_user,
        action=f"BLUEPRINT_{new_status}",
        resource_type="MASTER_BLUEPRINT",
        resource_id=project_id,
        project_id=project_id,
        details=f"{current_user.full_name} ({current_user.role}) {new_status.lower()} Master Blueprint with notes: '{comments}'",
        request=request
    )
    
    await db.commit()
    return ApiResponse(
        success=True,
        data={"status": new_status, "version_created": ver.version_number},
        message=f"Blueprint successfully {new_status.lower()}"
    )
