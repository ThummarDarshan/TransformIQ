from typing import Dict, Set, Optional, List, Union
from enum import Enum

class Permission(str, Enum):
    # Admin / Platform
    ADMIN_ACCESS = "admin.access"
    ORGANIZATION_MANAGE = "organization.manage"
    WORKSPACE_MANAGE = "workspace.manage"
    USER_MANAGE = "user.manage"
    AUDIT_VIEW = "audit.view"
    
    # Project Core
    PROJECT_VIEW = "project.view"
    PROJECT_CREATE = "project.create"
    PROJECT_EDIT = "project.edit"
    PROJECT_DELETE = "project.delete"
    PROJECT_MANAGE = "project.manage"
    TEAM_MANAGE = "team.manage"
    
    # Documents
    DOCUMENT_VIEW = "document.view"
    DOCUMENT_UPLOAD = "document.upload"
    DOCUMENT_DELETE = "document.delete"
    
    # Business Analysis & Discovery
    DISCOVERY_CHAT = "discovery.chat"
    REQUIREMENTS_VIEW = "requirements.view"
    REQUIREMENTS_EDIT = "requirements.edit"
    STAKEHOLDERS_VIEW = "stakeholders.view"
    STAKEHOLDERS_EDIT = "stakeholders.edit"
    ANALYSIS_VIEW = "analysis.view"
    ANALYSIS_RUN = "analysis.run"
    ANALYSIS_EDIT = "analysis.edit"
    GAP_ANALYSIS_VIEW = "gap_analysis.view"
    GAP_ANALYSIS_RUN = "gap_analysis.run"
    GAP_ANALYSIS_EDIT = "gap_analysis.edit"
    
    # Solutions & Recommendations
    RECOMMENDATION_VIEW = "recommendation.view"
    RECOMMENDATION_GENERATE = "recommendation.generate"
    RECOMMENDATION_EDIT = "recommendation.edit"
    RECOMMENDATION_REVIEW_BA = "recommendation.review_ba"
    RECOMMENDATION_REVIEW_ARCH = "recommendation.review_arch"
    RECOMMENDATION_APPROVE = "recommendation.approve"
    
    # Technical Architecture & Engineering
    PROCESS_VIEW = "process.view"
    PROCESS_GENERATE = "process.generate"
    PROCESS_EDIT = "process.edit"
    
    ARCHITECTURE_VIEW = "architecture.view"
    ARCHITECTURE_GENERATE = "architecture.generate"
    ARCHITECTURE_EDIT = "architecture.edit"
    ARCHITECTURE_SUBMIT = "architecture.submit"
    
    DATABASE_VIEW = "database.view"
    DATABASE_GENERATE = "database.generate"
    DATABASE_EDIT = "database.edit"
    
    API_VIEW = "api.view"
    API_GENERATE = "api.generate"
    API_EDIT = "api.edit"
    
    UX_VIEW = "ux.view"
    UX_GENERATE = "ux.generate"
    UX_EDIT = "ux.edit"
    
    # Planning & Scoring
    PLANNING_VIEW = "planning.view"
    PLANNING_GENERATE = "planning.generate"
    PLANNING_EDIT = "planning.edit"
    
    RISK_VIEW = "risk.view"
    RISK_EDIT = "risk.edit"
    
    SCORE_VIEW = "score.view"
    SCORE_CALCULATE = "score.calculate"
    SIMULATION_RUN = "simulation.run"
    
    # Blueprint & Governance
    BLUEPRINT_VIEW = "blueprint.view"
    BLUEPRINT_GENERATE = "blueprint.generate"
    BLUEPRINT_EDIT = "blueprint.edit"
    BLUEPRINT_APPROVE = "blueprint.approve"
    EXPORT_CREATE = "export.create"
    
    # Collaboration
    COMMENT_CREATE = "comment.create"
    VERSION_VIEW = "version.view"
    VERSION_CREATE = "version.create"

