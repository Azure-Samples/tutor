"use client";

import { useEffect, useState } from "react";

import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import DefaultLayout from "@/components/Layouts/DefaultLayout";
import { unwrapContent } from "@/types/api";
import { upskillingApi } from "@/utils/api";

// ---------------------------------------------------------------------------
// Domain types
// ---------------------------------------------------------------------------

interface Paragraph {
  title: string;
  content: string;
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

const EMPTY_PARAGRAPH: Paragraph = { title: "", content: "" };

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

  // Detail / form state
  const [formTitle, setFormTitle] = useState("");
  const [formTimeframe, setFormTimeframe] = useState<string>("week");
  const [formTopic, setFormTopic] = useState("");
  const [formClassId, setFormClassId] = useState("");
  const [formParagraphs, setFormParagraphs] = useState<Paragraph[]>([{ ...EMPTY_PARAGRAPH }]);
  const [formEvaluations, setFormEvaluations] = useState<Evaluation[]>([]);
  const [formLoading, setFormLoading] = useState(false);
  const [formError, setFormError] = useState("");
  const [formSuccess, setFormSuccess] = useState("");

  // Evaluation expand/collapse per paragraph index
  const [expandedEvals, setExpandedEvals] = useState<Set<number>>(new Set());

  // ------- Data fetching -------

  const fetchPlans = async () => {
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
  };

  useEffect(() => {
    fetchPlans();
  }, []);

  // ------- Navigation helpers -------

