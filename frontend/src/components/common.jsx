export function Kpi({ label, value, sub }) {
  return (
    <div className="card">
      <div className="kpi-label">{label}</div>
      <div className="kpi-value">{value}</div>
      {sub && <div className="kpi-sub">{sub}</div>}
    </div>
  );
}

export function Loading({ what = "data" }) {
  return <div className="state">Loading {what}…</div>;
}

export function ErrorState({ error }) {
  return (
    <div className="state">
      Could not load data.
      <br />
      <small>{String(error?.message || error)}</small>
      <br />
      <small>Is the backend running (uvicorn on :8000) and data ingested?</small>
    </div>
  );
}

export const inr = (n) =>
  "₹" + Math.round(Number(n) || 0).toLocaleString("en-IN");
