export interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  created_at: string;
}

export interface AuthResponse {
  token: {
    access_token: string;
    token_type: string;
    user_id: string;
    email: string;
    full_name: string;
    role: string;
  };
  user: User;
  organization_id?: string;
  workspace_id?: string;
}

export interface Project {
  id: string;
  name: string;
  slug: string;
  description?: string;
  workspace_id: string;
  status: string;
  industry: string;
  organization_size: string;
  business_objective?: string;
  business_problem?: string;
  current_systems?: string;
  expected_outcome?: string;
  constraints?: string;
  budget: number;
  timeline_months: number;
  overall_score?: number;
  ai_readiness?: number;
  automation_potential?: number;
  created_at: string;
  updated_at: string;
}

export interface DocumentItem {
  id: string;
  filename: string;
  file_type: string;
  file_size: number;
  summary: string;
  status: string;
  created_at: string;
}

export interface ChatMessage {
  id?: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  suggested_actions?: string[];
  created_at?: string;
}

export interface Requirement {
  code: string;
  title: string;
  description: string;
  req_type: string;
  priority: string;
  source?: string;
}

export interface Stakeholder {
  name: string;
  role: string;
  department: string;
  influence: string;
  interest: string;
  key_concerns: string;
}

export interface AsIsStep {
  step_number: number;
  activity: string;
  actor: string;
  system: string;
  duration: string;
  pain_point?: string;
  is_bottleneck: boolean;
}

export interface BusinessAnalysisData {
  business_summary: string;
  objectives: string[];
  stakeholders: Stakeholder[];
  functional_requirements: Requirement[];
  non_functional_requirements: Requirement[];
  pain_points: string[];
  as_is_process: AsIsStep[];
  constraints: string[];
  assumptions: string[];
  kpis: string[];
  confidence_level: number;
}

export interface GapItem {
  id?: string;
  category: string;
  title: string;
  current_state: string;
  desired_state: string;
  severity: string;
  impact: string;
  root_cause: string;
  recommended_action: string;
}

export interface GapAnalysisData {
  summary: string;
  total_gaps_count: number;
  critical_count: number;
  high_count: number;
  medium_count: number;
  gaps: GapItem[];
}

export interface RecommendationItem {
  id: string;
  category: string;
  title: string;
  description: string;
  reason: string;
  expected_impact: string;
  feasibility: string;
  priority: string;
  confidence_score: number;
  source_citation?: string;
  dependencies: string[];
  status: string;
}

export interface SolutionData {
  recommended_solution_name: string;
  tagline: string;
  executive_summary: string;
  key_capabilities: string[];
  expected_roi: string;
  technology_stack: Record<string, string[]>;
  recommendations: RecommendationItem[];
  alternative_solutions?: { name: string; pros: string; cons: string; verdict: string }[];
}

export interface ArchitectureComponent {
  id: string;
  name: string;
  layer: string;
  tech_stack: string;
  description: string;
  responsibilities: string[];
  position_x: number;
  position_y: number;
}

export interface ArchitectureConnection {
  id?: string;
  source: string;
  target: string;
  protocol: string;
  data_payload?: string;
  is_async: boolean;
}

export interface ArchitectureData {
  hld_overview: string;
  deployment_model: string;
  security_boundaries: string[];
  data_flow_summary: string;
  components: ArchitectureComponent[];
  connections: ArchitectureConnection[];
  lld_services?: { name: string; purpose: string }[];
}

export interface WorkflowNodeItem {
  id: string;
  node_key: string;
  node_type: string;
  label: string;
  description: string;
  actor: string;
  system: string;
  input_data?: string;
  output_data?: string;
  swimlane?: string;
  position_x: number;
  position_y: number;
}

export interface WorkflowEdgeItem {
  id?: string;
  source: string;
  target: string;
  label?: string;
  condition?: string;
}

export interface ProcessWorkflowData {
  process_name: string;
  process_summary: string;
  cycle_time_current: string;
  cycle_time_projected: string;
  efficiency_gain: string;
  swimlanes: string[];
  nodes: WorkflowNodeItem[];
  edges: WorkflowEdgeItem[];
}

export interface DatabaseField {
  name: string;
  type: string;
  is_primary: boolean;
  is_foreign: boolean;
  is_nullable: boolean;
  description?: string;
}

