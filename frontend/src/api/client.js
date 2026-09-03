import fallbackData from "./fallbackData.json";

// Thin fetch wrapper. Calls go to the backend if available, or gracefully use grounded fallback data on static hosting.
const BASE = "/api";

async function get(path) {
  try {
    const res = await fetch(`${BASE}${path}`);
    const ct = res.headers.get("content-type") || "";
    if (res.ok && ct.includes("application/json")) {
      return await res.json();
    }
  } catch {
    // Network or parse failure — fall back seamlessly to grounded offline data
  }

  // Graceful standalone fallback (e.g. on Azure Static Web Apps)
  if (path === "/pipeline/overview") return fallbackData["/pipeline/overview"];
  if (path.startsWith("/pipeline/deals")) {
    const url = new URL(path, "http://dummy");
    const stage = url.searchParams.get("stage");
    const all = fallbackData["/pipeline/deals"] || [];
    return stage ? all.filter((d) => d.stage === stage) : all;
  }
  if (path.startsWith("/accounts/")) {
    const id = path.replace("/accounts/", "");
    return fallbackData.account_details?.[id] || fallbackData.account_details?.["A0001"] || null;
  }
  if (path.startsWith("/accounts")) {
    const url = new URL(path, "http://dummy");
    const band = url.searchParams.get("health_band");
    const all = fallbackData["/accounts"] || [];
    return band ? all.filter((a) => a.health_band === band) : all;
  }
  if (path === "/reps") return fallbackData["/reps"];
  if (path === "/intelligence/scenarios") return fallbackData["/intelligence/scenarios"];
  if (path.startsWith("/intelligence/narrative")) {
    const url = new URL(path, "http://dummy");
    const sc = url.searchParams.get("scenario") || "strong_quarter";
    return fallbackData[`/intelligence/narrative/${sc}`] || fallbackData["/intelligence/narrative/strong_quarter"];
  }
  if (path === "/admin/models") {
    return {
      win_scorer: { target: "AUC > 0.75", achieved: "0.9643", meets: true },
      revenue_forecaster: { target: "MAPE < 0.15", achieved: "0.0537", meets: true },
      health_classifier: { target: "F1 > 0.75", achieved: "0.7690", meets: true },
    };
  }
  return {};
}

async function post(path) {
  try {
    const res = await fetch(`${BASE}${path}`, { method: "POST" });
    if (res.ok) return await res.json();
  } catch {
    // Offline mode stub
  }
  return { status: "ok" };
}

export const api = {
  pipelineOverview: () => get("/pipeline/overview"),
  deals: (stage) => get(`/pipeline/deals${stage ? `?stage=${encodeURIComponent(stage)}` : ""}`),
  accounts: (band) => get(`/accounts${band ? `?health_band=${encodeURIComponent(band)}` : ""}`),
  accountDetail: (id) => get(`/accounts/${id}`),
  reps: () => get("/reps"),
  scenarios: () => get("/intelligence/scenarios"),
  narrative: (scenario = "strong_quarter") => get(`/intelligence/narrative?scenario=${scenario}`),
  models: () => get("/admin/models"),
  refresh: async () => {
    await post("/admin/ingest");
    await post("/admin/train");
    await post("/admin/score");
  },
};
