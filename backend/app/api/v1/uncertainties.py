import uuid
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Body, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.config.database import get_db
from app.auth.deps import get_current_user, require_project_permission, record_audit_log
from app.auth.permissions import Permission
from app.models.user import User
from app.models.project import Project
from app.models.provenance import SourceEvidence
from app.models.uncertainty import (
    RequirementUncertainty, UncertaintyCategory, UncertaintySeverity, UncertaintyStatus
)
from app.schemas.project import ApiResponse
from app.schemas.uncertainty import (
    UncertaintyItemResponse, UncertaintyStats, UncertaintyListResponse,
    ConfirmUncertaintyRequest, EditAssumptionRequest, RejectUncertaintyRequest
)
from app.ai.uncertainty_analyzer import uncertainty_analyzer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/uncertainties", tags=["What I Couldn't Figure Out (Uncertainty Governance)"])

@router.get("/project/{project_id}", response_model=ApiResponse)
async def get_project_uncertainties(
    project_id: str,
    project: Project = Depends(require_project_permission(Permission.PROJECT_VIEW)),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve all identified uncertainties, assumptions, and user confirmations
    for the project ("WHAT I COULDN'T FIGURE OUT").
    Automatically analyzes project source material if no records exist yet.
    """
    # 1. Fetch existing uncertainties
    unc_res = await db.execute(
        select(RequirementUncertainty)
        .filter(RequirementUncertainty.project_id == project.id)
        .order_by(RequirementUncertainty.created_at.asc())
    )
    uncertainties = unc_res.scalars().all()
    
    # 2. If empty, run analyzer on project evidence and persist baseline uncertainties
    if not uncertainties:
        ev_res = await db.execute(select(SourceEvidence).filter(SourceEvidence.project_id == project.id))
        source_evidences = ev_res.scalars().all()
        
        raw_items = uncertainty_analyzer.analyze_source_material(
            project_id=project.id,
            project_name=project.name,
            industry=project.industry,
            business_problem=project.business_problem,
            business_objective=project.business_objective,
            source_evidences=source_evidences,
            existing_uncertainties=[]
        )
        
        new_records = []
        for item in raw_items:
            u_obj = RequirementUncertainty(
                id=str(uuid.uuid4()),
                project_id=project.id,
                title=item["title"],
                category=item["category"],
                severity=item["severity"],
                status=UncertaintyStatus.UNCONFIRMED.value,
                what_is_unclear=item["what_is_unclear"],
                why_unclear=item.get("why_unclear"),
                source_evidence_id=item.get("source_evidence_id"),
                source_code=item.get("source_code"),
                document_name=item.get("document_name"),
                page_number=item.get("page_number"),
                section_heading=item.get("section_heading"),
                evidence_text=item.get("evidence_text"),
                assumption=item["assumption"],
                is_high_risk_assumption=item.get("is_high_risk_assumption", False),
                what_to_confirm=item["what_to_confirm"],
                potential_impact=item["potential_impact"]
            )
            db.add(u_obj)
            new_records.append(u_obj)
            
        await db.commit()
        uncertainties = new_records

    # 3. Compute Stats
    total = len(uncertainties)
    unconfirmed = sum(1 for u in uncertainties if u.status == UncertaintyStatus.UNCONFIRMED.value)
    confirmed = sum(1 for u in uncertainties if u.status == UncertaintyStatus.CONFIRMED.value)
    resolved = sum(1 for u in uncertainties if u.status == UncertaintyStatus.RESOLVED.value)
    rejected = sum(1 for u in uncertainties if u.status == UncertaintyStatus.REJECTED.value)
    critical_c = sum(1 for u in uncertainties if u.severity == UncertaintySeverity.CRITICAL.value)
    high_c = sum(1 for u in uncertainties if u.severity == UncertaintySeverity.HIGH.value)
    medium_c = sum(1 for u in uncertainties if u.severity == UncertaintySeverity.MEDIUM.value)
    low_c = sum(1 for u in uncertainties if u.severity == UncertaintySeverity.LOW.value)

    stats = {
        "total_count": total,
        "unconfirmed_count": unconfirmed,
        "confirmed_count": confirmed,
        "resolved_count": resolved,
        "rejected_count": rejected,
        "critical_count": critical_c,
        "high_count": high_c,
        "medium_count": medium_c,
        "low_count": low_c
    }

    serialized = [
        {
            "id": u.id,
            "project_id": u.project_id,
            "title": u.title,
            "category": u.category,
            "severity": u.severity,
            "status": u.status,
            "what_is_unclear": u.what_is_unclear,
            "why_unclear": u.why_unclear,
            "source_evidence_id": u.source_evidence_id,
            "source_code": u.source_code,
            "document_name": u.document_name,
            "page_number": u.page_number,
            "section_heading": u.section_heading,
            "evidence_text": u.evidence_text,
            "assumption": u.assumption,
            "is_high_risk_assumption": u.is_high_risk_assumption,
            "what_to_confirm": u.what_to_confirm,
            "potential_impact": u.potential_impact,
            "user_clarification": u.user_clarification,
            "confirmed_by_id": u.confirmed_by_id,
            "confirmed_at": u.confirmed_at.isoformat() if u.confirmed_at else None,
            "resolution_action": u.resolution_action,
            "created_at": u.created_at.isoformat() if u.created_at else None,
            "updated_at": u.updated_at.isoformat() if u.updated_at else None
        }
        for u in uncertainties
    ]

    return ApiResponse(
        success=True,
        data={
            "project_id": project.id,
            "project_name": project.name,
            "stats": stats,
            "uncertainties": serialized
        },
        message="Uncertainties and clarifications retrieved successfully"
    )

@router.get("/{uncertainty_id}", response_model=ApiResponse)
async def get_uncertainty_detail(
    uncertainty_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed breakdown of a single requirement uncertainty item.
    """
    res = await db.execute(select(RequirementUncertainty).filter(RequirementUncertainty.id == uncertainty_id))
    u = res.scalars().first()
    if not u:
        raise HTTPException(status_code=404, detail="Uncertainty record not found.")

    return ApiResponse(
        success=True,
        data={
            "id": u.id,
            "project_id": u.project_id,
            "title": u.title,
            "category": u.category,
            "severity": u.severity,
            "status": u.status,
            "what_is_unclear": u.what_is_unclear,
            "why_unclear": u.why_unclear,
            "source_evidence_id": u.source_evidence_id,
            "source_code": u.source_code,
            "document_name": u.document_name,
            "page_number": u.page_number,
            "section_heading": u.section_heading,
            "evidence_text": u.evidence_text,
            "assumption": u.assumption,
            "is_high_risk_assumption": u.is_high_risk_assumption,
            "what_to_confirm": u.what_to_confirm,
            "potential_impact": u.potential_impact,
            "user_clarification": u.user_clarification,
            "confirmed_by_id": u.confirmed_by_id,
            "confirmed_at": u.confirmed_at.isoformat() if u.confirmed_at else None,
            "resolution_action": u.resolution_action
        },
        message="Uncertainty details retrieved"
    )

@router.post("/{uncertainty_id}/confirm", response_model=ApiResponse)
async def confirm_uncertainty(
    uncertainty_id: str,
    payload: ConfirmUncertaintyRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Confirm user clarification for an uncertainty item.
    Stores user-provided ground truth and transitions status to CONFIRMED.
    This confirmed truth will feed into future blueprint generation.
    """
    res = await db.execute(select(RequirementUncertainty).filter(RequirementUncertainty.id == uncertainty_id))
    u = res.scalars().first()
    if not u:
        raise HTTPException(status_code=404, detail="Uncertainty record not found.")

    u.user_clarification = payload.user_clarification.strip()
    u.status = UncertaintyStatus.CONFIRMED.value
    u.resolution_action = "CONFIRMED"
    u.confirmed_by_id = current_user.id
    u.confirmed_at = datetime.utcnow()
    u.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(u)

    await record_audit_log(
        db=db,
        user=current_user,
        action="CONFIRM_UNCERTAINTY",
        resource_type="REQUIREMENT_UNCERTAINTY",
        resource_id=u.id,
        project_id=u.project_id,
        details=f"User clarified uncertainty '{u.title}': {u.user_clarification[:120]}...",
        request=request
    )

    return ApiResponse(
        success=True,
        data={
            "id": u.id,
            "title": u.title,
            "status": u.status,
            "user_clarification": u.user_clarification,
            "confirmed_at": u.confirmed_at.isoformat() if u.confirmed_at else None
        },
        message=f"Clarification for '{u.title}' confirmed successfully."
    )

@router.post("/{uncertainty_id}/edit-assumption", response_model=ApiResponse)
async def edit_uncertainty_assumption(
    uncertainty_id: str,
    payload: EditAssumptionRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Accept or modify the AI's stated assumption for an uncertainty item.
    """
    res = await db.execute(select(RequirementUncertainty).filter(RequirementUncertainty.id == uncertainty_id))
    u = res.scalars().first()
    if not u:
        raise HTTPException(status_code=404, detail="Uncertainty record not found.")

    u.assumption = payload.assumption.strip()
    if payload.user_clarification:
        u.user_clarification = payload.user_clarification.strip()
    u.status = UncertaintyStatus.RESOLVED.value
    u.resolution_action = "EDITED_ASSUMPTION"
    u.confirmed_by_id = current_user.id
    u.confirmed_at = datetime.utcnow()
    u.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(u)

    await record_audit_log(
        db=db,
        user=current_user,
        action="EDIT_ASSUMPTION",
        resource_type="REQUIREMENT_UNCERTAINTY",
        resource_id=u.id,
        project_id=u.project_id,
        details=f"User updated assumption on '{u.title}': {u.assumption[:120]}...",
        request=request
    )

    return ApiResponse(
        success=True,
        data={
            "id": u.id,
            "title": u.title,
            "status": u.status,
            "assumption": u.assumption,
            "user_clarification": u.user_clarification
        },
        message=f"Assumption for '{u.title}' saved and resolved."
    )

@router.post("/{uncertainty_id}/reject", response_model=ApiResponse)
async def reject_uncertainty(
    uncertainty_id: str,
    payload: RejectUncertaintyRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Dismiss or reject an uncertainty item (e.g. out of scope or non-applicable).
    """
    res = await db.execute(select(RequirementUncertainty).filter(RequirementUncertainty.id == uncertainty_id))
    u = res.scalars().first()
    if not u:
        raise HTTPException(status_code=404, detail="Uncertainty record not found.")

    u.status = UncertaintyStatus.REJECTED.value
    u.resolution_action = "REJECTED"
    u.updated_at = datetime.utcnow()
    if payload.reason:
        u.user_clarification = f"Rejected: {payload.reason}"

    await db.commit()
    await db.refresh(u)

    await record_audit_log(
        db=db,
        user=current_user,
        action="REJECT_UNCERTAINTY",
        resource_type="REQUIREMENT_UNCERTAINTY",
        resource_id=u.id,
        project_id=u.project_id,
        details=f"User dismissed uncertainty '{u.title}'",
        request=request
    )

    return ApiResponse(
        success=True,
        data={
            "id": u.id,
            "title": u.title,
            "status": u.status
        },
        message=f"Uncertainty '{u.title}' dismissed."
    )

@router.post("/project/{project_id}/analyze", response_model=ApiResponse)
async def trigger_uncertainty_analysis(
    project_id: str,
    project: Project = Depends(require_project_permission(Permission.PROJECT_EDIT)),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Re-run AI uncertainty detection over project documents and problem statements.
    Preserves existing confirmed/resolved items and only surfaces newly detected unknowns.
    """
    # 1. Fetch existing uncertainties
    unc_res = await db.execute(
        select(RequirementUncertainty).filter(RequirementUncertainty.project_id == project.id)
    )
    existing = unc_res.scalars().all()
    
    # 2. Fetch source evidence
    ev_res = await db.execute(select(SourceEvidence).filter(SourceEvidence.project_id == project.id))
    source_evidences = ev_res.scalars().all()

    # 3. Analyze
    raw_items = uncertainty_analyzer.analyze_source_material(
        project_id=project.id,
        project_name=project.name,
        industry=project.industry,
        business_problem=project.business_problem,
        business_objective=project.business_objective,
        source_evidences=source_evidences,
        existing_uncertainties=existing
    )
    
    existing_titles = {u.title.lower().strip(): u for u in existing}
    new_added = 0
    
    for item in raw_items:
        key = item["title"].lower().strip()
        if key not in existing_titles:
            u_obj = RequirementUncertainty(
                id=str(uuid.uuid4()),
                project_id=project.id,
                title=item["title"],
                category=item["category"],
                severity=item["severity"],
                status=UncertaintyStatus.UNCONFIRMED.value,
                what_is_unclear=item["what_is_unclear"],
                why_unclear=item.get("why_unclear"),
                source_evidence_id=item.get("source_evidence_id"),
                source_code=item.get("source_code"),
                document_name=item.get("document_name"),
                page_number=item.get("page_number"),
                section_heading=item.get("section_heading"),
                evidence_text=item.get("evidence_text"),
                assumption=item["assumption"],
                is_high_risk_assumption=item.get("is_high_risk_assumption", False),
                what_to_confirm=item["what_to_confirm"],
                potential_impact=item["potential_impact"]
            )
            db.add(u_obj)
            new_added += 1

    await db.commit()

    # Re-fetch all
    all_unc_res = await db.execute(
        select(RequirementUncertainty)
        .filter(RequirementUncertainty.project_id == project.id)
        .order_by(RequirementUncertainty.created_at.asc())
    )
    all_uncertainties = all_unc_res.scalars().all()

    return ApiResponse(
        success=True,
        data={
            "project_id": project.id,
            "new_uncertainties_identified": new_added,
            "total_uncertainties": len(all_uncertainties)
        },
        message=f"Analysis complete. Identified {new_added} new requirement uncertainties."
    )
