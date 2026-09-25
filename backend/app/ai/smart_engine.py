import uuid
from typing import Dict, Any, List

def detect_domain(ctx: Dict[str, Any]) -> str:
    combined = (
        f"{ctx.get('name', '')} "
        f"{ctx.get('industry', '')} "
        f"{ctx.get('business_problem', '')} "
        f"{ctx.get('business_objective', '')}"
    ).lower()

    if any(k in combined for k in ["hr ", "hr consultancy", "recruitment", "recruiter", "candidate", "placement", "applicant", "staffing", "talent", "onboarding", "attendance", "ats"]):
        return "HR_RECRUITING"
    elif any(k in combined for k in ["complaint", "ticket", "triage", "customer service", "helpdesk", "case resolution", "sentiment"]):
        return "CUSTOMER_SUPPORT"
    elif any(k in combined for k in ["pos", "warehouse", "inventory", "stockout", "stock", "omni-channel", "omni", "supply chain", "store pos", "e-commerce & retail", "retail"]):
        return "RETAIL_SUPPLY_CHAIN"
    elif any(k in combined for k in ["fintech", "bank", "payment", "lending", "credit", "loan", "fraud", "kyc"]):
        return "FINTECH_BANKING"
    elif any(k in combined for k in ["health", "hospital", "clinic", "patient", "medical", "pharma", "clinical"]):
        return "HEALTHCARE"
    return "ENTERPRISE_GENERAL"


def build_contextual_business_analysis(ctx: Dict[str, Any]) -> Dict[str, Any]:
    project_name = ctx.get("name", "Digital Transformation Project")
    industry = ctx.get("industry", "Enterprise Services")
    problem = ctx.get("business_problem") or "Manual fragmented workflows, slow turnaround times, and lack of automated intelligence across operations."
    objective = ctx.get("business_objective") or "Automate end-to-end processing, reduce operational costs by 60%, and elevate customer satisfaction."
    domain = detect_domain(ctx)

    if domain == "HR_RECRUITING":
        return {
            "business_summary": f"{project_name} addresses critical operational bottlenecks for HR consultancy operations. Currently, candidate profiles and client accounts are scattered across 5 disconnected Excel sheets, client onboarding takes 2 weeks of manual paperwork, and recruiter attendance/placements lack centralized tracking.",
            "objectives": [
                "Eliminate duplicate candidate records by centralizing into a unified AI-powered ATS & CRM.",
                "Compress client onboarding lifecycle from 14 days to under 3 business days via automated digital workflows.",
                "Deploy automated recruiter attendance tracking and real-time placement pipeline visibility.",
                "Launch a responsive public-facing portal to showcase services and capture inbound client requisitions."
            ],
            "stakeholders": [
                {"name": "Aarav Sharma", "role": "Managing Director / Sponsor", "department": "Executive Leadership", "influence": "HIGH", "interest": "HIGH", "key_concerns": "Candidate data security, client onboarding velocity, recruiter ROI."},
                {"name": "Sneha Verma", "role": "Lead Talent Recruiter", "department": "Recruitment Operations", "influence": "HIGH", "interest": "HIGH", "key_concerns": "Ease of resume parsing, instant candidate matching, reduced spreadsheet overhead."},
                {"name": "Vikram Malhotra", "role": "Client Relationship Director", "department": "Business Development", "influence": "HIGH", "interest": "HIGH", "key_concerns": "Client contract SLAs, fast requisition fulfillment, zero lost leads."},
                {"name": "Ananya Desai", "role": "HR & Compliance Specialist", "department": "Human Resources & Legal", "influence": "MEDIUM", "interest": "HIGH", "key_concerns": "Recruiter attendance integrity, candidate privacy (GDPR/DPDP), employment audit trails."}
            ],
            "functional_requirements": [
                {"code": "REQ-HR-001", "title": "AI Resume Ingestion & Parsing", "description": "Extract structured candidate skills, experience, and contact data from uploaded PDF/Word resumes into unified profiles.", "req_type": "FUNCTIONAL", "priority": "CRITICAL", "source": "Recruiter Operations Requirements"},
                {"code": "REQ-HR-002", "title": "Recruiter CRM & Client Account Tracking", "description": "Manage client job requisitions, candidate submissions, interview stages, and billing contracts in one unified system.", "req_type": "FUNCTIONAL", "priority": "CRITICAL", "source": "Business Development Discovery"},
                {"code": "REQ-HR-003", "title": "Recruiter Attendance & Activity Engine", "description": "Automate daily recruiter attendance logging, check-in/check-out telemetry, and weekly activity dashboards.", "req_type": "FUNCTIONAL", "priority": "HIGH", "source": "Management Governance Policy"},
                {"code": "REQ-HR-004", "title": "Client Self-Service Onboarding Portal", "description": "Allow enterprise clients to upload job requirements, view shortlisted candidates, and approve interview schedules online.", "req_type": "FUNCTIONAL", "priority": "HIGH", "source": "Client Onboarding Standard"}
            ],
            "non_functional_requirements": [
                {"code": "NFR-HR-001", "title": "Candidate Data Privacy & Encryption", "description": "All candidate PII and resumes encrypted at rest (AES-256) with strict RBAC access policies.", "req_type": "NON_FUNCTIONAL", "priority": "CRITICAL", "source": "Security & Compliance Policy"},
                {"code": "NFR-HR-002", "title": "Sub-Second Resume Semantic Search", "description": "Execute vector similarity search across 100,000+ candidate profiles in under 350ms.", "req_type": "NON_FUNCTIONAL", "priority": "HIGH", "source": "System Performance Benchmark"},
                {"code": "NFR-HR-003", "title": "Zero Data Loss Multi-Tenant Architecture", "description": "Automated daily point-in-time PostgreSQL backups and 99.9% application uptime.", "req_type": "NON_FUNCTIONAL", "priority": "CRITICAL", "source": "Enterprise IT Policy"}
            ],
            "pain_points": [
                "Candidate records duplicated across 5 separate Excel workbooks causing recruiter confusion.",
                "Manual paperwork and email ping-pong stretches client onboarding to 14 days.",
                "No centralized visibility into which candidates are submitted, interviewed, or placed.",
                "Recruiter attendance and daily outreach tracked on paper sheets without accountability."
            ],
            "as_is_process": [
                {"step_number": 1, "activity": "Recruiter receives resume via personal email / WhatsApp", "actor": "Recruiter", "system": "Email / Messaging", "duration": "Variable", "is_bottleneck": False, "pain_points": "Unstructured storage"},
                {"step_number": 2, "activity": "Manually copy-paste candidate details into Excel workbook", "actor": "Recruiter", "system": "Excel Workbooks", "duration": "30 - 45 Mins", "is_bottleneck": True, "pain_points": "Typing errors & duplicate entries"},
                {"step_number": 3, "activity": "Email client company PDF profiles for requisition review", "actor": "Recruiter", "system": "Email Client", "duration": "2 - 5 Days", "is_bottleneck": True, "pain_points": "Lost email threads and delay"},
                {"step_number": 4, "activity": "Manual paper contracts and email exchange for client onboarding", "actor": "Client Lead", "system": "Paper / Scanned PDF", "duration": "7 - 14 Days", "is_bottleneck": True, "pain_points": "Paperwork friction"},
                {"step_number": 5, "activity": "Manual placement recording and monthly invoicing", "actor": "Accountant", "system": "Spreadsheet", "duration": "3 - 5 Days", "is_bottleneck": False, "pain_points": "Revenue leakage"}
            ],
            "kpis": [
                "Client Onboarding Turnaround (Target: < 3 Days)",
                "Resume Screening to Shortlist Time (Target: < 2 Hours)",
                "Candidate Record Duplication Rate (Target: 0%)",
                "Recruiter Daily Placement Throughput (Target: +45%)"
            ],
            "confidence_level": 0.98
        }
    elif domain == "RETAIL_SUPPLY_CHAIN":
        return {
            "business_summary": f"{project_name} addresses core supply chain and retail friction in {industry}. Fragmented legacy warehouse operations and offline POS sync delays cause recurring stockouts, inaccurate inventory counts, and multi-channel fulfillment bottlenecks.",
            "objectives": [
                "Deploy real-time event-driven inventory synchronization across all offline POS terminals and central warehouses.",
                "Eliminate retail stockouts by 80% through automated predictive replenishment algorithms.",
                "Unify in-store POS and e-commerce checkout into a single real-time stock allocation ledger.",
                "Reduce warehouse order pick-pack-ship cycle latency from 24h to under 2 hours."
            ],
            "stakeholders": [
                {"name": "Robert Chen", "role": "VP of Supply Chain & Retail Operations", "department": "Executive Leadership", "influence": "HIGH", "interest": "HIGH", "key_concerns": "Inventory accuracy, stockout reduction, store ROI."},
                {"name": "Maria Santos", "role": "Director of Warehouse Logistics", "department": "Distribution Operations", "influence": "HIGH", "interest": "HIGH", "key_concerns": "Pick-pack throughput, barcode scanning latency, warehouse capacity."},
                {"name": "Tariq Al-Mansoor", "role": "Head of Retail Store Systems", "department": "Retail IT", "influence": "HIGH", "interest": "HIGH", "key_concerns": "Offline POS survivability, sub-second sync, barcode terminal integration."},
                {"name": "Lisa Wong", "role": "Financial Controller & Auditor", "department": "Finance & Audit", "influence": "MEDIUM", "interest": "HIGH", "key_concerns": "Inventory shrink control, automated COGS accounting, reconciliation accuracy."}
            ],
            "functional_requirements": [
                {"code": "REQ-RET-001", "title": "Real-Time Multi-Warehouse Inventory Ledger", "description": "Maintain sub-second accurate stock counts across all distribution centers and retail stores with pessimistic lock guards.", "req_type": "FUNCTIONAL", "priority": "CRITICAL", "source": "Supply Chain Blueprint"},
                {"code": "REQ-RET-002", "title": "Offline-First Store POS Synchronization", "description": "Allow cash registers to process sales offline during network outages and auto-sync transactions upon reconnection.", "req_type": "FUNCTIONAL", "priority": "CRITICAL", "source": "Retail Store IT Spec"},
                {"code": "REQ-RET-003", "title": "Predictive Stockout & Auto-Replenishment Engine", "description": "Forecast store demand based on historical velocity and generate automated warehouse transfer orders.", "req_type": "FUNCTIONAL", "priority": "HIGH", "source": "Inventory Operations Policy"},
                {"code": "REQ-RET-004", "title": "Omni-Channel Unified Order Routing", "description": "Route online orders to the closest store or fulfillment center with available inventory for instant click-and-collect.", "req_type": "FUNCTIONAL", "priority": "HIGH", "source": "E-Commerce Architecture"}
            ],
            "non_functional_requirements": [
                {"code": "NFR-RET-001", "title": "Sub-100ms POS Transaction Response Time", "description": "Ensure barcode scan to inventory lock response completes in under 100ms at checkout.", "req_type": "NON_FUNCTIONAL", "priority": "CRITICAL", "source": "Checkout Performance Standard"},
                {"code": "NFR-RET-002", "title": "Event Bus Scalability (50,000 events/sec)", "description": "Handle peak Black Friday / holiday transaction surges without event queue dropouts.", "req_type": "NON_FUNCTIONAL", "priority": "CRITICAL", "source": "Infrastructure Sizing Spec"},
                {"code": "NFR-RET-003", "title": "PCI-DSS Level 1 & Audit Compliance", "description": "Tokenize all payment data and maintain immutable stock ledger transaction logs.", "req_type": "NON_FUNCTIONAL", "priority": "CRITICAL", "source": "Security & Financial Policy"}
            ],
            "pain_points": [
                "Nightly batch POS updates result in up to 24 hours of phantom inventory and customer stockouts.",
                "Warehouse management systems operate in isolated silos without visibility into store stock.",
                "Over 12% of online orders cancelled due to conflicting store checkout purchases.",
                "Manual inventory counts require closing retail branches for multiple business days."
            ],
            "as_is_process": [
                {"step_number": 1, "activity": "Customer purchases item at retail store cash register", "actor": "Store Cashier", "system": "Offline POS Terminal", "duration": "Instant", "is_bottleneck": False, "pain_points": None},
                {"step_number": 2, "activity": "POS logs sale locally on local terminal disk", "actor": "POS System", "system": "Local SQLite DB", "duration": "100ms", "is_bottleneck": False, "pain_points": "Isolated from central DB"},
                {"step_number": 3, "activity": "Nightly batch CSV export uploaded to central server at 11 PM", "actor": "Batch Cron", "system": "FTP / Batch Script", "duration": "12 - 18 Hours", "is_bottleneck": True, "pain_points": "24-hour stock blindness"},
                {"step_number": 4, "activity": "Warehouse staff manually checks physical bins for restocking", "actor": "Warehouse Worker", "system": "Clipboard / Paper", "duration": "4 - 8 Hours", "is_bottleneck": True, "pain_points": "Misplaced stock & stockouts"},
                {"step_number": 5, "activity": "Manager places emergency purchase orders with supplier", "actor": "Store Manager", "system": "Email / Phone", "duration": "2 - 4 Days", "is_bottleneck": True, "pain_points": "High expedited freight costs"}
            ],
            "kpis": [
                "Stockout Rate Reduction (Target: -80%)",
                "Inventory Count Accuracy (Target: > 99.4%)",
                "POS Real-Time Sync Latency (Target: < 500ms)",
                "Fulfillment Cycle Time (Target: < 2 Hours)"
            ],
            "confidence_level": 0.97
        }
    else:
        # Default / Customer Support / General
        return {
            "business_summary": f"{project_name} targets high-friction operational processes in {industry}. The current manual workflow suffers from delays, human triage overhead, and fragmented systems: {problem[:180]}...",
            "objectives": [
                f"Achieve 85%+ straight-through automated processing for {project_name}.",
                "Reduce operational cycle latency from 48 hours to under 15 minutes.",
                "Eliminate manual triage errors and enforce 99.9% SLA compliance.",
                "Deliver real-time visibility through interactive executive dashboards."
            ],
            "stakeholders": [
                {"name": "Sarah Jenkins", "role": "VP of Operations / Sponsor", "department": "Executive Leadership", "influence": "HIGH", "interest": "HIGH", "key_concerns": "Cost of transformation, business continuity, ROI within 12 months."},
                {"name": "Marcus Vance", "role": "Head of IT & Enterprise Architecture", "department": "Information Technology", "influence": "HIGH", "interest": "HIGH", "key_concerns": "Security posture, zero-trust API integration, and cloud scalability."},
                {"name": "Priya Patel", "role": "Operations Team Lead", "department": "Frontline Operations", "influence": "MEDIUM", "interest": "HIGH", "key_concerns": "User experience, agent learning curve, and reduction of manual entry."},
                {"name": "David Thorne", "role": "Compliance & Risk Director", "department": "Governance & Legal", "influence": "HIGH", "interest": "MEDIUM", "key_concerns": "Data privacy (GDPR/SOC2), audit trails, and explainability."}
            ],
            "functional_requirements": [
                {"code": "REQ-001", "title": "Automated Multi-Channel Ingestion", "description": f"Ingest requests, tickets, and documents seamlessly via REST APIs, Email webhooks, and Portal uploads in {industry}.", "req_type": "FUNCTIONAL", "priority": "CRITICAL", "source": "Initial Problem Statement & Discovery"},
                {"code": "REQ-002", "title": "AI Classification & Sentiment Routing", "description": "Utilize NLP and LLM classifiers to categorize incoming cases, detect customer sentiment, and calculate urgency scores.", "req_type": "FUNCTIONAL", "priority": "HIGH", "source": "SOP & Operational Guidelines"},
                {"code": "REQ-003", "title": "Human-in-the-Loop Escalation Matrix", "description": "Provide a dedicated review queue for cases where AI confidence falls below 85% or regulatory escalation is required.", "req_type": "FUNCTIONAL", "priority": "CRITICAL", "source": "Governance & Compliance Standard"},
                {"code": "REQ-004", "title": "Real-Time Telemetry & SLA Tracking", "description": "Track resolution time, agent productivity, and automated resolution rates on live interactive dashboards.", "req_type": "FUNCTIONAL", "priority": "MEDIUM", "source": "Operations Team Lead Requirements"}
            ],
            "non_functional_requirements": [
                {"code": "NFR-001", "title": "High Availability & 99.95% Uptime", "description": "Deploy across multi-zone container clusters with automated failover and zero-downtime rolling deployments.", "req_type": "NON_FUNCTIONAL", "priority": "CRITICAL", "source": "Enterprise IT Architecture Policy"},
                {"code": "NFR-002", "title": "Sub-Second API Response Times", "description": "Ensure 95th percentile response times for synchronous AI classification endpoints stay under 450ms.", "req_type": "NON_FUNCTIONAL", "priority": "HIGH", "source": "Performance Standards"},
                {"code": "NFR-003", "title": "Enterprise Security & RBAC Encryption", "description": "All data encrypted at rest (AES-256) and in transit (TLS 1.3) with strict Role-Based Access Control and audit logging.", "req_type": "NON_FUNCTIONAL", "priority": "CRITICAL", "source": "Security & Compliance Policy"}
            ],
            "pain_points": [
                "Manual ticket classification and assignment creates a 24-48 hour initial latency bottleneck.",
                "High variance in human judgment leads to 18% misrouted cases across departments.",
                "Lack of unified knowledge base forces agents to context-switch across 4 disconnected legacy systems.",
                "Zero proactive alerts on SLA breaches causing high customer churn and executive dissatisfaction."
            ],
            "as_is_process": [
                {"step_number": 1, "activity": "Customer submits issue via portal or email", "actor": "Customer", "system": "Mail Server / Web Form", "duration": "Instant", "is_bottleneck": False, "pain_points": None},
                {"step_number": 2, "activity": "Manual triage officer opens email, reads unstructured text", "actor": "Triage Officer", "system": "Email Client", "duration": "4 - 8 Hours", "is_bottleneck": True, "pain_points": "Manual reading delay"},
                {"step_number": 3, "activity": "Manually determine priority and assign department tag", "actor": "Triage Officer", "system": "Legacy CRM", "duration": "2 - 4 Hours", "is_bottleneck": True, "pain_points": "Subjective classification errors"},
                {"step_number": 4, "activity": "Department agent reviews and searches SOP guidelines", "actor": "Support Agent", "system": "PDF Documents / Shared Drive", "duration": "12 - 24 Hours", "is_bottleneck": True, "pain_points": "Fragmented knowledge"},
                {"step_number": 5, "activity": "Agent types response and closes ticket", "actor": "Support Agent", "system": "Legacy CRM", "duration": "2 - 6 Hours", "is_bottleneck": False, "pain_points": "Repetitive boilerplate writing"}
            ],
            "kpis": [
                "Straight-Through Processing Rate (Target: > 75%)",
                "Mean Time to Resolution (MTTR) Reduction (Target: -70%)",
                "First Contact Resolution (FCR) (Target: > 85%)",
                "Customer Satisfaction (CSAT) (Target: 4.6 / 5.0)"
            ],
            "confidence_level": 0.96
        }


