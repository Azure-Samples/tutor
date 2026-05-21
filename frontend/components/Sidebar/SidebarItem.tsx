import type { WorkspaceNavItem, WorkspaceNavMatchStrategy } from "@/utils/workspace";
import Link from "next/link";
import { usePathname } from "next/navigation";
import React from "react";

const DEFAULT_NAV_MATCH_STRATEGY: WorkspaceNavMatchStrategy = "exact";

function routeMatches(pathname: string, route: string, strategy: WorkspaceNavMatchStrategy) {
  if (strategy === "none") {
    return false;
  }

  if (route === "/") {
    return pathname === route;
  }

  if (strategy === "exact") {
    return pathname === route;
  }

  return pathname === route || pathname.startsWith(`${route}/`);
}

const SidebarItem = ({ item }: { item: WorkspaceNavItem }) => {
  const pathname = usePathname();
  const isItemActive =
    routeMatches(pathname, item.route, item.matchStrategy ?? DEFAULT_NAV_MATCH_STRATEGY) ||
    (item.matchRoutes ?? []).some((matchRoute) =>
      routeMatches(pathname, matchRoute.route, matchRoute.strategy),
    );
  const Icon = item.icon;

  return (
    <li>
      <Link
        href={item.route}
        aria-current={isItemActive ? "page" : undefined}
        className={`group flex min-h-11 items-start gap-2 rounded-lg border px-2.5 py-2 transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-700 focus-visible:ring-offset-2 ${
          isItemActive
            ? "border-teal-700 bg-teal-700 text-white shadow-sm"
            : "border-transparent bg-transparent text-slate-700 hover:border-stone-200 hover:bg-white/80 dark:text-slate-200 dark:hover:border-slate-700 dark:hover:bg-slate-900/70"
        }`}
      >
        <span
          className={`mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border transition ${
            isItemActive
              ? "border-white/20 bg-white/10 text-white"
              : "border-stone-200 bg-white text-slate-700 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-200"
          }`}
        >
          <Icon className="h-4 w-4" aria-hidden="true" />
        </span>
        <span className="min-w-0 flex-1">
          <span className="flex items-center gap-2">
            <span className="text-sm font-semibold leading-5">{item.label}</span>
            {item.badge && (
              <span
                className={`rounded-full px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-[0.12em] ${
                  isItemActive
                    ? "bg-white/10 text-white"
                    : "bg-stone-100 text-slate-500 dark:bg-slate-800 dark:text-slate-300"
                }`}
              >
                {item.badge}
              </span>
            )}
          </span>
          <span
            className={`mt-0.5 block break-words text-[11px] leading-4 ${
              isItemActive ? "text-teal-50" : "text-slate-500 dark:text-slate-400"
            }`}
          >
            {item.description}
          </span>
        </span>
      </Link>
    </li>
  );
};

export default SidebarItem;
