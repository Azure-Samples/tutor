import { useState } from "react";
import { FaHashtag, FaUser, FaRobot, FaFileAlt } from "react-icons/fa";

interface Grader {
  id?: string;
  name: string;
  model_id: string;
  metaprompt: string;
}

const GraderForm: React.FC<{ graderData?: Grader; onSuccess?: () => void }> = ({ graderData, onSuccess }) => {
  const [form, setForm] = useState<Grader>(graderData || { name: "", model_id: "", metaprompt: "" });
  const [status, setStatus] = useState("");
  const isEdit = !!graderData;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus("Saving...");
    // TODO: Implement API call for grader
    setTimeout(() => {
      setStatus(isEdit ? "Grader updated!" : "Grader created!");
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
        <FaHashtag /> Grader ID
      </label>
      <input
        type="text"
        value={form.id || ""}
        onChange={e => setForm({ ...form, id: e.target.value })}
        className="w-full rounded-2xl border-2 border-cyan-200 focus:border-green-400 focus:ring-2 focus:ring-green-200 px-4 py-3 text-lg transition-all duration-200 bg-cyan-50 dark:bg-cyan-900 placeholder:text-cyan-400 focus:bg-white dark:focus:bg-boxdark"
        placeholder="Grader ID"
      />
      <label className="flex items-center gap-2 text-green-700 font-bold">
        <FaUser /> Name
      </label>
      <input
        type="text"
        value={form.name}
        onChange={e => setForm({ ...form, name: e.target.value })}
        className="w-full rounded-2xl border-2 border-green-200 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-200 px-4 py-3 text-lg transition-all duration-200 bg-green-50 dark:bg-green-900 placeholder:text-green-400 focus:bg-white dark:focus:bg-boxdark"
        placeholder="Grader Name"
      />
      <label className="flex items-center gap-2 text-blue-700 font-bold">
        <FaRobot /> Model ID
      </label>
      <input
        type="text"
        value={form.model_id}
        onChange={e => setForm({ ...form, model_id: e.target.value })}
        className="w-full rounded-2xl border-2 border-blue-200 focus:border-yellow-400 focus:ring-2 focus:ring-yellow-200 px-4 py-3 text-lg transition-all duration-200 bg-blue-50 dark:bg-blue-900 placeholder:text-blue-400 focus:bg-white dark:focus:bg-boxdark"
        placeholder="Model ID"
      />
      <label className="flex items-center gap-2 text-yellow-700 font-bold">
        <FaFileAlt /> Metaprompt
      </label>
      <textarea
        value={form.metaprompt}
        onChange={e => setForm({ ...form, metaprompt: e.target.value })}
        className="w-full rounded-2xl border-2 border-yellow-200 focus:border-green-400 focus:ring-2 focus:ring-green-200 px-4 py-3 text-lg transition-all duration-200 bg-yellow-50 dark:bg-yellow-900 placeholder:text-yellow-400 focus:bg-white dark:focus:bg-boxdark resize-y min-h-[48px] max-h-[320px]"
        placeholder="Metaprompt (JSON)"
        rows={3}
      />
      {status && <p className="mt-2 text-center text-sm text-gray-700 dark:text-gray-300">{status}</p>}
    </form>
  );
};

export default GraderForm;
