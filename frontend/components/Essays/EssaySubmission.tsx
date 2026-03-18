"use client";

import React, { useEffect, useMemo, useRef, useState } from "react";
import { FaUpload, FaFileAlt, FaHistory, FaSpinner, FaSync } from "react-icons/fa";
import { essaysEngine } from "@/utils/api";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { unwrapContent } from "@/types/api";
import type { Essay, EssayEvaluationResult, EssayResource } from "@/types/essays";

interface EssayCase {
  id: string;
  topic_name: string;
  agents: unknown[];
  name?: string;
  description?: string;
  content?: string;
  explanation?: string;
  essay_id?: string;
}

interface Submission {
  resource: EssayResource;
  description: string;
  submittedAt: string;
  evaluation?: EssayEvaluationResult;
}

const isSubmissionResource = (resource: EssayResource): boolean => {
  const objectives = Array.isArray(resource.objective)
    ? resource.objective.map(item => String(item).toLowerCase())
    : [];
  if (objectives.includes("student_submission")) {
    return true;
  }

  const metadata =
    resource.metadata && typeof resource.metadata === "object"
      ? (resource.metadata as Record<string, unknown>)
      : null;
  if (metadata && typeof metadata.uploaded_at === "string" && metadata.uploaded_at.trim().length > 0) {
    return true;
  }

  return typeof resource.submittedAt === "string" && resource.submittedAt.trim().length > 0;
};

const asArray = <T,>(value: unknown): T[] => {
  const unwrapped = unwrapContent<unknown>(value);
  return Array.isArray(unwrapped) ? (unwrapped as T[]) : [];
};

const createIdentifier = () => {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `essay-${Math.random().toString(36).slice(2, 10)}`;
};

const formatStrategy = (strategy: string) => {
  if (!strategy) {
    return "Unknown";
  }
  const normalized = strategy.replace(/_/g, " ").toLowerCase();
  return normalized.charAt(0).toUpperCase() + normalized.slice(1);
};

const isStringArray = (value: unknown): value is string[] => {
  return Array.isArray(value) && value.every(item => typeof item === "string");
};

const parseEvaluationFromMetadata = (metadata: unknown): EssayEvaluationResult | undefined => {
  if (!metadata || typeof metadata !== "object") {
    return undefined;
  }
  const evaluation = (metadata as Record<string, unknown>).evaluation;
  if (!evaluation || typeof evaluation !== "object") {
    return undefined;
  }

  const candidate = evaluation as Record<string, unknown>;
  if (
    typeof candidate.strategy !== "string"
    || typeof candidate.verdict !== "string"
    || !isStringArray(candidate.strengths)
    || !isStringArray(candidate.improvements)
  ) {
    return undefined;
  }

  return {
    strategy: candidate.strategy,
    verdict: candidate.verdict,
    strengths: candidate.strengths,
    improvements: candidate.improvements,
  };
};

const allowedFileTypes = new Set([
  "application/pdf",
  "image/jpeg",
  "image/png",
  "image/gif",
  "image/webp",
]);

