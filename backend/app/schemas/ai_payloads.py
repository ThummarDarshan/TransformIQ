from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field

# --- Discovery Chat ---
class ChatMessageRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    language: Optional[str] = "en"  # en, hi, gu

class ChatMessageResponse(BaseModel):
    conversation_id: str
    message: str
    suggested_actions: List[str] = []
    extracted_insights: Optional[Dict[str, Any]] = None

# --- Business Analysis ---
class RequirementItem(BaseModel):
    code: str
    title: str
    description: str
    req_type: str = "FUNCTIONAL"  # FUNCTIONAL, NON_FUNCTIONAL, BUSINESS, COMPLIANCE
    priority: str = "HIGH"  # CRITICAL, HIGH, MEDIUM, LOW
    source: Optional[str] = "Document Context"

class StakeholderItem(BaseModel):
    name: str
    role: str
    department: str
    influence: str = "HIGH"
    interest: str = "HIGH"
    key_concerns: str

class AsIsStepItem(BaseModel):
    step_number: int
    activity: str
    actor: str
    system: str
    duration: str
    pain_point: Optional[str] = None
    is_bottleneck: bool = False

class BusinessAnalysisSchema(BaseModel):
    business_summary: str
    objectives: List[str]
    stakeholders: List[StakeholderItem]
    functional_requirements: List[RequirementItem]
    non_functional_requirements: List[RequirementItem]
    pain_points: List[str]
    as_is_process: List[AsIsStepItem]
    constraints: List[str]
    assumptions: List[str]
    kpis: List[str]
    confidence_level: float = 0.94

# --- Gap Analysis ---
class GapItem(BaseModel):
    id: Optional[str] = None
    category: str  # Process, People, Technology, Data, Automation, AI, Security, Integration
    title: str
    current_state: str
    desired_state: str
    severity: str = "HIGH"  # CRITICAL, HIGH, MEDIUM, LOW
    impact: str
    root_cause: str
    recommended_action: str

class GapAnalysisSchema(BaseModel):
    summary: str
    total_gaps_count: int
    critical_count: int
    high_count: int
    medium_count: int
    gaps: List[GapItem]

# --- AI & Automation Recommendations ---
class RecommendationItem(BaseModel):
    id: Optional[str] = None
    category: str  # AI, AUTOMATION, PROCESS, ARCHITECTURE, CLOUD
    title: str
    description: str
    reason: str
    expected_impact: str = "HIGH"  # HIGH, MEDIUM, LOW
    feasibility: str = "HIGH"      # HIGH, MEDIUM, LOW
    priority: str = "HIGH"         # HIGH, MEDIUM, LOW
    confidence_score: float = 0.92
    source_citation: Optional[str] = None
    dependencies: List[str] = []
    status: str = "AI_GENERATED"

class SolutionRecommendationSchema(BaseModel):
    recommended_solution_name: str
    tagline: str
    executive_summary: str
    key_capabilities: List[str]
    expected_roi: str
    technology_stack: Dict[str, List[str]]
    recommendations: List[RecommendationItem]
    alternative_solutions: List[Dict[str, Any]] = []

# --- Architecture ---
class ArchitectureComponentItem(BaseModel):
    id: str
    name: str
    layer: str  # Client, API_Gateway, Application_Services, AI_Engine, Data_Storage, External_Integrations, Security
    tech_stack: str
    description: str
    responsibilities: List[str]
    position_x: float = 0.0
    position_y: float = 0.0

class ArchitectureConnectionItem(BaseModel):
    id: Optional[str] = None
    source: str
    target: str
    protocol: str = "HTTPS/REST"
    data_payload: Optional[str] = None
    is_async: bool = False

class ArchitectureSchema(BaseModel):
    hld_overview: str
    deployment_model: str
    security_boundaries: List[str]
    data_flow_summary: str
    components: List[ArchitectureComponentItem]
    connections: List[ArchitectureConnectionItem]
    lld_services: List[Dict[str, Any]] = []

# --- Process Intelligence / Workflow ---
class WorkflowNodeItem(BaseModel):
    id: str
    node_key: str
    node_type: str  # start, task, ai_task, decision, human_review, end
    label: str
    description: str
    actor: str
    system: str
    input_data: Optional[str] = None
    output_data: Optional[str] = None
    swimlane: Optional[str] = None
    position_x: float = 0.0
    position_y: float = 0.0

class WorkflowEdgeItem(BaseModel):
    id: Optional[str] = None
    source: str
    target: str
    label: Optional[str] = None
    condition: Optional[str] = None

class ProcessWorkflowSchema(BaseModel):
    process_name: str
    process_summary: str
    cycle_time_current: str
    cycle_time_projected: str
    efficiency_gain: str
    swimlanes: List[str] = []
    nodes: List[WorkflowNodeItem]
    edges: List[WorkflowEdgeItem]

# --- Database & APIs ---
class DatabaseFieldItem(BaseModel):
    name: str
    type: str
    is_primary: bool = False
    is_foreign: bool = False
    is_nullable: bool = False
    description: Optional[str] = None

