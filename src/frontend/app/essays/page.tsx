import DefaultLayout from "@/components/Layouts/DefaultLayout";
import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import EssaySubmission from "@/components/Essays/EssaySubmission";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Essay Evaluation | Tutor",
  description:
    "Submit, review, and receive feedback on your essays. Grow your writing and critical thinking skills with supportive, actionable insights.",
};

const EssaysPage = () => {
  return (
    <DefaultLayout>
      <Breadcrumb 
        pageName="Essay Evaluation" 
        subtitle="Submit, review, and receive feedback on your essays. Grow your writing and critical thinking skills with supportive, actionable insights." 
      />
      <EssaySubmission />
    </DefaultLayout>
  );
};

export default EssaysPage;
