"use client";

import { useCallback, useState } from "react";

import type { Grader } from "@/types/grader";
import { unwrapContent } from "@/types/api";
import { questionsEngine } from "@/utils/api";

export const useQuestionsGraders = () => {
  const [graders, setGraders] = useState<Grader[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const refresh = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const res = await questionsEngine.get("/graders");
      const payload = unwrapContent<Grader[]>(res.data);
      setGraders(Array.isArray(payload) ? payload : []);
    } catch {
      setGraders([]);
      setError("Could not load graders.");
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    graders,
    setGraders,
    loading,
    error,
    refresh,
  };
};
