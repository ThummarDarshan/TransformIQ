import {
  LayoutDashboard,
  Building2,
  Users,
  Lock,
  Layers,
  FolderKanban,
  Cpu,
  Activity,
  ShieldCheck,
  Key,
  Sliders,
  Compass,
  FileText,
  FileSearch,
  ListTodo,
  UserCheck,
  GitBranch,
  Split,
  Sparkles,
  GitMerge,
  Database,
  Code2,
  Layout,
  CalendarDays,
  AlertTriangle,
  Award,
  FileCheck,
  Download,
  MessageSquare,
  History,
  CheckCircle2,
  LucideIcon
} from 'lucide-react';
import { hasPermission } from '../utils/permissions';

export interface SidebarItemConfig {
  id: string;
  label: string;
  icon: LucideIcon;
  route: string;
  requiredPermission: string;
  section: 'admin' | 'main' | 'transformation' | 'collaboration' | 'governance';
  order: number;
  step?: string | null;
  badge?: string;
  subItems?: { label: string; route: string; tab: string }[];
}

export interface RoleInfo {
  role: string;
  displayName: string;
  subtitle: string;
  description: string;
  color: {
    bg: string;
    text: string;
    border: string;
    badgeBg: string;
  };
}

export const ROLE_DEFINITIONS: Record<string, RoleInfo> = {
  ADMIN: {
    role: 'ADMIN',
    displayName: 'Admin',
    subtitle: 'Sarah Connor',
    description: 'Platform, Organization & Governance Control',
    color: {
      bg: 'bg-rose-500/20',
      text: 'text-rose-400',
      border: 'border-rose-500/40',
      badgeBg: 'bg-rose-500/10 text-rose-300 border-rose-500/30'
    }
  },
  PROJECT_OWNER: {
    role: 'PROJECT_OWNER',
    displayName: 'Project Owner',
    subtitle: 'Elena Rostova',
    description: 'Full End-to-End Transformation Ownership',
    color: {
      bg: 'bg-amber-500/20',
      text: 'text-amber-400',
      border: 'border-amber-500/40',
      badgeBg: 'bg-amber-500/10 text-amber-300 border-amber-500/30'
    }
  },
  BUSINESS_ANALYST: {
    role: 'BUSINESS_ANALYST',
    displayName: 'Business Analyst',
    subtitle: 'Priya Sharma',
    description: 'Requirements, Stakeholders & Gap Analysis',
    color: {
      bg: 'bg-emerald-500/20',
      text: 'text-emerald-400',
      border: 'border-emerald-500/40',
      badgeBg: 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30'
    }
  },
  SOLUTION_ARCHITECT: {
    role: 'SOLUTION_ARCHITECT',
    displayName: 'Solution Architect',
    subtitle: 'David Vance',
    description: 'HLD Architecture, BPMN, Schemas & API Design',
    color: {
      bg: 'bg-indigo-500/20',
      text: 'text-indigo-400',
      border: 'border-indigo-500/40',
      badgeBg: 'bg-indigo-500/10 text-indigo-300 border-indigo-500/30'
    }
  },
  MANAGER: {
    role: 'MANAGER',
    displayName: 'Manager',
    subtitle: 'Marcus Chen',
    description: 'Executive Review, Score & Blueprint Approval',
    color: {
      bg: 'bg-purple-500/20',
      text: 'text-purple-400',
      border: 'border-purple-500/40',
      badgeBg: 'bg-purple-500/10 text-purple-300 border-purple-500/30'
    }
  },
  MEMBER: {
    role: 'MEMBER',
    displayName: 'Member',
    subtitle: 'Liam O’Connor',
    description: 'Core Team Contributor & Task Execution',
    color: {
      bg: 'bg-blue-500/20',
      text: 'text-blue-400',
      border: 'border-blue-500/40',
      badgeBg: 'bg-blue-500/10 text-blue-300 border-blue-500/30'
    }
  },
  VIEWER: {
    role: 'VIEWER',
    displayName: 'Viewer',
    subtitle: 'Victoria Sterling',
    description: 'Read-Only Stakeholder & Audit Reviewer',
    color: {
      bg: 'bg-slate-500/20',
      text: 'text-slate-400',
      border: 'border-slate-500/40',
      badgeBg: 'bg-slate-500/10 text-slate-300 border-slate-500/30'
    }
  }
};

