// Updated SummaryData type to reflect the nested structure
export type SummaryData = {
  score: number;
  rationale: string;
  sub_criteria?: {
    score: number;
    rationale: string;
  };
};

// Updated Transcription type
export type Transcription = {
  id: string;
  filename: string;
  content: string;
  classification: string;
  successfulCall: string;
  identifiedClient: string;
  summaryData: SummaryData;
  improvementSuggestion: string;
  metadata: {
    file_name: string;
    file_size: number;
    transcription_duration: number;
    date?: string;
    duration?: string;
  };
};
