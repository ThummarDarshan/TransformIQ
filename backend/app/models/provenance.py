import enum
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.config.database import Base

class ProvenanceType(str, enum.Enum):
    DIRECT = "DIRECT"          # Explicitly stated in the source document/text
    DERIVED = "DERIVED"        # Logically inferred or synthesized from source context
    RECOMMENDED = "RECOMMENDED" # AI expert recommendation not explicitly in the source

class SourceType(str, enum.Enum):
    DOCUMENT_PDF = "DOCUMENT_PDF"
    DOCUMENT_DOCX = "DOCUMENT_DOCX"
    DOCUMENT_PPTX = "DOCUMENT_PPTX"
    DOCUMENT_TXT = "DOCUMENT_TXT"
    WEB_URL = "WEB_URL"
    BUSINESS_INPUT = "BUSINESS_INPUT"
    CHAT_DISCOVERY = "CHAT_DISCOVERY"

class SourceEvidence(Base):
    """
    Normalized canonical source evidence record.
    Represents an exact, stable citation anchor within an uploaded document, URL, or business context.
    """
    __tablename__ = "source_evidence"
    
    id = Column(String(36), primary_key=True, index=True) # e.g. UUID or SRC-001
    source_code = Column(String(50), index=True, nullable=True) # Human readable code e.g. SRC-101
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=True, index=True)
    chunk_id = Column(String(36), ForeignKey("document_chunks.id", ondelete="SET NULL"), nullable=True)
    
    document_name = Column(String(255), nullable=False) # e.g. "Customer_Complaint_BRD.pdf"
    source_type = Column(String(50), default=SourceType.DOCUMENT_PDF.value)
    
    page_number = Column(Integer, nullable=True)
    section_heading = Column(String(255), nullable=True)
    paragraph_number = Column(Integer, nullable=True)
    start_offset = Column(Integer, nullable=True)
    end_offset = Column(Integer, nullable=True)
    
    exact_text = Column(Text, nullable=False) # Verbatim sentence or paragraph from source
    source_url = Column(String(500), nullable=True)
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="source_evidences")
    document = relationship("Document", back_populates="source_evidences")
    provenance_links = relationship("ArtifactProvenance", back_populates="source_evidence", cascade="all, delete-orphan")


class ArtifactProvenance(Base):
    """
    Many-to-many provenance link associating any generated artifact/requirement
    to one or more exact SourceEvidence records with explicit rationale and classification.
    """
    __tablename__ = "artifact_provenances"
    
    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    
    artifact_type = Column(String(50), nullable=False, index=True) # REQUIREMENT, GAP, RECOMMENDATION, ARCHITECTURE, PROCESS, DATABASE, API, RISK, BLUEPRINT
    artifact_id = Column(String(100), nullable=False, index=True) # e.g. REQ-001 or UUID of requirement/gap/rec
    
    source_evidence_id = Column(String(36), ForeignKey("source_evidence.id", ondelete="CASCADE"), nullable=True, index=True)
    
    provenance_type = Column(String(50), default=ProvenanceType.DIRECT.value) # DIRECT, DERIVED, RECOMMENDED
    rationale = Column(Text, nullable=True) # Why this source evidence resulted in this generated item
    confidence_score = Column(Float, default=0.95)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    source_evidence = relationship("SourceEvidence", back_populates="provenance_links")
    project = relationship("Project")
