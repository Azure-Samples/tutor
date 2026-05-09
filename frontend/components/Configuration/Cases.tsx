"use client";

import Link from "next/link";

import { getRouteMetadata } from "@/utils/routeMetadata";

const CASES_ROUTE = "/configuration/cases";

const Cases = () => {
  const casesRoute = getRouteMetadata(CASES_ROUTE);

  return (
    <section className="w-full rounded-lg border border-stone-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-900">
      <p className="text-xs font-semibold uppercase tracking-[0.24em] text-teal-700 dark:text-teal-300">
        Compatibility adapter
      </p>
      <h2 className="mt-3 text-2xl font-semibold text-slate-900 dark:text-slate-50">
        Cases management is available as a routed configuration surface
      </h2>
      <p className="mt-3 max-w-3xl text-sm leading-7 text-slate-600 dark:text-slate-300">
        This component remains available for older imports, but the working cases experience lives
        at{" "}
        <span className="font-mono text-xs text-slate-900 dark:text-slate-50">
          {casesRoute?.path ?? CASES_ROUTE}
        </span>
        . Use that route for case creation, profiles, steps, and current APIM-backed case data.
      </p>
      <Link
        href={CASES_ROUTE}
        className="mt-5 inline-flex rounded-md border border-teal-700 bg-teal-700 px-4 py-2 text-sm font-semibold text-white transition hover:bg-teal-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-700 focus-visible:ring-offset-2"
      >
        Open cases management
      </Link>
    </section>
  );
};

export default Cases;
