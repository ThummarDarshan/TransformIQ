export const VALID_ROLES = [
  'ADMIN',
  'PROJECT_OWNER',
  'BUSINESS_ANALYST',
  'SOLUTION_ARCHITECT',
  'MANAGER',
  'MEMBER',
  'VIEWER'
] as const;

export type SystemRole = typeof VALID_ROLES[number];

// Centralized Role Permissions Map
export const ROLE_PERMISSIONS: Record<string, string[]> = {
  // 1. ADMIN
  ADMIN: [
    'admin.access',
    'organization.manage',
    'workspace.manage',
    'user.manage',
    'audit.view',
    'project.view',
    'project.manage',
    'team.manage',
    'document.view',
    'document.upload',
    'document.delete',
    'version.view',
    'export.create'
  ],

  // 2. PROJECT_OWNER
  PROJECT_OWNER: [
    'workspace.manage',
    'project.view',
    'project.create',
    'project.edit',
    'project.delete',
    'project.manage',
    'team.manage',
    'document.view',
    'document.upload',
    'document.delete',
    'discovery.chat',
    'requirements.view',
    'requirements.edit',
    'stakeholders.view',
    'stakeholders.edit',
    'analysis.view',
    'analysis.run',
    'analysis.edit',
    'gap_analysis.view',
    'gap_analysis.run',
    'gap_analysis.edit',
    'recommendation.view',
    'recommendation.generate',
    'recommendation.edit',
    'recommendation.approve',
    'process.view',
    'process.generate',
    'process.edit',
    'architecture.view',
    'architecture.generate',
    'architecture.edit',
    'database.view',
    'database.generate',
    'database.edit',
    'api.view',
    'api.generate',
    'api.edit',
    'ux.view',
    'ux.generate',
    'ux.edit',
    'planning.view',
    'planning.generate',
    'planning.edit',
    'risk.view',
    'risk.edit',
    'score.view',
    'score.calculate',
    'simulation.run',
    'blueprint.view',
    'blueprint.generate',
    'blueprint.edit',
    'blueprint.approve',
    'export.create',
    'comment.create',
    'version.view',
    'version.create',
    'audit.view'
  ],

  // 3. BUSINESS_ANALYST
  BUSINESS_ANALYST: [
    'project.view',
    'document.view',
    'document.upload',
    'discovery.chat',
    'requirements.view',
    'requirements.edit',
    'stakeholders.view',
    'stakeholders.edit',
    'analysis.view',
    'analysis.run',
    'analysis.edit',
    'gap_analysis.view',
    'gap_analysis.run',
    'gap_analysis.edit',
    'recommendation.view',
    'recommendation.generate',
    'recommendation.review_ba',
    'process.view',
    'process.generate',
    'process.edit',
    'architecture.view',
    'database.view',
    'api.view',
    'ux.view',
    'ux.generate',
    'ux.edit',
    'planning.view',
    'planning.generate',
    'risk.view',
    'risk.edit',
    'score.view',
    'score.calculate',
    'simulation.run',
    'blueprint.view',
    'export.create',
    'comment.create',
    'version.view'
  ],

  // 4. SOLUTION_ARCHITECT
  SOLUTION_ARCHITECT: [
    'project.view',
    'document.view',
    'document.upload',
    'discovery.chat',
    'requirements.view',
    'stakeholders.view',
    'analysis.view',
    'gap_analysis.view',
    'recommendation.view',
    'recommendation.generate',
    'recommendation.review_arch',
    'process.view',
    'process.generate',
    'process.edit',
    'architecture.view',
    'architecture.generate',
    'architecture.edit',
    'architecture.submit',
    'database.view',
    'database.generate',
    'database.edit',
    'api.view',
    'api.generate',
    'api.edit',
    'ux.view',
    'ux.generate',
    'planning.view',
    'planning.generate',
    'risk.view',
    'risk.edit',
    'score.view',
    'score.calculate',
    'simulation.run',
    'blueprint.view',
    'export.create',
    'comment.create',
    'version.view',
    'version.create'
  ],

  // 5. MANAGER
  MANAGER: [
    'project.view',
    'document.view',
    'document.upload',
    'discovery.chat',
    'requirements.view',
    'stakeholders.view',
    'analysis.view',
    'gap_analysis.view',
    'recommendation.view',
    'recommendation.approve',
    'process.view',
    'architecture.view',
    'database.view',
    'api.view',
    'ux.view',
    'planning.view',
    'risk.view',
    'score.view',
    'simulation.run',
    'blueprint.view',
    'blueprint.approve',
    'export.create',
    'comment.create',
    'version.view',
    'audit.view'
  ],

  // 6. MEMBER
  MEMBER: [
    'project.view',
    'document.view',
    'document.upload',
    'discovery.chat',
    'requirements.view',
    'stakeholders.view',
    'analysis.view',
    'gap_analysis.view',
    'recommendation.view',
    'process.view',
    'architecture.view',
    'database.view',
    'api.view',
    'ux.view',
    'planning.view',
    'risk.view',
    'score.view',
    'simulation.run',
    'blueprint.view',
    'export.create',
    'comment.create',
    'version.view'
  ],

  // 7. VIEWER (Read-Only)
  VIEWER: [
    'project.view',
    'document.view',
    'discovery.chat',
    'requirements.view',
    'stakeholders.view',
    'analysis.view',
    'gap_analysis.view',
    'recommendation.view',
    'process.view',
    'architecture.view',
    'database.view',
    'api.view',
    'ux.view',
    'planning.view',
    'risk.view',
    'score.view',
    'blueprint.view',
    'export.create',
    'version.view'
  ]
};