class DatabaseEntityItem(BaseModel):
    id: Optional[str] = None
    name: str
    description: str
    fields: List[DatabaseFieldItem]
    relationships: List[Dict[str, str]] = []
    indexes: List[str] = []

class DatabaseSchemaResponse(BaseModel):
    overview: str
    entities: List[DatabaseEntityItem]
    sql_ddl: Optional[str] = None

class ApiEndpointItem(BaseModel):
    id: Optional[str] = None
    method: str
    path: str
    summary: str
    description: str
    category: str = "Core"
    auth_required: bool = True
    request_body: Optional[Dict[str, Any]] = None
    response_body: Optional[Dict[str, Any]] = None
    error_responses: List[Dict[str, Any]] = []

class ApiCatalogSchema(BaseModel):
    api_title: str
    version: str = "1.0.0"
    base_url: str = "/api/v1"
    endpoints: List[ApiEndpointItem]
    openapi_spec: Optional[Dict[str, Any]] = None

# --- UX & Wireframes ---
class UserPersonaItem(BaseModel):
    name: str
    role: str
    goals: List[str]
    pain_points: List[str]

class WireframeComponentItem(BaseModel):
    type: str  # header, stat_card, chart, table, button, form_group, badge, alert
    label: str
    props: Dict[str, Any] = {}

class WireframeItem(BaseModel):
    id: Optional[str] = None
    screen_name: str
    purpose: str
    target_users: List[str]
    layout_type: str = "DASHBOARD"
    components: List[WireframeComponentItem]
    user_actions: List[str]

class UxDesignSchema(BaseModel):
    ux_strategy: str
    personas: List[UserPersonaItem]
    user_journey_stages: List[Dict[str, Any]]
    wireframes: List[WireframeItem]

# --- Planning, Estimates & Risks ---
class RoadmapTaskItem(BaseModel):
    title: str
    duration: str
    owner: str
    deliverable: str

class RoadmapPhaseItem(BaseModel):
    phase_name: str
    duration_weeks: int
    objective: str
    tasks: List[RoadmapTaskItem]
    milestones: List[str]
    risks: List[str]

class RoadmapSchema(BaseModel):
    name: str
    total_duration_weeks: int
    phases: List[RoadmapPhaseItem]

class RoleEstimateItem(BaseModel):
    role: str
    headcount: int
    hours: int
    rate_hourly: float
    cost: float

class EstimateSchema(BaseModel):
    total_estimated_hours: int
    total_estimated_cost: float
    currency: str = "USD"
    duration_months: int
    roles_breakdown: List[RoleEstimateItem]
    infrastructure_cost_monthly: float
    ai_api_cost_monthly: float
    assumptions: List[str]
    confidence_level: str = "HIGH"
    disclaimer: str = "AI-generated preliminary estimate. Validated estimates require detailed technical discovery."

class RiskItem(BaseModel):
    id: Optional[str] = None
    category: str
    title: str
    description: str
    probability: str  # HIGH, MEDIUM, LOW
    impact: str       # HIGH, MEDIUM, LOW
    severity: str     # CRITICAL, HIGH, MEDIUM, LOW
    mitigation_strategy: str
    owner: str
    status: str = "OPEN"

class RiskMatrixSchema(BaseModel):
    summary: str
    total_risks: int
    risks: List[RiskItem]

# --- Transformation Score ---
class TransformationScoreSchema(BaseModel):
    overall_score: int
    ai_readiness: int
    automation_potential: int
    data_readiness: int
    business_impact: int
    technical_feasibility: int
    implementation_readiness: int
    key_drivers: List[str]
    key_blockers: List[str]
    strategic_recommendations: List[str]
    disclaimer: str = "AI-assisted assessment based on project inputs."

# --- What-If Simulator ---
class SimulationRequest(BaseModel):
    automation_level: int = Field(75, ge=10, le=100)
    team_size: int = Field(6, ge=1, le=50)
    budget: float = Field(150000.0, ge=10000)
    timeline_months: int = Field(4, ge=1, le=24)
    ai_adoption_level: str = "HIGH"  # LOW, MEDIUM, HIGH, AGGRESSIVE

class SimulationResponse(BaseModel):
    scenario_name: str
    automation_level: int
    team_size: int
    budget: float
    timeline_months: int
    ai_adoption_level: str
    projected_effort_hours: int
    projected_cost: float
    projected_timeline_months: float
    expected_roi_percentage: float
    efficiency_gain_percentage: float
    risk_level: str
    simulation_insights: List[str]

# --- Master Blueprint ---
class MasterBlueprintSchema(BaseModel):
    project_id: str
    project_name: str
    industry: str
    generated_at: str
    executive_summary: str
    business_problem: str
    objectives: List[str]
    transformation_score: TransformationScoreSchema
    key_gaps: List[GapItem]
    recommended_solution: SolutionRecommendationSchema
    architecture_overview: ArchitectureSchema
    process_workflow: ProcessWorkflowSchema
    database_design: DatabaseSchemaResponse
    api_catalog: ApiCatalogSchema
    ux_wireframes: UxDesignSchema
    roadmap: RoadmapSchema
    estimates: EstimateSchema
    risks: List[RiskItem]
    approval_status: str = "UNDER_REVIEW"
