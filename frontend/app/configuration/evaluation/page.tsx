"use client";

import { useState } from "react";

import Breadcrumb from "@/components/Breadcrumbs/Breadcrumb";
import DefaultLayout from "@/components/Layouts/DefaultLayout";
import { evaluationApi } from "@/utils/api";

const DATASET_ID_INPUT_ID = "evaluation-dataset-id";
const DATASET_NAME_INPUT_ID = "evaluation-dataset-name";
const AGENT_ID_INPUT_ID = "evaluation-agent-id";
const RUN_ID_INPUT_ID = "evaluation-run-id";

const getErrorMessage = (error: unknown, fallback: string) =>
  error instanceof Error ? error.message : fallback;

const EvaluationConfigPage = () => {
  const [datasetId, setDatasetId] = useState("dataset-showcase-1");
  const [datasetName, setDatasetName] = useState("Showcase Dataset");
  const [agentId, setAgentId] = useState("agent-showcase");
  const [runId, setRunId] = useState("");
  const [status, setStatus] = useState("");
  const [result, setResult] = useState<unknown | null>(null);

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
    } catch (error: unknown) {
      setStatus(getErrorMessage(error, "Failed to create dataset."));
    }
  };

  const startRun = async () => {
    try {
      setStatus("Starting evaluation run...");
      const { data } = await evaluationApi.post("/evaluation/run", {
        agent_id: agentId,
        dataset_id: datasetId,
      });
      setRunId(data?.run_id || "");
      setResult(data);
      setStatus("Evaluation run queued.");
    } catch (error: unknown) {
      setStatus(getErrorMessage(error, "Failed to start evaluation run."));
    }
  };

  const loadRun = async () => {
    if (!runId) {
      setStatus("Run id is required.");
      return;
    }
    try {
      setStatus("Loading run status...");
      const { data } = await evaluationApi.get(`/evaluation/run/${encodeURIComponent(runId)}`);
      setResult(data);
      setStatus("Run status loaded.");
    } catch (error: unknown) {
      setStatus(getErrorMessage(error, "Failed to load run status."));
    }
  };

  return (
    <DefaultLayout>
      <Breadcrumb
        pageName="Evaluation Configuration"
        subtitle="Run agent quality checks through the APIM-exposed evaluation service."
      />
      <div className="mx-auto max-w-4xl space-y-4 rounded-2xl bg-white p-6 shadow dark:bg-boxdark">
        <div className="grid gap-4 md:grid-cols-2">
          <div>
            <label
              className="mb-1 block text-sm font-medium text-black dark:text-white"
              htmlFor={DATASET_ID_INPUT_ID}
            >
              Dataset ID
            </label>
            <input
              id={DATASET_ID_INPUT_ID}
              className="w-full rounded border px-3 py-2"
              value={datasetId}
              onChange={(e) => setDatasetId(e.target.value)}
              placeholder="dataset_id"
            />
          </div>
          <div>
            <label
              className="mb-1 block text-sm font-medium text-black dark:text-white"
              htmlFor={DATASET_NAME_INPUT_ID}
            >
              Dataset name
            </label>
            <input
              id={DATASET_NAME_INPUT_ID}
              className="w-full rounded border px-3 py-2"
              value={datasetName}
              onChange={(e) => setDatasetName(e.target.value)}
              placeholder="dataset name"
            />
          </div>
          <div>
            <label
              className="mb-1 block text-sm font-medium text-black dark:text-white"
              htmlFor={AGENT_ID_INPUT_ID}
            >
              Agent ID
            </label>
            <input
              id={AGENT_ID_INPUT_ID}
              className="w-full rounded border px-3 py-2"
              value={agentId}
              onChange={(e) => setAgentId(e.target.value)}
              placeholder="agent_id"
            />
          </div>
          <div>
            <label
              className="mb-1 block text-sm font-medium text-black dark:text-white"
              htmlFor={RUN_ID_INPUT_ID}
            >
              Run ID
            </label>
            <input
              id={RUN_ID_INPUT_ID}
              className="w-full rounded border px-3 py-2"
              value={runId}
              onChange={(e) => setRunId(e.target.value)}
              placeholder="run_id"
            />
          </div>
        </div>

        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            className="rounded bg-cyan-600 px-4 py-2 text-white hover:bg-cyan-700"
            onClick={createDataset}
          >
            Create Dataset
          </button>
          <button
            type="button"
            className="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
            onClick={startRun}
          >
            Start Run
          </button>
          <button
            type="button"
            className="rounded bg-emerald-600 px-4 py-2 text-white hover:bg-emerald-700"
            onClick={loadRun}
          >
            Load Run
          </button>
        </div>

        {status && <p className="text-sm text-gray-700 dark:text-gray-200">{status}</p>}
        {result !== null && (
          <div className="rounded border p-4">
            <pre className="overflow-auto whitespace-pre-wrap text-sm">
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </DefaultLayout>
  );
};

export default EvaluationConfigPage;
