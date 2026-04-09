"use client";

import SidebarItem from "@/components/Sidebar/SidebarItem";
import { useWorkspace } from "@/components/Workspace/WorkspaceProvider";
import Link from "next/link";
import type React from "react";

interface SidebarProps {
  sidebarOpen: boolean;
  setSidebarOpen: (arg: boolean) => void;
  exceptionRef?: React.RefObject<HTMLElement>;
}

interface SidebarHoverCardProps {
  description: string;
  eyebrow: string;
  position?: "side-start" | "side-end";
  title: string;
  triggerLabel: string;
  children?: React.ReactNode;
}

const hoverCardPositionStyles = {
  "side-start":
    "left-0 top-full mt-3 origin-top-left lg:left-full lg:top-0 lg:ml-3 lg:mt-0 lg:origin-top-left",
  "side-end":
    "left-0 bottom-full mb-3 origin-bottom-left lg:left-full lg:bottom-0 lg:mb-0 lg:ml-3 lg:origin-bottom-left",
} as const;

// No GoF pattern applies here; this is a small presentational hover disclosure.
const SidebarHoverCard = ({
  children,
  description,
  eyebrow,
  position = "side-start",
  title,
  triggerLabel,
}: SidebarHoverCardProps) => {
  return (
    <div className="group/hover-card relative inline-flex">
      <button
        type="button"
        className="inline-flex items-center rounded-full border border-stone-200 bg-white px-2.5 py-1 text-[11px] font-semibold text-slate-700 transition hover:border-teal-200 hover:bg-teal-50/80 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-700 focus-visible:ring-offset-2 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-200 dark:hover:border-teal-800 dark:hover:bg-slate-900"
      >
        <span>{triggerLabel}</span>
      </button>

      <div
        className={`invisible absolute z-50 w-[16rem] scale-95 rounded-[1.25rem] border border-stone-200 bg-white/95 p-4 opacity-0 shadow-xl transition duration-200 group-hover/hover-card:visible group-hover/hover-card:scale-100 group-hover/hover-card:opacity-100 group-focus-within/hover-card:visible group-focus-within/hover-card:scale-100 group-focus-within/hover-card:opacity-100 dark:border-slate-700 dark:bg-slate-950/95 ${hoverCardPositionStyles[position]}`}
      >
        <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-500 dark:text-slate-400">
          {eyebrow}
        </p>
        <p className="mt-2 text-base font-semibold text-slate-900 dark:text-slate-50">{title}</p>
        <p className="mt-2 text-sm leading-7 text-slate-600 dark:text-slate-300">{description}</p>
        {children ? <div className="mt-4">{children}</div> : null}
      </div>
    </div>
  );
};

const Sidebar = ({ sidebarOpen, setSidebarOpen, exceptionRef }: SidebarProps) => {
  const { currentContext, isLoading, roleConfig } = useWorkspace();
  const contextNote = isLoading
    ? "Tutor is resolving the latest context note for this role."
    : currentContext.note;

  return (
    <>
      {sidebarOpen && (
        <button
          type="button"
          aria-label="Close sidebar"
          className="fixed inset-0 z-30 bg-slate-950/20 backdrop-blur-[1px] lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <aside
        id="sidebar"
        className={`fixed left-0 top-[72px] z-40 flex h-[calc(100vh-72px)] w-[18rem] flex-col border-r border-stone-200 bg-stone-50/95 px-4 py-5 shadow-sm transition-transform duration-200 dark:border-slate-800 dark:bg-slate-950/90 ${
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="rounded-[1.25rem] border border-stone-200 bg-white/90 p-3 shadow-sm dark:border-slate-700 dark:bg-slate-900/80">
          <p className="text-[10px] font-semibold uppercase tracking-[0.24em] text-slate-500 dark:text-slate-400">
            {roleConfig.workspaceTitle}
          </p>
          <div className="mt-2 flex items-center gap-2">
            <div className="min-w-0">
              <h2 className="truncate text-[2rem] font-semibold leading-none text-slate-900 dark:text-slate-50">
                {roleConfig.label}
              </h2>
            </div>
          </div>
          <div className="mt-3 flex flex-wrap gap-1.5">
            <SidebarHoverCard
              description={roleConfig.publicPitch}
              eyebrow={roleConfig.workspaceTitle}
              position="side-start"
              title={roleConfig.label}
              triggerLabel="About"
            />
            <SidebarHoverCard
              description={contextNote}
              eyebrow="Current context"
              position="side-start"
              title={currentContext.label}
              triggerLabel="Context"
            >
              <p className="text-xs font-medium text-slate-500 dark:text-slate-400">
                {currentContext.scope}
              </p>
            </SidebarHoverCard>
            <SidebarHoverCard
              description={roleConfig.trustLabel}
              eyebrow="Trust note"
              position="side-start"
              title={`${roleConfig.label} guidance`}
              triggerLabel="Trust"
            >
              <Link
                href="/evidence-trust"
                className="inline-flex rounded-full border border-stone-200 bg-white px-3 py-2 text-sm font-medium text-slate-900 transition hover:bg-stone-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-700 focus-visible:ring-offset-2 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-50"
              >
                Review trust posture
              </Link>
            </SidebarHoverCard>
          </div>
        </div>

        <nav aria-label={`${roleConfig.label} navigation`} className="mt-4 flex-1 overflow-y-auto">
          <ul className="space-y-2">
            {roleConfig.navigation.map((item) => (
              <SidebarItem key={`${roleConfig.key}-${item.label}`} item={item} />
            ))}
          </ul>
        </nav>
      </aside>
    </>
  );
};

export default Sidebar;
