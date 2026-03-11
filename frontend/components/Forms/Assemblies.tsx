import { useState } from "react";
import { essaysEngine, questionsEngine } from "@/utils/api";
import { FaRobot, FaTag, FaBook, FaListOl, FaPlus, FaTimes, FaPen, FaUserTag } from "react-icons/fa";

type AgentField = {
  agent_id?: string;
  name: string;
  instructions: string;
  deployment: string;
  role?: string;
  temperature?: number;
  dimension?: string;
};

type UnifiedAssembly = {
  id: string;
  topic_name: string;
  service: "essays" | "questions";
  essay_id?: string;
  agents: AgentField[];
};

const DEPLOYMENT_OPTIONS = ["gpt-5-nano", "gpt-5"];
const ROLE_OPTIONS = ["default", "analytical", "narrative"] as const;

const AssemblyForm: React.FC<{ assemblyData?: UnifiedAssembly; onSuccess?: () => void }> = ({ assemblyData, onSuccess }) => {
  const [form, setForm] = useState<UnifiedAssembly>(
    assemblyData || { id: "", topic_name: "", service: "questions", essay_id: "", agents: [] }
  );
  const [status, setStatus] = useState("");
  const isEdit = !!assemblyData;

  const handleAgentChange = (index: number, field: keyof AgentField, value: string | number) => {
    const updated = form.agents.map((a, i) => (i === index ? { ...a, [field]: value } : a));
    setForm({ ...form, agents: updated });
  };

  const addAgent = () => {
    const newAgent: AgentField = form.service === "essays"
      ? { name: "", instructions: "", deployment: "gpt-5-nano", role: "default", temperature: 0.7 }
      : { name: "", instructions: "", deployment: "gpt-5-nano", dimension: "" };
    setForm({ ...form, agents: [...form.agents, newAgent] });
  };

  const removeAgent = (index: number) => {
    setForm({ ...form, agents: form.agents.filter((_, i) => i !== index) });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus("Saving...");
    try {
      const trimmedId = form.id?.trim();
      const assemblyId = isEdit
        ? (trimmedId || assemblyData?.id || "")
        : (trimmedId || (typeof crypto !== "undefined" && "randomUUID" in crypto ? crypto.randomUUID() : `asm-${Date.now()}`));

      if (isEdit && !assemblyId) {
        throw new Error("Missing assembly id for update.");
      }

      const agents = form.agents.map((a) => ({
        ...(a.agent_id ? { agent_id: a.agent_id } : {}),
        name: a.name,
        instructions: a.instructions,
        deployment: a.deployment,
        ...(form.service === "essays"
          ? { role: a.role ?? "default", temperature: a.temperature }
          : { dimension: a.dimension ?? "" }),
      }));

      let res;
      if (form.service === "essays") {
        const payload = { id: assemblyId, topic_name: form.topic_name, essay_id: form.essay_id || "", agents };
        res = isEdit
          ? await essaysEngine.put(`/assemblies/${assemblyId}`, payload)
          : await essaysEngine.post("/assemblies", payload);
      } else {
        const payload = { id: assemblyId, topic_name: form.topic_name, agents };
        if (isEdit) {
          res = await questionsEngine.put(`/assemblies/${assemblyId}`, payload);
        } else {
          res = await questionsEngine.post("/assemblies", payload);
        }
      }

      if (res.status === 200 || res.status === 201) {
        setStatus(isEdit ? "Assembly updated!" : "Assembly created!");
        if (onSuccess) onSuccess();
        if (!isEdit) setForm({ id: "", topic_name: "", service: "questions", essay_id: "", agents: [] });
      } else {
        setStatus("Error saving assembly.");
      }
    } catch {
      setStatus("Error saving assembly.");
    }
  };

  return (
    <form
      className="flex flex-col gap-4 w-full max-w-xl mx-auto p-0 form-dot-scrollbar overflow-y-auto"
      id="modal-form"
      onSubmit={handleSubmit}
    >
      <label className="flex items-center gap-2 text-cyan-700 font-bold">
        <FaRobot /> Service
      </label>
      <select
        value={form.service}
        onChange={(e) => setForm({ ...form, service: e.target.value as "essays" | "questions" })}
        disabled={isEdit}
        className="w-full rounded-2xl border-2 border-cyan-200 focus:border-green-400 focus:ring-2 focus:ring-green-200 px-4 py-3 text-lg transition-all duration-200 bg-cyan-50 dark:bg-cyan-900 focus:bg-white dark:focus:bg-boxdark"
      >
        <option value="questions">Questions</option>
        <option value="essays">Essays</option>
      </select>

      <label className="flex items-center gap-2 text-green-700 font-bold">
        <FaTag /> Topic Name
      </label>
      <input
        type="text"
        value={form.topic_name}
        onChange={(e) => setForm({ ...form, topic_name: e.target.value })}
        className="w-full rounded-2xl border-2 border-green-200 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-200 px-4 py-3 text-lg transition-all duration-200 bg-green-50 dark:bg-green-900 placeholder:text-green-400 focus:bg-white dark:focus:bg-boxdark"
        placeholder="Assembly topic name"
      />

      {form.service === "essays" && (
        <>
          <label className="flex items-center gap-2 text-blue-700 font-bold">
            <FaBook /> Essay ID
          </label>
          <input
            type="text"
            value={form.essay_id || ""}
            onChange={(e) => setForm({ ...form, essay_id: e.target.value })}
            className="w-full rounded-2xl border-2 border-blue-200 focus:border-yellow-400 focus:ring-2 focus:ring-yellow-200 px-4 py-3 text-lg transition-all duration-200 bg-blue-50 dark:bg-blue-900 placeholder:text-blue-400 focus:bg-white dark:focus:bg-boxdark"
            placeholder="Associated essay ID"
          />
        </>
      )}

      <label className="flex items-center gap-2 text-purple-700 font-bold">
        <FaListOl /> Agents
      </label>
      {form.agents.map((agent, index) => (
        <div key={index} className="flex flex-col gap-2 rounded-2xl border-2 border-purple-200 dark:border-purple-800 bg-purple-50 dark:bg-purple-900 p-4">
          <div className="flex items-center justify-between">
            <span className="font-bold text-purple-700 dark:text-purple-200 text-sm">Agent {index + 1}</span>
            <button
              type="button"
              onClick={() => removeAgent(index)}
              className="bg-gradient-to-br from-red-400 to-orange-400 text-white rounded-full p-2 shadow hover:scale-110 transition-all duration-200"
              title="Remove agent"
            >
              <FaTimes />
            </button>
          </div>
          <input
            type="text"
            value={agent.name}
            onChange={(e) => handleAgentChange(index, "name", e.target.value)}
            className="w-full rounded-2xl border-2 border-purple-200 focus:border-blue-400 focus:ring-2 focus:ring-blue-200 px-4 py-2 text-base transition-all duration-200 bg-white dark:bg-boxdark placeholder:text-purple-400"
            placeholder="Agent name"
          />
          <select
            value={agent.deployment}
            onChange={(e) => handleAgentChange(index, "deployment", e.target.value)}
            className="w-full rounded-2xl border-2 border-purple-200 focus:border-blue-400 focus:ring-2 focus:ring-blue-200 px-4 py-2 text-base transition-all duration-200 bg-white dark:bg-boxdark"
          >
            {DEPLOYMENT_OPTIONS.map((d) => (
              <option key={d} value={d}>{d}</option>
            ))}
          </select>
          <input
            type="number"
            value={agent.temperature ?? 0.7}
            onChange={(e) => handleAgentChange(index, "temperature", parseFloat(e.target.value))}
            step={0.1}
            min={0}
            max={2}
            className="w-full rounded-2xl border-2 border-purple-200 focus:border-blue-400 focus:ring-2 focus:ring-blue-200 px-4 py-2 text-base transition-all duration-200 bg-white dark:bg-boxdark placeholder:text-purple-400"
            placeholder="Temperature (0-2)"
          />
          {form.service === "essays" ? (
            <select
              value={agent.role ?? "default"}
              onChange={(e) => handleAgentChange(index, "role", e.target.value)}
              className="w-full rounded-2xl border-2 border-purple-200 focus:border-blue-400 focus:ring-2 focus:ring-blue-200 px-4 py-2 text-base transition-all duration-200 bg-white dark:bg-boxdark"
            >
              {ROLE_OPTIONS.map((r) => (
                <option key={r} value={r}>{r.charAt(0).toUpperCase() + r.slice(1)}</option>
              ))}
            </select>
          ) : (
            <input
              type="text"
              value={agent.dimension ?? ""}
              onChange={(e) => handleAgentChange(index, "dimension", e.target.value)}
              className="w-full rounded-2xl border-2 border-purple-200 focus:border-blue-400 focus:ring-2 focus:ring-blue-200 px-4 py-2 text-base transition-all duration-200 bg-white dark:bg-boxdark placeholder:text-purple-400"
              placeholder="Grading dimension"
            />
          )}
          <textarea
            value={agent.instructions}
            onChange={(e) => handleAgentChange(index, "instructions", e.target.value)}
            className="w-full rounded-2xl border-2 border-purple-200 focus:border-blue-400 focus:ring-2 focus:ring-blue-200 px-4 py-2 text-base transition-all duration-200 bg-white dark:bg-boxdark placeholder:text-purple-400 resize-y min-h-[48px] max-h-[160px]"
            placeholder="Agent instructions"
            rows={2}
          />
        </div>
      ))}
      <button
        type="button"
        onClick={addAgent}
        className="flex items-center gap-2 self-start px-4 py-2 bg-gradient-to-br from-green-400 to-emerald-500 text-white font-bold rounded-2xl shadow hover:scale-105 transition-all duration-200"
      >
        <FaPlus /> Add Agent
      </button>

      <button
        type="submit"
        className="mt-4 px-4 py-3 bg-gradient-to-br from-green-400 to-cyan-400 hover:from-cyan-400 hover:to-yellow-300 text-white font-bold rounded-2xl shadow-lg w-full flex items-center justify-center gap-2 text-lg transition-all duration-200"
      >
        {isEdit ? <FaPen /> : <FaPlus />} {isEdit ? "Update Assembly" : "Create Assembly"}
      </button>
      {status && <p className="mt-2 text-center text-sm text-gray-700 dark:text-gray-300">{status}</p>}
    </form>
  );
};

export default AssemblyForm;
