"use client";

import { useEffect, useState } from "react";
import { FaPen, FaPlus, FaTrash } from "react-icons/fa";

import GraderForm from "@/components/Forms/Grader";
import FormsModal from "@/components/common/Modals";
import { useQuestionsGraders } from "@/hooks/useQuestionsGraders";
import type { Grader } from "@/types/grader";
import { questionsEngine } from "@/utils/api";

const GradersList: React.FC = () => {
  const { graders, setGraders, loading, error, refresh } = useQuestionsGraders();
  const [selectedGrader, setSelectedGrader] = useState<Grader | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const closeAllModals = () => {
    setShowCreateModal(false);
    setShowEditModal(false);
    setShowDeleteModal(false);
  };

  const handleEdit = (grader: Grader) => {
    setSelectedGrader(grader);
    closeAllModals();
    setShowEditModal(true);
  };

  const handleDelete = (grader: Grader) => {
    setSelectedGrader(grader);
    closeAllModals();
    setShowDeleteModal(true);
  };

  const confirmDelete = async () => {
    if (!selectedGrader?.agent_id) {
      return;
    }
    await questionsEngine.delete(`/graders/${encodeURIComponent(selectedGrader.agent_id)}`);
    setGraders((prev) => prev.filter((item) => item.agent_id !== selectedGrader.agent_id));
    closeAllModals();
    setSelectedGrader(null);
  };

  return (
    <div className="w-full p-0">
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <span className="text-lg text-cyan-500 animate-pulse">Loading graders...</span>
        </div>
      ) : (
        <>
          <div className="flex items-center justify-between mb-6 gap-3">
            <p className="text-sm text-gray-600 dark:text-gray-300">
              Manage question grader agents referenced by assemblies.
            </p>
            <button
              className="flex items-center gap-2 bg-gradient-to-br from-green-400 to-cyan-400 hover:from-cyan-400 hover:to-yellow-300 text-white font-bold px-6 py-3 rounded-full shadow-lg hover:scale-105 transition-all duration-200 text-lg"
              onClick={() => {
                closeAllModals();
                setSelectedGrader(null);
                setShowCreateModal(true);
              }}
            >
              <FaPlus className="text-xl" /> New Grader
            </button>
          </div>

          {error && <p className="mb-4 text-sm text-red-600">{error}</p>}

          <div className="w-full overflow-x-auto rounded-xl bg-white dark:bg-boxdark shadow">
            <table className="w-full min-w-[650px] text-base">
              <thead>
                <tr className="text-cyan-700 dark:text-cyan-200 text-lg border-b border-cyan-100 dark:border-cyan-900">
                  <th className="py-4">Agent ID</th>
                  <th className="py-4">Dimension</th>
                  <th className="py-4">Deployment</th>
                  <th className="py-4">Actions</th>
                </tr>
              </thead>
              <tbody>
                {graders.map((grader) => (
                  <tr key={grader.agent_id} className="hover:bg-cyan-50 dark:hover:bg-cyan-900 transition-colors rounded-xl">
                    <td className="py-4 px-2 text-center font-semibold text-cyan-700 dark:text-cyan-200">{grader.agent_id}</td>
                    <td className="py-4 px-2 text-center text-green-700 dark:text-green-200">{grader.dimension}</td>
                    <td className="py-4 px-2 text-center text-blue-700 dark:text-blue-200">{grader.deployment}</td>
                    <td className="py-4 px-2 text-center">
                      <div className="flex gap-2 justify-center items-center">
                        <button onClick={() => handleEdit(grader)} className="bg-gradient-to-br from-blue-400 to-cyan-400 text-white rounded-full p-2 shadow hover:scale-110 transition-all duration-200" title="Edit"><FaPen /></button>
                        <button onClick={() => handleDelete(grader)} className="bg-gradient-to-br from-red-400 to-orange-400 text-white rounded-full p-2 shadow hover:scale-110 transition-all duration-200" title="Delete"><FaTrash /></button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {graders.length === 0 && (
              <div className="flex flex-col items-center justify-center py-16">
                <span className="text-5xl mb-4">🧠</span>
                <p className="text-xl text-cyan-700 dark:text-cyan-200 font-bold mb-2">No graders yet!</p>
                <p className="text-green-700 dark:text-green-200 mb-4">Create graders to compose evaluator assemblies.</p>
              </div>
            )}
          </div>
        </>
      )}

      <FormsModal open={showCreateModal} onClose={closeAllModals} title="Create a New Grader">
        <GraderForm onSuccess={() => { closeAllModals(); void refresh(); }} />
      </FormsModal>

      <FormsModal open={showEditModal && !showCreateModal && !showDeleteModal} onClose={closeAllModals} title="Edit Grader">
        {selectedGrader && <GraderForm graderData={selectedGrader} onSuccess={() => { closeAllModals(); void refresh(); }} />}
      </FormsModal>

      <FormsModal open={showDeleteModal && !showCreateModal && !showEditModal} onClose={closeAllModals} title="Confirm Delete">
        <div className="p-6">
          <h2 className="text-2xl font-bold text-red-700 mb-2 flex items-center gap-2"><span className="inline-block">⚠️</span>Confirm Delete</h2>
          <p className="mb-4 text-red-700 dark:text-red-300 font-medium">Are you sure you want to delete this grader? This action cannot be undone.</p>
          <div className="flex gap-2 mt-4">
            <button className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 transition-colors duration-200" onClick={confirmDelete}>Delete</button>
            <button className="bg-gray-300 px-4 py-2 rounded hover:bg-gray-400 transition-colors duration-200" onClick={closeAllModals}>Cancel</button>
          </div>
        </div>
      </FormsModal>
    </div>
  );
};

export default GradersList;
