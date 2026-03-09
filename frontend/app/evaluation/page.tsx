"use client";

import { useState } from "react";

import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import DefaultLayout from "@/components/Layouts/DefaultLayout";
import { evaluationApi } from "@/utils/api";

const EvaluationPage = () => {
  const [datasetId, setDatasetId] = useState("dataset-showcase-1");
  const [datasetName, setDatasetName] = useState("Showcase Dataset");
  const [agentId, setAgentId] = useState("agent-showcase");
  const [runId, setRunId] = useState("");
  const [status, setStatus] = useState("");
  const [result, setResult] = useState<any>(null);

  const createDataset = async () => {
    try {
      setStatus("Creating dataset...");
      const payload = {
        dataset_id: datasetId,
        name: datasetName,
        items: [{ prompt: "Explain acceleration.", expected: "Change in velocity over time." }],
      };
      const { data } = await evaluationApi.post("/datasets", payload);
      setResult(data);
      setStatus("Dataset created.");
    } catch (err: any) {
      setStatus(err?.message || "Failed to create dataset.");
    }
  };

  const startRun = async () => {
    try {
      setStatus("Starting evaluation run...");
      const { data } = await evaluationApi.post("/evaluation/run", { agent_id: agentId, dataset_id: datasetId });
      setRunId(data?.run_id || "");
      setResult(data);
      setStatus("Evaluation run queued.");
    } catch (err: any) {
      setStatus(err?.message || "Failed to start evaluation run.");
    }
  };

  const loadRun = async () => {
    if (!runId) {
      setStatus("Run id is required.");
      return;
    }
    try {
      setStatus("Loading run status...");
      const { data } = await evaluationApi.get(`/evaluation/run/${runId}`);
      setResult(data);
      setStatus("Run status loaded.");
    } catch (err: any) {
      setStatus(err?.message || "Failed to load run status.");
    }
  };

  return (
    <DefaultLayout>
      <Breadcrumb pageName="Evaluation" subtitle="Run agent quality checks through the APIM-exposed evaluation service." />
      <div className="mx-auto max-w-4xl space-y-4 rounded-2xl bg-white p-6 shadow dark:bg-boxdark">
        <div className="grid gap-4 md:grid-cols-2">
          <input className="rounded border px-3 py-2" value={datasetId} onChange={(e) => setDatasetId(e.target.value)} placeholder="dataset_id" />
          <input className="rounded border px-3 py-2" value={datasetName} onChange={(e) => setDatasetName(e.target.value)} placeholder="dataset name" />
          <input className="rounded border px-3 py-2" value={agentId} onChange={(e) => setAgentId(e.target.value)} placeholder="agent_id" />
          <input className="rounded border px-3 py-2" value={runId} onChange={(e) => setRunId(e.target.value)} placeholder="run_id" />
        </div>

        <div className="flex flex-wrap gap-2">
          <button className="rounded bg-cyan-600 px-4 py-2 text-white hover:bg-cyan-700" onClick={createDataset}>Create Dataset</button>
          <button className="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700" onClick={startRun}>Start Run</button>
          <button className="rounded bg-emerald-600 px-4 py-2 text-white hover:bg-emerald-700" onClick={loadRun}>Load Run</button>
        </div>

        {status && <p className="text-sm text-gray-700 dark:text-gray-200">{status}</p>}
        {result && (
          <div className="rounded border p-4">
            <pre className="overflow-auto whitespace-pre-wrap text-sm">{JSON.stringify(result, null, 2)}</pre>
          </div>
        )}
      </div>
    </DefaultLayout>
  );
};

export default EvaluationPage;