# Strict Page/Module Access Matrix as defined in Section 10 of Hackathon Specification
ROLE_PERMISSIONS: Dict[str, Set[str]] = {
    # 1. ADMIN (Platform Superuser with full system & project access)
    "ADMIN": {p.value for p in Permission},
    
    # 2. PROJECT_OWNER
    "PROJECT_OWNER": {
        Permission.WORKSPACE_MANAGE.value,
        Permission.PROJECT_VIEW.value,
        Permission.PROJECT_CREATE.value,
        Permission.PROJECT_EDIT.value,
        Permission.PROJECT_DELETE.value,
        Permission.PROJECT_MANAGE.value,
        Permission.TEAM_MANAGE.value,
        Permission.DOCUMENT_VIEW.value,
        Permission.DOCUMENT_UPLOAD.value,
        Permission.DOCUMENT_DELETE.value,
        Permission.DISCOVERY_CHAT.value,
        Permission.REQUIREMENTS_VIEW.value,
        Permission.REQUIREMENTS_EDIT.value,
        Permission.STAKEHOLDERS_VIEW.value,
        Permission.STAKEHOLDERS_EDIT.value,
        Permission.ANALYSIS_VIEW.value,
        Permission.ANALYSIS_RUN.value,
        Permission.ANALYSIS_EDIT.value,
        Permission.GAP_ANALYSIS_VIEW.value,
        Permission.GAP_ANALYSIS_RUN.value,
        Permission.GAP_ANALYSIS_EDIT.value,
        Permission.RECOMMENDATION_VIEW.value,
        Permission.RECOMMENDATION_GENERATE.value,
        Permission.RECOMMENDATION_EDIT.value,
        Permission.RECOMMENDATION_APPROVE.value,
        Permission.PROCESS_VIEW.value,
        Permission.PROCESS_GENERATE.value,
        Permission.PROCESS_EDIT.value,
        Permission.ARCHITECTURE_VIEW.value,
        Permission.ARCHITECTURE_GENERATE.value,
        Permission.ARCHITECTURE_EDIT.value,
        Permission.DATABASE_VIEW.value,
        Permission.DATABASE_GENERATE.value,
        Permission.DATABASE_EDIT.value,
        Permission.API_VIEW.value,
        Permission.API_GENERATE.value,
        Permission.API_EDIT.value,
        Permission.UX_VIEW.value,
        Permission.UX_GENERATE.value,
        Permission.UX_EDIT.value,
        Permission.PLANNING_VIEW.value,
        Permission.PLANNING_GENERATE.value,
        Permission.PLANNING_EDIT.value,
        Permission.RISK_VIEW.value,
        Permission.RISK_EDIT.value,
        Permission.SCORE_VIEW.value,
        Permission.SCORE_CALCULATE.value,
        Permission.SIMULATION_RUN.value,
        Permission.BLUEPRINT_VIEW.value,
        Permission.BLUEPRINT_GENERATE.value,
        Permission.BLUEPRINT_EDIT.value,
        Permission.BLUEPRINT_APPROVE.value,
        Permission.EXPORT_CREATE.value,
        Permission.COMMENT_CREATE.value,
        Permission.VERSION_VIEW.value,
        Permission.VERSION_CREATE.value,
        Permission.AUDIT_VIEW.value,
    },
    
    # 3. BUSINESS_ANALYST (BA)
    "BUSINESS_ANALYST": {
        Permission.PROJECT_VIEW.value,
        Permission.DOCUMENT_VIEW.value,
        Permission.DOCUMENT_UPLOAD.value,
        Permission.DISCOVERY_CHAT.value,
        Permission.REQUIREMENTS_VIEW.value,
        Permission.REQUIREMENTS_EDIT.value,
        Permission.STAKEHOLDERS_VIEW.value,
        Permission.STAKEHOLDERS_EDIT.value,
        Permission.ANALYSIS_VIEW.value,
        Permission.ANALYSIS_RUN.value,
        Permission.ANALYSIS_EDIT.value,
        Permission.GAP_ANALYSIS_VIEW.value,
        Permission.GAP_ANALYSIS_RUN.value,
        Permission.GAP_ANALYSIS_EDIT.value,
        Permission.RECOMMENDATION_VIEW.value,
        Permission.RECOMMENDATION_GENERATE.value,
        Permission.RECOMMENDATION_REVIEW_BA.value,
        Permission.PROCESS_VIEW.value,
        Permission.PROCESS_GENERATE.value,
        Permission.PROCESS_EDIT.value,
        Permission.ARCHITECTURE_VIEW.value, # Read-only
        Permission.DATABASE_VIEW.value,     # Read-only
        Permission.API_VIEW.value,          # Read-only
        Permission.UX_VIEW.value,
        Permission.UX_GENERATE.value,
        Permission.UX_EDIT.value,
        Permission.PLANNING_VIEW.value,
        Permission.PLANNING_GENERATE.value,
        Permission.RISK_VIEW.value,
        Permission.RISK_EDIT.value,
        Permission.SCORE_VIEW.value,
        Permission.SCORE_CALCULATE.value,
        Permission.SIMULATION_RUN.value,
        Permission.BLUEPRINT_VIEW.value,    # Read-only
        Permission.EXPORT_CREATE.value,
        Permission.COMMENT_CREATE.value,
        Permission.VERSION_VIEW.value,
    },
    
    # 4. SOLUTION_ARCHITECT (ARCH)
    "SOLUTION_ARCHITECT": {
        Permission.PROJECT_VIEW.value,
        Permission.DOCUMENT_VIEW.value,
        Permission.DOCUMENT_UPLOAD.value,
        Permission.DISCOVERY_CHAT.value,
        Permission.REQUIREMENTS_VIEW.value,
        Permission.STAKEHOLDERS_VIEW.value,
        Permission.ANALYSIS_VIEW.value,
        Permission.GAP_ANALYSIS_VIEW.value,
        Permission.RECOMMENDATION_VIEW.value,
        Permission.RECOMMENDATION_GENERATE.value,
        Permission.RECOMMENDATION_REVIEW_ARCH.value,
        Permission.PROCESS_VIEW.value,
        Permission.PROCESS_GENERATE.value,
        Permission.PROCESS_EDIT.value,
        Permission.ARCHITECTURE_VIEW.value,
        Permission.ARCHITECTURE_GENERATE.value,
        Permission.ARCHITECTURE_EDIT.value,
        Permission.ARCHITECTURE_SUBMIT.value,
        Permission.DATABASE_VIEW.value,
        Permission.DATABASE_GENERATE.value,
        Permission.DATABASE_EDIT.value,
        Permission.API_VIEW.value,
        Permission.API_GENERATE.value,
        Permission.API_EDIT.value,
        Permission.UX_VIEW.value,
        Permission.UX_GENERATE.value,
        Permission.PLANNING_VIEW.value,
        Permission.PLANNING_GENERATE.value,
        Permission.RISK_VIEW.value,
        Permission.RISK_EDIT.value,
        Permission.SCORE_VIEW.value,
        Permission.SCORE_CALCULATE.value,
        Permission.SIMULATION_RUN.value,
        Permission.BLUEPRINT_VIEW.value,    # Read-only
        Permission.BLUEPRINT_APPROVE.value,
        Permission.EXPORT_CREATE.value,
        Permission.COMMENT_CREATE.value,
        Permission.VERSION_VIEW.value,
        Permission.VERSION_CREATE.value,
    },
    
    # 5. MANAGER
    "MANAGER": {
        Permission.PROJECT_VIEW.value,
        Permission.DOCUMENT_VIEW.value,
        Permission.DOCUMENT_UPLOAD.value,
        Permission.DISCOVERY_CHAT.value,
        Permission.REQUIREMENTS_VIEW.value,
        Permission.STAKEHOLDERS_VIEW.value,
        Permission.ANALYSIS_VIEW.value,
        Permission.GAP_ANALYSIS_VIEW.value,
        Permission.RECOMMENDATION_VIEW.value,
        Permission.RECOMMENDATION_APPROVE.value,
        Permission.PROCESS_VIEW.value,
        Permission.ARCHITECTURE_VIEW.value,
        Permission.DATABASE_VIEW.value,
        Permission.API_VIEW.value,
        Permission.UX_VIEW.value,
        Permission.PLANNING_VIEW.value,
        Permission.RISK_VIEW.value,
        Permission.SCORE_VIEW.value,
        Permission.SIMULATION_RUN.value,
        Permission.BLUEPRINT_VIEW.value,
        Permission.BLUEPRINT_APPROVE.value,
        Permission.EXPORT_CREATE.value,
        Permission.COMMENT_CREATE.value,
        Permission.VERSION_VIEW.value,
        Permission.AUDIT_VIEW.value,
    },
    
    # 6. MEMBER
    "MEMBER": {
        Permission.PROJECT_VIEW.value,
        Permission.DOCUMENT_VIEW.value,
        Permission.DOCUMENT_UPLOAD.value,
        Permission.DISCOVERY_CHAT.value,
        Permission.REQUIREMENTS_VIEW.value,
        Permission.STAKEHOLDERS_VIEW.value,
        Permission.ANALYSIS_VIEW.value,
        Permission.GAP_ANALYSIS_VIEW.value,
        Permission.RECOMMENDATION_VIEW.value,
        Permission.PROCESS_VIEW.value,
        Permission.ARCHITECTURE_VIEW.value,
        Permission.DATABASE_VIEW.value,
        Permission.API_VIEW.value,
        Permission.UX_VIEW.value,
        Permission.PLANNING_VIEW.value,
        Permission.RISK_VIEW.value,
        Permission.SCORE_VIEW.value,
        Permission.SIMULATION_RUN.value,
        Permission.BLUEPRINT_VIEW.value,
        Permission.EXPORT_CREATE.value,
        Permission.COMMENT_CREATE.value,
        Permission.VERSION_VIEW.value,
    },
    
    # 7. VIEWER (Read-Only)
    "VIEWER": {
        Permission.PROJECT_VIEW.value,
        Permission.DOCUMENT_VIEW.value,
        Permission.DISCOVERY_CHAT.value,
        Permission.REQUIREMENTS_VIEW.value,
        Permission.STAKEHOLDERS_VIEW.value,
        Permission.ANALYSIS_VIEW.value,
        Permission.GAP_ANALYSIS_VIEW.value,
        Permission.RECOMMENDATION_VIEW.value,
        Permission.PROCESS_VIEW.value,
        Permission.ARCHITECTURE_VIEW.value,
        Permission.DATABASE_VIEW.value,
        Permission.API_VIEW.value,
        Permission.UX_VIEW.value,
        Permission.PLANNING_VIEW.value,
        Permission.RISK_VIEW.value,
        Permission.SCORE_VIEW.value,
        Permission.BLUEPRINT_VIEW.value,
        Permission.EXPORT_CREATE.value,
        Permission.VERSION_VIEW.value,
    }
}

# Add Aliases
ROLE_PERMISSIONS["OWNER"] = ROLE_PERMISSIONS["PROJECT_OWNER"]
ROLE_PERMISSIONS["ANALYST"] = ROLE_PERMISSIONS["BUSINESS_ANALYST"]
ROLE_PERMISSIONS["ARCHITECT"] = ROLE_PERMISSIONS["SOLUTION_ARCHITECT"]

def has_permission(role: str, permission: Union[Permission, str]) -> bool:
    """Checks if the given role has the requested permission."""
    role_key = role.upper() if role else "VIEWER"
    permissions = ROLE_PERMISSIONS.get(role_key, set())
    perm_val = permission.value if isinstance(permission, Permission) else str(permission)
    return perm_val in permissions
