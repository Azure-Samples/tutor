"use client";
import { useEffect, useState } from "react";
import { essaysEngine } from "@/utils/api";
import FormsModal from "@/components/common/Modals";
import { FaTrash, FaPen, FaPlus, FaUser, FaFileAlt, FaListAlt } from "react-icons/fa";
import EssayForm from "@/components/Forms/Essays";
import type { Essay } from "@/types/essays";

const EssaysList: React.FC = () => {
  const [essays, setEssays] = useState<Essay[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedEssay, setSelectedEssay] = useState<Essay | null>(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [modalLoading, setModalLoading] = useState(false);

  const closeAllModals = () => {
    setShowCreateModal(false);
    setShowEditModal(false);
    setShowDeleteModal(false);
  };

  useEffect(() => {
    setLoading(true);
    essaysEngine.get("/essays").then((res) => {
      setEssays(res.data.content || []);
      setLoading(false);
    });
  }, []);

  const handleEditClick = (essay: Essay) => {
    setSelectedEssay(essay);
    closeAllModals();
    setShowEditModal(true);
  };

  const handleDeleteClick = (essay: Essay) => {
    setSelectedEssay(essay);
    closeAllModals();
    setShowDeleteModal(true);
  };

  const confirmDelete = async () => {
    if (!selectedEssay?.id) return;
    await essaysEngine.delete(`/essays/${selectedEssay.id}`);
    setEssays(essays.filter((e) => e.id !== selectedEssay.id));
    closeAllModals();
    setSelectedEssay(null);
  };

  return (
    <div className="w-full p-0">
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <span className="text-lg text-cyan-500 animate-pulse">Loading essays...</span>
        </div>
      ) : (
        <>
          <div className="flex items-center justify-end mb-6">
            <button
              className="flex items-center gap-2 bg-gradient-to-br from-green-400 to-cyan-400 hover:from-cyan-400 hover:to-yellow-300 text-white font-bold px-6 py-3 rounded-full shadow-lg hover:scale-105 transition-all duration-200 text-lg"
              onClick={() => {
                closeAllModals();
                setShowCreateModal(true);
              }}
            >
              <FaPlus className="text-xl" /> New Essay
            </button>
          </div>
          <div className="w-full overflow-x-auto rounded-xl bg-white dark:bg-boxdark shadow">
            <table className="w-full min-w-[600px] text-base">
              <thead>
                <tr className="text-cyan-700 dark:text-cyan-200 text-lg border-b border-cyan-100 dark:border-cyan-900">
                  <th className="hidden">ID</th>
                  <th className="py-4">Topic</th>
                  <th className="py-4">Content</th>
                  <th className="py-4">Explanation</th>
                  <th className="py-4">Actions</th>
                </tr>
              </thead>
              <tbody>
                {essays.map((e) => (
                  <tr key={e.id} className="hover:bg-cyan-50 dark:hover:bg-cyan-900 transition-colors rounded-xl">
                    <td className="hidden">{e.id}</td>
                    <td className="py-4 px-2 text-center font-bold text-blue-700 dark:text-cyan-200">{e.topic}</td>
                    <td className="py-4 px-2 text-center text-green-700 dark:text-green-200 font-semibold">{e.content}</td>
                    <td className="py-4 px-2 text-center text-gray-700 dark:text-gray-200">{e.explanation || "N/A"}</td>
                    <td className="py-4 px-2 text-center">
                      <div className="flex gap-2 justify-center items-center">
                        <button onClick={() => handleDeleteClick(e)} className="bg-gradient-to-br from-red-400 to-orange-400 text-white rounded-full p-2 shadow hover:scale-110 transition-all duration-200" title="Delete"><FaTrash /></button>
                        <button onClick={() => handleEditClick(e)} className="bg-gradient-to-br from-blue-400 to-cyan-400 text-white rounded-full p-2 shadow hover:scale-110 transition-all duration-200" title="Edit"><FaPen /></button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {essays.length === 0 && (
              <div className="flex flex-col items-center justify-center py-16">
                <span className="text-5xl mb-4">🌈</span>
                <p className="text-xl text-cyan-700 dark:text-cyan-200 font-bold mb-2">No essays yet!</p>
                <p className="text-green-700 dark:text-green-200 mb-4">Click <span className="font-bold">New Essay</span> to create your first essay and make learning magical!</p>
              </div>
            )}
          </div>
        </>
      )}
      <FormsModal open={showCreateModal} onClose={closeAllModals} title="Create a New Essay">
        <EssayForm onSuccess={closeAllModals} />
      </FormsModal>
      <FormsModal open={showEditModal && !showCreateModal && !showDeleteModal} onClose={closeAllModals} title="Edit Essay">
        <EssayForm essayData={selectedEssay!} onSuccess={closeAllModals} />
      </FormsModal>
      <FormsModal open={showDeleteModal && !showCreateModal && !showEditModal} onClose={closeAllModals} title="Confirm Delete">
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
