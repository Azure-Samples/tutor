import type { Answer } from "./answer";
import type { Question } from "./question";

export type ChatResponse = {
  case_id: string;
  question: Question;
  answer: Answer;
};
