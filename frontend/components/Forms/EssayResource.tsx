import { useState } from "react";
import { FaLink, FaFileAlt, FaHashtag } from "react-icons/fa";

interface Resource {
  id?: string;
  url: string;
  content: string;
  essay_id: string;
}

const EssayResourceForm: React.FC<{ resourceData?: Resource; onSuccess?: () => void }> = ({ resourceData, onSuccess }) => {
  const [form, setForm] = useState<Resource>(resourceData || { url: "", content: "", essay_id: "" });
  const [status, setStatus] = useState("");
  const isEdit = !!resourceData;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus("Saving...");
    // TODO: Implement API call for resource
    setTimeout(() => {
      setStatus(isEdit ? "Resource updated!" : "Resource created!");
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
        <FaHashtag /> Essay ID
      </label>
      <input
        type="text"
        value={form.essay_id}
        onChange={e => setForm({ ...form, essay_id: e.target.value })}
        className="w-full rounded-2xl border-2 border-cyan-200 focus:border-green-400 focus:ring-2 focus:ring-green-200 px-4 py-3 text-lg transition-all duration-200 bg-cyan-50 dark:bg-cyan-900 placeholder:text-cyan-400 focus:bg-white dark:focus:bg-boxdark"
        placeholder="Essay ID"
      />
      <label className="flex items-center gap-2 text-green-700 font-bold">
        <FaLink /> URL
      </label>
      <input
        type="text"
        value={form.url}
        onChange={e => setForm({ ...form, url: e.target.value })}
        className="w-full rounded-2xl border-2 border-green-200 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-200 px-4 py-3 text-lg transition-all duration-200 bg-green-50 dark:bg-green-900 placeholder:text-green-400 focus:bg-white dark:focus:bg-boxdark"
        placeholder="Resource URL"
      />
      <label className="flex items-center gap-2 text-blue-700 font-bold">
        <FaFileAlt /> Content
      </label>
      <textarea
        value={form.content}
        onChange={e => setForm({ ...form, content: e.target.value })}
        className="w-full rounded-2xl border-2 border-blue-200 focus:border-yellow-400 focus:ring-2 focus:ring-yellow-200 px-4 py-3 text-lg transition-all duration-200 bg-blue-50 dark:bg-blue-900 placeholder:text-blue-400 focus:bg-white dark:focus:bg-boxdark resize-y min-h-[48px] max-h-[320px]"
        placeholder="Resource content"
        rows={3}
      />
      {status && <p className="mt-2 text-center text-sm text-gray-700 dark:text-gray-300">{status}</p>}
    </form>
  );
};

export default EssayResourceForm;