  const openCreate = () => {
    setEditingPlanId(null);
    setFormTitle("");
    setFormTimeframe("week");
    setFormTopic("");
    setFormClassId("");
    setFormParagraphs([{ ...EMPTY_PARAGRAPH }]);
    setFormEvaluations([]);
    setFormError("");
    setFormSuccess("");
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
      setFormParagraphs(plan.paragraphs.length > 0 ? plan.paragraphs : [{ ...EMPTY_PARAGRAPH }]);
      setFormEvaluations(plan.evaluations ?? []);
      setView("detail");
    } catch (err: unknown) {
      setListError(err instanceof Error ? err.message : "Failed to load plan details.");
    } finally {
      setFormLoading(false);
    }
  };

  const backToList = () => {
    setView("list");
    fetchPlans();
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
        paragraphs: formParagraphs,
        performance_history: [],
      };

      if (editingPlanId) {
        await upskillingApi.put(`/plans/${editingPlanId}`, body, { headers: AUTH_HEADERS });
        setFormSuccess("Plan updated successfully.");
      } else {
        const res = await upskillingApi.post("/plans", body, { headers: AUTH_HEADERS });
        const created = unwrapContent<Plan>(res.data);
        setEditingPlanId(created.id);
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
    try {
      await upskillingApi.post(`/plans/${planId}/evaluate`, {}, { headers: AUTH_HEADERS });
      await fetchPlans();
    } catch (err: unknown) {
      setListError(err instanceof Error ? err.message : "Failed to evaluate plan.");
    } finally {
      setListLoading(false);
    }
  };

  // ------- Paragraph helpers -------

  const updateParagraph = (idx: number, field: keyof Paragraph, value: string) => {
    setFormParagraphs((prev) => prev.map((p, i) => (i === idx ? { ...p, [field]: value } : p)));
  };

  const addParagraph = () => {
    setFormParagraphs((prev) => [...prev, { ...EMPTY_PARAGRAPH }]);
  };

  const removeParagraph = (idx: number) => {
    setFormParagraphs((prev) => (prev.length <= 1 ? prev : prev.filter((_, i) => i !== idx)));
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
    <span className={`inline-block rounded-full px-3 py-0.5 text-xs font-semibold ${STATUS_COLORS[status] ?? STATUS_COLORS.draft}`}>
      {status}
    </span>
  );

  const renderListView = () => (
    <>
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-lg font-semibold text-black dark:text-white">Teaching Plans</h3>
        <button
          onClick={openCreate}
          className="rounded bg-cyan-600 px-4 py-2 text-sm font-semibold text-white hover:bg-cyan-700"
        >
          + Create New Plan
        </button>
      </div>

      {listError && <p className="mb-4 rounded bg-red-50 p-3 text-sm text-red-600 dark:bg-red-900/30 dark:text-red-300">{listError}</p>}

      {listLoading && <p className="text-sm text-gray-500 dark:text-gray-400">Loading plans…</p>}

      {!listLoading && plans.length === 0 && (
        <p className="text-sm text-gray-500 dark:text-gray-400">No plans found. Create one to get started.</p>
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
                <th className="px-4 py-3 font-medium text-black dark:text-white">Updated</th>
                <th className="px-4 py-3 font-medium text-black dark:text-white">Actions</th>
              </tr>
            </thead>
            <tbody>
              {plans.map((plan) => (
                <tr key={plan.id} className="border-b border-stroke last:border-b-0 dark:border-strokedark">
                  <td className="px-4 py-3 text-black dark:text-white">{plan.title}</td>
                  <td className="px-4 py-3 text-gray-600 dark:text-gray-300">{plan.topic}</td>
                  <td className="px-4 py-3 text-gray-600 dark:text-gray-300">{plan.timeframe}</td>
                  <td className="px-4 py-3">{renderStatusBadge(plan.status)}</td>
                  <td className="px-4 py-3 text-gray-500 dark:text-gray-400">
                    {new Date(plan.updated_at).toLocaleDateString()}
                  </td>
                  <td className="flex gap-2 px-4 py-3">
                    <button
                      onClick={() => openEdit(plan.id)}
                      className="rounded bg-blue-600 px-3 py-1 text-xs font-semibold text-white hover:bg-blue-700"
                    >
                      View / Edit
                    </button>
                    <button
                      onClick={() => evaluatePlan(plan.id)}
                      className="rounded bg-emerald-600 px-3 py-1 text-xs font-semibold text-white hover:bg-emerald-700"
                    >
                      Evaluate
                    </button>
                    <button
                      onClick={() => deletePlan(plan.id)}
                      className="rounded bg-red-600 px-3 py-1 text-xs font-semibold text-white hover:bg-red-700"
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

  const renderDetailView = () => (
    <>
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-lg font-semibold text-black dark:text-white">
          {editingPlanId ? "Edit Plan" : "Create New Plan"}
        </h3>
        <button
          onClick={backToList}
          className="rounded border border-stroke px-4 py-2 text-sm font-semibold text-black hover:bg-gray-100 dark:border-strokedark dark:text-white dark:hover:bg-white/10"
        >
          ← Back to List
        </button>
      </div>

      {formError && <p className="mb-4 rounded bg-red-50 p-3 text-sm text-red-600 dark:bg-red-900/30 dark:text-red-300">{formError}</p>}
      {formSuccess && <p className="mb-4 rounded bg-emerald-50 p-3 text-sm text-emerald-600 dark:bg-emerald-900/30 dark:text-emerald-300">{formSuccess}</p>}

      {/* Form fields */}
      <div className="space-y-4">
        <div>
          <label className="mb-1 block text-sm font-medium text-black dark:text-white">Title</label>
          <input
            type="text"
            value={formTitle}
            onChange={(e) => setFormTitle(e.target.value)}
            className="w-full rounded border border-stroke bg-transparent px-4 py-2 text-black outline-none focus:border-cyan-600 dark:border-form-strokedark dark:bg-form-input dark:text-white"
            placeholder="Plan title"
          />
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          <div>
            <label className="mb-1 block text-sm font-medium text-black dark:text-white">Timeframe</label>
            <select
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
            <label className="mb-1 block text-sm font-medium text-black dark:text-white">Topic</label>
            <input
              type="text"
              value={formTopic}
              onChange={(e) => setFormTopic(e.target.value)}
              className="w-full rounded border border-stroke bg-transparent px-4 py-2 text-black outline-none focus:border-cyan-600 dark:border-form-strokedark dark:bg-form-input dark:text-white"
              placeholder="e.g. Physics"
            />
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-black dark:text-white">Class ID</label>
            <input
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
            <label className="text-sm font-medium text-black dark:text-white">Paragraphs</label>
            <button
              type="button"
              onClick={addParagraph}
              className="rounded bg-cyan-600 px-3 py-1 text-xs font-semibold text-white hover:bg-cyan-700"
            >
              + Add Paragraph
            </button>
          </div>

          <div className="space-y-3">
            {formParagraphs.map((para, idx) => (
              <div key={idx} className="rounded border border-stroke p-3 dark:border-form-strokedark">
                <div className="mb-2 flex items-center justify-between">
                  <span className="text-xs font-semibold text-gray-500 dark:text-gray-400">
                    Paragraph {idx + 1}
                  </span>
                  {formParagraphs.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeParagraph(idx)}
                      className="text-xs font-semibold text-red-500 hover:text-red-700"
                    >
                      Remove
                    </button>
                  )}
                </div>
                <input
                  type="text"
                  value={para.title}
                  onChange={(e) => updateParagraph(idx, "title", e.target.value)}
                  className="mb-2 w-full rounded border border-stroke bg-transparent px-3 py-1.5 text-sm text-black outline-none focus:border-cyan-600 dark:border-form-strokedark dark:bg-form-input dark:text-white"
                  placeholder="Paragraph title"
                />
                <textarea
                  value={para.content}
                  onChange={(e) => updateParagraph(idx, "content", e.target.value)}
                  rows={3}
                  className="w-full rounded border border-stroke bg-transparent px-3 py-1.5 text-sm text-black outline-none focus:border-cyan-600 dark:border-form-strokedark dark:bg-form-input dark:text-white"
                  placeholder="Paragraph content"
                />
              </div>
            ))}
          </div>
        </div>

        {/* Save */}
        <button
          onClick={savePlan}
          disabled={formLoading}
          className="rounded bg-cyan-600 px-6 py-2 font-semibold text-white hover:bg-cyan-700 disabled:opacity-50"
        >
          {formLoading ? "Saving…" : editingPlanId ? "Update Plan" : "Create Plan"}
        </button>
      </div>

      {/* Evaluations section */}
      {formEvaluations.length > 0 && (
        <div className="mt-8">
          <h4 className="mb-3 text-base font-semibold text-black dark:text-white">Evaluations</h4>
          <div className="space-y-2">
            {formEvaluations.map((ev) => (
              <div key={ev.paragraph_index} className="rounded border border-stroke dark:border-form-strokedark">
                <button
                  type="button"
                  onClick={() => toggleEval(ev.paragraph_index)}
                  className="flex w-full items-center justify-between px-4 py-3 text-left text-sm font-medium text-black hover:bg-gray-50 dark:text-white dark:hover:bg-white/5"
                >
                  <span>
                    §{ev.paragraph_index + 1} — {ev.title}
                  </span>
                  <span className="text-xs text-gray-400">{expandedEvals.has(ev.paragraph_index) ? "▲" : "▼"}</span>
                </button>

                {expandedEvals.has(ev.paragraph_index) && (
                  <div className="border-t border-stroke px-4 py-3 dark:border-form-strokedark">
                    {ev.feedback.map((fb, fbIdx) => (
                      <div key={fbIdx} className="mb-3 last:mb-0">
                        <div className="mb-1 flex items-center gap-2">
                          <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">{fb.agent}</span>
                          <span
                            className={`text-xs font-bold ${VERDICT_COLORS[fb.verdict.toLowerCase()] ?? VERDICT_COLORS.neutral}`}
                          >
                            {fb.verdict}
                          </span>
                        </div>

                        {fb.strengths.length > 0 && (
                          <ul className="mb-1 ml-4 list-disc text-sm text-emerald-700 dark:text-emerald-400">
                            {fb.strengths.map((s, i) => (
                              <li key={i}>{s}</li>
                            ))}
                          </ul>
                        )}

                        {fb.improvements.length > 0 && (
                          <ul className="ml-4 list-disc text-sm text-orange-600 dark:text-orange-400">
                            {fb.improvements.map((imp, i) => (
                              <li key={i}>{imp}</li>
                            ))}
                          </ul>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
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
