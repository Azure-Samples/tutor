import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import DefaultLayout from "@/components/Layouts/DefaultLayout";
import type { Metadata } from "next";

import EvaluationDashboard from "./_components/EvaluationDashboard";

export const metadata: Metadata = {
  title: "Tutor | Evaluation",
  description: "Evaluation datasets, run launch, and route capability status for Tutor.",
};

const EvaluationPage = () => (
  <DefaultLayout metadata={metadata}>
    <Breadcrumb
      pageName="Evaluation"
      subtitle="Inspect datasets, start evaluation runs, and verify route capability status."
    />
    <EvaluationDashboard />
  </DefaultLayout>
);

export default EvaluationPage;
