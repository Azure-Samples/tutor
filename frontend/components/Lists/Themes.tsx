"use client";
import ThemeForm from "@/components/Forms/Themes";
import FormsModal from "@/components/common/Modals";
import { unwrapContent } from "@/types/api";
import type { Theme } from "@/types/theme";
import { configurationApi } from "@/utils/api";
import { useCallback, useEffect, useState } from "react";
import { FaPen, FaPlus, FaTrash } from "react-icons/fa";

const ThemesList: React.FC = () => {
  const [themes, setThemes] = useState<Theme[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedTheme, setSelectedTheme] = useState<Theme | null>(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [modalLoading, setModalLoading] = useState(false);

  const closeAllModals = () => {
    setShowCreateModal(false);
    setShowEditModal(false);
    setShowDeleteModal(false);
  };

  const fetchThemes = useCallback(async () => {
    setLoading(true);
    try {
      const res = await configurationApi.get("/themes");
      const data = unwrapContent<Theme[]>(res.data);
      setThemes(Array.isArray(data) ? data : []);
    } catch {
      setThemes([]);
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    void fetchThemes();
  }, [fetchThemes]);

  const handleEditClick = async (t: Theme) => {
    setModalLoading(true);
    closeAllModals();
    setShowEditModal(true);
    setSelectedTheme(t);
    setModalLoading(false);
  };

  const handleDeleteClick = (t: Theme) => {
    setSelectedTheme(t);
    closeAllModals();
    setShowDeleteModal(true);
  };

  const confirmDelete = async () => {
    if (!selectedTheme?.id) return;
    await configurationApi.delete(`/themes/${selectedTheme.id}`);
    setThemes(themes.filter((t) => t.id !== selectedTheme.id));
    closeAllModals();
    setSelectedTheme(null);
  };

  return (
    <div className="w-full p-0">
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <span className="text-lg text-cyan-500 animate-pulse">Loading themes...</span>
        </div>
      ) : (
        <>
          <div className="flex items-center justify-end mb-6">
            <button
              type="button"
              className="flex items-center gap-2 bg-gradient-to-br from-green-400 to-cyan-400 hover:from-cyan-400 hover:to-yellow-300 text-white font-bold px-6 py-3 rounded-full shadow-lg hover:scale-105 transition-all duration-200 text-lg"
              onClick={() => {
                closeAllModals();
                setShowCreateModal(true);
              }}
            >
              <FaPlus className="text-xl" /> New Theme
            </button>
          </div>
          <div className="w-full overflow-x-auto rounded-xl bg-white dark:bg-boxdark shadow">
            <table className="w-full min-w-[600px] text-base">
              <thead>
                <tr className="text-cyan-700 dark:text-cyan-200 text-lg border-b border-cyan-100 dark:border-cyan-900">
                  <th className="py-4">Name</th>
                  <th className="py-4">Objective</th>
                  <th className="py-4">Criteria</th>
                  <th className="py-4">Actions</th>
                </tr>
              </thead>
              <tbody>
                {themes.map((t) => (
                  <tr
                    key={t.id ?? `${t.name}-${t.objective}`}
                    className="hover:bg-cyan-50 dark:hover:bg-cyan-900 transition-colors rounded-xl"
                  >
                    <td className="py-4 px-2 text-center font-bold text-blue-700 dark:text-cyan-200">
                      {t.name}
                    </td>
                    <td className="py-4 px-2 text-center text-green-700 dark:text-green-200 font-semibold">
                      {t.objective}
                    </td>
                    <td className="py-4 px-2 text-center text-gray-700 dark:text-gray-200">
                      {t.criteria.length} criteria
                    </td>
                    <td className="py-4 px-2 text-center">
                      <div className="flex gap-2 justify-center items-center">
                        <button
                          type="button"
                          onClick={() => handleDeleteClick(t)}
                          className="bg-gradient-to-br from-red-400 to-orange-400 text-white rounded-full p-2 shadow hover:scale-110 transition-all duration-200"
                          title="Delete"
                        >
                          <FaTrash />
                        </button>
                        <button
                          type="button"
                          onClick={() => handleEditClick(t)}
                          className="bg-gradient-to-br from-blue-400 to-cyan-400 text-white rounded-full p-2 shadow hover:scale-110 transition-all duration-200"
                          title="Edit"
                        >
                          <FaPen />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {themes.length === 0 && (
              <div className="flex flex-col items-center justify-center py-16">
                <span className="text-5xl mb-4">📋</span>
                <p className="text-xl text-cyan-700 dark:text-cyan-200 font-bold mb-2">
                  No themes yet!
                </p>
                <p className="text-green-700 dark:text-green-200 mb-4">
                  Click <span className="font-bold">New Theme</span> to create your first theme and
                  start evaluating essays!
                </p>
              </div>
            )}
          </div>
        </>
      )}
      <FormsModal open={showCreateModal} onClose={closeAllModals} title="Create a New Theme">
        <ThemeForm
          onSuccess={() => {
            closeAllModals();
            fetchThemes();
          }}
        />
      </FormsModal>
      <FormsModal
        open={showEditModal && !showCreateModal && !showDeleteModal}
        onClose={closeAllModals}
        title="Edit Theme"
      >
        {selectedTheme && (
          <ThemeForm
            themeData={selectedTheme}
            onSuccess={() => {
              closeAllModals();
              fetchThemes();
            }}
          />
        )}
      </FormsModal>
      <FormsModal
        open={showDeleteModal && !showCreateModal && !showEditModal}
        onClose={closeAllModals}
        title="Confirm Delete"
      >
        <div className="p-6">
          <h2 className="text-2xl font-bold text-red-700 mb-2 flex items-center gap-2">
            <span className="inline-block">⚠️</span>Confirm Delete
          </h2>
          <p className="mb-4 text-red-700 dark:text-red-300 font-medium">
            Are you sure you want to delete this theme? This action cannot be undone.
          </p>
          <div className="flex gap-2 mt-4">
            <button
              type="button"
              className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 transition-colors duration-200"
              onClick={confirmDelete}
            >
              Delete
            </button>
            <button
              type="button"
              className="bg-gray-300 px-4 py-2 rounded hover:bg-gray-400 transition-colors duration-200"
              onClick={closeAllModals}
            >
              Cancel
            </button>
          </div>
        </div>
      </FormsModal>
    </div>
  );
};

export default ThemesList;