// Complete catalog of possible navigation items
export const ALL_NAV_ITEMS: Record<string, SidebarItemConfig> = {
  // Admin Modules (Section 5)
  admin_dashboard: {
    id: 'admin_dashboard',
    label: 'Dashboard',
    icon: LayoutDashboard,
    route: '/admin?tab=dashboard',
    requiredPermission: 'admin.access',
    section: 'admin',
    order: 10
  },
  admin_organization: {
    id: 'admin_organization',
    label: 'Organization',
    icon: Building2,
    route: '/admin?tab=organization',
    requiredPermission: 'organization.manage',
    section: 'admin',
    order: 20,
    subItems: [
      { label: 'Organization Settings', route: '/admin?tab=organization', tab: 'organization' }
    ]
  },
  admin_users: {
    id: 'admin_users',
    label: 'Users',
    icon: Users,
    route: '/admin?tab=users',
    requiredPermission: 'user.manage',
    section: 'admin',
    order: 30
  },
  admin_roles: {
    id: 'admin_roles',
    label: 'Roles & Permissions',
    icon: Lock,
    route: '/admin?tab=roles',
    requiredPermission: 'admin.access',
    section: 'admin',
    order: 40
  },
  admin_workspaces: {
    id: 'admin_workspaces',
    label: 'Workspaces',
    icon: Layers,
    route: '/admin?tab=workspaces',
    requiredPermission: 'workspace.manage',
    section: 'admin',
    order: 50
  },
  admin_projects: {
    id: 'admin_projects',
    label: 'Projects',
    icon: FolderKanban,
    route: '/admin?tab=projects',
    requiredPermission: 'project.view',
    section: 'admin',
    order: 60
  },
  admin_ai_usage: {
    id: 'admin_ai_usage',
    label: 'AI Usage',
    icon: Cpu,
    route: '/admin?tab=ai-usage',
    requiredPermission: 'admin.access',
    section: 'admin',
    order: 70
  },
  admin_analytics: {
    id: 'admin_analytics',
    label: 'System Analytics',
    icon: Activity,
    route: '/admin?tab=analytics',
    requiredPermission: 'admin.access',
    section: 'admin',
    order: 80
  },
  admin_audit_logs: {
    id: 'admin_audit_logs',
    label: 'Audit Logs',
    icon: ShieldCheck,
    route: '/admin?tab=audit-logs',
    requiredPermission: 'audit.view',
    section: 'admin',
    order: 90
  },
  admin_integrations: {
    id: 'admin_integrations',
    label: 'Integrations',
    icon: Key,
    route: '/admin?tab=integrations',
    requiredPermission: 'admin.access',
    section: 'admin',
    order: 100
  },
  admin_settings: {
    id: 'admin_settings',
    label: 'System Settings',
    icon: Sliders,
    route: '/admin?tab=settings',
    requiredPermission: 'admin.access',
    section: 'admin',
    order: 110
  },

  // Main Platform
  dashboard: {
    id: 'dashboard',
    label: 'Dashboard',
    icon: LayoutDashboard,
    route: '/dashboard',
    requiredPermission: 'project.view',
    section: 'main',
    order: 1
  },
  projects: {
    id: 'projects',
    label: 'Projects',
    icon: FolderKanban,
    route: '/projects',
    requiredPermission: 'project.view',
    section: 'main',
    order: 2
  },

  // 13 Connected Pipeline Transformation Stages (with clean Steps 01 to 13)
  discovery: {
    id: 'discovery',
    label: 'Discovery',
    icon: Compass,
    route: '/projects/:projectId/discovery',
    requiredPermission: 'discovery.chat',
    section: 'transformation',
    order: 10,
    step: '01'
  },
  business_analysis: {
    id: 'business_analysis',
    label: 'Business Analysis',
    icon: FileSearch,
    route: '/projects/:projectId/business-analysis',
    requiredPermission: 'analysis.view',
    section: 'transformation',
    order: 20,
    step: '02'
  },
  gap_analysis: {
    id: 'gap_analysis',
    label: 'Gap Analysis',
    icon: Split,
    route: '/projects/:projectId/gap-analysis',
    requiredPermission: 'gap_analysis.view',
    section: 'transformation',
    order: 30,
    step: '03'
  },
  ai_recommendations: {
    id: 'ai_recommendations',
    label: 'AI Recommendations',
    icon: Sparkles,
    route: '/projects/:projectId/recommendations',
    requiredPermission: 'recommendation.view',
    section: 'transformation',
    order: 40,
    step: '04'
  },
  solution_architecture: {
    id: 'solution_architecture',
    label: 'Architecture',
    icon: Cpu,
    route: '/projects/:projectId/architecture',
    requiredPermission: 'architecture.view',
    section: 'transformation',
    order: 50,
    step: '05'
  },
  process_intelligence: {
    id: 'process_intelligence',
    label: 'Process',
    icon: GitMerge,
    route: '/projects/:projectId/process',
    requiredPermission: 'process.view',
    section: 'transformation',
    order: 60,
    step: '06'
  },
  database_design: {
    id: 'database_design',
    label: 'Database',
    icon: Database,
    route: '/projects/:projectId/database',
    requiredPermission: 'database.view',
    section: 'transformation',
    order: 70,
    step: '07'
  },
  api_design: {
    id: 'api_design',
    label: 'APIs',
    icon: Code2,
    route: '/projects/:projectId/apis',
    requiredPermission: 'api.view',
    section: 'transformation',
    order: 80,
    step: '08'
  },
  ux_design: {
    id: 'ux_design',
    label: 'UX',
    icon: Layout,
    route: '/projects/:projectId/ux',
    requiredPermission: 'ux.view',
    section: 'transformation',
    order: 90,
    step: '09'
  },
  planning: {
    id: 'planning',
    label: 'Planning',
    icon: CalendarDays,
    route: '/projects/:projectId/planning',
    requiredPermission: 'planning.view',
    section: 'transformation',
    order: 100,
    step: '10'
  },
  simulation: {
    id: 'simulation',
    label: 'Simulation',
    icon: Sliders,
    route: '/projects/:projectId/simulation',
    requiredPermission: 'simulation.run',
    section: 'transformation',
    order: 110,
    step: '11'
  },
  transformation_score: {
    id: 'transformation_score',
    label: 'Score',
    icon: Award,
    route: '/projects/:projectId/score',
    requiredPermission: 'score.view',
    section: 'transformation',
    order: 120,
    step: '12'
  },
  final_blueprint: {
    id: 'final_blueprint',
    label: 'Blueprint',
    icon: FileCheck,
    route: '/projects/:projectId/blueprint',
    requiredPermission: 'blueprint.view',
    section: 'transformation',
    order: 130,
    step: '13'
  },

  // Governance & Collaboration
  collaboration: {
    id: 'collaboration',
    label: 'Collaboration & Logs',
    icon: Users,
    route: '/projects/:projectId/collaboration',
    requiredPermission: 'project.view',
    section: 'collaboration',
    order: 140
  }
};

