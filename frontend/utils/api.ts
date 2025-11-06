import axios, { AxiosInstance, AxiosResponse } from "axios";

import { ApiEnvelope, unwrapContent } from "@/types/api";

export const BACK_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost";

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

export const avatarEngine = createClient(process.env.AVATAR_APP_BASE_URL, "http://localhost:8084");
export const essaysEngine = createClient(process.env.ESSAYS_APP_BASE_URL, "http://localhost:8083");
export const questionsEngine = createClient(process.env.QUESTIONS_APP_BASE_URL, "http://localhost:8082");
export const configurationApi = createClient(process.env.CONFIGURATION_APP_BASE_URL, "http://localhost:8081");
export const upskillingApi = createClient(process.env.UPSKILLING_APP_BASE_URL, "http://localhost:8085");

const api = createClient(process.env.WEB_APP_BASE_URL, "http://localhost:8084");

export default api;
