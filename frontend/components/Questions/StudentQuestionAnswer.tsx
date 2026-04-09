"use client";

import axios, { CanceledError } from "axios";
import { useEffect, useMemo, useState } from "react";

import type { Answer } from "@/types/answer";
import type { Assembly } from "@/types/assembly";
import type { ChatResponse } from "@/types/chatResponse";
import type { Question } from "@/types/question";
import type { QuestionEvaluationResult } from "@/types/questionEvaluation";
import { questionsEngine } from "@/utils/api";

const resolveQuestionKey = (question: Question) => question.id ?? question.topic ?? "";
const RESPONDENT = "student";

const createAnswerPayload = (question: Question, draft: string): Answer => {
  const questionId = resolveQuestionKey(question) || `question-${Date.now()}`;
  return {
    id:
      typeof crypto !== "undefined" && "randomUUID" in crypto
        ? crypto.randomUUID()
        : `draft-${Date.now()}`,
    text: draft,
    question_id: questionId,
    respondent: RESPONDENT,
  };
};

const StudentQuestionAnswer = () => {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [assemblies, setAssemblies] = useState<Assembly[]>([]);
  const [selectedQuestionId, setSelectedQuestionId] = useState<string>();
  const [selectedAssemblyId, setSelectedAssemblyId] = useState<string>();
  const [questionsLoading, setQuestionsLoading] = useState(false);
  const [assembliesLoading, setAssembliesLoading] = useState(false);
  const [questionsError, setQuestionsError] = useState<string | null>(null);
  const [assembliesError, setAssembliesError] = useState<string | null>(null);
  const [answerDraft, setAnswerDraft] = useState("");
  const [evaluation, setEvaluation] = useState<QuestionEvaluationResult | null>(null);
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [evaluationError, setEvaluationError] = useState<string | null>(null);

  const selectedQuestion = useMemo(
    () => questions.find((question) => resolveQuestionKey(question) === selectedQuestionId) || null,
    [questions, selectedQuestionId],
  );

  const selectedAssembly = useMemo(
    () => assemblies.find((assembly) => assembly.id === selectedAssemblyId) || null,
    [assemblies, selectedAssemblyId],
  );

  useEffect(() => {
    let active = true;
    setQuestionsLoading(true);
    questionsEngine
      .get<Question[]>("/questions")
      .then(({ data }) => {
        if (!active) {
          return;
        }
        const list = Array.isArray(data) ? data : [];
        setQuestions(list);
        setQuestionsError(null);
        const firstQuestion = list[0];
        const initialId = firstQuestion ? resolveQuestionKey(firstQuestion) : undefined;
        if (initialId) {
          setSelectedQuestionId(initialId);
        }
      })
      .catch(() => {
        if (!active) {
          return;
        }
        setQuestions([]);
        setQuestionsError("We could not load the questions. Refresh and try again.");
      })
      .finally(() => {
        if (active) {
          setQuestionsLoading(false);
        }
      });
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    let active = true;
    setAssembliesLoading(true);
    questionsEngine
      .get<Assembly[]>("/assemblies")
      .then(({ data }) => {
        if (!active) {
          return;
        }
        const list = Array.isArray(data) ? data : [];
        setAssemblies(list);
        setAssembliesError(null);
        const firstAssembly = list[0];
        if (firstAssembly?.id) {
          setSelectedAssemblyId(firstAssembly.id);
        }
      })
      .catch(() => {
        if (!active) {
          return;
        }
        setAssemblies([]);
        setAssembliesError("We could not load the evaluator assemblies. Refresh and try again.");
      })
      .finally(() => {
        if (active) {
          setAssembliesLoading(false);
        }
      });
    return () => {
      active = false;
    };
  }, []);

  // Debounce evaluation so graders run only after the student pauses typing.
  useEffect(() => {
    if (!selectedQuestion || !selectedAssembly) {
      return;
    }

    const draft = answerDraft.trim();
    if (draft.length === 0) {
      setEvaluation(null);
      setEvaluationError(null);
      setIsEvaluating(false);
      return;
    }

    if (!selectedAssembly.id) {
      setEvaluation(null);
      setEvaluationError("The selected evaluator assembly is missing an identifier.");
      return;
    }

    let active = true;
    const controller = new AbortController();
    const timeoutId = window.setTimeout(async () => {
      if (!active) {
        return;
      }
      setIsEvaluating(true);
      try {
        const questionId = resolveQuestionKey(selectedQuestion) || `question-${Date.now()}`;
        const questionPayload = { ...selectedQuestion, id: questionId };
        const answerPayload = createAnswerPayload(questionPayload, draft);
        const payload: ChatResponse = {
          case_id: selectedAssembly.id,
          question: questionPayload,
          answer: answerPayload,
        };
        const { data } = await questionsEngine.post<QuestionEvaluationResult>(
          "/grader/interaction",
          payload,
          { signal: controller.signal },
        );
        if (!active) {
          return;
        }
        setEvaluation(data);
        setEvaluationError(null);
      } catch (error) {
        if (!active) {
          return;
        }
        if (error instanceof CanceledError || (error as Error).name === "CanceledError") {
          return;
        }
        if (axios.isAxiosError(error) && error.code === "ERR_CANCELED") {
          return;
        }
        setEvaluationError("We could not evaluate your answer right now. Try again shortly.");
      } finally {
        if (active) {
          setIsEvaluating(false);
        }
      }
    }, 600);

    return () => {
      active = false;
      controller.abort();
      window.clearTimeout(timeoutId);
    };
  }, [answerDraft, selectedAssembly, selectedQuestion]);

  return (
    <div className="mx-auto mt-8 max-w-3xl rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
      <div className="flex flex-col gap-6">
        <header className="flex flex-col gap-2">
          <h2 className="text-2xl font-semibold text-slate-900">Answer Practice Questions</h2>
          <p className="text-sm text-slate-500">
            Choose a case, craft your response, and watch the graders react in real time.
          </p>
        </header>

        <section className="grid gap-4 md:grid-cols-2">
          <div className="flex flex-col gap-2">
            <label className="text-sm font-semibold text-slate-700" htmlFor="question-select">
              Question
            </label>
            <select
              id="question-select"
              className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200"
              value={selectedQuestionId ?? ""}
              onChange={(event) => {
                setSelectedQuestionId(event.target.value);
                setAnswerDraft("");
                setEvaluation(null);
                setEvaluationError(null);
              }}
              disabled={questionsLoading || questions.length === 0}
            >
              {questions.map((question) => {
                const value = resolveQuestionKey(question);
                if (!value) {
                  return null;
                }
                return (
                  <option key={value} value={value}>
                    {question.topic || question.question || value}
                  </option>
                );
              })}
            </select>
            {questionsLoading && <p className="text-xs text-slate-400">Loading questions…</p>}
            {questionsError && <p className="text-xs text-red-600">{questionsError}</p>}
          </div>

          <div className="flex flex-col gap-2">
            <label className="text-sm font-semibold text-slate-700" htmlFor="assembly-select">
              Evaluator Assembly
            </label>
            <select
              id="assembly-select"
              className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200"
              value={selectedAssemblyId ?? ""}
              onChange={(event) => {
                setSelectedAssemblyId(event.target.value);
                setEvaluation(null);
                setEvaluationError(null);
              }}
              disabled={assembliesLoading || assemblies.length === 0}
            >
              {assemblies.map((assembly) => (
                <option key={assembly.id} value={assembly.id}>
                  {assembly.topic_name || assembly.id}
                </option>
              ))}
            </select>
            {assembliesLoading && <p className="text-xs text-slate-400">Loading evaluators…</p>}
            {assembliesError && <p className="text-xs text-red-600">{assembliesError}</p>}
          </div>
        </section>

        {selectedQuestion ? (
          <section className="rounded-lg border border-slate-200 bg-slate-50 p-4">
            <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Prompt</h3>
            <p className="mt-2 text-base text-slate-900">{selectedQuestion.question}</p>
            {selectedQuestion.explanation && (
              <p className="mt-3 text-sm text-slate-600">{selectedQuestion.explanation}</p>
            )}
          </section>
        ) : (
          <section className="rounded-lg border border-dashed border-slate-300 p-8 text-center text-slate-500">
            No question is available right now.
          </section>
        )}

        <section className="flex flex-col gap-3">
          <label className="text-sm font-semibold text-slate-700" htmlFor="answer-input">
            Your Answer
          </label>
          <textarea
            id="answer-input"
            className="min-h-[140px] w-full rounded-lg border border-slate-300 px-3 py-2 text-base text-slate-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200"
            placeholder="Start typing your answer…"
            value={answerDraft}
            onChange={(event) => setAnswerDraft(event.target.value)}
            disabled={!selectedQuestion || !selectedAssembly}
          />
          <p className="text-xs text-slate-500">
            Feedback appears automatically after a short pause. Keep typing to refine your response.
          </p>
        </section>

        <section className="flex flex-col gap-3">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-slate-900">Evaluation</h3>
            {isEvaluating && <span className="text-xs font-medium text-blue-600">Evaluating…</span>}
          </div>
          {evaluationError && <p className="text-sm text-red-600">{evaluationError}</p>}
          {evaluation ? (
            <div className="space-y-4">
              <div className="rounded-lg border border-slate-200 bg-white p-4">
                <p className="text-sm font-semibold uppercase tracking-wide text-slate-500">
                  Overall
                </p>
                <p className="mt-2 whitespace-pre-line text-base text-slate-900">
                  {evaluation.overall}
                </p>
              </div>
              <div className="grid gap-4 md:grid-cols-2">
                {evaluation.dimensions.map((dimension) => (
                  <article
                    key={dimension.dimension}
                    className="rounded-lg border border-slate-200 bg-white p-4"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <p className="text-sm font-semibold text-slate-800">
                          {dimension.dimension}
                        </p>
                        <p className="mt-1 text-sm text-slate-600">{dimension.verdict}</p>
                      </div>
                      <span className="text-xs font-medium text-slate-500">
                        {Math.round(dimension.confidence * 100)}% confidence
                      </span>
                    </div>
                    {dimension.notes.length > 0 && (
                      <ul className="mt-3 list-disc space-y-1 pl-5 text-sm text-slate-600">
                        {dimension.notes.map((note, index) => (
                          <li key={`${dimension.dimension}-${index}`}>{note}</li>
                        ))}
                      </ul>
                    )}
                  </article>
                ))}
              </div>
            </div>
          ) : (
            <div className="rounded-lg border border-dashed border-slate-300 p-6 text-center text-sm text-slate-500">
              {answerDraft.trim().length === 0
                ? "Start typing to get instant feedback from the graders."
                : isEvaluating
                  ? "Crunching your answer with the graders…"
                  : "Waiting for feedback."}
            </div>
          )}
        </section>
      </div>
    </div>
  );
};

export default StudentQuestionAnswer;
