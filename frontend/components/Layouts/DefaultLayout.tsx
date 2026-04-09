"use client";
import Header from "@/components/Header";
import Sidebar from "@/components/Sidebar";
import type { Metadata } from "next";
import type React from "react";
import { useRef, useState } from "react";

export default function DefaultLayout({
  children,
  metadata,
  variant = "workspace",
}: {
  children: React.ReactNode;
  metadata?: Metadata;
  variant?: "workspace" | "public";
}) {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const sidebarSwitcherRef = useRef<HTMLButtonElement>(null);
  const isWorkspaceShell = variant === "workspace";

  return (
    <main id="main-content" className="min-h-screen text-slate-900 dark:text-slate-100">
      <div className="fixed left-0 top-0 z-50 w-full">
        <Header
          sidebarOpen={sidebarOpen}
          setSidebarOpen={setSidebarOpen}
          sidebarSwitcherRef={sidebarSwitcherRef}
          variant={variant}
        />
      </div>
      <div className="pt-[72px]">
        {isWorkspaceShell && (
          <Sidebar
            sidebarOpen={sidebarOpen}
            setSidebarOpen={setSidebarOpen}
            exceptionRef={sidebarSwitcherRef}
          />
        )}
        <div
          className={`min-h-[calc(100vh-72px)] transition-[margin] duration-200 ${
            isWorkspaceShell && sidebarOpen ? "lg:ml-[18rem]" : ""
          }`}
        >
          <div
            className={
              isWorkspaceShell
                ? "px-4 py-6 md:px-8 md:py-8"
                : "mx-auto max-w-7xl px-6 py-8 md:px-8 md:py-10"
            }
          >
            {children}
          </div>
        </div>
      </div>
    </main>
  );
}
