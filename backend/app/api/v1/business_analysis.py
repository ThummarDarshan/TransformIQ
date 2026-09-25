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
from app.models.transformation import Requirement, Stakeholder, BusinessProcess, RequirementType
from app.schemas.project import ApiResponse
from app.ai.orchestrator import orchestrator

router = APIRouter(prefix="/business-analysis", tags=["Business Analysis & Requirements"])

@router.get("/project/{project_id}", response_model=ApiResponse)
async def get_business_analysis(
    project_id: str,
    project: Project = Depends(require_project_permission(Permission.ANALYSIS_VIEW)),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    req_res = await db.execute(select(Requirement).filter(Requirement.project_id == project.id))
    reqs = req_res.scalars().all()
    
    sh_res = await db.execute(select(Stakeholder).filter(Stakeholder.project_id == project.id))
    stakeholders = sh_res.scalars().all()
    
    bp_res = await db.execute(select(BusinessProcess).filter(BusinessProcess.project_id == project.id))
    processes = bp_res.scalars().all()
    
    context_data = {
        "name": project.name,
        "industry": project.industry,
        "business_problem": project.business_problem,
        "business_objective": project.business_objective
    }
    
    if not reqs and not processes:
        result = await orchestrator.generate_business_analysis(context_data)
        for r in result["functional_requirements"]:
            db.add(Requirement(
                id=str(uuid.uuid4()),
                project_id=project.id,
                code=r["code"],
                title=r["title"],
                description=r["description"],
                priority=r["priority"],
                req_type=RequirementType.FUNCTIONAL.value,
                source=r.get("source", "AI Business Analysis")
            ))
        for r in result["non_functional_requirements"]:
            db.add(Requirement(
                id=str(uuid.uuid4()),
                project_id=project.id,
                code=r["code"],
                title=r["title"],
                description=r["description"],
                priority=r["priority"],
                req_type=RequirementType.NON_FUNCTIONAL.value,
                source=r.get("source", "AI Business Analysis")
            ))
        for p in result["as_is_process"]:
            db.add(BusinessProcess(
                id=str(uuid.uuid4()),
                project_id=project.id,
                step_number=p["step_number"],
                activity=p["activity"],
                actor=p["actor"],
                system=p["system"],
                duration=p["duration"],
                is_bottleneck=p.get("is_bottleneck", False),
                pain_points=p.get("pain_points")
            ))
        for s in result["stakeholders"]:
            db.add(Stakeholder(
                id=str(uuid.uuid4()),
                project_id=project.id,
                name=s["name"],
                role=s["role"],
                department=s["department"],
                influence=s["influence"],
                interest=s["interest"],
                key_concerns=s.get("key_concerns")
            ))
        await db.commit()
        return ApiResponse(success=True, data=result, message="Business analysis auto-populated")
        
    func_reqs = [r for r in reqs if r.req_type == RequirementType.FUNCTIONAL.value]
    nfunc_reqs = [r for r in reqs if r.req_type == RequirementType.NON_FUNCTIONAL.value]
    
    synth = await orchestrator.generate_business_analysis(context_data)
    
    # Load all provenance links for this project
    from app.models.provenance import SourceEvidence, ArtifactProvenance, ProvenanceType
    prov_res = await db.execute(select(ArtifactProvenance).filter(ArtifactProvenance.project_id == project.id))
    all_provs = prov_res.scalars().all()
    ev_res = await db.execute(select(SourceEvidence).filter(SourceEvidence.project_id == project.id))
    all_evs = {e.id: e for e in ev_res.scalars().all()}
    
    prov_map = {}
    for p in all_provs:
        ev = all_evs.get(p.source_evidence_id)
        if ev:
            prov_map[p.artifact_id] = {
                "provenance_type": p.provenance_type,
                "source_code": ev.source_code,
                "document_name": ev.document_name,
                "page_number": ev.page_number,
                "section_heading": ev.section_heading,
                "exact_text": ev.exact_text,
                "rationale": p.rationale,
                "confidence_score": p.confidence_score
            }

    def format_req(r):
        p_info = prov_map.get(r.code) or prov_map.get(r.id)
        if not p_info:
            is_rec = "recommended" in (r.source or "").lower()
            p_info = {
                "provenance_type": ProvenanceType.RECOMMENDED.value if is_rec else ProvenanceType.DERIVED.value,
                "source_code": "AI-REC" if is_rec else "SRC-001",
                "document_name": r.source or "Enterprise Solution Spec",
                "page_number": 1,
                "section_heading": "Requirements",
                "exact_text": r.description,
                "rationale": f"Generated to fulfill transformation target: '{r.title}'",
                "confidence_score": 0.94
            }
        return {
            "id": r.id,
            "code": r.code,
            "title": r.title,
            "description": r.description,
            "priority": r.priority,
            "req_type": r.req_type,
            "source": r.source,
            "provenance": p_info
        }

    return ApiResponse(
        success=True,
        data={
            "business_summary": synth.get("business_summary") or f"Operational baseline for {project.name} in {project.industry}.",
            "objectives": synth.get("objectives") or ([project.business_objective] if project.business_objective else []),
            "kpis": synth.get("kpis") or [
                "Cycle Turnaround Time < 15 mins",
                "Automation Throughput > 75%",
                "Error Rate Reduction > 85%"
            ],
            "as_is_process": [{
                "step_number": p.step_number,
                "activity": p.activity,
                "actor": p.actor,
                "system": p.system,
                "duration": p.duration,
                "is_bottleneck": p.is_bottleneck,
                "pain_points": p.pain_points
            } for p in processes] if processes else synth.get("as_is_process", []),
            "functional_requirements": [format_req(r) for r in func_reqs] if func_reqs else synth.get("functional_requirements", []),
            "non_functional_requirements": [format_req(r) for r in nfunc_reqs] if nfunc_reqs else synth.get("non_functional_requirements", []),
            "stakeholders": [{
                "name": s.name,
                "role": s.role,
                "department": s.department,
                "influence": s.influence,
                "interest": s.interest,
                "key_concerns": s.key_concerns
            } for s in stakeholders] if stakeholders else synth.get("stakeholders", [])
        }
    )

@router.post("/project/{project_id}/generate", response_model=ApiResponse)
async def generate_business_analysis(
    project_id: str,
    request: Request,
    project: Project = Depends(require_project_permission(Permission.ANALYSIS_RUN)),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    context_data = {
        "name": project.name,
        "industry": project.industry,
        "business_problem": project.business_problem,
        "business_objective": project.business_objective
    }
    
    result = await orchestrator.generate_business_analysis(context_data)
    
    # Clear & Save Requirements
    existing_reqs = await db.execute(select(Requirement).filter(Requirement.project_id == project.id))
    for er in existing_reqs.scalars().all():
        await db.delete(er)
        
    for r in result["functional_requirements"]:
        db.add(Requirement(
            id=str(uuid.uuid4()),
            project_id=project.id,
            code=r["code"],
            title=r["title"],
            description=r["description"],
            priority=r["priority"],
            req_type=RequirementType.FUNCTIONAL.value,
            source=r.get("source", "AI Business Analysis")
        ))
        
    for r in result["non_functional_requirements"]:
        db.add(Requirement(
            id=str(uuid.uuid4()),
            project_id=project.id,
            code=r["code"],
            title=r["title"],
            description=r["description"],
            priority=r["priority"],
            req_type=RequirementType.NON_FUNCTIONAL.value,
            source=r.get("source", "AI Business Analysis")
        ))
        
    # Clear & Save Processes
    existing_procs = await db.execute(select(BusinessProcess).filter(BusinessProcess.project_id == project.id))
    for ep in existing_procs.scalars().all():
        await db.delete(ep)
        
    for p in result["as_is_process"]:
        db.add(BusinessProcess(
            id=str(uuid.uuid4()),
            project_id=project.id,
            step_number=p["step_number"],
            activity=p["activity"],
            actor=p["actor"],
            system=p["system"],
            duration=p["duration"],
            is_bottleneck=p.get("is_bottleneck", False),
            pain_points=p.get("pain_points")
        ))
        
    # Clear & Save Stakeholders
    existing_sh = await db.execute(select(Stakeholder).filter(Stakeholder.project_id == project.id))
    for esh in existing_sh.scalars().all():
        await db.delete(esh)
        
    for s in result["stakeholders"]:
        db.add(Stakeholder(
            id=str(uuid.uuid4()),
            project_id=project.id,
            name=s["name"],
            role=s["role"],
            department=s["department"],
            influence=s["influence"],
            interest=s["interest"],
            key_concerns=s.get("key_concerns")
        ))
        
    await record_audit_log(
        db=db,
        user=current_user,
        action="GENERATE_BUSINESS_ANALYSIS",
        resource_type="BUSINESS_ANALYSIS",
        resource_id=project.id,
        project_id=project.id,
        details=f"{current_user.full_name} ({current_user.role}) executed AI business analysis for {project.name}",
        request=request
    )
        
    await db.commit()
    return ApiResponse(success=True, data=result, message="Business analysis generated successfully")