def build_contextual_gap_analysis(ctx: Dict[str, Any]) -> Dict[str, Any]:
    project_name = ctx.get("name", "TransformIQ Solution")
    industry = ctx.get("industry", "Enterprise Services")
    domain = detect_domain(ctx)

    if domain == "HR_RECRUITING":
        return {
            "summary": f"8-Dimension Gap Analysis for {project_name} reveals severe reliance on 5 manual Excel workbooks, 2-week paper onboarding cycles, lack of recruiter attendance tracking, and absence of an integrated applicant CRM.",
            "total_gaps_count": 8,
            "critical_count": 4,
            "high_count": 3,
            "medium_count": 1,
            "gaps": [
                {"category": "Process", "title": "Spreadsheet-Based Candidate Tracking", "current_state": "Recruiters manage candidate profiles in 5 separate Excel sheets.", "desired_state": "Centralized cloud ATS with automated status pipelines and duplicate detection.", "severity": "CRITICAL", "impact": "High rate of duplicate candidate outreach and lost client submissions.", "root_cause": "Absence of a unified recruiting CRM platform.", "recommended_action": "Implement unified PostgreSQL ATS database with AI candidate profile deduplication."},
                {"category": "Technology", "title": "No Public Web Presence or Inbound Portal", "current_state": "Zero public website; client requisitions received over informal phone/email.", "desired_state": "Modern React web portal with client job requisition submission and candidate showcase.", "severity": "CRITICAL", "impact": "Inability to attract premium enterprise clients or scale brand presence.", "root_cause": "Legacy business model operated entirely offline.", "recommended_action": "Deploy production-grade public website with client requisition forms and employer branding."},
                {"category": "Automation", "title": "2-Week Paperwork-Heavy Client Onboarding", "current_state": "Client contracts and compliance forms exchanged via scanned PDFs taking 14 days.", "desired_state": "3-day digital onboarding with automated document validation and e-signatures.", "severity": "CRITICAL", "impact": "Severe revenue delay and client drop-off during onboarding.", "root_cause": "Manual paper verification and contract creation.", "recommended_action": "Build 1-click digital client onboarding workflow with automated NDA & SLA templates."},
                {"category": "People", "title": "Zero Recruiter Attendance & Telemetry Tracking", "current_state": "Team of 12 recruiters has no centralized check-in or daily outreach accountability.", "desired_state": "Automated attendance logging, interview scheduling, and activity dashboards.", "severity": "HIGH", "impact": "Uneven workload distribution, unmonitored absenteeism, and untracked productivity.", "root_cause": "No HRMS / attendance system configured for internal staff.", "recommended_action": "Integrate daily recruiter attendance engine with activity telemetry."},
                {"category": "AI", "title": "Manual Resume Reading & Skills Tagging", "current_state": "Recruiters spend 4+ hours daily manually reading PDF resumes and typing skills.", "desired_state": "Instant AI resume parser extracting structured skills, experience, and candidate score in <2s.", "severity": "CRITICAL", "impact": "Slow time-to-submit and missed candidate placements for hot openings.", "root_cause": "Lack of NLP document parsing capabilities.", "recommended_action": "Integrate AI Resume Parsing & Semantic Skill Matching Engine."},
                {"category": "Data", "title": "Fragmented Excel Data Silos & Duplicate Profiles", "current_state": "Candidate records exist in multiple file versions without master record control.", "desired_state": "Single Source of Truth (SSOT) database with automatic fuzzy deduplication.", "severity": "HIGH", "impact": "Multiple recruiters contacting same candidate for different clients.", "root_cause": "Lack of relational database architecture.", "recommended_action": "Migrate all Excel archives into 3NF normalized PostgreSQL schema with unique email/phone indexing."},
                {"category": "Integration", "title": "Disjointed Communication Across Email & WhatsApp", "current_state": "Recruiter follow-ups stored in personal inboxes without team visibility.", "desired_state": "Shared communications hub linking client threads directly to candidate profiles.", "severity": "HIGH", "impact": "Lost client leads when recruiters are out of office or resign.", "root_cause": "No centralized communication logger.", "recommended_action": "Implement shared CRM activity timeline and notification dispatch."},
                {"category": "Security", "title": "Unsecured Resume Files on Local Desktops", "current_state": "Candidate resumes and PII stored in unencrypted local folder downloads.", "desired_state": "Encrypted cloud S3 bucket with strict role-based access control.", "severity": "MEDIUM", "impact": "Risk of data leakage and non-compliance with data protection acts.", "root_cause": "No centralized cloud storage policy.", "recommended_action": "Enforce AES-256 cloud blob storage with time-limited signed download URLs."}
            ]
        }
    elif domain == "RETAIL_SUPPLY_CHAIN":
        return {
            "summary": f"8-Dimension Gap Analysis for {project_name} reveals multi-day stock blindness due to batch POS syncing, disconnected warehouse bins, and lack of predictive replenishment.",
            "total_gaps_count": 8,
            "critical_count": 4,
            "high_count": 3,
            "medium_count": 1,
            "gaps": [
                {"category": "Process", "title": "Nightly Batch POS Sync Delay (24h Blindness)", "current_state": "Sales from retail store registers only sync to central server once a day at 11 PM.", "desired_state": "Sub-second event-driven stock synchronization across all stores and online channels.", "severity": "CRITICAL", "impact": "High frequency of customer stockouts and overselling items online.", "root_cause": "Legacy batch FTP architecture designed 10 years ago.", "recommended_action": "Deploy real-time WebSocket / Redis Pub-Sub event stream for instant POS inventory updates."},
                {"category": "Technology", "title": "Disconnected Warehouse & Store Inventory Systems", "current_state": "Distribution centers and retail outlets run separate software with no live visibility.", "desired_state": "Unified multi-location inventory ledger with real-time stock allocation.", "severity": "CRITICAL", "impact": "Emergency expedited freight orders and high inventory carrying costs.", "root_cause": "Siloed procurement and point-of-sale vendor platforms.", "recommended_action": "Consolidate into centralized FastAPI + PostgreSQL inventory engine with multi-warehouse support."},
                {"category": "AI", "title": "Absence of Predictive Restocking & Demand Forecasting", "current_state": "Store managers order replenishment based on subjective gut feel once a week.", "desired_state": "AI predictive replenishment calculating seasonal demand, velocity, and lead time.", "severity": "HIGH", "impact": "Overstock on slow-moving SKUs and stockouts on top 20% revenue drivers.", "root_cause": "No predictive ML forecasting pipelines.", "recommended_action": "Deploy AI demand forecasting model generating automated stock transfer recommendations."},
                {"category": "Automation", "title": "Manual Paper-Based Warehouse Pick-Pack", "current_state": "Warehouse pickers use printed paper sheets to locate items across aisles.", "desired_state": "Digital barcode/QR mobile scanner app with optimized picking routes.", "severity": "HIGH", "impact": "Slow 24-hour fulfillment turnaround and 4.2% picking error rate.", "root_cause": "Lack of digital warehouse management mobility.", "recommended_action": "Build mobile-friendly warehouse fulfillment scanner interface with audio feedback."},
                {"category": "Data", "title": "Inaccurate Stock Count Reconciliation", "current_state": "Physical store counts deviate by >6% from ERP records.", "desired_state": "Real-time cycle count audits with automated shrinkage flagging.", "severity": "HIGH", "impact": "Financial audit adjustments and unexplainable shrinkage losses.", "root_cause": "Untracked returns, breakage, and unrecorded cashier overrides.", "recommended_action": "Implement immutable transaction log ledger for every stock increment/decrement."},
                {"category": "People", "title": "Cashier Friction During Network Outages", "current_state": "POS system halts completely when store internet connection drops.", "desired_state": "Offline-first POS with local IndexedDB/SQLite caching and background synchronization.", "severity": "CRITICAL", "impact": "Store queues, frustrated shoppers, and abandoned carts during network glitches.", "root_cause": "Synchronous online-only POS architecture.", "recommended_action": "Implement Progressive Web App (PWA) POS with offline transaction queue."},
                {"category": "Integration", "title": "Lack of Real-Time Supplier EDI Webhooks", "current_state": "Purchase orders emailed as PDF attachments to suppliers.", "desired_state": "Direct REST API / EDI automated purchase order generation.", "severity": "MEDIUM", "impact": "3-5 day supplier turnaround delay on replenishment.", "root_cause": "Manual procurement order workflows.", "recommended_action": "Expose OpenAPI 3.0 procurement webhooks with automated PO dispatch."},
                {"category": "Security", "title": "Unrestricted Cashier Price Override Access", "current_state": "Any store cashier can alter item price tags without supervisor PIN authentication.", "desired_state": "Role-based authorization and real-time anomaly alerts for price discounts.", "severity": "HIGH", "impact": "Internal fraud risk and margin erosion.", "root_cause": "Missing RBAC policy enforcement at store level.", "recommended_action": "Enforce strict manager PIN/JWT auth guards on discount overrides."}
            ]
        }
    else:
        return {
            "summary": f"Comprehensive 8-dimension gap assessment for {project_name} identifies critical manual bottlenecks, lack of automated intelligence, and integration silos.",
            "total_gaps_count": 8,
            "critical_count": 3,
            "high_count": 3,
            "medium_count": 2,
            "gaps": [
                {"category": "Process", "title": "Manual Step-by-Step Triage & Assignment", "current_state": "Human operators manually review every inbound inquiry and route by memory.", "desired_state": "Automated zero-touch classification and dynamic queue routing powered by AI.", "severity": "CRITICAL", "impact": "24-48 hour delay on urgent customer issues and high operational staffing costs.", "root_cause": "Absence of intelligent workflow orchestration and rules engine.", "recommended_action": "Deploy AI Classification Agent with confidence-based human-in-the-loop fallback."},
                {"category": "Technology", "title": "Siloed Legacy Systems & Monolithic Backend", "current_state": "Customer data, ticket logs, and order history reside in isolated SQL databases.", "desired_state": "Unified API gateway and event-driven microservices architecture.", "severity": "HIGH", "impact": "Context switching, duplicate data entry, and slow API latency.", "root_cause": "Organic accretion of point solutions over 8+ years without enterprise integration strategy.", "recommended_action": "Implement RESTful integration layer and centralized Redis caching layer."},
                {"category": "AI", "title": "Zero Predictive Intelligence or NLP Automation", "current_state": "No AI models in production; 100% human cognitive load for text understanding.", "desired_state": "Transformer-based NLP, sentiment scoring, and retrieval-augmented response generation.", "severity": "CRITICAL", "impact": "Inability to scale during 3x peak load surges without hiring linear staff.", "root_cause": "Lack of AI infrastructure and domain-specific fine-tuned models.", "recommended_action": "Integrate TransformIQ AI Reasoning Engine with vector search over enterprise SOPs."},
                {"category": "Data", "title": "Unstructured Enterprise Knowledge & SOPs", "current_state": "Operational SOPs and resolution guidelines stored in static PDF/Word files on shared drives.", "desired_state": "Vectorized knowledge base with sub-second semantic retrieval (RAG).", "severity": "HIGH", "impact": "Inconsistent agent decisions and prolonged new hire onboarding (6+ weeks).", "root_cause": "No centralized knowledge management or embedding pipeline.", "recommended_action": "Implement automated document ingestion, chunking, and pgvector RAG pipeline."},
                {"category": "People", "title": "High Agent Cognitive Fatigue & Burnout", "current_state": "Agents spend 65% of their working hours on repetitive copy-paste tasks.", "desired_state": "Agents act as supervisors and high-value problem solvers assisted by AI copilots.", "severity": "MEDIUM", "impact": "32% annual staff turnover in support team and degraded morale.", "root_cause": "Lack of smart automation tools and repetitive cognitive friction.", "recommended_action": "Provide AI copilot with 1-click draft generation and context summaries."},
                {"category": "Security", "title": "Absence of Granular RBAC & Audit Trails", "current_state": "Shared departmental logins with no field-level PII masking or immutable audit logging.", "desired_state": "Strict RBAC, JWT token rotation, automated PII redaction, and tamper-evident audit trails.", "severity": "CRITICAL", "impact": "Compliance exposure under GDPR/SOC2 and potential data leakage risks.", "root_cause": "Legacy system architecture lacked modern security standards.", "recommended_action": "Implement JWT authentication, role guards, and audit trail logging on every action."},
                {"category": "Automation", "title": "Lack of SLA Alerting & Auto-Escalations", "current_state": "Breaches discovered only after customer escalation via executive complaints.", "desired_state": "Automated background cron monitors SLA thresholds and triggers tiered escalations.", "severity": "HIGH", "impact": "Customer churn and financial penalties for SLA violations.", "root_cause": "No proactive event-driven monitoring daemon.", "recommended_action": "Build background event bus with automated Slack/Teams and email webhooks."},
                {"category": "Integration", "title": "Batch File Syncs Instead of Real-Time Webhooks", "current_state": "Nightly batch CSV exports to sync customer records with ERP.", "desired_state": "Real-time bidirectional event-driven webhooks and message queues.", "severity": "MEDIUM", "impact": "Up to 24-hour data staleness across departments.", "root_cause": "Legacy point-to-point batch integrations.", "recommended_action": "Expose OpenAPI 3.0 webhooks with retry queues and idempotency keys."}
            ]
        }


