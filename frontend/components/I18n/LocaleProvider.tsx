"use client";

import {
  DEFAULT_LOCALE,
  LOCALE_METADATA,
  LOCALE_STORAGE_KEY,
  SUPPORTED_LOCALES,
  type AppDictionary,
  type Locale,
  type LocaleMetadata,
  getDictionary,
  normalizeLocale,
} from "@/utils/i18n";
import { type ReactNode, createContext, useContext, useEffect, useMemo, useState } from "react";

interface LocaleStore {
  locale: Locale;
  localeMetadata: LocaleMetadata;
  dictionary: AppDictionary;
  supportedLocales: LocaleMetadata[];
  setLocale: (locale: Locale) => void;
}

const LocaleContext = createContext<LocaleStore | null>(null);

function readStoredLocale(): Locale {
  if (typeof window === "undefined") {
    return DEFAULT_LOCALE;
  }

  try {
    return normalizeLocale(window.localStorage.getItem(LOCALE_STORAGE_KEY));
  } catch {
    return DEFAULT_LOCALE;
  }
}

export function LocaleProvider({ children }: { children: ReactNode }) {
  const [locale, setLocale] = useState<Locale>(DEFAULT_LOCALE);
  const [hasHydrated, setHasHydrated] = useState(false);

  useEffect(() => {
    setLocale(readStoredLocale());
    setHasHydrated(true);
  }, []);

  useEffect(() => {
    const metadata = LOCALE_METADATA[locale];

    document.documentElement.lang = metadata.htmlLang;
    document.documentElement.dir = metadata.direction;

    if (!hasHydrated) {
      return;
    }

    try {
      window.localStorage.setItem(LOCALE_STORAGE_KEY, locale);
    } catch {
      // Ignore storage failures; language selection still works for the current session.
    }
  }, [hasHydrated, locale]);

  const value = useMemo<LocaleStore>(
    () => ({
      locale,
      localeMetadata: LOCALE_METADATA[locale],
      dictionary: getDictionary(locale),
      supportedLocales: SUPPORTED_LOCALES.map((supportedLocale) => LOCALE_METADATA[supportedLocale]),
      setLocale,
    }),
    [locale],
  );

  return <LocaleContext.Provider value={value}>{children}</LocaleContext.Provider>;
}

export function useI18n() {
  const value = useContext(LocaleContext);

  if (!value) {
    throw new Error("useI18n must be used within LocaleProvider");
  }

  return value;
}