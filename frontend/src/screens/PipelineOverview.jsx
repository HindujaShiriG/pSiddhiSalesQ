import { useEffect, useState } from "react";
import {
  Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";
import { api } from "../api/client.js";
import { ErrorState, Kpi, Loading, inr } from "../components/common.jsx";

const STAGE_ORDER = [
  "Prospecting", "Qualification", "Proposal", "Negotiation", "Closed Won", "Closed Lost",
];

export default function PipelineOverview() {
  const [data, setData] = useState(null);
  const [deals, setDeals] = useState([]);
  const [error, setError] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  async function load() {
    try {
      setError(null);
      const [overview, dealList] = await Promise.all([api.pipelineOverview(), api.deals()]);
      setData(overview);
      setDeals(dealList);
    } catch (e) {
      setError(e);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function handleRefresh() {
    setRefreshing(true);
    try {
      await api.refresh();
      await load();
    } catch (e) {
      setError(e);
    } finally {
      setRefreshing(false);
    }
  }

  if (error) return <ErrorState error={error} />;
  if (!data) return <Loading what="pipeline" />;

  const chartData = [...data.stages]
    .sort((a, b) => STAGE_ORDER.indexOf(a.stage) - STAGE_ORDER.indexOf(b.stage))
    .map((s) => ({
      stage: s.stage,
      "Stage-weighted": Math.round(s.weighted_amount),
      "ML-weighted": Math.round(s.ml_weighted_amount || 0),
    }));

  return (
    <>
      <div className="toolbar">
        <div>
          <h1 className="page-title">Pipeline Overview</h1>
          <p className="page-sub">Live view of the unified pipeline — stage-weighted vs ML forecast</p>
        </div>
        <button className="btn" onClick={handleRefresh} disabled={refreshing}>
          {refreshing ? "Refreshing…" : "↻ Refresh data + ML"}
        </button>
      </div>

      <div className="kpi-row">
        <Kpi label="Open deals" value={data.open_deals} sub={`${data.total_deals} total`} />
        <Kpi label="Open pipeline value" value={inr(data.total_pipeline_value)} />
        <Kpi label="Stage-weighted forecast" value={inr(data.stage_weighted_forecast)} sub="naive baseline" />
        <Kpi
          label="ML forecast"
          value={data.ml_forecast != null ? inr(data.ml_forecast) : "—"}
          sub={data.ml_forecast != null ? "win-prob adjusted" : "train models to populate"}
        />
      </div>

      <div className="grid-2">
        <div className="card">
          <h3>Forecast by stage — stage-weighted vs ML</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData} margin={{ top: 8, right: 8, left: 8, bottom: 8 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2c3547" />
              <XAxis dataKey="stage" tick={{ fontSize: 11, fill: "#9aa7bd" }} interval={0} angle={-18} height={50} textAnchor="end" />
              <YAxis tick={{ fontSize: 11, fill: "#9aa7bd" }} tickFormatter={(v) => `${(v / 100000).toFixed(0)}L`} />
              <Tooltip formatter={(v) => inr(v)} contentStyle={{ background: "#1a2130", border: "1px solid #2c3547" }} />
              <Legend wrapperStyle={{ fontSize: 12 }} />
              <Bar dataKey="Stage-weighted" fill="#6b7a99" radius={[4, 4, 0, 0]} />
              <Bar dataKey="ML-weighted" fill="#4f8cff" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h3>Top deals by expected revenue</h3>
          <table>
            <thead>
              <tr>
                <th>Deal</th>
                <th>Stage</th>
                <th>Win %</th>
                <th>Expected</th>
              </tr>
            </thead>
            <tbody>
              {deals.slice(0, 10).map((d) => (
                <tr key={d.deal_id}>
                  <td>{d.deal_id}</td>
                  <td>{d.stage}</td>
                  <td>{d.predicted_win_prob != null ? `${Math.round(d.predicted_win_prob * 100)}%` : "—"}</td>
                  <td>{d.predicted_revenue != null ? inr(d.predicted_revenue) : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