/**
 * Role-to-Sidebar Map matching the Page Access Matrix
 */
export const ROLE_SIDEBAR_CONFIG: Record<string, string[]> = {
  // 1. ADMIN
  ADMIN: [
    'admin_dashboard',
    'admin_organization',
    'admin_users',
    'admin_roles',
    'admin_workspaces',
    'admin_projects',
    'admin_ai_usage',
    'admin_analytics',
    'admin_audit_logs',
    'admin_integrations',
    'admin_settings'
  ],

  // 2. PROJECT OWNER (Full Access across all 13 stages)
  PROJECT_OWNER: [
    'dashboard',
    'projects',
    'discovery',
    'business_analysis',
    'gap_analysis',
    'ai_recommendations',
    'solution_architecture',
    'process_intelligence',
    'database_design',
    'api_design',
    'ux_design',
    'planning',
    'simulation',
    'transformation_score',
    'final_blueprint',
    'collaboration'
  ],

  // 3. BUSINESS ANALYST (Discovery, BA, Gaps, Recommendations, UX, Planning, Simulation, Score, Blueprint, Collab)
  BUSINESS_ANALYST: [
    'dashboard',
    'projects',
    'discovery',
    'business_analysis',
    'gap_analysis',
    'ai_recommendations',
    'solution_architecture',
    'process_intelligence',
    'ux_design',
    'planning',
    'simulation',
    'transformation_score',
    'final_blueprint',
    'collaboration'
  ],

  // 4. SOLUTION ARCHITECT (Architecture, Process, DB, APIs, UX, Planning, Simulation, Score, Blueprint, Collab)
  SOLUTION_ARCHITECT: [
    'dashboard',
    'projects',
    'discovery',
    'business_analysis',
    'gap_analysis',
    'ai_recommendations',
    'solution_architecture',
    'process_intelligence',
    'database_design',
    'api_design',
    'ux_design',
    'planning',
    'simulation',
    'transformation_score',
    'final_blueprint',
    'collaboration'
  ],

  // 5. MANAGER (Executive overview, Business Analysis, Gaps, Recommendations, Architecture, Planning, Simulation, Score, Blueprint, Collab)
  MANAGER: [
    'dashboard',
    'projects',
    'discovery',
    'business_analysis',
    'gap_analysis',
    'ai_recommendations',
    'solution_architecture',
    'process_intelligence',
    'planning',
    'simulation',
    'transformation_score',
    'final_blueprint',
    'collaboration'
  ],

  // 6. MEMBER (Discovery, BA, Gaps, Recommendations, Process, Score, Blueprint, Collab)
  MEMBER: [
    'dashboard',
    'projects',
    'discovery',
    'business_analysis',
    'gap_analysis',
    'ai_recommendations',
    'process_intelligence',
    'transformation_score',
    'final_blueprint',
    'collaboration'
  ],

  // 7. VIEWER (Read-Only across standard stages)
  VIEWER: [
    'dashboard',
    'projects',
    'discovery',
    'business_analysis',
    'gap_analysis',
    'ai_recommendations',
    'solution_architecture',
    'process_intelligence',
    'transformation_score',
    'final_blueprint',
    'collaboration'
  ]
};

