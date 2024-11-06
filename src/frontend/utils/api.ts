import axios from 'axios';

export const BACK_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost'

export const webApp = axios.create({
  baseURL: process.env.WEB_APP_BASE_URL || "http://localhost:8081"
});

export const webApi = axios.create({
  baseURL: process.env.WEB_API_BASE_URL || "http://localhost:8082"
});

export const transcriptionApi = axios.create({
  baseURL: process.env.TRANSCRIPTION_API_BASE_URL || "http://localhost:8083"
});

export const evaluateApi = axios.create({
  baseURL: process.env.EVALUATE_API_BASE_URL || "http://localhost:8084"
});
