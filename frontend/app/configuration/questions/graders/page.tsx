import type { Metadata } from "next";

import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import DefaultLayout from "@/components/Layouts/DefaultLayout";
import GradersList from "@/components/Lists/Graders";

export const metadata: Metadata = {
  title: "Question Graders | Tutor",
  description: "Manage grader agents referenced by question evaluator assemblies.",
};

const QuestionGradersPage = () => {
  return (
    <DefaultLayout>
      <Breadcrumb pageName="Question Graders" subtitle="Create and maintain grader agents for assembly composition." />
      <GradersList />
    </DefaultLayout>
  );
};

export default QuestionGradersPage;
