from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.config.database import Base

class DatabaseEntity(Base):
    __tablename__ = "database_entities"
    
    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    name = Column(String(100), nullable=False)  # e.g., tickets, complaints
    description = Column(Text, nullable=True)
    table_type = Column(String(50), default="TABLE")  # TABLE, VIEW, ENUM
    fields_data = Column(JSON, default=list)  # list of field dicts
    indexes = Column(JSON, default=list)
    relationships_data = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="database_entities")

    def __init__(self, **kwargs):
        if "fields" in kwargs and "fields_data" not in kwargs:
            kwargs["fields_data"] = kwargs.pop("fields")
        if "relationships" in kwargs and "relationships_data" not in kwargs:
            kwargs["relationships_data"] = kwargs.pop("relationships")
        super().__init__(**kwargs)

    @property
    def fields(self):
        return self.fields_data

    @fields.setter
    def fields(self, val):
        self.fields_data = val

    @property
    def relationships(self):
        return self.relationships_data

    @relationships.setter
    def relationships(self, val):
        self.relationships_data = val

class ApiEndpoint(Base):
    __tablename__ = "api_endpoints"
    
    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    method = Column(String(10), nullable=False)  # GET, POST, PUT, DELETE, PATCH
    path = Column(String(255), nullable=False)
    summary = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), default="Core")
    auth_required = Column(Boolean, default=True)
    request_body = Column(JSON, default=dict)
    response_body = Column(JSON, default=dict)
    error_responses = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="api_endpoints")

    def __init__(self, **kwargs):
        if "request_schema" in kwargs and "request_body" not in kwargs:
            kwargs["request_body"] = kwargs.pop("request_schema")
        if "response_schema" in kwargs and "response_body" not in kwargs:
            kwargs["response_body"] = kwargs.pop("response_schema")
        super().__init__(**kwargs)

    @property
    def request_schema(self):
        return self.request_body

    @request_schema.setter
    def request_schema(self, val):
        self.request_body = val

    @property
    def response_schema(self):
        return self.response_body

    @response_schema.setter
    def response_schema(self, val):
        self.response_body = val

class Wireframe(Base):
    __tablename__ = "wireframes"
    
    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    screen_name = Column(String(255), nullable=False)
    purpose = Column(Text, nullable=False)
    target_users = Column(JSON, default=list)
    layout_type = Column(String(50), default="DASHBOARD")  # DASHBOARD, FORM, LIST, DETAIL, MODAL
    components_json = Column(JSON, default=list)
    user_actions = Column(JSON, default=list)
    preview_mockup = Column(JSON, default=dict)  # structured UI components for frontend interactive rendering
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="wireframes")
