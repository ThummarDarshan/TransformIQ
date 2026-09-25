import enum
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.config.database import Base

class RequirementType(str, enum.Enum):
    FUNCTIONAL = "FUNCTIONAL"
    NON_FUNCTIONAL = "NON_FUNCTIONAL"
    BUSINESS = "BUSINESS"
    COMPLIANCE = "COMPLIANCE"
    INTEGRATION = "INTEGRATION"

class Question(Base):
    __tablename__ = "questions"
    
    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    category = Column(String(100), default="General")
    answer_text = Column(Text, nullable=True)
    suggested_answers = Column(JSON, default=list)
    is_answered = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Requirement(Base):
    __tablename__ = "requirements"
    
    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    code = Column(String(50), nullable=False)  # e.g., REQ-001
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    req_type = Column(String(50), default=RequirementType.FUNCTIONAL.value)
    priority = Column(String(50), default="HIGH")  # CRITICAL, HIGH, MEDIUM, LOW
    source = Column(String(255), nullable=True)  # e.g., BRD.pdf Page 4
    confidence = Column(Float, default=0.95)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="requirements")

class Stakeholder(Base):
    __tablename__ = "stakeholders"
    
    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(String(255), nullable=False)
    department = Column(String(255), nullable=True)
    influence = Column(String(50), default="HIGH")  # HIGH, MEDIUM, LOW
    interest = Column(String(50), default="HIGH")
    key_concerns = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="stakeholders")

class BusinessProcess(Base):
    __tablename__ = "business_processes"
    
    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    name = Column(String(255), default="Process Flow")
    description = Column(Text, nullable=True)
    step_number = Column(Integer, default=1)
    activity = Column(String(255), default="")
    actor = Column(String(255), default="")
    system = Column(String(255), default="")
    duration = Column(String(100), default="")
    is_bottleneck = Column(Boolean, default=False)
    pain_points = Column(JSON, default=list)
    as_is_steps = Column(JSON, default=list)
    to_be_steps = Column(JSON, default=list)
    cycle_time_current = Column(String(100), nullable=True)
    cycle_time_projected = Column(String(100), nullable=True)
    bottlenecks = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="processes")

class Gap(Base):
    __tablename__ = "gaps"
    
    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    category = Column(String(100), nullable=False)  # Process, People, Technology, Data, Automation, AI, Security, Integration
    title = Column(String(255), nullable=False)
    current_state = Column(Text, nullable=False)
    desired_state = Column(Text, nullable=False)
    severity = Column(String(50), default="HIGH")  # CRITICAL, HIGH, MEDIUM, LOW
    impact = Column(Text, nullable=True)
    root_cause = Column(Text, nullable=True)
    recommended_action = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="gaps")

class Recommendation(Base):
    __tablename__ = "recommendations"
    
    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    category = Column(String(50), nullable=False)  # AI, AUTOMATION, PROCESS, ARCHITECTURE, CLOUD
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    reason = Column(Text, nullable=False)
    expected_impact = Column(String(50), default="HIGH")
    feasibility = Column(String(50), default="HIGH")
    priority = Column(String(50), default="HIGH")
    confidence_score = Column(Float, default=0.92)
    source_citation = Column(String(255), nullable=True)
    dependencies = Column(JSON, default=list)
    status = Column(String(50), default="AI_GENERATED")  # AI_GENERATED, REVIEWED, TECHNICALLY_REVIEWED, APPROVED, REJECTED
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="recommendations")

class Solution(Base):
    __tablename__ = "solutions"
    
    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    name = Column(String(255), nullable=False)
    tagline = Column(String(255), nullable=True)
    executive_summary = Column(Text, nullable=False)
    technology_stack = Column(JSON, default=dict)
    key_capabilities = Column(JSON, default=list)
    expected_roi = Column(Text, nullable=True)
    implementation_approach = Column(Text, nullable=True)
    status = Column(String(50), default="ACTIVE")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    project = relationship("Project", back_populates="solutions")
