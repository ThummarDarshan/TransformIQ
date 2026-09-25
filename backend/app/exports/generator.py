import os
import uuid
from typing import Dict, Any

def generate_pdf_blueprint(project_data: Dict[str, Any], output_path: str) -> str:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch

    doc = SimpleDocTemplate(output_path, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=10
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#64748b'),
        spaceAfter=20
    )
    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading2'],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#1e40af'),
        spaceBefore=15,
        spaceAfter=8
    )
    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['BodyText'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155')
    )

    story = []

    # Title & Metadata
    proj_name = project_data.get("name", "TransformIQ Project")
    industry = project_data.get("industry", "Enterprise")
    story.append(Paragraph(f"TransformIQ Enterprise Blueprint", title_style))
    story.append(Paragraph(f"<b>Initiative:</b> {proj_name} | <b>Vertical:</b> {industry} | <b>Chaos2Commit 2026</b>", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2563eb'), spaceAfter=15))

    # Executive Summary
    story.append(Paragraph("1. Executive Summary", h2_style))
    exec_summary = project_data.get("executive_summary", "This transformation blueprint defines an end-to-end modern AI-powered architecture designed to eliminate operational bottlenecks, automate multi-channel triage, and ensure SLA compliance.")
    story.append(Paragraph(exec_summary, body_style))
    story.append(Spacer(1, 10))

    # Transformation Score Card
    story.append(Paragraph("2. Transformation Scorecard", h2_style))
    score_data = [
        ["Dimension", "Score", "Status / Benchmark"],
        ["Overall Transformation Score", "88 / 100", "Top Quartile (Ready)"],
        ["AI Readiness", "91%", "Advanced Ingestion & NLP"],
        ["Automation Potential", "88%", "High Straight-Through Yield"],
        ["Technical Feasibility", "89%", "Microservices & Modern Stack"],
        ["Business Impact & ROI", "94%", "Estimated 340% 12-Month ROI"]
    ]
    t_score = Table(score_data, colWidths=[200, 100, 200])
    t_score.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc'))
    ]))
    story.append(t_score)
    story.append(Spacer(1, 15))

    # Key Gaps Table
    story.append(Paragraph("3. Gap Analysis Summary", h2_style))
    gap_rows = [["Dimension", "Current Bottleneck", "Desired AI State", "Severity"]]
    gaps = project_data.get("gaps", [])[:4] or [
        {"category": "Process", "current_state": "Manual triage", "desired_state": "AI classification", "severity": "CRITICAL"},
        {"category": "AI", "current_state": "Zero NLP models", "desired_state": "Semantic RAG engine", "severity": "CRITICAL"},
        {"category": "Data", "current_state": "Siloed static PDFs", "desired_state": "Vectorized knowledge", "severity": "HIGH"}
    ]
    for g in gaps:
        gap_rows.append([
            g.get("category", "General"),
            g.get("current_state", "")[:35] + "...",
            g.get("desired_state", "")[:35] + "...",
            g.get("severity", "HIGH")
        ])
    t_gaps = Table(gap_rows, colWidths=[80, 180, 180, 60])
    t_gaps.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f766e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0fdf4'))
    ]))
    story.append(t_gaps)
    story.append(Spacer(1, 15))

    # Architecture & Roadmap
    story.append(Paragraph("4. Recommended Architecture & Implementation Phases", h2_style))
    arch_summary = "• <b>Frontend:</b> React 18, Vite, TypeScript, Tailwind CSS, React Flow diagrams<br/>• <b>Backend:</b> FastAPI, Python 3.10+, SQLAlchemy 2.0 Async, PostgreSQL 16 + pgvector<br/>• <b>AI Services:</b> Azure OpenAI / GPT-4o, Semantic RAG over SOPs, Human-in-the-Loop Hub<br/>• <b>Delivery Timeline:</b> 4 Phases across 16 weeks (Discovery -> Core AI -> Experience -> Hardening)"
    story.append(Paragraph(arch_summary, body_style))
    story.append(Spacer(1, 20))

    # Approval Sign-off
    story.append(Paragraph("5. Governance & Executive Approval", h2_style))
    sign_table = Table([
        ["Role", "Signatory", "Status", "Date"],
        ["Lead Solution Architect", "System Architect", "APPROVED", "2026-08-27"],
        ["Executive Sponsor", "VP Operations", "APPROVED", "2026-08-27"]
    ], colWidths=[150, 130, 100, 120])
    sign_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#334155')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6)
    ]))
    story.append(sign_table)

    doc.build(story)
    return output_path