def build_contextual_recommendations(ctx: Dict[str, Any]) -> Dict[str, Any]:
    project_name = ctx.get("name", "TransformIQ Solution")
    industry = ctx.get("industry", "Enterprise Services")
    domain = detect_domain(ctx)

    if domain == "HR_RECRUITING":
        return {
            "recommended_solution_name": f"{project_name} — AI Talent & Placement Cloud Suite",
            "tagline": "AI Resume Parsing, Recruiter CRM, Attendance Telemetry & Client Onboarding Hub",
            "executive_summary": "A cloud-native SaaS platform replacing fragmented Excel workbooks with a unified Applicant Tracking System, AI-powered resume extractor, automated client digital onboarding, and recruiter attendance management.",
            "key_capabilities": [
                "AI Resume Parsing & Structured Skill Extraction (<2s per CV)",
                "Multi-Tenant Recruiter CRM & Requisition Pipeline Tracking",
                "Automated Recruiter Attendance & Activity Dashboard",
                "3-Day Digital Client Onboarding & E-Contract Portal",
                "Public Services Showcase Website with Inbound Lead Capture",
                "Automated Candidate Placement Invoicing & SLA Telemetry"
            ],
            "expected_roi": "380% Estimated ROI within 9 months; eliminates 5 Excel workbooks and cuts onboarding from 14 to 3 days.",
            "technology_stack": {
                "Frontend": ["React 18", "TypeScript", "Tailwind CSS", "Lucide Icons", "Vite"],
                "Backend": ["FastAPI", "Python 3.10+", "Pydantic v2", "SQLAlchemy AsyncPG"],
                "AI & NLP": ["Gemini 3.5 Flash Lite / PyPDF2", "Sentence Transformers", "pgvector Semantic Search"],
                "Database & Cache": ["PostgreSQL 16", "Redis 7.2"],
                "DevOps & Security": ["Docker", "Render / Azure Container Apps", "JWT RBAC", "AES-256"]
            },
            "recommendations": [
                {"category": "AI", "title": "Deploy Instant Resume Parsing Engine", "description": "Extract skills, certifications, and past experience automatically from uploaded resumes.", "reason": "Saves 4 hours per recruiter daily from manual spreadsheet typing.", "expected_impact": "HIGH", "feasibility": "HIGH", "priority": "CRITICAL", "confidence_score": 0.96, "source_citation": "HR Requirement REQ-HR-001", "dependencies": ["FastAPI Core", "PostgreSQL Storage"], "status": "AI_GENERATED"},
                {"category": "AUTOMATION", "title": "Implement 3-Day Digital Client Onboarding Flow", "description": "Replace scanned PDFs with online company registration, NDA signing, and requisition creator.", "reason": "Reduces client onboarding latency by 78% and eliminates paper loss.", "expected_impact": "HIGH", "feasibility": "HIGH", "priority": "CRITICAL", "confidence_score": 0.94, "source_citation": "Gap Analysis: Process Dimension", "dependencies": ["Client Portal", "Email Notification Service"], "status": "AI_GENERATED"},
                {"category": "HRMS", "title": "Automate Recruiter Attendance & Telemetry", "description": "Daily digital attendance logging with active candidate submission tracking.", "reason": "Ensures team accountability and provides executive placement visibility.", "expected_impact": "HIGH", "feasibility": "HIGH", "priority": "HIGH", "confidence_score": 0.92, "source_citation": "REQ-HR-003", "dependencies": ["PostgreSQL Schema", "Dashboard UI"], "status": "AI_GENERATED"},
                {"category": "ARCHITECTURE", "title": "Centralized 3NF ATS Database Architecture", "description": "Migrate all Excel data to relational tables with strict candidate deduplication.", "reason": "Eliminates duplicate candidate emails and conflicting outreach.", "expected_impact": "HIGH", "feasibility": "HIGH", "priority": "CRITICAL", "confidence_score": 0.98, "source_citation": "Data Dimension Gap #6", "dependencies": ["PostgreSQL 16 Migration"], "status": "AI_GENERATED"}
            ],
            "alternative_solutions": [
                {"name": "Off-The-Shelf ATS SaaS (Workable / Greenhouse)", "pros": "Quick setup", "cons": "Expensive recurring per-recruiter fee ($18,000/yr) and lacks custom attendance module", "verdict": "Rejected in favor of custom TransformIQ suite for full feature ownership."},
                {"name": "Google Sheets with AppScript Macros", "pros": "Low cost", "cons": "Fails on scale, lacks security/PII encryption, breaks under concurrent 12-recruiter load", "verdict": "Unsuitable for professional scaling."}
            ]
        }
    elif domain == "RETAIL_SUPPLY_CHAIN":
        return {
            "recommended_solution_name": f"{project_name} — Real-Time Omni-Channel Inventory & POS Engine",
            "tagline": "Sub-Second Multi-Warehouse Synchronization, Offline POS & Predictive Replenishment",
            "executive_summary": "A high-throughput, event-driven retail architecture connecting store cash registers, central warehouses, and e-commerce platforms with sub-second inventory accuracy.",
            "key_capabilities": [
                "Sub-Second Real-Time Store & Warehouse Stock Ledger",
                "Offline-First Store POS Engine with Automated Recovery Sync",
                "AI-Driven Predictive Stockout & Restock Replenishment",
                "Mobile Barcode/QR Warehouse Fulfillment & Pick-Pack Scanner",
                "Omni-Channel Click-and-Collect Order Routing",
                "Live Retail Shrinkage & Inventory Velocity Telemetry"
            ],
            "expected_roi": "420% Estimated ROI with $580,000 annual savings from eliminated stockouts and inventory shrinkage.",
            "technology_stack": {
                "Frontend": ["React 18", "TypeScript", "Tailwind CSS", "Vite", "PWA Offline"],
                "Backend": ["FastAPI", "Python 3.10+", "Celery Background Workers", "SQLAlchemy Async"],
                "Event Bus & AI": ["Redis 7.2 Pub/Sub", "Gemini 3.5 Flash Lite", "Scikit-Learn Velocity Model"],
                "Database & Cache": ["PostgreSQL 16", "Redis Cache", "IndexedDB Client Store"],
                "DevOps": ["Docker Swarm", "Kubernetes", "Prometheus Telemetry"]
            },
            "recommendations": [
                {"category": "ARCHITECTURE", "title": "Deploy Event-Driven POS Inventory Bus", "description": "Stream checkout transactions in real time to deduct warehouse stock immediately.", "reason": "Eliminates the 24-hour batch blindness and stops online overselling.", "expected_impact": "HIGH", "feasibility": "HIGH", "priority": "CRITICAL", "confidence_score": 0.97, "source_citation": "REQ-RET-001 & POS Spec", "dependencies": ["Redis Event Bus", "FastAPI Core"], "status": "AI_GENERATED"},
                {"category": "AI", "title": "Deploy Predictive Stockout Replenishment AI", "description": "Forecast store sales velocity and auto-generate warehouse stock transfer orders.", "reason": "Reduces stockouts by 80% without excessive inventory storage costs.", "expected_impact": "HIGH", "feasibility": "HIGH", "priority": "HIGH", "confidence_score": 0.93, "source_citation": "Supply Chain Gap #3", "dependencies": ["Sales History Corpus", "PostgreSQL Storage"], "status": "AI_GENERATED"},
                {"category": "STORE_TECH", "title": "PWA Offline-First Cashier POS Terminal", "description": "Enable full checkout and barcode scanning during network outages with auto-sync.", "reason": "Prevents store checkout downtime and lost in-store revenue.", "expected_impact": "HIGH", "feasibility": "HIGH", "priority": "CRITICAL", "confidence_score": 0.95, "source_citation": "REQ-RET-002", "dependencies": ["IndexedDB Local Store", "Service Workers"], "status": "AI_GENERATED"}
            ],
            "alternative_solutions": [
                {"name": "Monolithic Legacy ERP Upgrade (SAP Retail)", "pros": "Comprehensive", "cons": "18-month implementation and $350k+ licensing overhead", "verdict": "Rejected in favor of modern agile microservices."},
                {"name": "Pure Cloud-Only POS System", "pros": "Simple", "cons": "Fails completely during retail broadband outages", "verdict": "Rejected due to offline survivability requirement."}
            ]
        }
    else:
        return {
            "recommended_solution_name": f"{project_name} — Enterprise Intelligent Transformation Suite",
            "tagline": "Autonomous AI Ingestion, Cognitive Classification, Semantic RAG & Human-in-the-Loop Orchestration",
            "executive_summary": "A cloud-native, AI-first solution that automates 75%+ of operational triage, augments human decision-making with vector knowledge retrieval, and provides executive governance through real-time telemetry.",
            "key_capabilities": [
                "Intelligent Multi-Modal Document & Ticket Ingestion",
                "Zero-Shot NLP Case Classification & Priority Scoring",
                "Semantic RAG Knowledge Engine over SOPs & Guidelines",
                "Human-in-the-Loop Exception & Escalation Hub",
                "Dynamic SLA Monitoring & Real-time Webhook Dispatcher",
                "Executive Transformation & ROI Analytics Dashboard"
            ],
            "expected_roi": "340% Estimated ROI within 12 months with $420,000 net operational savings annually.",
            "technology_stack": {
                "Frontend": ["React 18", "TypeScript", "Tailwind CSS", "React Flow", "Recharts"],
                "Backend": ["FastAPI", "Python 3.10+", "Pydantic v2", "SQLAlchemy 2.0 Async"],
                "AI & ML": ["Gemini 3.5 Flash Lite", "Sentence Transformers", "pgvector RAG"],
                "Database & Cache": ["PostgreSQL 16", "Redis 7.2"],
                "Cloud & DevOps": ["Docker", "Azure Container Apps / Render", "GitHub Actions"]
            },
            "recommendations": [
                {"category": "AI", "title": "Deploy Multi-Class AI Intent & Sentiment Classifier", "description": "Automatically classify incoming customer issues into 14 categories with priority scoring within 250ms of arrival.", "reason": "Eliminates the 4-8 hour manual triage bottleneck and standardizes routing accuracy to >96%.", "expected_impact": "HIGH", "feasibility": "HIGH", "priority": "CRITICAL", "confidence_score": 0.95, "source_citation": "Gap Analysis: Process & AI Dimension", "dependencies": ["Document Context Engine", "REST API Ingestion"], "status": "AI_GENERATED"},
                {"category": "AUTOMATION", "title": "Implement Event-Driven Workflow Automation Engine", "description": "Orchestrate asynchronous ticket routing, automated acknowledgments, and CRM synchronization via webhook pipelines.", "reason": "Removes 65% of repetitive agent data entry and ensures zero dropped tickets.", "expected_impact": "HIGH", "feasibility": "HIGH", "priority": "HIGH", "confidence_score": 0.93, "source_citation": "Requirement REQ-001 & Gap #7", "dependencies": ["Database Schema Migration", "API Gateway"], "status": "AI_GENERATED"},
                {"category": "AI", "title": "Embed SOP Knowledge Base with Semantic RAG", "description": "Vectorize all enterprise SOPs, policies, and historical resolutions to generate instant recommended answers for support staff.", "reason": "Reduces agent research time from 20 minutes to 5 seconds per case.", "expected_impact": "HIGH", "feasibility": "MEDIUM", "priority": "HIGH", "confidence_score": 0.91, "source_citation": "Document Analysis & Gap #4", "dependencies": ["Document Extraction Pipeline", "Vector DB Index"], "status": "AI_GENERATED"},
                {"category": "ARCHITECTURE", "title": "Establish Zero-Trust API-First Integration Layer", "description": "Expose OpenAPI 3.0 compliant endpoints with JWT authentication, role guards, and rate limiting.", "reason": "Enables seamless multi-channel connectivity across web, mobile, and third-party enterprise tools.", "expected_impact": "HIGH", "feasibility": "HIGH", "priority": "CRITICAL", "confidence_score": 0.97, "source_citation": "NFR-003 & Enterprise Security Standards", "dependencies": ["FastAPI Core", "PostgreSQL Storage"], "status": "AI_GENERATED"}
            ],
            "alternative_solutions": [
                {"name": "Commercial Off-The-Shelf (COTS) SaaS Integration", "pros": "Faster initial setup", "cons": "High recurring per-seat licensing ($80k+/yr), limited custom AI flexibility, and vendor lock-in", "verdict": "Rejected in favor of custom TransformIQ blueprint for 60% lower total cost of ownership."},
                {"name": "Pure Rule-Based Automation (No AI)", "pros": "Zero AI API costs", "cons": "Fails on unstructured text, requires continuous manual rule maintenance, cannot adapt to sentiment", "verdict": "Insufficient to resolve core business problem."}
            ]
        }


