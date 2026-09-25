from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.uncertainty import UncertaintyCategory, UncertaintySeverity, UncertaintyStatus

class UncertaintyItemResponse(BaseModel):
    id: str
    project_id: str
    title: str
    category: str
    severity: str
    status: str
    what_is_unclear: str
    why_unclear: Optional[str] = None
    
    # Evidence & Source Linkage
    source_evidence_id: Optional[str] = None
    source_code: Optional[str] = None
    document_name: Optional[str] = None
    page_number: Optional[int] = None
    section_heading: Optional[str] = None
    evidence_text: Optional[str] = None
    
    # AI Assumption & Governance
    assumption: str
    is_high_risk_assumption: bool = False
    what_to_confirm: str
    potential_impact: str
    
    # User Confirmation Feedback
    user_clarification: Optional[str] = None
    confirmed_by_id: Optional[str] = None
    confirmed_at: Optional[datetime] = None
    resolution_action: Optional[str] = None
    
    metadata_json: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class UncertaintyStats(BaseModel):
    total_count: int = 0
    unconfirmed_count: int = 0
    confirmed_count: int = 0
    resolved_count: int = 0
    rejected_count: int = 0
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0

class UncertaintyListResponse(BaseModel):
    project_id: str
    project_name: str
    stats: UncertaintyStats
    uncertainties: List[UncertaintyItemResponse]

class ConfirmUncertaintyRequest(BaseModel):
    user_clarification: str = Field(..., min_length=2, description="The user's definitive answer / business rule confirmation")

class EditAssumptionRequest(BaseModel):
    assumption: str = Field(..., min_length=2, description="Modified or accepted assumption")
    user_clarification: Optional[str] = None

class RejectUncertaintyRequest(BaseModel):
    reason: Optional[str] = Field(None, description="Reason for rejecting or dismissing this uncertainty")
