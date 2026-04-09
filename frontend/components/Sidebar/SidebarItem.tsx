import type { WorkspaceNavItem } from "@/utils/workspace";
import Link from "next/link";
import { usePathname } from "next/navigation";
import React from "react";

function routeMatches(pathname: string, route: string, exactMatch = false) {
  if (route === "/") {
    return pathname === route;
  }

  if (exactMatch) {
    return pathname === route;
  }

  return pathname === route || pathname.startsWith(`${route}/`);
}

const SidebarItem = ({ item }: { item: WorkspaceNavItem }) => {
  const pathname = usePathname();
  const isItemActive =
    routeMatches(pathname, item.route, item.exactMatch) ||
    (item.matchRoutes ?? []).some((route) => routeMatches(pathname, route));
  const Icon = item.icon;

  return (
    <li>
      <Link
        href={item.route}
        aria-current={isItemActive ? "page" : undefined}
        className={`group flex items-start gap-3 rounded-[1.25rem] border px-3 py-3 transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-700 focus-visible:ring-offset-2 ${
          isItemActive
            ? "border-teal-700 bg-teal-700 text-white shadow-sm"
            : "border-transparent bg-transparent text-slate-700 hover:border-stone-200 hover:bg-white/80 dark:text-slate-200 dark:hover:border-slate-700 dark:hover:bg-slate-900/70"
        }`}
      >
        <span
          className={`mt-0.5 flex h-10 w-10 items-center justify-center rounded-xl border transition ${
            isItemActive
              ? "border-white/20 bg-white/10 text-white"
              : "border-stone-200 bg-white text-slate-700 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-200"
          }`}
        >
          <Icon className="h-4.5 w-4.5" aria-hidden="true" />
        </span>
        <span className="min-w-0 flex-1">
          <span className="flex items-center gap-2">
            <span className="font-semibold">{item.label}</span>
            {item.badge && (
              <span
                className={`rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase tracking-[0.16em] ${
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
            className={`mt-1 block text-xs leading-6 ${
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
