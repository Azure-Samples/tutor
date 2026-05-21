"use client";
import Header from "@/components/Header";
import Sidebar, { type SidebarDisclosureState } from "@/components/Sidebar";
import type { Metadata } from "next";
import type React from "react";
import { useEffect, useRef, useState } from "react";

const WORKSPACE_SHELL_METRICS_CLASS =
  "[--workspace-header-offset:9.75rem] [--workspace-sidebar-width:15.5rem] sm:[--workspace-header-offset:8.75rem] lg:[--workspace-header-offset:4.5rem]";
const PUBLIC_SHELL_METRICS_CLASS = "[--workspace-header-offset:5rem]";
const DESKTOP_SIDEBAR_QUERY = "(min-width: 1024px)";

export default function DefaultLayout({
  children,
  metadata,
  variant = "workspace",
}: {
  children: React.ReactNode;
  metadata?: Metadata;
  variant?: "workspace" | "public";
}) {
  // No GoF pattern applies; this layout tracks simple responsive disclosure state.
  const [sidebarState, setSidebarState] = useState<SidebarDisclosureState>("responsive");
  const [isDesktopSidebarViewport, setIsDesktopSidebarViewport] = useState(false);
  const sidebarSwitcherRef = useRef<HTMLButtonElement>(null);
  const isWorkspaceShell = variant === "workspace";
  const sidebarOpen =
    sidebarState === "open" || (sidebarState === "responsive" && isDesktopSidebarViewport);
  const setSidebarOpen = (open: boolean) => setSidebarState(open ? "open" : "closed");

  useEffect(() => {
    const desktopQuery = window.matchMedia(DESKTOP_SIDEBAR_QUERY);
    const syncDesktopViewport = () => setIsDesktopSidebarViewport(desktopQuery.matches);

    syncDesktopViewport();
    desktopQuery.addEventListener("change", syncDesktopViewport);

    return () => desktopQuery.removeEventListener("change", syncDesktopViewport);
  }, []);

  return (
    <main
      id="main-content"
      className={`min-h-screen overflow-x-hidden text-slate-900 dark:text-slate-100 ${
        isWorkspaceShell ? WORKSPACE_SHELL_METRICS_CLASS : PUBLIC_SHELL_METRICS_CLASS
      }`}
    >
      <div className="fixed left-0 top-0 z-50 w-full">
        <Header
          sidebarOpen={sidebarOpen}
          setSidebarOpen={setSidebarOpen}
          sidebarSwitcherRef={sidebarSwitcherRef}
          variant={variant}
        />
      </div>
      <div className="pt-[var(--workspace-header-offset)]">
        {isWorkspaceShell && (
          <Sidebar
            sidebarState={sidebarState}
            setSidebarOpen={setSidebarOpen}
            exceptionRef={sidebarSwitcherRef}
          />
        )}
        <div
          className={`min-h-[calc(100vh_-_var(--workspace-header-offset))] min-w-0 transition-[margin] duration-200 ${
            isWorkspaceShell && sidebarState !== "closed" ? "lg:ml-[var(--workspace-sidebar-width)]" : ""
          }`}
        >
          <div
            className={
              isWorkspaceShell
                ? "mx-auto w-full max-w-[112rem] min-w-0 px-3 py-4 sm:px-4 md:px-5 md:py-5 xl:px-6"
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
