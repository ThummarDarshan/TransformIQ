import asyncio
import os
import sys
import uuid
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from app.config.database import AsyncSessionLocal
from app.models.user import User, Organization, Workspace, ProjectMember, UserRole
from app.models.project import Project, ProjectStatus, BusinessContext, Document
from app.models.transformation import Requirement, Stakeholder, BusinessProcess, Gap, Recommendation, Solution, RequirementType
from app.models.architecture import ArchitectureComponent, ArchitectureConnection, WorkflowNode, WorkflowEdge
from app.models.design import DatabaseEntity, ApiEndpoint, Wireframe
from app.models.planning import Roadmap, Estimate, Risk, TransformationScore
from app.models.collaboration import Approval, AuditLog, Version
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
            
        # 7. Requirements
        res_req = await session.execute(select(Requirement).filter(Requirement.project_id == proj_id))
        if not res_req.scalars().all():
            reqs = [
                ("REQ-F01", "Automated Multi-Class Complaint Triage", "AI engine must classify incoming emails into 14 distinct issue taxonomies with >92% accuracy.", "CRITICAL", RequirementType.FUNCTIONAL.value),
                ("REQ-F02", "Real-Time Sentiment & Urgency Scoring", "Extract customer emotional urgency score (0-100) to trigger immediate escalation for VIP or churn-risk customers.", "HIGH", RequirementType.FUNCTIONAL.value),
                ("REQ-F03", "Zendesk & CRM Bi-Directional Sync", "Automatically enrich ticket fields, assign departmental queues, and trigger resolution workflows.", "HIGH", RequirementType.FUNCTIONAL.value),
                ("REQ-F04", "Human-in-the-Loop Override Console", "Specialist dashboard to review confidence scores <80% and validate AI decisions.", "MEDIUM", RequirementType.FUNCTIONAL.value),
                ("REQ-NF01", "Sub-500ms AI Processing Latency", "End-to-end classification and queue routing must complete in under 500 milliseconds.", "CRITICAL", RequirementType.NON_FUNCTIONAL.value),
                ("REQ-NF02", "PII Redaction & GDPR Compliance", "Automated masking of credit card numbers, social security numbers, and sensitive health data.", "CRITICAL", RequirementType.NON_FUNCTIONAL.value),
            ]
            for code, title, desc, prio, rtype in reqs:
                session.add(Requirement(
                    id=str(uuid.uuid4()),
                    project_id=proj_id,
                    code=code,
                    title=title,
                    description=desc,
                    priority=prio,
                    req_type=rtype,
                    source="Business Analyst Discovery"
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
            details="Customer Complaint Transformation initiative seeded with full 13-stage artifacts and 7 RBAC roles.",
            ip_address="127.0.0.1"
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
