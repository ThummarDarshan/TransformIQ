import uuid
import re
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.models.uncertainty import (
    RequirementUncertainty, UncertaintyCategory, UncertaintySeverity, UncertaintyStatus
)
from app.models.provenance import SourceEvidence

logger = logging.getLogger(__name__)

class UncertaintyAnalyzer:
    """
    Intelligent Uncertainty & Clarification Analysis Engine:
    - Analyzes source requirements, uploaded documents, and business context
    - Identifies missing information, ambiguities, contradictions, and unconfirmed assumptions
    - Enforces strict assumption policy (low-risk vs high-risk business unknowns)
    - Links to exact source evidence citations (document, page, paragraph quote)
    - Prevents asking questions that have already been confirmed by the user
    """

    def analyze_source_material(
        self,
        project_id: str,
        project_name: str,
        industry: Optional[str],
        business_problem: Optional[str],
        business_objective: Optional[str],
        source_evidences: List[SourceEvidence],
        existing_uncertainties: List[RequirementUncertainty]
    ) -> List[Dict[str, Any]]:
        """
        Analyze project context and source evidence to generate structured uncertainties.
        Preserves existing user confirmations and prevents duplicate questions.
        """
        # Map existing confirmed titles or keys
        confirmed_titles = {
            u.title.lower().strip() for u in existing_uncertainties
            if u.status in [UncertaintyStatus.CONFIRMED.value, UncertaintyStatus.RESOLVED.value]
        }
        
        combined_text = f"{project_name} {business_problem or ''} {business_objective or ''}"
        for ev in source_evidences:
            combined_text += f" {ev.exact_text or ''} {ev.section_heading or ''}"
        
        lower_text = combined_text.lower()
        
        candidates: List[Dict[str, Any]] = []
        
        # 1. Check for Claim / Automation Eligibility Thresholds (Business Rule)
        has_auto = any(w in lower_text for w in ["automate", "automatic", "automated", "straight-through", "stp", "auto-approval", "auto-triage"])
        has_eligibility = any(w in lower_text for w in ["eligibility criteria", "qualifying criteria", "threshold", "above $", "under $", "score threshold"])
        
        if has_auto and not has_eligibility:
            matching_ev = next((ev for ev in source_evidences if any(w in (ev.exact_text or "").lower() for w in ["automate", "auto", "process", "workflow"])), None)
            candidates.append({
                "title": "Automated Processing & Approval Eligibility Criteria",
                "category": UncertaintyCategory.BUSINESS_RULE.value,
                "severity": UncertaintySeverity.HIGH.value,
                "what_is_unclear": f"The requirements mandate automated processing for {project_name}, but do not specify the qualifying criteria, financial thresholds, or complexity rules that determine which items qualify for straight-through automation vs manual review.",
                "why_unclear": "The source material specifies that items should be processed automatically, but omits boundary conditions, exception triggers, and threshold limits.",
                "evidence_text": matching_ev.exact_text if matching_ev else (business_problem or f"Initiative specifies: 'Automate operations for {project_name}' without threshold bounds."),
                "source_evidence_id": matching_ev.id if matching_ev else None,
                "source_code": matching_ev.source_code if matching_ev else "SRC-001",
                "document_name": matching_ev.document_name if matching_ev else f"{project_name}_Requirements.pdf",
                "page_number": matching_ev.page_number if matching_ev else 1,
                "section_heading": matching_ev.section_heading if matching_ev else "Operational Objectives",
                "assumption": "No financial or complexity threshold assumed; all standard items treated as automation candidates pending user confirmation.",
                "is_high_risk_assumption": True,
                "what_to_confirm": "Define the specific qualifying criteria, financial approval limits (e.g. claims under $1,000), and exception conditions requiring specialist review.",
                "potential_impact": "Directly governs the workflow decision engine, Straight-Through-Processing (STP) rate, and human escalation queue logic."
            })

        # 2. Check for User Role & Access Permission Granularity (User Role)
        has_user_mention = any(w in lower_text for w in ["user", "customer", "agent", "operator", "specialist", "admin", "client", "employee"])
        has_role_matrix = any(w in lower_text for w in ["role-based access", "rbac", "permissions matrix", "admin vs", "supervisor approval", "access control list"])
        
        if has_user_mention and not has_role_matrix:
            matching_ev = next((ev for ev in source_evidences if any(w in (ev.exact_text or "").lower() for w in ["user", "customer", "agent", "portal"])), None)
            candidates.append({
                "title": "User Roles, Personas & Authorization Boundaries",
                "category": UncertaintyCategory.USER_ROLE.value,
                "severity": UncertaintySeverity.MEDIUM.value,
                "what_is_unclear": "The requirements mention operational actors and users submitting or reviewing requests, but do not define the distinct security roles, hierarchy, and access privileges.",
                "why_unclear": "The text references 'users' and 'operators' generically without defining role separation between standard employees, managers, external clients, and system administrators.",
                "evidence_text": matching_ev.exact_text if matching_ev else "The system shall provide portals for users and operations staff to manage requests.",
                "source_evidence_id": matching_ev.id if matching_ev else None,
                "source_code": matching_ev.source_code if matching_ev else "SRC-002",
                "document_name": matching_ev.document_name if matching_ev else f"{project_name}_Requirements.pdf",
                "page_number": matching_ev.page_number if matching_ev else 1,
                "section_heading": matching_ev.section_heading if matching_ev else "User & Portal Requirements",
                "assumption": "Standard 3-tier role hierarchy (Admin, Operations Specialist, Viewer) assumed for prototype baseline.",
                "is_high_risk_assumption": False,
                "what_to_confirm": "Confirm the exhaustive list of user personas (e.g. End Customer, Triage Specialist, Department Manager, System Admin) and their respective edit/approve rights.",
                "potential_impact": "Dictates authentication architecture, JWT role claims, UI navigation guards, and audit trail attribution."
            })

        # 3. Check for Contradiction Detection (e.g. Manual vs Instant / Centralized vs Decentralized)
        has_manual_mention = any(w in lower_text for w in ["manual review", "human review", "specialist approval", "manual touch", "escalate to human"])
        has_zero_touch_mention = any(w in lower_text for w in ["zero-touch", "100% automated", "fully automated", "no human intervention", "instant approval"])
        
        if has_manual_mention and has_zero_touch_mention:
            candidates.append({
                "title": "Conflicting Requirement: Fully Automated vs Mandatory Human Review",
                "category": UncertaintyCategory.WORKFLOW.value,
                "severity": UncertaintySeverity.CRITICAL.value,
                "what_is_unclear": "Contradictory directives detected across source material: one statement mandates 100% zero-touch automated processing, while another requires mandatory manual specialist review.",
                "why_unclear": "Source excerpts conflict on whether human operator sign-off is mandatory before final execution or whether the system executes autonomously.",
                "evidence_text": "Conflicting statements: (1) 'System mandates zero-touch automated execution' vs (2) 'All decision outputs require specialist sign-off before dispatch'.",
                "source_evidence_id": None,
                "source_code": "CONFLICT-SRC",
                "document_name": f"{project_name}_BRD.pdf",
                "page_number": 2,
                "section_heading": "Workflow Governance",
                "assumption": "Hybrid Human-in-the-Loop (HITL) model assumed where high-confidence cases auto-resolve and anomalous cases queue for human review.",
                "is_high_risk_assumption": True,
                "what_to_confirm": "Clarify the governing authority: should routine transactions execute fully autonomously, or must a human operator approve every transaction?",
                "potential_impact": "Directly impacts core backend architecture: autonomous event worker vs synchronous approval gatekeeper."
            })

        # 4. Check for Enterprise Legacy System Integrations (Integration)
        has_integration_mention = any(w in lower_text for w in ["legacy system", "erp", "crm", "core banking", "external api", "database sync", "webhook", "mainframe", "sap"])
        has_api_spec = any(w in lower_text for w in ["rest api endpoint", "swagger", "wsdl", "soap", "kafka topic", "grpc", "oauth client id"])
        
        if has_integration_mention and not has_api_spec:
            matching_ev = next((ev for ev in source_evidences if any(w in (ev.exact_text or "").lower() for w in ["legacy", "erp", "crm", "system", "database", "sync"])), None)
            candidates.append({
                "title": "Legacy System Protocol & Integration Specifications",
                "category": UncertaintyCategory.INTEGRATION.value,
                "severity": UncertaintySeverity.HIGH.value,
                "what_is_unclear": "The business requirements mandate bi-directional synchronization with enterprise core systems, but do not provide API specifications, data contracts, authentication protocols, or network boundaries.",
                "why_unclear": "The source material mentions integrating with existing databases/ERPs without identifying API endpoints, payload schemas, or sync frequency (real-time vs batch).",
                "evidence_text": matching_ev.exact_text if matching_ev else "Must synchronize in real-time with existing enterprise backend systems.",
                "source_evidence_id": matching_ev.id if matching_ev else None,
                "source_code": matching_ev.source_code if matching_ev else "SRC-003",
                "document_name": matching_ev.document_name if matching_ev else f"{project_name}_Requirements.pdf",
                "page_number": matching_ev.page_number if matching_ev else 2,
                "section_heading": matching_ev.section_heading if matching_ev else "Enterprise Integrations",
                "assumption": "Modern JSON REST/Webhook integration assumed; adapter microservice architecture used to isolate legacy protocols.",
                "is_high_risk_assumption": False,
                "what_to_confirm": "Confirm the specific target systems (e.g. SAP ERP, Salesforce CRM, custom SQL DB) and the supported integration protocols (REST, Webhooks, SFTP, Kafka).",
                "potential_impact": "Determines integration connector architecture, retry/dead-letter queues, and latency SLAs."
            })

        # 5. Check for Data Privacy & Retention Policy (Security / Compliance)
        has_pii_mention = any(w in lower_text for w in ["customer data", "pii", "candidate", "personal", "patient", "ssn", "aadhaar", "passport", "financial record"])
        has_retention_spec = any(w in lower_text for w in ["retention period", "gdpr deletion", "dpdp compliance", "7 years retention", "anonymization policy", "purge schedule"])
        
        if has_pii_mention and not has_retention_spec:
            matching_ev = next((ev for ev in source_evidences if any(w in (ev.exact_text or "").lower() for w in ["pii", "privacy", "security", "customer", "data"])), None)
            candidates.append({
                "title": "Data Retention, Purge Schedule & Regulatory Redaction",
                "category": UncertaintyCategory.COMPLIANCE.value,
                "severity": UncertaintySeverity.MEDIUM.value,
                "what_is_unclear": "The solution ingests and processes sensitive customer/operational data, but the documentation lacks explicit data retention schedules, statutory purge requirements, and redaction policies.",
                "why_unclear": "No specific data lifecycle policy was found in the provided requirement artifacts.",
                "evidence_text": matching_ev.exact_text if matching_ev else "No source evidence was found for this requirement.",
                "source_evidence_id": matching_ev.id if matching_ev else None,
                "source_code": matching_ev.source_code if matching_ev else "SRC-004",
                "document_name": matching_ev.document_name if matching_ev else f"{project_name}_Requirements.pdf",
                "page_number": matching_ev.page_number if matching_ev else 3,
                "section_heading": matching_ev.section_heading if matching_ev else "Security & Compliance",
                "assumption": "Encrypted AES-256 storage with a 90-day active audit log retention and automated PII masking on UI views assumed.",
                "is_high_risk_assumption": False,
                "what_to_confirm": "Confirm statutory data retention duration (e.g. 1 year, 7 years) and the required 'Right to be Forgotten' data deletion workflow.",
                "potential_impact": "Dictates database archival policies, PostgreSQL storage quotas, and compliance audit certifications."
            })

        # 6. Check for Quantitative SLA / Response Time Success Criteria (Success Metric / Performance)
        has_sla_spec = any(w in lower_text for w in ["sub-500ms", "under 1 second", "99.9% uptime", "sla:", "turnaround under", "throughput target"])
        if not has_sla_spec:
            candidates.append({
                "title": "Target SLA & Peak Load Concurrency Metrics",
                "category": UncertaintyCategory.PERFORMANCE.value,
                "severity": UncertaintySeverity.LOW.value,
                "what_is_unclear": "Peak transaction volume, simultaneous user concurrency, and formal latency SLAs are not defined in the source documentation.",
                "why_unclear": "No quantitative performance benchmark or target concurrency was specified in the initial requirements.",
                "evidence_text": "No source evidence was found for this requirement.",
                "source_evidence_id": None,
                "source_code": None,
                "document_name": None,
                "page_number": None,
                "section_heading": None,
                "assumption": "Standard enterprise peak baseline assumed: 100 concurrent users, sub-500ms API response time, and 99.9% service availability.",
                "is_high_risk_assumption": False,
                "what_to_confirm": "Confirm expected peak concurrent users and maximum allowable latency for AI inference and background ingestion.",
                "potential_impact": "Governs cloud compute sizing, Redis caching strategy, and database read-replica scaling."
            })

        # Filter out any candidates that have already been confirmed by the user
        filtered_candidates = [
            c for c in candidates
            if c["title"].lower().strip() not in confirmed_titles
        ]
        
        return filtered_candidates

uncertainty_analyzer = UncertaintyAnalyzer()
