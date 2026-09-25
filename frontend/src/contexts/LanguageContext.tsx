import React, { createContext, useContext, useState, useEffect } from 'react';
import enDict from '../locales/en.json';
import hiDict from '../locales/hi.json';
import guDict from '../locales/gu.json';
import { extraTranslations } from '../config/translations';

export type Language = 'en' | 'hi' | 'gu';

const localeMap: Record<Language, Record<string, string>> = {
  en: enDict,
  hi: hiDict,
  gu: guDict
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
    if (!key) return defaultText || '';

    // 1. Direct key match in locale JSON
    const dict = localeMap[language] || localeMap.en;
    if (dict[key]) {
      return dict[key];
    }

    // 2. Normalized snake_case key match
    const cleanKey = key.toLowerCase().replace(/\s+/g, '_').replace(/[^a-z0-9_]/g, '');
    if (dict[cleanKey]) {
      return dict[cleanKey];
    }

    // 3. Match from extraTranslations dictionary
    if (extraTranslations[cleanKey] && extraTranslations[cleanKey][language]) {
      return extraTranslations[cleanKey][language];
    }
    if (extraTranslations[key] && extraTranslations[key][language]) {
      return extraTranslations[key][language];
    }

    // 4. Check defaultText in translations
    if (defaultText) {
      const cleanDefault = defaultText.toLowerCase().replace(/\s+/g, '_').replace(/[^a-z0-9_]/g, '');
      if (dict[cleanDefault]) {
        return dict[cleanDefault];
      }
      if (extraTranslations[cleanDefault] && extraTranslations[cleanDefault][language]) {
        return extraTranslations[cleanDefault][language];
      }
      return defaultText;
    }

    return key;
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => useContext(LanguageContext);
