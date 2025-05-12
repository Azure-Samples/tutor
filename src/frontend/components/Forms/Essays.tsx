import { useState } from "react";
import type { Essay } from "@/types/essays";
import { essaysEngine } from "@/utils/api";
import { FaPen, FaFileAlt, FaListAlt } from "react-icons/fa";
import { v4 as uuidv4 } from 'uuid';

const EssayForm: React.FC<{ essayData?: Essay; onSuccess?: () => void }> = ({ essayData, onSuccess }) => {
  const [form, setForm] = useState<Essay>(essayData || { topic: "", content: "", explanation: "" });
  const [status, setStatus] = useState("");
  const isEdit = !!essayData;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus("Saving...");
    try {
      let res;
      let essayToSend = { ...form };
      if (!isEdit) {
        essayToSend.id = uuidv4();
      }
      if (isEdit) {
        res = await essaysEngine.put(`/essays/${form.id}`, essayToSend);
      } else {
        res = await essaysEngine.post("/essays", essayToSend);
      }
      if (res.status === 200 || res.status === 201) {
        setStatus(isEdit ? "Essay updated!" : "Essay created!");
        if (onSuccess) onSuccess();
      } else {
        setStatus("Error saving essay.");
      }
    } catch (e) {
      setStatus("Error saving essay.");
    }
  };

  return (
    <form
      className="flex flex-col gap-4 w-full max-w-xl mx-auto p-0 form-dot-scrollbar overflow-y-auto"
      id="modal-form"
      onSubmit={handleSubmit}
    >
      <label className="flex items-center gap-2 text-cyan-700 font-bold">
        <FaPen /> Topic
      </label>
      <input
        type="text"
        value={form.topic}
        onChange={e => setForm({ ...form, topic: e.target.value })}
        className="w-full rounded-2xl border-2 border-cyan-200 focus:border-green-400 focus:ring-2 focus:ring-green-200 px-4 py-3 text-lg transition-all duration-200 bg-cyan-50 dark:bg-cyan-900 placeholder:text-cyan-400 focus:bg-white dark:focus:bg-boxdark"
        placeholder="Essay topic"
      />
      <label className="flex items-center gap-2 text-blue-700 font-bold">
        <FaFileAlt /> Content
      </label>
      <textarea
        value={form.content}
        onChange={e => setForm({ ...form, content: e.target.value })}
        className="w-full rounded-2xl border-2 border-blue-200 focus:border-yellow-400 focus:ring-2 focus:ring-yellow-200 px-4 py-3 text-lg transition-all duration-200 bg-blue-50 dark:bg-blue-900 placeholder:text-blue-400 focus:bg-white dark:focus:bg-boxdark resize-y min-h-[48px] max-h-[320px]"
        placeholder="Essay content"
        rows={3}
      />
      <label className="flex items-center gap-2 text-green-700 font-bold">
        <FaListAlt /> Explanation
      </label>
      <textarea
        value={form.explanation}
        onChange={e => setForm({ ...form, explanation: e.target.value })}
        className="w-full rounded-2xl border-2 border-green-200 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-200 px-4 py-3 text-lg transition-all duration-200 bg-green-50 dark:bg-green-900 placeholder:text-green-400 focus:bg-white dark:focus:bg-boxdark resize-y min-h-[48px] max-h-[320px]"
        placeholder="Essay explanation (optional)"
        rows={2}
      />
      {status && <p className="mt-2 text-center text-sm text-gray-700 dark:text-gray-300">{status}</p>}
    </form>
  );
};

export default EssayForm;
