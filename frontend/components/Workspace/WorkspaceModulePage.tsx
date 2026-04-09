"use client";

import { useWorkspace } from "@/components/Workspace/WorkspaceProvider";
import { type WorkspaceRole, getRoleConfig } from "@/utils/workspace";
import Link from "next/link";

interface WorkspaceModuleLink {
  label: string;
  description: string;
  href: string;
  kind?: "primary" | "secondary";
}

interface WorkspaceModulePageProps {
  workspaceRole: WorkspaceRole;
  eyebrow: string;
  title: string;
  description: string;
  links: WorkspaceModuleLink[];
  notes: string[];
}

const WorkspaceModulePage = ({
  description,
  eyebrow,
  links,
  notes,
  title,
  workspaceRole,
}: WorkspaceModulePageProps) => {
  const { currentContext, isLoading, isMockMode, roleConfig } = useWorkspace();
  const activeRoleConfig =
    roleConfig.key === workspaceRole ? roleConfig : getRoleConfig(workspaceRole);

  return (
    <div className="space-y-8">
      <section className="rounded-[2rem] border border-stone-200 bg-white/90 p-6 shadow-sm md:p-8">
        <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
          <div className="max-w-3xl">
            <p className="text-xs font-semibold uppercase tracking-[0.3em] text-teal-700">
              {eyebrow}
            </p>
            <h1 className="mt-4 text-4xl font-semibold leading-tight text-slate-900 md:text-5xl dark:text-slate-50">
              {title}
            </h1>
            <p className="mt-4 text-lg leading-8 text-slate-600 dark:text-slate-300">
              {description}
            </p>
          </div>

          <aside className="w-full max-w-md rounded-[1.5rem] border border-stone-200 bg-stone-50/90 p-5 shadow-sm dark:border-slate-700 dark:bg-slate-900/70">
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500 dark:text-slate-400">
              Current context
            </p>
            <h2 className="mt-3 text-2xl font-semibold text-slate-900 dark:text-slate-50">
              {currentContext.label}
            </h2>
            <p className="mt-1 text-sm font-medium text-slate-600 dark:text-slate-300">
              {currentContext.scope}
            </p>
            <p className="mt-4 text-sm leading-7 text-slate-600 dark:text-slate-300">
              {currentContext.note}
            </p>
            <div className="mt-4 rounded-[1.25rem] border border-stone-200 bg-white/90 p-4 dark:border-slate-700 dark:bg-slate-950/70">
              <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-500 dark:text-slate-400">
                Trust note
              </p>
              <p className="mt-2 text-sm leading-7 text-slate-600 dark:text-slate-300">
                {activeRoleConfig.trustLabel}
              </p>
            </div>
          </aside>
        </div>
      </section>

      {!isLoading && isMockMode && (
        <div className="rounded-[1.5rem] border border-amber-200 bg-amber-50/80 p-4 text-sm leading-7 text-amber-950 dark:border-amber-900/60 dark:bg-amber-950/20 dark:text-amber-100">
          This route is still available while the backend access context is unavailable. Links below
          continue to target the existing working pages.
        </div>
      )}

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {links.map((link) => (
          <Link
            key={link.href}
            href={link.href}
            className={`rounded-[1.5rem] border p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-700 focus-visible:ring-offset-2 ${
              link.kind === "primary"
                ? "border-teal-700 bg-teal-700 text-white"
                : "border-stone-200 bg-white/90 text-slate-900 dark:border-slate-700 dark:bg-slate-900/75 dark:text-slate-50"
            }`}
          >
            <p className="text-lg font-semibold">{link.label}</p>
            <p
              className={`mt-3 text-sm leading-7 ${link.kind === "primary" ? "text-teal-50" : "text-slate-600 dark:text-slate-300"}`}
            >
              {link.description}
            </p>
          </Link>
        ))}
      </section>

      <section className="rounded-[1.75rem] border border-stone-200 bg-white/90 p-6 shadow-sm dark:border-slate-700 dark:bg-slate-900/75">
        <h2 className="text-2xl font-semibold text-slate-900 dark:text-slate-50">
          How this route works
        </h2>
        <div className="mt-5 grid gap-4 md:grid-cols-3">
          {notes.map((note) => (
            <div
              key={note}
              className="rounded-[1.25rem] border border-stone-200 bg-stone-50/90 p-4 text-sm leading-7 text-slate-600 dark:border-slate-700 dark:bg-slate-950/70 dark:text-slate-300"
            >
              {note}
            </div>
          ))}
        </div>
        <Link
          href={`/workspace/${workspaceRole}`}
          className="mt-5 inline-flex rounded-full border border-stone-200 bg-white px-4 py-2 text-sm font-medium text-slate-900 transition hover:bg-stone-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-700 focus-visible:ring-offset-2 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-50"
        >
          Back to {activeRoleConfig.label} home
        </Link>
      </section>
    </div>
  );
};

export default WorkspaceModulePage;
