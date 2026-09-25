import React, { createContext, useContext, useState, useEffect } from 'react';
import { extraTranslations } from '../config/translations';

export type Language = 'en' | 'hi' | 'gu';

interface Translations {
  [key: string]: {
    [key in Language]: string;
  };
}

export const translations: Translations = {
  ...extraTranslations,
  // Brand & General
  app_name: {
    en: "TransformIQ",
    hi: "ट्रांसफॉर्म आईक्यू",
    gu: "ટ્રાન્સફોર્મ આઈક્યુ"
  },
  tagline: {
    en: "From Business Chaos to Implementation-Ready Solutions",
    hi: "व्यावसायिक अराजकता से कार्यान्वयन-योग्य समाधान तक",
    gu: "વ્યવસાયિક અરાજકતાથી અમલીકરણ-તૈયાર ઉકેલો સુધી"
  },

  // Main Navigation Modules
  dashboard: {
    en: "Dashboard",
    hi: "डैशबोर्ड",
    gu: "ડેશબોર્ડ"
  },
  projects: {
    en: "Projects",
    hi: "परियोजनाएं",
    gu: "પ્રોજેક્ટ્સ"
  },
  discovery: {
    en: "Discovery",
    hi: "एआई खोज",
    gu: "એઆઈ શોધ"
  },
  business_analysis: {
    en: "Business Analysis",
    hi: "व्यावसायिक विश्लेषण",
    gu: "વ્યવસાય વિશ્લેષણ"
  },
  gap_analysis: {
    en: "Gap Analysis",
    hi: "गैप विश्लेषण",
    gu: "ગેપ વિશ્લેષણ"
  },
  ai_recommendations: {
    en: "AI Recommendations",
    hi: "एआई सिफारिशें",
    gu: "એઆઈ ભલામણો"
  },
  solution_architecture: {
    en: "Architecture",
    hi: "आर्किटेक्चर",
    gu: "આર્કિટેક્ચર"
  },
  process_intelligence: {
    en: "Process",
    hi: "प्रक्रिया वर्कफ़्लो",
    gu: "પ્રક્રિયા વર્કફ્લો"
  },
  database_design: {
    en: "Database",
    hi: "डेटाबेस स्कीमा",
    gu: "ડેટાબેઝ સ્કીમા"
  },
  api_design: {
    en: "APIs",
    hi: "एपीआई कैटलॉग",
    gu: "એપીઆઈ કેટલોગ"
  },
  ux_design: {
    en: "UX Design",
    hi: "यूएक्स डिज़ाइन",
    gu: "યુએક્સ ડિઝાઇન"
  },
  planning: {
    en: "Planning",
    hi: "योजना और रोडमैप",
    gu: "આયોજન અને રોડમેપ"
  },
  simulation: {
    en: "Simulation",
    hi: "सिमुलेशन",
    gu: "સિમ્યુલેશન"
  },
  transformation_score: {
    en: "Transformation Score",
    hi: "रूपांतरण स्कोर",
    gu: "ટ્રાન્સફોર્મેશન સ્કોર"
  },
  final_blueprint: {
    en: "Master Blueprint",
    hi: "मास्टर ब्लूप्रिंट",
    gu: "માસ્ટર બ્લુપ્રિન્ટ"
  },
  collaboration: {
    en: "Collaboration & Logs",
    hi: "टीम सहयोग और लॉग्स",
    gu: "ટીમ સહયોગ અને લોગ્સ"
  },

  // Admin Modules
  admin_dashboard: {
    en: "Admin Dashboard",
    hi: "व्यवस्थापक डैशबोर्ड",
    gu: "એડમિન ડેશબોર્ડ"
  },
  admin_organization: {
    en: "Organization",
    hi: "संगठन सेटिंग्स",
    gu: "સંસ્થા સેટિંગ્સ"
  },
  admin_users: {
    en: "User Management",
    hi: "उपयोगकर्ता प्रबंधन",
    gu: "વપરાશકર્તા સંચાલન"
  },
  admin_roles: {
    en: "Roles & Permissions",
    hi: "भूमिकाएं और अनुमतियां",
    gu: "ભૂમિકાઓ અને પરવાનગીઓ"
  },
  admin_workspaces: {
    en: "Workspaces",
    hi: "कार्यक्षेत्र",
    gu: "કાર્યક્ષેત્ર"
  },
  admin_projects: {
    en: "Projects Control",
    hi: "परियोजना नियंत्रण",
    gu: "પ્રોજેક્ટ નિયંત્રણ"
  },
  admin_ai_usage: {
    en: "AI Usage & Telemetry",
    hi: "एआई उपयोग और मेट्रिक्स",
    gu: "એઆઈ વપરાશ અને મેટ્રિક્સ"
  },
  admin_analytics: {
    en: "System Analytics",
    hi: "सिस्टम एनालिटिक्स",
    gu: "સિસ્ટમ એનાલિટિક્સ"
  },
  admin_audit_logs: {
    en: "Audit Logs",
    hi: "ऑडिट लॉग्स",
    gu: "ઓડિટ લોગ્સ"
  },
  admin_integrations: {
    en: "Integrations",
    hi: "एकीकरण (Integrations)",
    gu: "એકીકરણ (Integrations)"
  },
  admin_settings: {
    en: "System Settings",
    hi: "सिस्टम सेटिंग्स",
    gu: "સિસ્ટમ સેટિંગ્સ"
  },

  // Common UI Actions & Headers
  create_project: {
    en: "Create Project",
    hi: "नई परियोजना बनाएं",
    gu: "નવો પ્રોજેક્ટ બનાવો"
  },
  transformation_workflow: {
    en: "Transformation Workflow",
    hi: "रूपांतरण कार्यप्रवाह",
    gu: "રૂપાંતરણ વર્કફ્લો"
  },
  governance: {
    en: "Governance & Control",
    hi: "शासन और नियंत्रण",
    gu: "શાસન અને નિયંત્રણ"
  },
  active: {
    en: "Active",
    hi: "सक्रिय",
    gu: "સક્રિય"
  },
  evaluation_mode: {
    en: "Evaluation Mode",
    hi: "मूल्यांकन मोड",
    gu: "મૂલ્યાંકન મોડ"
  },
  exit_evaluation: {
    en: "Exit Evaluation Mode",
    hi: "मूल्यांकन मोड से बाहर निकलें",
    gu: "મૂલ્યાંકન મોડમાંથી બહાર નીકળો"
  },
  sign_out: {
    en: "Sign Out",
    hi: "साइन आउट",
    gu: "સાઇન આઉટ"
  },
  sign_in: {
    en: "Sign In",
    hi: "साइन इन",
    gu: "સાઇન ઇન"
  },
  notifications: {
    en: "Notifications",
    hi: "सूचनाएं",
    gu: "સૂચનાઓ"
  },
  score: {
    en: "Score",
    hi: "स्कोर",
    gu: "સ્કોર"
  },
  export_pdf: {
    en: "Export PDF",
    hi: "पीडीएफ निर्यात करें",
    gu: "પીડીએફ એક્સપોર્ટ કરો"
  },
  approve_blueprint: {
    en: "Approve Blueprint",
    hi: "ब्लूप्रिंट स्वीकृत करें",
    gu: "બ્લુપ્રિન્ટ મંજૂર કરો"
  }
};

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string, defaultText?: string) => string;
}

const LanguageContext = createContext<LanguageContextType>({
  language: 'en',
  setLanguage: () => {},
  t: (key: string, defaultText?: string) => defaultText || key,
});

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [language, setLanguageState] = useState<Language>(() => {
    return (localStorage.getItem('transformiq_lang') as Language) || 'en';
  });

  const setLanguage = (lang: Language) => {
    setLanguageState(lang);
    localStorage.setItem('transformiq_lang', lang);
  };

  const t = (key: string, defaultText?: string): string => {
    const cleanKey = key.toLowerCase().replace(/\s+/g, '_').replace(/[^a-z0-9_]/g, '');
    if (translations[cleanKey] && translations[cleanKey][language]) {
      return translations[cleanKey][language];
    }
    if (translations[key] && translations[key][language]) {
      return translations[key][language];
    }
    if (defaultText) {
      const cleanDefault = defaultText.toLowerCase().replace(/\s+/g, '_').replace(/[^a-z0-9_]/g, '');
      if (translations[cleanDefault] && translations[cleanDefault][language]) {
        return translations[cleanDefault][language];
      }
    }
    return defaultText || key;
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => useContext(LanguageContext);
