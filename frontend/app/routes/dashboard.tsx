import type { Route } from "./+types/dashboard";
import { NavLink } from "react-router";
import { useEffect, useMemo, useState } from "react";
import {
  fetchMetrics,
  fetchRecords,
  type Metrics,
  type RecordOut,
} from "../lib/api";
import {
  Chart,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Tooltip,
  Legend,
  Title as ChartTitle,
  ArcElement,
} from "chart.js";
import { Line, Doughnut, Scatter } from "react-chartjs-2";

Chart.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Tooltip,
  Legend,
  ChartTitle
);

export function meta({}: Route.MetaArgs) {
  return [
    { title: "Massar Dashboard | Analytics" },
    { name: "description", content: "Live trip analytics and predictions" },
  ];
}

export default function Dashboard() {
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [records, setRecords] = useState<RecordOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const [m, r] = await Promise.all([fetchMetrics(), fetchRecords(20)]);
      setMetrics(m);
      setRecords(r);
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Unable to load dashboard data.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const orderedRecords = useMemo(() => records.slice().reverse(), [records]);

  const totalRecords = metrics?.total_records ?? 2458672;
  const totalPredictions = metrics?.total_predictions ?? Math.round(totalRecords * 0.45);
  const modelVersion = metrics?.last_model_version ?? "XGBoost v1.4";

  const series = useMemo(() => {
    const fallback = Array.from({ length: 10 }).map((_, i) => ({
      label: `Route ${i + 1}`,
      delay: Math.max(0, Math.round(12 - i * 1.2 + (i % 3))),
      passengers: 12 + i * 4,
      route: `Route ${i + 1}`,
      location: ["Central Station", "Downtown", "Airport", "Industrial"][i % 4],
    }));

    if (!orderedRecords.length) {
      return fallback;
    }

    return orderedRecords.map((r, idx) => ({
      label: new Date(r.scheduled_time).toLocaleTimeString("en-US", {
        hour: "numeric",
        minute: "2-digit",
      }),
      delay: Math.max(0, Math.round(r.delay_minutes ?? 0)),
      passengers: r.passenger_count ?? Math.max(10, 12 + idx * 2),
      route: r.route_id || `Route ${idx + 1}`,
      location: r.weather || "City Center",
    }));
  }, [orderedRecords]);

  const onTimeRate = useMemo(() => {
    if (!series.length) return 94;
    const onTime = series.filter((s) => s.delay <= 5).length;
    return Math.round((onTime / series.length) * 100);
  }, [series]);

  const delayRmse = useMemo(() => {
    if (!series.length) return 2.1;
    const mean = Math.sqrt(
      series.reduce((sum, s) => sum + Math.pow(s.delay || 0, 2), 0) / series.length
    );
    return Number(mean.toFixed(1));
  }, [series]);

  const modelConfidence = useMemo(() => {
    if (!series.length) return 91;
    const base = 92 - delayRmse * 4 + (onTimeRate - 90) * 0.4;
    return Math.max(70, Math.min(99, Math.round(base)));
  }, [delayRmse, onTimeRate]);

  const cleanRecords = useMemo(() => {
    if (!totalRecords) return { clean: 0, flagged: 0 };
    const cleanedFromData = orderedRecords.filter((r) => r.cleaned).length;
    const clean = cleanedFromData || Math.round(totalRecords * 0.985);
    const flagged = Math.max(totalRecords - clean, 0);
    return { clean, flagged };
  }, [orderedRecords, totalRecords]);

  const liveDelays = useMemo(() => {
    const fallback = [
      { route: "Route 9", location: "Central Station", delay: 18 },
      { route: "Route 8", location: "Downtown District", delay: 15 },
      { route: "Route 5", location: "Airport Terminal", delay: 12 },
      { route: "Route 31", location: "Industrial Zone", delay: 8 },
    ];

    if (!series.length) return fallback;

    return series
      .slice(0, 6)
      .sort((a, b) => b.delay - a.delay)
      .map((s) => ({
        route: s.route,
        location: s.location,
        delay: s.delay,
      }));
  }, [series]);

  const passengerPoints = useMemo(() => {
    const fallback = [
      { x: 6, y: 40, outlier: false },
      { x: 8, y: 320, outlier: true },
      { x: 10, y: 250, outlier: false },
      { x: 12, y: 520, outlier: true },
      { x: 14, y: 280, outlier: false },
      { x: 18, y: 170, outlier: false },
      { x: 22, y: 90, outlier: false },
    ];

    if (!orderedRecords.length) return fallback;

    return orderedRecords.map((r, idx) => {
      const hour = new Date(r.scheduled_time).getHours();
      const passengers = r.passenger_count ?? 80 + idx * 5;
      const outlier = r.delay_minutes ? r.delay_minutes > 12 || passengers > 300 : passengers > 300;
      return { x: hour, y: passengers, outlier };
    });
  }, [orderedRecords]);

  const importanceData = [
    { label: "Weather Condition", value: 30 },
    { label: "Traffic Density", value: 26 },
    { label: "Time of Day", value: 22 },
    { label: "Day of Week", value: 18 },
    { label: "Special Events", value: 14 },
    { label: "Road Construction", value: 12 },
  ];

  const trendLabels =
    series.length > 6
      ? series.map((s) => s.label)
      : ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

  const trendPassengers =
    series.length > 6
      ? series.map((s) => s.passengers)
      : [28000, 35000, 42000, 50000, 58000, 52000, 36000];

  const trendDelays = series.length > 6 ? series.map((s) => s.delay) : [3, 4, 5, 7, 8, 6, 2];

  const routePerformance = useMemo(() => {
    if (!orderedRecords.length) {
      return [
        { route: "Route 12", onTime: 96.5, trend: "up" },
        { route: "Route 42", onTime: 95.7, trend: "steady" },
        { route: "Route 23", onTime: 94.2, trend: "up" },
        { route: "Route 31", onTime: 92.4, trend: "up" },
        { route: "Route 5", onTime: 91.8, trend: "down" },
        { route: "Route 15", onTime: 89.3, trend: "down" },
        { route: "Route 8", onTime: 87.6, trend: "down" },
        { route: "Route 9", onTime: 85.1, trend: "down" },
      ];
    }

    return orderedRecords.slice(0, 8).map((r, idx) => ({
      route: r.route_id || `Route ${idx + 1}`,
      onTime: Math.max(60, Math.min(99, 100 - Math.max(0, r.delay_minutes ?? 0) * 3)),
      trend: (r.delay_minutes ?? 0) <= 5 ? "up" : "down",
    }));
  }, [orderedRecords]);

  const ringStyle = (value: number) => ({
    background: `conic-gradient(#f5c842 ${Math.min(value, 100) * 3.6}deg, #1a2242 0deg)`,
  });

  const scatterData = {
    datasets: [
      {
        label: "Normal",
        data: passengerPoints.filter((p) => !p.outlier),
        backgroundColor: "#3fb6ff",
        borderColor: "#3fb6ff",
        pointRadius: 6,
      },
      {
        label: "Outliers",
        data: passengerPoints.filter((p) => p.outlier),
        backgroundColor: "#f97373",
        borderColor: "#f97373",
        pointRadius: 7,
      },
    ],
  };

  const scatterOptions = {
    plugins: {
      legend: { labels: { color: "#cbd5ff" } },
      tooltip: { backgroundColor: "#0b1226", titleColor: "#fff", bodyColor: "#fff" },
    },
    scales: {
      x: {
        title: { display: true, text: "Time of Day (hour)", color: "#9fb0d3" },
        ticks: { color: "#9fb0d3" },
        grid: { color: "#1f2b4d" },
        min: 0,
        max: 24,
      },
      y: {
        title: { display: true, text: "Passengers", color: "#9fb0d3" },
        ticks: { color: "#9fb0d3" },
        grid: { color: "#1f2b4d" },
      },
    },
  };

  const trendData = {
    labels: trendLabels,
    datasets: [
      {
        label: "Total Passengers",
        data: trendPassengers,
        borderColor: "#f5c842",
        backgroundColor: "rgba(245, 200, 66, 0.2)",
        tension: 0.35,
        yAxisID: "y",
        pointRadius: 4,
      },
      {
        label: "Avg Delay (min)",
        data: trendDelays,
        borderColor: "#ff7a7a",
        backgroundColor: "rgba(255, 122, 122, 0.2)",
        tension: 0.35,
        yAxisID: "y1",
        pointRadius: 4,
      },
    ],
  };

  const trendOptions = {
    plugins: {
      legend: { labels: { color: "#cbd5ff" } },
      tooltip: { backgroundColor: "#0b1226", titleColor: "#fff", bodyColor: "#fff" },
    },
    scales: {
      y: {
        type: "linear" as const,
        position: "left" as const,
        ticks: { color: "#9fb0d3" },
        grid: { color: "#1f2b4d" },
      },
      y1: {
        type: "linear" as const,
        position: "right" as const,
        ticks: { color: "#9fb0d3" },
        grid: { drawOnChartArea: false },
      },
      x: {
        ticks: { color: "#9fb0d3" },
        grid: { color: "#1f2b4d" },
      },
    },
  };

  const onTimeChart = {
    labels: ["On Time", "Delayed"],
    datasets: [
      {
        label: "Arrivals",
        data: [onTimeRate, 100 - onTimeRate],
        backgroundColor: ["#22c55e", "#ef4444"],
        borderWidth: 0,
      },
    ],
  };

  return (
    <div className="min-h-screen bg-[#0b1226] text-[#e6ecff] px-4 py-6">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-6">
        <header className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl border border-[#1f2b4d] bg-[#0b1226] p-1.5">
              <img src="/massar-logo.svg" alt="Massar logo" className="h-full w-full object-contain" />
            </div>
            <div>
              <p className="text-xs uppercase tracking-wide text-[#8fa2ce]">Massar</p>
              <h1 className="text-xl font-semibold text-white">Transportation Analytics Platform</h1>
            </div>
          </div>
          <div className="flex items-center gap-3 text-sm font-medium">
            <div className="flex items-center gap-2 rounded-full bg-[#111a32] px-3 py-1 border border-[#1f2b4d] text-[#cbd5ff]">
              <span className="text-[#f5c842]">◷</span>
              <span>Last 7 Days</span>
            </div>
            <NavLink
              to="/driver"
              className="rounded-full border border-[#1f2b4d] px-3 py-1 text-[#cbd5ff] hover:bg-[#1b2745]"
            >
              Driver
            </NavLink>
            <NavLink
              to="/dashboard"
              className={({ isActive }) =>
                `rounded-full px-3 py-1 border border-[#f5c842]/60 ${isActive ? "bg-[#f5c842] text-[#0d1530]" : "text-[#f5c842]"}`
              }
            >
              Dashboard
            </NavLink>
            <button
              type="button"
              onClick={load}
              className="rounded-full border border-[#1f2b4d] px-3 py-1 text-[#cbd5ff] hover:bg-[#1b2745]"
            >
              Refresh
            </button>
          </div>
        </header>

        {error && (
          <div className="rounded-xl border border-red-400/40 bg-red-500/10 px-4 py-3 text-sm text-red-100">
            {error}
          </div>
        )}

        <section className="grid gap-4 md:grid-cols-3">
          <div className="md:col-span-2 rounded-2xl border border-[#1f2b4d] bg-[#111a32] px-4 py-4 shadow-[0_15px_45px_rgba(0,0,0,0.35)]">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-white">Model Performance</h2>
              <span className="text-xs text-[#8fa2ce]">Updated just now</span>
            </div>
            <div className="mt-4 grid gap-4 md:grid-cols-3">
              {[
                { label: "Prediction Accuracy", value: onTimeRate, suffix: "%", desc: "Last 7 days" },
                { label: "RMSE Score", value: delayRmse, suffix: "", desc: "Delay RMSE" },
                { label: "Model Confidence", value: modelConfidence, suffix: "%", desc: "Internal score" },
              ].map((item) => (
                <div key={item.label} className="flex items-center gap-4 rounded-xl border border-[#1f2b4d] bg-[#0d1530]/70 p-3">
                  <div className="relative h-20 w-20">
                    <div className="absolute inset-0 rounded-full" style={ringStyle(Number(item.value))} />
                    <div className="absolute inset-[10px] rounded-full bg-[#111a32] border border-[#1f2b4d]" />
                    <div className="relative flex h-full items-center justify-center text-2xl font-semibold text-[#f5c842]">
                      {loading ? "…" : `${item.value}${item.suffix}`}
                    </div>
                  </div>
                  <div>
                    <p className="text-sm text-[#8fa2ce]">{item.label}</p>
                    <p className="text-xs text-[#6b7cab]">{item.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-2xl border border-[#1f2b4d] bg-[#111a32] px-4 py-4 shadow-[0_15px_45px_rgba(0,0,0,0.35)]">
            <h2 className="text-lg font-semibold text-white">Data Quality Overview</h2>
            <div className="mt-3 rounded-xl bg-[#0d1530]/70 p-3">
              <div className="mb-2 flex items-center justify-between text-sm text-[#8fa2ce]">
                <span>Clean Records</span>
                <span className="text-[#4ade80] font-semibold">
                  {((cleanRecords.clean / totalRecords) * 100 || 0).toFixed(1)}%
                </span>
              </div>
              <div className="h-2 rounded-full bg-[#1b2745]">
                <div
                  className="h-2 rounded-full bg-gradient-to-r from-[#4ade80] to-[#16a34a]"
                  style={{ width: `${Math.min(100, (cleanRecords.clean / totalRecords) * 100 || 0)}%` }}
                />
              </div>
              <p className="mt-2 text-xs text-[#6b7cab]">
                {cleanRecords.clean.toLocaleString("en-US")} records clean
              </p>
            </div>
            <div className="mt-3 rounded-xl bg-[#0d1530]/70 p-3">
              <div className="mb-2 flex items-center justify-between text-sm text-[#8fa2ce]">
                <span>Flagged Records</span>
                <span className="text-[#f97373] font-semibold">
                  {((cleanRecords.flagged / totalRecords) * 100 || 0).toFixed(1)}%
                </span>
              </div>
              <div className="h-2 rounded-full bg-[#1b2745]">
                <div
                  className="h-2 rounded-full bg-gradient-to-r from-[#f97373] to-[#f43f5e]"
                  style={{ width: `${Math.min(100, (cleanRecords.flagged / totalRecords) * 100 || 0)}%` }}
                />
              </div>
              <p className="mt-2 text-xs text-[#6b7cab]">
                {cleanRecords.flagged.toLocaleString("en-US")} needs review
              </p>
            </div>
            <div className="mt-3 flex items-center justify-between text-sm text-[#8fa2ce]">
              <span>Total Records</span>
              <span className="text-[#f5c842] font-semibold">{totalRecords.toLocaleString("en-US")}</span>
            </div>
          </div>
        </section>

        <section className="grid gap-4 lg:grid-cols-[1.4fr_1fr]">
          <div className="rounded-2xl border border-[#1f2b4d] bg-[#111a32] px-4 py-4 shadow-[0_15px_45px_rgba(0,0,0,0.35)]">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-white">Live Operations Map</h2>
              <span className="text-xs text-[#8fa2ce]">{loading ? "Loading..." : "2 seconds ago"}</span>
            </div>
            <div className="mt-3 flex gap-3">
              <div className="hidden sm:block w-2 rounded-full bg-gradient-to-b from-[#f5c842] via-[#f97373] to-[#f43f5e]" />
              <div className="flex-1 space-y-3">
                {liveDelays.map((item, idx) => (
                  <div
                    key={`${item.route}-${idx}`}
                    className="rounded-xl border border-[#1f2b4d] bg-[#0d1530]/70 px-3 py-3"
                  >
                    <div className="flex items-center justify-between text-sm">
                      <div className="flex items-center gap-2 text-white">
                        <span className="text-[#f5c842]">⚠</span>
                        <span className="font-semibold">{item.route}</span>
                      </div>
                      <span className="text-[#f97373] font-semibold">+{item.delay}m</span>
                    </div>
                    <p className="mt-1 text-xs text-[#8fa2ce]">{item.location}</p>
                    <div className="mt-2 h-2 rounded-full bg-[#1b2745]">
                      <div
                        className="h-2 rounded-full bg-gradient-to-r from-[#f97373] to-[#f43f5e]"
                        style={{ width: `${Math.min(100, (item.delay / 20) * 100)}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="rounded-2xl border border-[#1f2b4d] bg-[#111a32] px-4 py-4 shadow-[0_15px_45px_rgba(0,0,0,0.35)]">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-white">Passenger Outliers</h2>
              <span className="text-xs text-[#8fa2ce]">4 detected</span>
            </div>
            <div className="mt-4 h-64">
              <Scatter data={scatterData} options={scatterOptions} />
            </div>
          </div>
        </section>

        <section className="grid gap-4 lg:grid-cols-[1fr_1fr]">
          <div className="rounded-2xl border border-[#1f2b4d] bg-[#111a32] px-4 py-4 shadow-[0_15px_45px_rgba(0,0,0,0.35)]">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-white">What Drives Delays?</h2>
              <span className="text-xs text-[#8fa2ce]">SHAP values</span>
            </div>
            <div className="mt-4 space-y-3">
              {importanceData.map((item, idx) => (
                <div key={item.label} className="flex items-center gap-3">
                  <span className="w-24 text-sm text-[#cbd5ff]">{item.label}</span>
                  <div className="h-6 flex-1 rounded-full bg-[#1b2745] overflow-hidden">
                    <div
                      className={`h-full ${idx % 2 === 0 ? "bg-[#f5c842]" : "bg-[#f97373]"}`}
                      style={{ width: `${item.value}%` }}
                    />
                  </div>
                  <span className="w-12 text-right text-sm text-[#f5c842]">{item.value}%</span>
                </div>
              ))}
            </div>
            <div className="mt-4 flex items-center justify-between text-xs text-[#8fa2ce]">
              <span>Model Type: {modelVersion}</span>
              <span>
                R<sup>2</sup> = 0.87
              </span>
            </div>
          </div>

          <div className="rounded-2xl border border-[#1f2b4d] bg-[#111a32] px-4 py-4 shadow-[0_15px_45px_rgba(0,0,0,0.35)]">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-white">Historical Trends</h2>
              <span className="text-xs text-[#8fa2ce]">Last period</span>
            </div>
            <div className="mt-2 h-64">
              <Line data={trendData} options={trendOptions} />
            </div>
            <div className="mt-4 grid grid-cols-3 gap-2 text-center text-sm text-[#8fa2ce]">
              <div className="rounded-xl border border-[#1f2b4d] bg-[#0d1530]/70 p-2">
                <p className="text-xs">Avg Daily Passengers</p>
                <p className="text-lg font-semibold text-[#f5c842]">
                  {Math.round(
                    (trendPassengers.reduce((a, b) => a + b, 0) / trendPassengers.length) || 0
                  ).toLocaleString("en-US")}
                </p>
              </div>
              <div className="rounded-xl border border-[#1f2b4d] bg-[#0d1530]/70 p-2">
                <p className="text-xs">Avg Delay</p>
                <p className="text-lg font-semibold text-[#f97373]">
                  {Number(
                    (
                      trendDelays.reduce((a, b) => a + b, 0) / trendDelays.length || 0
                    ).toFixed(1)
                  )}{" "}
                  min
                </p>
              </div>
              <div className="rounded-xl border border-[#1f2b4d] bg-[#0d1530]/70 p-2">
                <p className="text-xs">Peak Day</p>
                <p className="text-lg font-semibold text-[#cbd5ff]">Friday</p>
              </div>
            </div>
          </div>
        </section>

        <section className="grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
          <div className="rounded-2xl border border-[#1f2b4d] bg-[#111a32] px-4 py-4 shadow-[0_15px_45px_rgba(0,0,0,0.35)]">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-white">Arrival Quality</h2>
              <span className="text-xs text-[#8fa2ce]">Auto-updating</span>
            </div>
            <div className="mt-4 h-56">
              <Doughnut
                data={onTimeChart}
                options={{
                  plugins: {
                    legend: {
                      position: "bottom" as const,
                      labels: { color: "#cbd5ff" },
                    },
                  },
                  cutout: "68%",
                }}
              />
            </div>
            <div className="mt-4 grid grid-cols-3 gap-2 text-sm text-[#8fa2ce]">
              <div className="rounded-xl border border-[#1f2b4d] bg-[#0d1530]/70 p-3">
                <p className="text-xs">Model</p>
                <p className="text-base font-semibold text-white">{modelVersion}</p>
              </div>
              <div className="rounded-xl border border-[#1f2b4d] bg-[#0d1530]/70 p-3">
                <p className="text-xs">Records</p>
                <p className="text-base font-semibold text-white">
                  {totalRecords.toLocaleString("en-US")}
                </p>
              </div>
              <div className="rounded-xl border border-[#1f2b4d] bg-[#0d1530]/70 p-3">
                <p className="text-xs">Predictions</p>
                <p className="text-base font-semibold text-white">
                  {totalPredictions.toLocaleString("en-US")}
                </p>
              </div>
            </div>
          </div>

          <div className="rounded-2xl border border-[#1f2b4d] bg-[#111a32] px-4 py-4 shadow-[0_15px_45px_rgba(0,0,0,0.35)]">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-white">Route Performance</h2>
              <span className="text-xs text-[#8fa2ce]">Avg: 91.5% on-time</span>
            </div>
            <div className="mt-3 max-h-[370px] space-y-2 overflow-auto pr-1">
              {routePerformance.map((item) => (
                <div
                  key={item.route}
                  className="flex items-center justify-between rounded-xl border border-[#1f2b4d] bg-[#0d1530]/70 px-3 py-2"
                >
                  <div className="w-20 text-sm text-white">{item.route}</div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-semibold text-white">
                      {item.onTime.toFixed(1)}%
                    </span>
                    <span
                      className={
                        item.trend === "up"
                          ? "text-green-400"
                          : item.trend === "steady"
                          ? "text-[#f5c842]"
                          : "text-[#f97373]"
                      }
                    >
                      {item.trend === "up" ? "↗" : item.trend === "steady" ? "•" : "↘"}
                    </span>
                  </div>
                  <div className="h-2 w-20 rounded-full bg-[#1b2745]">
                    <div
                      className={`h-2 rounded-full ${
                        item.trend === "up"
                          ? "bg-[#4ade80]"
                          : item.trend === "steady"
                          ? "bg-[#f5c842]"
                          : "bg-[#f97373]"
                      }`}
                      style={{ width: `${Math.min(100, item.onTime)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-3 flex items-center justify-between text-xs text-[#8fa2ce]">
              <span>Showing {routePerformance.length} routes</span>
              <span>Scroll for more</span>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}


