import axios from 'axios';

export const BACK_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost'

const api = axios.create({
  baseURL: process.env.WEB_APP_BASE_URL || "http://localhost:8084"
});

export const avatarEngine = axios.create({
  baseURL: process.env.AVATAR_APP_BASE_URL || "http://localhost:8084"
});

export const essaysEngine = axios.create({
  baseURL: process.env.ESSAYS_APP_BASE_URL || "http://localhost:8082"
});

export const questionsEngine = axios.create({
  baseURL: process.env.QUESTIONS_APP_BASE_URL || "http://localhost:8083"
});

export const configurationApi = axios.create({
  baseURL: process.env.CONFIGURATION_APP_BASE_URL || "http://localhost:8081"
});

export default api;