def build_contextual_architecture(ctx: Dict[str, Any]) -> Dict[str, Any]:
    project_name = ctx.get("name", "TransformIQ Architecture")
    domain = detect_domain(ctx)

    if domain == "HR_RECRUITING":
        return {
            "hld_overview": f"Architecture for {project_name}: Cloud-native modular services with React candidate/client portals, FastAPI ATS core, Gemini AI resume parser, and PostgreSQL 16 database.",
            "deployment_model": "Multi-Tenant Containerized Architecture on Render / Azure Container Apps.",
            "security_boundaries": [
                "Cloudflare SSL Termination & WAF for public client/candidate portal",
                "JWT Token Authentication & Role-Based Access (ADMIN, RECRUITER, CLIENT)",
                "Isolated PostgreSQL tenant schema with AES-256 encrypted resume storage"
            ],
            "data_flow_summary": "Candidate uploads resume -> API Gateway -> AI Resume Parser extracts skills -> Matched against active client job requisitions in PostgreSQL -> Recruiter reviews in ATS -> Client approves candidate via Portal.",
            "components": [
                {"id": "comp-hr-portal", "name": "Recruiter ATS & Client Portal", "layer": "Client", "tech_stack": "React 18, TypeScript, Tailwind CSS, Vite", "description": "Responsive web app for candidate management, interview scheduling, and client onboarding.", "responsibilities": ["Candidate pipeline", "Attendance logging", "Client onboarding forms", "Job board"], "position_x": 50.0, "position_y": 150.0},
                {"id": "comp-hr-gateway", "name": "API Gateway & Auth Guard", "layer": "API_Gateway", "tech_stack": "FastAPI, JWT, RBAC Guard", "description": "Validates user session tokens and routes recruitment API requests.", "responsibilities": ["JWT verification", "Rate limiting", "CORS management"], "position_x": 300.0, "position_y": 150.0},
                {"id": "comp-hr-core", "name": "ATS & Recruitment Service", "layer": "Application_Services", "tech_stack": "Python 3.10, FastAPI, SQLAlchemy Async", "description": "Manages candidate records, job requisitions, recruiter attendance, and placement contracts.", "responsibilities": ["Candidate deduplication", "Attendance tracking", "Client onboarding lifecycle"], "position_x": 550.0, "position_y": 80.0},
                {"id": "comp-hr-ai", "name": "AI Resume Parsing & Matching", "layer": "AI_Engine", "tech_stack": "Gemini 3.5 Flash Lite, Sentence Transformers", "description": "Extracts structured data from PDF/DOCX resumes and calculates candidate-job match score.", "responsibilities": ["Resume text extraction", "Skill ontology mapping", "Semantic profile ranking"], "position_x": 550.0, "position_y": 280.0},
                {"id": "comp-hr-db", "name": "PostgreSQL Relational Storage", "layer": "Data_Storage", "tech_stack": "PostgreSQL 16, pgvector", "description": "Stores candidate profiles, client accounts, recruiter attendance logs, and job openings.", "responsibilities": ["3NF transactional data", "ACID guarantees", "Vector candidate embeddings"], "position_x": 800.0, "position_y": 80.0},
                {"id": "comp-hr-notify", "name": "Email & WhatsApp Notification Dispatcher", "layer": "External_Integrations", "tech_stack": "SendGrid / SMTP, Twilio API", "description": "Sends interview invitations, onboarding notifications, and placement confirmations.", "responsibilities": ["Automated email alerts", "Client notification triggers"], "position_x": 1050.0, "position_y": 180.0}
            ],
            "connections": [
                {"source": "comp-hr-portal", "target": "comp-hr-gateway", "protocol": "HTTPS/REST", "data_payload": "JSON API Payloads", "is_async": False},
                {"source": "comp-hr-gateway", "target": "comp-hr-core", "protocol": "HTTP Async", "data_payload": "Authenticated Context", "is_async": False},
                {"source": "comp-hr-core", "target": "comp-hr-ai", "protocol": "Async HTTP", "data_payload": "Raw Resume Binary / Text", "is_async": True},
                {"source": "comp-hr-core", "target": "comp-hr-db", "protocol": "SQL (AsyncPG)", "data_payload": "Candidates, Clients, Attendance", "is_async": False},
                {"source": "comp-hr-ai", "target": "comp-hr-db", "protocol": "pgvector Insert", "data_payload": "Skill Embeddings", "is_async": False},
                {"source": "comp-hr-core", "target": "comp-hr-notify", "protocol": "REST Webhook", "data_payload": "Interview & Placement Events", "is_async": True}
            ],
            "lld_services": [
                {"name": "CandidateService", "purpose": "Handles candidate creation, resume parsing, and duplicate detection."},
                {"name": "AttendanceService", "purpose": "Tracks daily recruiter check-in/out and compiles productivity metrics."},
                {"name": "ClientOnboardingService", "purpose": "Manages digital client contracts, NDA signatures, and company profiles."},
                {"name": "PlacementService", "purpose": "Coordinates interview stages, offers, and placement fee billing."}
            ]
        }
    elif domain == "RETAIL_SUPPLY_CHAIN":
        return {
            "hld_overview": f"Architecture for {project_name}: High-throughput event-driven microservices architecture connecting retail POS terminals, central warehouses, and e-commerce stores.",
            "deployment_model": "Kubernetes / Docker Swarm with Redis Cluster and Multi-AZ PostgreSQL.",
            "security_boundaries": [
                "mTLS internal service communication between warehouse scanners and API",
                "Store POS tokenized terminal identity certificates",
                "Encrypted inventory and transaction audit ledger in PostgreSQL"
            ],
            "data_flow_summary": "POS checkout scan -> Event Bus publishes stock deduction -> Warehouse inventory ledger updated in <50ms -> If stock falls below threshold, AI replenishment triggers transfer order.",
            "components": [
                {"id": "comp-ret-pos", "name": "Store POS & Mobile Scanners", "layer": "Client", "tech_stack": "React PWA, IndexedDB Offline, Barcode API", "description": "Cashier checkout registers and warehouse barcode picking devices.", "responsibilities": ["Barcode scanning", "Offline transaction queue", "Cashier interface"], "position_x": 50.0, "position_y": 150.0},
                {"id": "comp-ret-gateway", "name": "Retail API Gateway", "layer": "API_Gateway", "tech_stack": "FastAPI, Envoy, Token Auth", "description": "Validates terminal credentials and routes store transactions.", "responsibilities": ["POS authentication", "Rate limiting", "Batch queue sync"], "position_x": 300.0, "position_y": 150.0},
                {"id": "comp-ret-core", "name": "Inventory & Order Engine", "layer": "Application_Services", "tech_stack": "Python 3.10, FastAPI, Celery", "description": "Manages multi-warehouse stock counts, stock transfers, and omni-channel order routing.", "responsibilities": ["Real-time inventory locks", "Stock transfer workflows", "Omni order fulfillment"], "position_x": 550.0, "position_y": 80.0},
                {"id": "comp-ret-event", "name": "Event Bus & Redis Cache", "layer": "Data_Storage", "tech_stack": "Redis 7.2 Pub/Sub, Streams", "description": "Sub-millisecond event streamer broadcasting stock deductions to all channels.", "responsibilities": ["Real-time stock broadcast", "Lock management", "Pub/Sub dispatch"], "position_x": 550.0, "position_y": 280.0},
                {"id": "comp-ret-db", "name": "Master PostgreSQL Inventory Ledger", "layer": "Data_Storage", "tech_stack": "PostgreSQL 16, TimescaleDB / Audit", "description": "Stores inventory items, warehouses, store terminals, orders, and transfer logs.", "responsibilities": ["ACID transaction logging", "Pessimistic locking", "Stock history"], "position_x": 800.0, "position_y": 80.0},
                {"id": "comp-ret-ai", "name": "Predictive Replenishment AI", "layer": "AI_Engine", "tech_stack": "Gemini 3.5 Flash Lite / ML Forecast", "description": "Analyzes sales velocity and triggers automated stock replenishment.", "responsibilities": ["Demand prediction", "Automated purchase order generation"], "position_x": 1050.0, "position_y": 180.0}
            ],
            "connections": [
                {"source": "comp-ret-pos", "target": "comp-ret-gateway", "protocol": "WebSocket / HTTPS", "data_payload": "POS Transaction Event", "is_async": False},
                {"source": "comp-ret-gateway", "target": "comp-ret-core", "protocol": "gRPC / HTTP", "data_payload": "Validated Transaction", "is_async": False},
                {"source": "comp-ret-core", "target": "comp-ret-event", "protocol": "Redis Stream", "data_payload": "Stock Deduct Event", "is_async": True},
                {"source": "comp-ret-core", "target": "comp-ret-db", "protocol": "SQL (AsyncPG)", "data_payload": "Inventory Items & Orders", "is_async": False},
                {"source": "comp-ret-event", "target": "comp-ret-ai", "protocol": "Event Hook", "data_payload": "Velocity Signals", "is_async": True}
            ],
            "lld_services": [
                {"name": "InventoryLedgerService", "purpose": "Maintains sub-second accurate multi-warehouse stock levels with lock guards."},
                {"name": "POSSyncService", "purpose": "Handles offline store queue sync and batch reconciliation."},
                {"name": "TransferOrderService", "purpose": "Orchestrates inter-warehouse stock transfers and pick-pack-ship states."},
                {"name": "ReplenishmentService", "purpose": "Executes predictive restock algorithms and supplier purchase orders."}
            ]
        }
    else:
        return {
            "hld_overview": f"High-Level Architecture for {project_name}: Event-driven microservices pattern with API Gateway, FastAPI core, asynchronous AI inference, and PostgreSQL storage.",
            "deployment_model": "Multi-Zone Kubernetes / Docker Swarm with Azure Container Apps or AWS ECS.",
            "security_boundaries": [
                "Public Ingress protected by Cloudflare WAF & TLS 1.3 Termination",
                "API Gateway with JWT validation and Rate Limiting per tenant",
                "Internal Service Mesh with mTLS and network isolation",
                "Database and Storage encrypted with customer-managed keys (KMS)"
            ],
            "data_flow_summary": "Inbound request -> API Gateway -> Auth check -> AI Engine Classifier -> Vector SOP Search -> PostgreSQL -> Webhook notification.",
            "components": [
                {"id": "comp-client", "name": "Web & Mobile Clients", "layer": "Client", "tech_stack": "React 18, TypeScript, Tailwind CSS, Vite", "description": "Responsive SPA providing executive dashboards, discovery chat, and visual design tools.", "responsibilities": ["User interaction", "State management", "React Flow diagrams", "Real-time updates"], "position_x": 50.0, "position_y": 150.0},
                {"id": "comp-gateway", "name": "API Gateway & Auth", "layer": "API_Gateway", "tech_stack": "FastAPI, JWT, RBAC Guard", "description": "Single entry point handling SSL termination, rate limiting, and tenant token validation.", "responsibilities": ["Authentication", "CORS policy", "Tenant routing", "Request logging"], "position_x": 300.0, "position_y": 150.0},
                {"id": "comp-core-service", "name": "Transformation Core Service", "layer": "Application_Services", "tech_stack": "Python 3.10, FastAPI, SQLAlchemy 2.0 Async", "description": "Orchestrates project state, business analysis, gap detection, and blueprint generation.", "responsibilities": ["Project lifecycle", "State synchronization", "Business logic", "Export generation"], "position_x": 550.0, "position_y": 80.0},
                {"id": "comp-ai-engine", "name": "AI Intelligence Engine", "layer": "AI_Engine", "tech_stack": "Gemini 3.5 Flash Lite, LangChain, RAG", "description": "Executes domain classification, sentiment scoring, and multi-agent reasoning.", "responsibilities": ["Text classification", "Contextual RAG", "Structured schema validation", "Explainability"], "position_x": 550.0, "position_y": 280.0},
                {"id": "comp-db", "name": "Relational Storage (PostgreSQL)", "layer": "Data_Storage", "tech_stack": "PostgreSQL 16, pgvector, SQLAlchemy", "description": "Stores tenants, projects, models, schemas, audit logs, and vector embeddings.", "responsibilities": ["ACID transactions", "Multi-tenancy isolation", "Vector similarity search", "Audit history"], "position_x": 800.0, "position_y": 80.0},
                {"id": "comp-cache", "name": "Cache & Event Bus", "layer": "Data_Storage", "tech_stack": "Redis 7.2 / RabbitMQ", "description": "Caches session data and delivers asynchronous event notifications.", "responsibilities": ["Response caching", "Job queues", "Real-time pub/sub"], "position_x": 800.0, "position_y": 280.0},
                {"id": "comp-integrations", "name": "Enterprise Integrations", "layer": "External_Integrations", "tech_stack": "REST Webhooks, ERP/CRM Connectors", "description": "Connects seamlessly with external ticketing, CRM, and corporate email servers.", "responsibilities": ["Outbound webhooks", "Email dispatch", "ERP synchronization"], "position_x": 1050.0, "position_y": 180.0}
            ],
            "connections": [
                {"source": "comp-client", "target": "comp-gateway", "protocol": "HTTPS/REST", "data_payload": "JSON API Payloads", "is_async": False},
                {"source": "comp-gateway", "target": "comp-core-service", "protocol": "gRPC / HTTP", "data_payload": "Authenticated Context", "is_async": False},
                {"source": "comp-core-service", "target": "comp-ai-engine", "protocol": "Async HTTP", "data_payload": "Prompt & RAG Chunks", "is_async": True},
                {"source": "comp-core-service", "target": "comp-db", "protocol": "SQL (AsyncPG)", "data_payload": "Entities & Blueprints", "is_async": False},
                {"source": "comp-ai-engine", "target": "comp-db", "protocol": "pgvector Query", "data_payload": "Cosine Embeddings", "is_async": False},
                {"source": "comp-core-service", "target": "comp-cache", "protocol": "Redis Protocol", "data_payload": "Session & Token State", "is_async": True},
                {"source": "comp-core-service", "target": "comp-integrations", "protocol": "REST Webhook", "data_payload": "Resolved Events", "is_async": True}
            ],
            "lld_services": [
                {"name": "AuthService", "purpose": "Handles JWT authentication, password hashing, and role checks."},
                {"name": "ContextService", "purpose": "Extracts and indexes document text into searchable project context."},
                {"name": "AIOrchestratorService", "purpose": "Dispatches tasks to specialized agents with JSON schema validation."},
                {"name": "ExportService", "purpose": "Generates production-grade PDF, DOCX, XLSX, and PPTX reports."}
            ]
        }


def build_contextual_process_workflow(ctx: Dict[str, Any]) -> Dict[str, Any]:
    project_name = ctx.get("name", "Process Workflow")
    domain = detect_domain(ctx)

    if domain == "HR_RECRUITING":
        return {
            "process_name": "Autonomous Candidate Ingestion, Matching & Placement Workflow",
            "process_summary": "End-to-end BPMN workflow covering candidate resume upload, AI skill extraction, automated job matching, client review, and digitized placement onboarding.",
            "cycle_time_current": "14 Days (Manual Spreadsheets & Paperwork)",
            "cycle_time_projected": "3 Days (AI-Powered Platform)",
            "efficiency_gain": "78.5% Cycle Time Reduction",
            "swimlanes": ["Candidate / Applicant", "AI Resume & Matching Engine", "Internal Recruiter", "Enterprise Client Company"],
            "nodes": [
                {"id": "node-hr-1", "node_key": "START_APPLY", "node_type": "start", "label": "Candidate Submits Resume", "description": "Candidate uploads CV via web portal or email.", "actor": "Candidate / Applicant", "system": "Public Career Portal", "input_data": "Resume PDF / DOCX", "output_data": "Raw resume document", "swimlane": "Candidate / Applicant", "position_x": 50.0, "position_y": 100.0},
                {"id": "node-hr-2", "node_key": "AI_PARSE", "node_type": "ai_task", "label": "AI Resume Parsing & OCR", "description": "Extract contact info, skills, education, and years of experience into structured profile.", "actor": "AI Resume & Matching Engine", "system": "Gemini 3.5 Flash Lite Parser", "input_data": "Raw resume document", "output_data": "Structured Candidate JSON", "swimlane": "AI Resume & Matching Engine", "position_x": 260.0, "position_y": 100.0},
                {"id": "node-hr-3", "node_key": "AI_MATCH", "node_type": "ai_task", "label": "Semantic Match Against Open Jobs", "description": "Compute similarity score between candidate skills and active client job openings.", "actor": "AI Resume & Matching Engine", "system": "pgvector Semantic Matcher", "input_data": "Structured Candidate JSON", "output_data": "Top 3 Matched Requisitions & Match %", "swimlane": "AI Resume & Matching Engine", "position_x": 480.0, "position_y": 100.0},
                {"id": "node-hr-4", "node_key": "RECRUITER_SCREEN", "node_type": "human_review", "label": "Recruiter Phone Screen & Validation", "description": "Assigned recruiter conducts 15-minute phone screening and logs attendance/notes.", "actor": "Internal Recruiter", "system": "ATS Recruiter Hub", "input_data": "Matched candidate profile", "output_data": "Screening Status: SHORTLISTED / REJECTED", "swimlane": "Internal Recruiter", "position_x": 700.0, "position_y": 280.0},
                {"id": "node-hr-5", "node_key": "CLIENT_REVIEW", "node_type": "decision", "label": "Client Interview & Offer Decision", "description": "Client reviews shortlisted profile in portal and conducts final technical interview.", "actor": "Enterprise Client Company", "system": "Client Onboarding Portal", "input_data": "Shortlisted candidate profile", "output_data": "Offer Extended / Next Candidate", "swimlane": "Enterprise Client Company", "position_x": 940.0, "position_y": 420.0},
                {"id": "node-hr-6", "node_key": "DIGITAL_ONBOARD", "node_type": "task", "label": "Digital Contract & Placement Finalized", "description": "Auto-generate offer agreement, NDA, and automated recruiter placement commission.", "actor": "Internal Recruiter", "system": "Contract & Invoicing Engine", "input_data": "Accepted offer details", "output_data": "Active Placement Record & Invoice", "swimlane": "Internal Recruiter", "position_x": 1160.0, "position_y": 280.0},
                {"id": "node-hr-7", "node_key": "END_HIRED", "node_type": "end", "label": "Candidate Placed Successfully", "description": "Candidate onboarded at client and telemetry logged into executive dashboard.", "actor": "AI Resume & Matching Engine", "system": "Analytics Dashboard", "input_data": "Placement record", "output_data": "Closed Requisition & Placement Metric", "swimlane": "AI Resume & Matching Engine", "position_x": 1380.0, "position_y": 100.0}
            ],
            "edges": [
                {"source": "node-hr-1", "target": "node-hr-2", "label": "Upload Event"},
                {"source": "node-hr-2", "target": "node-hr-3", "label": "Parsed Profile"},
                {"source": "node-hr-3", "target": "node-hr-4", "label": "Matched Jobs"},
                {"source": "node-hr-4", "target": "node-hr-5", "label": "Shortlisted CVs"},
                {"source": "node-hr-5", "target": "node-hr-6", "label": "Offer Accepted"},
                {"source": "node-hr-6", "target": "node-hr-7", "label": "Placement Done"}
            ]
        }
    elif domain == "RETAIL_SUPPLY_CHAIN":
        return {
            "process_name": "Real-Time Omni-Channel Inventory Sync & Restock Workflow",
            "process_summary": "BPMN process from in-store POS checkout or online order placement to sub-second warehouse inventory lock and predictive stock replenishment.",
            "cycle_time_current": "24 Hours (Nightly Batch)",
            "cycle_time_projected": "150 Milliseconds (Live Event Stream)",
            "efficiency_gain": "99.8% Cycle Time Reduction",
            "swimlanes": ["Retail Store Shopper / Cashier", "Store POS Terminal (Local)", "TransformIQ Real-Time Inventory Engine", "Central Warehouse Logistics"],
            "nodes": [
                {"id": "node-ret-1", "node_key": "START_SCAN", "node_type": "start", "label": "Barcode Scanned at Checkout", "description": "Cashier scans item barcode or online customer clicks Buy Now.", "actor": "Retail Store Shopper / Cashier", "system": "POS Barcode Scanner / Web", "input_data": "Item SKU & Quantity", "output_data": "Checkout transaction request", "swimlane": "Retail Store Shopper / Cashier", "position_x": 50.0, "position_y": 100.0},
                {"id": "node-ret-2", "node_key": "POS_AUTH", "node_type": "task", "label": "Local POS Check & Offline Buffer", "description": "Verify local terminal cash register buffer and process payment.", "actor": "Store POS Terminal (Local)", "system": "Local PWA POS Engine", "input_data": "Checkout transaction request", "output_data": "Paid Transaction Payload", "swimlane": "Store POS Terminal (Local)", "position_x": 260.0, "position_y": 280.0},
                {"id": "node-ret-3", "node_key": "EVENT_DEDUCT", "node_type": "ai_task", "label": "Sub-Second Stock Deduction & Lock", "description": "Broadcast Redis event to deduct inventory count across all store/online channels.", "actor": "TransformIQ Real-Time Inventory Engine", "system": "FastAPI + Redis Event Bus", "input_data": "Paid Transaction Payload", "output_data": "Updated Inventory Balance", "swimlane": "TransformIQ Real-Time Inventory Engine", "position_x": 480.0, "position_y": 100.0},
                {"id": "node-ret-4", "node_key": "STOCK_CHECK", "node_type": "decision", "label": "Stock Below Reorder Level?", "description": "Check if current SKU count is below predictive safety buffer threshold.", "actor": "TransformIQ Real-Time Inventory Engine", "system": "Predictive Restock Engine", "input_data": "Updated Inventory Balance", "output_data": "Branch: YES (Restock) / NO (Normal)", "swimlane": "TransformIQ Real-Time Inventory Engine", "position_x": 700.0, "position_y": 100.0},
                {"id": "node-ret-5", "node_key": "WAREHOUSE_PICK", "node_type": "task", "label": "Generate Warehouse Transfer & Pick Route", "description": "Generate digital pick list for warehouse workers to replenish store shelves.", "actor": "Central Warehouse Logistics", "system": "Mobile Scanner WMS", "input_data": "Automated Stock Transfer Order", "output_data": "Items Picked, Packed & Dispatched", "swimlane": "Central Warehouse Logistics", "position_x": 940.0, "position_y": 420.0},
                {"id": "node-ret-6", "node_key": "END_SYNCED", "node_type": "end", "label": "Inventory Reconciled & Logged", "description": "Stock balance synchronized across all enterprise ledgers.", "actor": "TransformIQ Real-Time Inventory Engine", "system": "PostgreSQL Inventory Ledger", "input_data": "Dispatch confirmation", "output_data": "100% Reconciled Stock State", "swimlane": "TransformIQ Real-Time Inventory Engine", "position_x": 1160.0, "position_y": 100.0}
            ],
            "edges": [
                {"source": "node-ret-1", "target": "node-ret-2", "label": "Scan Event"},
                {"source": "node-ret-2", "target": "node-ret-3", "label": "Publish Transaction"},
                {"source": "node-ret-3", "target": "node-ret-4", "label": "Evaluated Balance"},
                {"source": "node-ret-4", "target": "node-ret-5", "label": "Yes (Below Threshold)"},
                {"source": "node-ret-4", "target": "node-ret-6", "label": "No (Adequate Stock)"},
                {"source": "node-ret-5", "target": "node-ret-6", "label": "Restocked"}
            ]
        }
    else:
        return {
            "process_name": "Autonomous Intelligent Triage & Resolution Workflow",
            "process_summary": "End-to-end BPMN-compliant operational process featuring automated ingestion, AI intent analysis, smart routing, and human-in-the-loop governance.",
            "cycle_time_current": "48 Hours (Manual)",
            "cycle_time_projected": "12 Minutes (AI-Powered)",
            "efficiency_gain": "87.5% Cycle Time Reduction",
            "swimlanes": ["Customer / User", "TransformIQ AI Engine", "Enterprise Systems", "Operations Specialist"],
            "nodes": [
                {"id": "node-1", "node_key": "START_EVENT", "node_type": "start", "label": "Inbound Case Arrives", "description": "Customer submits issue via Email, Web Portal, or Mobile App.", "actor": "Customer / User", "system": "Web Portal / Mail Server", "input_data": "Raw ticket payload & attachments", "output_data": "Standardized JSON event", "swimlane": "Customer / User", "position_x": 50.0, "position_y": 100.0},
                {"id": "node-2", "node_key": "AI_INGEST", "node_type": "ai_task", "label": "AI Text Extraction & Ingestion", "description": "Extract text from body and attachments (PDF, DOCX, Images).", "actor": "TransformIQ AI Engine", "system": "Document Parser & OCR", "input_data": "Standardized JSON event", "output_data": "Normalized clean text corpus", "swimlane": "TransformIQ AI Engine", "position_x": 260.0, "position_y": 100.0},
                {"id": "node-3", "node_key": "AI_CLASSIFY", "node_type": "ai_task", "label": "Classification & Sentiment Scoring", "description": "Classify intent category, urgency level, and extract key entities.", "actor": "TransformIQ AI Engine", "system": "Transformer Classifier", "input_data": "Normalized clean text corpus", "output_data": "Category tag, Sentiment (-1.0 to 1.0), Urgency score", "swimlane": "TransformIQ AI Engine", "position_x": 480.0, "position_y": 100.0},
                {"id": "node-4", "node_key": "DECISION_CONFIDENCE", "node_type": "decision", "label": "AI Confidence > 85%?", "description": "Verify whether prediction confidence satisfies automated threshold.", "actor": "TransformIQ AI Engine", "system": "Rules Engine", "input_data": "Confidence metric", "output_data": "Branch: YES (Auto-Route) / NO (Human Review)", "swimlane": "TransformIQ AI Engine", "position_x": 700.0, "position_y": 100.0},
                {"id": "node-5", "node_key": "HUMAN_REVIEW", "node_type": "human_review", "label": "Specialist Review & Override", "description": "Operations specialist inspects flagged case, validates tags, or overrides suggestion.", "actor": "Operations Specialist", "system": "TransformIQ Review Hub", "input_data": "Flagged case with AI suggested tags", "output_data": "Approved routing metadata", "swimlane": "Operations Specialist", "position_x": 700.0, "position_y": 280.0},
                {"id": "node-6", "node_key": "AUTO_ROUTE", "node_type": "task", "label": "Dispatch to Target Department CRM", "description": "Publish event to department queue and trigger SLA timer countdown.", "actor": "Enterprise Systems", "system": "CRM / ERP API", "input_data": "Approved routing metadata", "output_data": "Assigned Ticket ID & SLA Timer", "swimlane": "Enterprise Systems", "position_x": 940.0, "position_y": 100.0},
                {"id": "node-7", "node_key": "RAG_DRAFT", "node_type": "ai_task", "label": "Generate RAG Suggested Resolution", "description": "Retrieve matching SOP sections and draft personalized customer response.", "actor": "TransformIQ AI Engine", "system": "Semantic RAG Engine", "input_data": "Case history + Vector DB Context", "output_data": "Pre-filled resolution draft", "swimlane": "TransformIQ AI Engine", "position_x": 1160.0, "position_y": 100.0},
                {"id": "node-8", "node_key": "END_EVENT", "node_type": "end", "label": "Case Resolved & Telemetry Logged", "description": "Notify customer, update ERP records, and log telemetry into analytics.", "actor": "Enterprise Systems", "system": "Customer Portal & Analytics DB", "input_data": "Resolution payload", "output_data": "Closed Ticket Status & KPI Metrics", "swimlane": "Enterprise Systems", "position_x": 1380.0, "position_y": 100.0}
            ],
            "edges": [
                {"source": "node-1", "target": "node-2", "label": "HTTP Post"},
                {"source": "node-2", "target": "node-3", "label": "Clean Text"},
                {"source": "node-3", "target": "node-4", "label": "Evaluated"},
                {"source": "node-4", "target": "node-6", "label": "Yes (>85%)", "condition": "confidence >= 0.85"},
                {"source": "node-4", "target": "node-5", "label": "No (<85%)", "condition": "confidence < 0.85"},
                {"source": "node-5", "target": "node-6", "label": "Approved"},
                {"source": "node-6", "target": "node-7", "label": "Enriched"},
                {"source": "node-7", "target": "node-8", "label": "Dispatched"}
            ]
        }


