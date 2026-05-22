"use client";

import { useI18n } from "@/components/I18n/LocaleProvider";
import { getPublicContent, getRoleConfigList } from "@/utils/workspace";
import Link from "next/link";

export function HomePageContent() {
  const { locale } = useI18n();
  const content = getPublicContent(locale);
  const roleConfigList = getRoleConfigList(locale);
  const page = content.pages.home;

  return (
    <div className="space-y-16">
      <section className="grid gap-6 lg:grid-cols-[minmax(0,1.25fr)_minmax(20rem,24rem)]">
        <div className="rounded-[2rem] border border-stone-200 bg-white/92 p-8 shadow-sm md:p-10 dark:border-slate-700 dark:bg-slate-900/80">
          <p className="text-xs font-semibold uppercase tracking-[0.32em] text-teal-700">
            {page.heroEyebrow}
          </p>
          <h1 className="mt-4 text-4xl font-semibold leading-tight text-slate-900 md:text-6xl dark:text-slate-50">
            {page.heroTitle}
          </h1>
          <p className="mt-5 max-w-3xl text-lg leading-8 text-slate-600 dark:text-slate-300">
            {page.heroDescription}
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link
              href="/workspace/student"
              className="rounded-full border border-teal-700 bg-teal-700 px-5 py-3 text-sm font-semibold text-white transition hover:bg-teal-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-700 focus-visible:ring-offset-2"
            >
              {page.primaryCta}
            </Link>
            <Link
              href="/programs"
              className="rounded-full border border-stone-200 bg-white px-5 py-3 text-sm font-semibold text-slate-900 transition hover:bg-stone-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-700 focus-visible:ring-offset-2 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-50 dark:hover:bg-slate-800"
            >
              {page.programsCta}
            </Link>
            <Link
              href="/evidence-trust"
              className="rounded-full border border-stone-200 bg-white px-5 py-3 text-sm font-semibold text-slate-900 transition hover:bg-stone-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-700 focus-visible:ring-offset-2 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-50 dark:hover:bg-slate-800"
            >
              {page.trustCta}
            </Link>
          </div>

          <div className="mt-10 grid gap-4 md:grid-cols-3">
            {content.highlights.map((highlight) => (
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
            {page.trustPostureEyebrow}
          </p>
          <div className="mt-4 space-y-4">
            {content.trustPrinciples.map((principle) => (
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
            {page.programsEyebrow}
          </p>
          <h2 className="text-3xl font-semibold text-slate-900 dark:text-slate-50">
            {page.programsTitle}
          </h2>
        </div>
        <div className="grid gap-5 lg:grid-cols-3">
          {content.programs.map((program) => (
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
                {page.programCardCta}
              </Link>
            </article>
          ))}
        </div>
      </section>

      <section>
        <div className="mb-6 flex flex-col gap-2">
          <p className="text-xs font-semibold uppercase tracking-[0.28em] text-teal-700">
            {page.rolePreviewsEyebrow}
          </p>
          <h2 className="text-3xl font-semibold text-slate-900 dark:text-slate-50">
            {page.rolePreviewsTitle}
          </h2>
        </div>
        <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
          {roleConfigList.map((role) => (
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
              {page.institutionalEyebrow}
            </p>
            <h2 className="mt-4 text-3xl font-semibold text-slate-900 dark:text-slate-50">
              {page.institutionalTitle}
            </h2>
            <p className="mt-4 text-sm leading-8 text-slate-600 dark:text-slate-300">
              {page.institutionalDescription}
            </p>
          </div>
          <div className="flex flex-col gap-3">
            <Link
              href="/institutions"
              className="rounded-full border border-teal-700 bg-teal-700 px-5 py-3 text-center text-sm font-semibold text-white transition hover:bg-teal-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-700 focus-visible:ring-offset-2"
            >
              {page.institutionCta}
            </Link>
            <Link
              href="/workspace/professor"
              className="rounded-full border border-stone-200 bg-white px-5 py-3 text-center text-sm font-semibold text-slate-900 transition hover:bg-stone-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-700 focus-visible:ring-offset-2 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-50 dark:hover:bg-slate-800"
            >
              {page.professorCta}
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}

export function ProgramsPageContent() {
  const { locale } = useI18n();
  const content = getPublicContent(locale);
  const page = content.pages.programs;

  return (
    <div className="space-y-10">
      <section className="rounded-[2rem] border border-stone-200 bg-white/92 p-8 shadow-sm dark:border-slate-700 dark:bg-slate-900/80">
        <p className="text-xs font-semibold uppercase tracking-[0.28em] text-teal-700">
          {page.eyebrow}
        </p>
        <h1 className="mt-4 text-4xl font-semibold text-slate-900 dark:text-slate-50">
          {page.title}
        </h1>
        <p className="mt-4 max-w-3xl text-sm leading-8 text-slate-600 dark:text-slate-300">
          {page.description}
        </p>
      </section>

      <section className="grid gap-5 lg:grid-cols-3">
        {content.programs.map((program) => (
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
              {page.cardCta}
            </Link>
          </article>
        ))}
      </section>

      <section className="rounded-[1.75rem] border border-amber-200 bg-amber-50/85 p-6 text-sm leading-7 text-amber-950 shadow-sm dark:border-amber-900/60 dark:bg-amber-950/30 dark:text-amber-100">
        <p className="font-semibold">{page.limitTitle}</p>
        <p className="mt-2">{page.limitDescription}</p>
      </section>
    </div>
  );
}

export function InstitutionsPageContent() {
  const { locale } = useI18n();
  const content = getPublicContent(locale);
  const page = content.pages.institutions;

  return (
    <div className="space-y-10">
      <section className="rounded-[2rem] border border-stone-200 bg-white/92 p-8 shadow-sm dark:border-slate-700 dark:bg-slate-900/80">
        <p className="text-xs font-semibold uppercase tracking-[0.28em] text-teal-700">
          {page.eyebrow}
        </p>
        <h1 className="mt-4 text-4xl font-semibold text-slate-900 dark:text-slate-50">
          {page.title}
        </h1>
        <p className="mt-4 max-w-3xl text-sm leading-8 text-slate-600 dark:text-slate-300">
          {page.description}
        </p>
      </section>

      <section className="grid gap-5 lg:grid-cols-3">
        {content.institutionPriorities.map((priority) => (
          <article
            key={priority.title}
            className="rounded-[1.75rem] border border-stone-200 bg-white/92 p-6 shadow-sm dark:border-slate-700 dark:bg-slate-900/80"
          >
            <h2 className="text-2xl font-semibold text-slate-900 dark:text-slate-50">
              {priority.title}
            </h2>
            <p className="mt-4 text-sm leading-8 text-slate-600 dark:text-slate-300">
              {priority.description}
            </p>
          </article>
        ))}
      </section>

      <section className="rounded-[1.75rem] border border-stone-200 bg-white/92 p-8 shadow-sm dark:border-slate-700 dark:bg-slate-900/80">
        <div className="grid gap-6 lg:grid-cols-[minmax(0,1.1fr)_minmax(0,0.9fr)] lg:items-center">
          <div>
            <h2 className="text-3xl font-semibold text-slate-900 dark:text-slate-50">
              {page.honestyTitle}
            </h2>
            <p className="mt-4 text-sm leading-8 text-slate-600 dark:text-slate-300">
              {page.honestyDescription}
            </p>
          </div>
          <div className="flex flex-col gap-3">
            <Link
              href="/workspace/admin"
              className="rounded-full border border-teal-700 bg-teal-700 px-5 py-3 text-center text-sm font-semibold text-white transition hover:bg-teal-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-700 focus-visible:ring-offset-2"
            >
              {page.adminCta}
            </Link>
            <Link
              href="/workspace/supervisor"
              className="rounded-full border border-stone-200 bg-white px-5 py-3 text-center text-sm font-semibold text-slate-900 transition hover:bg-stone-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-700 focus-visible:ring-offset-2 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-50 dark:hover:bg-slate-800"
            >
              {page.supervisorCta}
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}

export function EvidenceTrustPageContent() {
  const { locale } = useI18n();
  const content = getPublicContent(locale);
  const page = content.pages.evidenceTrust;

  return (
    <div className="space-y-10">
      <section className="rounded-[2rem] border border-stone-200 bg-white/92 p-8 shadow-sm dark:border-slate-700 dark:bg-slate-900/80">
        <p className="text-xs font-semibold uppercase tracking-[0.28em] text-teal-700">
          {page.eyebrow}
        </p>
        <h1 className="mt-4 text-4xl font-semibold text-slate-900 dark:text-slate-50">
          {page.title}
        </h1>
        <p className="mt-4 max-w-3xl text-sm leading-8 text-slate-600 dark:text-slate-300">
          {page.description}
        </p>
      </section>

      <section className="grid gap-5 lg:grid-cols-2">
        {content.trustPrinciples.map((principle) => (
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
        {page.cards.map((card) => (
          <article
            key={card.title}
            className="rounded-[1.75rem] border border-stone-200 bg-white/92 p-6 shadow-sm dark:border-slate-700 dark:bg-slate-900/80"
          >
            <h2 className="text-2xl font-semibold text-slate-900 dark:text-slate-50">
              {card.title}
            </h2>
            <p className="mt-4 text-sm leading-8 text-slate-600 dark:text-slate-300">
              {card.description}
            </p>
          </article>
        ))}
      </section>
    </div>
  );
}