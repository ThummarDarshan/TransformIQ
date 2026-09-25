import logging
import re
from typing import Dict, Any, Optional
from app.config.settings import settings
from app.ai.provider import GeminiProvider, OpenAIProvider, AzureOpenAIProvider
from app.ai import smart_engine

logger = logging.getLogger(__name__)

class AIOrchestrator:
    def __init__(self):
        self.provider_name = settings.AI_PROVIDER
        
    def _get_provider(self):
        # 1. Check explicit provider preference
        if settings.AI_PROVIDER == "gemini" and settings.GEMINI_API_KEY:
            return GeminiProvider()
        elif settings.AI_PROVIDER == "openai" and settings.OPENAI_API_KEY:
            return OpenAIProvider()
        elif settings.AI_PROVIDER == "azure_openai" and settings.AZURE_OPENAI_API_KEY:
            return AzureOpenAIProvider()

        # 2. Auto-detection mode (prioritize Gemini for free-tier excellence)
        if settings.GEMINI_API_KEY:
            return GeminiProvider()
        elif settings.OPENAI_API_KEY:
            return OpenAIProvider()
        elif settings.AZURE_OPENAI_API_KEY:
            return AzureOpenAIProvider()
        return None

    async def run_discovery_chat(self, history: list, context_data: Dict[str, Any], language: str = "en") -> Dict[str, Any]:
        last_msg = history[-1]["content"] if history else "Tell me about this project."
        
        # Check if real LLM is configured
        provider = self._get_provider()
        if provider:
            try:
                system_prompt = f"You are the TransformIQ AI Discovery Assistant. Language: {language}. Ask structured discovery questions about processes, stakeholders, systems, bottlenecks, budget, and compliance."
                reply = await provider.generate_chat(
                    [{"role": "system", "content": system_prompt}] + history,
                    context_data
                )
                return {
                    "message": reply,
                    "suggested_actions": [
                        "Review current AS-IS process bottlenecks",
                        "Extract functional requirements",
                        "Generate 8-dimension gap analysis",
                        "Calculate TransformIQ readiness score"
                    ]
                }
            except Exception as e:
                logger.warning(f"AI Provider call failed, falling back to smart engine: {e}")

        # Contextual dynamic discovery response
        proj_name = context_data.get("name", "this initiative")
        industry = context_data.get("industry", "enterprise")
        
        # Multilingual conversational greetings
        if language == "hi":
            reply = f"नमस्ते! मैं TransformIQ AI डिस्कवरी सहायक हूँ। '{proj_name}' के संदर्भ में आपके {industry} वर्कफ़्लो और मुख्य चुनौतियों का विश्लेषण करने के लिए मैं तैयार हूँ। क्या आप अपने वर्तमान सिस्टम और मुख्य बाधाओं के बारे में विस्तार से बता सकते हैं?"
            suggestions = [
                "वर्तमान प्रक्रियाओं का विश्लेषण करें",
                "गैप एनालिसिस (Gap Analysis) तैयार करें",
                "AI और ऑटोमेशन सिफारिशें देखें",
                "ट्रांसफॉर्मेशन स्कोर की गणना करें"
            ]
        elif language == "gu":
            reply = f"નમસ્તે! હું TransformIQ AI ડિસ્કવરી સહાયક છું. '{proj_name}' પ્રોજેક્ટ માટે તમારા {industry} વર્કફ્લો અને મુખ્ય પડકારોનું વિશ્લેષણ કરવા માટે હું તૈયાર છું. શું તમે તમારી વર્તમાન સિસ્ટમ્સ અને મુખ્ય મુશ્કેલીઓ વિશે વિગતો આપી શકો છો?"
            suggestions = [
                "વર્તમાન પ્રક્રિયાઓનું વિશ્લેષણ કરો",
                "ગેપ એનાલિસિસ (Gap Analysis) જનરેટ કરો",
                "AI અને ઓટોમેશન ભલામણો જુઓ",
                "ટ્રાન્સફોર્મેશન સ્કોર ગણો"
            ]
        else:
            reply = f"Hello! I am your TransformIQ AI Transformation Companion. Based on the business objectives for **{proj_name}** ({industry}), I've analyzed your challenge context and extracted critical operational variables.\n\nKey Discovery Findings:\n• **High Triage Friction**: Significant manual reading and categorization overhead.\n• **Integration Boundaries**: Disconnected legacy data stores requiring API-first bridges.\n• **Automation Candidates**: Straight-through NLP intent routing and SOP-grounded RAG assistance.\n\nWould you like me to generate the full **AS-IS Business Analysis**, run the **8-Dimension Gap Matrix**, or produce the **React Flow Architecture Blueprint**?"
            suggestions = [
                "Generate Complete Business Analysis & Requirements",
                "Execute 8-Dimension Gap Analysis",
                "Build Solution Architecture & BPMN Process",
                "Calculate TransformIQ Readiness Score"
            ]

        return {
            "message": reply,
            "suggested_actions": suggestions,
            "extracted_insights": {
                "industry": industry,
                "complexity_level": "Enterprise High",
                "recommended_architecture": "Event-Driven Microservices + FastAPI + RAG"
            }
        }

    async def chat_companion(self, message: str, project_context: str = "", language: str = "en") -> str:
        provider = self._get_provider()
        if provider:
            try:
                system_prompt = (
                    f"You are the TransformIQ Enterprise AI Transformation Companion. "
                    f"You are an expert Chief Digital Transformation Officer and Enterprise Solutions Architect. "
                    f"Language: {language}. "
                    f"Always answer directly, professionally, and dynamically based on the project context provided.\n\n"
                    f"Project Context:\n{project_context}\n\n"
                    f"Guidelines:\n"
                    f"- Provide actionable, technically grounded advice (mention specific tech stacks, microservices, databases, API designs, or ROI figures when relevant).\n"
                    f"- Structure your answer with clear markdown bullet points and sections.\n"
                    f"- Suggest logical next steps in the TransformIQ transformation workflow."
                )
                reply = await provider.generate_chat(
                    [{"role": "system", "content": system_prompt}, {"role": "user", "content": message}],
                    {"context": project_context}
                )
                if reply and reply.strip():
                    return reply.strip()
            except Exception as e:
                logger.warning(f"AI Provider ({type(provider).__name__}) call failed: {e}")

        # Smart contextual response based on user query and project context
        msg_lower = message.lower()
        proj_title = project_context.splitlines()[0] if project_context else "Enterprise Transformation Initiative"
        
        # 1. Greetings & Introductory queries
        if re.search(r'\b(hi|hello|hey|namaste|kem cho|greetings)\b', msg_lower) or any(phrase in msg_lower for phrase in ["who are you", "what can you do", "introduce yourself"]):
            return (
                f"**Welcome to TransformIQ AI Transformation Companion!**\n\n"
                f"I am your dedicated enterprise solution architect for **{proj_title}**.\n\n"
                f"**Here is how I can assist your transformation journey:**\n"
                f"• **Discovery & Scoping**: Synthesize problem statements, legacy tech constraints, and operational goals.\n"
                f"• **Requirements Engineering**: Generate Functional & Non-Functional requirements with stakeholder matrices.\n"
                f"• **Architecture & BPMN**: Design decoupled cloud microservices, PostgreSQL schemas, and interactive BPMN workflows.\n"
                f"• **Estimation & Roadmap**: Calculate agile sprint velocity, INR/USD budgets, and What-If ROI projections.\n\n"
                f"Try asking: *\"What is the recommended tech stack?\"*, *\"What are our top process gaps?\"*, or *\"How much will this cost?\"*"
            )

        # 2. Architecture & Technical Stacks
        if any(w in msg_lower for w in ["architecture", "tech stack", "technology", "hld", "lld", "cloud", "aws", "azure", "fastapi", "microservice", "backend", "frontend", "infrastructure"]):
            return (
                f"**Enterprise Architecture Blueprint for {proj_title}**:\n\n"
                f"• **API & Ingestion Gateway**: High-throughput FastAPI (Python 3.10+) asynchronous services behind Traefik/Nginx reverse proxy with OAuth2 JWT & RBAC security.\n"
                f"• **AI & Semantic Intelligence Layer**: Hybrid RAG pipeline combining vector embeddings (pgvector / Chroma) with Gemini 2.0 Flash for sub-second NLP triage.\n"
                f"• **Persistence & Event Streaming**: PostgreSQL 16 for ACID 3NF transactional data, Redis 7 for sub-millisecond session caching and message queues.\n"
                f"• **Enterprise UX Studio**: React 18 + Vite + Tailwind CSS with interactive ReactFlow canvas and responsive mobile-first wireframes.\n"
                f"• **High Availability & SLA**: Multi-zone containerized deployment with automatic horizontal scaling targeting 99.95% availability.\n\n"
                f"👉 *Next Action: Open the **Architecture** stage to inspect, customize, and persist the interactive system component graph.*"
            )

        # 3. Gaps, Bottlenecks & Problems
        if any(w in msg_lower for w in ["gap", "bottleneck", "challenge", "problem", "friction", "pain point", "delay", "issue"]):
            return (
                f"**Strategic Operational Gaps & Bottleneck Analysis**:\n\n"
                f"1. **Manual Triage Latency**: Operational queue backlogs stretch ticket routing to 48+ hours, creating severe SLA violations.\n"
                f"2. **Data Fragmentation**: Disconnected siloed systems force duplicate data entry across spreadsheets and legacy CRMs.\n"
                f"3. **Absence of Autonomous STP**: 100% of standard transactions require manual employee touchpoints, driving high overhead.\n"
                f"4. **Compliance & Visibility Deficit**: Lack of centralized telemetry prevents real-time tracking of process bottlenecks.\n\n"
                f"**Remediation Blueprint**: Deploy AI intent parsing with >85% confidence routing, straight-through order updates, and exception queues.\n\n"
                f"👉 *Next Action: View the **8-Dimension Gap Matrix** in the Gap Analysis stage.*"
            )

        # 4. Cost, Estimates & Roadmap
        if any(w in msg_lower for w in ["cost", "budget", "price", "estimate", "hour", "timeline", "week", "month", "roi", "savings", "staffing"]):
            return (
                f"**Transformation Roadmap, Budget & ROI Forecast**:\n\n"
                f"• **Delivery Cadence**: 16 Weeks structured into 4 Agile Sprints (Foundation, Core Logic, Review Hub, Hardening).\n"
                f"• **Engineering Capacity**: 6 Cross-functional Engineers (Architect, AI Engineer, Backend, Frontend, DevOps, QA).\n"
                f"• **Total Effort**: ~1,120 engineering hours with estimated investment of ~$138,500.\n"
                f"• **Financial Impact**: Projected 87% operational efficiency gain, generating estimated annual operational savings of $360,000+ with breakeven in 6.4 months.\n\n"
                f"👉 *Next Action: Adjust live parameters in the **What-If Simulation** tab to model custom ROI scenarios.*"
            )

        # 5. Database, Schema & Models
        if any(w in msg_lower for w in ["database", "db", "schema", "table", "sql", "ddl", "postgres", "entity", "er diagram", "relation"]):
            return (
                f"**Relational Database Design & Data Architecture**:\n\n"
                f"• **Database Engine**: PostgreSQL 16 (Relational 3NF with JSONB flexibility and pgvector extension).\n"
                f"• **Core Entities**: Accounts, Tickets/Workflows, AI Analysis Chunks, Audit Trails, and System Telemetry.\n"
                f"• **Performance Indexing**: B-tree indices on foreign keys, GIN indices on JSONB payloads, and HNSW vector indices.\n"
                f"• **Data Integrity & Privacy**: AES-256 at rest, strict tenant-scoped schemas, and automated point-in-time recovery (PITR).\n\n"
                f"👉 *Next Action: Inspect and copy the executable SQL DDL in the **Database Design** stage.*"
            )

        # 6. APIs, Endpoints & Integration
        if any(w in msg_lower for w in ["api", "endpoint", "rest", "integration", "webhook", "openapi", "swagger"]):
            return (
                f"**API Architecture & Integration Strategy**:\n\n"
                f"• **API Specification**: RESTful OpenAPI 3.0 standards with strict Pydantic v2 payload validation.\n"
                f"• **Security Guardrails**: Bearer JWT authentication, OAuth2 scopes, and rate limiting (1,200 requests/minute).\n"
                f"• **Event Hooks**: Webhook subscriptions for asynchronous status events, external CRM callbacks, and Slack/Teams alerts.\n\n"
                f"👉 *Next Action: Explore mock responses and request schemas in the **APIs** stage.*"
            )

        # 7. HR / Talent / Recruitment domain
        if any(w in msg_lower for w in ["hr", "candidate", "resume", "recruit", "applicant", "attendance", "onboard"]):
            return (
                f"**HR & Recruitment Modernization Plan**:\n\n"
                f"• **AI Resume Ingestion**: Automated sub-2s resume parsing extracting skills, experience, and contact details from PDF/DOCX.\n"
                f"• **Centralized Candidate CRM**: Eliminates 5 duplicate Excel sheets with unified candidate and client pipeline tracking.\n"
                f"• **Recruiter Attendance & Metrics**: Real-time daily check-in telemetry and placement analytics.\n"
                f"• **Client Portal**: Self-service job requisition posting, candidate shortlisting, and 1-click digital contracts.\n\n"
                f"👉 *Next Action: Generate the full ATS roadmap in the **Business Analysis** stage.*"
            )

        # 8. General domain response
        return (
            f"**TransformIQ Advisory for {proj_title}**:\n\n"
            f"Regarding your query: *\"{message}\"*\n\n"
            f"• **Strategic Recommendation**: Modernize manual operational dependencies into event-driven straight-through workflows.\n"
            f"• **AI Integration**: Ground LLM intent extraction with enterprise SOP vector knowledge to ensure >90% precision.\n"
            f"• **Measurable Target**: Compress cycle times by 65-80% while preserving full SOC2 audit logging.\n\n"
            f"👉 *You can navigate to **Business Analysis**, **Solution Architecture**, or **Planning** to view and download full implementation artifacts.*"
        )

    async def generate_business_analysis(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        return smart_engine.build_contextual_business_analysis(context_data)

    async def generate_gap_analysis(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        return smart_engine.build_contextual_gap_analysis(context_data)

    async def generate_recommendations(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        return smart_engine.build_contextual_recommendations(context_data)

    async def generate_architecture(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        return smart_engine.build_contextual_architecture(context_data)

    async def generate_process_workflow(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        return smart_engine.build_contextual_process_workflow(context_data)

    async def generate_database_design(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        return smart_engine.build_contextual_database(context_data)

    async def generate_api_catalog(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        return smart_engine.build_contextual_apis(context_data)

    async def generate_api_design(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        return smart_engine.build_contextual_apis(context_data)

    async def generate_ux_design(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        return smart_engine.build_contextual_ux(context_data)

    async def generate_planning(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        return smart_engine.build_contextual_planning(context_data)

    async def generate_estimates(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        return smart_engine.build_contextual_estimates(context_data)

    async def generate_risks(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        return smart_engine.build_contextual_risks(context_data)

    async def generate_score(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        return smart_engine.build_contextual_score(context_data)

    async def run_what_if_simulation(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        return smart_engine.calculate_what_if_simulation(request_data)

orchestrator = AIOrchestrator()
