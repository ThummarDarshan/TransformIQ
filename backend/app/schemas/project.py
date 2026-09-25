from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict

class OrganizationBase(BaseModel):
    name: str
    industry: Optional[str] = "Technology"
    size: Optional[str] = "1000-5000"

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationResponse(OrganizationBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    slug: str
    owner_id: str
    created_at: datetime

class WorkspaceBase(BaseModel):
    name: str
    description: Optional[str] = None

class WorkspaceCreate(WorkspaceBase):
    organization_id: str

class WorkspaceResponse(WorkspaceBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    created_at: datetime

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    industry: Optional[str] = "E-Commerce"
    organization_size: Optional[str] = "Enterprise (1000+)"
    business_objective: Optional[str] = None
    business_problem: Optional[str] = None
    current_systems: Optional[str] = None
    expected_outcome: Optional[str] = None
    constraints: Optional[str] = None
    budget: Optional[float] = 150000.0
    timeline_months: Optional[int] = 4

class ProjectCreate(ProjectBase):
    workspace_id: Optional[str] = None

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    business_objective: Optional[str] = None
    business_problem: Optional[str] = None
    current_systems: Optional[str] = None
    expected_outcome: Optional[str] = None
    constraints: Optional[str] = None
    budget: Optional[float] = None
    timeline_months: Optional[int] = None

class ProjectResponse(ProjectBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    slug: str
    workspace_id: str
    status: str
    created_at: datetime
    updated_at: datetime


class ApiResponse(BaseModel):
    success: bool = True
    data: Optional[Any] = None
    message: Optional[str] = None
    error: Optional[Dict[str, Any]] = None
