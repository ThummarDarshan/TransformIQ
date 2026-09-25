import asyncio
import os
import sys
import uuid
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from app.config.database import AsyncSessionLocal
from app.models.user import User, Organization, Workspace, ProjectMember, UserRole
from app.models.project import Project, ProjectStatus, BusinessContext, Document, DocumentChunk
from app.models.transformation import Requirement, Stakeholder, BusinessProcess, Gap, Recommendation, Solution, RequirementType
from app.models.architecture import ArchitectureComponent, ArchitectureConnection, WorkflowNode, WorkflowEdge
from app.models.design import DatabaseEntity, ApiEndpoint, Wireframe
from app.models.planning import Roadmap, Estimate, Risk, TransformationScore
from app.models.collaboration import Approval, AuditLog, Version
from app.models.provenance import SourceEvidence, ArtifactProvenance, ProvenanceType, SourceType
from app.models.uncertainty import RequirementUncertainty, UncertaintyCategory, UncertaintySeverity, UncertaintyStatus
from app.auth.security import get_password_hash
from sqlalchemy.future import select

async def seed_rbac():
    print("Seeding TransformIQ RBAC demo environment & 'Customer Complaint Transformation' project...")
    async with AsyncSessionLocal() as session:
        # 1. Create Users
        users_def = [
            {"email": "admin@transformiq.local", "name": "Sarah Connor", "role": UserRole.ADMIN.value},
            {"email": "owner@transformiq.local", "name": "Elena Rostova", "role": UserRole.PROJECT_OWNER.value},
            {"email": "analyst@transformiq.local", "name": "Priya Sharma", "role": UserRole.BUSINESS_ANALYST.value},
            {"email": "architect@transformiq.local", "name": "David Chen", "role": UserRole.SOLUTION_ARCHITECT.value},
            {"email": "manager@transformiq.local", "name": "Marcus Vance", "role": UserRole.MANAGER.value},
            {"email": "member@transformiq.local", "name": "Liam Murphy", "role": UserRole.MEMBER.value},
            {"email": "viewer@transformiq.local", "name": "Victoria Stone", "role": UserRole.VIEWER.value},
        ]
        
        user_map = {}
        for u_data in users_def:
            res_u = await session.execute(select(User).filter(User.email == u_data["email"]))
            user = res_u.scalars().first()
            if not user:
                user = User(
                    id=str(uuid.uuid4()),
                    email=u_data["email"],
                    hashed_password=get_password_hash("TransformIQ@2026"),
                    full_name=u_data["name"],
                    role=u_data["role"],
                    is_active=True
                )
                session.add(user)
                await session.flush()
            else:
                user.full_name = u_data["name"]
                user.role = u_data["role"]
                user.hashed_password = get_password_hash("TransformIQ@2026")
            user_map[u_data["role"]] = user
            print(f"[USER] {u_data['name']} <{u_data['email']}> | Role: {u_data['role']}")
            
        owner_user = user_map[UserRole.PROJECT_OWNER.value]
        
        # 2. Organization
        res_org = await session.execute(select(Organization).filter(Organization.slug == "acme-retail-enterprise"))
        org = res_org.scalars().first()
        if not org:
            org = Organization(
                id=str(uuid.uuid4()),
                name="Acme Global Retail & Logistics",
                slug="acme-retail-enterprise",
                industry="E-Commerce & Omnichannel Retail",
                size="Enterprise (10000+)",
                owner_id=owner_user.id
            )
            session.add(org)
            await session.flush()
            
        # 3. Workspace
        res_ws = await session.execute(select(Workspace).filter(Workspace.organization_id == org.id))
        ws = res_ws.scalars().first()
        if not ws:
            ws = Workspace(
                id=str(uuid.uuid4()),
                name="Customer Experience Transformation",
                description="AI-driven customer operations, complaints resolution, and intelligent triage.",
                organization_id=org.id
            )
            session.add(ws)
            await session.flush()
            
        # 4. Project: "Customer Complaint Transformation"
        proj_slug = "customer-complaint-transformation"
        res_proj = await session.execute(select(Project).filter(Project.slug == proj_slug))
        project = res_proj.scalars().first()
        
        if not project:
            proj_id = str(uuid.uuid4())
            project = Project(
                id=proj_id,
                name="Customer Complaint Transformation",
                slug=proj_slug,
                description="Intelligent AI-driven triage, classification, sentiment analysis, and routing for 50,000+ monthly customer complaints.",
                workspace_id=ws.id,
                status=ProjectStatus.APPROVED.value,
                industry="E-Commerce & Retail",
                organization_size="Enterprise (10000+)",
                business_objective="Automate 85% of customer complaint classification, reduce resolution latency from 48h to 12m, and ensure 99.9% SLA compliance.",
                business_problem="Company receives thousands of customer complaints via email. Current manual process involves employees reading complaints, manually selecting categories, assigning priorities, and routing to departments. This causes slow resolution (48h), high employee fatigue, and lack of real-time analytics.",
                current_systems="Zendesk Support, Shared Outlook Mailboxes, Legacy Oracle CRM, Manual Excel spreadsheets",
                expected_outcome="85% automated straight-through classification and routing, instant sentiment priority alerts, 48h -> 12m turnaround time, $1.4M annual operational cost reduction.",
                constraints="SOC-2 and GDPR compliance for customer PII, zero-downtime integration with Zendesk APIs, sub-500ms AI inference latency.",
                budget=240000,
                timeline_months=4
            )
            session.add(project)
            await session.flush()
            print(f"[PROJECT] Created '{project.name}' (ID: {project.id})")
        else:
            proj_id = project.id
            print(f"[PROJECT] Found existing '{project.name}' (ID: {project.id})")
            
        # 5. Project Memberships
        for role_key, user_obj in user_map.items():
            res_mem = await session.execute(
                select(ProjectMember).filter(
                    ProjectMember.project_id == proj_id,
                    ProjectMember.user_id == user_obj.id
                )
            )
            if not res_mem.scalars().first():
                session.add(ProjectMember(
                    id=str(uuid.uuid4()),
                    project_id=proj_id,
                    user_id=user_obj.id,
                    role=role_key
                ))
                
        # 6. Transformation Score
        res_sc = await session.execute(select(TransformationScore).filter(TransformationScore.project_id == proj_id))
        if not res_sc.scalars().first():
            session.add(TransformationScore(
                id=str(uuid.uuid4()),
                project_id=proj_id,
                overall_score=92,
                ai_readiness=95,
                automation_potential=91,
                data_readiness=84,
                business_impact=96,
                technical_feasibility=92,
                implementation_readiness=88
            ))
            
        # 6.5. Source Documents & Traceable Evidence
        doc_filename = "Acme_Customer_Complaint_Transformation_BRD.pdf"
        res_doc = await session.execute(select(Document).filter(Document.project_id == proj_id, Document.filename == doc_filename))
        doc = res_doc.scalars().first()
        if not doc:
            doc_id = str(uuid.uuid4())
            doc = Document(
                id=doc_id,
                project_id=proj_id,
                filename=doc_filename,
                file_type="pdf",
                file_size=184320,
                storage_path=f"uploads/{doc_filename}",
                extracted_text="Executive Business Requirements Document for Automated Customer Complaints Transformation.",
                summary="Business Requirements Document specifying 48h resolution bottlenecks, manual reading friction, Zendesk & Oracle CRM sync requirements, and GDPR PII masking mandates.",
                status="PROCESSED"
            )
            session.add(doc)
            await session.flush()

        # Seed Chunks & Canonical Source Evidence if not present
        res_ev_check = await session.execute(select(SourceEvidence).filter(SourceEvidence.project_id == proj_id))
        if not res_ev_check.scalars().all():
            evidence_data = [
                {
                    "code": "SRC-001",
                    "page": 2,
                    "section": "2.1 Problem Statement & Turnaround Latency",
                    "text": "Company receives thousands of customer complaints via email daily. Current manual process involves employees reading complaints, manually selecting categories, and routing to departments, causing up to 48-hour resolution latency.",
                },
                {
                    "code": "SRC-002",
                    "page": 2,
                    "section": "2.3 Customer Sentiment & VIP Churn Risks",
                    "text": "Urgent complaints from VIP enterprise accounts and high churn-risk consumers are frequently buried in shared inboxes, causing high-profile contract cancellations.",
                },
                {
                    "code": "SRC-003",
                    "page": 3,
                    "section": "3.2 System Integrations & Workflows",
                    "text": "The intelligent classification solution must integrate bi-directionally with Zendesk Support APIs and Oracle CRM to synchronize ticket status, category tags, and priority queues in real-time.",
                },
                {
                    "code": "SRC-004",
                    "page": 4,
                    "section": "4.1 Data Privacy & Security Mandates",
                    "text": "All customer emails contain sensitive PII including payment details, national IDs, and contact info which must be redacted before sending to external AI models.",
                }
            ]

            ev_map = {}
            for idx, ed in enumerate(evidence_data):
                chunk_id = str(uuid.uuid4())
                chunk = DocumentChunk(
                    id=chunk_id,
                    document_id=doc.id,
                    chunk_index=idx,
                    content=ed["text"],
                    page_number=ed["page"],
                    metadata_json={"source": doc_filename, "source_code": ed["code"], "section_heading": ed["section"]}
                )
                session.add(chunk)
                await session.flush()

                ev_id = str(uuid.uuid4())
                evidence = SourceEvidence(
                    id=ev_id,
                    source_code=ed["code"],
                    project_id=proj_id,
                    document_id=doc.id,
                    chunk_id=chunk_id,
                    document_name=doc_filename,
                    source_type=SourceType.DOCUMENT_PDF.value,
                    page_number=ed["page"],
                    section_heading=ed["section"],
                    paragraph_number=idx + 1,
                    start_offset=idx * 250,
                    end_offset=(idx * 250) + len(ed["text"]),
                    exact_text=ed["text"],
                    metadata_json={"source": doc_filename, "code": ed["code"]}
                )
                session.add(evidence)
                ev_map[ed["code"]] = ev_id
                await session.flush()

        # 7. Requirements with Traceability
        res_req = await session.execute(select(Requirement).filter(Requirement.project_id == proj_id))
        if not res_req.scalars().all():
            reqs = [
                ("REQ-F01", "Automated Multi-Class Complaint Triage", "AI engine must classify incoming emails into 14 distinct issue taxonomies with >92% accuracy.", "CRITICAL", RequirementType.FUNCTIONAL.value, "SRC-001", ProvenanceType.DIRECT.value, "Directly derived from Section 2.1 stating manual email reading and category assignment takes 48 hours."),
                ("REQ-F02", "Real-Time Sentiment & Urgency Scoring", "Extract customer emotional urgency score (0-100) to trigger immediate escalation for VIP or churn-risk customers.", "HIGH", RequirementType.FUNCTIONAL.value, "SRC-002", ProvenanceType.DIRECT.value, "Directly addresses Section 2.3 requirement to prioritize VIP complaints buried in inboxes."),
                ("REQ-F03", "Zendesk & CRM Bi-Directional Sync", "Automatically enrich ticket fields, assign departmental queues, and trigger resolution workflows.", "HIGH", RequirementType.FUNCTIONAL.value, "SRC-003", ProvenanceType.DIRECT.value, "Directly derived from Section 3.2 system integration mandate with Zendesk and Oracle CRM."),
                ("REQ-F04", "Human-in-the-Loop Override Console", "Specialist dashboard to review confidence scores <80% and validate AI decisions.", "MEDIUM", RequirementType.FUNCTIONAL.value, "SRC-001", ProvenanceType.DERIVED.value, "Derived as a human-in-the-loop safety net to achieve 100% accuracy on ambiguous complaints."),
                ("REQ-NF01", "Sub-500ms AI Processing Latency", "End-to-end classification and queue routing must complete in under 500 milliseconds.", "CRITICAL", RequirementType.NON_FUNCTIONAL.value, None, ProvenanceType.RECOMMENDED.value, "Architectural recommendation to ensure real-time stream processing throughput."),
                ("REQ-NF02", "PII Redaction & GDPR Compliance", "Automated masking of credit card numbers, social security numbers, and sensitive health data.", "CRITICAL", RequirementType.NON_FUNCTIONAL.value, "SRC-004", ProvenanceType.DIRECT.value, "Directly enforced by Section 4.1 requiring PII sanitization before AI processing."),
            ]
            for code, title, desc, prio, rtype, src_code, prov_type, rationale in reqs:
                req_id = str(uuid.uuid4())
                session.add(Requirement(
                    id=req_id,
                    project_id=proj_id,
                    code=code,
                    title=title,
                    description=desc,
                    priority=prio,
                    req_type=rtype,
                    source=f"{doc_filename} (Page {2 if '01' in (src_code or '') or '02' in (src_code or '') else 3})" if src_code else "AI Solution Architecture Standard"
                ))
                await session.flush()

        # Seed ArtifactProvenance links if missing
        res_prov_check = await session.execute(select(ArtifactProvenance).filter(ArtifactProvenance.project_id == proj_id))
        if not res_prov_check.scalars().all():
            provenance_mappings = [
                ("REQUIREMENT", "REQ-F01", "SRC-001", ProvenanceType.DIRECT.value, "Directly derived from Section 2.1 stating manual email reading and category assignment takes 48 hours."),
                ("REQUIREMENT", "REQ-F02", "SRC-002", ProvenanceType.DIRECT.value, "Directly addresses Section 2.3 requirement to prioritize VIP complaints buried in inboxes."),
                ("REQUIREMENT", "REQ-F03", "SRC-003", ProvenanceType.DIRECT.value, "Directly derived from Section 3.2 system integration mandate with Zendesk and Oracle CRM."),
                ("REQUIREMENT", "REQ-F04", "SRC-001", ProvenanceType.DERIVED.value, "Derived as a human-in-the-loop safety net to achieve 100% accuracy on ambiguous complaints."),
                ("REQUIREMENT", "REQ-NF01", None, ProvenanceType.RECOMMENDED.value, "Architectural best practice recommendation to ensure real-time stream processing throughput."),
                ("REQUIREMENT", "REQ-NF02", "SRC-004", ProvenanceType.DIRECT.value, "Directly enforced by Section 4.1 requiring PII sanitization before AI processing."),
            ]
            for art_type, art_id, src_code, prov_type, rationale in provenance_mappings:
                found_ev = None
                if src_code:
                    res_ev = await session.execute(select(SourceEvidence).filter(SourceEvidence.project_id == proj_id, SourceEvidence.source_code == src_code))
                    found_ev = res_ev.scalars().first()
                session.add(ArtifactProvenance(
                    id=str(uuid.uuid4()),
                    project_id=proj_id,
                    artifact_type=art_type,
                    artifact_id=art_id,
                    source_evidence_id=found_ev.id if found_ev else None,
                    provenance_type=prov_type,
                    rationale=rationale,
                    confidence_score=0.96 if prov_type == "DIRECT" else (0.88 if prov_type == "DERIVED" else 0.80)
                ))

        # 8. Gaps
        res_gaps = await session.execute(select(Gap).filter(Gap.project_id == proj_id))
        if not res_gaps.scalars().all():
            gaps = [
                ("Process", "Manual Email Classification Bottleneck", "Staff spend 4-6 minutes reading each email and manually assigning tags", "Zero-touch automated classification within 500ms", "CRITICAL", "High latency (48h) and high operational overhead"),
                ("Technology", "Siloed Legacy CRM Without Webhooks", "Legacy Oracle CRM lacks real-time streaming APIs for modern incident triage", "Event-driven REST/Webhook integration layer with async message broker", "HIGH", "Delays in cross-departmental escalations"),
                ("Data", "Unstructured Free-Text Ingestion", "No standard template or structured taxonomy for customer complaints", "NLP entity extraction and sentiment vector embeddings", "HIGH", "Inconsistent categorization and blind spots in analytics"),
                ("Governance", "Lack of SLA Tracking & Alerting", "No proactive notification when critical complaints sit unassigned", "Automated SLA monitors with Slack/PagerDuty alerts", "MEDIUM", "Risk of high-profile customer churn")
            ]
            for cat, title, curr, des, sev, imp in gaps:
                session.add(Gap(
                    id=str(uuid.uuid4()),
                    project_id=proj_id,
                    category=cat,
                    title=title,
                    current_state=curr,
                    desired_state=des,
                    severity=sev,
                    impact=imp,
                    root_cause="Absence of cognitive AI layer in existing customer service workflow",
                    recommended_action="Deploy TransformIQ Complaint AI microservice with FastAPI + Azure OpenAI"
                ))

        # 9. Solution & Recommendations
        res_sol = await session.execute(select(Solution).filter(Solution.project_id == proj_id))
        if not res_sol.scalars().first():
            session.add(Solution(
                id=str(uuid.uuid4()),
                project_id=proj_id,
                name="IntelliTriage — Enterprise Complaint Intelligence",
                tagline="Real-time cognitive classification, sentiment prioritization, and automated queue dispatch.",
                executive_summary="IntelliTriage transforms Acme's customer support operations from a 48-hour manual bottleneck into a 12-minute straight-through resolution engine. By combining Azure OpenAI LLMs, vector-based semantic retrieval, and event-driven microservices, IntelliTriage automatically classifies, prioritizes, and routes 85% of complaints with zero manual intervention.",
                expected_roi="380% ROI in Year 1 ($1.4M operational savings, 85% labor reduction)",
                key_capabilities=["Multi-Class NLP Classification", "Sentiment Urgency Engine", "Zendesk & CRM Event Gateway", "Human-in-the-Loop Specialist UI"],
                technology_stack={"Frontend": ["React 19", "TailwindCSS", "React Flow"], "Backend": ["FastAPI", "Python 3.10", "SQLAlchemy Async"], "AI": ["Azure OpenAI GPT-4o", "Sentence-Transformers"], "Database": ["PostgreSQL 16", "pgvector", "Redis"]}
            ))

        res_recs = await session.execute(select(Recommendation).filter(Recommendation.project_id == proj_id))
        if not res_recs.scalars().all():
            recs = [
                ("AI & Automation", "Deploy Fine-Tuned NLP Complaint Classifier", "Automatically categorize tickets into 14 distinct service buckets with >92% confidence.", "Directly removes 4-6 minutes of manual triage per ticket.", "HIGH", "HIGH", "HIGH", 0.94, "APPROVED"),
                ("AI & Automation", "Real-Time Sentiment & Churn-Risk Scoring", "Evaluate sentiment polarity and customer lifetime value to fast-track critical escalations.", "Prevents high-value customer churn through instant routing.", "HIGH", "HIGH", "HIGH", 0.91, "APPROVED"),
                ("Process Optimization", "Automated Queue Dispatch via Webhooks", "Stream tickets directly to the right engineering or finance team without dispatcher delays.", "Eliminates departmental handoff lag.", "HIGH", "MEDIUM", "LOW", 0.88, "APPROVED"),
                ("Governance & Quality", "Human-in-the-Loop Escalation Console", "Flag tickets with confidence <80% or sensitive keywords for human specialist review.", "Guarantees 100% safety and regulatory adherence.", "CRITICAL", "MEDIUM", "LOW", 0.96, "APPROVED"),
            ]
            for cat, title, desc, reason, imp, feas, prio, conf, stat in recs:
                session.add(Recommendation(
                    id=str(uuid.uuid4()),
                    project_id=proj_id,
                    category=cat,
                    title=title,
                    description=desc,
                    reason=reason,
                    expected_impact=imp,
                    feasibility=feas,
                    priority=prio,
                    confidence_score=conf,
                    status=stat
                ))

        # 10. Architecture Components & Connections
        res_comps = await session.execute(select(ArchitectureComponent).filter(ArchitectureComponent.project_id == proj_id))
        if not res_comps.scalars().all():
            c1_id = str(uuid.uuid4())
            c2_id = str(uuid.uuid4())
            c3_id = str(uuid.uuid4())
            c4_id = str(uuid.uuid4())
            c5_id = str(uuid.uuid4())
            
            comps = [
                (c1_id, "Ingress Gateway & WAF", "Ingress / Security", "Cloudflare + Envoy", "TLS termination, rate limiting, and webhook validation.", "Validates incoming Zendesk & email events.", 100.0, 150.0),
                (c2_id, "FastAPI Orchestrator", "Core Services", "Python FastAPI / Uvicorn", "Async orchestration, RBAC security, and event streaming.", "Executes multi-agent transformation pipeline.", 350.0, 150.0),
                (c3_id, "AI Classification Engine", "AI / ML Layer", "Azure OpenAI GPT-4o + Embeddings", "Zero-shot categorization and sentiment analysis.", "Assigns intent taxonomy and confidence score.", 600.0, 100.0),
                (c4_id, "PostgreSQL & Vector Store", "Data Persistence", "PostgreSQL 16 + pgvector", "Relational metadata and document embeddings.", "Stores tickets, audit logs, and vector chunks.", 600.0, 250.0),
                (c5_id, "Human Review Console", "Frontend UI", "React 19 + TailwindCSS", "Specialist interface for exception handling.", "Displays low-confidence queue and analytics.", 850.0, 150.0)
            ]
            for cid, name, layer, tech, desc, resp, px, py in comps:
                session.add(ArchitectureComponent(
                    id=cid,
                    project_id=proj_id,
                    name=name,
                    layer=layer,
                    tech_stack=tech,
                    description=desc,
                    responsibilities=resp,
                    position_x=px,
                    position_y=py
                ))
                
            conns = [
                (c1_id, c2_id, "HTTPS / Webhook", "Raw Inbound Complaint Event", False),
                (c2_id, c3_id, "gRPC / REST", "Sanitized Text & Context", True),
                (c2_id, c4_id, "asyncpg Pool", "Ticket Entity & Audit Record", False),
                (c3_id, c2_id, "JSON Payload", "Category, Urgency, Confidence", False),
                (c2_id, c5_id, "WebSocket / REST", "Exception Stream & Review Alerts", True),
            ]
            for src, tgt, proto, payload, is_async in conns:
                session.add(ArchitectureConnection(
                    id=str(uuid.uuid4()),
                    project_id=proj_id,
                    source_component_id=src,
                    target_component_id=tgt,
                    protocol=proto,
                    data_payload=payload,
                    is_async=is_async
                ))

        # 11. Approval Record
        res_app = await session.execute(select(Approval).filter(Approval.project_id == proj_id, Approval.artifact_type == "BLUEPRINT"))
        if not res_app.scalars().first():
            session.add(Approval(
                id=str(uuid.uuid4()),
                project_id=proj_id,
                artifact_type="BLUEPRINT",
                status="APPROVED",
                requested_by=owner_user.full_name,
                reviewed_by=user_map[UserRole.MANAGER.value].full_name,
                comments="Comprehensive solution blueprint approved for implementation kickoff.",
                decision_date=datetime.utcnow()
            ))

        # 12. Version Snapshot
        res_ver = await session.execute(select(Version).filter(Version.project_id == proj_id))
        if not res_ver.scalars().first():
            session.add(Version(
                id=str(uuid.uuid4()),
                project_id=proj_id,
                artifact_type="MASTER_BLUEPRINT",
                version_number=1,
                change_summary="Initial verified Master Blueprint snapshot with Manager approval.",
                author_name=user_map[UserRole.MANAGER.value].full_name,
                snapshot_json={"status": "APPROVED", "timestamp": datetime.utcnow().isoformat()}
            ))

        # 13. Audit Log
        session.add(AuditLog(
            id=str(uuid.uuid4()),
            project_id=proj_id,
            user_id=owner_user.id,
            user_name=owner_user.full_name,
            action="INITIALIZE_TRANSFORMATION_INITIATIVE",
            details="Customer Complaint Transformation initiative seeded with full 14-stage artifacts and 7 RBAC roles.",
            ip_address="127.0.0.1"
        ))

        # 14. Requirement Uncertainties & Governance ("WHAT I COULDN'T FIGURE OUT")
        res_unc = await session.execute(select(RequirementUncertainty).filter(RequirementUncertainty.project_id == proj_id))
        if not res_unc.scalars().first():
            ev_list_res = await session.execute(select(SourceEvidence).filter(SourceEvidence.project_id == proj_id))
            ev_map = {e.source_code: e for e in ev_list_res.scalars().all()}
            
            unc_defs = [
                (
                    "Automated Resolution Eligibility & Financial Threshold",
                    UncertaintyCategory.BUSINESS_RULE.value,
                    UncertaintySeverity.HIGH.value,
                    "The requirements mandate automated customer complaint resolution, but omit the maximum compensation refund threshold and eligibility conditions for instant straight-through processing.",
                    "The BRD states 'All routine complaints should be resolved automatically', but does not specify a dollar limit or dispute severity cap.",
                    "SRC-001",
                    "No financial threshold assumed; all tier-1 standard complaints eligible pending confirmation.",
                    True,
                    "Define maximum automated refund dollar threshold (e.g. $50 vs $250) and eligibility criteria.",
                    "Dictates the rules engine thresholds, ERP financial authorization limits, and human escalation queues."
                ),
                (
                    "Customer Service Specialist Roles & Approval Rights",
                    UncertaintyCategory.USER_ROLE.value,
                    UncertaintySeverity.MEDIUM.value,
                    "The documentation references 'customer support agents' and 'supervisors' but lacks a formal Role-Based Access Control (RBAC) permissions matrix.",
                    "General references to 'operations staff' without distinguishing tier-1 agents from tier-2 escalation specialists.",
                    "SRC-002",
                    "Standard 3-tier hierarchy (Support Agent, Escalation Manager, Admin) assumed for system design.",
                    False,
                    "Confirm the exact user personas and approval sign-off authorities.",
                    "Impacts JWT token permission claims, UI action guards, and audit trail compliance."
                ),
                (
                    "Legacy Oracle ERP Webhook vs Batch Polling Protocol",
                    UncertaintyCategory.INTEGRATION.value,
                    UncertaintySeverity.HIGH.value,
                    "The specification requires bi-directional sync with legacy enterprise ERP, but does not provide API contracts, webhook capabilities, or batch polling frequencies.",
                    "Source states 'Must synchronize with enterprise backend' without providing API specifications.",
                    "SRC-003",
                    "Event-driven REST Webhook architecture assumed with async retry queue.",
                    False,
                    "Confirm target ERP version, supported integration protocol (REST vs SOAP vs SFTP batch), and sync latency SLA.",
                    "Determines connector architecture, dead-letter queue design, and ERP network gateway configuration."
                ),
                (
                    "Statutory PII Data Retention & GDPR Redaction Schedule",
                    UncertaintyCategory.COMPLIANCE.value,
                    UncertaintySeverity.MEDIUM.value,
                    "The platform processes customer complaint communications containing PII, but no statutory data retention schedule or purge policy was specified.",
                    "No source evidence found regarding data retention schedules.",
                    "SRC-004",
                    "90-day active retention with automated AES-256 encrypted archival and PII masking on UI views assumed.",
                    False,
                    "Confirm data retention duration (e.g. 1 year vs 7 years) and Right-to-be-Forgotten deletion workflows.",
                    "Governs PostgreSQL database archiving jobs, cloud backup storage quotas, and compliance certifications."
                )
            ]
            
            for utitle, ucat, usev, uwhat, uwhy, usrc, uass, urisk, uconf, uimp in unc_defs:
                ev_obj = ev_map.get(usrc)
                session.add(RequirementUncertainty(
                    id=str(uuid.uuid4()),
                    project_id=proj_id,
                    title=utitle,
                    category=ucat,
                    severity=usev,
                    status=UncertaintyStatus.UNCONFIRMED.value,
                    what_is_unclear=uwhat,
                    why_unclear=uwhy,
                    source_evidence_id=ev_obj.id if ev_obj else None,
                    source_code=usrc,
                    document_name=ev_obj.document_name if ev_obj else "Acme_Customer_Complaint_Transformation_BRD.pdf",
                    page_number=ev_obj.page_number if ev_obj else 1,
                    section_heading=ev_obj.section_heading if ev_obj else "Business Requirements",
                    evidence_text=ev_obj.exact_text if ev_obj else "All routine complaints should be resolved automatically within 15 minutes.",
                    assumption=uass,
                    is_high_risk_assumption=urisk,
                    what_to_confirm=uconf,
                    potential_impact=uimp,
                    metadata_json={},
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                ))

        await session.commit()
        print("\n[SUCCESS] RBAC Seed completed successfully!")
        print("==================================================================")
        print("DEV TEST ACCOUNTS (Password for all: TransformIQ@2026):")
        print("  1. ADMIN:              admin@transformiq.local      (Sarah Connor)")
        print("  2. PROJECT OWNER:      owner@transformiq.local      (Elena Rostova)")
        print("  3. BUSINESS ANALYST:   analyst@transformiq.local    (Priya Sharma)")
        print("  4. SOLUTION ARCHITECT: architect@transformiq.local  (David Chen)")
        print("  5. MANAGER:            manager@transformiq.local    (Marcus Vance)")
        print("  6. MEMBER:             member@transformiq.local     (Liam Murphy)")
        print("  7. VIEWER:             viewer@transformiq.local     (Victoria Stone)")
        print("==================================================================")

if __name__ == "__main__":
    asyncio.run(seed_rbac())
