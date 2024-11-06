import React from "react";
import { Metadata } from "next";
import DefaultLayout from "@/components/Layouts/DefaultLayout";
import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import TranscriptionJob from "@/components/ProcessTranscription";


export const metadata: Metadata = {
  title: "Tayra | Transcribe",
  description: "Transcribe list of audios already uploaded.",
};


const ExecuteTranscriptionPage = () => {
  return (
    <DefaultLayout>
      <Breadcrumb pageName={"Audio Transcription"} />
      <div className="flex flex-row w-full justify-between gap-6">
        <TranscriptionJob />
      </div>
    </DefaultLayout>
  );
};

export default ExecuteTranscriptionPage;