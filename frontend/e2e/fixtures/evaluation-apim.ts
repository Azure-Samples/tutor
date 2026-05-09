import type { Page, Route } from "@playwright/test";

export interface EvaluationDatasetItem {
  [fieldName: string]: string;
}

export interface EvaluationDataset {
  dataset_id: string;
  name: string;
  items: EvaluationDatasetItem[];
}

export interface EvaluationRun {
  run_id: string;
  agent_id: string;
  dataset_id: string;
  status: string;
  total_cases: number;
}

export interface EvaluationApimRequest {
  method: string;
  path: string;
}

export interface EvaluationApimState {
  datasets: EvaluationDataset[];
  requests: EvaluationApimRequest[];
  runSequence: number;
  runs: Record<string, EvaluationRun>;
}

const DEFAULT_DATASET = {
  dataset_id: "foundation-dataset",
  name: "Foundation Evaluation Dataset",
  items: [
    {
      expected: "Acceleration is the change in velocity over time.",
      prompt: "Explain acceleration in one sentence.",
    },
  ],
} as const satisfies EvaluationDataset;

const RUN_PATH_PREFIX = "/api/evaluation/evaluation/run/";

const cloneDataset = (dataset: EvaluationDataset): EvaluationDataset => ({
  dataset_id: dataset.dataset_id,
  name: dataset.name,
  items: dataset.items.map((item) => ({ ...item })),
});

export const createEvaluationApimState = (): EvaluationApimState => ({
  datasets: [cloneDataset(DEFAULT_DATASET)],
  requests: [],
  runSequence: 1,
  runs: {},
});

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null;

const toStringValue = (value: unknown): string | null => {
  if (typeof value !== "string") {
    return null;
  }

  const trimmedValue = value.trim();

  return trimmedValue.length > 0 ? trimmedValue : null;
};

const toDatasetItem = (value: unknown): EvaluationDatasetItem | null => {
  if (!isRecord(value)) {
    return null;
  }

  const item: EvaluationDatasetItem = {};

  for (const [fieldName, fieldValue] of Object.entries(value)) {
    if (typeof fieldValue === "string") {
      item[fieldName] = fieldValue;
    }
  }

  return Object.keys(item).length > 0 ? item : null;
};

const toDatasetItems = (value: unknown): EvaluationDatasetItem[] => {
  if (!Array.isArray(value)) {
    return [];
  }

  return value.map(toDatasetItem).filter((item): item is EvaluationDatasetItem => item !== null);
};

const readJsonPayload = (route: Route): Record<string, unknown> => {
  try {
    const payload: unknown = route.request().postDataJSON();

    return isRecord(payload) ? payload : {};
  } catch {
    return {};
  }
};

const fulfillJson = async (route: Route, status: number, body: unknown) => {
  await route.fulfill({
    body: JSON.stringify(body),
    contentType: "application/json",
    status,
  });
};

const createDatasetFromPayload = (payload: Record<string, unknown>): EvaluationDataset | null => {
  const datasetId = toStringValue(payload.dataset_id);
  const name = toStringValue(payload.name);

  if (!datasetId || !name) {
    return null;
  }

  return {
    dataset_id: datasetId,
    items: toDatasetItems(payload.items),
    name,
  };
};

const createRunFromPayload = (
  state: EvaluationApimState,
  payload: Record<string, unknown>,
): EvaluationRun | null => {
  const agentId = toStringValue(payload.agent_id);
  const datasetId = toStringValue(payload.dataset_id);

  if (!agentId || !datasetId) {
    return null;
  }

  const dataset = state.datasets.find((candidate) => candidate.dataset_id === datasetId);
  const runId = `run-e2e-${String(state.runSequence).padStart(3, "0")}`;
  state.runSequence += 1;

  return {
    agent_id: agentId,
    dataset_id: datasetId,
    run_id: runId,
    status: "queued",
    total_cases: dataset?.items.length ?? 0,
  };
};

const rememberDataset = (state: EvaluationApimState, dataset: EvaluationDataset) => {
  const existingDatasetIndex = state.datasets.findIndex(
    (candidate) => candidate.dataset_id === dataset.dataset_id,
  );

  if (existingDatasetIndex >= 0) {
    state.datasets[existingDatasetIndex] = cloneDataset(dataset);
    return;
  }

  state.datasets.push(cloneDataset(dataset));
};

const getRunIdFromPath = (path: string): string =>
  decodeURIComponent(path.slice(RUN_PATH_PREFIX.length));

// Adapter between Playwright route interception and the evaluation APIM contract.
export const mockEvaluationApim = async (
  page: Page,
  state: EvaluationApimState = createEvaluationApimState(),
): Promise<EvaluationApimState> => {
  await page.route("**/api/evaluation/**", async (route) => {
    const request = route.request();
    const requestUrl = new URL(request.url());
    const method = request.method();
    const path = requestUrl.pathname;

    state.requests.push({ method, path });

    if (method === "GET" && path === "/api/evaluation/datasets") {
      await fulfillJson(route, 200, { datasets: state.datasets.map(cloneDataset) });
      return;
    }

    if (method === "POST" && path === "/api/evaluation/datasets") {
      const dataset = createDatasetFromPayload(readJsonPayload(route));

      if (!dataset) {
        await fulfillJson(route, 400, { detail: "Dataset ID and name are required." });
        return;
      }

      rememberDataset(state, dataset);
      await fulfillJson(route, 201, cloneDataset(dataset));
      return;
    }

    if (method === "POST" && path === "/api/evaluation/evaluation/run") {
      const run = createRunFromPayload(state, readJsonPayload(route));

      if (!run) {
        await fulfillJson(route, 400, { detail: "Agent ID and dataset ID are required." });
        return;
      }

      state.runs[run.run_id] = run;
      await fulfillJson(route, 202, run);
      return;
    }

    if (method === "GET" && path.startsWith(RUN_PATH_PREFIX)) {
      const runId = getRunIdFromPath(path);
      const run = state.runs[runId];

      if (!run) {
        await fulfillJson(route, 404, { detail: `Run ${runId} was not found.` });
        return;
      }

      await fulfillJson(route, 200, run);
      return;
    }

    await fulfillJson(route, 404, { detail: `Unhandled evaluation route: ${method} ${path}` });
  });

  return state;
};