def build_contextual_database(ctx: Dict[str, Any]) -> Dict[str, Any]:
    project_name = ctx.get("name", "Database Schema")
    domain = detect_domain(ctx)

    if domain == "HR_RECRUITING":
        return {
            "overview": f"Normalized 3NF Relational Data Model for {project_name} in PostgreSQL. Covers candidate records, resume skills, client companies, job requisitions, placements, and recruiter attendance.",
            "entities": [
                {
                    "name": "candidates",
                    "description": "Central candidate profiles with parsed skills, experience, and contact data.",
                    "fields": [
                        {"name": "id", "type": "VARCHAR(36)", "is_primary": True, "is_foreign": False, "is_nullable": False, "description": "UUID Primary Key"},
                        {"name": "full_name", "type": "VARCHAR(255)", "is_primary": False, "is_foreign": False, "is_nullable": False, "description": "Candidate name"},
                        {"name": "email", "type": "VARCHAR(255)", "is_primary": False, "is_foreign": False, "is_nullable": False, "description": "Unique email"},
                        {"name": "phone", "type": "VARCHAR(50)", "is_primary": False, "is_foreign": False, "is_nullable": True, "description": "Contact phone"},
                        {"name": "primary_skills", "type": "TEXT", "is_primary": False, "is_foreign": False, "is_nullable": True, "description": "Extracted key skills (JSON/CSV)"},
                        {"name": "years_experience", "type": "NUMERIC(4,1)", "is_primary": False, "is_foreign": False, "is_nullable": True, "description": "Total professional experience"},
                        {"name": "resume_file_url", "type": "VARCHAR(500)", "is_primary": False, "is_foreign": False, "is_nullable": True, "description": "Encrypted S3 bucket document URL"},
                        {"name": "status", "type": "VARCHAR(50)", "is_primary": False, "is_foreign": False, "is_nullable": False, "description": "ACTIVE, SCREENING, INTERVIEWING, PLACED"}
                    ],
                    "relationships": [{"target": "candidate_placements", "type": "ONE_TO_MANY"}],
                    "indexes": ["idx_candidate_email", "idx_candidate_status"]
                },
                {
                    "name": "client_companies",
                    "description": "Enterprise client accounts managing job requisitions and hiring agreements.",
                    "fields": [
                        {"name": "id", "type": "VARCHAR(36)", "is_primary": True, "is_foreign": False, "is_nullable": False, "description": "UUID Primary Key"},
                        {"name": "company_name", "type": "VARCHAR(255)", "is_primary": False, "is_foreign": False, "is_nullable": False, "description": "Corporate client name"},
                        {"name": "industry", "type": "VARCHAR(100)", "is_primary": False, "is_foreign": False, "is_nullable": True, "description": "Industry domain"},
                        {"name": "onboarding_status", "type": "VARCHAR(50)", "is_primary": False, "is_foreign": False, "is_nullable": False, "description": "PENDING_NDA, ACTIVE, SUSPENDED"},
                        {"name": "contact_person", "type": "VARCHAR(255)", "is_primary": False, "is_foreign": False, "is_nullable": True, "description": "Primary HR contact name"},
                        {"name": "created_at", "type": "TIMESTAMP", "is_primary": False, "is_foreign": False, "is_nullable": False, "description": "Onboarding timestamp"}
                    ],
                    "relationships": [{"target": "job_openings", "type": "ONE_TO_MANY"}],
                    "indexes": ["idx_client_name", "idx_client_status"]
                },
                {
                    "name": "job_openings",
                    "description": "Active job requisitions submitted by client companies.",
                    "fields": [
                        {"name": "id", "type": "VARCHAR(36)", "is_primary": True, "is_foreign": False, "is_nullable": False, "description": "UUID Primary Key"},
                        {"name": "client_company_id", "type": "VARCHAR(36)", "is_primary": False, "is_foreign": True, "is_nullable": False, "description": "FK to client_companies"},
                        {"name": "job_title", "type": "VARCHAR(255)", "is_primary": False, "is_foreign": False, "is_nullable": False, "description": "Position title"},
                        {"name": "target_experience_years", "type": "INT", "is_primary": False, "is_foreign": False, "is_nullable": True, "description": "Required years"},
                        {"name": "budget_max_salary", "type": "NUMERIC(12,2)", "is_primary": False, "is_foreign": False, "is_nullable": True, "description": "Maximum offered compensation"},
                        {"name": "status", "type": "VARCHAR(50)", "is_primary": False, "is_foreign": False, "is_nullable": False, "description": "OPEN, INTERVIEWING, FULFILLED, CLOSED"}
                    ],
                    "relationships": [{"target": "client_companies", "type": "MANY_TO_ONE"}, {"target": "candidate_placements", "type": "ONE_TO_MANY"}],
                    "indexes": ["idx_job_client", "idx_job_status"]
                },
                {
                    "name": "recruiter_attendance",
                    "description": "Daily attendance logs and activity telemetry for the internal recruitment team.",
                    "fields": [
                        {"name": "id", "type": "VARCHAR(36)", "is_primary": True, "is_foreign": False, "is_nullable": False, "description": "UUID Primary Key"},
                        {"name": "recruiter_user_id", "type": "VARCHAR(36)", "is_primary": False, "is_foreign": False, "is_nullable": False, "description": "User ID of recruiter"},
                        {"name": "date", "type": "DATE", "is_primary": False, "is_foreign": False, "is_nullable": False, "description": "Attendance log date"},
                        {"name": "check_in_time", "type": "TIMESTAMP", "is_primary": False, "is_foreign": False, "is_nullable": True, "description": "Morning login timestamp"},
                        {"name": "check_out_time", "type": "TIMESTAMP", "is_primary": False, "is_foreign": False, "is_nullable": True, "description": "Evening logout timestamp"},
                        {"name": "resumes_screened_count", "type": "INT", "is_primary": False, "is_foreign": False, "is_nullable": False, "description": "Daily screened CV count"},
                        {"name": "interviews_scheduled_count", "type": "INT", "is_primary": False, "is_foreign": False, "is_nullable": False, "description": "Daily scheduled interview count"}
                    ],
                    "relationships": [],
                    "indexes": ["idx_recruiter_date"]
                }
            ],
            "sql_ddl": """-- Aarav HR Consultancy Schema DDL
CREATE TABLE client_companies (
    id VARCHAR(36) PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    industry VARCHAR(100),
    onboarding_status VARCHAR(50) DEFAULT 'ACTIVE',
    contact_person VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE candidates (
    id VARCHAR(36) PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    primary_skills TEXT,
    years_experience NUMERIC(4,1),
    resume_file_url VARCHAR(500),
    status VARCHAR(50) DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE job_openings (
    id VARCHAR(36) PRIMARY KEY,
    client_company_id VARCHAR(36) REFERENCES client_companies(id) ON DELETE CASCADE,
    job_title VARCHAR(255) NOT NULL,
    target_experience_years INT,
    budget_max_salary NUMERIC(12,2),
    status VARCHAR(50) DEFAULT 'OPEN'
);

CREATE TABLE recruiter_attendance (
    id VARCHAR(36) PRIMARY KEY,
    recruiter_user_id VARCHAR(36) NOT NULL,
    date DATE NOT NULL,
    check_in_time TIMESTAMP,
    check_out_time TIMESTAMP,
    resumes_screened_count INT DEFAULT 0,
    interviews_scheduled_count INT DEFAULT 0
);
"""
        }
    elif domain == "RETAIL_SUPPLY_CHAIN":
        return {
            "overview": f"Multi-Warehouse Inventory & POS Transaction Relational Schema for {project_name} in PostgreSQL with optimistic concurrency guards and sub-millisecond stock indexes.",
            "entities": [
                {
                    "name": "inventory_items",
                    "description": "Master SKU catalog tracking real-time stock balances across all locations.",
                    "fields": [
                        {"name": "id", "type": "VARCHAR(36)", "is_primary": True, "is_foreign": False, "is_nullable": False, "description": "UUID Primary Key"},
                        {"name": "sku_code", "type": "VARCHAR(100)", "is_primary": False, "is_foreign": False, "is_nullable": False, "description": "Unique SKU barcode"},
                        {"name": "item_name", "type": "VARCHAR(255)", "is_primary": False, "is_foreign": False, "is_nullable": False, "description": "Product display title"},
                        {"name": "category", "type": "VARCHAR(100)", "is_primary": False, "is_foreign": False, "is_nullable": True, "description": "Merchandise category"},
                        {"name": "unit_price", "type": "NUMERIC(10,2)", "is_primary": False, "is_foreign": False, "is_nullable": False, "description": "Retail selling price"},
                        {"name": "reorder_point", "type": "INT", "is_primary": False, "is_foreign": False, "is_nullable": False, "description": "Safety stock threshold for AI restock"},
                        {"name": "total_available_stock", "type": "INT", "is_primary": False, "is_foreign": False, "is_nullable": False, "description": "Global aggregated inventory"}
                    ],
                    "relationships": [{"target": "stock_locations", "type": "ONE_TO_MANY"}],
                    "indexes": ["idx_sku_code", "idx_item_category"]
                },
                {
                    "name": "warehouses_stores",
                    "description": "Physical distribution hubs and retail store locations.",
                    "fields": [
                        {"name": "id", "type": "VARCHAR(36)", "is_primary": True, "is_foreign": False, "is_nullable": False, "description": "UUID Primary Key"},
                        {"name": "location_name", "type": "VARCHAR(255)", "is_primary": False, "is_foreign": False, "is_nullable": False, "description": "Store or DC Name"},
                        {"name": "location_type", "type": "VARCHAR(50)", "is_primary": False, "is_foreign": False, "is_nullable": False, "description": "CENTRAL_DC, RETAIL_STORE, FULFILLMENT_HUB"},
                        {"name": "city", "type": "VARCHAR(100)", "is_primary": False, "is_foreign": False, "is_nullable": True, "description": "City location"}
                    ],
                    "relationships": [{"target": "stock_locations", "type": "ONE_TO_MANY"}],
                    "indexes": ["idx_loc_type"]
                },
                {
                    "name": "store_pos_terminals",
                    "description": "Registered point-of-sale cash registers capable of offline transactions.",
                    "fields": [
                        {"name": "id", "type": "VARCHAR(36)", "is_primary": True, "is_foreign": False, "is_nullable": False, "description": "UUID Primary Key"},
                        {"name": "store_location_id", "type": "VARCHAR(36)", "is_primary": False, "is_foreign": True, "is_nullable": False, "description": "FK to warehouses_stores"},
                        {"name": "terminal_code", "type": "VARCHAR(50)", "is_primary": False, "is_foreign": False, "is_nullable": False, "description": "POS-01, POS-02"},
                        {"name": "last_sync_timestamp", "type": "TIMESTAMP", "is_primary": False, "is_foreign": False, "is_nullable": True, "description": "Last successful sync time"},
                        {"name": "status", "type": "VARCHAR(50)", "is_primary": False, "is_foreign": False, "is_nullable": False, "description": "ONLINE, OFFLINE_SYNCING"}
                    ],
                    "relationships": [{"target": "warehouses_stores", "type": "MANY_TO_ONE"}],
                    "indexes": ["idx_pos_store"]
                }
            ],
            "sql_ddl": """-- Global Omni-Channel Retail Schema DDL
CREATE TABLE warehouses_stores (
    id VARCHAR(36) PRIMARY KEY,
    location_name VARCHAR(255) NOT NULL,
    location_type VARCHAR(50) NOT NULL,
    city VARCHAR(100)
);

CREATE TABLE inventory_items (
    id VARCHAR(36) PRIMARY KEY,
    sku_code VARCHAR(100) UNIQUE NOT NULL,
    item_name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    unit_price NUMERIC(10,2) NOT NULL,
    reorder_point INT DEFAULT 50,
    total_available_stock INT DEFAULT 0
);

CREATE TABLE store_pos_terminals (
    id VARCHAR(36) PRIMARY KEY,
    store_location_id VARCHAR(36) REFERENCES warehouses_stores(id) ON DELETE CASCADE,
    terminal_code VARCHAR(50) NOT NULL,
    last_sync_timestamp TIMESTAMP,
    status VARCHAR(50) DEFAULT 'ONLINE'
);
"""
        }
    else:
        return {
            "overview": "Normalized 3NF relational data model engineered in PostgreSQL with index optimization and support for pgvector embeddings.",
            "entities": [
                {
                    "name": "tenants_organizations",
                    "description": "Multi-tenant organization boundary providing strict data isolation.",
                    "fields": [
                        {"name": "id", "type": "VARCHAR(36)", "is_primary": True, "is_foreign": False, "is_nullable": False, "description": "UUID Primary Key"},
                        {"name": "name", "type": "VARCHAR(255)", "is_primary": False, "is_foreign": False, "is_nullable": False, "description": "Enterprise Organization Name"},
                        {"name": "industry", "type": "VARCHAR(100)", "is_primary": False, "is_foreign": False, "is_nullable": True, "description": "Industry vertical"},
                        {"name": "created_at", "type": "TIMESTAMP", "is_primary": False, "is_foreign": False, "is_nullable": False, "description": "Record creation timestamp"}
                    ],
                    "relationships": [{"target": "projects", "type": "ONE_TO_MANY"}],
                    "indexes": ["idx_org_name"]
                },
                {
                    "name": "case_records",
                    "description": "Inbound transactions, tickets, or claims undergoing AI processing.",
                    "fields": [
                        {"name": "id", "type": "VARCHAR(36)", "is_primary": True, "is_foreign": False, "is_nullable": False, "description": "UUID Primary Key"},
                        {"name": "project_id", "type": "VARCHAR(36)", "is_primary": False, "is_foreign": True, "is_nullable": False, "description": "FK to projects"},
                        {"name": "title", "type": "VARCHAR(255)", "is_primary": False, "is_foreign": False, "is_nullable": False, "description": "Case subject or summary"},
                        {"name": "category", "type": "VARCHAR(100)", "is_primary": False, "is_foreign": False, "is_nullable": True, "description": "AI classified category"},
                        {"name": "sentiment_score", "type": "FLOAT", "is_primary": False, "is_foreign": False, "is_nullable": True, "description": "Sentiment metric (-1.0 to 1.0)"},
                        {"name": "urgency_level", "type": "VARCHAR(50)", "is_primary": False, "is_foreign": False, "is_nullable": False, "description": "CRITICAL, HIGH, MEDIUM, LOW"},
                        {"name": "confidence", "type": "FLOAT", "is_primary": False, "is_foreign": False, "is_nullable": False, "description": "AI model confidence score"},
                        {"name": "status", "type": "VARCHAR(50)", "is_primary": False, "is_foreign": False, "is_nullable": False, "description": "QUEUED, ROUTED, REVIEW, RESOLVED"}
                    ],
                    "relationships": [{"target": "projects", "type": "MANY_TO_ONE"}],
                    "indexes": ["idx_case_proj", "idx_case_urgency", "idx_case_status"]
                }
            ],
            "sql_ddl": """-- TransformIQ Schema DDL
CREATE TABLE case_records (
    id VARCHAR(36) PRIMARY KEY,
    project_id VARCHAR(36) NOT NULL,
    title VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    sentiment_score FLOAT,
    urgency_level VARCHAR(50) DEFAULT 'HIGH',
    confidence FLOAT DEFAULT 0.95,
    status VARCHAR(50) DEFAULT 'QUEUED'
);
"""
        }


