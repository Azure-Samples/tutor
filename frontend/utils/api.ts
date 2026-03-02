import axios, { AxiosInstance, AxiosResponse } from "axios";

import { ApiEnvelope, unwrapContent } from "@/types/api";

export const BACK_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost";
const APIM_BASE_URL = process.env.NEXT_PUBLIC_APIM_BASE_URL;
const IS_PRODUCTION = process.env.NODE_ENV === "production";

if (IS_PRODUCTION && !APIM_BASE_URL) {
  throw new Error("NEXT_PUBLIC_APIM_BASE_URL is required in production deployments.");
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

const createClient = (baseURL: string | undefined, fallback?: string): AxiosInstance => {
  const client = axios.create({
    baseURL: normalizeBaseURL(baseURL) || normalizeBaseURL(fallback),
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
  directBaseURL: string | undefined,
  fallback: string,
  apimPath: string
): AxiosInstance => {
  if (APIM_BASE_URL) {
    const normalizedBase = normalizeBaseURL(APIM_BASE_URL);
    const normalizedPath = apimPath.replace(/^\/+/, "");
    return createClient(normalizedBase ? `${normalizedBase}/${normalizedPath}` : undefined, fallback);
  }

  if (IS_PRODUCTION) {
    return createClient(normalizeBaseURL(directBaseURL));
  }

  return createClient(normalizeBaseURL(directBaseURL), fallback);
};

export const avatarEngine = createServiceClient(process.env.NEXT_PUBLIC_AVATAR_APP_BASE_URL, "http://localhost:8084", "api/avatar");
export const essaysEngine = createServiceClient(process.env.NEXT_PUBLIC_ESSAYS_APP_BASE_URL, "http://localhost:8083", "api/essays");
export const questionsEngine = createServiceClient(process.env.NEXT_PUBLIC_QUESTIONS_APP_BASE_URL, "http://localhost:8082", "api/questions");
export const configurationApi = createServiceClient(process.env.NEXT_PUBLIC_CONFIGURATION_APP_BASE_URL, "http://localhost:8081", "api/configuration");
export const upskillingApi = createServiceClient(process.env.NEXT_PUBLIC_UPSKILLING_APP_BASE_URL, "http://localhost:8085", "api/upskilling");
export const webApp = createServiceClient(process.env.NEXT_PUBLIC_WEB_APP_BASE_URL, "http://localhost:8084", "api/chat");
export const transcriptionApi = createServiceClient(process.env.NEXT_PUBLIC_TRANSCRIPTION_APP_BASE_URL, "http://localhost:8084", "api/questions");
export const webApi = webApp;

const api = createServiceClient(process.env.NEXT_PUBLIC_WEB_APP_BASE_URL, "http://localhost:8084", "api/chat");

export default api;
