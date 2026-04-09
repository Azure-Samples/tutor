import type { Transcription } from "@/types/transcription";
import type React from "react";

type TranscriptionProps = {
  transcription: Transcription;
};

const TranscriptionView: React.FC<TranscriptionProps> = ({ transcription }) => {
  const mainText =
    (typeof transcription.transcription === "string" && transcription.transcription) ||
    (typeof transcription.content === "string" && transcription.content) ||
    (typeof transcription.text === "string" && transcription.text) ||
    "No transcription content available.";

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold text-black dark:text-white">Transcription</h2>
      <div className="rounded-sm border border-stroke bg-gray-2 p-4 dark:border-strokedark dark:bg-meta-4">
        <p className="whitespace-pre-wrap text-body dark:text-bodydark">{mainText}</p>
      </div>
    </div>
  );
};

export default TranscriptionView;