def build_contextual_apis(ctx: Dict[str, Any]) -> Dict[str, Any]:
    project_name = ctx.get("name", "TransformIQ API")
    domain = detect_domain(ctx)

    if domain == "HR_RECRUITING":
        return {
            "api_title": f"{project_name} — Recruitment & ATS REST API",
            "version": "1.0.0",
            "base_url": "/api/v1",
            "endpoints": [
                {
                    "method": "POST",
                    "path": "/api/v1/candidates/parse-resume",
                    "summary": "AI Parse & Ingest Resume Document",
                    "description": "Uploads PDF/Word resume, extracts structured candidate profile, skills, and experience via Gemini AI.",
                    "category": "Candidate Management",
                    "auth_required": True,
                    "request_body": {"file_name": "sneha_sharma_resume.pdf", "file_base64": "JVBERi0xLjQK...", "target_job_id": "JOB-9021"},
                    "response_body": {"candidate_id": "CAND-8812", "full_name": "Sneha Sharma", "extracted_skills": ["Python", "React", "AWS", "FastAPI"], "years_experience": 5.5, "match_score": 0.94},
                    "error_responses": [{"code": 400, "message": "Invalid resume format"}, {"code": 401, "message": "Unauthorized"}]
                },
                {
                    "method": "POST",
                    "path": "/api/v1/recruiters/attendance/check-in",
                    "summary": "Log Recruiter Daily Attendance",
                    "description": "Records daily login time and initializes recruiter activity tracking session.",
                    "category": "Attendance & HRMS",
                    "auth_required": True,
                    "request_body": {"recruiter_user_id": "REC-012", "location_coords": "28.6139,77.2090"},
                    "response_body": {"status": "CHECKED_IN", "timestamp": "2026-09-23T09:00:00Z", "active_requisitions_count": 8},
                    "error_responses": [{"code": 400, "message": "Already checked in today"}]
                },
                {
                    "method": "POST",
                    "path": "/api/v1/clients/onboard",
                    "summary": "Submit Digital Client Onboarding",
                    "description": "Registers new enterprise client company with signed NDA and opens initial job requisitions.",
                    "category": "Client Management",
                    "auth_required": True,
                    "request_body": {"company_name": "Apex Fintech Ltd", "industry": "Fintech", "contact_email": "hr@apexfintech.com", "open_positions_count": 4},
                    "response_body": {"client_id": "CLIENT-4410", "onboarding_status": "ACTIVE", "portal_access_url": "https://aaravhr.com/client-portal/apex"},
                    "error_responses": [{"code": 400, "message": "Company email already registered"}]
                },
                {
                    "method": "GET",
                    "path": "/api/v1/placements/pipeline",
                    "summary": "Retrieve Active Placement Telemetry",
                    "description": "Returns counts of candidates across screening, client interview, offer, and joined stages.",
                    "category": "Analytics",
                    "auth_required": True,
                    "request_body": None,
                    "response_body": {"total_candidates": 4120, "active_interviews": 48, "offers_this_month": 19, "average_days_to_place": 6.2},
                    "error_responses": []
                }
            ],
            "openapi_spec": {"openapi": "3.0.3", "info": {"title": "Aarav HR ATS API", "version": "1.0.0"}}
        }
    elif domain == "RETAIL_SUPPLY_CHAIN":
        return {
            "api_title": f"{project_name} — Inventory & POS REST API",
            "version": "1.0.0",
            "base_url": "/api/v1",
            "endpoints": [
                {
                    "method": "POST",
                    "path": "/api/v1/inventory/sync-pos",
                    "summary": "Real-Time POS Sale Stock Deduction",
                    "description": "Deducts purchased SKU quantity from warehouse inventory ledger and updates channel availability in <50ms.",
                    "category": "POS Integration",
                    "auth_required": True,
                    "request_body": {"terminal_id": "POS-MUMBAI-01", "transaction_id": "TXN-88219", "items": [{"sku_code": "SKU-9921", "qty": 2, "unit_price": 49.99}]},
                    "response_body": {"status": "DEDUCTED_SUCCESS", "remaining_stock": 142, "reorder_triggered": False},
                    "error_responses": [{"code": 400, "message": "Insufficient stock balance"}, {"code": 401, "message": "Unauthorized terminal"}]
                },
                {
                    "method": "POST",
                    "path": "/api/v1/warehouses/stock-transfer",
                    "summary": "Initiate Inter-Warehouse Transfer",
                    "description": "Dispatches stock from central distribution center to retail store facing low inventory.",
                    "category": "Warehouse Logistics",
                    "auth_required": True,
                    "request_body": {"source_dc_id": "DC-CENTRAL", "target_store_id": "STORE-SOUTH", "sku_code": "SKU-9921", "transfer_qty": 200},
                    "response_body": {"transfer_id": "TRF-3301", "status": "IN_TRANSIT", "estimated_arrival": "2026-09-24T14:00:00Z"},
                    "error_responses": [{"code": 404, "message": "Warehouse location not found"}]
                },
                {
                    "method": "GET",
                    "path": "/api/v1/inventory/reorder-alerts",
                    "summary": "Retrieve AI Predictive Restock Alerts",
                    "description": "Returns list of merchandise SKUs projected to stock out within next 7 days based on velocity.",
                    "category": "Predictive AI",
                    "auth_required": True,
                    "request_body": None,
                    "response_body": {"alert_count": 6, "items": [{"sku_code": "SKU-1049", "current_stock": 12, "projected_demand_7d": 85, "recommended_order_qty": 250}]},
                    "error_responses": []
                }
            ],
            "openapi_spec": {"openapi": "3.0.3", "info": {"title": "Retail Inventory API", "version": "1.0.0"}}
        }
    else:
        return {
            "api_title": "TransformIQ Enterprise Solution API",
            "version": "1.0.0",
            "base_url": "/api/v1",
            "endpoints": [
                {
                    "method": "POST",
                    "path": "/api/v1/cases/ingest",
                    "summary": "Ingest and Classify Inbound Case",
                    "description": "Accepts raw case text or document metadata, executes AI classification and returns intent tags and routing destination.",
                    "category": "Core Ingestion",
                    "auth_required": True,
                    "request_body": {"customer_id": "CUST-98213", "channel": "EMAIL", "subject": "Delayed shipment order #49281", "body_text": "I ordered 5 days ago with express delivery and have not received tracking info."},
                    "response_body": {"case_id": "CASE-44910", "category": "Shipping & Logistics", "urgency": "HIGH", "sentiment": -0.72, "confidence": 0.96, "assigned_department": "Logistics Expedited Queue"},
                    "error_responses": [{"code": 400, "message": "Invalid payload format"}, {"code": 401, "message": "Unauthorized bearer token"}]
                },
                {
                    "method": "GET",
                    "path": "/api/v1/cases/{case_id}/recommendation",
                    "summary": "Retrieve AI Suggested Resolution Draft",
                    "description": "Performs semantic RAG over enterprise SOPs and outputs recommended resolution response for the agent.",
                    "category": "AI Services",
                    "auth_required": True,
                    "request_body": None,
                    "response_body": {"case_id": "CASE-44910", "suggested_response": "Dear Customer, we apologize for the delivery delay on order #49281. We have expedited your tracking with carrier priority.", "cited_sop": "SOP-LOG-04: Late Delivery Compensation Policy", "confidence": 0.94},
                    "error_responses": [{"code": 404, "message": "Case ID not found"}]
                }
            ],
            "openapi_spec": {"openapi": "3.0.3", "info": {"title": "TransformIQ API", "version": "1.0.0"}}
        }


