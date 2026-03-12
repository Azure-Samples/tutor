import { useState } from "react";
import { FaHashtag, FaRobot, FaRulerHorizontal } from "react-icons/fa";

import type { Grader } from "@/types/grader";
import { questionsEngine } from "@/utils/api";

const GraderForm: React.FC<{ graderData?: Grader; onSuccess?: () => void }> = ({ graderData, onSuccess }) => {
  const [form, setForm] = useState<Grader>(graderData || { agent_id: "", dimension: "", deployment: "" });
  const [status, setStatus] = useState("");
  const isEdit = !!graderData;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus("Saving...");
    try {
      const graderId = (graderData?.agent_id || form.agent_id || "").trim();
      if (!graderId) {
        setStatus("Agent ID is required.");
        return;
      }

      const payload: Grader = {
        agent_id: graderId,
        dimension: form.dimension,
        deployment: form.deployment,
      };

      const res = isEdit
        ? await questionsEngine.put(`/graders/${encodeURIComponent(graderId)}`, payload)
        : await questionsEngine.post("/graders", payload);

      if (res.status === 200 || res.status === 201) {
        setStatus(isEdit ? "Grader updated!" : "Grader created!");
        if (onSuccess) {
          onSuccess();
        }
        if (!isEdit) {
          setForm({ agent_id: "", dimension: "", deployment: "" });
        }
      } else {
        setStatus("Error saving grader.");
      }
    } catch {
      setStatus("Error saving grader.");
    }
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
        value={form.agent_id}
        onChange={e => setForm({ ...form, agent_id: e.target.value })}
        disabled={isEdit}
        className="w-full rounded-2xl border-2 border-cyan-200 focus:border-green-400 focus:ring-2 focus:ring-green-200 px-4 py-3 text-lg transition-all duration-200 bg-cyan-50 dark:bg-cyan-900 placeholder:text-cyan-400 focus:bg-white dark:focus:bg-boxdark"
        placeholder="Azure AI Foundry agent ID"
      />
      <label className="flex items-center gap-2 text-green-700 font-bold">
        <FaRulerHorizontal /> Dimension
      </label>
      <input
        type="text"
        value={form.dimension}
        onChange={e => setForm({ ...form, dimension: e.target.value })}
        className="w-full rounded-2xl border-2 border-green-200 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-200 px-4 py-3 text-lg transition-all duration-200 bg-green-50 dark:bg-green-900 placeholder:text-green-400 focus:bg-white dark:focus:bg-boxdark"
        placeholder="Evaluation dimension (e.g. clarity, correctness)"
      />
      <label className="flex items-center gap-2 text-blue-700 font-bold">
        <FaRobot /> Deployment
      </label>
      <input
        type="text"
        value={form.deployment}
        onChange={e => setForm({ ...form, deployment: e.target.value })}
        className="w-full rounded-2xl border-2 border-blue-200 focus:border-yellow-400 focus:ring-2 focus:ring-yellow-200 px-4 py-3 text-lg transition-all duration-200 bg-blue-50 dark:bg-blue-900 placeholder:text-blue-400 focus:bg-white dark:focus:bg-boxdark"
        placeholder="Model deployment name"
      />
      {status && <p className="mt-2 text-center text-sm text-gray-700 dark:text-gray-300">{status}</p>}
    </form>
  );
};

export default GraderForm;
