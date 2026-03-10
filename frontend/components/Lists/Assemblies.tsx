"use client";
import { useEffect, useState } from "react";
import { essaysEngine, questionsEngine } from "@/utils/api";
import { unwrapContent } from "@/types/api";
import FormsModal from "@/components/common/Modals";
import { FaTrash, FaPlus, FaEye } from "react-icons/fa";
import AssemblyForm from "@/components/Forms/Assemblies";
import type { AssemblyDefinition } from "@/types/essays";
import type { Assembly as QAssembly } from "@/types/assembly";

type UnifiedAssembly = {
  id: string;
  topic_name: string;
  service: "essays" | "questions";
  essay_id?: string;
  agents: { agent_id?: string; name?: string; deployment: string; role?: string; temperature?: number; dimension?: string; instructions?: string }[];
};

const AssembliesList: React.FC = () => {
  const [assemblies, setAssemblies] = useState<UnifiedAssembly[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedAssembly, setSelectedAssembly] = useState<UnifiedAssembly | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showDetailsModal, setShowDetailsModal] = useState(false);

  const closeAllModals = () => {
    setShowCreateModal(false);
    setShowDeleteModal(false);
    setShowDetailsModal(false);
  };

  const fetchAssemblies = async () => {
    setLoading(true);
    try {
      const [essayRes, questionRes] = await Promise.allSettled([
        essaysEngine.get("/assemblies"),
        questionsEngine.get("/assemblies"),
      ]);

      const unified: UnifiedAssembly[] = [];

      if (essayRes.status === "fulfilled") {
        const essayData = unwrapContent<AssemblyDefinition[]>(essayRes.value.data);
        if (Array.isArray(essayData)) {
          for (const s of essayData) {
            unified.push({
              id: s.id,
              topic_name: s.topic_name,
              service: "essays",
              essay_id: s.essay_id,
              agents: s.agents.map((a) => ({
                agent_id: a.agent_id,
                name: a.name,
                instructions: a.instructions,
                deployment: a.deployment,
                role: a.role,
                temperature: a.temperature,
              })),
            });
          }
        }
      }

      if (questionRes.status === "fulfilled") {
        const questionData = unwrapContent<QAssembly[]>(questionRes.value.data);
        if (Array.isArray(questionData)) {
          for (const a of questionData) {
            unified.push({
              id: a.id,
              topic_name: a.topic_name ?? "",
              service: "questions",
              agents: a.agents.map((g) => ({
                agent_id: g.agent_id,
                dimension: g.dimension,
                deployment: g.deployment,
              })),
            });
          }
        }
      }

      setAssemblies(unified);
    } catch {
      setAssemblies([]);
    }
    setLoading(false);
  };

  useEffect(() => { fetchAssemblies(); }, []);

  const handleDeleteClick = (a: UnifiedAssembly) => {
    setSelectedAssembly(a);
    closeAllModals();
    setShowDeleteModal(true);
  };

  const handleDetailsClick = (a: UnifiedAssembly) => {
    setSelectedAssembly(a);
    closeAllModals();
    setShowDetailsModal(true);
  };

  const confirmDelete = async () => {
    if (!selectedAssembly?.id || selectedAssembly.service !== "questions") return;
    await questionsEngine.delete(`/assemblies/${selectedAssembly.id}`);
    setAssemblies(assemblies.filter((a) => a.id !== selectedAssembly.id));
    closeAllModals();
    setSelectedAssembly(null);
  };

  return (
    <div className="w-full p-0">
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <span className="text-lg text-cyan-500 animate-pulse">Loading assemblies...</span>
        </div>
      ) : (
        <>
          <div className="flex items-center justify-end mb-6">
            <button
              className="flex items-center gap-2 bg-gradient-to-br from-green-400 to-cyan-400 hover:from-cyan-400 hover:to-yellow-300 text-white font-bold px-6 py-3 rounded-full shadow-lg hover:scale-105 transition-all duration-200 text-lg"
              onClick={() => { closeAllModals(); setShowCreateModal(true); }}
            >
              <FaPlus className="text-xl" /> New Assembly
            </button>
          </div>
          <div className="w-full overflow-x-auto rounded-xl bg-white dark:bg-boxdark shadow">
            <table className="w-full min-w-[600px] text-base">
              <thead>
                <tr className="text-cyan-700 dark:text-cyan-200 text-lg border-b border-cyan-100 dark:border-cyan-900">
                  <th className="py-4">Service</th>
                  <th className="py-4">Topic</th>
                  <th className="py-4">Essay ID</th>
                  <th className="py-4">Agents</th>
                  <th className="py-4">Actions</th>
                </tr>
              </thead>
              <tbody>
                {assemblies.map((a, idx) => (
                  <tr key={a.id + idx} className="hover:bg-cyan-50 dark:hover:bg-cyan-900 transition-colors rounded-xl">
                    <td className="py-4 px-2 text-center">
                      {a.service === "essays" ? (
                        <span className="inline-block px-3 py-1 rounded-full text-xs font-bold bg-gradient-to-br from-yellow-300 to-pink-400 text-white shadow">Essays</span>
                      ) : (
                        <span className="inline-block px-3 py-1 rounded-full text-xs font-bold bg-gradient-to-br from-green-300 to-lime-400 text-white shadow">Questions</span>
                      )}
                    </td>
                    <td className="py-4 px-2 text-center font-bold text-blue-700 dark:text-cyan-200">{a.topic_name}</td>
                    <td className="py-4 px-2 text-center text-green-700 dark:text-green-200 font-semibold">{a.essay_id || "—"}</td>
                    <td className="py-4 px-2 text-center text-gray-700 dark:text-gray-200">{a.agents.length} agents</td>
                    <td className="py-4 px-2 text-center">
                      <div className="flex gap-2 justify-center items-center">
                        <button
                          onClick={() => handleDetailsClick(a)}
                          className="bg-gradient-to-br from-blue-400 to-cyan-400 text-white rounded-full p-2 shadow hover:scale-110 transition-all duration-200"
                          title="View details"
                        >
                          <FaEye />
                        </button>
                        {a.service === "questions" && (
                          <button
                            onClick={() => handleDeleteClick(a)}
                            className="bg-gradient-to-br from-red-400 to-orange-400 text-white rounded-full p-2 shadow hover:scale-110 transition-all duration-200"
                            title="Delete"
                          >
                            <FaTrash />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {assemblies.length === 0 && (
              <div className="flex flex-col items-center justify-center py-16">
                <span className="text-5xl mb-4">🤖</span>
                <p className="text-xl text-cyan-700 dark:text-cyan-200 font-bold mb-2">No assemblies yet!</p>
                <p className="text-green-700 dark:text-green-200 mb-4">Click <span className="font-bold">New Assembly</span> to configure your first AI evaluator swarm.</p>
              </div>
            )}
          </div>
        </>
      )}

      <FormsModal open={showCreateModal} onClose={closeAllModals} title="Create a New Assembly">
        <AssemblyForm onSuccess={() => { closeAllModals(); fetchAssemblies(); }} />
      </FormsModal>

      <FormsModal open={showDeleteModal && !showCreateModal && !showDetailsModal} onClose={closeAllModals} title="Confirm Delete">
        <div className="p-6">
          <h2 className="text-2xl font-bold text-red-700 mb-2 flex items-center gap-2"><span className="inline-block">⚠️</span>Confirm Delete</h2>
          <p className="mb-4 text-red-700 dark:text-red-300 font-medium">Are you sure you want to delete this assembly? This action cannot be undone.</p>
          <div className="flex gap-2 mt-4">
            <button className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 transition-colors duration-200" onClick={confirmDelete}>Delete</button>
            <button className="bg-gray-300 px-4 py-2 rounded hover:bg-gray-400 transition-colors duration-200" onClick={closeAllModals}>Cancel</button>
          </div>
        </div>
      </FormsModal>

      <FormsModal open={showDetailsModal && !showCreateModal && !showDeleteModal} onClose={closeAllModals} title="Assembly Details">
        {selectedAssembly && (
          <div className="p-4 flex flex-col gap-4">
            <div className="flex items-center gap-3 mb-2">
              {selectedAssembly.service === "essays" ? (
                <span className="inline-block px-3 py-1 rounded-full text-xs font-bold bg-gradient-to-br from-yellow-300 to-pink-400 text-white shadow">Essays</span>
              ) : (
                <span className="inline-block px-3 py-1 rounded-full text-xs font-bold bg-gradient-to-br from-green-300 to-lime-400 text-white shadow">Questions</span>
              )}
              <span className="font-bold text-lg text-blue-700 dark:text-cyan-200">{selectedAssembly.topic_name}</span>
              {selectedAssembly.essay_id && (
                <span className="text-sm text-green-700 dark:text-green-300">Essay: {selectedAssembly.essay_id}</span>
              )}
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {selectedAssembly.agents.map((agent, idx) => (
                <div key={agent.agent_id ?? String(idx)} className="rounded-2xl border-2 border-purple-200 dark:border-purple-800 bg-purple-50 dark:bg-purple-900 p-4 shadow">
                  <p className="font-bold text-purple-700 dark:text-purple-200 text-lg mb-1">{agent.role ?? agent.dimension ?? agent.name ?? "Agent"}</p>
                  <p className="text-sm text-blue-700 dark:text-blue-300 mb-1">Deployment: <span className="font-semibold">{agent.deployment}</span></p>
                  {agent.agent_id && (
                    <p className="text-sm text-cyan-700 dark:text-cyan-300 mb-1">ID: <span className="font-mono text-xs">{agent.agent_id}</span></p>
                  )}
                  {agent.dimension && (
                    <p className="text-sm text-green-700 dark:text-green-300 mb-1">Dimension: <span className="font-semibold">{agent.dimension}</span></p>
                  )}
                </div>
              ))}
            </div>
            {selectedAssembly.agents.length === 0 && (
              <p className="text-center text-gray-500 dark:text-gray-400 italic">No agents in this assembly.</p>
            )}
          </div>
        )}
      </FormsModal>
    </div>
  );
};

export default AssembliesList;