def build_contextual_ux(ctx: Dict[str, Any]) -> Dict[str, Any]:
    project_name = ctx.get("name", "UX Design Studio")
    domain = detect_domain(ctx)

    if domain == "HR_RECRUITING":
        return {
            "ux_strategy": "High-velocity talent recruitment dashboard focused on candidate pipeline Kanban, fast resume previewing, 1-click interview scheduling, and client account health.",
            "personas": [
                {"name": "Aarav Sharma", "role": "Managing Director / Owner", "goals": ["Track daily recruiter attendance & outreach", "Monitor monthly placement revenue", "Accelerate client onboarding"], "pain_points": ["Spreadsheet data corruption", "Lost client contracts"]},
                {"name": "Sneha Verma", "role": "Senior Talent Recruiter", "goals": ["Parse candidate resumes instantly", "Match candidates to job openings with 1 click", "Avoid duplicate candidate calls"], "pain_points": ["Manual typing into 5 Excel files", "Lack of shared status"]}
            ],
            "user_journey_stages": [
                {"stage": "1. Resume Drop & Parse", "description": "Recruiter drags 20 resumes into portal; AI extracts skills and tags in <5 seconds."},
                {"stage": "2. Candidate-Job Matching", "description": "System calculates match % against open client requisitions and highlights top 3 matches."},
                {"stage": "3. Interview & Client Submission", "description": "Recruiter sends formatted profile to client portal with 1 click."},
                {"stage": "4. Placement & Attendance Telemetry", "description": "Offer accepted; automated placement record and commission generated."}
            ],
            "wireframes": [
                {
                    "screen_name": "Recruiter ATS Pipeline & Attendance Command Center",
                    "purpose": "Provides live candidate Kanban columns (New, Screened, Client Review, Offered, Placed), recruiter check-in button, and active requisition metrics.",
                    "target_users": ["Recruiters", "HR Operations", "Managing Director"],
                    "layout_type": "DASHBOARD",
                    "components": [
                        {"type": "header", "label": "Aarav HR — Recruiter Command Center", "props": {"badge": "Live ATS"}},
                        {"type": "stat_card", "label": "Active Placements This Month", "props": {"value": "24 Placed", "trend": "+35% vs target"}},
                        {"type": "stat_card", "label": "Recruiter Attendance Today", "props": {"value": "12 / 12 Present", "trend": "100% Team Checked-In"}},
                        {"type": "stat_card", "label": "Avg Client Onboarding Time", "props": {"value": "2.8 Days", "trend": "-78% from 14 days"}},
                        {"type": "table", "label": "Recent Candidate Resume Ingestions", "props": {"columns": ["Candidate Name", "Skills", "Exp (Yrs)", "Matched Job", "Status"]}}
                    ],
                    "user_actions": ["Upload Batch Resumes", "Check-In Attendance", "Create Client Requisition", "Export Placement Report"]
                },
                {
                    "screen_name": "Client Self-Service Onboarding & Job Requisition Portal",
                    "purpose": "Enables corporate clients to sign digital agreements, view shortlisted candidate profiles, and approve interview slots.",
                    "target_users": ["Corporate Client HR", "Hiring Managers"],
                    "layout_type": "DETAIL",
                    "components": [
                        {"type": "alert", "label": "3 Candidates Shortlisted for Senior Fullstack Engineer", "props": {"severity": "info"}},
                        {"type": "form_group", "label": "Submit New Job Requisition", "props": {"value": "Role, Experience, Budget, Tech Stack"}},
                        {"type": "button", "label": "Schedule Technical Interview", "props": {"variant": "primary"}}
                    ],
                    "user_actions": ["Approve Candidate", "Request More Profiles", "Sign Agreement"]
                }
            ]
        }
    elif domain == "RETAIL_SUPPLY_CHAIN":
        return {
            "ux_strategy": "High-density retail telemetry command center and touch-optimized cashier POS interface engineered for sub-second barcode scans and offline survivability.",
            "personas": [
                {"name": "Robert Chen", "role": "VP of Supply Chain", "goals": ["Monitor real-time inventory across 40 stores", "Eliminate out-of-stock items", "Optimize warehouse transfers"], "pain_points": ["24-hour stock blindness", "Emergency logistics costs"]},
                {"name": "Maria Santos", "role": "Store Cashier & Stock Clerk", "goals": ["Scan items without register lag", "Check nearby store stock when item is sold out", "Process checkout during internet drops"], "pain_points": ["Frozen POS terminals", "Customer queue complaints"]}
            ],
            "user_journey_stages": [
                {"stage": "1. In-Store Barcode Scan", "description": "Cashier scans SKU; sub-100ms pricing lookup and local cart calculation."},
                {"stage": "2. Real-Time Event Sync", "description": "Payment confirmed; event dispatched to central PostgreSQL ledger to deduct stock globally."},
                {"stage": "3. Predictive Reorder Alert", "description": "Inventory drops below safety threshold; AI generates automated warehouse transfer order."},
                {"stage": "4. Warehouse Pick & Delivery", "description": "Warehouse picker scans QR code to dispatch replacement stock to store."}
            ],
            "wireframes": [
                {
                    "screen_name": "Omni-Channel Retail Inventory Command Center",
                    "purpose": "Displays live stock levels across central warehouses and retail stores, stockout risk alerts, and offline POS sync status.",
                    "target_users": ["Supply Chain Leaders", "Store Managers"],
                    "layout_type": "DASHBOARD",
                    "components": [
                        {"type": "header", "label": "Global Retail — Multi-Store Inventory Hub", "props": {"badge": "Sub-Second Sync"}},
                        {"type": "stat_card", "label": "Stockout Incidents Prevented", "props": {"value": "184 Items", "trend": "-82% Stockouts"}},
                        {"type": "stat_card", "label": "POS Real-Time Sync Latency", "props": {"value": "42ms", "trend": "Live WebSocket"}},
                        {"type": "stat_card", "label": "Active Stores Online", "props": {"value": "48 / 48 Stores", "trend": "100% Operational"}},
                        {"type": "table", "label": "Critical Inventory Restock Alerts", "props": {"columns": ["SKU Code", "Item Name", "Current Stock", "Reorder Qty", "Action"]}}
                    ],
                    "user_actions": ["Trigger Warehouse Transfer", "Reconcile Cycle Count", "Export Stock Valuation"]
                }
            ]
        }
    else:
        return {
            "ux_strategy": "High-density enterprise design system emphasizing zero-cognitive-friction, dark/light theme harmony, responsive layout, and instant explainability.",
            "personas": [
                {"name": "Elena Rostova", "role": "Chief Operating Officer / Executive", "goals": ["Monitor transformation ROI", "Track SLA compliance across departments", "Identify operational bottlenecks early"], "pain_points": ["Static monthly reports", "Lack of real-time visibility"]},
                {"name": "Devin Clark", "role": "Frontline Operations Lead", "goals": ["Process flagged cases with minimal clicks", "Review AI suggestions quickly", "Manage agent shift queues"], "pain_points": ["Context switching between 5 apps", "Manual copy-pasting"]}
            ],
            "user_journey_stages": [
                {"stage": "1. Discovery & Upload", "description": "User enters business problem or uploads SOP/BRD document."},
                {"stage": "2. Intelligence Generation", "description": "AI generates gap analysis, recommendations, and transformation score."},
                {"stage": "3. Interactive Design", "description": "Architect refines React Flow HLD/LLD diagrams, ER schema, and API catalog."},
                {"stage": "4. What-If Simulation", "description": "User tunes budget/team sliders to recalculate timeline and ROI."},
                {"stage": "5. Blueprint Approval & Export", "description": "Executive reviews and exports one-click PDF, Word, Excel, or PPT reports."}
            ],
            "wireframes": [
                {
                    "screen_name": "Executive Transformation Dashboard",
                    "purpose": "Provides high-level transformation KPIs, readiness score radar, and active bottleneck alerts.",
                    "target_users": ["Executive Leadership", "Transformation Directors"],
                    "layout_type": "DASHBOARD",
                    "components": [
                        {"type": "header", "label": "TransformIQ Command Center", "props": {"badge": "Live Telemetry"}},
                        {"type": "stat_card", "label": "Transformation Readiness", "props": {"value": "88/100", "trend": "+12% vs benchmark"}},
                        {"type": "stat_card", "label": "Automation Potential", "props": {"value": "84%", "trend": "High Straight-Through Rate"}},
                        {"type": "stat_card", "label": "Projected Annual ROI", "props": {"value": "$420,000", "trend": "340% Total Return"}}
                    ],
                    "user_actions": ["Filter by Department", "Export PDF Summary", "Launch What-If Simulator"]
                }
            ]
        }


def build_contextual_planning(ctx: Dict[str, Any]) -> Dict[str, Any]:
    project_name = ctx.get("name", "Master Roadmap")
    domain = detect_domain(ctx)

    if domain == "HR_RECRUITING":
        return {
            "name": f"{project_name} — 12-Week Agile Delivery Roadmap",
            "total_duration_weeks": 12,
            "phases": [
                {
                    "phase_name": "Phase 1: Excel Data Migration & ATS Database Setup",
                    "duration_weeks": 3,
                    "objective": "Consolidate 5 Excel candidate workbooks into 3NF PostgreSQL schema with duplicate cleaning.",
                    "tasks": [
                        {"title": "Excel Data Audit & Duplicate Scrubbing", "duration": "Week 1", "owner": "Data Engineer", "deliverable": "Cleaned Candidate Master Dataset"},
                        {"title": "PostgreSQL Schema Setup & Multi-Tenant Migrations", "duration": "Week 2-3", "owner": "Backend Lead", "deliverable": "Active Database Schema"}
                    ],
                    "milestones": ["Data Migration Complete", "Zero Duplicate Profiles"],
                    "risks": ["Inconsistent formatting across historical Excel files"]
                },
                {
                    "phase_name": "Phase 2: AI Resume Parsing & Recruiter CRM Engine",
                    "duration_weeks": 4,
                    "objective": "Build FastAPI endpoints for AI resume ingestion, skill extraction, and candidate pipeline tracking.",
                    "tasks": [
                        {"title": "Gemini Resume Parsing Pipeline Integration", "duration": "Week 4-5", "owner": "AI Engineer", "deliverable": "Resume Parser Service (<2s)"},
                        {"title": "Recruiter Attendance & Activity Tracking Engine", "duration": "Week 6-7", "owner": "Backend Engineer", "deliverable": "Attendance API & Dashboards"}
                    ],
                    "milestones": ["Resume Parser Alpha Live", "Recruiter Attendance Module Ready"],
                    "risks": ["Unstructured PDF resume variations"]
                },
                {
                    "phase_name": "Phase 3: Public Website & Client Onboarding Portal",
                    "duration_weeks": 3,
                    "objective": "Launch public website to showcase HR services and deploy client onboarding hub.",
                    "tasks": [
                        {"title": "Public Services Website & Job Board", "duration": "Week 8-9", "owner": "Frontend Engineer", "deliverable": "Responsive Public Web Portal"},
                        {"title": "Client Digital Onboarding & E-Contracts", "duration": "Week 9-10", "owner": "Fullstack Engineer", "deliverable": "3-Day Digital Onboarding Flow"}
                    ],
                    "milestones": ["Public Website Live", "First Client Digital Onboarded"],
                    "risks": ["Client adoption of online contracts"]
                },
                {
                    "phase_name": "Phase 4: UAT, Recruiter Training & Full Go-Live",
                    "duration_weeks": 2,
                    "objective": "Train team of 12 recruiters, sunset Excel workbooks, and achieve 100% production rollout.",
                    "tasks": [
                        {"title": "Recruiter Workflow Training & SOP Handover", "duration": "Week 11", "owner": "Program Manager", "deliverable": "Trained Recruitment Team"},
                        {"title": "Production Deployment & Excel Sunset", "duration": "Week 12", "owner": "DevOps Lead", "deliverable": "100% Live Production System"}
                    ],
                    "milestones": ["Excel Fully Deprecated", "Go-Live Complete"],
                    "risks": ["Resistance to digital attendance transition"]
                }
            ]
        }
    elif domain == "RETAIL_SUPPLY_CHAIN":
        return {
            "name": f"{project_name} — 14-Week Retail Transformation Roadmap",
            "total_duration_weeks": 14,
            "phases": [
                {
                    "phase_name": "Phase 1: Architecture & Real-Time Event Bus Setup",
                    "duration_weeks": 3,
                    "objective": "Deploy Redis Pub/Sub cluster and configure FastAPI inventory ledger.",
                    "tasks": [
                        {"title": "Inventory Ledger Schema & Pessimistic Lock Setup", "duration": "Week 1-2", "owner": "Backend Lead", "deliverable": "PostgreSQL 16 Inventory DB"},
                        {"title": "Redis Event Stream & WebSocket Bus Configuration", "duration": "Week 2-3", "owner": "Cloud Architect", "deliverable": "Real-time Event Stream"}
                    ],
                    "milestones": ["Event Bus Configured", "Sub-50ms Latency Validated"],
                    "risks": ["Network jitter between store branches and cloud"]
                },
                {
                    "phase_name": "Phase 2: Offline-First Store POS PWA Development",
                    "duration_weeks": 4,
                    "objective": "Build touch-optimized offline POS cashier terminal with automated queue reconciliation.",
                    "tasks": [
                        {"title": "POS PWA Frontend & Barcode Scanning Integration", "duration": "Week 4-6", "owner": "Frontend Lead", "deliverable": "React PWA POS Client"},
                        {"title": "Offline IndexedDB Cache & Recovery Sync Engine", "duration": "Week 6-7", "owner": "Fullstack Engineer", "deliverable": "Zero-Loss Sync Worker"}
                    ],
                    "milestones": ["POS Offline Alpha Test Passed", "Store Pilot Demo"],
                    "risks": ["Barcode scanner hardware compatibility"]
                },
                {
                    "phase_name": "Phase 3: Predictive Replenishment & Warehouse Scanner",
                    "duration_weeks": 4,
                    "objective": "Integrate AI demand forecasting and mobile warehouse picking application.",
                    "tasks": [
                        {"title": "AI Predictive Demand & Safety Stock Forecasting", "duration": "Week 8-10", "owner": "AI/ML Engineer", "deliverable": "Replenishment Algorithm"},
                        {"title": "Mobile Warehouse Pick-Pack-Ship Application", "duration": "Week 10-11", "owner": "Frontend Engineer", "deliverable": "Mobile Scanner UI"}
                    ],
                    "milestones": ["Warehouse Mobile Scanner Live", "First AI Reorder Generated"],
                    "risks": ["Warehouse staff learning curve on mobile scanners"]
                },
                {
                    "phase_name": "Phase 4: Store Cutover & Production Rollout",
                    "duration_weeks": 3,
                    "objective": "Roll out across all retail store branches and decommission nightly batch jobs.",
                    "tasks": [
                        {"title": "Phased 5-Store Pilot Cutover & Monitoring", "duration": "Week 12-13", "owner": "Retail Ops Director", "deliverable": "Pilot Evaluation Report"},
                        {"title": "Full Network Deployment & 24h Batch Sunset", "duration": "Week 14", "owner": "DevOps Lead", "deliverable": "100% Live Retail Network"}
                    ],
                    "milestones": ["Batch FTP Script Decommissioned", "Full Go-Live Complete"],
                    "risks": ["Holiday peak traffic surges"]
                }
            ]
        }
    else:
        return {
            "name": f"{project_name} Master Transformation Roadmap",
            "total_duration_weeks": 16,
            "phases": [
                {
                    "phase_name": "Phase 1: Discovery & Architecture Alignment",
                    "duration_weeks": 3,
                    "objective": "Ingest enterprise artifacts, validate functional requirements, and align security boundaries.",
                    "tasks": [
                        {"title": "Stakeholder Discovery Interviews & SOP Ingestion", "duration": "Week 1-2", "owner": "Lead Business Analyst", "deliverable": "Validated Business Analysis Spec"},
                        {"title": "Architecture & Security Boundary Sign-Off", "duration": "Week 2-3", "owner": "Solution Architect", "deliverable": "HLD/LLD Technical Blueprint"}
                    ],
                    "milestones": ["Architecture Sign-Off", "Security Review Approval"],
                    "risks": ["Delay in legacy database credentials provisioning"]
                },
                {
                    "phase_name": "Phase 2: Core Platform & AI Engine Development",
                    "duration_weeks": 6,
                    "objective": "Build FastAPI microservices, configure PostgreSQL/pgvector, and train/fine-tune AI classifiers.",
                    "tasks": [
                        {"title": "REST API Gateway & Multi-Tenant Database Setup", "duration": "Week 4-6", "owner": "Backend Lead", "deliverable": "OpenAPI 3.0 Endpoints & Migrations"},
                        {"title": "AI Classification Pipeline & RAG Knowledge Store", "duration": "Week 6-9", "owner": "AI/ML Engineer", "deliverable": "Model Inference Service (<300ms latency)"}
                    ],
                    "milestones": ["AI Ingestion Service Live", "Alpha API Integration"],
                    "risks": ["Data skew in historical ticket training corpus"]
                },
                {
                    "phase_name": "Phase 3: Frontend Experience & Human-in-the-Loop Hub",
                    "duration_weeks": 4,
                    "objective": "Deliver responsive React SPA, interactive diagram editors, and specialist review hubs.",
                    "tasks": [
                        {"title": "Executive Dashboard & Live Telemetry Views", "duration": "Week 10-12", "owner": "Frontend Engineer", "deliverable": "React 18 + Tailwind SPA"},
                        {"title": "Human-in-the-Loop Exception Queue", "duration": "Week 12-13", "owner": "Fullstack Engineer", "deliverable": "Specialist Review Interface"}
                    ],
                    "milestones": ["Feature Complete Demo", "User Acceptance Testing (UAT)"],
                    "risks": ["Agent resistance to new user workflow"]
                },
                {
                    "phase_name": "Phase 4: Pilot Rollout & Production Hardening",
                    "duration_weeks": 3,
                    "objective": "Conduct security penetration testing, load testing, and phased production cutover.",
                    "tasks": [
                        {"title": "SOC2 Compliance Audit & Load Testing (5000 req/min)", "duration": "Week 14", "owner": "DevOps & Security Lead", "deliverable": "Audit Penetration Report"},
                        {"title": "Phased Production Deployment & Training", "duration": "Week 15-16", "owner": "Program Manager", "deliverable": "100% Production Cutover"}
                    ],
                    "milestones": ["Go-Live Deployment", "Phase 1 Transformation Complete"],
                    "risks": ["Traffic surges during holiday peak"]
                }
            ]
        }


