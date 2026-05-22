"use client";

import { useI18n } from "@/components/I18n/LocaleProvider";

const LocalizedSkipLink = () => {
  const { dictionary } = useI18n();

  return (
    <a
      href="#main-content"
      className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-[10000] focus:rounded-md focus:bg-white focus:px-3 focus:py-2 focus:text-sm focus:font-medium focus:text-black"
    >
      {dictionary.layout.skipToMain}
    </a>
  );
};

export default LocalizedSkipLink;