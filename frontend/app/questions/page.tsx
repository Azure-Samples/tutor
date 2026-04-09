import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import DefaultLayout from "@/components/Layouts/DefaultLayout";
import StudentQuestionAnswer from "@/components/Questions/StudentQuestionAnswer";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Questions | Tutor App",
  description: "Manage and review questions for the Tutor application.",
};

const QuestionsPage = () => {
  return (
    <DefaultLayout metadata={metadata}>
      <Breadcrumb pageName="Questions" />
      <StudentQuestionAnswer />
    </DefaultLayout>
  );
};

export default QuestionsPage;