def build_contextual_estimates(ctx: Dict[str, Any]) -> Dict[str, Any]:
    domain = detect_domain(ctx)
    if domain == "HR_RECRUITING":
        return {
            "total_estimated_hours": 840,
            "total_estimated_cost": 96500.0,
            "currency": "USD",
            "duration_months": 3,
            "roles_breakdown": [
                {"role": "Lead Solutions Architect", "headcount": 1, "hours": 120, "rate_hourly": 140.0, "cost": 16800.0},
                {"role": "Senior Fullstack Engineer (React / FastAPI)", "headcount": 2, "hours": 440, "rate_hourly": 115.0, "cost": 50600.0},
                {"role": "AI / NLP Engineer", "headcount": 1, "hours": 160, "rate_hourly": 130.0, "cost": 20800.0},
                {"role": "QA & Deployment Specialist", "headcount": 1, "hours": 120, "rate_hourly": 69.17, "cost": 8300.0}
            ],
            "infrastructure_cost_monthly": 350.0,
            "ai_api_cost_monthly": 180.0,
            "assumptions": ["12-week agile delivery timeline", "Standard cloud compute on Render / Azure Container Apps"],
            "confidence_level": "HIGH"
        }
    elif domain == "RETAIL_SUPPLY_CHAIN":
        return {
            "total_estimated_hours": 1020,
            "total_estimated_cost": 128000.0,
            "currency": "USD",
            "duration_months": 3.5,
            "roles_breakdown": [
                {"role": "Principal Solutions Architect", "headcount": 1, "hours": 140, "rate_hourly": 145.0, "cost": 20300.0},
                {"role": "Senior Backend & Event Stream Engineer", "headcount": 2, "hours": 460, "rate_hourly": 125.0, "cost": 57500.0},
                {"role": "Senior POS / PWA Frontend Engineer", "headcount": 1, "hours": 260, "rate_hourly": 115.0, "cost": 29900.0},
                {"role": "DevOps & Hardware Integration Specialist", "headcount": 1, "hours": 160, "rate_hourly": 126.88, "cost": 20300.0}
            ],
            "infrastructure_cost_monthly": 550.0,
            "ai_api_cost_monthly": 240.0,
            "assumptions": ["3.5-month delivery with multi-store pilot", "Redis Pub/Sub cluster + PostgreSQL multi-AZ"],
            "confidence_level": "HIGH"
        }
    else:
        return {
            "total_estimated_hours": 1120,
            "total_estimated_cost": 138500.0,
            "currency": "USD",
            "duration_months": 4,
            "roles_breakdown": [
                {"role": "Lead Solution Architect", "headcount": 1, "hours": 160, "rate_hourly": 140.0, "cost": 22400.0},
                {"role": "Senior AI / ML Engineer", "headcount": 1, "hours": 280, "rate_hourly": 135.0, "cost": 37800.0},
                {"role": "Senior Backend Engineer (Python/FastAPI)", "headcount": 1, "hours": 280, "rate_hourly": 120.0, "cost": 33600.0},
                {"role": "Senior Frontend Engineer (React/TypeScript)", "headcount": 1, "hours": 240, "rate_hourly": 115.0, "cost": 27600.0},
                {"role": "DevOps & Security Specialist", "headcount": 1, "hours": 80, "rate_hourly": 130.0, "cost": 10400.0},
                {"role": "QA & Test Automation Engineer", "headcount": 1, "hours": 80, "rate_hourly": 85.0, "cost": 6800.0}
            ],
            "infrastructure_cost_monthly": 650.0,
            "ai_api_cost_monthly": 420.0,
            "assumptions": ["Standard 4-month delivery cadence with dedicated agile sprint team."],
            "confidence_level": "HIGH"
        }


def build_contextual_risks(ctx: Dict[str, Any]) -> Dict[str, Any]:
    domain = detect_domain(ctx)
    if domain == "HR_RECRUITING":
        return {
            "summary": "Risk matrix for HR Consultancy transformation highlights data migration fidelity, recruiter workflow adoption, and client onboarding compliance.",
            "risks": [
                {"category": "Data", "risk_title": "Historical Excel Data Inconsistency", "impact": "MEDIUM", "likelihood": "HIGH", "mitigation": "Automated data normalization scripts with fuzzy candidate deduplication algorithms."},
                {"category": "Adoption", "risk_title": "Recruiter Resistance to Attendance & ATS", "impact": "MEDIUM", "likelihood": "MEDIUM", "mitigation": "Provide intuitive, low-click UI with gamified placement tracking and mobile check-in."},
                {"category": "Compliance", "risk_title": "Candidate PII Data Protection", "impact": "HIGH", "likelihood": "LOW", "mitigation": "AES-256 cloud encryption, time-limited signed CV download URLs, and strict RBAC guards."},
                {"category": "AI", "risk_title": "Unconventional Resume Format Parsing Errors", "impact": "LOW", "likelihood": "MEDIUM", "mitigation": "Human-in-the-loop manual skill editor fallback when confidence score is <80%."}
            ]
        }
    elif domain == "RETAIL_SUPPLY_CHAIN":
        return {
            "summary": "Risk matrix for Retail & Inventory transformation highlights network disruptions, POS hardware variance, and holiday peak load.",
            "risks": [
                {"category": "Infrastructure", "risk_title": "Store Broadband Outages During Rush Hours", "impact": "HIGH", "likelihood": "MEDIUM", "mitigation": "Offline-first PWA POS architecture with local IndexedDB buffering and automatic sync upon reconnect."},
                {"category": "Integration", "risk_title": "Multi-Store Concurrency Race Conditions", "impact": "HIGH", "likelihood": "LOW", "mitigation": "Pessimistic inventory locking in PostgreSQL with Redis sub-millisecond stock streams."},
                {"category": "Adoption", "risk_title": "Warehouse Staff Barcode Scanner Learning Curve", "impact": "MEDIUM", "likelihood": "MEDIUM", "mitigation": "Audio-guided visual picking routes on Android mobile devices with 1-day training workshops."},
                {"category": "Scale", "risk_title": "Black Friday 50x Traffic Surges", "impact": "HIGH", "likelihood": "LOW", "mitigation": "Horizontal container auto-scaling and Redis queue decoupling."}
            ]
        }
    else:
        return {
            "summary": "Risk evaluation matrix identified 4 manageable project risks with pre-emptive mitigation strategies.",
            "risks": [
                {"category": "Technical", "risk_title": "Integration with Legacy Backend Endpoints", "impact": "HIGH", "likelihood": "MEDIUM", "mitigation": "Build robust adapter middleware with exponential backoff retries."},
                {"category": "AI", "risk_title": "Hallucination or Misclassification on Edge Cases", "impact": "MEDIUM", "likelihood": "LOW", "mitigation": "Enforce strict Human-in-the-Loop review queue for confidence scores <85%."},
                {"category": "Security", "risk_title": "PII Exposure in AI Prompts", "impact": "CRITICAL", "likelihood": "LOW", "mitigation": "Automatic regex and NLP PII redaction layer prior to model inference."},
                {"category": "Schedule", "risk_title": "Scope Creep During Sprint Reviews", "impact": "MEDIUM", "likelihood": "MEDIUM", "mitigation": "Strict milestone definition with formal change request governance."}
            ]
        }


def build_contextual_score(ctx: Dict[str, Any]) -> Dict[str, Any]:
    domain = detect_domain(ctx)
    if domain == "HR_RECRUITING":
        return {
            "overall_score": 86,
            "overall_readiness_score": 86,
            "ai_readiness": 92,
            "automation_potential": 88,
            "data_readiness": 84,
            "business_impact": 94,
            "technical_feasibility": 90,
            "implementation_readiness": 85,
            "tier": "TRANSFORMATION_READY",
            "benchmark_percentile": 89,
            "executive_summary": "Strong business justification for digital ATS, client onboarding acceleration, and recruiter attendance automation. High feasibility with rapid 12-week ROI.",
            "key_drivers": [
                "Cutting client onboarding cycle from 14 days down to 3 days.",
                "Eliminating candidate duplication across 5 disparate Excel spreadsheets.",
                "Automating daily recruiter check-in and activity telemetry."
            ],
            "key_blockers": [
                "Historical resume formatting variance requiring human-in-the-loop fallback.",
                "Recruiter change management during migration off legacy spreadsheets."
            ],
            "strategic_recommendations": [
                "Deploy unified PostgreSQL ATS schema with email/phone deduplication index.",
                "Integrate Gemini 3.5 Flash Lite resume parsing pipeline for sub-2s candidate ingestion.",
                "Launch public career website with client digital contract onboarding."
            ],
            "dimensions": [
                {"dimension": "Process Maturity", "score": 78, "benchmark": 65, "status": "ADVANCED"},
                {"dimension": "Technology Modernization", "score": 88, "benchmark": 70, "status": "EXCELLENT"},
                {"dimension": "AI & Resume Intelligence", "score": 92, "benchmark": 60, "status": "INDUSTRY_LEADER"},
                {"dimension": "Data Architecture & Deduplication", "score": 84, "benchmark": 68, "status": "EXCELLENT"},
                {"dimension": "Recruiter Adoption & Culture", "score": 82, "benchmark": 72, "status": "ADVANCED"},
                {"dimension": "Candidate Security & Compliance", "score": 90, "benchmark": 75, "status": "EXCELLENT"},
                {"dimension": "Client Workflow Automation", "score": 86, "benchmark": 64, "status": "EXCELLENT"},
                {"dimension": "Enterprise Integration", "score": 88, "benchmark": 69, "status": "EXCELLENT"}
            ],
            "strengths": [
                "Clear business objective: cutting onboarding from 14 days to 3 days.",
                "High willingness to deprecate 5 manual Excel spreadsheets.",
                "Direct revenue impact through faster candidate placement turnaround."
            ],
            "recommendations_summary": "Proceed directly to Phase 1 database migration and AI resume parser deployment."
        }
    elif domain == "RETAIL_SUPPLY_CHAIN":
        return {
            "overall_score": 89,
            "overall_readiness_score": 89,
            "ai_readiness": 88,
            "automation_potential": 94,
            "data_readiness": 92,
            "business_impact": 96,
            "technical_feasibility": 91,
            "implementation_readiness": 87,
            "tier": "ENTERPRISE_READY",
            "benchmark_percentile": 93,
            "executive_summary": "Compelling operational case for real-time inventory synchronization. High technical feasibility with event-driven microservices architecture.",
            "key_drivers": [
                "Eliminating out-of-stock incidents and customer lost sales across 40+ stores.",
                "Transitioning from 24h batch synchronization to sub-50ms Redis event streams.",
                "Offline POS survivability during retail broadband disruptions."
            ],
            "key_blockers": [
                "Store barcode scanner hardware calibration across retail branches.",
                "High concurrency load handling during Black Friday peak shopping hours."
            ],
            "strategic_recommendations": [
                "Configure Redis Pub/Sub cluster with PostgreSQL pessimistic stock lock guards.",
                "Deploy PWA offline store registers with background reconciliation worker.",
                "Implement AI demand forecasting for automated inter-warehouse transfers."
            ],
            "dimensions": [
                {"dimension": "Process Maturity", "score": 84, "benchmark": 68, "status": "EXCELLENT"},
                {"dimension": "Technology Modernization", "score": 94, "benchmark": 72, "status": "INDUSTRY_LEADER"},
                {"dimension": "AI & Demand Forecasting", "score": 88, "benchmark": 62, "status": "EXCELLENT"},
                {"dimension": "Real-Time Inventory Data", "score": 92, "benchmark": 70, "status": "INDUSTRY_LEADER"},
                {"dimension": "Store Staff Operations", "score": 80, "benchmark": 71, "status": "ADVANCED"},
                {"dimension": "PCI & Transaction Security", "score": 95, "benchmark": 80, "status": "INDUSTRY_LEADER"},
                {"dimension": "POS Event Automation", "score": 90, "benchmark": 66, "status": "INDUSTRY_LEADER"},
                {"dimension": "Supply Chain Integration", "score": 89, "benchmark": 70, "status": "EXCELLENT"}
            ],
            "strengths": [
                "Massive financial return from preventing store stockouts and inventory shrinkage.",
                "Clear architectural path from nightly batch to sub-second Redis event streams.",
                "Offline-first POS design guarantees zero store sales disruption."
            ],
            "recommendations_summary": "Approve architecture blueprint and initiate Phase 1 Redis event bus configuration."
        }
    else:
        return {
            "overall_score": 88,
            "overall_readiness_score": 88,
            "ai_readiness": 94,
            "automation_potential": 91,
            "data_readiness": 86,
            "business_impact": 92,
            "technical_feasibility": 89,
            "implementation_readiness": 88,
            "tier": "TRANSFORMATION_READY",
            "benchmark_percentile": 91,
            "executive_summary": "High operational readiness across all 8 enterprise dimensions. AI straight-through processing will deliver immediate 70%+ latency reduction.",
            "key_drivers": [
                "Accelerating triage resolution from 48h to 12 minutes.",
                "Automating tier-1 classification with >85% confidence threshold.",
                "Empowering support staff with semantic RAG SOP recommendations."
            ],
            "key_blockers": [
                "Legacy CRM API connectivity and rate limitations.",
                "Initial SOP document vectorization corpus preparation."
            ],
            "strategic_recommendations": [
                "Deploy multi-class transformer classification microservice.",
                "Implement human-in-the-loop review queue for low-confidence edge cases.",
                "Build real-time executive telemetry dashboard for SLA tracking."
            ],
            "dimensions": [
                {"dimension": "Process Maturity", "score": 82, "benchmark": 67, "status": "EXCELLENT"},
                {"dimension": "Technology Modernization", "score": 91, "benchmark": 71, "status": "EXCELLENT"},
                {"dimension": "AI & NLP Automation", "score": 94, "benchmark": 62, "status": "INDUSTRY_LEADER"},
                {"dimension": "Data Architecture & RAG", "score": 86, "benchmark": 68, "status": "EXCELLENT"},
                {"dimension": "People & Change Management", "score": 79, "benchmark": 70, "status": "ADVANCED"},
                {"dimension": "Security & RBAC Compliance", "score": 93, "benchmark": 78, "status": "INDUSTRY_LEADER"},
                {"dimension": "Workflow Automation", "score": 89, "benchmark": 65, "status": "EXCELLENT"},
                {"dimension": "API & Integration Layer", "score": 90, "benchmark": 69, "status": "EXCELLENT"}
            ],
            "strengths": [
                "Executive sponsorship aligned with clear ROI and SLA targets.",
                "Robust microservices and vector embedding architecture.",
                "Built-in Human-in-the-Loop review safeguards for compliance safety."
            ],
            "recommendations_summary": "Proceed with Phase 1 deployment and model fine-tuning on enterprise SOP corpus."
        }


def calculate_what_if_simulation(req: Dict[str, Any]) -> Dict[str, Any]:
    budget = float(req.get("budget", 150000.0))
    team_size = int(req.get("team_size", 6))
    
    # Handle both automation_level (0-100) and automation_target (0.0-1.0)
    raw_auto = req.get("automation_level")
    if raw_auto is not None:
        auto_level_int = int(raw_auto)
        automation_target = auto_level_int / 100.0 if auto_level_int > 1 else float(auto_level_int)
    else:
        automation_target = float(req.get("automation_target", 0.80))
        auto_level_int = int(automation_target * 100) if automation_target <= 1 else int(automation_target)

    timeline_months = int(req.get("timeline_months", 4))
    ai_adoption = req.get("ai_adoption_level", "HIGH").upper()
    include_rag = bool(req.get("include_rag", True))
    complexity = req.get("complexity", "MEDIUM")

    # Base baseline timeline
    base_weeks = float(timeline_months * 4.0)
    if team_size > 6:
        base_weeks = max(8.0, base_weeks - (team_size - 6) * 1.2)
    elif team_size < 6:
        base_weeks = min(36.0, base_weeks + (6 - team_size) * 2.0)

    if complexity == "HIGH" or ai_adoption == "AGGRESSIVE":
        base_weeks *= 1.15
    elif complexity == "LOW" or ai_adoption == "LOW":
        base_weeks *= 0.90

    # Effort calculation
    projected_effort_hours = int(base_weeks * 40 * team_size)
    projected_timeline_months = round(base_weeks / 4.0, 1)

    # ROI Calculation
    multiplier = 3.2 if ai_adoption in ["HIGH", "AGGRESSIVE"] else 2.4
    annual_savings = (budget * multiplier) * automation_target * (1.15 if include_rag else 1.0)
    net_roi_percent = round(((annual_savings - budget) / budget) * 100, 1)
    efficiency_gain = round(min(95.0, auto_level_int * (1.1 if include_rag else 0.95)), 1)
    breakeven_months = round(max(2.5, 12.0 / ((net_roi_percent / 100.0) + 1.0)), 1)
    risk_level = "LOW" if team_size >= 5 and budget >= 100000 else "MEDIUM" if budget >= 75000 else "HIGH"

    insights = [
        f"Team size of {team_size} delivers projected go-live in {round(base_weeks, 1)} weeks ({projected_timeline_months} months).",
        f"Targeting {auto_level_int}% automation yields ${round(annual_savings):,} estimated annual operational savings with {net_roi_percent}% ROI.",
        f"Projected breakeven reached in {breakeven_months} months post-production rollout."
    ]

    scenario_name = req.get("scenario_name") or f"{ai_adoption} AI Adoption ({auto_level_int}% Automation, {team_size} Eng)"

    return {
        "scenario_name": scenario_name,
        "automation_level": auto_level_int,
        "team_size": team_size,
        "budget": budget,
        "timeline_months": timeline_months,
        "ai_adoption_level": ai_adoption,
        "projected_effort_hours": projected_effort_hours,
        "projected_cost": round(budget * 0.92, 2),
        "projected_timeline_months": projected_timeline_months,
        "expected_roi_percentage": net_roi_percent,
        "efficiency_gain_percentage": efficiency_gain,
        "risk_level": risk_level,
        "simulation_insights": insights,
        # Backward compatibility fields
        "calculated_timeline_weeks": round(base_weeks, 1),
        "calculated_budget_required": budget,
        "projected_annual_savings": round(annual_savings, 2),
        "projected_roi_percent": net_roi_percent,
        "breakeven_period_months": breakeven_months,
        "projected_straight_through_rate": efficiency_gain,
        "key_tradeoffs": insights
    }

