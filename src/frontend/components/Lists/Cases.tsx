"use client";
import { useEffect, useState } from "react";
import { avatarEngine } from "@/utils/api";
import { Case } from "@/types/cases";
import FormsModal from "@/components/common/Modals";
import { FaTrash, FaPen, FaUser, FaPlus } from "react-icons/fa";
import CaseForm from "@/components/Forms/Cases";
import StepsForm from "@/components/Forms/Steps";
import ProfileForm from "@/components/Forms/Profile";

const CasesList: React.FC = () => {
  const [cases, setCases] = useState<Case[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCase, setSelectedCase] = useState<Case | null>(null);
  const [showStepsModal, setShowStepsModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [modalLoading, setModalLoading] = useState(false);

  const closeAllModals = () => {
    setShowCreateModal(false);
    setShowStepsModal(false);
    setShowEditModal(false);
    setShowProfileModal(false);
    setShowDeleteModal(false);
  };

  useEffect(() => {
    setLoading(true);
    avatarEngine.get("/cases").then((res) => {
      setCases(res.data.result || []);
      setLoading(false);
    });
  }, []);

  const handleStepsClick = (c: Case) => {
    setSelectedCase(c);
    closeAllModals();
    setShowStepsModal(true);
  };

  const handleEditClick = async (id?: string) => {
    if (!id) return;
    setModalLoading(true);
    closeAllModals();
    setShowEditModal(true);
    const res = await avatarEngine.get(`/cases/${id}`);
    setSelectedCase(res.data.result);
    setModalLoading(false);
  };

  const handleProfileClick = async (id?: string) => {
    if (!id) return;
    setModalLoading(true);
    closeAllModals();
    setShowProfileModal(true);
    const res = await avatarEngine.get(`/cases/${id}`);
    setSelectedCase(res.data.result);
    setModalLoading(false);
  };

  const handleDeleteClick = (c: Case) => {
    setSelectedCase(c);
    closeAllModals();
    setShowDeleteModal(true);
  };

  const confirmDelete = async () => {
    if (!selectedCase?.id) return;
    await avatarEngine.delete(`/cases/${selectedCase.id}`);
    setCases(cases.filter((c) => c.id !== selectedCase.id));
    closeAllModals();
    setSelectedCase(null);
  };

  return (
    <div className="w-full p-0">
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <span className="text-lg text-cyan-500 animate-pulse">Loading cases...</span>
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
              <FaPlus className="text-xl" /> New Case
            </button>
          </div>
          <div className="w-full overflow-x-auto rounded-xl bg-white dark:bg-boxdark shadow">
            <table className="w-full min-w-[600px] text-base">
              <thead>
                <tr className="text-cyan-700 dark:text-cyan-200 text-lg border-b border-cyan-100 dark:border-cyan-900">
                  <th className="hidden">ID</th>
                  <th className="py-4">Name</th>
                  <th className="py-4">Role</th>
                  <th className="py-4">Steps</th>
                  <th className="py-4">Actions</th>
                </tr>
              </thead>
              <tbody>
                {cases.map((c) => (
                  <tr key={c.id} className="hover:bg-cyan-50 dark:hover:bg-cyan-900 transition-colors rounded-xl">
                    <td className="hidden">{c.id}</td>
                    <td className="py-4 px-2 text-center font-bold text-blue-700 dark:text-cyan-200">
                      <span className="inline-block">🎭</span> {c.name}
                    </td>
                    <td className="py-4 px-2 text-center text-green-700 dark:text-green-200 font-semibold">{c.role}</td>
                    <td className="py-4 px-2 text-center">
                      <button className="text-cyan-600 font-bold underline hover:text-yellow-500 transition-colors duration-200" onClick={() => handleStepsClick(c)}>
                        {c.steps?.length || 0}
                      </button>
                    </td>
                    <td className="py-4 px-2 text-center">
                      <div className="flex gap-2 justify-center items-center">
                        <button onClick={() => handleDeleteClick(c)} className="bg-gradient-to-br from-red-400 to-orange-400 text-white rounded-full p-2 shadow hover:scale-110 transition-all duration-200" title="Delete"><FaTrash /></button>
                        <button onClick={() => handleEditClick(c.id)} className="bg-gradient-to-br from-blue-400 to-cyan-400 text-white rounded-full p-2 shadow hover:scale-110 transition-all duration-200" title="Edit"><FaPen /></button>
                        <button onClick={() => handleProfileClick(c.id)} className="bg-gradient-to-br from-green-400 to-yellow-400 text-white rounded-full p-2 shadow hover:scale-110 transition-all duration-200" title="Profile"><FaUser /></button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {cases.length === 0 && (
              <div className="flex flex-col items-center justify-center py-16">
                <span className="text-5xl mb-4">🌈</span>
                <p className="text-xl text-cyan-700 dark:text-cyan-200 font-bold mb-2">No cases yet!</p>
                <p className="text-green-700 dark:text-green-200 mb-4">Click <span className="font-bold">New Case</span> to create your first scenario and make learning magical!</p>
              </div>
            )}
          </div>
        </>
      )}
      <FormsModal open={showCreateModal} onClose={closeAllModals} title="Create a New Case">
        <CaseForm onSuccess={closeAllModals} />
      </FormsModal>
      <FormsModal open={showStepsModal && !showCreateModal && !showEditModal && !showProfileModal && !showDeleteModal} onClose={closeAllModals} title="Case Steps">
        {selectedCase ? (
          <StepsForm
            steps={selectedCase.steps || []}
            onChange={() => {}}
            readOnly={false}
            caseId={selectedCase.id}
          />
        ) : (
          <div className="flex justify-center items-center h-40">
            <span className="text-lg text-gray-500">Loading...</span>
          </div>
        )}
      </FormsModal>
      <FormsModal open={showEditModal && !showCreateModal && !showDeleteModal} onClose={closeAllModals} title="Edit Case">
        <CaseForm caseData={selectedCase!} onSuccess={closeAllModals} />
      </FormsModal>
      <FormsModal open={showProfileModal && !showCreateModal && !showStepsModal && !showEditModal && !showDeleteModal} onClose={closeAllModals} title="Case Profile">
        {modalLoading ? (
          <div className="flex justify-center items-center h-40">
            <span className="text-lg text-gray-500">Loading...</span>
          </div>
        ) : selectedCase?.profile ? (
          <ProfileForm
            profile={selectedCase.profile}
            onChange={() => {}}
            readOnly={true}
          />
        ) : null}
      </FormsModal>
      <FormsModal open={showDeleteModal && !showCreateModal && !showEditModal} onClose={closeAllModals} title="Confirm Delete">
        <div className="p-6">
          <h2 className="text-2xl font-bold text-red-700 mb-2 flex items-center gap-2">
            <span className="inline-block">⚠️</span>
            Confirm Delete
          </h2>
          <p className="mb-4 text-red-700 dark:text-red-300 font-medium">
            Are you sure you want to delete this case? This action cannot be undone.
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

export default CasesList;