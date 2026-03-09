import axios, { AxiosInstance, AxiosResponse } from "axios";

import { ApiEnvelope, unwrapContent } from "@/types/api";

const APIM_BASE_URL = process.env.NEXT_PUBLIC_APIM_BASE_URL;
if (!APIM_BASE_URL) {
  throw new Error("NEXT_PUBLIC_APIM_BASE_URL is required. Frontend-backend traffic must flow through APIM.");
}

type MaybeEnvelope<T> = ApiEnvelope<T> | T;

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

const unwrapResponse = <T>(response: AxiosResponse<MaybeEnvelope<T>>) => {
  if (response && response.data) {
    response.data = unwrapContent<T>(response.data);
  }
  return response as AxiosResponse<T>;
};

const createClient = (baseURL: string | undefined): AxiosInstance => {
  const client = axios.create({
    baseURL: normalizeBaseURL(baseURL),
  });
  client.interceptors.request.use((config) => {
    if (config.baseURL) {
      config.baseURL = normalizeBaseURL(config.baseURL);
    }

    if (typeof config.url === "string" && config.url.startsWith("http://")) {
      const isLocal = /^http:\/\/(localhost|127\.0\.0\.1)(:\d+)?/i.test(config.url);
      if (!isLocal) {
        config.url = `https://${config.url.slice("http://".length)}`;
      }
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
  apimPath: string
): AxiosInstance => {
  const normalizedBase = normalizeBaseURL(APIM_BASE_URL);
  const normalizedPath = apimPath.replace(/^\/+/, "");
  return createClient(normalizedBase ? `${normalizedBase}/${normalizedPath}` : undefined);
};

export const avatarEngine = createServiceClient(process.env.NEXT_PUBLIC_AVATAR_APP_BASE_URL, "http://localhost:8084", "api/avatar");
export const essaysEngine = createServiceClient(process.env.NEXT_PUBLIC_ESSAYS_APP_BASE_URL, "http://localhost:8083", "api/essays");
export const questionsEngine = createServiceClient(process.env.NEXT_PUBLIC_QUESTIONS_APP_BASE_URL, "http://localhost:8082", "api/questions");
export const configurationApi = createServiceClient(process.env.NEXT_PUBLIC_CONFIGURATION_APP_BASE_URL, "http://localhost:8081", "api/configuration");
export const upskillingApi = createServiceClient(process.env.NEXT_PUBLIC_UPSKILLING_APP_BASE_URL, "http://localhost:8085", "api/upskilling");
export const chatApi = createServiceClient(process.env.NEXT_PUBLIC_WEB_APP_BASE_URL, "http://localhost:8086", "api/chat");
export const evaluationApi = createServiceClient(process.env.NEXT_PUBLIC_EVALUATION_APP_BASE_URL, "http://localhost:8086", "api/evaluation");
export const lmsGatewayApi = createServiceClient(process.env.NEXT_PUBLIC_LMS_GATEWAY_APP_BASE_URL, "http://localhost:8087", "api/lms-gateway");

// Compatibility aliases for legacy modules still in the repo.
export const webApp = chatApi;
export const webApi = chatApi;
export const transcriptionApi = questionsEngine;

export default chatApi;
