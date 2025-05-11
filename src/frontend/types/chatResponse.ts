import type { Question } from "./question";
import type { Answer } from "./answer";

export type ChatResponse = {
  case_id: string;
  question: Question;
  answer: Answer;
};
