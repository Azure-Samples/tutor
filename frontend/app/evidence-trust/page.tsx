import DefaultLayout from "@/components/Layouts/DefaultLayout";
import { TRUST_PRINCIPLES } from "@/utils/workspace";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Evidence and Trust | Tutor",
  description:
    "How Tutor distinguishes deterministic record surfaces, advisory guidance, and degraded states.",
};

const EvidenceTrustPage = () => {
  return (
    <DefaultLayout variant="public">
      <div className="space-y-10">
        <section className="rounded-[2rem] border border-stone-200 bg-white/92 p-8 shadow-sm dark:border-slate-700 dark:bg-slate-900/80">
          <p className="text-xs font-semibold uppercase tracking-[0.28em] text-teal-700">
            Evidence and trust
          </p>
          <h1 className="mt-4 text-4xl font-semibold text-slate-900 dark:text-slate-50">
            Tutor does not pretend AI output is institutional truth.
          </h1>
          <p className="mt-4 max-w-3xl text-sm leading-8 text-slate-600 dark:text-slate-300">
            This Wave 1 slice makes trust boundaries visible in the UI. Deterministic summaries stay
            primary, role and context are explicitly mocked, and degraded orchestration paths remain
            legible instead of being polished away.
          </p>
        </section>

        <section className="grid gap-5 lg:grid-cols-2">
          {TRUST_PRINCIPLES.map((principle) => (
            <article
              key={principle.title}
              className="rounded-[1.75rem] border border-stone-200 bg-white/92 p-6 shadow-sm dark:border-slate-700 dark:bg-slate-900/80"
            >
              <h2 className="text-2xl font-semibold text-slate-900 dark:text-slate-50">
                {principle.title}
              </h2>
              <p className="mt-4 text-sm leading-8 text-slate-600 dark:text-slate-300">
                {principle.description}
              </p>
            </article>
          ))}
        </section>

        <section className="grid gap-5 lg:grid-cols-3">
          <article className="rounded-[1.75rem] border border-stone-200 bg-white/92 p-6 shadow-sm dark:border-slate-700 dark:bg-slate-900/80">
            <h2 className="text-2xl font-semibold text-slate-900 dark:text-slate-50">
              Visible provenance
            </h2>
            <p className="mt-4 text-sm leading-8 text-slate-600 dark:text-slate-300">
              Role dashboards explain what comes from queue state, school indicators, current
              workflow context, and advisory synthesis.
            </p>
          </article>
          <article className="rounded-[1.75rem] border border-stone-200 bg-white/92 p-6 shadow-sm dark:border-slate-700 dark:bg-slate-900/80">
            <h2 className="text-2xl font-semibold text-slate-900 dark:text-slate-50">
              Mocked context honesty
            </h2>
            <p className="mt-4 text-sm leading-8 text-slate-600 dark:text-slate-300">
              Role and context switching are local-state pilots for now. The shell says so openly
              instead of simulating finished relationship-aware auth.
            </p>
          </article>
          <article className="rounded-[1.75rem] border border-stone-200 bg-white/92 p-6 shadow-sm dark:border-slate-700 dark:bg-slate-900/80">
            <h2 className="text-2xl font-semibold text-slate-900 dark:text-slate-50">
              Degraded-state clarity
            </h2>
            <p className="mt-4 text-sm leading-8 text-slate-600 dark:text-slate-300">
              If orchestration falls back or a source is delayed, Tutor shows that state and
              downgrades the authority of the generated layer.
            </p>
          </article>
        </section>
      </div>
    </DefaultLayout>
  );
};

export default EvidenceTrustPage;
