"use client";

import { unwrapContent } from "@/types/api";
import type { Essay, EssayEvaluationResult, EssayResource } from "@/types/essays";
import { essaysEngine } from "@/utils/api";
import type React from "react";
import { useEffect, useMemo, useRef, useState } from "react";
import { FaFileAlt, FaHistory, FaSpinner, FaSync, FaUpload } from "react-icons/fa";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

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

type AssemblyRecord = {
  id: string;
  topic_name: string;
  agents?: unknown[];
  description?: string;
  content?: string;
  explanation?: string;
  essay_id?: string;
};

type ResourceRecord = {
  id: string;
  objective?: string[] | string;
  content?: string | null;
  url?: string | null;
  essay_id: string;
  file_name?: string | null;
  content_type?: string | null;
  encoded_content?: string | null;
  metadata?: unknown;
  submittedAt?: string;
};

const isSubmissionResource = (resource: EssayResource): boolean => {
  const objectives = Array.isArray(resource.objective)
    ? resource.objective.map((item) => String(item).toLowerCase())
    : [];
  if (objectives.includes("student_submission")) {
    return true;
  }

  const metadata =
    resource.metadata && typeof resource.metadata === "object"
      ? (resource.metadata as Record<string, unknown>)
      : null;
  if (
    metadata &&
    typeof metadata.uploaded_at === "string" &&
    metadata.uploaded_at.trim().length > 0
  ) {
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
  return Array.isArray(value) && value.every((item) => typeof item === "string");
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
    typeof candidate.strategy !== "string" ||
    typeof candidate.verdict !== "string" ||
    !isStringArray(candidate.strengths) ||
    !isStringArray(candidate.improvements)
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

const surfaceClassName =
  "rounded-[1.75rem] border border-stone-200 bg-white/90 p-6 shadow-sm dark:border-slate-700 dark:bg-slate-900/75";

const subduedSurfaceClassName =
  "rounded-[1.5rem] border border-stone-200 bg-stone-50/80 p-5 shadow-sm dark:border-slate-700 dark:bg-slate-950/70";

const fieldClassName =
  "w-full rounded-xl border border-stone-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-teal-700 focus:ring-2 focus:ring-teal-700/10 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-50 dark:placeholder:text-slate-500";

const secondaryButtonClassName =
  "inline-flex items-center gap-2 rounded-full border border-stone-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-stone-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-700 focus-visible:ring-offset-2 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-200";

const primaryButtonClassName =
  "inline-flex items-center justify-center gap-2 rounded-full bg-teal-700 px-5 py-3 text-sm font-semibold text-white transition hover:bg-teal-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-700 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:bg-slate-400 dark:disabled:bg-slate-700";

const tabButtonClassName = (isActive: boolean) =>
  `inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm font-semibold transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-700 focus-visible:ring-offset-2 ${
    isActive
      ? "bg-slate-900 text-white dark:bg-slate-100 dark:text-slate-950"
      : "border border-stone-200 bg-white text-slate-700 hover:bg-stone-50 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-200"
  }`;

// No GoF pattern applies here; this component is a straightforward submission and review workspace.

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
    return resources.filter((resource) => {
      const tag = resource.objective?.[0]?.toLowerCase();
      return tag !== "student_submission";
    });
  }, [resourcesByEssay, selectedEssayId]);

  const selectedHistory = useMemo(() => {
    if (!selectedEssayId) {
      return [] as Submission[];
    }
    return history.filter((entry) => entry.resource.essay_id === selectedEssayId);
  }, [history, selectedEssayId]);

  useEffect(() => {
    let active = true;
    setLoadingCases(true);
    essaysEngine
      .get("/assemblies")
      .then((res) => {
        if (!active) {
          return undefined;
        }
        const raw = asArray<AssemblyRecord>(res.data);
        if (raw.length === 0) {
          return essaysEngine.get("/essays").then((essayRes) => {
            if (!active) {
              return;
            }
            const essays = asArray<Essay>(essayRes.data);
            const fallbackCases: EssayCase[] = essays.map((essay) => ({
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
        const mapped: EssayCase[] = raw.map((entry) => ({
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
      .catch((err) => {
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
    setEvaluationResult(null);
    setEvaluationError(null);
    setSelectedCase((previous) => {
      if (cases.length === 0) {
        return null;
      }
      if (!previous) {
        return cases[0];
      }
      const match = cases.find((item) => item.id === previous.id);
      return match ?? cases[0];
    });
  }, [cases]);

  useEffect(() => {
    setLoadingHistory(true);
    essaysEngine
      .get("/resources")
      .then((res) => {
        const content = asArray<ResourceRecord>(res.data);
        const grouped: Record<string, EssayResource[]> = {};
        const mappedHistory: Submission[] = content.flatMap((record) => {
          const objectives = Array.isArray(record.objective)
            ? record.objective
            : record.objective
              ? [record.objective]
              : [];
          const metadata =
            typeof record.metadata === "object" && record.metadata !== null
              ? (record.metadata as Record<string, unknown>)
              : {};
          const uploadedAt =
            typeof metadata.uploaded_at === "string"
              ? metadata.uploaded_at
              : (record.submittedAt ?? "");
          const descriptionMeta =
            typeof metadata.description === "string" ? metadata.description : "";
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
          return [
            {
              resource: parsed,
              description: (descriptionMeta || details.join(" ") || tag || "").trim(),
              submittedAt: uploadedAt,
              evaluation: parseEvaluationFromMetadata(metadata),
            },
          ];
        });
        setHistory(mappedHistory);
        setResourcesByEssay(grouped);
      })
      .catch((err) => {
        console.error("Failed to load resources", err);
        setHistory([]);
        setResourcesByEssay({});
      })
      .finally(() => setLoadingHistory(false));
  }, []);

  useEffect(() => {
    essaysEngine
      .get("/essays")
      .then((res) => {
        const items = asArray<Essay>(res.data);
        const lookup: Record<string, Essay> = {};
        for (const item of items) {
          if (item.id) {
            lookup[item.id] = item;
          }
        }
        setEssayLookup(lookup);
      })
      .catch((err) => console.warn("Could not load essays for reference text:", err));
  }, []);

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
      content_file_location: (baseEssay as Record<string, unknown> | undefined)
        ?.content_file_location,
      assembly_id: selectedCase.id,
    };

    const evaluationResources = evaluationCriteria;

    try {
      const evaluationResponse = await essaysEngine.post<EssayEvaluationResult>(
        "/grader/interaction",
        {
          case_id: selectedCase.id,
          essay: evaluationEssay,
          resources: evaluationResources,
        },
      );
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
      setResourcesByEssay((previous) => ({ ...previous, [essayIdForCase]: nextResources }));
      const submission: Submission = {
        resource: storedResource,
        description,
        submittedAt:
          typeof storedResource.metadata?.uploaded_at === "string"
            ? storedResource.metadata.uploaded_at
            : new Date().toISOString(),
        evaluation: evaluationRecord ?? undefined,
      };
      setHistory((previous) => [submission, ...previous]);
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
        const targetEntry = history.find((entry) => entry.resource.id === targetId);
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
      setHistory((previous) =>
        previous.map((entry) =>
          entry.resource.essay_id === essayId
            ? {
                ...entry,
                resource:
                  targetId !== "current" && entry.resource.id === targetId
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
      <section
        className={`${surfaceClassName} flex min-h-[40vh] flex-col items-center justify-center text-center`}
      >
        <FaSpinner className="text-3xl text-teal-700 animate-spin" />
        <h2 className="mt-4 text-2xl font-semibold text-slate-900 dark:text-slate-50">
          Loading essay workspace
        </h2>
        <p className="mt-2 max-w-md text-sm leading-7 text-slate-600 dark:text-slate-300">
          Tutor is preparing the available essay cases, reference text, and evaluation history.
        </p>
      </section>
    );
  }

  const selectedCaseLabel = selectedCase?.name || selectedCase?.topic_name || "Selected case";

  return (
    <div className="mx-auto w-full max-w-5xl space-y-8">
      <section className={surfaceClassName}>
        <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
          <div className="max-w-3xl">
            <p className="text-xs font-semibold uppercase tracking-[0.3em] text-teal-700">
              Essay evaluation
            </p>
            <h2 className="mt-3 text-3xl font-semibold leading-tight text-slate-900 dark:text-slate-50 md:text-4xl">
              Submit and review essay responses
            </h2>
            <p className="mt-3 text-sm leading-7 text-slate-600 dark:text-slate-300">
              Select a case, submit a response, and review evaluation output in a single workspace.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => setActiveTab("submission")}
              className={tabButtonClassName(activeTab === "submission")}
            >
              <FaUpload /> Submission
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("history")}
              className={tabButtonClassName(activeTab === "history")}
            >
              <FaHistory /> History
            </button>
          </div>
        </div>

        <div className="mt-6 grid gap-4 lg:grid-cols-[minmax(0,2fr)_minmax(16rem,1fr)] lg:items-end">
          <div>
            <label
              htmlFor="essay-case"
              className="text-sm font-semibold text-slate-900 dark:text-slate-100"
            >
              Essay case
            </label>
            {cases.length === 0 ? (
              <div className="mt-2 rounded-xl border border-rose-200 bg-rose-50/80 px-4 py-3 text-sm text-rose-800 dark:border-rose-900/60 dark:bg-rose-950/20 dark:text-rose-100">
                No essay cases are available right now. Please try again later.
              </div>
            ) : (
              <select
                id="essay-case"
                className={`${fieldClassName} mt-2`}
                value={selectedCase?.id || ""}
                onChange={(event: React.ChangeEvent<HTMLSelectElement>) => {
                  const next = cases.find((ca) => ca.id === event.target.value) || null;
                  setSelectedCase(next);
                  setEvaluationResult(null);
                  setEvaluationError(null);
                }}
              >
                <option value="">Select an essay case</option>
                {cases.map((ca) => (
                  <option key={ca.id} value={ca.id}>
                    {ca.name || ca.topic_name || "Untitled"}
                  </option>
                ))}
              </select>
            )}
          </div>

          <div className={subduedSurfaceClassName}>
            <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-500 dark:text-slate-400">
              Current case
            </p>
            <p className="mt-2 text-lg font-semibold text-slate-900 dark:text-slate-50">
              {selectedCaseLabel}
            </p>
            <p className="mt-2 text-sm leading-7 text-slate-600 dark:text-slate-300">
              {selectedEssay?.explanation ||
                selectedCase?.description ||
                "Select a case to review the source material and submission guidance."}
            </p>
          </div>
        </div>
      </section>

      {activeTab === "submission" ? (
        <>
          {selectedCase && (
            <section className="grid gap-4 xl:grid-cols-2">
              <article
                className={`${surfaceClassName} max-h-[28rem] overflow-y-auto prose prose-sm max-w-none prose-slate md:prose-base dark:prose-invert`}
              >
                <h3 className="mb-2 text-lg font-semibold text-slate-900 dark:text-slate-50">
                  Reference text
                </h3>
                <div className="break-words">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {selectedEssay?.content ||
                      selectedCase.content ||
                      "No reference text available."}
                  </ReactMarkdown>
                </div>
              </article>
              <article
                className={`${surfaceClassName} max-h-[28rem] overflow-y-auto prose prose-sm max-w-none prose-slate md:prose-base dark:prose-invert`}
              >
                <h3 className="mb-2 text-lg font-semibold text-slate-900 dark:text-slate-50">
                  Instructions and rubric
                </h3>
                <div className="break-words">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {selectedEssay?.explanation ||
                      selectedCase.explanation ||
                      selectedCase.description ||
                      "No instructions available."}
                  </ReactMarkdown>
                </div>
                {evaluationCriteria.length === 0 && (
                  <p className="mt-4 text-sm text-slate-600 dark:text-slate-300">
                    No specific evaluation criteria found for this essay. The graders will rely on
                    their default strategy.
                  </p>
                )}
              </article>
            </section>
          )}
          <form onSubmit={handleSubmit} className={`${surfaceClassName} flex flex-col gap-6`}>
            <div className="grid gap-6 lg:grid-cols-[minmax(0,2fr)_minmax(16rem,1fr)]">
              <div className="space-y-6">
                <div>
                  <label
                    htmlFor="essay-description"
                    className="text-sm font-semibold text-slate-900 dark:text-slate-100"
                  >
                    Submission title
                  </label>
                  <input
                    id="essay-description"
                    type="text"
                    className={`${fieldClassName} mt-2`}
                    value={description}
                    onChange={(event) => setDescription(event.target.value)}
                    placeholder="Short description for this submission"
                  />
                </div>
                <div>
                  <label
                    htmlFor="essay-text"
                    className="text-sm font-semibold text-slate-900 dark:text-slate-100"
                  >
                    Essay response
                  </label>
                  <textarea
                    id="essay-text"
                    className={`${fieldClassName} mt-2 min-h-[14rem] resize-y`}
                    value={essayText}
                    onChange={(event) => setEssayText(event.target.value)}
                    placeholder="Paste or draft the essay response here"
                  />
                </div>
              </div>

              <div className={subduedSurfaceClassName}>
                <p className="text-sm font-semibold text-slate-900 dark:text-slate-50">
                  Supporting file
                </p>
                <p className="mt-2 text-sm leading-7 text-slate-600 dark:text-slate-300">
                  Upload a PDF or image version when the submission should be reviewed from an
                  attached document.
                </p>
                <input
                  id="essay-file"
                  type="file"
                  accept=".pdf,image/*"
                  ref={fileInputRef}
                  onChange={handleFileChange}
                  className="mt-4 block w-full text-sm text-slate-600 file:mr-4 file:rounded-full file:border-0 file:bg-slate-100 file:px-4 file:py-2 file:font-medium file:text-slate-700 hover:file:bg-slate-200 dark:text-slate-300 dark:file:bg-slate-800 dark:file:text-slate-100 dark:hover:file:bg-slate-700"
                />
                {essayFile ? (
                  <p className="mt-4 inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-sm text-emerald-800 dark:border-emerald-900/60 dark:bg-emerald-950/20 dark:text-emerald-100">
                    <FaFileAlt /> {essayFile.name}
                  </p>
                ) : null}
                {uploadError ? (
                  <p className="mt-4 text-sm text-rose-700 dark:text-rose-200">{uploadError}</p>
                ) : null}
              </div>
            </div>
            <button
              type="submit"
              className={primaryButtonClassName}
              disabled={submitting || !selectedCase}
            >
              {submitting ? <FaSpinner className="animate-spin" /> : <FaUpload />}
              {submitting ? "Submitting response" : "Submit response"}
            </button>
          </form>
          <section className={surfaceClassName}>
            <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500 dark:text-slate-400">
                  Evaluation
                </p>
                <h3 className="mt-2 text-2xl font-semibold text-slate-900 dark:text-slate-50">
                  Review results
                </h3>
              </div>
              {selectedEssayId && (
                <button
                  type="button"
                  onClick={() => triggerReevaluation(selectedEssayId, "current")}
                  className={secondaryButtonClassName}
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
              <div className="mt-4 flex items-center gap-2 text-sm text-teal-700 dark:text-teal-300">
                <FaSpinner className="animate-spin" /> Evaluating essay...
              </div>
            )}
            {evaluationError && (
              <div className="mt-4 rounded-xl border border-rose-200 bg-rose-50/80 px-4 py-3 text-sm text-rose-800 dark:border-rose-900/60 dark:bg-rose-950/20 dark:text-rose-100">
                {evaluationError}
              </div>
            )}
            {!submitting && !evaluationResult && !evaluationError && (
              <div className="mt-4 rounded-xl border border-dashed border-stone-300 bg-stone-50/70 p-6 text-center text-sm text-slate-500 dark:border-slate-700 dark:bg-slate-950/60 dark:text-slate-400">
                No evaluation is available yet. Submit a response to review strengths and next
                steps.
              </div>
            )}
            {evaluationResult && (
              <div className="mt-4 rounded-[1.5rem] border border-stone-200 bg-stone-50/80 p-6 dark:border-slate-700 dark:bg-slate-950/60">
                <div className="flex flex-col gap-2">
                  <span className="inline-flex w-fit rounded-full border border-stone-200 bg-white px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-slate-700 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200">
                    Strategy: {formatStrategy(evaluationResult.strategy)}
                  </span>
                  <p className="text-base whitespace-pre-line text-slate-900 dark:text-slate-100">
                    {evaluationResult.verdict}
                  </p>
                </div>
                <div className="mt-6 grid gap-4 md:grid-cols-2">
                  <div>
                    <h4 className="text-sm font-semibold text-slate-900 dark:text-slate-50">
                      Strengths
                    </h4>
                    <ul className="mt-2 space-y-2 text-sm text-slate-700 dark:text-slate-200">
                      {evaluationResult.strengths.map((item) => (
                        <li
                          key={`strength-${item}`}
                          className="rounded-lg border border-stone-200 bg-white px-3 py-2 dark:border-slate-700 dark:bg-slate-900"
                        >
                          {item}
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-slate-900 dark:text-slate-50">
                      Improvements
                    </h4>
                    <ul className="mt-2 space-y-2 text-sm text-slate-700 dark:text-slate-200">
                      {evaluationResult.improvements.map((item) => (
                        <li
                          key={`improvement-${item}`}
                          className="rounded-lg border border-stone-200 bg-white px-3 py-2 dark:border-slate-700 dark:bg-slate-900"
                        >
                          {item}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            )}
          </section>
        </>
      ) : (
        <section className={surfaceClassName}>
          <div className="flex items-center gap-2">
            <FaHistory className="text-slate-500 dark:text-slate-400" />
            <h3 className="text-2xl font-semibold text-slate-900 dark:text-slate-50">
              Submission history
            </h3>
          </div>
          {loadingHistory ? (
            <div className="mt-4 flex items-center gap-2 text-sm text-teal-700 dark:text-teal-300">
              <FaSpinner className="animate-spin" /> Loading history...
            </div>
          ) : !selectedCase ? (
            <div className="mt-4 rounded-xl border border-dashed border-stone-300 bg-stone-50/70 p-4 text-sm text-slate-500 dark:border-slate-700 dark:bg-slate-950/60 dark:text-slate-400">
              Select an essay case to review its submission history.
            </div>
          ) : selectedHistory.length === 0 ? (
            <div className="mt-4 rounded-xl border border-dashed border-stone-300 bg-stone-50/70 p-4 text-sm text-slate-500 dark:border-slate-700 dark:bg-slate-950/60 dark:text-slate-400">
              No submissions have been recorded for this case yet.
            </div>
          ) : (
            <ul className="mt-4 divide-y divide-stone-200 dark:divide-slate-800">
              {selectedHistory.map((entry) => (
                <li key={entry.resource.id} className="py-4">
                  <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                    <div>
                      <span className="font-semibold text-slate-900 dark:text-slate-50">
                        {entry.submittedAt
                          ? new Date(entry.submittedAt).toLocaleString()
                          : "Unknown date"}
                      </span>{" "}
                      -
                      {entry.resource.file_name ? (
                        <span className="inline-flex items-center gap-1 text-slate-700 dark:text-slate-200">
                          <FaFileAlt />
                          {entry.resource.file_name}
                        </span>
                      ) : (
                        <span className="text-slate-700 dark:text-slate-200">Written essay</span>
                      )}
                      <div className="text-sm italic text-slate-500 dark:text-slate-400">
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
                        <span className="text-xs text-slate-400 dark:text-slate-500">
                          Evaluation not available.
                        </span>
                      )}
                      <button
                        type="button"
                        onClick={() =>
                          entry.resource.essay_id &&
                          triggerReevaluation(entry.resource.essay_id, entry.resource.id)
                        }
                        className={secondaryButtonClassName}
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
        </section>
      )}
    </div>
  );
};

export default EssaySubmission;
