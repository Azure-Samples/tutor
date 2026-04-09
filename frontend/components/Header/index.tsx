"use client";

import ContextSwitcher from "@/components/Header/ContextSwitcher";
import DarkModeSwitcher from "@/components/Header/DarkModeSwitcher";
import DropdownUser from "@/components/Header/DropdownUser";
import RoleSwitcher from "@/components/Header/RoleSwitcher";
import SidebarSwitcher from "@/components/Header/SidebarSwitcher";
import { useWorkspace } from "@/components/Workspace/WorkspaceProvider";
import { PUBLIC_NAV_LINKS } from "@/utils/workspace";
import Image from "next/image";
import Link from "next/link";

const Header = (props: {
  sidebarOpen: boolean;
  setSidebarOpen: (arg0: boolean) => void;
  sidebarSwitcherRef?: React.RefObject<HTMLButtonElement>;
  variant?: "workspace" | "public";
}) => {
  const { currentRole, isLoading, isMockMode } = useWorkspace();

  if (props.variant === "public") {
    return (
      <header className="border-b border-stone-200/80 bg-white/90 backdrop-blur dark:border-slate-800 dark:bg-slate-950/85">
        <div className="mx-auto flex w-full max-w-7xl items-center justify-between gap-4 px-6 py-4 md:px-8">
          <Link href="/" aria-label="Go to Tutor home" className="flex items-center gap-3">
            <Image
              width={44}
              height={44}
              src="/images/logo/logo.webp"
              alt="Tutor"
              priority
              className="rounded-xl object-cover"
            />
            <span>
              <span className="block text-[11px] font-semibold uppercase tracking-[0.3em] text-teal-700">
                Tutor
              </span>
              <span className="block text-base font-semibold text-slate-900 dark:text-slate-50">
                Lifelong learning platform
              </span>
            </span>
          </Link>

          <nav aria-label="Public navigation" className="hidden items-center gap-6 md:flex">
            {PUBLIC_NAV_LINKS.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className="text-sm font-medium text-slate-600 transition hover:text-slate-900 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-700 focus-visible:ring-offset-2 dark:text-slate-300 dark:hover:text-slate-50"
              >
                {link.label}
              </Link>
            ))}
          </nav>

          <div className="flex items-center gap-3">
            <ul className="flex items-center gap-3">
              <DarkModeSwitcher />
            </ul>
            <Link
              href={`/workspace/${currentRole}`}
              className="rounded-full border border-teal-700 bg-teal-700 px-4 py-2 text-sm font-semibold text-white transition hover:bg-teal-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-700 focus-visible:ring-offset-2"
            >
              Enter pilot workspace
            </Link>
          </div>
        </div>
      </header>
    );
  }

  return (
    <header className="border-b border-stone-200/80 bg-white/90 backdrop-blur dark:border-slate-800 dark:bg-slate-950/85">
      <div className="flex w-full items-center gap-4 px-4 py-3 md:px-6">
        <div className="flex items-center gap-3">
          <Link
            href={`/workspace/${currentRole}`}
            aria-label="Go to current workspace"
            className="flex items-center gap-3"
          >
            <Image
              width={42}
              height={42}
              src="/images/logo/logo.webp"
              alt="Tutor"
              priority
              className="rounded-xl object-cover"
            />
            <span className="hidden sm:block">
              <span className="block text-[11px] font-semibold uppercase tracking-[0.28em] text-teal-700">
                Tutor
              </span>
              <span className="block text-sm font-semibold text-slate-900 dark:text-slate-50">
                Role-aware workspace shell
              </span>
            </span>
          </Link>
          {isLoading && (
            <span className="hidden rounded-full border border-stone-200 bg-stone-50 px-3 py-1 text-xs font-medium text-slate-700 xl:inline-flex dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200">
              Resolving access context
            </span>
          )}
          {!isLoading && isMockMode && (
            <span className="hidden rounded-full border border-amber-200 bg-amber-50 px-3 py-1 text-xs font-medium text-amber-900 xl:inline-flex dark:border-amber-900/60 dark:bg-amber-950/30 dark:text-amber-100">
              Fallback workspace context
            </span>
          )}
        </div>

        <div className="ml-auto hidden flex-1 items-start justify-center gap-3 lg:flex">
          <RoleSwitcher />
          <ContextSwitcher />
        </div>

        <div className="flex items-center gap-3">
          <Link
            href="/evidence-trust"
            className="hidden rounded-full border border-stone-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-stone-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-700 focus-visible:ring-offset-2 xl:inline-flex dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200 dark:hover:bg-slate-800"
          >
            Help & Trust
          </Link>

          <ul className="flex items-center gap-3">
            <DarkModeSwitcher />
            <li>
              <SidebarSwitcher
                sidebarOpen={props.sidebarOpen}
                setSidebarOpen={props.setSidebarOpen}
                ref={props.sidebarSwitcherRef}
              />
            </li>
          </ul>

          <DropdownUser />
        </div>
      </div>

      <div className="border-t border-stone-200/70 px-4 pb-3 pt-3 lg:hidden dark:border-slate-800">
        <div className="flex flex-col gap-3 sm:flex-row">
          <RoleSwitcher />
          <ContextSwitcher />
        </div>
      </div>
    </header>
  );
};

export default Header;