/**
 * Returns formatted sidebar navigation items for the given evaluation role and active project ID
 */
export function getSidebarItemsForRole(
  role: string,
  projectId: string = ''
): SidebarItemConfig[] {
  const roleKey = role?.toUpperCase() || 'VIEWER';
  const itemKeys = ROLE_SIDEBAR_CONFIG[roleKey] || ROLE_SIDEBAR_CONFIG.VIEWER;

  return itemKeys
    .map(key => ALL_NAV_ITEMS[key])
    .filter(Boolean)
    .filter(item => hasPermission(roleKey, item.requiredPermission))
    .map(item => ({
      ...item,
      route: projectId && projectId !== 'default'
        ? item.route.replace(':projectId', projectId)
        : (item.route.includes(':projectId') ? '/projects' : item.route)
    }));
}

/**
 * Route-to-Permission mapping used by RouteGuard
 */
export const ROUTE_PERMISSION_MAP: { pattern: RegExp; permission: string; moduleName: string }[] = [
  { pattern: /^\/admin/, permission: 'admin.access', moduleName: 'Admin Control Center' },
  { pattern: /^\/dashboard/, permission: 'project.view', moduleName: 'Dashboard' },
  { pattern: /^\/projects$/, permission: 'project.view', moduleName: 'Projects' },
  { pattern: /\/projects\/[^/]+\/discovery/, permission: 'discovery.chat', moduleName: 'Discovery' },
  { pattern: /\/projects\/[^/]+\/business-analysis/, permission: 'analysis.view', moduleName: 'Business Analysis' },
  { pattern: /\/projects\/[^/]+\/gap-analysis/, permission: 'gap_analysis.view', moduleName: 'Gap Analysis' },
  { pattern: /\/projects\/[^/]+\/recommendations/, permission: 'recommendation.view', moduleName: 'AI Recommendations' },
  { pattern: /\/projects\/[^/]+\/architecture/, permission: 'architecture.view', moduleName: 'Solution Architecture' },
  { pattern: /\/projects\/[^/]+\/process/, permission: 'process.view', moduleName: 'Process Intelligence' },
  { pattern: /\/projects\/[^/]+\/database/, permission: 'database.view', moduleName: 'Database Design' },
  { pattern: /\/projects\/[^/]+\/apis/, permission: 'api.view', moduleName: 'API Design' },
  { pattern: /\/projects\/[^/]+\/ux/, permission: 'ux.view', moduleName: 'UX Design' },
  { pattern: /\/projects\/[^/]+\/planning/, permission: 'planning.view', moduleName: 'Planning & Estimation' },
  { pattern: /\/projects\/[^/]+\/simulation/, permission: 'simulation.run', moduleName: 'Scenario Simulation' },
  { pattern: /\/projects\/[^/]+\/score/, permission: 'score.view', moduleName: 'Transformation Score' },
  { pattern: /\/projects\/[^/]+\/blueprint/, permission: 'blueprint.view', moduleName: 'Master Blueprint' },
  { pattern: /\/projects\/[^/]+\/collaboration/, permission: 'project.view', moduleName: 'Collaboration & Team' }
];

/**
 * Checks if an active path is authorized for the given role
 */
export function checkRouteAccess(
  pathname: string,
  role: string
): { authorized: boolean; moduleName: string; requiredPermission: string } {
  for (const entry of ROUTE_PERMISSION_MAP) {
    if (entry.pattern.test(pathname)) {
      const authorized = hasPermission(role, entry.permission);
      return {
        authorized,
        moduleName: entry.moduleName,
        requiredPermission: entry.permission
      };
    }
  }

  return { authorized: true, moduleName: 'General Module', requiredPermission: 'project.view' };
}
