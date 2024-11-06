import React from "react";
import { Metadata } from "next";
import DefaultLayout from "@/components/Layouts/DefaultLayout";
import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import EvaluationJob from "@/components/ProcessEvaluation";


export const metadata: Metadata = {
  title: "Tayra | Evaluate",
  description: "Evaluate transcriptions according to a set of rules.",
};


const ExecuteTranscriptionPage = () => {
  return (
    <DefaultLayout>
      <Breadcrumb pageName={"Transcription Evaluation"} />
      <div className="flex flex-col md:flex-row justify-between gap-6 p-6">
        <EvaluationJob />
      </div>
    </DefaultLayout>
  );
};

export default ExecuteTranscriptionPage;