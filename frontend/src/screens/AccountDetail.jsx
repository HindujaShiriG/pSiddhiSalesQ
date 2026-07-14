import { useEffect, useState } from "react";
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import { api } from "../api/client.js";
import { ErrorState, Kpi, Loading, inr } from "../components/common.jsx";

const BAND_COLOR = { Healthy: "#35c48a", "At-Risk": "#f2b03d", Critical: "#f2685a" };

export default function AccountDetail() {
  const [accounts, setAccounts] = useState([]);
  const [selected, setSelected] = useState(null);
  const [detail, setDetail] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.accounts().then((list) => {
      setAccounts(list);
      if (list.length) setSelected(list[0].account_id);
    }).catch(setError);
  }, []);

  useEffect(() => {
    if (!selected) return;
    setDetail(null);
    api.accountDetail(selected).then(setDetail).catch(setError);
  }, [selected]);

  if (error) return <ErrorState error={error} />;
  if (!accounts.length) return <Loading what="accounts" />;

  const bandCounts = accounts.reduce((acc, a) => {
    acc[a.health_band] = (acc[a.health_band] || 0) + 1;
    return acc;
  }, {});
  const pieData = Object.entries(bandCounts).map(([name, value]) => ({ name, value }));

  return (
    <>
      <div className="toolbar">
        <div>
          <h1 className="page-title">Account Detail</h1>
          <p className="page-sub">Account-health signals + open pipeline per account</p>
        </div>
        <select className="btn" value={selected || ""} onChange={(e) => setSelected(e.target.value)}>
          {accounts.map((a) => (
            <option key={a.account_id} value={a.account_id}>
              {a.name} ({a.health_band})
            </option>
          ))}
        </select>
      </div>

      {!detail ? (
        <Loading what="account" />
      ) : (
        <>
          <div className="kpi-row">
            <Kpi label="Account" value={detail.account.name} sub={`${detail.account.industry} · ${detail.account.segment}`} />
            <Kpi label="ARR" value={inr(detail.account.arr)} />
            <Kpi
              label="Health"
              value={detail.account.health_band}
              sub={`risk ${Math.round(detail.account.risk_score * 100)}% · renews in ${detail.account.days_to_renewal}d`}
            />
            <Kpi label="Open pipeline" value={inr(detail.open_pipeline_value)} sub={`${detail.deals.length} deals`} />
          </div>

          <div className="grid-2">
            <div className="card">
              <h3>Open & recent deals</h3>
              <table>
                <thead>
                  <tr>
                    <th>Deal</th>
                    <th>Stage</th>
                    <th>Amount</th>
                    <th>Win %</th>
                    <th>Age</th>
                  </tr>
                </thead>
                <tbody>
                  {detail.deals.map((d) => (
                    <tr key={d.deal_id}>
                      <td>{d.deal_id}</td>
                      <td>{d.stage}{d.is_stalled ? " ⚠" : ""}</td>
                      <td>{inr(d.amount)}</td>
                      <td>{d.predicted_win_prob != null ? `${Math.round(d.predicted_win_prob * 100)}%` : "—"}</td>
                      <td>{d.age_days}d</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="card">
              <h3>Portfolio health mix</h3>
              <ResponsiveContainer width="100%" height={260}>
                <PieChart>
                  <Pie data={pieData} dataKey="value" nameKey="name" outerRadius={90} label>
                    {pieData.map((entry) => (
                      <Cell key={entry.name} fill={BAND_COLOR[entry.name] || "#6b7a99"} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ background: "#1a2130", border: "1px solid #2c3547" }} />
                </PieChart>
              </ResponsiveContainer>
              <div style={{ display: "flex", gap: 14, justifyContent: "center", fontSize: 12 }}>
                {pieData.map((p) => (
                  <span key={p.name}>
                    <span className={`badge ${p.name}`}>{p.name}</span> {p.value}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </>
      )}
    </>
  );
}
