import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User, Organization, Workspace, ProjectMember, UserRole
from app.models.project import Project, BusinessContext, Document, DocumentChunk, ProjectStatus
from app.models.transformation import Requirement, Stakeholder, BusinessProcess, Gap, Recommendation, Solution, RequirementType
from app.models.architecture import ArchitectureComponent, ArchitectureConnection, WorkflowNode, WorkflowEdge
from app.models.design import DatabaseEntity, ApiEndpoint, Wireframe
from app.models.planning import Roadmap, Estimate, Risk, TransformationScore, SimulationScenario
from app.models.collaboration import (
    Conversation, Message, Approval, Comment, Version, Notification, AuditLog, AIRun
)
from app.auth.security import get_password_hash
from app.ai import smart_engine

async def seed_database(db: AsyncSession):
    # Check if already seeded
    res = await db.execute(select(User).filter(User.email == "demo@transformiq.ai"))
    if res.scalars().first():
        return

    # 1. Create Demo Users
    admin_user = User(
        id=str(uuid.uuid4()),
        email="admin@transformiq.ai",
        hashed_password=get_password_hash("Admin@12345"),
        full_name="Kishan Patel (System Admin)",
        role=UserRole.ADMIN.value,
        is_active=True
    )
    demo_user = User(
        id=str(uuid.uuid4()),
        email="demo@transformiq.ai",
        hashed_password=get_password_hash("Demo@12345"),
        full_name="Alex Mercer (Lead Architect)",
        role=UserRole.ARCHITECT.value,
        is_active=True
    )
    db.add_all([admin_user, demo_user])
    await db.flush()

    # 2. Create Organization & Workspace
    org = Organization(
        id=str(uuid.uuid4()),
        name="Apex Global Retail & Logistics",
        slug="apex-global",
        industry="E-Commerce & Supply Chain",
        size="2,500 - 10,000 Employees",
        owner_id=demo_user.id
    )
    db.add(org)
    await db.flush()

    workspace = Workspace(
        id=str(uuid.uuid4()),
        name="Customer Experience & AI Modernization",
        description="Digital transformation initiatives targeting customer support, claims automation, and logistics routing.",
        organization_id=org.id
    )
    db.add(workspace)
    await db.flush()

    # 3. Create Demo Project
    project = Project(
        id=str(uuid.uuid4()),
        name="Omni-Channel Customer Complaint & Triage Transformation",
        slug="omni-channel-customer-complaint-transformation",
        description="Enterprise transformation to automate customer complaint ingestion, categorization, sentiment extraction, and autonomous department routing.",
        workspace_id=workspace.id,
        status=ProjectStatus.ANALYSIS.value,
        industry="Retail & E-Commerce",
        organization_size="5,000 Employees",
        business_objective="Reduce initial complaint triage latency from 48 hours to under 15 minutes, eliminate manual misrouting, and achieve 75%+ straight-through automated resolution for tier-1 cases.",
        business_problem="Customer complaints received across email, web forms, and Zendesk are manually reviewed by 14 triage agents. High human error (18% misroute rate), high turnover, and delayed resolutions cause $1.2M in annual customer churn.",
        current_systems="Zendesk Enterprise, Salesforce Service Cloud, Legacy SQL Server 2012, Shared Outlook Inboxes, Manual Excel Logs.",
        expected_outcome="Autonomous AI classification pipeline, multi-tenant agent copilot, automated SLA escalations, sub-second vector search over SOPs.",
        constraints="Must comply with GDPR/CCPA for PII redaction, 99.9% uptime SLA, integrate with legacy on-prem CRM via REST adapters.",
        budget=185000.0,
        timeline_months=4
    )
    db.add(project)
    await db.flush()

    # Membership
    member = ProjectMember(
        id=str(uuid.uuid4()),
        project_id=project.id,
        user_id=demo_user.id,
        role=UserRole.PROJECT_OWNER.value
    )
    db.add(member)

    # 4. Ingest Sample Document & Chunks
    doc = Document(
        id=str(uuid.uuid4()),
        project_id=project.id,
        filename="Customer_Support_SOP_and_BRD_v2.pdf",
        file_type="pdf",
        file_size=428000,
        storage_path="./uploads/Customer_Support_SOP_and_BRD_v2.pdf",
        extracted_text="Customer Support Standard Operating Procedure (SOP) & Business Requirements Document (BRD). All incoming complaints must be classified into Billing, Delivery, Product Quality, or Account Security. Escalations must occur within 2 hours for Platinum accounts.",
        summary="Defines triage policies, escalation SLAs, and manual department queues.",
        status="PROCESSED"
    )
    db.add(doc)
    await db.flush()

    chunk = DocumentChunk(
        id=str(uuid.uuid4()),
        document_id=doc.id,
        chunk_index=0,
        content="Section 4.2: Triage SLAs - Urgent complaints involving billing discrepancies or shipment damages over $500 must receive immediate routing to Senior Finance within 30 minutes.",
        page_number=1,
        metadata_json={"section": "4.2", "policy": "SLA"}
    )
    db.add(chunk)

    # 5. Populate Context & Analysis Elements
    ctx_data = {
        "name": project.name,
        "industry": project.industry,
        "business_problem": project.business_problem,
        "business_objective": project.business_objective
    }
    
    ba = smart_engine.build_contextual_business_analysis(ctx_data)
    for r in ba.get("functional_requirements", []) + ba.get("non_functional_requirements", []):
        db.add(Requirement(
            id=str(uuid.uuid4()),
            project_id=project.id,
            code=r["code"],
            title=r["title"],
            description=r["description"],
            req_type=r["req_type"],
            priority=r["priority"],
            source=r["source"],
            confidence=0.95
        ))
    for s in ba.get("stakeholders", []):
        db.add(Stakeholder(
            id=str(uuid.uuid4()),
            project_id=project.id,
            name=s["name"],
            role=s["role"],
            department=s["department"],
            influence=s["influence"],
            interest=s["interest"],
            key_concerns=s["key_concerns"]
        ))
    db.add(BusinessProcess(
        id=str(uuid.uuid4()),
        project_id=project.id,
        name="Customer Complaint Triage & Resolution",
        description="AS-IS manual routing vs TO-BE autonomous AI workflow.",
        as_is_steps=ba.get("as_is_process", []),
        cycle_time_current="48 Hours",
        cycle_time_projected="12 Minutes",
        bottlenecks=["Manual email triage officer delay", "Subjective department classification errors"]
    ))

    # 6. Gaps
    gap_data = smart_engine.build_contextual_gap_analysis(ctx_data)
    for g in gap_data.get("gaps", []):
        db.add(Gap(
            id=str(uuid.uuid4()),
            project_id=project.id,
            category=g.get("category", "Process"),
            title=g.get("title") or g.get("gap_title", "Identified Gap"),
            current_state=g.get("current_state", "Manual operations"),
            desired_state=g.get("desired_state", "Automated operations"),
            severity=g.get("severity", "MEDIUM"),
            impact=g.get("impact", "Operational latency"),
            root_cause=g.get("root_cause", "Legacy system limitations"),
            recommended_action=g.get("recommended_action", "Implement automation")
        ))

    # 7. Recommendations & Solution
    rec_data = smart_engine.build_contextual_recommendations(ctx_data)
    for rc in rec_data.get("recommendations", []):
        db.add(Recommendation(
            id=str(uuid.uuid4()),
            project_id=project.id,
            category=rc.get("category", "General"),
            title=rc.get("title", "Transformation Recommendation"),
            description=rc.get("description", "Recommended architectural upgrade"),
            reason=rc.get("reason", "Improves operational efficiency"),
            expected_impact=rc.get("expected_impact", "HIGH"),
            feasibility=rc.get("feasibility", "HIGH"),
            priority=rc.get("priority", "HIGH"),
            confidence_score=rc.get("confidence_score", 0.95),
            source_citation=rc.get("source_citation", "Enterprise Requirements"),
            dependencies=rc.get("dependencies", []),
            status="APPROVED"
        ))
    db.add(Solution(
        id=str(uuid.uuid4()),
        project_id=project.id,
        name=rec_data.get("recommended_solution_name", "Enterprise Solution"),
        tagline=rec_data.get("tagline", "Digital Transformation Engine"),
        executive_summary=rec_data.get("executive_summary", "Solution architecture"),
        technology_stack=rec_data.get("technology_stack", {}),
        key_capabilities=rec_data.get("key_capabilities", []),
        expected_roi=rec_data.get("expected_roi", "300% ROI"),
        implementation_approach="Phased agile rollout across 4 sprints with canary model deployment."
    ))

    # 8. Architecture Components & Connections
    arch_data = smart_engine.build_contextual_architecture(ctx_data)
    comp_map = {}
    for comp in arch_data.get("components", []):
        unique_id = f"{project.id[:8]}_{comp['id']}"
        comp_map[comp["id"]] = unique_id
        db.add(ArchitectureComponent(
            id=unique_id,
            project_id=project.id,
            name=comp["name"],
            layer=comp["layer"],
            tech_stack=comp["tech_stack"],
            description=comp["description"],
            responsibilities=comp["responsibilities"],
            position_x=comp["position_x"],
            position_y=comp["position_y"]
        ))
    for conn in arch_data.get("connections", []):
        db.add(ArchitectureConnection(
            id=str(uuid.uuid4()),
            project_id=project.id,
            source_component_id=comp_map.get(conn["source"], conn["source"]),
            target_component_id=comp_map.get(conn["target"], conn["target"]),
            protocol=conn["protocol"],
            data_payload=conn.get("data_payload"),
            is_async=conn.get("is_async", False)
        ))

    # 9. Workflow Nodes & Edges
    wf_data = smart_engine.build_contextual_process_workflow(ctx_data)
    for node in wf_data.get("nodes", []):
        db.add(WorkflowNode(
            id=f"{project.id[:8]}_{node['id']}",
            project_id=project.id,
            node_key=node["node_key"],
            node_type=node["node_type"],
            label=node["label"],
            description=node["description"],
            actor=node["actor"],
            system=node["system"],
            input_data=node.get("input_data"),
            output_data=node.get("output_data"),
            swimlane=node.get("swimlane"),
            position_x=node["position_x"],
            position_y=node["position_y"]
        ))
    for edge in wf_data.get("edges", []):
        db.add(WorkflowEdge(
            id=str(uuid.uuid4()),
            project_id=project.id,
            source_node_key=edge["source"],
            target_node_key=edge["target"],
            label=edge.get("label"),
            condition=edge.get("condition")
        ))

    # 10. Database, APIs & UX Wireframes
    db_data = smart_engine.build_contextual_database(ctx_data)
    for ent in db_data.get("entities", []):
        db.add(DatabaseEntity(
            id=str(uuid.uuid4()),
            project_id=project.id,
            name=ent["name"],
            description=ent["description"],
            fields_data=ent["fields"],
            relationships_data=ent.get("relationships", []),
            indexes=ent.get("indexes", [])
        ))

    api_data = smart_engine.build_contextual_apis(ctx_data)
    for ep in api_data.get("endpoints", []):
        db.add(ApiEndpoint(
            id=str(uuid.uuid4()),
            project_id=project.id,
            method=ep["method"],
            path=ep["path"],
            summary=ep["summary"],
            description=ep["description"],
            category=ep["category"],
            auth_required=ep["auth_required"],
            request_body=ep.get("request_body"),
            response_body=ep.get("response_body"),
            error_responses=ep.get("error_responses", [])
        ))

    ux_data = smart_engine.build_contextual_ux(ctx_data)
    for wf in ux_data.get("wireframes", []):
        db.add(Wireframe(
            id=str(uuid.uuid4()),
            project_id=project.id,
            screen_name=wf["screen_name"],
            purpose=wf["purpose"],
            target_users=wf["target_users"],
            layout_type=wf["layout_type"],
            components_json=wf["components"],
            user_actions=wf["user_actions"]
        ))

    # 11. Planning, Estimates, Risks, Scores & Simulations
    plan_data = smart_engine.build_contextual_planning(ctx_data)
    db.add(Roadmap(
        id=str(uuid.uuid4()),
        project_id=project.id,
        name=plan_data["name"],
        total_duration_weeks=plan_data["total_duration_weeks"],
        phases=plan_data["phases"]
    ))

    est_data = smart_engine.build_contextual_estimates(ctx_data)
    db.add(Estimate(
        id=str(uuid.uuid4()),
        project_id=project.id,
        total_estimated_hours=est_data["total_estimated_hours"],
        total_estimated_cost=est_data["total_estimated_cost"],
        currency="USD",
        duration_months=est_data["duration_months"],
        roles_breakdown=est_data["roles_breakdown"],
        infrastructure_cost=est_data.get("infrastructure_cost_monthly", 0.0),
        ai_api_cost_monthly=est_data.get("ai_api_cost_monthly", 0.0),
        assumptions=est_data["assumptions"]
    ))

    risk_data = smart_engine.build_contextual_risks(ctx_data)
    for rk in risk_data.get("risks", []):
        db.add(Risk(
            id=str(uuid.uuid4()),
            project_id=project.id,
            category=rk.get("category", "General"),
            title=rk.get("title") or rk.get("risk_title", "Identified Risk"),
            description=rk.get("description") or rk.get("mitigation", "Risk description"),
            probability=rk.get("probability") or rk.get("likelihood", "MEDIUM"),
            impact=rk.get("impact", "HIGH"),
            severity=rk.get("severity") or rk.get("impact", "HIGH"),
            mitigation_strategy=rk.get("mitigation_strategy") or rk.get("mitigation", "Standard mitigation strategy."),
            owner=rk.get("owner", "Lead Architect / PM")
        ))

    score_data = smart_engine.build_contextual_score(ctx_data)
    db.add(TransformationScore(
        id=str(uuid.uuid4()),
        project_id=project.id,
        overall_score=score_data["overall_score"],
        ai_readiness=score_data["ai_readiness"],
        automation_potential=score_data["automation_potential"],
        data_readiness=score_data["data_readiness"],
        business_impact=score_data["business_impact"],
        technical_feasibility=score_data["technical_feasibility"],
        implementation_readiness=score_data["implementation_readiness"],
        key_drivers=score_data["key_drivers"],
        key_blockers=score_data["key_blockers"],
        strategic_recommendations=score_data["strategic_recommendations"]
    ))

    sim_res = smart_engine.calculate_what_if_simulation({"automation_level": 75, "team_size": 6, "budget": 150000.0, "timeline_months": 4})
    db.add(SimulationScenario(
        id=str(uuid.uuid4()),
        project_id=project.id,
        scenario_name=sim_res["scenario_name"],
        automation_level=sim_res["automation_level"],
        team_size=sim_res["team_size"],
        budget=sim_res["budget"],
        timeline_months=sim_res["timeline_months"],
        ai_adoption_level=sim_res["ai_adoption_level"],
        projected_effort_hours=sim_res["projected_effort_hours"],
        projected_cost=sim_res["projected_cost"],
        projected_timeline_months=sim_res["projected_timeline_months"],
        expected_roi_percentage=sim_res["expected_roi_percentage"],
        efficiency_gain_percentage=sim_res["efficiency_gain_percentage"],
        risk_level=sim_res["risk_level"],
        simulation_insights=sim_res["simulation_insights"]
    ))

    # 12. Approvals, Comments, Audit Logs & Notifications
    db.add(Approval(
        id=str(uuid.uuid4()),
        project_id=project.id,
        artifact_type="BLUEPRINT",
        status="APPROVED",
        requested_by="Alex Mercer (Lead Architect)",
        reviewed_by="Kishan Patel (System Admin)",
        comments="Approved for MVP Phase 1 rollout.",
        decision_date=datetime.utcnow()
    ))
    db.add(Comment(
        id=str(uuid.uuid4()),
        project_id=project.id,
        author_id=demo_user.id,
        section="architecture",
        content="Architecture reviewed. The decoupled FastAPI gateway and pgvector semantic search layer satisfy the sub-500ms SLA target."
    ))
    db.add(AuditLog(
        id=str(uuid.uuid4()),
        project_id=project.id,
        user_id=demo_user.id,
        user_name="Alex Mercer",
        action="SEEDED_INITIAL_TRANSFORMATION",
        details="Initialized Customer Support Transformation with complete 24-dimension blueprint.",
        created_at=datetime.utcnow()
    ))
    db.add(Notification(
        id=str(uuid.uuid4()),
        user_id=demo_user.id,
        title="Transformation Blueprint Ready",
        message="Your Customer Support Transformation blueprint has been generated and validated with an 88/100 readiness score.",
        type="SUCCESS",
        link=f"/projects/{project.id}/blueprint"
    ))

    await db.commit()
