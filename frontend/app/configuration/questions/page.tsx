import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import DefaultLayout from "@/components/Layouts/DefaultLayout";
import QuestionsList from "@/components/Lists/Questions";
import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Questions | Tutor App",
  description: "Manage and review questions for the Tutor application.",
};

const QuestionsPage = () => {
  return (
    <DefaultLayout metadata={metadata}>
      <Breadcrumb
        pageName="Questions"
        subtitle="Manage the question bank and jump to grader/answer admin views."
      />
      <div className="mb-6 grid grid-cols-1 gap-4 md:grid-cols-3">
        <Link
          href="/configuration/questions"
          className="rounded-2xl border-2 border-cyan-200 bg-cyan-50 px-4 py-3 text-center font-semibold text-cyan-700 transition-colors hover:bg-cyan-100 dark:bg-cyan-900 dark:text-cyan-200"
        >
          Questions
        </Link>
        <Link
          href="/configuration/questions/graders"
          className="rounded-2xl border-2 border-green-200 bg-green-50 px-4 py-3 text-center font-semibold text-green-700 transition-colors hover:bg-green-100 dark:bg-green-900 dark:text-green-200"
        >
          Graders
        </Link>
        <Link
          href="/configuration/questions/answers"
          className="rounded-2xl border-2 border-blue-200 bg-blue-50 px-4 py-3 text-center font-semibold text-blue-700 transition-colors hover:bg-blue-100 dark:bg-blue-900 dark:text-blue-200"
        >
          Answers
        </Link>
      </div>
      <QuestionsList />
    </DefaultLayout>
  );
};

export default QuestionsPage;
