export type Language = 'en' | 'hi' | 'gu';

export interface TranslationEntry {
  en: string;
  hi: string;
  gu: string;
}

export type TranslationDictionary = Record<string, TranslationEntry>;

export const extraTranslations: TranslationDictionary = {
  // --- Admin Portal & Governance ---
  "enterprise_administration__governance": {
    en: "Enterprise Administration & Governance",
    hi: "एंटरप्राइज प्रशासन और शासन",
    gu: "એન્ટરપ્રાઇઝ વહીવટ અને શાસન"
  },
  "platform_control_center": {
    en: "Chaos2Commit 2026 Platform Control Center • Centralized RBAC, Multi-Tenant Hierarchy & AI Telemetry",
    hi: "Chaos2Commit 2026 प्लेटफॉर्म नियंत्रण केंद्र • केंद्रीकृत RBAC, बहु-किराएदार पदानुक्रम और AI टेलीमेट्री",
    gu: "Chaos2Commit 2026 પ્લેટફોર્મ નિયંત્રણ કેન્દ્ર • કેન્દ્રીયકૃત RBAC, બહુ-ટેનન્ટ પદાનુક્રમ અને AI ટેલિમેટ્રી"
  },
  "total_users": {
    en: "Total Users",
    hi: "कुल उपयोगकर्ता",
    gu: "કુલ વપરાશકર્તાઓ"
  },
  "all_7_roles_active": {
    en: "All 7 Roles Active",
    hi: "सभी 7 भूमिकाएं सक्रिय",
    gu: "તમામ 7 ભૂમિકાઓ સક્રિય"
  },
  "organizations": {
    en: "Organizations",
    hi: "संगठन",
    gu: "સંસ્થાઓ"
  },
  "multi_tenant_scoped": {
    en: "Multi-Tenant Scoped",
    hi: "मल्टी-टेनेंट स्कोप्ड",
    gu: "મલ્ટિ-ટેનન્ટ સ્કોપ્ડ"
  },
  "initiatives": {
    en: "Initiatives",
    hi: "पहल / परियोजनाएं",
    gu: "પહેલ / પ્રોજેક્ટ્સ"
  },
  "13_pipeline_stages": {
    en: "13 Pipeline Stages",
    hi: "13 पाइपलाइन चरण",
    gu: "13 પાઇપલાઇન તબક્કા"
  },
  "ai_invocations": {
    en: "AI Invocations",
    hi: "एआई कॉल / उपयोग",
    gu: "એઆઈ કૉલ્સ / વપરાશ"
  },
  "mtd_spend": {
    en: "MTD Spend",
    hi: "इस महीने का खर्च",
    gu: "આ મહિનાનો ખર્ચ"
  },
  "security__rbac_enforcement_status": {
    en: "Security & RBAC Enforcement Status",
    hi: "सुरक्षा और आरबीएसी प्रवर्तन स्थिति",
    gu: "સુરક્ષા અને RBAC અમલીકરણ સ્થિતિ"
  },
  "tenant_isolation_policy": {
    en: "Tenant Isolation Policy",
    hi: "किराएदार अलगाव नीति",
    gu: "ટેનન્ટ અલગતા નીતિ"
  },
  "data_encryption_standard": {
    en: "Data Encryption Standard",
    hi: "डेटा एन्क्रिप्शन मानक",
    gu: "ડેટા એન્ક્રિપ્શન માનક"
  },
  "vector_search_engine": {
    en: "Vector Search Engine",
    hi: "वेक्टर खोज इंजन",
    gu: "વેક્ટર સર્ચ એન્જિન"
  },
  "immutable_audit_logging": {
    en: "Immutable Audit Logging",
    hi: "अपरिवर्तनीय ऑडिट लॉगिंग",
    gu: "અપરિવર્તનીય ઓડિટ લોગીંગ"
  },
  "quick_administration_workflows": {
    en: "Quick Administration Workflows",
    hi: "त्वरित प्रशासनिक कार्यप्रवाह",
    gu: "ઝડપી વહીવટી વર્કફ્લો"
  },
  "manage_users": {
    en: "Manage Users",
    hi: "उपयोगकर्ता प्रबंधित करें",
    gu: "વપરાશકર્તાઓ સંચાલિત કરો"
  },
  "assign_roles__status": {
    en: "Assign roles & status",
    hi: "भूमिकाएं और स्थिति असाइन करें",
    gu: "ભૂમિકાઓ અને સ્થિતિ સોંપો"
  },
  "organization": {
    en: "Organization",
    hi: "संगठन प्रोफाइल",
    gu: "સંસ્થા પ્રોફાઇલ"
  },
  "profile__compliance": {
    en: "Profile & compliance",
    hi: "प्रोफ़ाइल और अनुपालन",
    gu: "પ્રોફાઇલ અને અનુપાલન"
  },
  "ai_token_telemetry": {
    en: "AI Token Telemetry",
    hi: "एआई टोकन टेलीमेट्री",
    gu: "એઆઈ ટોકન ટેલિમેટ્રી"
  },
  "monitor_model_spend": {
    en: "Monitor model spend",
    hi: "मॉडल खर्च की निगरानी करें",
    gu: "મોડેલ ખર્ચની દેખરેખ રાખો"
  },
  "audit_trail": {
    en: "Audit Trail",
    hi: "ऑडिट ट्रेल",
    gu: "ઓડિટ ટ્રેઇલ"
  },
  "review_security_logs": {
    en: "Review security logs",
    hi: "सुरक्षा लॉग की समीक्षा करें",
    gu: "સુરક્ષા લોગની સમીક્ષા કરો"
  },
  "recent_platform_governance_events": {
    en: "Recent Platform Governance Events",
    hi: "हालिया प्लेटफॉर्म गवर्नेंस ईवेंट्स",
    gu: "તાજેતરના પ્લેટફોર્મ ગવર્નન્સ ઇવેન્ટ્સ"
  },
  "view_full_audit_log": {
    en: "View Full Audit Log",
    hi: "पूरा ऑडिट लॉग देखें",
    gu: "સંપૂર્ણ ઓડિટ લોગ જુઓ"
  },
  "platform_status_healthy": {
    en: "Platform Status: Healthy (99.98%)",
    hi: "प्लेटफॉर्म स्थिति: स्वस्थ (99.98%)",
    gu: "પ્લેટફોર્મ સ્થિતિ: હેલ્ધી (99.98%)"
  },
  "sync": {
    en: "Sync",
    hi: "सिंक करें",
    gu: "સિંક કરો"
  },

  // --- Dashboard & Role Perspectives ---
  "transformation_portfolio": {
    en: "Transformation Portfolio",
    hi: "रूपांतरण पोर्टफोलियो",
    gu: "રૂપાંતરણ પોર્ટફોલિયો"
  },
  "manage_and_launch_initiatives": {
    en: "Manage and launch AI-driven enterprise transformation initiatives.",
    hi: "एआई-संचालित एंटरप्राइज रूपांतरण पहलों का प्रबंधन और शुभारंभ करें।",
    gu: "એઆઈ-સંચાલિત એન્ટરપ્રાઇઝ રૂપાંતરણ પહેલોનું સંચાલન અને શુભારંભ કરો."
  },
  "budget": {
    en: "Budget",
    hi: "बजट",
    gu: "બજેટ"
  },
  "timeline": {
    en: "Timeline",
    hi: "समय-सीमा",
    gu: "સમયમર્યાદા"
  },
  "months": {
    en: "Months",
    hi: "महीने",
    gu: "મહિના"
  },
  "ai_discovery": {
    en: "AI Discovery",
    hi: "एआई खोज",
    gu: "એઆઈ શોધ"
  },
  "view_all_projects": {
    en: "View All Projects",
    hi: "सभी परियोजनाएं देखें",
    gu: "બધા પ્રોજેક્ટ્સ જુઓ"
  },
  "avg_transformation_score": {
    en: "Avg Transformation Score",
    hi: "औसत रूपांतरण स्कोर",
    gu: "સરેરાશ ટ્રાન્સફોર્મેશન સ્કોર"
  },
  "ai_readiness": {
    en: "AI Readiness",
    hi: "एआई तत्परता",
    gu: "એઆઈ સજ્જતા"
  },
  "automation_potential": {
    en: "Automation Potential",
    hi: "स्वचालन क्षमता",
    gu: "ઓટોમેશન ક્ષમતા"
  },
  "delivery_readiness": {
    en: "Delivery Readiness",
    hi: "वितरण तत्परता",
    gu: "ડિલિવરી સજ્જતા"
  },
  "projects_at_risk": {
    en: "Projects At Risk",
    hi: "जोखिम में परियोजनाएं",
    gu: "જોખમમાં પ્રોજેક્ટ્સ"
  },
  "readiness_assessment": {
    en: "TransformIQ Readiness Assessment (6 Dimensions)",
    hi: "ट्रांसफॉर्म आईक्यू तत्परता मूल्यांकन (6 आयाम)",
    gu: "ટ્રાન્સફોર્મ આઈક્યુ સજ્જતા મૂલ્યાંકન (6 પરિમાણો)"
  },
  "cycle_time_reduction": {
    en: "Cycle Time Reduction: AS-IS vs TO-BE (Hours)",
    hi: "चक्र समय में कमी: AS-IS बनाम TO-BE (घंटे)",
    gu: "સાયકલ સમયમાં ઘટાડો: AS-IS વિ TO-BE (કલાકો)"
  },

  // --- Common Buttons & Controls ---
  "save_changes": {
    en: "Save Changes",
    hi: "बदलाव सहेजें",
    gu: "ફેરફારો સાચવો"
  },
  "cancel": {
    en: "Cancel",
    hi: "रद्द करें",
    gu: "રદ કરો"
  },
  "edit_settings": {
    en: "Edit Settings",
    hi: "सेटिंग्स संपादित करें",
    gu: "સેટિંગ્સ સંપાદિત કરો"
  },
  "add_user": {
    en: "Add User",
    hi: "उपयोगकर्ता जोड़ें",
    gu: "વપરાશકર્તા ઉમેરો"
  },
  "filter": {
    en: "Filter",
    hi: "फ़िल्टर",
    gu: "ફિલ્ટર"
  },
  "search": {
    en: "Search",
    hi: "खोजें",
    gu: "શોધો"
  },
  "actions": {
    en: "Actions",
    hi: "कार्रवाई",
    gu: "ક્રિયાઓ"
  },
  "status": {
    en: "Status",
    hi: "स्थिति",
    gu: "સ્થિતિ"
  },

  // --- Role Perspective Banners ---
  "platform_administration__governance_center": {
    en: "Platform Administration & Governance Center",
    hi: "प्लेटफॉर्म प्रशासन और शासन केंद्र",
    gu: "પ્લેટફોર્મ વહીવટ અને શાસન કેન્દ્ર"
  },
  "transformation_executive_portfolio": {
    en: "Transformation Executive Portfolio",
    hi: "रूपांतरण कार्यकारी पोर्टफोलियो",
    gu: "ટ્રાન્સફોર્મેશન એક્ઝિક્યુટિવ પોર્ટફોલિયો"
  },
  "business_analysis__requirements_hub": {
    en: "Business Analysis & Requirements Hub",
    hi: "व्यावसायिक विश्लेषण और आवश्यकताएं केंद्र",
    gu: "વ્યવસાય વિશ્લેષણ અને જરૂરિયાતો કેન્દ્ર"
  },
  "solution_architecture__technical_design_hub": {
    en: "Solution Architecture & Technical Design Hub",
    hi: "समाधान वास्तुकला और तकनीकी डिजाइन केंद्र",
    gu: "સોલ્યુશન આર્કિટેક્ચર અને ટેકનિકલ ડિઝાઇન કેન્દ્ર"
  },
  "executive_decision__governance_dashboard": {
    en: "Executive Decision & Governance Dashboard",
    hi: "कार्यकारी निर्णय और शासन डैशबोर्ड",
    gu: "એક્ઝિક્યુટિવ નિર્ણય અને શાસન ડેશબોર્ડ"
  },
  "transformation_team_collaboration_workspace": {
    en: "Transformation Team Collaboration Workspace",
    hi: "रूपांतरण टीम सहयोग कार्यक्षेत्र",
    gu: "ટ્રાન્સફોર્મેશન ટીમ સહયોગ કાર્યક્ષેત્ર"
  },
  "stakeholder_read_only_transformation_overview": {
    en: "Stakeholder Read-Only Transformation Overview",
    hi: "हितधारक केवल-पठन रूपांतरण अवलोकन",
    gu: "સ્ટેકહોલ્ડર રીડ-ઓન્લી ટ્રાન્સફોર્મેશન વિહંગાવલોકન"
  },

  // --- Workspaces & Projects Tabs ---
  "enterprise_workspaces_directory": {
    en: "Enterprise Workspaces Directory",
    hi: "एंटरप्राइज कार्यक्षेत्र निर्देशिका",
    gu: "એન્ટરપ્રાઇઝ કાર્યક્ષેત્ર ડિરેક્ટરી"
  },
  "hierarchical_groupings_of_transformation_initiatives": {
    en: "Hierarchical groupings of transformation initiatives within organization.",
    hi: "संगठन के भीतर रूपांतरण पहलों का पदानुक्रमित समूहन।",
    gu: "સંસ્થાની અંદર રૂપાંતરણ પહેલોનું પદાનુક્રમિત જૂથીકરણ."
  },
  "main_transformation_workspace": {
    en: "Main Transformation Workspace",
    hi: "मुख्य रूपांतरण कार्यक्षेत्र",
    gu: "મુખ્ય ટ્રાન્સફોર્મેશન કાર્યક્ષેત્ર"
  },
  "customer_experience_transformation": {
    en: "Customer Experience Transformation",
    hi: "ग्राहक अनुभव रूपांतरण",
    gu: "ગ્રાહક અનુભવ ટ્રાન્સફોર્મેશન"
  },
  "default_workspace_for_enterprise_initiatives": {
    en: "Default workspace for enterprise initiatives",
    hi: "एंटरप्राइज पहलों के लिए डिफ़ॉल्ट कार्यक्षेत्र",
    gu: "એન્ટરપ્રાઇઝ પહેલો માટે ડિફોલ્ટ કાર્યક્ષેત્ર"
  },
  "ai_driven_customer_operations": {
    en: "AI-driven customer operations, complaints resolution, and intelligent triage.",
    hi: "एआई-संचालित ग्राहक संचालन, शिकायत निवारण और बुद्धिमान ट्राइएज।",
    gu: "એઆઈ-સંચાલિત ગ્રાહક કામગીરી, ફરીયાદ નિવારણ અને બુદ્ધિશાળી ટ્રાયજ."
  },
  "projects_colon": {
    en: "Projects:",
    hi: "परियोजनाएं:",
    gu: "પ્રોજેક્ટ્સ:"
  },
  "created_colon": {
    en: "Created:",
    hi: "निर्मित:",
    gu: "બનાવ્યાની તારીખ:"
  },
  "global_transformation_initiatives": {
    en: "Global Transformation Initiatives",
    hi: "वैश्विक रूपांतरण पहल",
    gu: "વૈશ્વિક ટ્રાન્સફોર્મેશન પહેલ"
  },
  "view_project": {
    en: "View Project",
    hi: "परियोजना देखें",
    gu: "પ્રોજેક્ટ જુઓ"
  },
  "new_transformation_initiative": {
    en: "New Transformation Initiative",
    hi: "नई रूपांतरण पहल",
    gu: "નવી ટ્રાન્સફોર્મેશન પહેલ"
  },
  "create_transformation_initiative": {
    en: "Create Transformation Initiative",
    hi: "रूपांतरण पहल बनाएं",
    gu: "ટ્રાન્સફોર્મેશન પહેલ બનાવો"
  },
  "project_name_star": {
    en: "Project Name *",
    hi: "परियोजना का नाम *",
    gu: "પ્રોજેક્ટનું નામ *"
  },
  "business_problem_description": {
    en: "Business Problem / Chaos Description *",
    hi: "व्यावसायिक समस्या / अराजकता विवरण *",
    gu: "વ્યવસાયિક સમસ્યા / અરાજકતા વિગત *"
  },
  "target_budget": {
    en: "Target Budget ($ USD)",
    hi: "लक्ष्य बजट ($ USD)",
    gu: "લક્ષ્ય બજેટ ($ USD)"
  },
  "timeline_months": {
    en: "Timeline (Months)",
    hi: "समय सीमा (महीने)",
    gu: "સમયમર્યાદા (મહિના)"
  },
  "upload_enterprise_document": {
    en: "Upload Enterprise Document (PDF, Word, PPTX, TXT)",
    hi: "एंटरप्राइज दस्तावेज़ अपलोड करें (PDF, Word, PPTX, TXT)",
    gu: "એન્ટરપ્રાઇઝ દસ્તાવેજ અપલોડ કરો (PDF, Word, PPTX, TXT)"
  },
  "reference_web_url": {
    en: "Reference Web / BRD URL (Website, Online Spec, Documentation)",
    hi: "संदर्भ वेब / बीआरडी यूआरएल (वेबसाइट, ऑनलाइन विशिष्टता, दस्तावेज)",
    gu: "સંદર્ભ વેબ / BRD URL (વેબસાઇટ, ઓનલાઇન સ્પેક, દસ્તાવેજીકરણ)"
  },
  "grounded_documents": {
    en: "Grounded Documents",
    hi: "सत्यापित / संदर्भित दस्तावेज",
    gu: "આધારભૂત દસ્તાવેજો"
  },
  "initialize_ai_discovery": {
    en: "Initialize AI Discovery",
    hi: "एआई खोज प्रारंभ करें",
    gu: "એઆઈ શોધ શરૂ કરો"
  },

  // --- Users & Roles Tabs ---
  "enterprise_user_directory": {
    en: "Enterprise User Directory & Role Assignment",
    hi: "एंटरप्राइज उपयोगकर्ता निर्देशिका और भूमिका असाइनमेंट",
    gu: "એન્ટરપ્રાઇઝ વપરાશકર્તા ડિરેક્ટરી અને ભૂમિકા સોંપણી"
  },
  "user": {
    en: "User",
    hi: "उपयोगकर्ता",
    gu: "વપરાશકર્તા"
  },
  "email": {
    en: "Email",
    hi: "ईमेल",
    gu: "ઇમેઇલ"
  },
  "current_role": {
    en: "Current Role",
    hi: "वर्तमान भूमिका",
    gu: "વર્તમાન ભૂમિકા"
  },
  "change_role": {
    en: "Change Role",
    hi: "भूमिका बदलें",
    gu: "ભૂમિકા બદલો"
  },
  "create_authorized_user": {
    en: "Create Authorized User",
    hi: "अधिकृत उपयोगकर्ता बनाएं",
    gu: "અધિકૃત વપરાશકર્તા બનાવો"
  },
  "full_name": {
    en: "Full Name",
    hi: "पूरा नाम",
    gu: "સંપૂર્ણ નામ"
  },
  "email_address": {
    en: "Email Address",
    hi: "ईमेल पता",
    gu: "ઇમેઇલ સરનામું"
  },
  "password": {
    en: "Password",
    hi: "पासवर्ड",
    gu: "પાસવર્ડ"
  },
  "assigned_role": {
    en: "Assigned Role",
    hi: "असाइन की गई भूमिका",
    gu: "સોંપાયેલ ભૂમિકા"
  },
  "create_account": {
    en: "Create Account",
    hi: "खाता बनाएं",
    gu: "ખાતું બનાવો"
  },
  "activate": {
    en: "Activate",
    hi: "सक्रिय करें",
    gu: "સક્રિય કરો"
  },
  "disable": {
    en: "Disable",
    hi: "अक्षम करें",
    gu: "નિષ્ક્રિય કરો"
  },
  "centralized_rbac_matrix": {
    en: "Centralized Role-Based Access Control (RBAC) Matrix",
    hi: "केंद्रीकृत भूमिका-आधारित पहुंच नियंत्रण (RBAC) मैट्रिक्स",
    gu: "કેન્દ્રીયકૃત ભૂમિકા-આધારિત ઍક્સેસ કંટ્રોલ (RBAC) મેટ્રિક્સ"
  },

  // --- Telemetry, Analytics, Audit & Settings Tabs ---
  "ai_token_telemetry_analytics": {
    en: "AI Token Telemetry & LLM Consumption Analytics",
    hi: "एआई टोकन टेलीमेट्री और एलएलएम खपत एनालिटिक्स",
    gu: "એઆઈ ટોકન ટેલિમેટ્રી અને LLM વપરાશ એનાલિટિક્સ"
  },
  "total_token_ingestion": {
    en: "Total Token Ingestion",
    hi: "कुल टोकन अंतर्ग्रहण",
    gu: "કુલ ટોકન વપરાશ"
  },
  "average_latency": {
    en: "Average Latency",
    hi: "औसत विलंबता (Latency)",
    gu: "સરેરાશ લેટન્સી (Latency)"
  },
  "configured_model_deployments": {
    en: "Configured Model Deployments",
    hi: "कॉन्फ़िगर किए गए मॉडल परिनियोजन",
    gu: "કોન્ફિગર કરેલ મોડેલ ડિપ્લોયમેન્ટ્સ"
  },
  "system_analytics_performance": {
    en: "System Analytics & Performance Metrics",
    hi: "सिस्टम एनालिटिक्स और प्रदर्शन मेट्रिक्स",
    gu: "સિસ્ટમ એનાલિટિક્સ અને પ્રદર્શન મેટ્રિક્સ"
  },
  "system_uptime": {
    en: "System Uptime",
    hi: "सिस्टम अपटाइम",
    gu: "સિસ્ટમ અપટાઇમ"
  },
  "p95_api_latency": {
    en: "p95 API Latency",
    hi: "p95 एपीआई विलंबता",
    gu: "p95 એપીઆઈ લેટન્સી"
  },
  "database_pool_health": {
    en: "Database Pool Health",
    hi: "डेटाबेस पूल स्वास्थ्य",
    gu: "ડેટાબેઝ પુલ હેલ્થ"
  },
  "rate_limit_headroom": {
    en: "Rate Limit Headroom",
    hi: "दर सीमा छूट",
    gu: "રેટ લિમિટ હેડરૂમ"
  },
  "immutable_security_audit_trail": {
    en: "Immutable Security & Governance Audit Trail",
    hi: "अपरिवर्तनीय सुरक्षा और शासन ऑडिट ट्रेल",
    gu: "અપરિવર્તનીય સુરક્ષા અને શાસન ઓડિટ ટ્રેઇલ"
  },
  "timestamp": {
    en: "Timestamp",
    hi: "समय-मुहर (Timestamp)",
    gu: "સમય-છાપ (Timestamp)"
  },
  "actor": {
    en: "Actor",
    hi: "उपयोगकर्ता / एजेंट",
    gu: "વપરાશકર્તા / એજન્ટ"
  },
  "action_event": {
    en: "Action Event",
    hi: "कार्रवाई घटना",
    gu: "ક્રિયા ઇવેન્ટ"
  },
  "details": {
    en: "Details",
    hi: "विवरण",
    gu: "વિગતો"
  },
  "ip_address": {
    en: "IP Address",
    hi: "आईपी पता",
    gu: "આઈપી સરનામું"
  },
  "enterprise_connectors_integrations": {
    en: "Enterprise Connectors & Service Integrations",
    hi: "एंटरप्राइज कनेक्टर्स और सेवा एकीकरण",
    gu: "એન્ટરપ્રાઇઝ કનેક્ટર્સ અને સેવા એકીકરણ"
  },
  "connected": {
    en: "Connected",
    hi: "कनेक्टेड",
    gu: "કનેક્ટેડ"
  },
  "system_configuration_security": {
    en: "System Configuration & Security Parameters",
    hi: "सिस्टम कॉन्फ़िगरेशन और सुरक्षा पैरामीटर",
    gu: "સિસ્ટમ કોન્ફિગરેશન અને સુરક્ષા પરિમાણો"
  },
  "security__authentication": {
    en: "Security & Authentication",
    hi: "सुरक्षा और प्रमाणीकरण",
    gu: "સુરક્ષા અને પ્રમાણીકરણ"
  },
  "ai_orchestrator_engine": {
    en: "AI Orchestrator Engine",
    hi: "एआई ऑर्केस्ट्रेटर इंजन",
    gu: "એઆઈ ઓર્કેસ્ટ્રેટર એન્જિન"
  },

  // --- Pipeline & Studio Pages ---
  "requirements__business_analysis": {
    en: "Requirements & Business Analysis",
    hi: "आवश्यकताएं और व्यावसायिक विश्लेषण",
    gu: "જરૂરિયાતો અને વ્યવસાય વિશ્લેષણ"
  },
  "8_dimension_gap_matrix": {
    en: "8-Dimension Gap Matrix",
    hi: "8-आयामी गैप मैट्रिक्स",
    gu: "8-પરિમાણીય ગેપ મેટ્રિક્સ"
  },
  "ai_recommendations_engine": {
    en: "AI Recommendations Engine",
    hi: "एआई सिफारिशें इंजन",
    gu: "એઆઈ ભલામણો એન્જિન"
  },
  "high_level_architecture": {
    en: "High Level Solution Architecture (HLD)",
    hi: "उच्च स्तरीय समाधान वास्तुकला (HLD)",
    gu: "હાઇ લેવલ સોલ્યુશન આર્કિટેક્ચર (HLD)"
  },
  "bpmn_process_workflows": {
    en: "BPMN Process Workflows & Automation",
    hi: "BPMN प्रक्रिया कार्यप्रवाह और स्वचालन",
    gu: "BPMN પ્રક્રિયા વર્કફ્લો અને ઓટોમેશન"
  },
  "database_schema_design": {
    en: "Database Schema & Entity Models",
    hi: "डेटाबेस स्कीमा और इकाई मॉडल",
    gu: "ડેટાબેઝ સ્કીમા અને એન્ટિટી મોડલ્સ"
  },
  "openapi_contracts_catalog": {
    en: "OpenAPI Contracts & Catalog",
    hi: "OpenAPI अनुबंध और कैटलॉग",
    gu: "OpenAPI કરારો અને કેટલોગ"
  },
  "ux_wireframes__personas": {
    en: "UX Wireframes & User Personas",
    hi: "यूएक्स वायरफ्रेम और उपयोगकर्ता व्यक्तित्व",
    gu: "યુએક્સ વાયરફ્રેમ્સ અને વપરાશકર્તા પર્સના"
  },
  "planning__estimation_roadmap": {
    en: "Planning & Estimation Roadmap",
    hi: "योजना और अनुमान रोडमैप",
    gu: "આયોજન અને અંદાજ રોડમેપ"
  },
  "scenario_simulation__roi": {
    en: "Scenario Simulation & ROI Analysis",
    hi: "परिदृश्य सिमुलेशन और आरओआई विश्लेषण",
    gu: "સિનારીયો સિમ્યુલેશન અને ROI વિશ્લેષણ"
  },
  "master_transformation_blueprint": {
    en: "Master Transformation Blueprint",
    hi: "मास्टर रूपांतरण ब्लूप्रिंट",
    gu: "માસ્ટર ટ્રાન્સફોર્મેશન બ્લુપ્રિન્ટ"
  }
};
