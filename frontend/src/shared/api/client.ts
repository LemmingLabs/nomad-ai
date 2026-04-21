import axios from 'axios';
import { AxiosError } from 'axios';
import { config } from '../config';

export const apiClient = axios.create({
  baseURL: config.apiBaseUrl,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ─── Request Interceptor ─────────────────────────────────────────────────────
apiClient.interceptors.request.use(
  (req) => {
    const token = localStorage.getItem(config.storageKeys.accessToken);
    if (token && req.headers) {
      req.headers.Authorization = `Bearer ${token}`;
    }
    return req;
  },
  (error: unknown) =>
    Promise.reject(error instanceof Error ? error : new Error('Request interceptor failed')),
);

// ─── Response Interceptor ────────────────────────────────────────────────────
apiClient.interceptors.response.use(
  (response) => response,
  (error: unknown) => {
    if (error instanceof AxiosError && error.response?.status === 401) {
      localStorage.removeItem(config.storageKeys.accessToken);
    }
    return Promise.reject(error instanceof Error ? error : new Error('Response interceptor failed'));
  },
);
