import { evaluationApi } from "@/utils/api";

export type EvaluationDatasetItem = Record<string, string>;

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

export interface CreateEvaluationDatasetInput {
  dataset_id: string;
  name: string;
  items: EvaluationDatasetItem[];
}

export interface StartEvaluationRunInput {
  agent_id: string;
  dataset_id: string;
}

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null;

const toStringValue = (value: unknown): string | undefined => {
  if (typeof value !== "string") {
    return undefined;
  }

  const trimmed = value.trim();
  return trimmed.length > 0 ? trimmed : undefined;
};

const toNumberValue = (value: unknown): number | undefined => {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }

  if (typeof value === "string") {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : undefined;
  }

  return undefined;
};

const extractArrayPayload = (data: unknown, key: string): unknown[] => {
  if (Array.isArray(data)) {
    return data;
  }

  if (isRecord(data)) {
    if (Array.isArray(data[key])) {
      return data[key];
    }

    if (Array.isArray(data.result)) {
      return data.result;
    }
  }

  return [];
};

const normalizeDatasetItem = (value: unknown): EvaluationDatasetItem | null => {
  if (!isRecord(value)) {
    return null;
  }

  const item: EvaluationDatasetItem = {};

  for (const [key, fieldValue] of Object.entries(value)) {
    if (typeof fieldValue === "string") {
      item[key] = fieldValue;
    }
  }

  return Object.keys(item).length > 0 ? item : null;
};

export const normalizeEvaluationDataset = (value: unknown): EvaluationDataset | null => {
  if (!isRecord(value)) {
    return null;
  }

  const datasetId = toStringValue(value.dataset_id) ?? toStringValue(value.id);
  const name = toStringValue(value.name) ?? datasetId;

  if (!datasetId || !name) {
    return null;
  }

  const items = Array.isArray(value.items)
    ? value.items
        .map(normalizeDatasetItem)
        .filter((item): item is EvaluationDatasetItem => item !== null)
    : [];

  return {
    dataset_id: datasetId,
    name,
    items,
  };
};

export const normalizeEvaluationRun = (value: unknown): EvaluationRun | null => {
  if (!isRecord(value)) {
    return null;
  }

  const runId = toStringValue(value.run_id) ?? toStringValue(value.id);
  const agentId = toStringValue(value.agent_id);
  const datasetId = toStringValue(value.dataset_id);
  const status = toStringValue(value.status) ?? "unknown";

  if (!runId || !agentId || !datasetId) {
    return null;
  }

  return {
    run_id: runId,
    agent_id: agentId,
    dataset_id: datasetId,
    status,
    total_cases: toNumberValue(value.total_cases) ?? 0,
  };
};

export const getEvaluationErrorMessage = (error: unknown, fallback: string): string => {
  if (error instanceof Error && error.message.trim().length > 0) {
    return error.message;
  }

  return fallback;
};

export const listEvaluationDatasets = async (): Promise<EvaluationDataset[]> => {
  const { data } = await evaluationApi.get<unknown>("/datasets");

  return extractArrayPayload(data, "datasets")
    .map(normalizeEvaluationDataset)
    .filter((dataset): dataset is EvaluationDataset => dataset !== null);
};

export const createEvaluationDataset = async (
  input: CreateEvaluationDatasetInput,
): Promise<EvaluationDataset> => {
  const { data } = await evaluationApi.post<unknown>("/datasets", input);
  const dataset = normalizeEvaluationDataset(data);

  if (!dataset) {
    throw new Error("The evaluation service returned an unreadable dataset response.");
  }

  return dataset;
};

export const startEvaluationRun = async (
  input: StartEvaluationRunInput,
): Promise<EvaluationRun> => {
  const { data } = await evaluationApi.post<unknown>("/evaluation/run", input);
  const run = normalizeEvaluationRun(data);

  if (!run) {
    throw new Error("The evaluation service returned an unreadable run response.");
  }

  return run;
};

export const getEvaluationRun = async (runId: string): Promise<EvaluationRun> => {
  const { data } = await evaluationApi.get<unknown>(`/evaluation/run/${encodeURIComponent(runId)}`);
  const run = normalizeEvaluationRun(data);

  if (!run) {
    throw new Error("The evaluation service returned an unreadable run response.");
  }

  return run;
};
