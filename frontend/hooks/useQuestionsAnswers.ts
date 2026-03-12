"use client";

import { useCallback, useState } from "react";

import type { Answer } from "@/types/answer";
import { unwrapContent } from "@/types/api";
import { questionsEngine } from "@/utils/api";

export const useQuestionsAnswers = () => {
  const [answers, setAnswers] = useState<Answer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const refresh = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const res = await questionsEngine.get("/answers");
      const payload = unwrapContent<Answer[]>(res.data);
      setAnswers(Array.isArray(payload) ? payload : []);
    } catch {
      setAnswers([]);
      setError("Could not load answers.");
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    answers,
    setAnswers,
    loading,
    error,
    refresh,
  };
};
