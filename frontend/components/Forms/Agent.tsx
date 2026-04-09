import { useMemo, useState } from "react";
import { FaInfoCircle, FaRobot, FaTemperatureLow, FaTerminal, FaUserTag } from "react-icons/fa";

import type { AgentDefinition, AgentRef } from "@/types/essays";
import { essaysEngine } from "@/utils/api";

interface AgentFormProps {
  onSuccess?: (agent: AgentRef) => void;
}

const ROLE_OPTIONS = ["default", "analytical", "narrative"] as const;

const defaultAgent: AgentDefinition = {
  name: "",
  instructions: "",
  deployment: "",
  role: "default",
  temperature: undefined,
};

const AgentForm: React.FC<AgentFormProps> = ({ onSuccess }) => {
  const [form, setForm] = useState<AgentDefinition>(defaultAgent);
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const temperatureValue = useMemo(() => {
    if (form.temperature === undefined || form.temperature === null) {
      return "";
    }
    return String(form.temperature);
  }, [form.temperature]);

  const updateField = <K extends keyof AgentDefinition>(key: K, value: AgentDefinition[K]) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setSubmitting(true);
    setStatus(null);
    setError(null);
    try {
      const response = await essaysEngine.post<AgentRef>("/agents", form);
      setStatus(`Agent provisioned with id ${response.data.agent_id}`);
      if (onSuccess) {
        onSuccess(response.data);
      }
      setForm(defaultAgent);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Failed to provision agent.";
      setError(message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form
      id="modal-form"
      className="flex flex-col gap-4 w-full max-w-xl mx-auto p-0 form-dot-scrollbar overflow-y-auto"
      onSubmit={handleSubmit}
    >
      <label htmlFor="agent-name" className="flex items-center gap-2 text-cyan-700 font-bold">
        <FaRobot /> Agent Name
      </label>
      <input
        id="agent-name"
        type="text"
        value={form.name}
        onChange={(event) => updateField("name", event.target.value)}
        className="w-full rounded-2xl border-2 border-cyan-200 focus:border-green-400 focus:ring-2 focus:ring-green-200 px-4 py-3 text-lg transition-all duration-200 bg-cyan-50 dark:bg-cyan-900 placeholder:text-cyan-400 focus:bg-white dark:focus:bg-boxdark"
        placeholder="Friendly agent name"
        required
      />

      <label
        htmlFor="agent-instructions"
        className="flex items-center gap-2 text-blue-700 font-bold"
      >
        <FaInfoCircle /> Instructions
      </label>
      <textarea
        id="agent-instructions"
        value={form.instructions}
        onChange={(event) => updateField("instructions", event.target.value)}
        className="w-full rounded-2xl border-2 border-blue-200 focus:border-yellow-400 focus:ring-2 focus:ring-yellow-200 px-4 py-3 text-lg transition-all duration-200 bg-blue-50 dark:bg-blue-900 placeholder:text-blue-400 focus:bg-white dark:focus:bg-boxdark resize-y min-h-[96px] max-h-[320px]"
        placeholder="System instructions for the agent"
        required
      />

      <label
        htmlFor="agent-deployment"
        className="flex items-center gap-2 text-green-700 font-bold"
      >
        <FaTerminal /> Deployment Name
      </label>
      <input
        id="agent-deployment"
        type="text"
        value={form.deployment}
        onChange={(event) => updateField("deployment", event.target.value)}
        className="w-full rounded-2xl border-2 border-green-200 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-200 px-4 py-3 text-lg transition-all duration-200 bg-green-50 dark:bg-green-900 placeholder:text-green-400 focus:bg-white dark:focus:bg-boxdark"
        placeholder="Azure AI Foundry deployment name"
        required
      />

      <label htmlFor="agent-role" className="flex items-center gap-2 text-orange-700 font-bold">
        <FaUserTag /> Role
      </label>
      <select
        id="agent-role"
        value={form.role}
        onChange={(event) => updateField("role", event.target.value)}
        className="w-full rounded-2xl border-2 border-orange-200 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-200 px-4 py-3 text-lg transition-all duration-200 bg-orange-50 dark:bg-orange-900 focus:bg-white dark:focus:bg-boxdark"
        required
      >
        {ROLE_OPTIONS.map((r) => (
          <option key={r} value={r}>
            {r.charAt(0).toUpperCase() + r.slice(1)}
          </option>
        ))}
      </select>

      <label
        htmlFor="agent-temperature"
        className="flex items-center gap-2 text-purple-700 font-bold"
      >
        <FaTemperatureLow /> Temperature (optional)
      </label>
      <input
        id="agent-temperature"
        type="number"
        min="0"
        max="2"
        step="0.1"
        value={temperatureValue}
        onChange={(event) => {
          const value = event.target.value;
          updateField("temperature", value === "" ? undefined : Number(value));
        }}
        className="w-full rounded-2xl border-2 border-purple-200 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-200 px-4 py-3 text-lg transition-all duration-200 bg-purple-50 dark:bg-purple-900 placeholder:text-purple-400 focus:bg-white dark:focus:bg-boxdark"
        placeholder="Leave blank to use the deployment default"
      />

      {status && (
        <p className="mt-2 text-center text-sm text-green-700 dark:text-green-300">{status}</p>
      )}
      {error && <p className="mt-2 text-center text-sm text-red-600 dark:text-red-300">{error}</p>}
      {submitting && (
        <p className="mt-2 text-center text-sm text-cyan-700 dark:text-cyan-300">
          Provisioning agent...
        </p>
      )}
    </form>
  );
};

export default AgentForm;
