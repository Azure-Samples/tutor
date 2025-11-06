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
  const [sidebarOpen, setSidebarOpen] = useState(false);
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
            <div id="#root" className="dark:bg-boxdark-2 dark:text-bodydark">
              {loading ? <Loader /> : children}
            </div>
          </body>
        </html>
      </HumanEvaluationProvider>
    </TranscriptionProvider>
  );
}