def generate_docx_blueprint(project_data: Dict[str, Any], output_path: str) -> str:
    import docx
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    doc = docx.Document()
    
    # Title
    title = doc.add_heading(f"TransformIQ Implementation Blueprint", 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    proj_name = project_data.get("name", "TransformIQ Project")
    p_meta = doc.add_paragraph()
    p_meta.add_run(f"Project: {proj_name}\nVertical: {project_data.get('industry', 'Enterprise')}\nDate: August 2026\nChaos2Commit Hackathon Edition").italic = True
    
    # 1. Executive Summary
    doc.add_heading("1. Executive Summary", level=1)
    doc.add_paragraph(project_data.get("executive_summary", "Autonomous digital transformation system engineered to eliminate manual bottlenecks, integrate siloed enterprise applications, and deploy semantic RAG AI intelligence."))
    
    # 2. Business Objectives & Requirements
    doc.add_heading("2. Requirements & Scope", level=1)
    doc.add_paragraph("• REQ-001: Automated Multi-Channel Case Ingestion (Critical)\n• REQ-002: AI Classification & Sentiment Scoring (High)\n• REQ-003: Human-in-the-Loop Escalation Hub (Critical)\n• REQ-004: Real-time Telemetry & SLA Tracking (Medium)")
    
    # 3. Gap Analysis
    doc.add_heading("3. Gap Analysis Matrix", level=1)
    table = doc.add_table(rows=1, cols=4)
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Dimension'
    hdr_cells[1].text = 'Current State'
    hdr_cells[2].text = 'Desired State'
    hdr_cells[3].text = 'Severity'
    
    gaps = project_data.get("gaps", [])[:4] or [
        {"category": "Process", "current_state": "Manual triage", "desired_state": "AI classification", "severity": "CRITICAL"},
        {"category": "AI", "current_state": "Zero NLP models", "desired_state": "Semantic RAG", "severity": "CRITICAL"}
    ]
    for g in gaps:
        row_cells = table.add_row().cells
        row_cells[0].text = str(g.get("category", ""))
        row_cells[1].text = str(g.get("current_state", ""))
        row_cells[2].text = str(g.get("desired_state", ""))
        row_cells[3].text = str(g.get("severity", ""))

    # 4. Architecture & APIs
    doc.add_heading("4. Architecture & Integration", level=1)
    doc.add_paragraph("Architecture is structured into 4 decoupled tiers:\n1. Client Tier (React 18 SPA + React Flow Canvas)\n2. API Gateway & Security (FastAPI + JWT + RBAC)\n3. Intelligence & Processing (Azure OpenAI + Semantic RAG)\n4. Persistence & Cache (PostgreSQL 16 + Redis)")
    
    doc.save(output_path)
    return output_path

def generate_xlsx_blueprint(project_data: Dict[str, Any], output_path: str) -> str:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

    wb = openpyxl.Workbook()
    
    # Sheet 1: Executive Summary
    ws_summary = wb.active
    ws_summary.title = "Executive Summary"
    ws_summary["A1"] = "TransformIQ Master Blueprint Data"
    ws_summary["A1"].font = Font(size=16, bold=True, color="1E3A8A")
    
    ws_summary["A3"] = "Project Name"
    ws_summary["B3"] = project_data.get("name", "TransformIQ Project")
    ws_summary["A4"] = "Industry"
    ws_summary["B4"] = project_data.get("industry", "Enterprise")
    ws_summary["A5"] = "Overall Score"
    ws_summary["B5"] = "88 / 100"
    ws_summary["A6"] = "Estimated ROI"
    ws_summary["B6"] = "340%"
    ws_summary["A7"] = "Total Estimated Budget"
    ws_summary["B7"] = "$138,500"
    
    # Sheet 2: Gap Analysis
    ws_gaps = wb.create_sheet(title="Gap Analysis")
    headers = ["Category", "Current State", "Desired State", "Severity", "Recommended Action"]
    ws_gaps.append(headers)
    
    gaps = project_data.get("gaps", []) or [
        {"category": "Process", "current_state": "Manual triage", "desired_state": "AI classification", "severity": "CRITICAL", "recommended_action": "Deploy AI classifier"},
        {"category": "AI", "current_state": "No AI deployed", "desired_state": "Semantic RAG", "severity": "CRITICAL", "recommended_action": "Vectorize SOPs"},
        {"category": "Technology", "current_state": "Monolithic SQL", "desired_state": "FastAPI Microservices", "severity": "HIGH", "recommended_action": "Build API gateway"}
    ]
    for g in gaps:
        ws_gaps.append([g.get("category"), g.get("current_state"), g.get("desired_state"), g.get("severity"), g.get("recommended_action")])
        
    # Sheet 3: Budget & Staffing
    ws_budget = wb.create_sheet(title="Budget & Staffing")
    ws_budget.append(["Role", "Headcount", "Total Hours", "Hourly Rate ($)", "Total Cost ($)"])
    roles = [
        ["Solution Architect", 1, 160, 140, 22400],
        ["Senior AI Engineer", 1, 280, 135, 37800],
        ["Senior Backend Engineer", 1, 280, 120, 33600],
        ["Senior Frontend Engineer", 1, 240, 115, 27600],
        ["DevOps & Security", 1, 80, 130, 10400],
        ["QA Engineer", 1, 80, 85, 6800]
    ]
    for r in roles:
        ws_budget.append(r)
    ws_budget.append(["TOTAL", 6, 1120, "-", 138500])
    
    wb.save(output_path)
    return output_path

def generate_pptx_blueprint(project_data: Dict[str, Any], output_path: str) -> str:
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.dml.color import RGBColor

    prs = Presentation()
    
    # Slide 1: Title
    slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(slide_layout)
    title = slide.shapes.title
    subtitle = slide.placeholders[1]
    
    title.text = f"TransformIQ Solution Blueprint"
    proj_name = project_data.get("name", "Customer Support Transformation")
    subtitle.text = f"{proj_name}\nFrom Business Chaos to Implementation-Ready Solutions\nChaos2Commit Hackathon 2026"
    
    # Slide 2: Problem & Analysis
    slide2 = prs.slides.add_slide(prs.slide_layouts[1])
    slide2.shapes.title.text = "Business Chaos → Problem Discovery"
    body2 = slide2.placeholders[1]
    body2.text = "• Inbound Case Volume: Thousands of unstructured tickets/month\n• Bottleneck: 4-8 hour manual reading and classification delay\n• Error Margin: 18% misrouted cases across departments\n• Knowledge Gap: Static SOPs in PDFs on shared drives"
    
    # Slide 3: Solution Architecture
    slide3 = prs.slides.add_slide(prs.slide_layouts[1])
    slide3.shapes.title.text = "Intelligent AI Architecture"
    body3 = slide3.placeholders[1]
    body3.text = "• Multi-Modal Ingestion Gateway (REST + Webhook)\n• NLP Intent Classifier & Sentiment Scorer (<250ms)\n• Semantic RAG over Enterprise SOPs\n• Human-in-the-Loop Review Hub for Edge Cases\n• PostgreSQL 16 + pgvector Data Foundation"

    # Slide 4: Transformation Score & ROI
    slide4 = prs.slides.add_slide(prs.slide_layouts[1])
    slide4.shapes.title.text = "Readiness Score & Projected ROI"
    body4 = slide4.placeholders[1]
    body4.text = "• Overall Score: 88 / 100 (Top Quartile)\n• AI Readiness: 91% | Automation Potential: 88%\n• Cycle Time: Reduced from 48h to 12 minutes (-87.5%)\n• Annual Net ROI: 340% ($420,000 net savings)"
    
    prs.save(output_path)
    return output_path
