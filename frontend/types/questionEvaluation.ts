export type QuestionEvaluationStatus = "pending" | "evaluating" | "completed";

export type DimensionEvaluation = {
  dimension: string;
  verdict: string;
  confidence: number;
  notes: string[];
};

export type QuestionEvaluationResult = {
  question_id: string;
  status: QuestionEvaluationStatus;
  overall: string;
  dimensions: DimensionEvaluation[];
};