// Aliases
ROLE_PERMISSIONS.OWNER = ROLE_PERMISSIONS.PROJECT_OWNER;
ROLE_PERMISSIONS.ANALYST = ROLE_PERMISSIONS.BUSINESS_ANALYST;
ROLE_PERMISSIONS.ARCHITECT = ROLE_PERMISSIONS.SOLUTION_ARCHITECT;

/**
 * Check if a role has a specific permission
 */
export function hasPermission(role: string, permissionKey: string): boolean {
  if (!role) return false;
  const roleKey = role.toUpperCase();
  const perms = ROLE_PERMISSIONS[roleKey] || [];
  return perms.includes(permissionKey);
}

/**
 * Check if a role has ANY of the specified permissions
 */
export function hasAnyPermission(role: string, permissionKeys: string[]): boolean {
  if (!role || !permissionKeys.length) return false;
  const roleKey = role.toUpperCase();
  const perms = ROLE_PERMISSIONS[roleKey] || [];
  return permissionKeys.some(key => perms.includes(key));
}

/**
 * Check if a role has ALL of the specified permissions
 */
export function hasAllPermissions(role: string, permissionKeys: string[]): boolean {
  if (!role || !permissionKeys.length) return false;
  const roleKey = role.toUpperCase();
  const perms = ROLE_PERMISSIONS[roleKey] || [];
  return permissionKeys.every(key => perms.includes(key));
}

/**
 * Helper to check view permission for a module
 */
export function canView(role: string, moduleName: string): boolean {
  return hasPermission(role, `${moduleName}.view`);
}

/**
 * Helper to check edit permission for a module
 */
export function canEdit(role: string, moduleName: string): boolean {
  return hasPermission(role, `${moduleName}.edit`);
}

/**
 * Helper to check create permission for a module
 */
export function canCreate(role: string, moduleName: string): boolean {
  return hasPermission(role, `${moduleName}.create`) || hasPermission(role, `${moduleName}.generate`);
}

/**
 * Helper to check delete permission for a module
 */
export function canDelete(role: string, moduleName: string): boolean {
  return hasPermission(role, `${moduleName}.delete`);
}

/**
 * Helper to check approve permission for a module
 */
export function canApprove(role: string, moduleName: string): boolean {
  return hasPermission(role, `${moduleName}.approve`);
}

/**
 * Check if role is read-only (e.g. VIEWER)
 */
export function isReadOnlyRole(role: string): boolean {
  return role?.toUpperCase() === 'VIEWER';
}
