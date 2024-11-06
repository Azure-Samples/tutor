"use client";
import React, { useState, useEffect, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import { Transcription } from "@/types/transcription";
import { transcriptionApi } from "@/utils/api";
import { useTranscriptionContext } from "@/utils/transcriptionContext";

const ListLayout: React.FC = () => {
  const { id } = useParams();
  const router = useRouter();
  const { transcriptions, setTranscriptions, setSelectedTranscription } = useTranscriptionContext();
  const [isLoading, setIsLoading] = useState(false);

  const decodedId = decodeURIComponent(id);
  const cachedTranscriptions = transcriptions[decodedId] || [];

  const fetchTranscriptions = useCallback(async (specialistId: string) => {
    setIsLoading(true);
    try {
      // Fetch transcription data only (without evaluations)
      const transcriptionResponse = await transcriptionApi.get(`/specialist-data?specialist=${encodeURIComponent(specialistId)}`);
      const specialistsData = transcriptionResponse.data?.result;

      if (!Array.isArray(specialistsData) || specialistsData.length === 0) {
        console.error("No specialist data found for this ID:", specialistsData);
        return;
      }

      const specialist = specialistsData[0]; // Assuming the first specialist matches the requested ID
      const transcriptionsArray = specialist.transcriptions || [];
      if (!Array.isArray(transcriptionsArray)) {
        console.error("Transcriptions data structure is not as expected:", specialistsData);
        return;
      }

      // Set transcriptions without evaluations
      setTranscriptions(specialistId, transcriptionsArray);
    } catch (error) {
      console.error("Failed to fetch transcriptions:", error);
    } finally {
      setIsLoading(false);
    }
  }, [setTranscriptions]);

  useEffect(() => {
    if (cachedTranscriptions.length > 0) {
      setIsLoading(false);
    } else {
      fetchTranscriptions(decodedId);
    }
  }, [decodedId, cachedTranscriptions.length, fetchTranscriptions]);

  const handleTranscriptionClick = (transcription: Transcription) => {
    setSelectedTranscription(transcription);
    router.push(`/transcriptions/${transcription.id}`);
  };

  return (
    <div className="p-6 bg-white dark:bg-gray-800 min-h-screen">
      <h1 className="text-2xl font-bold mb-4 text-black dark:text-white">
        {decodedId} Evaluations
      </h1>
      {isLoading ? (
        <p className="text-gray-500 dark:text-gray-400">Loading...</p>
      ) : (
        <>
          <h3 className="font-bold my-4 text-black dark:text-white">
            Transcriptions
          </h3>
          {cachedTranscriptions.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {cachedTranscriptions.map((transcription) => (
                <div 
                  key={transcription.id} 
                  className="border p-4 rounded-lg shadow cursor-pointer"
                  onClick={() => handleTranscriptionClick(transcription)}
                >
                  <p className="font-medium text-lg">{transcription.id}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 dark:text-gray-400">
              No evaluation found for this specialist.
            </p>
          )}
        </>
      )}
    </div>
  );
};

export default ListLayout;
