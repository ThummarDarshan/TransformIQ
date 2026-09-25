from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.config.database import Base

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    title = Column(String(255), default="AI Discovery Session")
    module = Column(String(50), default="DISCOVERY")  # DISCOVERY, CONSULTANT, ARCHITECT, PLANNING
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(String(36), primary_key=True, index=True)
    conversation_id = Column(String(36), ForeignKey("conversations.id"), nullable=False)
    role = Column(String(50), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    structured_data = Column(JSON, nullable=True)
    suggested_actions = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    conversation = relationship("Conversation", back_populates="messages")

class Approval(Base):
    __tablename__ = "approvals"
    
    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    artifact_type = Column(String(50), nullable=False)  # BLUEPRINT, ARCHITECTURE, PROCESS, REQUIREMENTS, ESTIMATE
    artifact_id = Column(String(36), nullable=True)
    status = Column(String(50), default="UNDER_REVIEW")  # DRAFT, UNDER_REVIEW, APPROVED, REJECTED, ARCHIVED
    requested_by = Column(String(255), nullable=False)
    reviewed_by = Column(String(255), nullable=True)
    comments = Column(Text, nullable=True)
    decision_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="approvals")

class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    author_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    section = Column(String(100), nullable=False)  # architecture, gaps, roadmap, database, blueprint
    content = Column(Text, nullable=False)
    mentions = Column(JSON, default=list)
    resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="comments")
    author = relationship("User", back_populates="comments")

class Version(Base):
    __tablename__ = "versions"
    
    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    artifact_type = Column(String(100), nullable=False)
    version_number = Column(Integer, nullable=False)
    change_summary = Column(Text, nullable=False)
    author_name = Column(String(255), default="System AI / User")
    snapshot_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="versions")

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(50), default="INFO")  # INFO, SUCCESS, WARNING, APPROVAL
    link = Column(String(255), nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    user_name = Column(String(255), nullable=True)
    action = Column(String(100), nullable=False)  # e.g., GENERATED_ARCHITECTURE, APPROVED_BLUEPRINT
    details = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="audit_logs")
    user = relationship("User", back_populates="audit_logs")

class AIRun(Base):
    __tablename__ = "ai_runs"
    
    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    agent_name = Column(String(100), nullable=False)  # ArchitectureAgent, GapAnalysisAgent, etc.
    model = Column(String(100), nullable=False)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    duration_ms = Column(Integer, default=0)
    status = Column(String(50), default="SUCCESS")  # SUCCESS, ERROR
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="ai_runs")

class ExportJob(Base):
    __tablename__ = "export_jobs"
    
    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    export_type = Column(String(50), nullable=False)  # PDF, DOCX, XLSX, PPTX
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="exports")
