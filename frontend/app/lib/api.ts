import axios from "axios";

// Use environment variable for API URL, fallback to localhost for development
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 
    "Content-Type": "application/json",
    "Accept": "application/json",
  },
  timeout: 30000, // 30 second timeout
  withCredentials: false,
});

// Add response interceptor for better error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const apiUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";
    if (error.code === "ECONNABORTED" || error.message === "Network Error") {
      error.response = {
        data: {
          detail: `Unable to connect to the server at ${apiUrl}. Please check if the backend is running and the VITE_API_BASE_URL environment variable is set correctly.`,
        },
      };
    } else if (!error.response) {
      error.response = {
        data: {
          detail: `Network error: Unable to reach the server at ${apiUrl}. Please check if the backend is running.`,
        },
      };
    }
    return Promise.reject(error);
  }
);

export interface RecordInPayload {
  route_id: string;
  scheduled_time: string;
  actual_time?: string | null;
  weather: string;
  passenger_count?: number | null;
  latitude?: number | null;
  longitude?: number | null;
}

export interface RecordOut {
  id: number;
  route_id: string;
  scheduled_time: string;
  actual_time?: string | null;
  weather: string;
  passenger_count?: number | null;
  latitude?: number | null;
  longitude?: number | null;
  cleaned: boolean;
  delay_minutes?: number | null;
  created_at: string;
}

export interface PredictOut {
  record_id?: number | null;
  predicted_delay: number;
  model_version: string;
}

export interface Metrics {
  total_records: number;
  total_predictions: number;
  last_model_version: string | null;
}

export interface PredictionWithRecord {
  id: number;
  predicted_delay: number;
  model_version: string;
  created_at: string;
  record: RecordOut;
}

export type IngestResponse =
  | RecordOut
  | {
      record?: RecordOut;
      prediction?: PredictOut;
      message?: string;
    };

export async function ingestRecord(payload: RecordInPayload) {
  const { data } = await api.post<IngestResponse>("/records/ingest", payload);
  return data;
}

export async function fetchMetrics() {
  const { data } = await api.get<Metrics>("/metrics");
  return data;
}

export async function fetchRecords(limit = 20, offset = 0) {
  const { data } = await api.get<RecordOut[]>("/records/", {
    params: { limit, offset },
  });
  return data;
}

export async function predictDelay(payload: RecordInPayload, persist = false) {
  const { data } = await api.post<PredictOut>("/predict", payload, {
    params: { persist },
  });
  return data;
}

export async function fetchPredictions(limit = 20, offset = 0) {
  const { data } = await api.get<PredictionWithRecord[]>("/records/predictions", {
    params: { limit, offset },
  });
  return data;
}

