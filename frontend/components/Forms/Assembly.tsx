import { useState } from "react";
import { FaHashtag, FaUserFriends, FaBook } from "react-icons/fa";

interface Assembly {
  id?: string;
  agents: string; // Comma-separated Grader IDs
  topic_name: string;
}

const AssemblyForm: React.FC<{ assemblyData?: Assembly; onSuccess?: () => void }> = ({ assemblyData, onSuccess }) => {
  const [form, setForm] = useState<Assembly>(assemblyData || { agents: "", topic_name: "" });
  const [status, setStatus] = useState("");
  const isEdit = !!assemblyData;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus("Saving...");
    // TODO: Implement API call for assembly
    setTimeout(() => {
      setStatus(isEdit ? "Assembly updated!" : "Assembly created!");
      if (onSuccess) onSuccess();
    }, 800);
  };

  return (
    <form
      className="flex flex-col gap-4 w-full max-w-xl mx-auto p-0 form-dot-scrollbar overflow-y-auto"
      id="modal-form"
      onSubmit={handleSubmit}
    >
      <label className="flex items-center gap-2 text-cyan-700 font-bold">
        <FaHashtag /> Assembly ID
      </label>
      <input
        type="text"
        value={form.id || ""}
        onChange={e => setForm({ ...form, id: e.target.value })}
        className="w-full rounded-2xl border-2 border-cyan-200 focus:border-green-400 focus:ring-2 focus:ring-green-200 px-4 py-3 text-lg transition-all duration-200 bg-cyan-50 dark:bg-cyan-900 placeholder:text-cyan-400 focus:bg-white dark:focus:bg-boxdark"
        placeholder="Assembly ID"
      />
      <label className="flex items-center gap-2 text-green-700 font-bold">
        <FaUserFriends /> Grader IDs (comma-separated)
      </label>
      <input
        type="text"
        value={form.agents}
        onChange={e => setForm({ ...form, agents: e.target.value })}
        className="w-full rounded-2xl border-2 border-green-200 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-200 px-4 py-3 text-lg transition-all duration-200 bg-green-50 dark:bg-green-900 placeholder:text-green-400 focus:bg-white dark:focus:bg-boxdark"
        placeholder="Grader IDs (comma-separated)"
      />
      <label className="flex items-center gap-2 text-blue-700 font-bold">
        <FaBook /> Topic Name
      </label>
      <input
        type="text"
        value={form.topic_name}
        onChange={e => setForm({ ...form, topic_name: e.target.value })}
        className="w-full rounded-2xl border-2 border-blue-200 focus:border-yellow-400 focus:ring-2 focus:ring-yellow-200 px-4 py-3 text-lg transition-all duration-200 bg-blue-50 dark:bg-blue-900 placeholder:text-blue-400 focus:bg-white dark:focus:bg-boxdark"
        placeholder="Topic Name"
      />
      {status && <p className="mt-2 text-center text-sm text-gray-700 dark:text-gray-300">{status}</p>}
    </form>
  );
};

export default AssemblyForm;
