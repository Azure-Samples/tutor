"use client";

import { useEffect, useState } from "react";
import { FaPen, FaPlus, FaTrash } from "react-icons/fa";

import FormsModal from "@/components/common/Modals";
import AnswerForm from "@/components/Forms/Answers";
import { useQuestionsAnswers } from "@/hooks/useQuestionsAnswers";
import type { Answer } from "@/types/answer";
import { questionsEngine } from "@/utils/api";

const AnswersList: React.FC = () => {
  const { answers, setAnswers, loading, error, refresh } = useQuestionsAnswers();
  const [selectedAnswer, setSelectedAnswer] = useState<Answer | null>(null);
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

  const handleEdit = (answer: Answer) => {
    setSelectedAnswer(answer);
    closeAllModals();
    setShowEditModal(true);
  };

  const handleDelete = (answer: Answer) => {
    setSelectedAnswer(answer);
    closeAllModals();
    setShowDeleteModal(true);
  };

  const confirmDelete = async () => {
    if (!selectedAnswer?.id) {
      return;
    }
    await questionsEngine.delete(`/answers/${encodeURIComponent(selectedAnswer.id)}`);
    setAnswers((prev) => prev.filter((item) => item.id !== selectedAnswer.id));
    closeAllModals();
    setSelectedAnswer(null);
  };

  return (
    <div className="w-full p-0">
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <span className="text-lg text-cyan-500 animate-pulse">Loading answers...</span>
        </div>
      ) : (
        <>
          <div className="flex items-center justify-between mb-6 gap-3">
            <p className="text-sm text-gray-600 dark:text-gray-300">
              Stored learner responses used by evaluator workflows.
            </p>
            <button
              className="flex items-center gap-2 bg-gradient-to-br from-green-400 to-cyan-400 hover:from-cyan-400 hover:to-yellow-300 text-white font-bold px-6 py-3 rounded-full shadow-lg hover:scale-105 transition-all duration-200 text-lg"
              onClick={() => {
                closeAllModals();
                setSelectedAnswer(null);
                setShowCreateModal(true);
              }}
            >
              <FaPlus className="text-xl" /> New Answer
            </button>
          </div>

          {error && <p className="mb-4 text-sm text-red-600">{error}</p>}

          <div className="w-full overflow-x-auto rounded-xl bg-white dark:bg-boxdark shadow">
            <table className="w-full min-w-[700px] text-base">
              <thead>
                <tr className="text-cyan-700 dark:text-cyan-200 text-lg border-b border-cyan-100 dark:border-cyan-900">
                  <th className="py-4">Answer ID</th>
                  <th className="py-4">Question ID</th>
                  <th className="py-4">Respondent</th>
                  <th className="py-4">Text</th>
                  <th className="py-4">Actions</th>
                </tr>
              </thead>
              <tbody>
                {answers.map((answer) => (
                  <tr key={answer.id} className="hover:bg-cyan-50 dark:hover:bg-cyan-900 transition-colors rounded-xl">
                    <td className="py-4 px-2 text-center font-semibold text-cyan-700 dark:text-cyan-200">{answer.id}</td>
                    <td className="py-4 px-2 text-center text-green-700 dark:text-green-200">{answer.question_id}</td>
                    <td className="py-4 px-2 text-center text-blue-700 dark:text-blue-200">{answer.respondent}</td>
                    <td className="py-4 px-2 text-center text-gray-700 dark:text-gray-200 max-w-[280px] truncate">{answer.text}</td>
                    <td className="py-4 px-2 text-center">
                      <div className="flex gap-2 justify-center items-center">
                        <button onClick={() => handleEdit(answer)} className="bg-gradient-to-br from-blue-400 to-cyan-400 text-white rounded-full p-2 shadow hover:scale-110 transition-all duration-200" title="Edit"><FaPen /></button>
                        <button onClick={() => handleDelete(answer)} className="bg-gradient-to-br from-red-400 to-orange-400 text-white rounded-full p-2 shadow hover:scale-110 transition-all duration-200" title="Delete"><FaTrash /></button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {answers.length === 0 && (
              <div className="flex flex-col items-center justify-center py-16">
                <span className="text-5xl mb-4">🧾</span>
                <p className="text-xl text-cyan-700 dark:text-cyan-200 font-bold mb-2">No answers yet!</p>
                <p className="text-green-700 dark:text-green-200 mb-4">Create an answer to validate question evaluation flows.</p>
              </div>
            )}
          </div>
        </>
      )}

      <FormsModal open={showCreateModal} onClose={closeAllModals} title="Create a New Answer">
        <AnswerForm onSuccess={() => { closeAllModals(); void refresh(); }} />
      </FormsModal>

      <FormsModal open={showEditModal && !showCreateModal && !showDeleteModal} onClose={closeAllModals} title="Edit Answer">
        {selectedAnswer && <AnswerForm answerData={selectedAnswer} onSuccess={() => { closeAllModals(); void refresh(); }} />}
      </FormsModal>

      <FormsModal open={showDeleteModal && !showCreateModal && !showEditModal} onClose={closeAllModals} title="Confirm Delete">
        <div className="p-6">
          <h2 className="text-2xl font-bold text-red-700 mb-2 flex items-center gap-2"><span className="inline-block">⚠️</span>Confirm Delete</h2>
          <p className="mb-4 text-red-700 dark:text-red-300 font-medium">Are you sure you want to delete this answer? This action cannot be undone.</p>
          <div className="flex gap-2 mt-4">
            <button className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 transition-colors duration-200" onClick={confirmDelete}>Delete</button>
            <button className="bg-gray-300 px-4 py-2 rounded hover:bg-gray-400 transition-colors duration-200" onClick={closeAllModals}>Cancel</button>
          </div>
        </div>
      </FormsModal>
    </div>
  );
};

export default AnswersList;
