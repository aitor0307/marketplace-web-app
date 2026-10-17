import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import { LANGUAGES, type LanguageCode } from '@/config/constants';
import en from '@/i18n/locales/en.json';
import es from '@/i18n/locales/es.json';

const LANGUAGE_KEY = 'marketplace.language';

function initialLanguage(): LanguageCode {
  try {
    const stored = localStorage.getItem(LANGUAGE_KEY);
    if (stored && (LANGUAGES as readonly string[]).includes(stored)) return stored as LanguageCode;
  } catch {
    // Storage unavailable: fall through to the browser language.
  }
  const browser = navigator.language.slice(0, 2);
  return (LANGUAGES as readonly string[]).includes(browser) ? (browser as LanguageCode) : 'en';
}

void i18n.use(initReactI18next).init({
  resources: {
    en: { translation: en },
    es: { translation: es },
  },
  lng: initialLanguage(),
  fallbackLng: 'en',
  interpolation: {
    escapeValue: false,
  },
});

i18n.on('languageChanged', (language) => {
  document.documentElement.lang = language;
  try {
    localStorage.setItem(LANGUAGE_KEY, language);
  } catch {
    // Not persisted; the choice still applies for this visit.
  }
});

export default i18n;
