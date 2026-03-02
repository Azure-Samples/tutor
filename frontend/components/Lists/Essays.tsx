"use client";
import { useCallback, useEffect, useState } from "react";
import { essaysEngine } from "@/utils/api";
import FormsModal from "@/components/common/Modals";
import { FaTrash, FaPlus, FaRobot, FaSync } from "react-icons/fa";
import EssayForm from "@/components/Forms/Essays";
import AgentForm from "@/components/Forms/Agent";
import type { Essay, EssayEvaluationResult, ProvisionedAgent } from "@/types/essays";
import { unwrapContent } from "@/types/api";

const EssaysList: React.FC = () => {
  const [essays, setEssays] = useState<Essay[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedEssay, setSelectedEssay] = useState<Essay | null>(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showAgentModal, setShowAgentModal] = useState(false);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [loadError, setLoadError] = useState(false);
  const [latestAgent, setLatestAgent] = useState<ProvisionedAgent | null>(null);
  const [processingId, setProcessingId] = useState<string | null>(null);
  const [reprocessError, setReprocessError] = useState<string | null>(null);
  const [latestEvaluation, setLatestEvaluation] = useState<{
    essayId: string;
    topic: string;
    result: EssayEvaluationResult;
  } | null>(null);

  const fetchEssays = useCallback(async (focusEssayId?: string) => {
    try {
      setLoading(true);
      setLoadError(false);
      const res = await essaysEngine.get("/essays");
      const data = unwrapContent<Essay[]>(res.data);
      const items = Array.isArray(data) ? data : [];
      setEssays(items);
      if (focusEssayId) {
        const match = items.find((item) => item.id === focusEssayId);
        if (match) {
          setSelectedEssay(match);
        }
      }
    } catch (error) {
      console.error("Error fetching essays:", error);
      setEssays([]);
      setLoadError(true);
    } finally {
      setLoading(false);
    }
  }, []);

  const closeAllModals = () => {
    setShowCreateModal(false);
    setShowDeleteModal(false);
    setShowAgentModal(false);
    setShowDetailsModal(false);
  };

  useEffect(() => {
    void fetchEssays();
  }, [fetchEssays]);

  const handleDeleteClick = (essay: Essay) => {
    setSelectedEssay(essay);
    closeAllModals();
    setShowDeleteModal(true);
  };

  const handleCardClick = (essay: Essay) => {
    closeAllModals();
    setSelectedEssay(essay);
    setShowDetailsModal(true);
  };

  const closeDetailsModal = () => {
    setShowDetailsModal(false);
    setSelectedEssay(null);
  };

  const confirmDelete = async () => {
    if (!selectedEssay?.id) return;
    await essaysEngine.delete(`/essays/${selectedEssay.id}`);
    setEssays((prev) => prev.filter((e) => e.id !== selectedEssay.id));
    closeAllModals();
    setSelectedEssay(null);
  };

  const formatStrategy = (strategy: string) => {
    if (!strategy) {
      return "Unknown";
    }
    const normalized = strategy.replace(/_/g, " ").toLowerCase();
    return normalized.charAt(0).toUpperCase() + normalized.slice(1);
  };

  const handleReprocess = async (essay: Essay) => {
    if (!essay.id) {
      setReprocessError("Selected essay is missing an identifier.");
      return;
    }
    setProcessingId(essay.id);
    setReprocessError(null);
    try {
      const res = await essaysEngine.post<EssayEvaluationResult>(`/essays/${essay.id}/evaluate`);
      const evaluation = res.data;
      setLatestEvaluation({ essayId: essay.id, topic: essay.topic, result: evaluation });
    } catch (error) {
      console.error("Failed to re-evaluate essay", error);
      let message = "Could not re-run the evaluation. Please try again.";
      if (error && typeof error === "object" && "message" in error && typeof (error as { message?: string }).message === "string") {
        message = (error as { message: string }).message || message;
      }
      setReprocessError(message);
      setLatestEvaluation(null);
    } finally {
      setProcessingId(null);
    }
  };

  const showEmptyState = !loading && (loadError || essays.length === 0);

  return (
    <div className="w-full p-0">
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <span className="text-lg text-cyan-500 animate-pulse">Loading essays...</span>
        </div>
      ) : showEmptyState ? (
        <div className="rounded-xl border border-yellow-300 dark:border-yellow-700 bg-yellow-50 dark:bg-yellow-900 p-8 shadow flex flex-col gap-6 items-center text-center">
          <div>
            <p className="text-xl font-bold text-yellow-800 dark:text-yellow-200">
              No essay was found. Ready to create the first one or provision an agent?
            </p>
            <p className="text-yellow-700 dark:text-yellow-300 mt-2">
              Start by setting up agents in Azure AI Foundry or add a new essay to evaluate.
            </p>
          </div>
          <div className="flex flex-col sm:flex-row gap-4">
            <button
              className="flex items-center gap-2 bg-gradient-to-br from-green-400 to-cyan-400 hover:from-cyan-400 hover:to-yellow-300 text-white font-bold px-6 py-3 rounded-full shadow-lg hover:scale-105 transition-all duration-200 text-lg"
              onClick={() => {
                closeAllModals();
                setSelectedEssay(null);
                setShowCreateModal(true);
              }}
            >
              <FaPlus className="text-xl" /> New Essay
            </button>
            <button
              className="flex items-center gap-2 bg-gradient-to-br from-purple-500 to-blue-500 hover:from-blue-500 hover:to-purple-400 text-white font-bold px-6 py-3 rounded-full shadow-lg hover:scale-105 transition-all duration-200 text-lg"
              onClick={() => {
                closeAllModals();
                setShowAgentModal(true);
              }}
            >
              <FaRobot className="text-xl" /> Provision Agent
            </button>
          </div>
          {latestAgent && (
            <div className="mt-4 text-sm text-cyan-800 dark:text-cyan-200 bg-cyan-100/80 dark:bg-cyan-900/40 rounded-2xl px-4 py-3">
              <p className="font-semibold">Last provisioned agent:</p>
              <p>{latestAgent.name} ({latestAgent.id})</p>
            </div>
          )}
        </div>
      ) : (
        <>
          <div className="flex flex-col gap-4 mb-6">
            {latestAgent && (
              <div className="rounded-2xl border border-cyan-200 dark:border-cyan-800 bg-cyan-50 dark:bg-cyan-900/40 px-4 py-3 text-sm text-cyan-800 dark:text-cyan-200">
                <span className="font-semibold">Last provisioned agent:</span> {latestAgent.name} ({latestAgent.id})
              </div>
            )}
            <div className="flex flex-col sm:flex-row items-center justify-end gap-3">
              <button
                className="flex items-center gap-2 bg-gradient-to-br from-purple-500 to-blue-500 hover:from-blue-500 hover:to-purple-400 text-white font-bold px-6 py-3 rounded-full shadow-lg hover:scale-105 transition-all duration-200 text-lg"
                onClick={() => {
                  closeAllModals();
                  setShowAgentModal(true);
                }}
              >
                <FaRobot className="text-xl" /> Provision Agent
              </button>
              <button
                className="flex items-center gap-2 bg-gradient-to-br from-green-400 to-cyan-400 hover:from-cyan-400 hover:to-yellow-300 text-white font-bold px-6 py-3 rounded-full shadow-lg hover:scale-105 transition-all duration-200 text-lg"
                onClick={() => {
                  closeAllModals();
                  setSelectedEssay(null);
                  setShowCreateModal(true);
                }}
              >
                <FaPlus className="text-xl" /> New Essay
              </button>
            </div>
            {reprocessError && (
              <div className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                {reprocessError}
              </div>
            )}
            {latestEvaluation && (
              <div className="rounded-2xl border border-cyan-200 dark:border-cyan-800 bg-white dark:bg-boxdark shadow px-5 py-5">
                <div className="flex flex-col gap-1">
                  <span className="text-xs font-semibold uppercase tracking-wide text-cyan-600 dark:text-cyan-300">
                    Latest evaluation
                  </span>
                  <h4 className="text-lg font-bold text-slate-900 dark:text-cyan-100">
                    {latestEvaluation.topic}
                  </h4>
                  <p className="text-sm text-slate-600 dark:text-slate-300 whitespace-pre-line">
                    {latestEvaluation.result.verdict}
                  </p>
                </div>
                <div className="mt-4 flex flex-wrap items-center gap-2 text-xs text-cyan-600 dark:text-cyan-300">
                  <span className="font-semibold">Strategy:</span>
                  <span>{formatStrategy(latestEvaluation.result.strategy)}</span>
                </div>
                <div className="mt-4 grid gap-4 md:grid-cols-2">
                  <div>
                    <h5 className="text-sm font-semibold text-green-700 dark:text-green-300">Strengths</h5>
                    <ul className="mt-2 space-y-1 text-sm text-slate-700 dark:text-slate-200">
                      {latestEvaluation.result.strengths.map((item, index) => (
                        <li key={`latest-strength-${index}`} className="rounded-lg bg-cyan-50/60 dark:bg-cyan-900/40 px-3 py-2">
                          {item}
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <h5 className="text-sm font-semibold text-orange-700 dark:text-orange-300">Improvements</h5>
                    <ul className="mt-2 space-y-1 text-sm text-slate-700 dark:text-slate-200">
                      {latestEvaluation.result.improvements.map((item, index) => (
                        <li key={`latest-improvement-${index}`} className="rounded-lg bg-orange-50/80 dark:bg-orange-900/30 px-3 py-2">
                          {item}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            )}
          </div>
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
            {essays.map((e) => (
              <div
                key={e.id}
                role="button"
                tabIndex={0}
                onClick={() => handleCardClick(e)}
                onKeyDown={(event) => {
                  if (event.key === "Enter" || event.key === " ") {
                    event.preventDefault();
                    handleCardClick(e);
                  }
                }}
                className="group flex flex-col justify-between rounded-2xl border border-cyan-200 dark:border-cyan-800 bg-white dark:bg-boxdark shadow hover:shadow-lg transition-all duration-200 focus:outline-none focus:ring-4 focus:ring-cyan-400/40"
              >
                <div className="flex items-start justify-between gap-3 p-4">
                  <div className="text-left">
                    <p className="text-sm uppercase tracking-wide text-cyan-600 dark:text-cyan-300">Essay Topic</p>
                    <h3 className="text-xl font-bold text-blue-700 dark:text-cyan-100 truncate">{e.topic}</h3>
                  </div>
                  <span className="rounded-full bg-cyan-50 dark:bg-cyan-900/60 px-3 py-1 text-xs font-semibold text-cyan-700 dark:text-cyan-200">View</span>
                </div>
                <div className="flex items-center justify-between gap-3 border-t border-cyan-100 dark:border-cyan-900 px-4 py-3">
                  <span className="text-sm font-medium text-cyan-600 dark:text-cyan-300">Click to view & edit</span>
                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={(event) => {
                        event.stopPropagation();
                        void handleReprocess(e);
                      }}
                      className="flex items-center gap-1 rounded-full bg-gradient-to-br from-cyan-400 to-blue-400 px-3 py-2 text-sm font-semibold text-white shadow hover:scale-105 transition-all duration-200 disabled:opacity-70"
                      title="Re-run evaluation"
                      disabled={processingId === e.id}
                    >
                      <FaSync className={processingId === e.id ? "animate-spin" : ""} />
                      {processingId === e.id ? "Re-evaluating" : "Re-evaluate"}
                    </button>
                    <button
                      type="button"
                      onClick={(event) => {
                        event.stopPropagation();
                        handleDeleteClick(e);
                      }}
                      className="flex items-center gap-1 rounded-full bg-gradient-to-br from-red-400 to-orange-400 px-3 py-2 text-sm font-semibold text-white shadow hover:scale-105 transition-all duration-200"
                      title="Delete"
                    >
                      <FaTrash />
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
      <FormsModal open={showCreateModal} onClose={closeAllModals} title="Create a New Essay">
        <EssayForm
          onSuccess={() => {
            closeAllModals();
            void fetchEssays();
          }}
        />
      </FormsModal>
      <FormsModal open={showAgentModal && !showCreateModal && !showDeleteModal} onClose={closeAllModals} title="Provision Foundry Agent">
        <AgentForm
          onSuccess={(agent) => {
            setLatestAgent(agent);
            closeAllModals();
          }}
        />
      </FormsModal>
      <FormsModal open={showDetailsModal} onClose={closeDetailsModal} title="Essay Details">
        {selectedEssay && (
          <EssayForm
            essayData={selectedEssay}
            onSuccess={() => {
              void fetchEssays(selectedEssay.id);
            }}
          />
        )}
      </FormsModal>
      <FormsModal open={showDeleteModal && !showCreateModal} onClose={closeAllModals} title="Confirm Delete">
        <div className="p-6">
          <h2 className="text-2xl font-bold text-red-700 mb-2 flex items-center gap-2">
            <span className="inline-block">⚠️</span>
            Confirm Delete
          </h2>
          <p className="mb-4 text-red-700 dark:text-red-300 font-medium">
            Are you sure you want to delete this essay? This action cannot be undone.
          </p>
          <div className="flex gap-2 mt-4">
            <button className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 transition-colors duration-200" onClick={confirmDelete}>Delete</button>
            <button className="bg-gray-300 px-4 py-2 rounded hover:bg-gray-400 transition-colors duration-200" onClick={closeAllModals}>Cancel</button>
          </div>
        </div>
      </FormsModal>
    </div>
  );
};

export default EssaysList;
