export type Question = {
  id?: string;
  topic: string;
  question: string;
  explanation?: string | null;
  answer?: string | null;
};