"use client";

import Link from "next/link";
import { type FormEvent, useCallback, useEffect, useMemo, useState } from "react";

import {
  type EvaluationDataset,
  type EvaluationRun,
  createEvaluationDataset,
  getEvaluationErrorMessage,
  listEvaluationDatasets,
  startEvaluationRun,
} from "@/utils/evaluation";
import {
  ROUTE_CATEGORY_LABELS,
  ROUTE_METADATA,
  ROUTE_STATUS_LABELS,
  type RouteCategory,
  type RouteMetadata,
} from "@/utils/routeMetadata";

const DATASET_ID_INPUT_ID = "evaluation-dashboard-dataset-id";
const DATASET_NAME_INPUT_ID = "evaluation-dashboard-dataset-name";
const DATASET_PROMPT_INPUT_ID = "evaluation-dashboard-dataset-prompt";
const DATASET_EXPECTED_INPUT_ID = "evaluation-dashboard-dataset-expected";
const RUN_DATASET_INPUT_ID = "evaluation-dashboard-run-dataset";
const RUN_AGENT_INPUT_ID = "evaluation-dashboard-run-agent";

const ROUTE_GROUPS: RouteCategory[] = [
  "public",
  "workspace",
  "configuration",
  "adapter",
  "blocked",
  "planned",
];

const getStatusBadgeClassName = (status: RouteMetadata["status"]): string => {
  switch (status) {
    case "implemented":
      return "border-teal-200 bg-teal-50 text-teal-800 dark:border-teal-900 dark:bg-teal-950/40 dark:text-teal-200";
    case "adapter":
      return "border-sky-200 bg-sky-50 text-sky-800 dark:border-sky-900 dark:bg-sky-950/40 dark:text-sky-200";
    case "blocked":
      return "border-amber-200 bg-amber-50 text-amber-900 dark:border-amber-900 dark:bg-amber-950/40 dark:text-amber-100";
    case "planned":
      return "border-slate-200 bg-slate-50 text-slate-700 dark:border-slate-700 dark:bg-slate-950/60 dark:text-slate-200";
  }
};

