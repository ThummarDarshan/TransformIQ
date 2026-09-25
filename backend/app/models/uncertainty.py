import enum
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.config.database import Base

class UncertaintyCategory(str, enum.Enum):
    BUSINESS_RULE = "BUSINESS_RULE"
    USER_ROLE = "USER_ROLE"
    WORKFLOW = "WORKFLOW"
    DATA = "DATA"
    INTEGRATION = "INTEGRATION"
    SECURITY = "SECURITY"
    COMPLIANCE = "COMPLIANCE"
    PERFORMANCE = "PERFORMANCE"
    UI_UX = "UI_UX"
    TECHNICAL_CONSTRAINT = "TECHNICAL_CONSTRAINT"
    SUCCESS_METRIC = "SUCCESS_METRIC"
    SCOPE = "SCOPE"
    TIMELINE = "TIMELINE"
    BUDGET = "BUDGET"
    OTHER = "OTHER"

class UncertaintySeverity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class UncertaintyStatus(str, enum.Enum):
    UNCONFIRMED = "UNCONFIRMED"
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"
    RESOLVED = "RESOLVED"

class RequirementUncertainty(Base):
    """
    Structured Uncertainty / Assumption Model:
    Tracks ambiguous, incomplete, contradictory, or missing requirements
    along with explicit AI assumptions, source citations, user confirmations,
    and downstream architecture/workflow impact.
    """
    __tablename__ = "requirement_uncertainties"
    
    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    
    title = Column(String(255), nullable=False)
    category = Column(String(50), default=UncertaintyCategory.BUSINESS_RULE.value, index=True)
    severity = Column(String(50), default=UncertaintySeverity.MEDIUM.value, index=True)
    status = Column(String(50), default=UncertaintyStatus.UNCONFIRMED.value, index=True)
    
    what_is_unclear = Column(Text, nullable=False)
    why_unclear = Column(Text, nullable=True)
    
    # Source-Linked Evidence Citation
    source_evidence_id = Column(String(36), ForeignKey("source_evidence.id", ondelete="SET NULL"), nullable=True)
    source_code = Column(String(50), nullable=True) # e.g. "SRC-102"
    document_name = Column(String(255), nullable=True)
    page_number = Column(Integer, nullable=True)
    section_heading = Column(String(255), nullable=True)
    evidence_text = Column(Text, nullable=True) # Verbatim sentence quote or explicit missing note
    
    # AI Assumption & Governance
    assumption = Column(Text, nullable=False) # e.g. "No eligibility threshold was assumed."
    is_high_risk_assumption = Column(Boolean, default=False)
    what_to_confirm = Column(Text, nullable=False) # e.g. "Define eligibility criteria for automated claims."
    potential_impact = Column(Text, nullable=False) # e.g. "Affects STP automation rate and exception routing logic."
    
    # User Confirmation & Feedback Loop
    user_clarification = Column(Text, nullable=True) # User-provided truth fed back into generation
    confirmed_by_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    confirmed_at = Column(DateTime, nullable=True)
    resolution_action = Column(String(50), nullable=True) # "CONFIRMED", "EDITED_ASSUMPTION", "REJECTED"
    
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="uncertainties")
    source_evidence = relationship("SourceEvidence", foreign_keys=[source_evidence_id])
    confirmed_by = relationship("User", foreign_keys=[confirmed_by_id])
