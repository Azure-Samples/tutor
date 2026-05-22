"use client";

import { useI18n } from "@/components/I18n/LocaleProvider";
import type { Locale } from "@/utils/i18n";
import { useId } from "react";
import { FiGlobe } from "react-icons/fi";

const LanguageSwitcher = () => {
  const id = useId();
  const { dictionary, locale, setLocale, supportedLocales } = useI18n();

  return (
    <div className="flex items-center gap-2 rounded-full border border-stone-200 bg-white px-3 py-2 text-slate-700 shadow-sm dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200">
      <FiGlobe aria-hidden="true" className="h-4 w-4 shrink-0" />
      <label htmlFor={id} className="sr-only">
        {dictionary.language.label}
      </label>
      <select
        id={id}
        aria-label={dictionary.language.label}
        title={dictionary.language.title}
        value={locale}
        onChange={(event) => setLocale(event.target.value as Locale)}
        className="max-w-[7.5rem] bg-transparent text-sm font-semibold outline-none focus-visible:ring-2 focus-visible:ring-teal-700 focus-visible:ring-offset-2 dark:bg-slate-900"
      >
        {supportedLocales.map((metadata) => (
          <option key={metadata.code} value={metadata.code}>
            {metadata.nativeName}
          </option>
        ))}
      </select>
    </div>
  );
};

export default LanguageSwitcher;