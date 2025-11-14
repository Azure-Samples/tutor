import { useEffect, useMemo, useState } from "react";
import { FaPen, FaFileAlt, FaListAlt, FaBell, FaHashtag, FaUsersCog, FaLink } from "react-icons/fa";
import { v4 as uuidv4 } from "uuid";

import type { AgentDefinition, Essay, ProvisionedAgent, SwarmDefinition } from "@/types/essays";
import { unwrapContent } from "@/types/api";
import { essaysEngine } from "@/utils/api";

const DEFAULT_ESSAY: Essay = {
  topic: "",
  content: "",
  explanation: "",
  theme: "",
  assembly_id: null,
};

type EssayFormProps = {
  essayData?: Essay;
  onSuccess?: () => void;
};

const EssayForm: React.FC<EssayFormProps> = ({ essayData, onSuccess }) => {
  const [form, setForm] = useState<Essay>(essayData ? { ...DEFAULT_ESSAY, ...essayData } : DEFAULT_ESSAY);
  const [status, setStatus] = useState<string>("");
  const isEdit = Boolean(essayData);

  const [availableAgents, setAvailableAgents] = useState<ProvisionedAgent[]>([]);
  const [loadingAgents, setLoadingAgents] = useState<boolean>(false);
  const [agentsError, setAgentsError] = useState<string | null>(null);

  const [assemblyId, setAssemblyId] = useState<string>(essayData?.assembly_id ?? "");
  const [existingAssemblyId, setExistingAssemblyId] = useState<string | null>(null);
  const [assemblyTopic, setAssemblyTopic] = useState<string>(essayData?.topic ?? "");
  const [assemblyTopicTouched, setAssemblyTopicTouched] = useState<boolean>(false);
  const [selectedAgents, setSelectedAgents] = useState<string[]>([]);
  const [assemblyStatus, setAssemblyStatus] = useState<string | null>(null);
  const [assemblyError, setAssemblyError] = useState<string | null>(null);
  const [loadingAssembly, setLoadingAssembly] = useState<boolean>(false);
  const [existingAssemblyAgents, setExistingAssemblyAgents] = useState<AgentDefinition[]>([]);

  const agentsById = useMemo(() => {
    const lookup = new Map<string, ProvisionedAgent>();
    for (const agent of availableAgents) {
      lookup.set(agent.id, agent);
    }
    return lookup;
  }, [availableAgents]);

  useEffect(() => {
    if (essayData) {
      setForm({ ...DEFAULT_ESSAY, ...essayData });
      setAssemblyId(essayData.assembly_id ?? "");
      setAssemblyTopic(essayData.topic ?? "");
      setExistingAssemblyId(essayData.assembly_id ?? null);
    } else {
      setForm(DEFAULT_ESSAY);
      setAssemblyId("");
      setAssemblyTopic("");
      setExistingAssemblyId(null);
    }
    setSelectedAgents([]);
    setExistingAssemblyAgents([]);
    setAssemblyTopicTouched(false);
    setAssemblyStatus(null);
    setAssemblyError(null);
    setStatus("");
  }, [essayData]);

  useEffect(() => {
    const fetchAgents = async () => {
      setLoadingAgents(true);
      setAgentsError(null);
      try {
        const res = await essaysEngine.get("/agents");
        const items = unwrapContent<ProvisionedAgent[]>(res.data) || [];
        setAvailableAgents(items);
      } catch (error) {
        console.error("Failed to load agents", error);
        setAgentsError("Could not load agents from Azure AI Foundry.");
      } finally {
        setLoadingAgents(false);
      }
    };

    fetchAgents().catch(() => undefined);
  }, []);

  useEffect(() => {
    if (!essayData?.id) {
      return;
    }
    const loadAssembly = async (essayId: string) => {
      setLoadingAssembly(true);
      setAssemblyError(null);
      try {
        const res = await essaysEngine.get("/assemblies", { params: { essay_id: essayId } });
        const assemblies = unwrapContent<SwarmDefinition[]>(res.data) || [];
        if (assemblies.length === 0) {
          setExistingAssemblyId(null);
          setSelectedAgents([]);
          setExistingAssemblyAgents([]);
          setAssemblyId(essayData.assembly_id ?? "");
          return;
        }
        const assembly = assemblies[0];
        setExistingAssemblyId(assembly.id);
        setAssemblyId(assembly.id);
        setAssemblyTopic(assembly.topic_name);
        setSelectedAgents(assembly.agents.map((agent) => agent.id ?? "").filter(Boolean));
        setExistingAssemblyAgents(assembly.agents);
        setForm((prev) => ({ ...prev, assembly_id: assembly.id }));
      } catch (error) {
        console.error("Failed to load assembly", error);
        setAssemblyError("Could not load the assembly associated with this essay.");
      } finally {
        setLoadingAssembly(false);
      }
    };

    loadAssembly(essayData.id).catch(() => undefined);
  }, [essayData?.id]);

  useEffect(() => {
    if (!assemblyTopicTouched && !isEdit) {
      setAssemblyTopic(form.topic);
    }
  }, [form.topic, assemblyTopicTouched, isEdit]);

  const toggleAgentSelection = (agentId: string) => {
    setSelectedAgents((prev) =>
      prev.includes(agentId) ? prev.filter((id) => id !== agentId) : [...prev, agentId]
    );
  };

  const persistAssembly = async (essayId: string): Promise<boolean> => {
    const trimmedAssemblyId = (assemblyId || essayId).trim();

    if (existingAssemblyId && existingAssemblyId !== trimmedAssemblyId) {
      setAssemblyError("Assembly ID cannot be changed. Delete the existing assembly first.");
      return false;
    }

    const agentDefinitions: AgentDefinition[] = selectedAgents
      .map((agentId) => agentsById.get(agentId) ?? existingAssemblyAgents.find((agent) => agent.id === agentId))
      .filter(Boolean)
      .map((agent) => ({
        id: agent!.id,
        name: agent!.name,
        instructions: agent!.instructions,
        deployment: agent!.deployment,
        temperature: agent!.temperature ?? undefined,
      }));

    if (agentDefinitions.length === 0) {
      setAssemblyError("Select at least one agent to build the assembly.");
      return false;
    }

    const payload: SwarmDefinition = {
      id: trimmedAssemblyId,
      topic_name: assemblyTopic.trim() || form.topic,
      essay_id: essayId,
      agents: agentDefinitions,
    };

    try {
      setAssemblyStatus("Saving assembly...");
      setAssemblyError(null);
      if (existingAssemblyId) {
        await essaysEngine.put(`/assemblies/${existingAssemblyId}`, payload);
      } else {
        await essaysEngine.post("/assemblies", payload);
      }
      setExistingAssemblyId(trimmedAssemblyId);
      setAssemblyId(trimmedAssemblyId);
      setExistingAssemblyAgents(agentDefinitions);
      setForm((prev) => ({ ...prev, assembly_id: trimmedAssemblyId }));
      setAssemblyStatus("Assembly saved!");
      return true;
    } catch (error) {
      console.error("Failed to persist assembly", error);
      setAssemblyError("Could not save the assembly. Please try again.");
      setAssemblyStatus(null);
      return false;
    }
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setStatus("Saving essay...");
    setAssemblyStatus(null);
    setAssemblyError(null);

    try {
      const essayPayload: Essay = { ...form };
      if (!isEdit) {
        essayPayload.id = essayPayload.id ?? uuidv4();
      }

      const request = isEdit
        ? essaysEngine.put(`/essays/${essayPayload.id}`, essayPayload)
        : essaysEngine.post("/essays", essayPayload);

      const response = await request;
      if (response.status !== 200 && response.status !== 201) {
        setStatus("Error saving essay.");
        return;
      }

      const payload = unwrapContent<Essay>(response.data) || essayPayload;
      const essayId = payload.id ?? essayPayload.id;
      if (!essayId) {
        setStatus("Essay saved, but no identifier was returned.");
        return;
      }

      setForm(payload);

      let assemblySaved = true;
      if (selectedAgents.length > 0 || existingAssemblyId) {
        assemblySaved = await persistAssembly(essayId);
      }

      if (assemblySaved) {
        setStatus(isEdit ? "Essay updated!" : "Essay created!");
        if (!isEdit && !assemblyId) {
          setAssemblyId(essayId);
        }
        if (onSuccess) {
          onSuccess();
        }
      } else {
        setStatus("Essay saved. Please resolve assembly configuration errors.");
      }
    } catch (error) {
      console.error("Error saving essay", error);
      setStatus("Error saving essay.");
    }
  };

  return (
    <form
      className="flex flex-col gap-5 w-full max-w-2xl mx-auto p-0 form-dot-scrollbar overflow-y-auto"
      id="modal-form"
      onSubmit={handleSubmit}
    >
      <div className="flex flex-col gap-2">
        <label className="flex items-center gap-2 text-cyan-700 font-bold">
          <FaPen /> Topic
        </label>
        <input
          type="text"
          value={form.topic}
          onChange={(event) => setForm({ ...form, topic: event.target.value })}
          className="w-full rounded-2xl border-2 border-cyan-200 focus:border-green-400 focus:ring-2 focus:ring-green-200 px-4 py-3 text-lg transition-all duration-200 bg-cyan-50 dark:bg-cyan-900 placeholder:text-cyan-400 focus:bg-white dark:focus:bg-boxdark"
          placeholder="Essay topic"
        />
      </div>

      <div className="flex flex-col gap-2">
        <label className="flex items-center gap-2 text-cyan-700 font-bold">
          <FaBell /> Theme
        </label>
        <input
          type="text"
          value={form.theme ?? ""}
          onChange={(event) => setForm({ ...form, theme: event.target.value })}
          className="w-full rounded-2xl border-2 border-cyan-200 focus:border-green-400 focus:ring-2 focus:ring-green-200 px-4 py-3 text-lg transition-all duration-200 bg-cyan-50 dark:bg-cyan-900 placeholder:text-cyan-400 focus:bg-white dark:focus:bg-boxdark"
          placeholder="Theme that should be considered by the LLM when writing the essay correction (optional)"
        />
      </div>

      <div className="flex flex-col gap-2">
        <label className="flex items-center gap-2 text-blue-700 font-bold">
          <FaFileAlt /> Content
        </label>
        <textarea
          value={form.content}
          onChange={(event) => setForm({ ...form, content: event.target.value })}
          className="w-full rounded-2xl border-2 border-blue-200 focus:border-yellow-400 focus:ring-2 focus:ring-yellow-200 px-4 py-3 text-lg transition-all duration-200 bg-blue-50 dark:bg-blue-900 placeholder:text-blue-400 focus:bg-white dark:focus:bg-boxdark resize-y min-h-[48px] max-h-[320px]"
          placeholder="Content to be presented by the student to write the essay, and by the LLM to correct it"
          rows={3}
        />
      </div>

      <div className="flex flex-col gap-2">
        <label className="flex items-center gap-2 text-green-700 font-bold">
          <FaListAlt /> Explanation
        </label>
        <textarea
          value={form.explanation ?? ""}
          onChange={(event) => setForm({ ...form, explanation: event.target.value })}
          className="w-full rounded-2xl border-2 border-green-200 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-200 px-4 py-3 text-lg transition-all duration-200 bg-green-50 dark:bg-green-900 placeholder:text-green-400 focus:bg-white dark:focus:bg-boxdark resize-y min-h-[48px] max-h-[320px]"
          placeholder="Explanation of the essay correction criteria to be used by the student and the LLM (optional)"
          rows={2}
        />
      </div>

      <div className="rounded-2xl border-2 border-purple-200 bg-purple-50 dark:bg-purple-900/40 px-5 py-5 flex flex-col gap-4">
        <div className="flex items-center gap-2 text-purple-700 font-bold text-lg">
          <FaUsersCog /> Assembly Configuration
        </div>
        <p className="text-sm text-purple-700/80 dark:text-purple-200/80 flex items-center gap-2">
          <FaLink /> Assemblies define which Azure AI Foundry agents evaluate this essay.
        </p>

        <div className="flex flex-col gap-2">
          <label className="flex items-center gap-2 text-purple-700 font-semibold">
            <FaHashtag /> Assembly ID
          </label>
          <input
            type="text"
            value={assemblyId}
            onChange={(event) => setAssemblyId(event.target.value)}
            className="w-full rounded-2xl border-2 border-purple-200 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-200 px-4 py-3 text-base transition-all duration-200 bg-white dark:bg-boxdark"
            placeholder="Defaults to the essay identifier"
            disabled={Boolean(existingAssemblyId)}
          />
          {existingAssemblyId && (
            <p className="text-xs text-purple-600 dark:text-purple-200">
              This essay already has an assembly. Delete it first if you need to change the identifier.
            </p>
          )}
        </div>

        <div className="flex flex-col gap-2">
          <label className="flex items-center gap-2 text-purple-700 font-semibold">
            <FaPen /> Assembly Topic
          </label>
          <input
            type="text"
            value={assemblyTopic}
            onChange={(event) => {
              setAssemblyTopic(event.target.value);
              setAssemblyTopicTouched(true);
            }}
            className="w-full rounded-2xl border-2 border-purple-200 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-200 px-4 py-3 text-base transition-all duration-200 bg-white dark:bg-boxdark"
            placeholder="Topic name that will group the agents"
          />
        </div>

        <div className="flex flex-col gap-3">
          <span className="text-sm font-semibold text-purple-700 flex items-center gap-2">
            <FaUsersCog /> Select agents to include
          </span>
          {loadingAgents ? (
            <p className="text-sm text-purple-600">Loading available agents...</p>
          ) : agentsError ? (
            <p className="text-sm text-red-600">{agentsError}</p>
          ) : availableAgents.length === 0 ? (
            <p className="text-sm text-purple-600">No agents are currently provisioned.</p>
          ) : (
            <div className="grid gap-3 sm:grid-cols-2">
              {availableAgents.map((agent) => (
                <label
                  key={agent.id}
                  className="flex items-start gap-3 rounded-2xl border border-purple-200 bg-white/80 dark:bg-boxdark/80 px-4 py-3 shadow hover:shadow-lg transition-all duration-200 cursor-pointer"
                >
                  <input
                    type="checkbox"
                    checked={selectedAgents.includes(agent.id)}
                    onChange={() => toggleAgentSelection(agent.id)}
                    className="mt-1"
                  />
                  <div className="flex flex-col gap-1 text-sm">
                    <span className="font-semibold text-purple-700 dark:text-purple-200">{agent.name}</span>
                    <span className="text-purple-600/80 dark:text-purple-100/80">{agent.deployment}</span>
                    {agent.instructions && (
                      <span className="text-xs text-purple-500/80 line-clamp-2">{agent.instructions}</span>
                    )}
                  </div>
                </label>
              ))}
            </div>
          )}
        </div>

        {loadingAssembly && <p className="text-sm text-purple-600">Loading existing assembly...</p>}
        {assemblyStatus && <p className="text-sm text-green-600">{assemblyStatus}</p>}
        {assemblyError && <p className="text-sm text-red-600">{assemblyError}</p>}
      </div>

      {status && <p className="mt-2 text-center text-sm text-gray-700 dark:text-gray-300">{status}</p>}
    </form>
  );
};

export default EssayForm;
