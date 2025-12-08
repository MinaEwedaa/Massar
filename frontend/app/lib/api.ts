import axios from "axios";

export const api = axios.create({
  baseURL: "http://localhost:8000/api/v1",
  headers: { "Content-Type": "application/json" },
});

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

