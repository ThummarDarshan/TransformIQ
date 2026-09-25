from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.config.database import Base

class ArchitectureComponent(Base):
    __tablename__ = "architecture_components"
    
    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    name = Column(String(255), nullable=False)
    layer = Column(String(100), nullable=False)  # Client, API_Gateway, Application_Services, AI_Engine, Data_Storage, External_Integrations, Security
    tech_stack = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    responsibilities = Column(JSON, default=list)
    position_x = Column(Float, default=0.0)
    position_y = Column(Float, default=0.0)
    config_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="architecture_components")

class ArchitectureConnection(Base):
    __tablename__ = "architecture_connections"
    
    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    source_component_id = Column(String(36), nullable=False)
    target_component_id = Column(String(36), nullable=False)
    protocol = Column(String(50), default="HTTPS/REST")  # gRPC, REST, WebSocket, Kafka, AMQP
    data_payload = Column(String(255), nullable=True)
    is_async = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="architecture_connections")

class WorkflowNode(Base):
    __tablename__ = "workflow_nodes"
    
    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    node_key = Column(String(100), nullable=False)
    node_type = Column(String(50), nullable=False)  # start, task, ai_task, decision, human_review, end
    label = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    actor = Column(String(100), nullable=True)  # e.g., Customer, AI Engine, Support Agent
    system = Column(String(100), nullable=True)  # e.g., CRM, VectorDB, ERP
    input_data = Column(Text, nullable=True)
    output_data = Column(Text, nullable=True)
    position_x = Column(Float, default=0.0)
    position_y = Column(Float, default=0.0)
    swimlane = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="workflow_nodes")

class WorkflowEdge(Base):
    __tablename__ = "workflow_edges"
    
    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    source_node_key = Column(String(100), nullable=False)
    target_node_key = Column(String(100), nullable=False)
    label = Column(String(255), nullable=True)
    condition = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="workflow_edges")
