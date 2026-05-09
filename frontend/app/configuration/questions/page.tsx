import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import DefaultLayout from "@/components/Layouts/DefaultLayout";
import QuestionsList from "@/components/Lists/Questions";
import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Questions | Tutor App",
  description: "Manage and review questions for the Tutor application.",
};

const QUESTION_ADMIN_LINKS = [
  {
    href: "/configuration/questions",
    isCurrent: true,
    label: "Questions",
  },
  {
    href: "/configuration/questions/graders",
    isCurrent: false,
    label: "Graders",
  },
  {
    href: "/configuration/questions/answers",
    isCurrent: false,
    label: "Answers",
  },
] as const;

const getQuestionAdminLinkClassName = (isCurrent: boolean): string =>
  [
    "inline-flex min-h-10 items-center rounded-md px-3 py-2 text-sm font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-700 focus-visible:ring-offset-2",
    isCurrent
      ? "bg-white text-teal-800 shadow-sm dark:bg-slate-900 dark:text-teal-300"
      : "text-slate-600 hover:bg-white hover:text-slate-900 dark:text-slate-300 dark:hover:bg-slate-900 dark:hover:text-slate-50",
  ].join(" ");

const QuestionsPage = () => {
  return (
    <DefaultLayout metadata={metadata}>
      <Breadcrumb
        pageName="Questions"
        subtitle="Manage the question bank and jump to grader/answer admin views."
      />
      <nav aria-label="Question administration sections" className="mb-6">
        <div className="inline-flex flex-wrap gap-1 rounded-lg border border-stone-200 bg-stone-100 p-1 dark:border-slate-700 dark:bg-slate-950">
          {QUESTION_ADMIN_LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              aria-current={link.isCurrent ? "page" : undefined}
              className={getQuestionAdminLinkClassName(link.isCurrent)}
            >
              {link.label}
            </Link>
          ))}
        </div>
      </nav>
      <QuestionsList />
    </DefaultLayout>
  );
};

export default QuestionsPage;
