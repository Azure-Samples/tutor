import type { Metadata } from "next";

import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import DefaultLayout from "@/components/Layouts/DefaultLayout";
import AnswersList from "@/components/Lists/Answers";

export const metadata: Metadata = {
  title: "Question Answers | Tutor",
  description: "Manage stored answers used by the questions evaluation workflow.",
};

const QuestionAnswersPage = () => {
  return (
    <DefaultLayout>
      <Breadcrumb
        pageName="Question Answers"
        subtitle="Create and manage answer records for evaluation workflows."
      />
      <AnswersList />
    </DefaultLayout>
  );
};

export default QuestionAnswersPage;
