"use client";
import "@/css/satoshi.css";
import "@/css/style.css";
import "jsvectormap/dist/jsvectormap.css";
import "flatpickr/dist/flatpickr.min.css";
import React, { useEffect, useState } from "react";
import Loader from "@/components/common/Loader";
import { TranscriptionProvider } from '@/utils/transcriptionContext';
import { HumanEvaluationProvider } from '@/utils/humanEvalContext';

import "./globals.css";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const [loading, setLoading] = useState<boolean>(true);

  // const pathname = usePathname();

  useEffect(() => {
    setTimeout(() => setLoading(false), 1000);
  }, []);

  return (
    <TranscriptionProvider>
      <HumanEvaluationProvider>
        <html lang="en">
          <body>
            <a
              href="#main-content"
              className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-[10000] focus:rounded-md focus:bg-white focus:px-3 focus:py-2 focus:text-sm focus:font-medium focus:text-black"
            >
              Skip to main content
            </a>
            <div id="root" className="dark:bg-boxdark-2 dark:text-bodydark">
              {loading ? <Loader /> : children}
            </div>
          </body>
        </html>
      </HumanEvaluationProvider>
    </TranscriptionProvider>
  );
}
