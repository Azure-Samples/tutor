import axios, {
  type AxiosInstance,
  type AxiosResponse,
  type InternalAxiosRequestConfig,
} from "axios";

import { type ApiEnvelope, unwrapContent } from "@/types/api";

type MaybeEnvelope<T> = ApiEnvelope<T> | T;

const LOCAL_DEVELOPMENT_HEADERS = {
  "X-User-Id": "showcase-user",
  "X-User-Name": "Showcase User",
  "X-User-Email": "showcase-user@local.test",
  "X-User-Roles": "student,professor,principal,supervisor,admin,alumni",
  "X-Institution-Ids": "tutor-pilot-tenant",
  "X-School-Ids": "aurora-campus-north,aurora-campus-west",
  "X-Program-Ids": "executive-mba,analytics-reentry",
  "X-Course-Ids": "leadership-communication,applied-analytics",
  "X-Class-Ids": "writing-studio-a,capstone-advising",
  "X-Learner-Ids": "amelia-ortiz,paulo-nogueira",
  "X-Staff-Ids": "showcase-user,helena-costa,marcos-azevedo,renata-mendes,luciana-vieira",
  "X-Feature-Flags": "workspace-shell,workspace-snapshots,learner-record-preview",
} as const;

const LOCAL_HOST_PATTERN = /^(localhost|127\.0\.0\.1|0\.0\.0\.0|\[::1\]|::1)$/i;

const normalizeBaseURL = (value: string | undefined): string | undefined => {
  if (!value) {
    return undefined;
  }

  const trimmed = value.trim();
  if (!trimmed) {
    return undefined;
  }

  if (/^http:\/\/(localhost|127\.0\.0\.1)(:\d+)?/i.test(trimmed)) {
    return trimmed.replace(/\/+$/, "");
  }

  if (trimmed.startsWith("http://")) {
    return `https://${trimmed.slice("http://".length)}`.replace(/\/+$/, "");
  }

  return trimmed.replace(/\/+$/, "");
};

const getRequiredApimBaseUrl = (): string => {
  const normalizedBase = normalizeBaseURL(process.env.NEXT_PUBLIC_APIM_BASE_URL);

  if (!normalizedBase) {
    throw new Error(
      "NEXT_PUBLIC_APIM_BASE_URL is required. Frontend-backend traffic must flow through APIM.",
    );
  }

  return normalizedBase;
};

const unwrapResponse = <T>(response: AxiosResponse<MaybeEnvelope<T>>) => {
  if (response?.data) {
    response.data = unwrapContent<T>(response.data);
  }
  return response as AxiosResponse<T>;
};

const isLocalLikeUrl = (value: string | undefined): boolean => {
  if (!value) {
    return false;
  }

  try {
    const candidate =
      value.startsWith("http://") || value.startsWith("https://") ? value : `http://${value}`;
    return LOCAL_HOST_PATTERN.test(new URL(candidate).hostname);
  } catch {
    return /^https?:\/\/(localhost|127\.0\.0\.1|0\.0\.0\.0|\[::1\]|::1)(:\d+)?/i.test(value);
  }
};

const applyLegacyLocalHeaders = (config: InternalAxiosRequestConfig) => {
  const headers = config.headers as unknown as {
    set?: (name: string, value: string) => void;
    [key: string]: unknown;
  };

  if (typeof headers?.set === "function") {
    for (const [name, value] of Object.entries(LOCAL_DEVELOPMENT_HEADERS)) {
      headers.set?.(name, value);
    }
    return;
  }

  config.headers = {
    ...(config.headers || {}),
    ...LOCAL_DEVELOPMENT_HEADERS,
  } as never;
};

const createClient = (
  baseURL: string | undefined,
  resolveBaseURL?: () => string | undefined,
): AxiosInstance => {
  const client = axios.create({
    baseURL: normalizeBaseURL(baseURL),
  });
  client.interceptors.request.use((config) => {
    const resolvedBaseURL =
      normalizeBaseURL(config.baseURL) ?? normalizeBaseURL(resolveBaseURL?.());

    if (resolvedBaseURL) {
      config.baseURL = resolvedBaseURL;
    }

    if (typeof config.url === "string" && config.url.startsWith("http://")) {
      const isLocal = /^http:\/\/(localhost|127\.0\.0\.1)(:\d+)?/i.test(config.url);
      if (!isLocal) {
        config.url = `https://${config.url.slice("http://".length)}`;
      }
    }

    if (isLocalLikeUrl(config.baseURL) || isLocalLikeUrl(config.url)) {
      applyLegacyLocalHeaders(config);
    }

    return config;
  });
  client.interceptors.response.use(unwrapResponse, (error) => {
    const data = error?.response?.data;
    if (data && typeof data === "object" && "detail" in data) {
      error.message = (data as { detail?: string }).detail || error.message;
    }
    return Promise.reject(error);
  });
  return client;
};

const createServiceClient = (
  _directBaseURL: string | undefined,
  _fallback: string,
  apimPath: string,
): AxiosInstance => {
  const normalizedPath = apimPath.replace(/^\/+/, "");

  return createClient(undefined, () => `${getRequiredApimBaseUrl()}/${normalizedPath}`);
};

export const avatarEngine = createServiceClient(
  process.env.NEXT_PUBLIC_AVATAR_APP_BASE_URL,
  "http://localhost:8084",
  "api/avatar",
);
export const essaysEngine = createServiceClient(
  process.env.NEXT_PUBLIC_ESSAYS_APP_BASE_URL,
  "http://localhost:8083",
  "api/essays",
);
export const questionsEngine = createServiceClient(
  process.env.NEXT_PUBLIC_QUESTIONS_APP_BASE_URL,
  "http://localhost:8082",
  "api/questions",
);
export const configurationApi = createServiceClient(
  process.env.NEXT_PUBLIC_CONFIGURATION_APP_BASE_URL,
  "http://localhost:8081",
  "api/configuration",
);
export const upskillingApi = createServiceClient(
  process.env.NEXT_PUBLIC_UPSKILLING_APP_BASE_URL,
  "http://localhost:8085",
  "api/upskilling",
);
export const chatApi = createServiceClient(
  process.env.NEXT_PUBLIC_WEB_APP_BASE_URL,
  "http://localhost:8086",
  "api/chat",
);
export const evaluationApi = createServiceClient(
  process.env.NEXT_PUBLIC_EVALUATION_APP_BASE_URL,
  "http://localhost:8086",
  "api/evaluation",
);
export const lmsGatewayApi = createServiceClient(
  process.env.NEXT_PUBLIC_LMS_GATEWAY_APP_BASE_URL,
  "http://localhost:8087",
  "api/lms-gateway",
);
export const insightsApi = createServiceClient(
  process.env.NEXT_PUBLIC_INSIGHTS_APP_BASE_URL,
  "http://localhost:8088",
  "api/insights",
);

// Compatibility aliases for legacy modules still in the repo.
export const webApp = chatApi;
export const webApi = chatApi;
export const transcriptionApi = questionsEngine;

export default chatApi;
