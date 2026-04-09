import "@/css/satoshi.css";
import "@/css/style.css";
import "jsvectormap/dist/jsvectormap.css";
import "flatpickr/dist/flatpickr.min.css";
import { WorkspaceProvider } from "@/components/Workspace/WorkspaceProvider";
import { HumanEvaluationProvider } from "@/utils/humanEvalContext";
import { TranscriptionProvider } from "@/utils/transcriptionContext";
import type React from "react";

import "./globals.css";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <a
          href="#main-content"
          className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-[10000] focus:rounded-md focus:bg-white focus:px-3 focus:py-2 focus:text-sm focus:font-medium focus:text-black"
        >
          Skip to main content
        </a>
        <TranscriptionProvider>
          <HumanEvaluationProvider>
            <WorkspaceProvider>
              <div id="root" className="min-h-screen dark:text-bodydark">
                {children}
              </div>
            </WorkspaceProvider>
          </HumanEvaluationProvider>
        </TranscriptionProvider>
      </body>
    </html>
  );
}
