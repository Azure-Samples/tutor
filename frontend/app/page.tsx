import DefaultLayout from "@/components/Layouts/DefaultLayout";
import {
  PUBLIC_HIGHLIGHTS,
  PUBLIC_PROGRAMS,
  ROLE_CONFIG_LIST,
  TRUST_PRINCIPLES,
} from "@/utils/workspace";
import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Tutor | Lifelong Learning Platform",
  description:
    "Institution-owned lifelong learning platform for learner records, guided learning, leadership briefings, and curated re-entry.",
};

const HomePage = () => {
  return (
    <DefaultLayout metadata={metadata} variant="public">
      <div className="space-y-16">
        <section className="grid gap-6 lg:grid-cols-[minmax(0,1.25fr)_minmax(20rem,24rem)]">
          <div className="rounded-[2rem] border border-stone-200 bg-white/92 p-8 shadow-sm md:p-10 dark:border-slate-700 dark:bg-slate-900/80">
            <p className="text-xs font-semibold uppercase tracking-[0.32em] text-teal-700">
              Institution-owned lifelong learning
            </p>
            <h1 className="mt-4 text-4xl font-semibold leading-tight text-slate-900 md:text-6xl dark:text-slate-50">
              A professional academic front door for learner records, guided work, leadership
              briefings, and curated re-entry.
            </h1>
            <p className="mt-5 max-w-3xl text-lg leading-8 text-slate-600 dark:text-slate-300">
              Tutor is moving from feature launcher to role-aware platform. Wave 1 keeps current
              capabilities intact while introducing calmer navigation, role-native workspaces,
              evidence-first trust messaging, and curated program framing.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link
                href="/workspace/student"
                className="rounded-full border border-teal-700 bg-teal-700 px-5 py-3 text-sm font-semibold text-white transition hover:bg-teal-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-700 focus-visible:ring-offset-2"
              >
                Enter a pilot workspace
              </Link>
              <Link
                href="/programs"
                className="rounded-full border border-stone-200 bg-white px-5 py-3 text-sm font-semibold text-slate-900 transition hover:bg-stone-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-700 focus-visible:ring-offset-2 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-50 dark:hover:bg-slate-800"
              >
                Explore curated programs
              </Link>
              <Link
                href="/evidence-trust"
                className="rounded-full border border-stone-200 bg-white px-5 py-3 text-sm font-semibold text-slate-900 transition hover:bg-stone-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-700 focus-visible:ring-offset-2 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-50 dark:hover:bg-slate-800"
              >
                Review evidence and trust
              </Link>
            </div>

            <div className="mt-10 grid gap-4 md:grid-cols-3">
              {PUBLIC_HIGHLIGHTS.map((highlight) => (
                <article
                  key={highlight.title}
                  className="rounded-[1.5rem] border border-stone-200 bg-stone-50/80 p-5 dark:border-slate-700 dark:bg-slate-950/60"
                >
                  <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-50">
                    {highlight.title}
                  </h2>
                  <p className="mt-3 text-sm leading-7 text-slate-600 dark:text-slate-300">
                    {highlight.description}
                  </p>
                </article>
              ))}
            </div>
          </div>

          <aside className="rounded-[2rem] border border-stone-200 bg-white/90 p-6 shadow-sm dark:border-slate-700 dark:bg-slate-900/80">
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500 dark:text-slate-400">
              Trust posture
            </p>
            <div className="mt-4 space-y-4">
              {TRUST_PRINCIPLES.map((principle) => (
                <article
                  key={principle.title}
                  className="rounded-[1.25rem] border border-stone-200 bg-stone-50/80 p-4 dark:border-slate-700 dark:bg-slate-950/60"
                >
                  <h2 className="text-base font-semibold text-slate-900 dark:text-slate-50">
                    {principle.title}
                  </h2>
                  <p className="mt-2 text-sm leading-7 text-slate-600 dark:text-slate-300">
                    {principle.description}
                  </p>
                </article>
              ))}
            </div>
          </aside>
        </section>

        <section>
          <div className="mb-6 flex flex-col gap-2">
            <p className="text-xs font-semibold uppercase tracking-[0.28em] text-teal-700">
              Curated programs and re-entry
            </p>
            <h2 className="text-3xl font-semibold text-slate-900 dark:text-slate-50">
              Pilot offerings with clear audience, evidence framing, and role entry points.
            </h2>
          </div>
          <div className="grid gap-5 lg:grid-cols-3">
            {PUBLIC_PROGRAMS.map((program) => (
              <article
                key={program.title}
                className="rounded-[1.75rem] border border-stone-200 bg-white/92 p-6 shadow-sm dark:border-slate-700 dark:bg-slate-900/80"
              >
                <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500 dark:text-slate-400">
                  {program.audience}
                </p>
                <h3 className="mt-3 text-2xl font-semibold text-slate-900 dark:text-slate-50">
                  {program.title}
                </h3>
                <p className="mt-2 text-sm font-medium text-teal-700 dark:text-teal-300">
                  {program.format}
                </p>
                <p className="mt-4 text-sm leading-7 text-slate-600 dark:text-slate-300">
                  {program.description}
                </p>
                <div className="mt-4 flex flex-wrap gap-2">
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
                  Open relevant workspace
                </Link>
              </article>
            ))}
          </div>
        </section>

        <section>
          <div className="mb-6 flex flex-col gap-2">
            <p className="text-xs font-semibold uppercase tracking-[0.28em] text-teal-700">
              Role previews
            </p>
            <h2 className="text-3xl font-semibold text-slate-900 dark:text-slate-50">
              One shell, different density and emphasis by audience.
            </h2>
          </div>
          <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
            {ROLE_CONFIG_LIST.map((role) => (
              <Link
                key={role.key}
                href={`/workspace/${role.key}`}
                className="rounded-[1.75rem] border border-stone-200 bg-white/92 p-6 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-700 focus-visible:ring-offset-2 dark:border-slate-700 dark:bg-slate-900/80"
              >
                <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500 dark:text-slate-400">
                  {role.workspaceTitle}
                </p>
                <h3 className="mt-3 text-2xl font-semibold text-slate-900 dark:text-slate-50">
                  {role.label}
                </h3>
                <p className="mt-3 text-sm leading-7 text-slate-600 dark:text-slate-300">
                  {role.publicPitch}
                </p>
              </Link>
            ))}
          </div>
        </section>

        <section className="rounded-[2rem] border border-stone-200 bg-white/92 p-8 shadow-sm dark:border-slate-700 dark:bg-slate-900/80">
          <div className="grid gap-6 lg:grid-cols-[minmax(0,1.1fr)_minmax(0,0.9fr)]">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.28em] text-teal-700">
                Institutional framing
              </p>
              <h2 className="mt-4 text-3xl font-semibold text-slate-900 dark:text-slate-50">
                Reposition the product without pretending the whole platform migration is already
                done.
              </h2>
              <p className="mt-4 text-sm leading-8 text-slate-600 dark:text-slate-300">
                This first slice is intentionally narrow. It introduces a credible academic front
                door, a shared role-aware shell, and first workspace homes while preserving the
                current route structure behind those surfaces.
              </p>
            </div>
            <div className="flex flex-col gap-3">
              <Link
                href="/institutions"
                className="rounded-full border border-teal-700 bg-teal-700 px-5 py-3 text-center text-sm font-semibold text-white transition hover:bg-teal-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-700 focus-visible:ring-offset-2"
              >
                See institution-facing positioning
              </Link>
              <Link
                href="/workspace/professor"
                className="rounded-full border border-stone-200 bg-white px-5 py-3 text-center text-sm font-semibold text-slate-900 transition hover:bg-stone-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-700 focus-visible:ring-offset-2 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-50 dark:hover:bg-slate-800"
              >
                Preview professor workspace
              </Link>
            </div>
          </div>
        </section>
      </div>
    </DefaultLayout>
  );
};

export default HomePage;
