"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useTranscriptionContext } from "@/utils/transcriptionContext";
import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import DefaultLayout from "@/components/Layouts/DefaultLayout";
import Transcription from "@/components/Transcriptions";
import { questionsEngine } from "@/utils/api";
import type { Transcription as TranscriptionType } from "@/types/transcription";

const TranscriptionPage: React.FC = () => {
  const { selectedTranscription } = useTranscriptionContext();
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const [routeTranscription, setRouteTranscription] = useState<TranscriptionType | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const questionId = Array.isArray(params?.id) ? params.id[0] : params?.id;

  useEffect(() => {
    if (selectedTranscription || !questionId) {
      return;
    }

    setIsLoading(true);
    questionsEngine
      .get(`/questions/${questionId}`)
      .then((response) => {
        const payload = response.data as TranscriptionType;
        setRouteTranscription(payload ?? null);
      })
      .catch(() => {
        setRouteTranscription(null);
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [questionId, selectedTranscription]);

  const handleBack = () => {
    router.back();
  };

  const transcriptionToRender = selectedTranscription ?? routeTranscription;

  if (isLoading) {
    return (
      <DefaultLayout>
        <Breadcrumb pageName="Evaluate Transcription" />
        <div className="p-6 bg-white dark:bg-gray-800">
          <p>Loading transcription...</p>
        </div>
      </DefaultLayout>
    );
  }

  if (!transcriptionToRender) {
    return (
      <DefaultLayout>
        <Breadcrumb pageName="Evaluate Transcription" />
        <button
          onClick={handleBack}
          className="mb-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Go Back
        </button>
        <div className="p-6 bg-white dark:bg-gray-800">
          <p>Transcription not found.</p>
        </div>
      </DefaultLayout>
    );
  }

  return (
    <DefaultLayout>
      <Breadcrumb pageName="Evaluate Transcription" />
      <button
        onClick={handleBack}
        className="mb-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
      >
        Back
      </button>
      <div className="p-6 bg-white dark:bg-gray-800">
        <Transcription transcription={transcriptionToRender} />
      </div>
    </DefaultLayout>
  );
};

export default TranscriptionPage;
