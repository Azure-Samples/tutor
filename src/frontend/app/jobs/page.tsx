import React from "react";
import Link from "next/link";
import Image from "next/image";
import { Metadata } from "next";
import DefaultLayout from "@/components/Layouts/DefaultLayout";
import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";

export const metadata: Metadata = {
  title: "Tayra | Job Execution",
  description: "This is the job execution page for Tayra.",
};

const ConfigurationPage = () => {
  return (
    <DefaultLayout>
      <Breadcrumb pageName={"Job Execution"} />
      <div className="flex flex-row justify-center gap-6 p-6">

        <Link
          href="/jobs/audio-upload"
          className="flex flex-col items-center min-w-100 min-h-100 w-1/4 p-6 bg-white hover:bg-light-cyan shadow-lg rounded-lg hover:shadow-xl transition-shadow cursor-pointer text-center"
        >
            <Image
              width={250}
              height={250}
              src="/images/upload.png"
              alt="Upload Icon"
              className="mb-4"
            />
            <h3 className="text-2xl font-semibold text-gray-800">Upload</h3>
            <p className="mt-2 text-gray-600">
              Manually upload files for the blob storage.
            </p>
        </Link>

        <Link
          href="/jobs/transcribe"
          className="flex flex-col items-center min-w-100 min-h-100 w-1/4 p-6 bg-white hover:bg-light-cyan shadow-lg rounded-lg hover:shadow-xl transition-shadow cursor-pointer text-center"
        >
            <Image
              width={250}
              height={250}
              src="/images/transcription.png"
              alt="Transcription Icon"
              className="mb-4"
            />
            <h3 className="text-2xl font-semibold text-gray-800">Transcribe</h3>
            <p className="mt-2 text-gray-600">
              Transcribe files manually, allowing multiple selection criteria.
            </p>
        </Link>

        <Link
          href="/jobs/evaluate"
          className="flex flex-col items-center min-w-100 min-h-100 w-1/4 p-6 bg-white hover:bg-light-cyan shadow-lg rounded-lg hover:shadow-xl transition-shadow cursor-pointer text-center"
        >
            <Image
              width={250}
              height={250}
              src="/images/evaluation.png"
              alt="Evaluation Icon"
              className="mb-4"
            />
            <h3 className="text-2xl font-semibold text-gray-800">Evaluate</h3>
            <p className="mt-2 text-gray-600">
              Evaluate transcriptions, allowing the selection of custom rules.
            </p>
        </Link>

      </div>
    </DefaultLayout>
  );
};

export default ConfigurationPage;
