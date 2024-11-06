import { Transcription } from "@/types/transcription";


export type Specialist = {
  name: string;
  role: string;
  transcriptions: Transcription[];
  performance: number;
};