import type { Route } from "./+types/driver";
import { Link, NavLink } from "react-router";
import { useEffect, useMemo, useState } from "react";
import { ingestRecord, type IngestResponse } from "../lib/api";

const weatherOptions = ["Clear", "Cloudy", "Rainy", "Stormy", "Windy"];

function timeToIso(time: string) {
  const [hours, minutes] = time.split(":").map(Number);
  const now = new Date();
  now.setHours(hours || 0, minutes || 0, 0, 0);
  return now.toISOString();
}

export function meta({}: Route.MetaArgs) {
  return [
    { title: "Massar Driver | Data Entry" },
    { name: "description", content: "Capture route arrivals and sync to backend" },
  ];
}

export default function Driver() {
  const [routeId, setRouteId] = useState("Route 402: Downtown Loop");
  const [scheduledTime, setScheduledTime] = useState("14:30");
  const [actualTime, setActualTime] = useState("14:35");
  const [weather, setWeather] = useState("Clear");
  const [autoWeather, setAutoWeather] = useState(true);
  const [passengers, setPassengers] = useState(12);
  const [coords, setCoords] = useState<{ latitude?: number; longitude?: number }>({});
  const [loading, setLoading] = useState(false);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [prediction, setPrediction] = useState<number | null>(null);
  const [recordId, setRecordId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!navigator?.geolocation) return;
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setCoords({
          latitude: Number(pos.coords.latitude.toFixed(6)),
          longitude: Number(pos.coords.longitude.toFixed(6)),
        });
      },
      () => {
        setCoords({});
      },
      { enableHighAccuracy: false, maximumAge: 120000 }
    );
  }, []);

  useEffect(() => {
    if (autoWeather) {
      setWeather("Clear");
    }
  }, [autoWeather]);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setFeedback(null);
    setPrediction(null);
    setError(null);

    try {
      const payload = {
        route_id: routeId,
        scheduled_time: timeToIso(scheduledTime),
        actual_time: actualTime ? timeToIso(actualTime) : null,
        weather,
        passenger_count: passengers,
        latitude: coords.latitude ?? null,
        longitude: coords.longitude ?? null,
      };

      const res = await ingestRecord(payload);
      const record =
        "record" in (res as IngestResponse) && (res as any).record
          ? (res as any).record
          : (res as any);
      const predictionValue =
        "prediction" in (res as IngestResponse) && (res as any).prediction
          ? (res as any).prediction.predicted_delay
          : null;

      setFeedback("Trip data submitted and stored successfully.");
      setRecordId(record?.id ?? null);
      setPrediction(predictionValue);
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Failed to submit trip data.");
    } finally {
      setLoading(false);
    }
  };

  const statusText = useMemo(() => {
    if (prediction === null) return "Awaiting prediction";
    if (prediction <= 0) return "On time";
    if (prediction <= 5) return "Slight delay";
    return "Delayed";
  }, [prediction]);

  const shellBg = "bg-[#0b1226]";
  const panelBg = "bg-[#0f1834]";
  const card = "rounded-2xl border border-[#1f2b4d] bg-[#111a32] shadow-[0_15px_45px_rgba(0,0,0,0.35)]";
  const pill = "rounded-xl bg-[#0f1834] border border-[#1f2b4d]";
  const accent = "#f5c842";
  const handleRefresh = () => window.location.reload();

  return (
    <div className={`min-h-screen ${shellBg} text-[#e6ecff] px-4 pb-12 pt-6`}>
      <div className="mx-auto flex w-full max-w-5xl flex-col gap-6">
        <header className="flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-[#1f2b4d] bg-[#0f1834] px-4 py-3 shadow-[0_10px_30px_rgba(0,0,0,0.35)]">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl border border-[#1f2b4d] bg-[#0b1226] p-2">
              <img src="/massar-logo.svg" alt="Massar logo" className="h-full w-full object-contain" />
            </div>
            <div>
              <p className="text-xs uppercase tracking-wide text-[#8fa2ce]">Driver Console</p>
              <h1 className="text-lg font-semibold text-white">Live Trip Entry & Instant Prediction</h1>
            </div>
          </div>
          <div className="flex items-center gap-2 text-sm font-medium">
            <NavLink
              to="/driver"
              className={({ isActive }) =>
                `${pill} px-3 py-1 ${isActive ? "bg-[#f5c842] text-[#0d1530] border-[#f5c842]" : "text-[#cbd5ff]"}`
              }
            >
              Driver
            </NavLink>
            <NavLink
              to="/dashboard"
              className={({ isActive }) =>
                `${pill} px-3 py-1 ${isActive ? "bg-[#f5c842] text-[#0d1530] border-[#f5c842]" : "text-[#cbd5ff]"}`
              }
            >
              Dashboard
            </NavLink>
            <button
              type="button"
              onClick={handleRefresh}
              className={`${pill} px-3 py-1 text-[#cbd5ff] hover:bg-[#152147]`}
            >
              Refresh
            </button>
          </div>
        </header>

        <div className="grid gap-4 lg:grid-cols-[1.4fr_1fr]">
          <form onSubmit={handleSubmit} className="space-y-4">
            <section className={`${card} p-4`}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm text-[#8fa2ce]">
                  <span className="text-[#f5c842]">📍</span>
                  <span>Route</span>
                </div>
                <span className="rounded-full bg-[#182449] px-3 py-1 text-xs text-[#cbd5ff]">Live</span>
              </div>
              <div className="mt-2 text-xl font-semibold text-white">{routeId}</div>
              <div className={`${pill} mt-4 p-3`}>
                <div className="flex items-center justify-between text-xs text-[#8fa2ce]">
                  <span>Location</span>
                  {coords.latitude && coords.longitude ? (
                    <span className="text-[11px] text-[#f5c842]">
                      {coords.latitude}, {coords.longitude}
                    </span>
                  ) : (
                    <span className="text-[11px] text-[#6b7cab]">Locating...</span>
                  )}
                </div>
                <div className="mt-3 flex items-center justify-between">
                  <span className="h-3 w-3 rounded-full bg-[#f5c842]" />
                  <div className="mx-2 h-px flex-1 border-b border-dotted border-[#f5c842]/50" />
                  <span className="h-4 w-4 rounded-full border-2 border-[#f5c842] bg-white/5" />
                  <div className="mx-2 h-px flex-1 border-b border-dotted border-[#f5c842]/50" />
                  <span className="h-3 w-3 rounded-full bg-[#f5c842]" />
                </div>
              </div>
            </section>

            <section className="grid gap-3 md:grid-cols-2">
              <div className={`${card} p-4`}>
                <div className="flex items-center justify-between text-sm text-[#8fa2ce]">
                  <div className="flex items-center gap-2">
                    <span>🕒</span>
                    <span>Scheduled</span>
                  </div>
                  <span className="text-[11px] text-[#6b7cab]">Local time</span>
                </div>
                <input
                  type="time"
                  value={scheduledTime}
                  onChange={(e) => setScheduledTime(e.target.value)}
                  className="mt-3 w-full rounded-xl border border-[#24355f] bg-[#0b1226] px-3 py-2 text-lg font-semibold text-white focus:border-[#f5c842] focus:outline-none focus:ring-1 focus:ring-[#f5c842]"
                />
              </div>
              <div className={`${card} p-4`}>
                <div className="flex items-center justify-between text-sm text-[#8fa2ce]">
                  <div className="flex items-center gap-2">
                    <span>⏱️</span>
                    <span>Actual Arrival</span>
                  </div>
                  <button
                    type="button"
                    onClick={() =>
                      setActualTime(new Date().toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit" }))
                    }
                    className="text-[11px] text-[#f5c842] underline"
                  >
                    Now
                  </button>
                </div>
                <input
                  type="time"
                  value={actualTime}
                  onChange={(e) => setActualTime(e.target.value)}
                  className="mt-3 w-full rounded-xl border border-[#24355f] bg-[#0b1226] px-3 py-2 text-lg font-semibold text-white focus:border-[#f5c842] focus:outline-none focus:ring-1 focus:ring-[#f5c842]"
                />
              </div>
            </section>

            <section className={`${card} p-4`}>
              <div className="flex items-center justify-between text-sm text-[#8fa2ce]">
                <div className="flex items-center gap-2">
                  <span>🚌</span>
                  <span>Passenger Count</span>
                </div>
                <span className="text-[11px] text-[#6b7cab]">Tap to adjust</span>
              </div>
              <div className="mt-4 flex items-center justify-center gap-6">
                <button
                  type="button"
                  onClick={() => setPassengers((p) => Math.max(0, p - 1))}
                  className="h-12 w-12 rounded-2xl border border-[#24355f] bg-[#0b1226] text-3xl leading-none text-white shadow-inner shadow-black/30 transition hover:-translate-y-[1px]"
                >
                  −
                </button>
                <div className="text-4xl font-semibold text-[#f5c842]">{passengers}</div>
                <button
                  type="button"
                  onClick={() => setPassengers((p) => p + 1)}
                  className="h-12 w-12 rounded-2xl border border-[#24355f] bg-[#0b1226] text-3xl leading-none text-white shadow-inner shadow-black/30 transition hover:-translate-y-[1px]"
                >
                  +
                </button>
              </div>
            </section>

            <section className={`${card} p-4 space-y-3`}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm text-[#8fa2ce]">
                  <span>🌤️</span>
                  <span>Weather Conditions</span>
                </div>
                <label className="inline-flex cursor-pointer items-center gap-2 text-xs text-[#8fa2ce]">
                  <span>Auto</span>
                  <input
                    type="checkbox"
                    checked={autoWeather}
                    onChange={(e) => setAutoWeather(e.target.checked)}
                    className="h-5 w-5 accent-[#f5c842]"
                  />
                </label>
              </div>
              <div className="flex items-center gap-3">
                <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-[#0b1226] border border-[#24355f] text-2xl">
                  ☀️
                </div>
                <div className="flex-1">
                  <div className="text-lg font-semibold text-[#f5c842]">{weather}</div>
                  <div className="text-sm text-[#8fa2ce]">{autoWeather ? "Auto-detected" : "Manual entry"}</div>
                </div>
              </div>
              {!autoWeather && (
                <div className="grid grid-cols-2 gap-3">
                  {weatherOptions.map((option) => (
                    <button
                      key={option}
                      type="button"
                      onClick={() => setWeather(option)}
                      className={`rounded-xl border px-3 py-2 text-sm font-medium transition ${
                        option === weather
                          ? "border-[#f5c842] bg-[#f5c842] text-[#0d1530]"
                          : "border-[#24355f] bg-[#0b1226] text-white hover:border-[#f5c842]"
                      }`}
                    >
                      {option}
                    </button>
                  ))}
                </div>
              )}
            </section>

            <section className={`${card} p-4 space-y-3`}>
              <div className="flex items-center justify-between text-sm text-[#8fa2ce]">
                <span>Status</span>
                <Link to="/dashboard" className="text-xs text-[#f5c842] underline">
                  View dashboard
                </Link>
              </div>
              <div className="flex items-center gap-2">
                <span className="h-2.5 w-2.5 rounded-full bg-[#f5c842]" />
                <div className="text-base font-medium text-white">{statusText}</div>
              </div>
              {prediction !== null && (
                <div className="flex items-center justify-between rounded-xl bg-[#0b1226] border border-[#24355f] px-3 py-2 text-sm">
                  <span className="text-[#8fa2ce]">Predicted delay</span>
                  <span className="font-semibold text-[#f5c842]">{prediction.toFixed(1)} min</span>
                </div>
              )}
              {recordId && (
                <div className="text-xs text-[#6b7cab]">Record ID: {recordId}</div>
              )}
            </section>

            {error && (
              <div className="rounded-2xl border border-red-500/50 bg-red-500/10 px-4 py-3 text-sm text-red-100">
                {error}
              </div>
            )}
            {feedback && (
              <div className="rounded-2xl border border-emerald-400/60 bg-emerald-500/15 px-4 py-3 text-sm text-emerald-100">
                {feedback}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-2xl bg-[#f5c842] py-4 text-lg font-semibold text-[#0d1530] shadow-lg shadow-amber-500/30 transition hover:translate-y-[1px] disabled:cursor-not-allowed disabled:opacity-70"
            >
              {loading ? "Submitting..." : "Submit Trip Data"}
            </button>
          </form>

          <aside className="space-y-4">
            <div className={`${card} p-4`}>
              <div className="flex items-center justify-between text-sm text-[#8fa2ce]">
                <span>Quick glance</span>
                <span className="rounded-full bg-[#182449] px-2 py-[2px] text-[11px] text-[#f5c842]">
                  Live
                </span>
              </div>
              <div className="mt-4 space-y-3 text-sm text-[#cbd5ff]">
                <div className="flex items-center justify-between rounded-xl bg-[#0b1226] border border-[#24355f] px-3 py-2">
                  <span>Route</span>
                  <span className="font-semibold text-white">{routeId}</span>
                </div>
                <div className="flex items-center justify-between rounded-xl bg-[#0b1226] border border-[#24355f] px-3 py-2">
                  <span>Scheduled</span>
                  <span className="font-semibold text-white">{scheduledTime}</span>
                </div>
                <div className="flex items-center justify-between rounded-xl bg-[#0b1226] border border-[#24355f] px-3 py-2">
                  <span>Actual</span>
                  <span className="font-semibold text-white">{actualTime}</span>
                </div>
                <div className="flex items-center justify-between rounded-xl bg-[#0b1226] border border-[#24355f] px-3 py-2">
                  <span>Passengers</span>
                  <span className="font-semibold text-[#f5c842]">{passengers}</span>
                </div>
                <div className="flex items-center justify-between rounded-xl bg-[#0b1226] border border-[#24355f] px-3 py-2">
                  <span>Weather</span>
                  <span className="font-semibold text-white">{weather}</span>
                </div>
              </div>
            </div>
            <div className={`${card} p-4`}>
              <div className="flex items-center justify-between text-sm text-[#8fa2ce]">
                <span>Tips</span>
                <span className="text-[11px] text-[#6b7cab]">For better predictions</span>
              </div>
              <ul className="mt-3 space-y-2 text-sm text-[#cbd5ff]">
                <li className="flex gap-2">
                  <span className="text-[#f5c842]">•</span>
                  Keep actual arrival within ±2 min accuracy.
                </li>
                <li className="flex gap-2">
                  <span className="text-[#f5c842]">•</span>
                  Update weather if conditions change.
                </li>
                <li className="flex gap-2">
                  <span className="text-[#f5c842]">•</span>
                  Passenger counts help improve peak forecasts.
                </li>
              </ul>
            </div>
          </aside>
        </div>
      </div>
    </div>
  );
}

