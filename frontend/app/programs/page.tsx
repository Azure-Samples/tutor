import DefaultLayout from "@/components/Layouts/DefaultLayout";
import { PUBLIC_PROGRAMS } from "@/utils/workspace";
import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Programs | Tutor",
  description:
    "Curated programs and re-entry offers aligned to Tutor's lifelong-learning platform direction.",
};

const ProgramsPage = () => {
  return (
    <DefaultLayout variant="public">
      <div className="space-y-10">
        <section className="rounded-[2rem] border border-stone-200 bg-white/92 p-8 shadow-sm dark:border-slate-700 dark:bg-slate-900/80">
          <p className="text-xs font-semibold uppercase tracking-[0.28em] text-teal-700">
            Curated pilot catalog
          </p>
          <h1 className="mt-4 text-4xl font-semibold text-slate-900 dark:text-slate-50">
            Programs and re-entry offers with clear audience, scope, and outcome framing.
          </h1>
          <p className="mt-4 max-w-3xl text-sm leading-8 text-slate-600 dark:text-slate-300">
            Wave 1 intentionally avoids a broad marketplace. These entries preview how Tutor can
            expose institution-owned programs, alumni re-entry, and leadership pilots without
            turning the public surface into a feature menu.
          </p>
        </section>

        <section className="grid gap-5 lg:grid-cols-3">
          {PUBLIC_PROGRAMS.map((program) => (
            <article
              key={program.title}
              className="rounded-[1.75rem] border border-stone-200 bg-white/92 p-6 shadow-sm dark:border-slate-700 dark:bg-slate-900/80"
            >
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500 dark:text-slate-400">
                {program.audience}
              </p>
              <h2 className="mt-3 text-2xl font-semibold text-slate-900 dark:text-slate-50">
                {program.title}
              </h2>
              <p className="mt-2 text-sm font-medium text-teal-700 dark:text-teal-300">
                {program.format}
              </p>
              <p className="mt-4 text-sm leading-7 text-slate-600 dark:text-slate-300">
                {program.description}
              </p>
              <div className="mt-5 flex flex-wrap gap-2">
                {program.outcomes.map((outcome) => (
                  <span
                    key={outcome}
                    className="rounded-full border border-stone-200 bg-stone-50 px-3 py-1 text-xs font-medium text-slate-600 dark:border-slate-700 dark:bg-slate-950/60 dark:text-slate-300"
                  >
                    {outcome}
                  </span>
                ))}
              </div>
              <Link
                href={program.href}
                className="mt-5 inline-flex rounded-full border border-teal-700 px-4 py-2 text-sm font-semibold text-teal-700 transition hover:bg-teal-700 hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-700 focus-visible:ring-offset-2 dark:text-teal-300 dark:hover:text-white"
              >
                Open related workspace
              </Link>
            </article>
          ))}
        </section>

        <section className="rounded-[1.75rem] border border-amber-200 bg-amber-50/85 p-6 text-sm leading-7 text-amber-950 shadow-sm dark:border-amber-900/60 dark:bg-amber-950/30 dark:text-amber-100">
          <p className="font-semibold">Wave 1 limit</p>
          <p className="mt-2">
            These entries are curated placeholders for the first slice. They are not a full
            enrollment, entitlement, or commerce implementation.
          </p>
        </section>
      </div>
    </DefaultLayout>
  );
};

export default ProgramsPage;
