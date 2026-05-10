"use client";

import { useCallback, useEffect, useState } from "react";

import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import DefaultLayout from "@/components/Layouts/DefaultLayout";
import { unwrapContent } from "@/types/api";
import { upskillingApi } from "@/utils/api";
import type { IntelligenceGovernanceMetadata } from "@/utils/workspace-api";

// ---------------------------------------------------------------------------
// Domain types
// ---------------------------------------------------------------------------

interface Paragraph {
  title: string;
  content: string;
}

interface ParagraphDraft extends Paragraph {
  id: string;
}

interface EvaluationFeedback {
  agent: string;
  verdict: string;
  strengths: string[];
  improvements: string[];
}

interface Evaluation {
  paragraph_index: number;
  title: string;
  feedback: EvaluationFeedback[];
}

interface AdvisoryTrainingStep {
  sequence: number;
  title: string;
  rationale: string;
  evidence_refs: string[];
}

interface AdvisoryTrainingPlan {
  plan_id: string;
  professor_id: string;
  status: "draft";
  generated_at: string;
  human_review_required: boolean;
  steps: AdvisoryTrainingStep[];
  governance: IntelligenceGovernanceMetadata;
}

interface Plan {
  id: string;
  professor_id: string;
  title: string;
  timeframe: string;
  topic: string;
  class_id: string;
  status: string;
  paragraphs: Paragraph[];
  evaluations: Evaluation[];
  performance_history: unknown[];
  advisory_training_plan: AdvisoryTrainingPlan | null;
  created_at: string;
  updated_at: string;
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const AUTH_HEADERS = {
  "X-User-Id": "professor-demo",
  "X-User-Roles": "professor",
};

const STATUS_COLORS: Record<string, string> = {
  draft: "bg-gray-200 text-gray-700 dark:bg-gray-600 dark:text-gray-200",
  evaluated: "bg-emerald-100 text-emerald-700 dark:bg-emerald-800 dark:text-emerald-200",
  revised: "bg-blue-100 text-blue-700 dark:bg-blue-800 dark:text-blue-200",
  archived: "bg-yellow-100 text-yellow-700 dark:bg-yellow-800 dark:text-yellow-200",
};

const VERDICT_COLORS: Record<string, string> = {
  positive: "text-emerald-600 dark:text-emerald-400",
  negative: "text-red-600 dark:text-red-400",
  neutral: "text-gray-600 dark:text-gray-400",
};

const TIMEFRAMES = ["week", "month", "semester", "year"] as const;

let paragraphDraftSequence = 0;

const PLAN_TITLE_INPUT_ID = "upskilling-plan-title";
const PLAN_TIMEFRAME_INPUT_ID = "upskilling-plan-timeframe";
const PLAN_TOPIC_INPUT_ID = "upskilling-plan-topic";
const PLAN_CLASS_ID_INPUT_ID = "upskilling-plan-class-id";

const createParagraphDraft = (paragraph: Partial<Paragraph> = {}): ParagraphDraft => ({
  id: `paragraph-${paragraphDraftSequence++}`,
  title: paragraph.title ?? "",
  content: paragraph.content ?? "",
});

const toParagraphPayload = ({ title, content }: ParagraphDraft): Paragraph => ({
  title,
  content,
});

const feedbackKey = (evaluation: Evaluation, feedback: EvaluationFeedback) =>
  [
    evaluation.paragraph_index,
    feedback.agent,
    feedback.verdict,
    feedback.strengths.join("|"),
    feedback.improvements.join("|"),
  ].join(":");

const formatLabel = (value: string) =>
  value
    .replace(/[_:-]+/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .replace(/\b\w/g, (character) => character.toUpperCase());

const formatReviewLabel = (value: string) => {
  const normalizedValue = value.toLowerCase().replace(/[\s:-]+/g, "_");

  if (normalizedValue === "not_final" || normalizedValue === "non_final") {
    return "Review draft";
  }

  if (normalizedValue.includes("final")) {
    return "Review recorded";
  }

  if (normalizedValue.includes("operational")) {
    return "Review required";
  }

  return formatLabel(value);
};

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

const UpskillingConfigPage = () => {
  // View state
  const [view, setView] = useState<"list" | "detail">("list");
  const [editingPlanId, setEditingPlanId] = useState<string | null>(null);

  // List state
  const [plans, setPlans] = useState<Plan[]>([]);
  const [listLoading, setListLoading] = useState(false);
  const [listError, setListError] = useState("");
  const [listSuccess, setListSuccess] = useState("");

  // Detail / form state
  const [formTitle, setFormTitle] = useState("");
  const [formTimeframe, setFormTimeframe] = useState<string>("week");
  const [formTopic, setFormTopic] = useState("");
  const [formClassId, setFormClassId] = useState("");
  const [formParagraphs, setFormParagraphs] = useState<ParagraphDraft[]>([createParagraphDraft()]);
  const [formEvaluations, setFormEvaluations] = useState<Evaluation[]>([]);
  const [formAdvisoryTrainingPlan, setFormAdvisoryTrainingPlan] =
    useState<AdvisoryTrainingPlan | null>(null);
  const [formLoading, setFormLoading] = useState(false);
  const [formError, setFormError] = useState("");
  const [formSuccess, setFormSuccess] = useState("");
  const [advisoryLoadingPlanId, setAdvisoryLoadingPlanId] = useState<string | null>(null);

  // Evaluation expand/collapse per paragraph index
  const [expandedEvals, setExpandedEvals] = useState<Set<number>>(new Set());

  // ------- Data fetching -------

  const fetchPlans = useCallback(async () => {
    setListLoading(true);
    setListError("");
    try {
      const res = await upskillingApi.get("/plans", { headers: AUTH_HEADERS });
      setPlans(unwrapContent<Plan[]>(res.data));
    } catch (err: unknown) {
      setListError(err instanceof Error ? err.message : "Failed to load plans.");
    } finally {
      setListLoading(false);
    }
  }, []);

  useEffect(() => {
    void fetchPlans();
  }, [fetchPlans]);

  // ------- Navigation helpers -------

  const openCreate = () => {
    setEditingPlanId(null);
    setFormTitle("");
    setFormTimeframe("week");
    setFormTopic("");
    setFormClassId("");
    setFormParagraphs([createParagraphDraft()]);
    setFormEvaluations([]);
    setFormAdvisoryTrainingPlan(null);
    setFormError("");
    setFormSuccess("");
    setListSuccess("");
    setExpandedEvals(new Set());
    setView("detail");
  };

  const openEdit = async (planId: string) => {
    setFormLoading(true);
    setFormError("");
    setFormSuccess("");
    setExpandedEvals(new Set());
    try {
      const res = await upskillingApi.get(`/plans/${planId}`, { headers: AUTH_HEADERS });
      const plan = unwrapContent<Plan>(res.data);
      setEditingPlanId(plan.id);
      setFormTitle(plan.title);
      setFormTimeframe(plan.timeframe);
      setFormTopic(plan.topic);
      setFormClassId(plan.class_id);
      setFormParagraphs(
        plan.paragraphs.length > 0
          ? plan.paragraphs.map((paragraph) => createParagraphDraft(paragraph))
          : [createParagraphDraft()],
      );
      setFormEvaluations(plan.evaluations ?? []);
      setFormAdvisoryTrainingPlan(plan.advisory_training_plan ?? null);
      setView("detail");
    } catch (err: unknown) {
      setListError(err instanceof Error ? err.message : "Failed to load plan details.");
    } finally {
      setFormLoading(false);
    }
  };

  const backToList = () => {
    setView("list");
    void fetchPlans();
  };

  // ------- CRUD actions -------

  const savePlan = async () => {
    setFormLoading(true);
    setFormError("");
    setFormSuccess("");
    try {
      const body = {
        title: formTitle,
        timeframe: formTimeframe,
        topic: formTopic,
        class_id: formClassId,
        paragraphs: formParagraphs.map(toParagraphPayload),
        performance_history: [],
      };

      if (editingPlanId) {
        const res = await upskillingApi.put(`/plans/${editingPlanId}`, body, {
          headers: AUTH_HEADERS,
        });
        const updated = unwrapContent<Plan>(res.data);
        setFormAdvisoryTrainingPlan(updated.advisory_training_plan ?? null);
        setFormSuccess("Plan updated successfully.");
      } else {
        const res = await upskillingApi.post("/plans", body, { headers: AUTH_HEADERS });
        const created = unwrapContent<Plan>(res.data);
        setEditingPlanId(created.id);
        setFormAdvisoryTrainingPlan(created.advisory_training_plan ?? null);
        setFormSuccess("Plan created successfully.");
      }
    } catch (err: unknown) {
      setFormError(err instanceof Error ? err.message : "Failed to save plan.");
    } finally {
      setFormLoading(false);
    }
  };

  const deletePlan = async (planId: string) => {
    if (!confirm("Are you sure you want to delete this plan?")) return;
    setListLoading(true);
    try {
      await upskillingApi.delete(`/plans/${planId}`, { headers: AUTH_HEADERS });
      await fetchPlans();
    } catch (err: unknown) {
      setListError(err instanceof Error ? err.message : "Failed to delete plan.");
    } finally {
      setListLoading(false);
    }
  };

  const evaluatePlan = async (planId: string) => {
    setListLoading(true);
    setListError("");
    setListSuccess("");
    try {
      await upskillingApi.post(`/plans/${planId}/evaluate`, {}, { headers: AUTH_HEADERS });
      await fetchPlans();
    } catch (err: unknown) {
      setListError(err instanceof Error ? err.message : "Failed to evaluate plan.");
    } finally {
      setListLoading(false);
    }
  };

  const draftAdvisoryTrainingPlan = async (planId: string, surface: "list" | "detail") => {
    setAdvisoryLoadingPlanId(planId);

    if (surface === "list") {
      setListError("");
      setListSuccess("");
    } else {
      setFormError("");
      setFormSuccess("");
    }

    try {
      const res = await upskillingApi.post(
        `/plans/${planId}/advisory-training-plan`,
        {},
        { headers: AUTH_HEADERS },
      );
      const updated = unwrapContent<Plan>(res.data);
      setPlans((previous) =>
        previous.map((plan) => (plan.id === updated.id ? { ...plan, ...updated } : plan)),
      );

      if (editingPlanId === updated.id || surface === "detail") {
        setFormAdvisoryTrainingPlan(updated.advisory_training_plan ?? null);
      }

      if (surface === "list") {
        setListSuccess("Draft advisory training plan generated for review.");
      } else {
        setFormSuccess("Draft advisory training plan generated for review.");
      }
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Failed to draft advisory training plan.";
      if (surface === "list") {
        setListError(message);
      } else {
        setFormError(message);
      }
    } finally {
      setAdvisoryLoadingPlanId(null);
    }
  };

  // ------- Paragraph helpers -------

  const updateParagraph = (paragraphId: string, field: keyof Paragraph, value: string) => {
    setFormParagraphs((prev) =>
      prev.map((paragraph) =>
        paragraph.id === paragraphId ? { ...paragraph, [field]: value } : paragraph,
      ),
    );
  };

  const addParagraph = () => {
    setFormParagraphs((prev) => [...prev, createParagraphDraft()]);
  };

  const removeParagraph = (paragraphId: string) => {
    setFormParagraphs((prev) =>
      prev.length <= 1 ? prev : prev.filter((paragraph) => paragraph.id !== paragraphId),
    );
  };

  const toggleEval = (idx: number) => {
    setExpandedEvals((prev) => {
      const next = new Set(prev);
      if (next.has(idx)) next.delete(idx);
      else next.add(idx);
      return next;
    });
  };

  // ------- Renderers -------

  const renderStatusBadge = (status: string) => (
    <span
      className={`inline-block rounded-full px-3 py-0.5 text-xs font-semibold ${STATUS_COLORS[status] ?? STATUS_COLORS.draft}`}
    >
      {status}
    </span>
  );

  const renderListView = () => (
    <>
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-lg font-semibold text-black dark:text-white">Teaching Plans</h3>
        <button
          type="button"
          onClick={openCreate}
          className="rounded bg-cyan-700 px-4 py-2 text-sm font-semibold text-white hover:bg-cyan-800"
        >
          + Create New Plan
        </button>
      </div>

      {listError && (
        <p className="mb-4 rounded bg-red-50 p-3 text-sm text-red-600 dark:bg-red-900/30 dark:text-red-300">
          {listError}
        </p>
      )}
      {listSuccess && (
        <p className="mb-4 rounded bg-emerald-50 p-3 text-sm text-emerald-600 dark:bg-emerald-900/30 dark:text-emerald-300">
          {listSuccess}
        </p>
      )}

      {listLoading && <p className="text-sm text-gray-500 dark:text-gray-400">Loading plans…</p>}

      {!listLoading && plans.length === 0 && (
        <p className="text-sm text-gray-500 dark:text-gray-400">
          No plans found. Create one to get started.
        </p>
      )}

      {!listLoading && plans.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full table-auto text-sm">
            <thead>
              <tr className="border-b border-stroke text-left dark:border-strokedark">
                <th className="px-4 py-3 font-medium text-black dark:text-white">Title</th>
                <th className="px-4 py-3 font-medium text-black dark:text-white">Topic</th>
                <th className="px-4 py-3 font-medium text-black dark:text-white">Timeframe</th>
                <th className="px-4 py-3 font-medium text-black dark:text-white">Status</th>
                <th className="px-4 py-3 font-medium text-black dark:text-white">Advisory draft</th>
                <th className="px-4 py-3 font-medium text-black dark:text-white">Updated</th>
                <th className="px-4 py-3 font-medium text-black dark:text-white">Actions</th>
              </tr>
            </thead>
            <tbody>
              {plans.map((plan) => (
                <tr
                  key={plan.id}
                  className="border-b border-stroke last:border-b-0 dark:border-strokedark"
                >
                  <td className="px-4 py-3 text-black dark:text-white">{plan.title}</td>
                  <td className="px-4 py-3 text-gray-600 dark:text-gray-300">{plan.topic}</td>
                  <td className="px-4 py-3 text-gray-600 dark:text-gray-300">{plan.timeframe}</td>
                  <td className="px-4 py-3">{renderStatusBadge(plan.status)}</td>
                  <td className="px-4 py-3">
                    {plan.advisory_training_plan ? (
                      <span className="inline-block rounded-full bg-amber-100 px-3 py-0.5 text-xs font-semibold text-amber-800 dark:bg-amber-900/50 dark:text-amber-100">
                        Review required
                      </span>
                    ) : (
                      <span className="inline-block rounded-full bg-gray-100 px-3 py-0.5 text-xs font-semibold text-gray-700 dark:bg-gray-700 dark:text-gray-200">
                        Not drafted
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-gray-500 dark:text-gray-400">
                    {new Date(plan.updated_at).toLocaleDateString()}
                  </td>
                  <td className="flex gap-2 px-4 py-3">
                    <button
                      type="button"
                      onClick={() => openEdit(plan.id)}
                      className="rounded bg-blue-700 px-3 py-1 text-xs font-semibold text-white hover:bg-blue-800"
                    >
                      View / Edit
                    </button>
                    <button
                      type="button"
                      onClick={() => evaluatePlan(plan.id)}
                      className="rounded bg-emerald-700 px-3 py-1 text-xs font-semibold text-white hover:bg-emerald-800"
                    >
                      Evaluate
                    </button>
                    <button
                      type="button"
                      onClick={() => draftAdvisoryTrainingPlan(plan.id, "list")}
                      disabled={advisoryLoadingPlanId === plan.id}
                      className="rounded bg-amber-800 px-3 py-1 text-xs font-semibold text-white hover:bg-amber-900 disabled:opacity-50"
                    >
                      {advisoryLoadingPlanId === plan.id ? "Drafting" : "Draft advisory"}
                    </button>
                    <button
                      type="button"
                      onClick={() => deletePlan(plan.id)}
                      className="rounded bg-red-700 px-3 py-1 text-xs font-semibold text-white hover:bg-red-800"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );

  const renderAdvisoryTrainingPlan = (advisoryTrainingPlan: AdvisoryTrainingPlan | null) => {
    if (!advisoryTrainingPlan) {
      return null;
    }

    const reviewLabel = formatReviewLabel(advisoryTrainingPlan.governance.review.status);
    const reviewDecisionLabel = advisoryTrainingPlan.governance.final_decision
      ? "Review recorded"
      : "Review draft";

    return (
      <section className="mt-8 rounded border border-amber-200 bg-amber-50/70 p-4 dark:border-amber-900/60 dark:bg-amber-950/20">
        <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-amber-700 dark:text-amber-200">
              Advisory training plan
            </p>
            <h4 className="mt-2 text-base font-semibold text-black dark:text-white">
              Draft plan for professor review
            </h4>
          </div>
          <div className="flex flex-wrap gap-2">
            <span className="rounded-full bg-white px-3 py-1 text-xs font-semibold text-amber-800 dark:bg-amber-950 dark:text-amber-100">
              {formatLabel(advisoryTrainingPlan.status)}
            </span>
            <span className="rounded-full bg-white px-3 py-1 text-xs font-semibold text-amber-800 dark:bg-amber-950 dark:text-amber-100">
              {reviewLabel}
            </span>
            <span className="rounded-full bg-white px-3 py-1 text-xs font-semibold text-amber-800 dark:bg-amber-950 dark:text-amber-100">
              {reviewDecisionLabel}
            </span>
          </div>
        </div>

        <dl className="mt-4 grid gap-3 text-sm text-amber-950 md:grid-cols-3 dark:text-amber-100">
          <div>
            <dt className="font-semibold">Human review</dt>
            <dd>{advisoryTrainingPlan.human_review_required ? "Required" : "Not required"}</dd>
          </div>
          <div>
            <dt className="font-semibold">Advisory state</dt>
            <dd>{advisoryTrainingPlan.governance.advisory_only ? "Advisory only" : "Review required"}</dd>
          </div>
          <div>
            <dt className="font-semibold">Appeal</dt>
            <dd>{advisoryTrainingPlan.governance.appeal.available ? "Available" : "Unavailable"}</dd>
          </div>
        </dl>

        <div className="mt-4 space-y-3">
          {advisoryTrainingPlan.steps.map((step) => (
            <article
              key={`${step.sequence}:${step.title}`}
              className="rounded border border-amber-200 bg-white/80 p-3 dark:border-amber-900/60 dark:bg-amber-950/30"
            >
              <p className="text-sm font-semibold text-black dark:text-white">
                {step.sequence}. {step.title}
              </p>
              <p className="mt-1 text-sm leading-6 text-amber-950 dark:text-amber-100">
                {step.rationale}
              </p>
              {step.evidence_refs.length > 0 && (
                <p className="mt-2 text-xs font-medium text-amber-800 dark:text-amber-200">
                  Evidence: {step.evidence_refs.join(", ")}
                </p>
              )}
            </article>
          ))}
        </div>
      </section>
    );
  };

  const renderDetailView = () => (
    <>
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-lg font-semibold text-black dark:text-white">
          {editingPlanId ? "Edit Plan" : "Create New Plan"}
        </h3>
        <button
          type="button"
          onClick={backToList}
          className="rounded border border-stroke px-4 py-2 text-sm font-semibold text-black hover:bg-gray-100 dark:border-strokedark dark:text-white dark:hover:bg-white/10"
        >
          ← Back to List
        </button>
      </div>

      {formError && (
        <p className="mb-4 rounded bg-red-50 p-3 text-sm text-red-600 dark:bg-red-900/30 dark:text-red-300">
          {formError}
        </p>
      )}
      {formSuccess && (
        <p className="mb-4 rounded bg-emerald-50 p-3 text-sm text-emerald-600 dark:bg-emerald-900/30 dark:text-emerald-300">
          {formSuccess}
        </p>
      )}

      {/* Form fields */}
      <div className="space-y-4">
        <div>
          <label
            className="mb-1 block text-sm font-medium text-black dark:text-white"
            htmlFor={PLAN_TITLE_INPUT_ID}
          >
            Title
          </label>
          <input
            id={PLAN_TITLE_INPUT_ID}
            type="text"
            value={formTitle}
            onChange={(e) => setFormTitle(e.target.value)}
            className="w-full rounded border border-stroke bg-transparent px-4 py-2 text-black outline-none focus:border-cyan-600 dark:border-form-strokedark dark:bg-form-input dark:text-white"
            placeholder="Plan title"
          />
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          <div>
            <label
              className="mb-1 block text-sm font-medium text-black dark:text-white"
              htmlFor={PLAN_TIMEFRAME_INPUT_ID}
            >
              Timeframe
            </label>
            <select
              id={PLAN_TIMEFRAME_INPUT_ID}
              value={formTimeframe}
              onChange={(e) => setFormTimeframe(e.target.value)}
              className="w-full rounded border border-stroke bg-transparent px-4 py-2 text-black outline-none focus:border-cyan-600 dark:border-form-strokedark dark:bg-form-input dark:text-white"
            >
              {TIMEFRAMES.map((tf) => (
                <option key={tf} value={tf}>
                  {tf.charAt(0).toUpperCase() + tf.slice(1)}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label
              className="mb-1 block text-sm font-medium text-black dark:text-white"
              htmlFor={PLAN_TOPIC_INPUT_ID}
            >
              Topic
            </label>
            <input
              id={PLAN_TOPIC_INPUT_ID}
              type="text"
              value={formTopic}
              onChange={(e) => setFormTopic(e.target.value)}
              className="w-full rounded border border-stroke bg-transparent px-4 py-2 text-black outline-none focus:border-cyan-600 dark:border-form-strokedark dark:bg-form-input dark:text-white"
              placeholder="e.g. Physics"
            />
          </div>

          <div>
            <label
              className="mb-1 block text-sm font-medium text-black dark:text-white"
              htmlFor={PLAN_CLASS_ID_INPUT_ID}
            >
              Class ID
            </label>
            <input
              id={PLAN_CLASS_ID_INPUT_ID}
              type="text"
              value={formClassId}
              onChange={(e) => setFormClassId(e.target.value)}
              className="w-full rounded border border-stroke bg-transparent px-4 py-2 text-black outline-none focus:border-cyan-600 dark:border-form-strokedark dark:bg-form-input dark:text-white"
              placeholder="e.g. class-3A"
            />
          </div>
        </div>

        {/* Paragraphs */}
        <div>
          <div className="mb-2 flex items-center justify-between">
            <p className="text-sm font-medium text-black dark:text-white">Paragraphs</p>
            <button
              type="button"
              onClick={addParagraph}
              className="rounded bg-cyan-700 px-3 py-1 text-xs font-semibold text-white hover:bg-cyan-800"
            >
              + Add Paragraph
            </button>
          </div>

          <div className="space-y-3">
            {formParagraphs.map((para, idx) => (
              <div
                key={para.id}
                className="rounded border border-stroke p-3 dark:border-form-strokedark"
              >
                <div className="mb-2 flex items-center justify-between">
                  <span className="text-xs font-semibold text-gray-500 dark:text-gray-400">
                    Paragraph {idx + 1}
                  </span>
                  {formParagraphs.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeParagraph(para.id)}
                      className="text-xs font-semibold text-red-500 hover:text-red-700"
                    >
                      Remove
                    </button>
                  )}
                </div>
                <input
                  type="text"
                  value={para.title}
                  onChange={(e) => updateParagraph(para.id, "title", e.target.value)}
                  aria-label={`Paragraph ${idx + 1} title`}
                  className="mb-2 w-full rounded border border-stroke bg-transparent px-3 py-1.5 text-sm text-black outline-none focus:border-cyan-600 dark:border-form-strokedark dark:bg-form-input dark:text-white"
                  placeholder="Paragraph title"
                />
                <textarea
                  value={para.content}
                  onChange={(e) => updateParagraph(para.id, "content", e.target.value)}
                  aria-label={`Paragraph ${idx + 1} content`}
                  rows={3}
                  className="w-full rounded border border-stroke bg-transparent px-3 py-1.5 text-sm text-black outline-none focus:border-cyan-600 dark:border-form-strokedark dark:bg-form-input dark:text-white"
                  placeholder="Paragraph content"
                />
              </div>
            ))}
          </div>
        </div>

        <div className="flex flex-wrap gap-3">
          <button
            type="button"
            onClick={savePlan}
            disabled={formLoading}
            className="rounded bg-cyan-700 px-6 py-2 font-semibold text-white hover:bg-cyan-800 disabled:opacity-50"
          >
            {formLoading ? "Saving…" : editingPlanId ? "Update Plan" : "Create Plan"}
          </button>
          {editingPlanId && (
            <button
              type="button"
              onClick={() => draftAdvisoryTrainingPlan(editingPlanId, "detail")}
              disabled={advisoryLoadingPlanId === editingPlanId}
              className="rounded bg-amber-800 px-6 py-2 font-semibold text-white hover:bg-amber-900 disabled:opacity-50"
            >
              {advisoryLoadingPlanId === editingPlanId
                ? "Drafting advisory plan"
                : "Draft advisory training plan"}
            </button>
          )}
        </div>
      </div>

      {renderAdvisoryTrainingPlan(formAdvisoryTrainingPlan)}

      {/* Evaluations section */}
      {formEvaluations.length > 0 && (
        <div className="mt-8">
          <h4 className="mb-3 text-base font-semibold text-black dark:text-white">Evaluations</h4>
          <div className="space-y-2">
            {formEvaluations.map((ev) => {
              const isExpanded = expandedEvals.has(ev.paragraph_index);
              const feedbackRegionId = `evaluation-feedback-${ev.paragraph_index}`;

              return (
                <div
                  key={ev.paragraph_index}
                  className="rounded border border-stroke dark:border-form-strokedark"
                >
                  <button
                    type="button"
                    onClick={() => toggleEval(ev.paragraph_index)}
                    aria-expanded={isExpanded}
                    aria-controls={feedbackRegionId}
                    className="flex w-full items-center justify-between px-4 py-3 text-left text-sm font-medium text-black hover:bg-gray-50 dark:text-white dark:hover:bg-white/5"
                  >
                    <span>
                      §{ev.paragraph_index + 1} — {ev.title}
                    </span>
                    <span className="text-xs text-gray-400">
                      {isExpanded ? "▲" : "▼"}
                    </span>
                  </button>

                  <div
                    id={feedbackRegionId}
                    hidden={!isExpanded}
                    className="border-t border-stroke px-4 py-3 dark:border-form-strokedark"
                  >
                    {ev.feedback.map((fb) => (
                      <div key={feedbackKey(ev, fb)} className="mb-3 last:mb-0">
                        <div className="mb-1 flex items-center gap-2">
                          <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                            {fb.agent}
                          </span>
                          <span
                            className={`text-xs font-bold ${VERDICT_COLORS[fb.verdict.toLowerCase()] ?? VERDICT_COLORS.neutral}`}
                          >
                            {fb.verdict}
                          </span>
                        </div>

                        {fb.strengths.length > 0 && (
                          <ul className="mb-1 ml-4 list-disc text-sm text-emerald-700 dark:text-emerald-400">
                            {fb.strengths.map((strength) => (
                              <li key={`${fb.agent}:strength:${strength}`}>{strength}</li>
                            ))}
                          </ul>
                        )}

                        {fb.improvements.length > 0 && (
                          <ul className="ml-4 list-disc text-sm text-orange-600 dark:text-orange-400">
                            {fb.improvements.map((improvement) => (
                              <li key={`${fb.agent}:improvement:${improvement}`}>{improvement}</li>
                            ))}
                          </ul>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </>
  );

  // ------- Main render -------

  return (
    <DefaultLayout>
      <Breadcrumb
        pageName="Upskilling Configuration"
        subtitle="Create, manage, and evaluate teaching plans with agentic coaching feedback."
      />

      <div className="mx-auto max-w-5xl rounded-2xl bg-white p-6 shadow dark:bg-boxdark">
        {view === "list" ? renderListView() : renderDetailView()}
      </div>
    </DefaultLayout>
  );
};

export default UpskillingConfigPage;
