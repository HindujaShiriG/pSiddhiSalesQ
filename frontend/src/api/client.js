// Thin fetch wrapper. All calls go through the Vite proxy to the FastAPI backend.
const BASE = "/api";

async function get(path) {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`GET ${path} -> ${res.status}`);
  return res.json();
}

async function post(path) {
  const res = await fetch(`${BASE}${path}`, { method: "POST" });
  if (!res.ok) throw new Error(`POST ${path} -> ${res.status}`);
  return res.json();
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