const EvaluationDashboard = () => {
  const [datasets, setDatasets] = useState<EvaluationDataset[]>([]);
  const [datasetId, setDatasetId] = useState("pilot-evaluation-dataset");
  const [datasetName, setDatasetName] = useState("Pilot Evaluation Dataset");
  const [prompt, setPrompt] = useState("Explain acceleration in one sentence.");
  const [expected, setExpected] = useState("Acceleration is the change in velocity over time.");
  const [selectedDatasetId, setSelectedDatasetId] = useState("");
  const [agentId, setAgentId] = useState("agent-showcase");
  const [activeRun, setActiveRun] = useState<EvaluationRun | null>(null);
  const [statusMessage, setStatusMessage] = useState("Loading evaluation datasets...");
  const [errorMessage, setErrorMessage] = useState("");
  const [isLoadingDatasets, setIsLoadingDatasets] = useState(true);
  const [isCreatingDataset, setIsCreatingDataset] = useState(false);
  const [isStartingRun, setIsStartingRun] = useState(false);

  const routeGroups = useMemo(
    () =>
      ROUTE_GROUPS.map((category) => ({
        category,
        routes: ROUTE_METADATA.filter((route) => route.category === category),
      })).filter((group) => group.routes.length > 0),
    [],
  );

  const loadDatasets = useCallback(async (announce = true) => {
    try {
      setIsLoadingDatasets(true);
      setErrorMessage("");
      const nextDatasets = await listEvaluationDatasets();
      setDatasets(nextDatasets);
      setSelectedDatasetId(
        (currentDatasetId) => currentDatasetId || nextDatasets[0]?.dataset_id || "",
      );

      if (announce) {
        setStatusMessage(
          nextDatasets.length > 0
            ? `Loaded ${nextDatasets.length} evaluation dataset${
                nextDatasets.length === 1 ? "" : "s"
              }.`
            : "No evaluation datasets are available yet.",
        );
      }
    } catch (error: unknown) {
      setDatasets([]);
      setErrorMessage(getEvaluationErrorMessage(error, "Failed to load evaluation datasets."));
      setStatusMessage("Evaluation datasets could not be loaded.");
    } finally {
      setIsLoadingDatasets(false);
    }
  }, []);

  useEffect(() => {
    loadDatasets();
  }, [loadDatasets]);

  const handleCreateDataset = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const normalizedDatasetId = datasetId.trim();
    const normalizedDatasetName = datasetName.trim();
    const normalizedPrompt = prompt.trim();
    const normalizedExpected = expected.trim();

    if (!normalizedDatasetId || !normalizedDatasetName) {
      setErrorMessage("Dataset ID and name are required.");
      setStatusMessage("Dataset creation needs required fields.");
      return;
    }

    if (!normalizedPrompt || !normalizedExpected) {
      setErrorMessage("Prompt and expected answer are required for the first dataset item.");
      setStatusMessage("Dataset creation needs one complete evaluation item.");
      return;
    }

    try {
      setIsCreatingDataset(true);
      setErrorMessage("");
      setStatusMessage("Creating evaluation dataset...");
      const dataset = await createEvaluationDataset({
        dataset_id: normalizedDatasetId,
        name: normalizedDatasetName,
        items: [{ prompt: normalizedPrompt, expected: normalizedExpected }],
      });

      setSelectedDatasetId(dataset.dataset_id);
      await loadDatasets(false);
      setStatusMessage(`Dataset ${dataset.dataset_id} is ready for evaluation runs.`);
    } catch (error: unknown) {
      setErrorMessage(getEvaluationErrorMessage(error, "Failed to create dataset."));
      setStatusMessage("Dataset creation failed.");
    } finally {
      setIsCreatingDataset(false);
    }
  };

  const handleStartRun = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const normalizedAgentId = agentId.trim();
    const normalizedDatasetId = selectedDatasetId.trim();

    if (!normalizedAgentId || !normalizedDatasetId) {
      setErrorMessage("Agent ID and dataset are required to start an evaluation run.");
      setStatusMessage("Evaluation run needs an agent and dataset.");
      return;
    }

    try {
      setIsStartingRun(true);
      setErrorMessage("");
      setStatusMessage("Starting evaluation run...");
      const run = await startEvaluationRun({
        agent_id: normalizedAgentId,
        dataset_id: normalizedDatasetId,
      });
      setActiveRun(run);
      setStatusMessage(`Evaluation run ${run.run_id} is ${run.status}.`);
    } catch (error: unknown) {
      setErrorMessage(getEvaluationErrorMessage(error, "Failed to start evaluation run."));
      setStatusMessage("Evaluation run could not be started.");
    } finally {
      setIsStartingRun(false);
    }
  };

  return (
    <div className="space-y-8">
      <section className="grid gap-4 xl:grid-cols-[minmax(0,1.15fr)_minmax(22rem,0.85fr)]">
        <div className="rounded-lg border border-stone-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-900">
          <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-teal-700 dark:text-teal-300">
                Evaluation operations
              </p>
              <h1 className="mt-3 text-3xl font-semibold text-slate-900 dark:text-slate-50">
                Dataset inventory and run launch
              </h1>
              <p className="mt-3 max-w-3xl text-sm leading-7 text-slate-600 dark:text-slate-300">
                This dashboard uses the APIM-backed evaluation facade to list datasets, create a
                small dataset, start a run, and open the run viewer without falling back to the old
                configuration redirect.
              </p>
            </div>
            <Link
              href="/configuration/evaluation"
              className="inline-flex rounded-md border border-stone-200 bg-white px-4 py-2 text-sm font-semibold text-slate-900 transition hover:bg-stone-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-700 focus-visible:ring-offset-2 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-50 dark:hover:bg-slate-800"
            >
              Open advanced utility
            </Link>
          </div>

          <div className="mt-6 grid gap-4 md:grid-cols-3">
            <div className="rounded-md border border-stone-200 bg-stone-50 p-4 dark:border-slate-700 dark:bg-slate-950/60">
              <p className="text-xs font-medium uppercase tracking-[0.2em] text-slate-500 dark:text-slate-400">
                Datasets
              </p>
              <p className="mt-2 text-2xl font-semibold text-slate-900 dark:text-slate-50">
                {isLoadingDatasets ? "..." : datasets.length}
              </p>
            </div>
            <div className="rounded-md border border-stone-200 bg-stone-50 p-4 dark:border-slate-700 dark:bg-slate-950/60">
              <p className="text-xs font-medium uppercase tracking-[0.2em] text-slate-500 dark:text-slate-400">
                Selected dataset
              </p>
              <p className="mt-2 break-words text-lg font-semibold text-slate-900 dark:text-slate-50">
                {selectedDatasetId || "None selected"}
              </p>
            </div>
            <div className="rounded-md border border-stone-200 bg-stone-50 p-4 dark:border-slate-700 dark:bg-slate-950/60">
              <p className="text-xs font-medium uppercase tracking-[0.2em] text-slate-500 dark:text-slate-400">
                Last run
              </p>
              <p className="mt-2 break-words text-lg font-semibold text-slate-900 dark:text-slate-50">
                {activeRun?.run_id ?? "Not started"}
              </p>
            </div>
          </div>
        </div>

        <aside className="rounded-lg border border-stone-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-900">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-500 dark:text-slate-400">
            Live status
          </p>
          <output
            aria-live="polite"
            className="mt-3 block rounded-md border border-teal-100 bg-teal-50 p-4 text-sm leading-7 text-teal-950 dark:border-teal-900 dark:bg-teal-950/40 dark:text-teal-100"
          >
            {statusMessage}
          </output>
          {errorMessage && (
            <div
              role="alert"
              className="mt-3 rounded-md border border-amber-200 bg-amber-50 p-4 text-sm leading-7 text-amber-950 dark:border-amber-900 dark:bg-amber-950/40 dark:text-amber-100"
            >
              {errorMessage}
            </div>
          )}
          {activeRun && (
            <Link
              href={`/evaluation/${encodeURIComponent(activeRun.run_id)}`}
              className="mt-4 inline-flex rounded-md border border-teal-700 bg-teal-700 px-4 py-2 text-sm font-semibold text-white transition hover:bg-teal-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-700 focus-visible:ring-offset-2"
            >
              View run {activeRun.run_id}
            </Link>
          )}
        </aside>
      </section>

      <section className="grid gap-4 xl:grid-cols-2">
        <form
          className="rounded-lg border border-stone-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-900"
          onSubmit={handleCreateDataset}
        >
          <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-50">
            Create dataset
          </h2>
          <p className="mt-2 text-sm leading-7 text-slate-600 dark:text-slate-300">
            Create a minimal dataset through POST /api/evaluation/datasets for evaluation dry runs.
          </p>
          <div className="mt-5 grid gap-4 md:grid-cols-2">
            <div>
              <label
                htmlFor={DATASET_ID_INPUT_ID}
                className="mb-2 block text-sm font-medium text-slate-900 dark:text-slate-100"
              >
                Dataset ID
              </label>
              <input
                id={DATASET_ID_INPUT_ID}
                value={datasetId}
                onChange={(event) => setDatasetId(event.target.value)}
                className="w-full rounded-md border border-stone-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none transition focus:border-teal-700 focus:ring-2 focus:ring-teal-700/20 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100"
                placeholder="pilot-evaluation-dataset"
              />
            </div>
            <div>
              <label
                htmlFor={DATASET_NAME_INPUT_ID}
                className="mb-2 block text-sm font-medium text-slate-900 dark:text-slate-100"
              >
                Dataset name
              </label>
              <input
                id={DATASET_NAME_INPUT_ID}
                value={datasetName}
                onChange={(event) => setDatasetName(event.target.value)}
                className="w-full rounded-md border border-stone-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none transition focus:border-teal-700 focus:ring-2 focus:ring-teal-700/20 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100"
                placeholder="Pilot Evaluation Dataset"
              />
            </div>
            <div>
              <label
                htmlFor={DATASET_PROMPT_INPUT_ID}
                className="mb-2 block text-sm font-medium text-slate-900 dark:text-slate-100"
              >
                Prompt
              </label>
              <textarea
                id={DATASET_PROMPT_INPUT_ID}
                value={prompt}
                onChange={(event) => setPrompt(event.target.value)}
                className="min-h-28 w-full rounded-md border border-stone-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none transition focus:border-teal-700 focus:ring-2 focus:ring-teal-700/20 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100"
                placeholder="Prompt to evaluate"
              />
            </div>
            <div>
              <label
                htmlFor={DATASET_EXPECTED_INPUT_ID}
                className="mb-2 block text-sm font-medium text-slate-900 dark:text-slate-100"
              >
                Expected answer
              </label>
              <textarea
                id={DATASET_EXPECTED_INPUT_ID}
                value={expected}
                onChange={(event) => setExpected(event.target.value)}
                className="min-h-28 w-full rounded-md border border-stone-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none transition focus:border-teal-700 focus:ring-2 focus:ring-teal-700/20 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100"
                placeholder="Expected answer"
              />
            </div>
          </div>
          <button
            type="submit"
            disabled={isCreatingDataset}
            className="mt-5 rounded-md border border-teal-700 bg-teal-700 px-4 py-2 text-sm font-semibold text-white transition hover:bg-teal-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-700 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isCreatingDataset ? "Creating dataset..." : "Create dataset"}
          </button>
        </form>

        <form
          className="rounded-lg border border-stone-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-900"
          onSubmit={handleStartRun}
        >
          <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-50">
            Start evaluation run
          </h2>
          <p className="mt-2 text-sm leading-7 text-slate-600 dark:text-slate-300">
            Queue an evaluation run through POST /api/evaluation/evaluation/run, then inspect the
            generated run route.
          </p>
          <div className="mt-5 grid gap-4 md:grid-cols-2">
            <div>
              <label
                htmlFor={RUN_DATASET_INPUT_ID}
                className="mb-2 block text-sm font-medium text-slate-900 dark:text-slate-100"
              >
                Dataset
              </label>
              <select
                id={RUN_DATASET_INPUT_ID}
                value={selectedDatasetId}
                onChange={(event) => setSelectedDatasetId(event.target.value)}
                className="w-full rounded-md border border-stone-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none transition focus:border-teal-700 focus:ring-2 focus:ring-teal-700/20 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100"
              >
                <option value="">Select a dataset</option>
                {datasets.map((dataset) => (
                  <option key={dataset.dataset_id} value={dataset.dataset_id}>
                    {dataset.name} ({dataset.dataset_id})
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label
                htmlFor={RUN_AGENT_INPUT_ID}
                className="mb-2 block text-sm font-medium text-slate-900 dark:text-slate-100"
              >
                Agent ID
              </label>
              <input
                id={RUN_AGENT_INPUT_ID}
                value={agentId}
                onChange={(event) => setAgentId(event.target.value)}
                className="w-full rounded-md border border-stone-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none transition focus:border-teal-700 focus:ring-2 focus:ring-teal-700/20 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100"
                placeholder="agent-showcase"
              />
            </div>
          </div>
          <button
            type="submit"
            disabled={isStartingRun || datasets.length === 0}
            className="mt-5 rounded-md border border-teal-700 bg-teal-700 px-4 py-2 text-sm font-semibold text-white transition hover:bg-teal-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-700 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isStartingRun ? "Starting run..." : "Start run"}
          </button>
          {datasets.length === 0 && !isLoadingDatasets && (
            <p className="mt-3 text-sm leading-7 text-slate-600 dark:text-slate-300">
              Create a dataset before launching an evaluation run.
            </p>
          )}
        </form>
      </section>

      <section className="rounded-lg border border-stone-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-900">
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-50">
              Evaluation datasets
            </h2>
            <p className="mt-2 text-sm leading-7 text-slate-600 dark:text-slate-300">
              Loaded with GET /api/evaluation/datasets through the evaluation API facade.
            </p>
          </div>
          <button
            type="button"
            onClick={() => loadDatasets()}
            disabled={isLoadingDatasets}
            className="rounded-md border border-stone-200 bg-white px-4 py-2 text-sm font-semibold text-slate-900 transition hover:bg-stone-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-700 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-50 dark:hover:bg-slate-800"
          >
            {isLoadingDatasets ? "Refreshing..." : "Refresh datasets"}
          </button>
        </div>

        <div className="mt-5 overflow-x-auto">
          <table className="w-full min-w-[42rem] text-left text-sm">
            <thead>
              <tr className="border-b border-stone-200 text-xs uppercase tracking-[0.18em] text-slate-500 dark:border-slate-700 dark:text-slate-400">
                <th className="py-3 pr-4 font-semibold">Dataset</th>
                <th className="py-3 pr-4 font-semibold">Dataset ID</th>
                <th className="py-3 pr-4 font-semibold">Items</th>
                <th className="py-3 font-semibold">Action</th>
              </tr>
            </thead>
            <tbody>
              {datasets.map((dataset) => (
                <tr
                  key={dataset.dataset_id}
                  className="border-b border-stone-100 text-slate-700 last:border-0 dark:border-slate-800 dark:text-slate-200"
                >
                  <td className="py-3 pr-4 font-medium text-slate-900 dark:text-slate-50">
                    {dataset.name}
                  </td>
                  <td className="py-3 pr-4 font-mono text-xs">{dataset.dataset_id}</td>
                  <td className="py-3 pr-4">{dataset.items.length}</td>
                  <td className="py-3">
                    <button
                      type="button"
                      onClick={() => setSelectedDatasetId(dataset.dataset_id)}
                      className="rounded-md border border-stone-200 px-3 py-1.5 text-xs font-semibold text-slate-900 transition hover:bg-stone-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-700 focus-visible:ring-offset-2 dark:border-slate-700 dark:text-slate-50 dark:hover:bg-slate-800"
                    >
                      Use for run
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {datasets.length === 0 && !isLoadingDatasets && (
            <p className="mt-4 rounded-md border border-stone-200 bg-stone-50 p-4 text-sm leading-7 text-slate-600 dark:border-slate-700 dark:bg-slate-950/60 dark:text-slate-300">
              No datasets were returned by the evaluation service.
            </p>
          )}
        </div>
      </section>

      <section className="rounded-lg border border-stone-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-900">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-teal-700 dark:text-teal-300">
            Route capability map
          </p>
          <h2 className="mt-3 text-xl font-semibold text-slate-900 dark:text-slate-50">
            Current, adapter, blocked, and planned surfaces
          </h2>
          <p className="mt-2 text-sm leading-7 text-slate-600 dark:text-slate-300">
            This map is data-driven from the frontend route registry so pilot users can see which
            capabilities are live, bridged, blocked, or planned.
          </p>
        </div>

        <div className="mt-6 grid gap-5 lg:grid-cols-2">
          {routeGroups.map(({ category, routes }) => (
            <div
              key={category}
              className="rounded-md border border-stone-200 dark:border-slate-700"
            >
              <div className="border-b border-stone-200 px-4 py-3 dark:border-slate-700">
                <h3 className="text-base font-semibold text-slate-900 dark:text-slate-50">
                  {ROUTE_CATEGORY_LABELS[category]}
                </h3>
              </div>
              <ul className="divide-y divide-stone-100 dark:divide-slate-800">
                {routes.map((route) => (
                  <li key={route.path} className="p-4">
                    <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                      <div>
                        <p className="font-mono text-xs text-slate-500 dark:text-slate-400">
                          {route.path}
                        </p>
                        <p className="mt-1 font-semibold text-slate-900 dark:text-slate-50">
                          {route.label}
                        </p>
                      </div>
                      <span
                        className={`inline-flex w-fit rounded-full border px-3 py-1 text-xs font-semibold ${getStatusBadgeClassName(
                          route.status,
                        )}`}
                      >
                        {ROUTE_STATUS_LABELS[route.status]}
                      </span>
                    </div>
                    <p className="mt-3 text-sm leading-7 text-slate-600 dark:text-slate-300">
                      {route.capability}
                    </p>
                    {route.status === "adapter" && (
                      <p className="mt-2 text-xs font-medium text-slate-500 dark:text-slate-400">
                        Adapts to {route.adaptsTo}
                      </p>
                    )}
                    {route.status === "blocked" && (
                      <p className="mt-2 text-xs font-medium text-amber-900 dark:text-amber-100">
                        Blocker: {route.blocker}
                      </p>
                    )}
                    {(route.status === "implemented" || route.status === "adapter") && (
                      <Link
                        href={route.href}
                        className="mt-3 inline-flex rounded-md border border-stone-200 px-3 py-1.5 text-xs font-semibold text-slate-900 transition hover:bg-stone-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-700 focus-visible:ring-offset-2 dark:border-slate-700 dark:text-slate-50 dark:hover:bg-slate-800"
                      >
                        Open route
                      </Link>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};

export default EvaluationDashboard;
