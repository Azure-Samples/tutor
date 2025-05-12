import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import QuestionsList from "@/components/Lists/Questions";
import { Metadata } from "next";
import DefaultLayout from "@/components/Layouts/DefaultLayout";

export const metadata: Metadata = {
  title: "Questions | Tutor App",
  description: "Manage and review questions for the Tutor application.",
};

const QuestionsPage = () => {
  return (
    <DefaultLayout metadata={metadata}>
      <Breadcrumb pageName="Questions" />
      <QuestionsList />
    </DefaultLayout>
  );
};

export default QuestionsPage;