const EssaySubmission: React.FC = () => {
  const [cases, setCases] = useState<EssayCase[]>([]);
  const [selectedCase, setSelectedCase] = useState<EssayCase | null>(null);
  const [essayText, setEssayText] = useState("");
  const [essayFile, setEssayFile] = useState<File | null>(null);
  const [description, setDescription] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [evaluationResult, setEvaluationResult] = useState<EssayEvaluationResult | null>(null);
  const [evaluationError, setEvaluationError] = useState<string | null>(null);
  const [history, setHistory] = useState<Submission[]>([]);
  const [loadingCases, setLoadingCases] = useState(true);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [activeTab, setActiveTab] = useState<"submission" | "history">("submission");
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [reprocessTarget, setReprocessTarget] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [essayLookup, setEssayLookup] = useState<Record<string, Essay>>({});
  const [resourcesByEssay, setResourcesByEssay] = useState<Record<string, EssayResource[]>>({});

  const selectedEssayId = useMemo(() => {
    if (!selectedCase) {
      return null;
    }
    return selectedCase.essay_id ?? selectedCase.id;
  }, [selectedCase]);

  const selectedEssay = useMemo(() => {
    if (!selectedEssayId) {
      return undefined;
    }
    return essayLookup[selectedEssayId];
  }, [essayLookup, selectedEssayId]);

  const evaluationCriteria = useMemo(() => {
    if (!selectedEssayId) {
      return [] as EssayResource[];
    }
    const resources = resourcesByEssay[selectedEssayId] ?? [];
    return resources.filter(resource => {
      const tag = resource.objective?.[0]?.toLowerCase();
      return tag !== "student_submission";
    });
  }, [resourcesByEssay, selectedEssayId]);

  const selectedHistory = useMemo(() => {
    if (!selectedEssayId) {
      return [] as Submission[];
    }
    return history.filter(entry => entry.resource.essay_id === selectedEssayId);
  }, [history, selectedEssayId]);

  useEffect(() => {
    let active = true;
    setLoadingCases(true);
    essaysEngine
      .get("/assemblies")
      .then(res => {
        if (!active) {
          return undefined;
        }
        const raw = asArray<any>(res.data);
        if (!raw || raw.length === 0) {
          return essaysEngine.get("/essays").then(essayRes => {
            if (!active) {
              return;
            }
            const essays = asArray<Essay>(essayRes.data);
            const fallbackCases: EssayCase[] = essays.map(essay => ({
              id: essay.id ?? createIdentifier(),
              topic_name: essay.topic,
              agents: [],
              name: essay.topic,
              description: essay.explanation,
              content: essay.content,
              explanation: essay.explanation,
              essay_id: essay.id,
            }));
            setCases(fallbackCases);
          });
        }
        const mapped: EssayCase[] = raw.map((entry: any) => ({
          id: entry.id,
          topic_name: entry.topic_name,
          agents: entry.agents ?? [],
          name: entry.topic_name,
          description: entry.description ?? "",
          content: entry.content,
          explanation: entry.explanation,
          essay_id: entry.essay_id,
        }));
        setCases(mapped);
        return undefined;
      })
      .catch(err => {
        if (!active) {
          return;
        }
        console.error("Failed loading /assemblies:", err);
        setCases([]);
      })
      .finally(() => {
        if (active) {
          setLoadingCases(false);
        }
      });
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    setSelectedCase(previous => {
      if (cases.length === 0) {
        return null;
      }
      if (!previous) {
        return cases[0];
      }
      const match = cases.find(item => item.id === previous.id);
      return match ?? cases[0];
    });
  }, [cases]);

  useEffect(() => {
    setLoadingHistory(true);
    essaysEngine
      .get("/resources")
      .then(res => {
        const content = asArray<any>(res.data);
        const grouped: Record<string, EssayResource[]> = {};
        const mappedHistory: Submission[] = content.flatMap((record: any) => {
          const objectives = Array.isArray(record.objective)
            ? record.objective
            : (record.objective ? [record.objective] : []);
          const metadata = typeof record.metadata === "object" && record.metadata !== null
            ? (record.metadata as Record<string, unknown>)
            : {};
          const uploadedAt = typeof metadata.uploaded_at === "string"
            ? metadata.uploaded_at
            : (record.submittedAt ?? "");
          const descriptionMeta = typeof metadata.description === "string" ? metadata.description : "";
          const parsed: EssayResource = {
            id: record.id,
            objective: objectives,
            content: record.content ?? undefined,
            url: record.url ?? undefined,
            essay_id: record.essay_id,
            file_name: record.file_name ?? undefined,
            content_type: record.content_type ?? undefined,
            encoded_content: record.encoded_content ?? undefined,
            metadata: metadata,
            submittedAt: uploadedAt,
          };
          if (parsed.essay_id) {
            grouped[parsed.essay_id] = [...(grouped[parsed.essay_id] ?? []), parsed];
          }
          if (!isSubmissionResource(parsed)) {
            return [];
          }
          const [tag, ...details] = objectives;
          return [{
            resource: parsed,
            description: (descriptionMeta || details.join(" ") || tag || "").trim(),
            submittedAt: uploadedAt,
            evaluation: parseEvaluationFromMetadata(metadata),
          }];
        });
        setHistory(mappedHistory);
        setResourcesByEssay(grouped);
      })
      .catch(err => {
        console.error("Failed to load resources", err);
        setHistory([]);
        setResourcesByEssay({});
      })
      .finally(() => setLoadingHistory(false));
  }, []);

  useEffect(() => {
    essaysEngine
      .get("/essays")
      .then(res => {
        const items = asArray<Essay>(res.data);
        const lookup: Record<string, Essay> = {};
        items.forEach(item => {
          if (item.id) {
            lookup[item.id] = item;
          }
        });
        setEssayLookup(lookup);
      })
      .catch(err => console.warn("Could not load essays for reference text:", err));
  }, []);

  useEffect(() => {
    setEvaluationResult(null);
    setEvaluationError(null);
  }, [selectedCase?.id]);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (!event.target.files || !event.target.files[0]) {
      setEssayFile(null);
      return;
    }

    const nextFile = event.target.files[0];
    if (!allowedFileTypes.has(nextFile.type)) {
      setUploadError("Please upload a PDF or image file (PNG, JPG, GIF, or WebP).");
      setEssayFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
      return;
    }

    setUploadError(null);
    setEssayFile(nextFile);
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    const trimmedEssay = essayText.trim();
    if (!selectedCase || (!trimmedEssay && !essayFile)) {
      setEvaluationError("Please provide essay text or upload a valid file before submitting.");
      return;
    }

    setSubmitting(true);
    setEvaluationResult(null);
    setEvaluationError(null);

    const essayIdForCase = selectedEssayId ?? selectedCase.id;
    const objectives = description ? ["student_submission", description] : ["student_submission"];

    const formData = new FormData();
    formData.append("essay_id", essayIdForCase);
    formData.append("objective", JSON.stringify(objectives));
    if (description) {
      formData.append("description", description);
    }
    if (trimmedEssay) {
      formData.append("submission_text", trimmedEssay);
    }
    if (essayFile) {
      formData.append("file", essayFile);
    }

    let storedResource: EssayResource | null = null;
    let evaluationRecord: EssayEvaluationResult | null = null;

    try {
      const resourceResponse = await essaysEngine.post("/resources/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      storedResource = unwrapContent<EssayResource>(resourceResponse.data);
    } catch (error) {
      console.error("Failed to submit essay resource", error);
      setEvaluationError("We couldn't submit your essay right now. Please try again.");
      setSubmitting(false);
      return;
    }

    const baseEssay = selectedEssay;
    const submissionContent = storedResource?.content ?? trimmedEssay;
    const submissionIdentifier = storedResource?.id ?? createIdentifier();
    const evaluationEssay = {
      id: submissionIdentifier,
      topic: baseEssay?.topic || selectedCase.topic_name || "Essay Submission",
      content: submissionContent || "",
      explanation: baseEssay?.explanation || selectedCase.explanation || "",
      theme: baseEssay?.theme,
      file_url: baseEssay?.file_url,
      content_file_location: (baseEssay as Record<string, unknown> | undefined)?.content_file_location,
      assembly_id: selectedCase.id,
    };

    const evaluationResources = evaluationCriteria;

    try {
      const evaluationResponse = await essaysEngine.post<EssayEvaluationResult>("/grader/interaction", {
        case_id: selectedCase.id,
        essay: evaluationEssay,
        resources: evaluationResources,
      });
      evaluationRecord = evaluationResponse.data;
      setEvaluationResult(evaluationRecord);
      setEvaluationError(null);
    } catch (error) {
      console.error("Failed to evaluate essay submission", error);
      setEvaluationResult(null);
      setEvaluationError("We couldn't evaluate your essay right now. Please try again.");
    } finally {
      setSubmitting(false);
    }

    if (storedResource) {
      if (evaluationRecord) {
        const existingMetadata =
          storedResource.metadata && typeof storedResource.metadata === "object"
            ? (storedResource.metadata as Record<string, unknown>)
            : {};
        const metadataWithEvaluation: Record<string, unknown> = {
          ...existingMetadata,
          evaluation: evaluationRecord,
        };

        try {
          await essaysEngine.put(`/resources/${storedResource.id}`, {
            id: storedResource.id,
            essay_id: storedResource.essay_id,
            objective: storedResource.objective,
            content: storedResource.content,
            url: storedResource.url,
            file_name: storedResource.file_name,
            content_type: storedResource.content_type,
            encoded_content: storedResource.encoded_content,
            metadata: metadataWithEvaluation,
          });
          storedResource = { ...storedResource, metadata: metadataWithEvaluation };
        } catch (error) {
          console.warn("Failed to persist evaluation metadata", error);
        }
      }

      const nextResources = [...(resourcesByEssay[essayIdForCase] ?? []), storedResource];
      setResourcesByEssay(previous => ({ ...previous, [essayIdForCase]: nextResources }));
      const submission: Submission = {
        resource: storedResource,
        description,
        submittedAt:
          (typeof storedResource.metadata?.uploaded_at === "string"
            ? storedResource.metadata.uploaded_at
            : new Date().toISOString()),
        evaluation: evaluationRecord ?? undefined,
      };
      setHistory(previous => [submission, ...previous]);
      setEssayText("");
      setEssayFile(null);
      setDescription("");
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
      setUploadError(null);
      setActiveTab("history");
    }
  };

  const triggerReevaluation = async (essayId: string, targetId: string) => {
    setReprocessTarget(targetId);
    try {
      const response = await essaysEngine.post(`/essays/${essayId}/evaluate`);
      const evaluation = unwrapContent<EssayEvaluationResult>(response.data);
      setEvaluationResult(evaluation);
      setEvaluationError(null);
      if (targetId !== "current") {
        const targetEntry = history.find(entry => entry.resource.id === targetId);
        if (targetEntry) {
          const existingMetadata =
            targetEntry.resource.metadata && typeof targetEntry.resource.metadata === "object"
              ? (targetEntry.resource.metadata as Record<string, unknown>)
              : {};
          const metadataWithEvaluation: Record<string, unknown> = {
            ...existingMetadata,
            evaluation,
          };

          try {
            await essaysEngine.put(`/resources/${targetEntry.resource.id}`, {
              id: targetEntry.resource.id,
              essay_id: targetEntry.resource.essay_id,
              objective: targetEntry.resource.objective,
              content: targetEntry.resource.content,
              url: targetEntry.resource.url,
              file_name: targetEntry.resource.file_name,
              content_type: targetEntry.resource.content_type,
              encoded_content: targetEntry.resource.encoded_content,
              metadata: metadataWithEvaluation,
            });
          } catch (error) {
            console.warn("Failed to persist re-evaluation metadata", error);
          }
        }
      }
      setHistory(previous =>
        previous.map(entry =>
          entry.resource.essay_id === essayId
            ? {
              ...entry,
              resource: targetId !== "current" && entry.resource.id === targetId
                ? {
                  ...entry.resource,
                  metadata: {
                    ...(entry.resource.metadata && typeof entry.resource.metadata === "object"
                      ? entry.resource.metadata
                      : {}),
                    evaluation,
                  },
                }
                : entry.resource,
              evaluation,
            }
            : entry,
        ),
      );
    } catch (error) {
      console.error("Failed to re-evaluate essay", error);
      setEvaluationError("Re-evaluation failed. Please try again.");
    } finally {
      setReprocessTarget(null);
    }
  };

  if (loadingCases) {
    return (
      <div className="w-full h-[60vh] flex flex-col justify-center items-center">
        <FaSpinner className="animate-spin text-4xl text-cyan-500 mb-4" />
        <span className="text-xl text-cyan-700 font-bold">Loading essay themes...</span>
      </div>
    );
  }

  return (
    <div className="w-full max-w-4xl mx-auto p-4">
      <h2 className="text-3xl font-extrabold mb-4 flex items-center gap-2">
        ✍️ Submit Your Essay Adventure!
      </h2>
      <div className="mb-6">
        <label className="block font-semibold mb-2 text-lg flex items-center gap-2">
          🎯 Pick Your Mission (Essay Case)
        </label>
        {loadingCases ? (
          <div className="flex items-center gap-2 text-cyan-600">
            <FaSpinner className="animate-spin" /> Loading cases...
          </div>
        ) : cases.length === 0 ? (
          <div className="text-red-600 font-bold">No essay cases available. Please try again later.</div>
        ) : (
          <select
            className="w-full rounded-2xl border-2 border-cyan-300 px-3 py-2 text-lg bg-cyan-50 dark:bg-cyan-900 focus:border-green-400 focus:ring-2 focus:ring-green-200"
            value={selectedCase?.id || ""}
            onChange={(event: React.ChangeEvent<HTMLSelectElement>) => {
              const next = cases.find(ca => ca.id === event.target.value) || null;
              setSelectedCase(next);
            }}
          >
            <option value="">-- 🚀 Choose your challenge --</option>
            {cases.map(ca => (
              <option key={ca.id} value={ca.id}>
                📝 {ca.name || ca.topic_name || "Untitled"}
              </option>
            ))}
          </select>
        )}
      </div>
      <div className="mb-6 flex gap-3">
        <button
          type="button"
          onClick={() => setActiveTab("submission")}
          className={`rounded-full px-4 py-2 text-sm font-semibold transition-colors ${
            activeTab === "submission"
              ? "bg-cyan-500 text-white shadow"
              : "bg-slate-200 text-slate-600 hover:bg-slate-300"
          }`}
        >
          ✏️ Submit Essay
        </button>
        <button
          type="button"
          onClick={() => setActiveTab("history")}
          className={`rounded-full px-4 py-2 text-sm font-semibold transition-colors ${
            activeTab === "history"
              ? "bg-cyan-500 text-white shadow"
              : "bg-slate-200 text-slate-600 hover:bg-slate-300"
          }`}
        >
          <FaHistory className="inline mr-1" /> View History
        </button>
      </div>
      {activeTab === "submission" ? (
        <>
          {selectedCase && (
            <div className="mb-8 grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="rounded-2xl border-2 border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-900/40 p-4 overflow-y-auto max-h-[360px] prose prose-sm md:prose-base dark:prose-invert">
                <h3 className="text-lg font-bold mb-2">📄 Reference Text</h3>
                <div className="break-words">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {selectedEssay?.content || selectedCase.content || "No reference text available."}
                  </ReactMarkdown>
                </div>
              </div>
              <div className="rounded-2xl border-2 border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-900/40 p-4 overflow-y-auto max-h-[360px] prose prose-sm md:prose-base dark:prose-invert">
                <h3 className="text-lg font-bold mb-2">🧭 Instructions / Rubric</h3>
                <div className="break-words">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {selectedEssay?.explanation || selectedCase.explanation || selectedCase.description || "No instructions available."}
                  </ReactMarkdown>
                </div>
                {evaluationCriteria.length === 0 && (
                  <p className="mt-4 text-sm text-green-700/80 dark:text-green-200/80">
                    No specific evaluation criteria found for this essay. The graders will rely on their default strategy.
                  </p>
                )}
              </div>
            </div>
          )}
          <form onSubmit={handleSubmit} className="bg-white dark:bg-boxdark rounded-2xl shadow-lg border-2 border-cyan-100 dark:border-cyan-800 p-8 mb-8 flex flex-col gap-6">
            <label className="font-semibold flex items-center gap-2 text-green-700">
              🏷️ Give your essay a catchy description!
            </label>
            <input
              type="text"
              className="rounded-2xl border-2 border-green-200 px-3 py-2 text-lg bg-green-50 dark:bg-green-900 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-200"
              value={description}
              onChange={event => setDescription(event.target.value)}
              placeholder="e.g. My Epic Argument for Pizza Fridays"
            />
            <label className="font-semibold flex items-center gap-2 text-blue-700">
              ✏️ Write your essay masterpiece below!
            </label>
            <textarea
              className="rounded-2xl border-2 border-blue-200 px-3 py-2 text-lg min-h-[120px] bg-blue-50 dark:bg-blue-900 focus:border-yellow-400 focus:ring-2 focus:ring-yellow-200"
              value={essayText}
              onChange={event => setEssayText(event.target.value)}
              placeholder="Once upon a time... (or paste your essay here!)"
            />
            <div className="flex flex-col md:flex-row md:items-center gap-4">
              <div className="flex items-center gap-2">
                <label className="font-semibold flex items-center gap-2 text-pink-700">
                  📎 Upload essay file (PDF or image)
                </label>
                <input
                  type="file"
                  accept=".pdf,image/*"
                  ref={fileInputRef}
                  onChange={handleFileChange}
                  className="rounded border-2 border-pink-200 px-2 py-1 bg-pink-50 dark:bg-pink-900 focus:border-cyan-400"
                />
              </div>
              {essayFile ? (
                <span className="text-green-700 flex items-center gap-1">
                  <FaFileAlt /> {essayFile.name}
                </span>
              ) : null}
              {uploadError ? <span className="text-sm text-red-600">{uploadError}</span> : null}
            </div>
            <button
              type="submit"
              className="mt-4 bg-gradient-to-br from-green-400 to-cyan-400 text-white font-bold px-8 py-4 rounded-full shadow-lg hover:scale-105 transition-all duration-200 flex items-center gap-3 justify-center text-xl"
              disabled={submitting || !selectedCase}
            >
              {submitting ? <FaSpinner className="animate-spin" /> : <FaUpload />}
              {" "}
              {submitting ? "Sending to the wizards..." : "Submit Essay!"}
            </button>
          </form>
          <div className="mb-8">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-2xl font-bold flex items-center gap-2">🔍 Evaluation Results</h3>
              {selectedEssayId && (
                <button
                  type="button"
                  onClick={() => triggerReevaluation(selectedEssayId, "current")}
                  className="flex items-center gap-2 rounded-full border border-cyan-400 px-4 py-2 text-sm font-semibold text-cyan-600 hover:bg-cyan-50"
                  disabled={reprocessTarget !== null}
                >
                  {reprocessTarget === "current" ? (
                    <FaSpinner className="animate-spin" />
                  ) : (
                    <FaSync />
                  )}
                  Re-run evaluation
                </button>
              )}
            </div>
            {submitting && (
              <div className="text-cyan-600 flex items-center gap-2">
                <FaSpinner className="animate-spin" /> Evaluating essay...
              </div>
            )}
            {evaluationError && (
              <div className="mt-3 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                {evaluationError}
              </div>
            )}
            {!submitting && !evaluationResult && !evaluationError && (
              <div className="rounded-2xl border-2 border-dashed border-slate-300 p-6 text-center text-sm text-slate-500">
                No evaluation yet. Submit your essay to get magical feedback! ✨
              </div>
            )}
            {evaluationResult && (
              <div className="mt-4 rounded-2xl border-2 border-cyan-200 bg-cyan-50 dark:bg-cyan-900 shadow p-6">
                <div className="flex flex-col gap-2">
                  <span className="text-sm font-semibold uppercase text-cyan-600">
                    Strategy: {formatStrategy(evaluationResult.strategy)}
                  </span>
                  <p className="text-base text-slate-900 whitespace-pre-line dark:text-slate-100">
                    {evaluationResult.verdict}
                  </p>
                </div>
                <div className="mt-6 grid gap-4 md:grid-cols-2">
                  <div>
                    <h4 className="text-sm font-semibold text-green-700">Strengths</h4>
                    <ul className="mt-2 space-y-2 text-sm text-slate-700 dark:text-slate-200">
                      {evaluationResult.strengths.map((item, index) => (
                        <li key={`strength-${index}`} className="rounded-lg bg-white/80 dark:bg-white/10 px-3 py-2 shadow-sm">
                          {item}
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-orange-700">Improvements</h4>
                    <ul className="mt-2 space-y-2 text-sm text-slate-700 dark:text-slate-200">
                      {evaluationResult.improvements.map((item, index) => (
                        <li key={`improvement-${index}`} className="rounded-lg bg-white/80 dark:bg-white/10 px-3 py-2 shadow-sm">
                          {item}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            )}
          </div>
        </>
      ) : (
        <div>
          <h3 className="text-2xl font-bold mb-2 flex items-center gap-2">
            <FaHistory /> Submission History
          </h3>
          {loadingHistory ? (
            <div className="text-cyan-600 flex items-center gap-2">
              <FaSpinner className="animate-spin" /> Loading history...
            </div>
          ) : !selectedCase ? (
            <div className="text-gray-500">Select an essay mission to review its submission history.</div>
          ) : selectedHistory.length === 0 ? (
            <div className="text-gray-500">No submissions yet. Be the first to submit your essay adventure! 🚀</div>
          ) : (
            <ul className="divide-y">
              {selectedHistory.map(entry => (
                <li key={entry.resource.id} className="py-4">
                  <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                    <div>
                      <span className="font-semibold">
                        {entry.submittedAt ? new Date(entry.submittedAt).toLocaleString() : "Unknown date"}
                      </span>{" "}-
                      {entry.resource.file_name ? (
                        <span className="text-green-700 flex items-center gap-1">
                          <FaFileAlt />
                          {entry.resource.file_name}
                        </span>
                      ) : (
                        <span className="text-blue-700">📝 Written Essay</span>
                      )}
                      <div className="text-gray-600 text-sm italic">
                        {entry.description || "No description."}
                      </div>
                    </div>
                    <div className="flex flex-col md:items-end gap-2 text-sm text-slate-600 dark:text-slate-200">
                      {entry.evaluation ? (
                        <>
                          <span className="font-semibold text-cyan-700">
                            Strategy: {formatStrategy(entry.evaluation.strategy)}
                          </span>
                          <span className="whitespace-pre-line max-w-xl text-left md:text-right">
                            {entry.evaluation.verdict}
                          </span>
                        </>
                      ) : (
                        <span className="text-xs text-gray-400">Evaluation not available.</span>
                      )}
                      <button
                        type="button"
                        onClick={() => entry.resource.essay_id && triggerReevaluation(entry.resource.essay_id, entry.resource.id)}
                        className="flex items-center gap-2 rounded-full border border-cyan-400 px-3 py-1 text-xs font-semibold text-cyan-600 hover:bg-cyan-50"
                        disabled={reprocessTarget !== null || !entry.resource.essay_id}
                      >
                        {reprocessTarget === entry.resource.id ? (
                          <FaSpinner className="animate-spin" />
                        ) : (
                          <FaSync />
                        )}
                        Re-run evaluation
                      </button>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
};

export default EssaySubmission;
