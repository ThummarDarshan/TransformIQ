from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.config.database import Base

class Roadmap(Base):
    __tablename__ = "roadmaps"
    
    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    name = Column(String(255), nullable=False)
    total_duration_weeks = Column(Integer, default=12)
    phases = Column(JSON, default=list)  # list of phase objects with tasks, milestones, deliverables
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="roadmaps")

class Estimate(Base):
    __tablename__ = "estimates"
    
    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    total_estimated_hours = Column(Integer, default=0)
    total_estimated_cost = Column(Float, default=0.0)
    currency = Column(String(10), default="USD")
    duration_months = Column(Integer, default=3)
    roles_breakdown = Column(JSON, default=list)  # AI Engineer, Backend, Frontend, DevOps, QA, PM, Solution Architect
    infrastructure_cost = Column(Float, default=0.0)
    ai_api_cost_monthly = Column(Float, default=0.0)
    assumptions = Column(JSON, default=list)
    confidence_level = Column(String(50), default="MEDIUM")
    disclaimer = Column(String(500), default="AI-generated preliminary estimate. Validated estimates require detailed technical discovery.")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="estimates")

class Risk(Base):
    __tablename__ = "risks"
    
    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    category = Column(String(50), nullable=False)  # Technical, Business, AI, Security, Data, Integration, Adoption, Schedule
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    probability = Column(String(50), default="MEDIUM")  # HIGH, MEDIUM, LOW
    impact = Column(String(50), default="HIGH")  # HIGH, MEDIUM, LOW
    severity = Column(String(50), default="HIGH")  # CRITICAL, HIGH, MEDIUM, LOW
    mitigation_strategy = Column(Text, nullable=False)
    owner = Column(String(100), default="Lead Architect / PM")
    status = Column(String(50), default="OPEN")  # OPEN, MITIGATING, RESOLVED, ACCEPTED
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="risks")

class TransformationScore(Base):
    __tablename__ = "transformation_scores"
    
    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    overall_score = Column(Integer, nullable=False)  # 0-100
    ai_readiness = Column(Integer, nullable=False)  # 0-100
    automation_potential = Column(Integer, nullable=False)  # 0-100
    data_readiness = Column(Integer, nullable=False)  # 0-100
    business_impact = Column(Integer, nullable=False)  # 0-100
    technical_feasibility = Column(Integer, nullable=False)  # 0-100
    implementation_readiness = Column(Integer, nullable=False)  # 0-100
    score_breakdown = Column(JSON, default=dict)
    key_drivers = Column(JSON, default=list)
    key_blockers = Column(JSON, default=list)
    strategic_recommendations = Column(JSON, default=list)
    disclaimer = Column(String(500), default="AI-assisted assessment based on project inputs and enterprise artifacts.")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="scores")

class SimulationScenario(Base):
    __tablename__ = "simulation_scenarios"
    
    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    scenario_name = Column(String(255), nullable=False)
    automation_level = Column(Integer, default=75)  # percentage 0-100
    team_size = Column(Integer, default=6)
    budget = Column(Float, default=150000.0)
    timeline_months = Column(Integer, default=4)
    ai_adoption_level = Column(String(50), default="HIGH")  # LOW, MEDIUM, HIGH, AGGRESSIVE
    
    # Calculated outputs
    projected_effort_hours = Column(Integer, default=0)
    projected_cost = Column(Float, default=0.0)
    projected_timeline_months = Column(Float, default=0.0)
    expected_roi_percentage = Column(Float, default=0.0)
    efficiency_gain_percentage = Column(Float, default=0.0)
    risk_level = Column(String(50), default="MODERATE")
    simulation_insights = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="simulations")
