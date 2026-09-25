import enum
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.config.database import Base

class ProjectStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    DISCOVERY = "DISCOVERY"
    ANALYSIS = "ANALYSIS"
    RECOMMENDATION = "RECOMMENDATION"
    DESIGN = "DESIGN"
    PLANNING = "PLANNING"
    APPROVED = "APPROVED"
    COMPLETED = "COMPLETED"

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), index=True, nullable=False)
    description = Column(Text, nullable=True)
    workspace_id = Column(String(36), ForeignKey("workspaces.id"), nullable=False)
    status = Column(String(50), default=ProjectStatus.DRAFT.value)
    
    # Business attributes
    industry = Column(String(100), nullable=True)
    organization_size = Column(String(50), nullable=True)
    business_objective = Column(Text, nullable=True)
    business_problem = Column(Text, nullable=True)
    current_systems = Column(Text, nullable=True)
    expected_outcome = Column(Text, nullable=True)
    constraints = Column(Text, nullable=True)
    budget = Column(Float, nullable=True)
    timeline_months = Column(Integer, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    workspace = relationship("Workspace", back_populates="projects")
    members = relationship("ProjectMember", back_populates="project", cascade="all, delete-orphan")
    business_context = relationship("BusinessContext", back_populates="project", uselist=False, cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="project", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="project", cascade="all, delete-orphan")
    
    # Transformation elements
    requirements = relationship("Requirement", back_populates="project", cascade="all, delete-orphan")
    stakeholders = relationship("Stakeholder", back_populates="project", cascade="all, delete-orphan")
    processes = relationship("BusinessProcess", back_populates="project", cascade="all, delete-orphan")
    gaps = relationship("Gap", back_populates="project", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="project", cascade="all, delete-orphan")
    solutions = relationship("Solution", back_populates="project", cascade="all, delete-orphan")
    
    # Architecture & Design
    architecture_components = relationship("ArchitectureComponent", back_populates="project", cascade="all, delete-orphan")
    architecture_connections = relationship("ArchitectureConnection", back_populates="project", cascade="all, delete-orphan")
    workflow_nodes = relationship("WorkflowNode", back_populates="project", cascade="all, delete-orphan")
    workflow_edges = relationship("WorkflowEdge", back_populates="project", cascade="all, delete-orphan")
    database_entities = relationship("DatabaseEntity", back_populates="project", cascade="all, delete-orphan")
    api_endpoints = relationship("ApiEndpoint", back_populates="project", cascade="all, delete-orphan")
    wireframes = relationship("Wireframe", back_populates="project", cascade="all, delete-orphan")
    
    # Planning & Governance
    roadmaps = relationship("Roadmap", back_populates="project", cascade="all, delete-orphan")
    estimates = relationship("Estimate", back_populates="project", cascade="all, delete-orphan")
    risks = relationship("Risk", back_populates="project", cascade="all, delete-orphan")
    scores = relationship("TransformationScore", back_populates="project", cascade="all, delete-orphan")
    simulations = relationship("SimulationScenario", back_populates="project", cascade="all, delete-orphan")
    approvals = relationship("Approval", back_populates="project", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="project", cascade="all, delete-orphan")
    versions = relationship("Version", back_populates="project", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="project", cascade="all, delete-orphan")
    exports = relationship("ExportJob", back_populates="project", cascade="all, delete-orphan")
    ai_runs = relationship("AIRun", back_populates="project", cascade="all, delete-orphan")

class BusinessContext(Base):
    __tablename__ = "business_contexts"
    
    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), unique=True, nullable=False)
    summary = Column(Text, nullable=True)
    domain_knowledge = Column(JSON, default=dict)
    key_entities = Column(JSON, default=list)
    key_metrics = Column(JSON, default=list)
    constraints_json = Column(JSON, default=list)
    assumptions = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    project = relationship("Project", back_populates="business_context")

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)  # pdf, docx, pptx, txt
    file_size = Column(Integer, nullable=False)
    storage_path = Column(String(500), nullable=False)
    extracted_text = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    status = Column(String(50), default="PROCESSED")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")

class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    
    id = Column(String(36), primary_key=True, index=True)
    document_id = Column(String(36), ForeignKey("documents.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    page_number = Column(Integer, nullable=True)
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    document = relationship("Document", back_populates="chunks")
