import DefaultLayout from "@/components/Layouts/DefaultLayout";
import { INSTITUTION_PRIORITIES } from "@/utils/workspace";
import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "For Institutions | Tutor",
  description:
    "Institution-facing positioning for Tutor's learner-record-centered lifelong-learning platform direction.",
};

const InstitutionsPage = () => {
  return (
    <DefaultLayout variant="public">
      <div className="space-y-10">
        <section className="rounded-[2rem] border border-stone-200 bg-white/92 p-8 shadow-sm dark:border-slate-700 dark:bg-slate-900/80">
          <p className="text-xs font-semibold uppercase tracking-[0.28em] text-teal-700">
            For institutions
          </p>
          <h1 className="mt-4 text-4xl font-semibold text-slate-900 dark:text-slate-50">
            Reposition Tutor as the institution-owned control plane for lifelong learning and
            outcomes.
          </h1>
          <p className="mt-4 max-w-3xl text-sm leading-8 text-slate-600 dark:text-slate-300">
            Wave 1 focuses on product posture and navigation: role-aware shells, curated entry
            points, and trust-first presentation. Existing routes and backend flows remain in place
            while the frontend stops behaving like a demo launcher.
          </p>
        </section>

        <section className="grid gap-5 lg:grid-cols-3">
          {INSTITUTION_PRIORITIES.map((priority) => (
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
                This slice stays honest about what is implemented.
              </h2>
              <p className="mt-4 text-sm leading-8 text-slate-600 dark:text-slate-300">
                No full route migration, no fake auth, and no invented authority. The value here is
                a cleaner academic front door, role-native shell, and visible governance language
                that the rest of the product can grow into.
              </p>
            </div>
            <div className="flex flex-col gap-3">
              <Link
                href="/workspace/admin"
                className="rounded-full border border-teal-700 bg-teal-700 px-5 py-3 text-center text-sm font-semibold text-white transition hover:bg-teal-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-700 focus-visible:ring-offset-2"
              >
                Preview admin workspace
              </Link>
              <Link
                href="/workspace/supervisor"
                className="rounded-full border border-stone-200 bg-white px-5 py-3 text-center text-sm font-semibold text-slate-900 transition hover:bg-stone-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-700 focus-visible:ring-offset-2 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-50 dark:hover:bg-slate-800"
              >
                Preview supervisor workspace
              </Link>
            </div>
          </div>
        </section>
      </div>
    </DefaultLayout>
  );
};

export default InstitutionsPage;
