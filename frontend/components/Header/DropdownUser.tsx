"use client";

import ClickOutside from "@/components/ClickOutside";
import { useWorkspace } from "@/components/Workspace/WorkspaceProvider";
import Image from "next/image";
import Link from "next/link";
import { useState } from "react";

const DropdownUser = () => {
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const { actor, currentContext, currentRole, isMockMode, roleConfig } = useWorkspace();
  const displayName = actor?.display_name || roleConfig.personaName;
  const detailLine = actor?.email || roleConfig.personaDetail;
  const workspaceHref = currentContext.workspacePath || `/workspace/${currentRole}`;
  const identityLabel = isMockMode
    ? `${roleConfig.label} fallback context`
    : `${roleConfig.label} access context`;

  return (
    <ClickOutside onClick={() => setDropdownOpen(false)} className="relative">
      <button
        type="button"
        onClick={() => setDropdownOpen(!dropdownOpen)}
        className="flex items-center gap-3 rounded-full border border-stone-200 bg-white px-2 py-1.5 text-left shadow-sm transition hover:bg-stone-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-700 focus-visible:ring-offset-2 dark:border-slate-700 dark:bg-slate-900 dark:hover:bg-slate-800"
        aria-expanded={dropdownOpen}
        aria-haspopup="menu"
      >
        <span className="hidden text-right lg:block">
          <span className="block text-sm font-medium text-slate-900 dark:text-slate-50">
            {displayName}
          </span>
          <span className="block text-xs text-slate-500 dark:text-slate-400">{identityLabel}</span>
        </span>

        <span className="flex h-10 w-10 items-center justify-center overflow-hidden rounded-full border border-stone-200 bg-stone-100 dark:border-slate-700 dark:bg-slate-800">
          <Image
            width={64}
            height={64}
            src="/images/user/like-a-boss.png"
            alt="Pilot user"
            className="h-10 w-10 object-cover"
          />
        </span>
      </button>

      {dropdownOpen && (
        <div
          role="menu"
          className="absolute right-0 mt-3 w-72 rounded-[1.5rem] border border-stone-200 bg-white p-4 shadow-xl dark:border-slate-700 dark:bg-slate-950"
        >
          <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-500 dark:text-slate-400">
            Active actor
          </p>
          <p className="mt-3 text-lg font-semibold text-slate-900 dark:text-slate-50">
            {displayName}
          </p>
          <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">{detailLine}</p>

          <div className="mt-4 rounded-[1.25rem] border border-stone-200 bg-stone-50 p-4 dark:border-slate-700 dark:bg-slate-900/70">
            <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-500 dark:text-slate-400">
              Current role
            </p>
            <p className="mt-2 text-sm font-semibold text-slate-900 dark:text-slate-50">
              {roleConfig.label}
            </p>
            <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">
              {currentContext.label}
            </p>
            <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
              {currentContext.scope}
            </p>
          </div>

          <div className="mt-4 flex flex-col gap-2">
            <Link
              href={workspaceHref}
              onClick={() => setDropdownOpen(false)}
              className="rounded-xl border border-stone-200 bg-white px-4 py-3 text-sm font-medium text-slate-900 transition hover:bg-stone-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-700 focus-visible:ring-offset-2 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-50 dark:hover:bg-slate-800"
            >
              Open current workspace
            </Link>
            <Link
              href="/evidence-trust"
              onClick={() => setDropdownOpen(false)}
              className="rounded-xl border border-stone-200 bg-white px-4 py-3 text-sm font-medium text-slate-900 transition hover:bg-stone-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-700 focus-visible:ring-offset-2 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-50 dark:hover:bg-slate-800"
            >
              Evidence & Trust
            </Link>
            <Link
              href="/programs"
              onClick={() => setDropdownOpen(false)}
              className="rounded-xl border border-stone-200 bg-white px-4 py-3 text-sm font-medium text-slate-900 transition hover:bg-stone-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-700 focus-visible:ring-offset-2 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-50 dark:hover:bg-slate-800"
            >
              Curated programs
            </Link>
          </div>
        </div>
      )}
    </ClickOutside>
  );
};

export default DropdownUser;
