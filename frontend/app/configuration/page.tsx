import DefaultLayout from "@/components/Layouts/DefaultLayout";
import { getRouteMetadata } from "@/utils/routeMetadata";
import type { Metadata } from "next";
import Link from "next/link";
import {
  FiBookOpen,
  FiCheckSquare,
  FiCpu,
  FiDatabase,
  FiLayers,
  FiMessageSquare,
  FiSliders,
  FiUsers,
} from "react-icons/fi";
import type { IconType } from "react-icons";

export const metadata: Metadata = {
  title: "Tutor | Configuration",
  description: "Administrative configuration hub for Tutor content, policy, and integrations.",
};

interface ConfigurationRouteConfig {
  href: string;
  title: string;
  section: string;
  icon: IconType;
}

const CONFIGURATION_ROUTE_CONFIGS = [
  {
    href: "/configuration/cases",
    icon: FiUsers,
    section: "Content setup",
    title: "Cases",
  },
  {
    href: "/configuration/themes",
    icon: FiLayers,
    section: "Content setup",
    title: "Themes",
  },
  {
    href: "/configuration/questions",
    icon: FiCheckSquare,
    section: "Assessment policy",
    title: "Questions",
  },
  {
    href: "/configuration/agents",
    icon: FiCpu,
    section: "AI operations",
    title: "Agents",
  },
  {
    href: "/configuration/upskilling",
    icon: FiBookOpen,
    section: "Faculty workflows",
    title: "Upskilling",
  },
  {
    href: "/configuration/evaluation",
    icon: FiSliders,
    section: "AI operations",
    title: "Evaluation adapter",
  },
  {
    href: "/configuration/supervisor",
    icon: FiMessageSquare,
    section: "Leadership utilities",
    title: "Supervisor",
  },
  {
    href: "/configuration/lms-gateway",
    icon: FiDatabase,
    section: "Integrations",
    title: "LMS Gateway",
  },
] as const satisfies readonly ConfigurationRouteConfig[];

const getConfigurationRouteCards = () =>
  CONFIGURATION_ROUTE_CONFIGS.map((routeConfig) => {
    const route = getRouteMetadata(routeConfig.href);

    return {
      ...routeConfig,
      audience: route?.audience ?? "Admins and faculty operators",
      capability: route?.capability ?? "Administrative utility for Tutor operators.",
      label: route?.label ?? routeConfig.title,
      status: route?.status === "adapter" ? "Adapter" : "Active",
    };
  });

const configurationRouteCards = getConfigurationRouteCards();

const ConfigurationPage = () => {
  return (
    <DefaultLayout metadata={metadata}>
      <div className="space-y-8">
        <header className="border-b border-stone-200 pb-6 dark:border-slate-700">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-teal-700 dark:text-teal-300">
            Admin configuration
          </p>
          <h1 className="mt-3 max-w-4xl text-3xl font-semibold leading-tight text-slate-900 md:text-4xl dark:text-slate-50">
            Configuration operations hub
          </h1>
          <p className="mt-3 max-w-3xl text-sm leading-7 text-slate-600 dark:text-slate-300">
            A compact entry point for content setup, assessment policy, AI operations, leadership
            utilities, and LMS integration work. These links preserve the current configuration
            routes while presenting them in the shared Tutor workspace style.
          </p>
          <dl className="mt-5 flex flex-wrap gap-x-6 gap-y-2 text-sm text-slate-600 dark:text-slate-300">
            <div className="flex items-center gap-2">
              <dt className="font-medium text-slate-900 dark:text-slate-50">Surfaces</dt>
              <dd>{configurationRouteCards.length}</dd>
            </div>
            <div className="flex items-center gap-2">
              <dt className="font-medium text-slate-900 dark:text-slate-50">Primary audience</dt>
              <dd>Admins and faculty operators</dd>
            </div>
            <div className="flex items-center gap-2">
              <dt className="font-medium text-slate-900 dark:text-slate-50">Coverage</dt>
              <dd>Content, policy, AI, leadership, integrations</dd>
            </div>
          </dl>
        </header>

        <section aria-labelledby="configuration-routes-heading">
          <div className="mb-4 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <h2
                id="configuration-routes-heading"
                className="text-xl font-semibold text-slate-900 dark:text-slate-50"
              >
                Administrative surfaces
              </h2>
              <p className="mt-2 text-sm leading-7 text-slate-600 dark:text-slate-300">
                Route details are sourced from the frontend route registry so capability language
                stays aligned with the rest of the platform.
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
            {configurationRouteCards.map((route) => {
              const Icon = route.icon;

              return (
                <Link
                  key={route.href}
                  href={route.href}
                  className="group flex min-h-52 flex-col rounded-lg border border-stone-200 bg-white p-4 shadow-sm transition-colors hover:border-teal-700 hover:bg-stone-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-700 focus-visible:ring-offset-2 dark:border-slate-700 dark:bg-slate-900 dark:hover:border-teal-500 dark:hover:bg-slate-800"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-center gap-2 text-sm font-medium text-teal-700 dark:text-teal-300">
                      <Icon aria-hidden="true" className="h-4 w-4" />
                      <span>{route.section}</span>
                    </div>
                    <span className="rounded-md border border-stone-200 px-2 py-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-slate-500 dark:border-slate-700 dark:text-slate-400">
                      {route.status}
                    </span>
                  </div>
                  <h3 className="mt-4 text-lg font-semibold text-slate-900 dark:text-slate-50">
                    {route.title}
                  </h3>
                  <p className="mt-2 text-xs font-medium uppercase tracking-[0.18em] text-slate-500 dark:text-slate-400">
                    {route.label}
                  </p>
                  <p className="mt-3 flex-1 text-sm leading-6 text-slate-600 dark:text-slate-300">
                    {route.capability}
                  </p>
                  <p className="mt-4 text-sm font-semibold text-teal-700 group-hover:text-teal-800 dark:text-teal-300 dark:group-hover:text-teal-200">
                    Open {route.title}
                  </p>
                </Link>
              );
            })}
          </div>
        </section>
      </div>
    </DefaultLayout>
  );
};

export default ConfigurationPage;