export interface DatabaseEntity {
  id?: string;
  name: string;
  description: string;
  fields: DatabaseField[];
  relationships?: { target: string; type: string }[];
  indexes?: string[];
}

export interface DatabaseData {
  overview: string;
  entities: DatabaseEntity[];
  sql_ddl?: string;
}

export interface ApiEndpoint {
  id?: string;
  method: string;
  path: string;
  summary: string;
  description: string;
  category: string;
  auth_required: boolean;
  request_body?: Record<string, any>;
  response_body?: Record<string, any>;
  error_responses?: { code: number; message: string }[];
}

export interface ApiCatalogData {
  api_title: string;
  version: string;
  base_url: string;
  endpoints: ApiEndpoint[];
  openapi_spec?: Record<string, any>;
}

export interface WireframeComponent {
  type: string;
  label: string;
  props?: Record<string, any>;
}

export interface WireframeItem {
  id?: string;
  screen_name: string;
  purpose: string;
  target_users: string[];
  layout_type: string;
  components: WireframeComponent[];
  user_actions: string[];
}

export interface UxData {
  ux_strategy: string;
  personas: { name: string; role: string; goals: string[]; pain_points: string[] }[];
  user_journey_stages: { stage: string; description: string }[];
  wireframes: WireframeItem[];
}

export interface RoadmapTask {
  title: string;
  duration: string;
  owner: string;
  deliverable: string;
}

export interface RoadmapPhase {
  phase_name: string;
  duration_weeks: number;
  objective: string;
  tasks: RoadmapTask[];
  milestones: string[];
  risks: string[];
}

export interface RoleEstimate {
  role: string;
  headcount: number;
  hours: number;
  rate_hourly: number;
  cost: number;
}

export interface PlanningData {
  roadmap: {
    name: string;
    total_duration_weeks: number;
    phases: RoadmapPhase[];
  };
  estimate: {
    total_estimated_hours: number;
    total_estimated_cost: number;
    currency: string;
    duration_months: number;
    roles_breakdown: RoleEstimate[];
    infrastructure_cost_monthly: number;
    ai_api_cost_monthly: number;
    assumptions: string[];
    confidence_level: string;
    disclaimer: string;
  };
}

export interface RiskItem {
  id?: string;
  category: string;
  title: string;
  description: string;
  probability: string;
  impact: string;
  severity: string;
  mitigation_strategy: string;
  owner: string;
  status: string;
}

export interface TransformationScoreData {
  overall_score: number;
  ai_readiness: number;
  automation_potential: number;
  data_readiness: number;
  business_impact: number;
  technical_feasibility: number;
  implementation_readiness: number;
  key_drivers: string[];
  key_blockers: string[];
  strategic_recommendations: string[];
  disclaimer: string;
}

export interface SimulationResult {
  scenario_name: string;
  automation_level: number;
  team_size: number;
  budget: number;
  timeline_months: number;
  ai_adoption_level: string;
  projected_effort_hours: number;
  projected_cost: number;
  projected_timeline_months: number;
  expected_roi_percentage: number;
  efficiency_gain_percentage: number;
  risk_level: string;
  simulation_insights: string[];
}

export interface MasterBlueprintData {
  project_id: string;
  project_name: string;
  industry: string;
  generated_at: string;
  executive_summary: string;
  business_problem: string;
  objectives: string[];
  transformation_score: TransformationScoreData;
  key_gaps: GapItem[];
  recommended_solution: {
    name: string;
    tagline: string;
    expected_roi: string;
    technology_stack: Record<string, string[]>;
    key_capabilities: string[];
    recommendations_count: number;
  };
  architecture_summary: {
    components_count: number;
    layers: string[];
    deployment: string;
  };
  process_summary: {
    nodes_count: number;
    cycle_time_current: string;
    cycle_time_projected: string;
    efficiency_gain: string;
  };
  database_summary: {
    entities_count: number;
    tables: string[];
  };
  api_summary: {
    endpoints_count: number;
    version: string;
    spec: string;
  };
  ux_summary: {
    wireframes_count: number;
    target_personas: string[];
  };
  roadmap_summary: {
    total_duration_weeks: number;
    phases_count: number;
  };
  estimate_summary: {
    total_hours: number;
    total_cost: number;
    duration_months: number;
    currency: string;
  };
  risks_summary: {
    total_risks: number;
    mitigations_active: boolean;
  };
  approval_status: string;
  reviewed_by?: string;
  decision_date?: string;
}
