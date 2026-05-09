import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import DefaultLayout from "@/components/Layouts/DefaultLayout";
import type { Metadata } from "next";

import EvaluationRunViewer from "../_components/EvaluationRunViewer";

type EvaluationRunPageProps = {
  params: Promise<{
    runId: string;
  }>;
};

export const generateMetadata = async ({ params }: EvaluationRunPageProps): Promise<Metadata> => {
  const { runId } = await params;

  return {
    title: `Evaluation Run ${runId} | Tutor`,
    description: "Evaluation run status and metadata for Tutor governance review.",
  };
};

const EvaluationRunPage = async ({ params }: EvaluationRunPageProps) => {
  const { runId } = await params;

  return (
    <DefaultLayout>
      <Breadcrumb
        pageName="Evaluation Run"
        subtitle={`Inspect run ${runId} through the APIM-backed evaluation service.`}
      />
      <EvaluationRunViewer runId={runId} />
    </DefaultLayout>
  );
};

export default EvaluationRunPage;
