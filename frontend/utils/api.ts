import axios, { AxiosInstance, AxiosResponse } from "axios";

import { ApiEnvelope, unwrapContent } from "@/types/api";

const resolveEnv = (publicName: string, legacyName?: string): string | undefined => {
  if (process.env[publicName]) {
    return process.env[publicName];
  }

  if (legacyName && process.env[legacyName]) {
    return process.env[legacyName];
  }

  return undefined;
};

export const BACK_URL = resolveEnv("NEXT_PUBLIC_API_BASE_URL", "API_BASE_URL") || "http://localhost";
const APIM_BASE_URL = process.env.NEXT_PUBLIC_APIM_BASE_URL;

type MaybeEnvelope<T> = ApiEnvelope<T> | T;

const unwrapResponse = <T>(response: AxiosResponse<MaybeEnvelope<T>>) => {
  if (response && response.data) {
    response.data = unwrapContent<T>(response.data);
  }
  return response as AxiosResponse<T>;
};

const createClient = (baseURL: string | undefined, fallback: string): AxiosInstance => {
  const client = axios.create({ baseURL: baseURL || fallback });
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
    const normalizedBase = APIM_BASE_URL.replace(/\/+$/, "");
    const normalizedPath = apimPath.replace(/^\/+/, "");
    return createClient(`${normalizedBase}/${normalizedPath}`, fallback);
  }

  return createClient(directBaseURL, fallback);
};

export const avatarEngine = createServiceClient(resolveEnv("NEXT_PUBLIC_AVATAR_APP_BASE_URL", "AVATAR_APP_BASE_URL"), "http://localhost:8084", "api/avatar");
export const essaysEngine = createServiceClient(resolveEnv("NEXT_PUBLIC_ESSAYS_APP_BASE_URL", "ESSAYS_APP_BASE_URL"), "http://localhost:8083", "api/essays");
export const questionsEngine = createServiceClient(resolveEnv("NEXT_PUBLIC_QUESTIONS_APP_BASE_URL", "QUESTIONS_APP_BASE_URL"), "http://localhost:8082", "api/questions");
export const configurationApi = createServiceClient(resolveEnv("NEXT_PUBLIC_CONFIGURATION_APP_BASE_URL", "CONFIGURATION_APP_BASE_URL"), "http://localhost:8081", "api/configuration");
export const upskillingApi = createServiceClient(resolveEnv("NEXT_PUBLIC_UPSKILLING_APP_BASE_URL", "UPSKILLING_APP_BASE_URL"), "http://localhost:8085", "api/upskilling");
export const webApp = createServiceClient(resolveEnv("NEXT_PUBLIC_WEB_APP_BASE_URL", "WEB_APP_BASE_URL"), "http://localhost:8084", "api/chat");
export const transcriptionApi = createServiceClient(resolveEnv("NEXT_PUBLIC_TRANSCRIPTION_APP_BASE_URL", "TRANSCRIPTION_APP_BASE_URL"), "http://localhost:8084", "api/questions");
export const webApi = webApp;

const api = createServiceClient(resolveEnv("NEXT_PUBLIC_WEB_APP_BASE_URL", "WEB_APP_BASE_URL"), "http://localhost:8084", "api/chat");

export default api;
