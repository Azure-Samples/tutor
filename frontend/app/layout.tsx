import "@/css/style.css";
import "jsvectormap/dist/jsvectormap.css";
import "flatpickr/dist/flatpickr.min.css";
import LocalizedSkipLink from "@/components/I18n/LocalizedSkipLink";
import { LocaleProvider } from "@/components/I18n/LocaleProvider";
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
        <LocaleProvider>
          <LocalizedSkipLink />
          <TranscriptionProvider>
            <HumanEvaluationProvider>
              <WorkspaceProvider>
                <div id="root" className="min-h-screen text-slate-900 dark:text-slate-100">
                  {children}
                </div>
              </WorkspaceProvider>
            </HumanEvaluationProvider>
          </TranscriptionProvider>
        </LocaleProvider>
      </body>
    </html>
  );
}
