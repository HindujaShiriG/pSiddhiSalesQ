import { useEffect, useState } from "react";
import { api } from "../api/client.js";
import { ErrorState, Kpi, Loading, inr } from "../components/common.jsx";

const SCENARIO_META = {
  strong_quarter: {
    title: "Strong Quarter",
    tagline: "Momentum & Upside Execution",
    badgeColor: "var(--good)",
    badgeBg: "rgba(53,196,138,0.15)",
    summary: "Capitalize on high win-rate opportunities, identify expansion accounts, and commit to stretch targets.",
    icon: "📈",
  },
  at_risk_quarter: {
    title: "At-Risk Quarter",
    tagline: "Risk Mitigation & Churn Defense",
    badgeColor: "var(--warn)",
    badgeBg: "rgba(242,176,61,0.15)",
    summary: "Mitigate pipeline slippage, intervene on stalled opportunities, and safeguard high-risk renewals.",
    icon: "⚠️",
  },
  recovery: {
    title: "Recovery Scenario",
    tagline: "Deal Triage & Rep Coaching",
    badgeColor: "var(--bad)",
    badgeBg: "rgba(242,104,90,0.15)",
    summary: "Execute emergency pipeline triage, pair senior reps on critical deals, and fast-track quick-win closes.",
    icon: "🔄",
  },
};

export default function AIIntelligence() {
  const [scenario, setScenario] = useState("strong_quarter");
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [regenerating, setRegenerating] = useState(false);

  async function loadScenario(scen) {
    try {
      setError(null);
      setLoading(true);
      const res = await api.narrative(scen);
      setData(res);
    } catch (e) {
      setError(e);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadScenario(scenario);
  }, [scenario]);

  async function handleRegenerate() {
    setRegenerating(true);
    try {
      await api.refresh();
      await loadScenario(scenario);
    } catch (e) {
      setError(e);
    } finally {
      setRegenerating(false);
    }
  }

  const currentMeta = SCENARIO_META[scenario] || SCENARIO_META.strong_quarter;
  const brief = data?.brief;

  return (
    <>
      <div className="toolbar">
        <div>
          <h1 className="page-title">AI Sales Intelligence</h1>
          <p className="page-sub">
            AI/ML core engine generating scenario-grounded executive narratives, pipeline risk detection, and retention plays
          </p>
        </div>
        <button className="btn" onClick={handleRegenerate} disabled={regenerating || loading}>
          {regenerating ? "Regenerating…" : "✨ Re-run AI & Refresh"}
        </button>
      </div>

      {/* Scenario Selector Tabs */}
      <div className="scenario-tabs-container card" style={{ padding: 8, marginBottom: 20 }}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 8 }}>
          {Object.entries(SCENARIO_META).map(([key, meta]) => {
            const isActive = scenario === key;
            return (
              <button
                key={key}
                className={`scenario-tab ${isActive ? "active" : ""}`}
                onClick={() => setScenario(key)}
                style={{
                  padding: "12px 16px",
                  background: isActive ? "var(--panel-2)" : "transparent",
                  border: isActive ? `1px solid ${meta.badgeColor}` : "1px solid transparent",
                  borderRadius: 8,
                  cursor: "pointer",
                  textAlign: "left",
                  color: "inherit",
                  transition: "all 0.2s ease",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
                  <span style={{ fontSize: 16 }}>{meta.icon}</span>
                  <strong style={{ fontSize: 14 }}>{meta.title}</strong>
                </div>
                <div style={{ fontSize: 11, color: "var(--muted)" }}>{meta.tagline}</div>
              </button>
            );
          })}
        </div>
      </div>

      {loading ? (
        <Loading what={`${currentMeta.title} narrative & ML inference`} />
      ) : error ? (
        <ErrorState error={error} />
      ) : (
        <>
          {/* Grounded Metrics Banner */}
          {brief && (
            <div className="kpi-row">
              <Kpi
                label="Open Deals"
                value={brief.open_deals}
                sub={`₹${(brief.total_pipeline_value / 10000000).toFixed(2)} Cr pipeline`}
              />
              <Kpi
                label="ML Revenue Forecast"
                value={inr(brief.ml_forecast)}
                sub={`vs stage-weighted ${inr(brief.stage_weighted_forecast)}`}
              />
              <Kpi
                label="Stalled Deals"
                value={brief.stalled_deals}
                sub={brief.stalled_deals > 0 ? "Immediate triage required" : "Pipeline healthy"}
              />
              <Kpi
                label="At-Risk Accounts"
                value={brief.at_risk_accounts?.length || 0}
                sub="Critical/At-Risk health band"
              />
            </div>
          )}

          {/* AI Narrative Main Card */}
          <div className="card" style={{ marginBottom: 24, borderLeft: `4px solid ${currentMeta.badgeColor}` }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16, borderBottom: "1px solid var(--border)", paddingBottom: 12 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <span
                  style={{
                    display: "inline-block",
                    padding: "3px 10px",
                    borderRadius: 16,
                    fontSize: 12,
                    fontWeight: 600,
                    background: currentMeta.badgeBg,
                    color: currentMeta.badgeColor,
                  }}
                >
                  {currentMeta.title} Mode
                </span>
                <span style={{ fontSize: 12, color: "var(--muted)" }}>
                  Inference Source:{" "}
                  <strong style={{ color: data.source === "gemini" ? "var(--good)" : "var(--accent)" }}>
                    {data.source === "gemini" ? "Google Gemini 2.5 Flash" : "Grounded ML Narrative Engine (Deterministic Fallback)"}
                  </strong>
                </span>
              </div>
              <span style={{ fontSize: 11, color: "var(--muted)" }}>RFP S4-I-21 Requirement</span>
            </div>

            <div className="narrative" style={{ fontSize: 14, lineHeight: 1.65, whiteSpace: "pre-wrap", color: "var(--text)" }}>
              {data.narrative}
            </div>
          </div>

          {/* Actionable Callouts Grid */}
          <div className="grid-2">
            {/* Top Pipeline Opportunities */}
            <div className="card">
              <h3>Priority Focus Opportunities ({brief?.top_deals?.length || 0})</h3>
              <p style={{ fontSize: 12, color: "var(--muted)", margin: "-6px 0 12px" }}>
                Highest expected value deals ranked by ML Win Probability × Predicted Revenue
              </p>
              <table>
                <thead>
                  <tr>
                    <th>Deal / Account</th>
                    <th>Stage</th>
                    <th>Win Prob</th>
                    <th>Expected</th>
                  </tr>
                </thead>
                <tbody>
                  {brief?.top_deals?.map((d) => (
                    <tr key={d.deal_id}>
                      <td>
                        <strong>{d.account}</strong>
                        <div style={{ fontSize: 11, color: "var(--muted)" }}>{d.deal_id}</div>
                      </td>
                      <td>
                        <span className="badge" style={{ background: "var(--panel-2)", color: "var(--text)" }}>
                          {d.stage}
                        </span>
                      </td>
                      <td>
                        <strong style={{ color: (d.win_prob || 0) >= 0.6 ? "var(--good)" : "var(--warn)" }}>
                          {Math.round((d.win_prob || 0) * 100)}%
                        </strong>
                      </td>
                      <td>{inr(d.expected_revenue)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Account Churn Watchlist */}
            <div className="card">
              <h3>Account Churn Watchlist ({brief?.at_risk_accounts?.length || 0})</h3>
              <p style={{ fontSize: 12, color: "var(--muted)", margin: "-6px 0 12px" }}>
                Accounts flagged by the ML Account Health Classifier as requiring retention intervention
              </p>
              <table>
                <thead>
                  <tr>
                    <th>Account</th>
                    <th>Health Band</th>
                    <th>Risk</th>
                    <th>Renewal In</th>
                  </tr>
                </thead>
                <tbody>
                  {brief?.at_risk_accounts?.map((a) => (
                    <tr key={a.account_id}>
                      <td>
                        <strong>{a.name}</strong>
                        <div style={{ fontSize: 11, color: "var(--muted)" }}>{a.account_id}</div>
                      </td>
                      <td>
                        <span className={`badge ${a.band}`}>{a.band}</span>
                      </td>
                      <td>
                        <strong style={{ color: a.risk_score >= 0.65 ? "var(--bad)" : "var(--warn)" }}>
                          {Math.round(a.risk_score * 100)}%
                        </strong>
                      </td>
                      <td>{a.days_to_renewal} days</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </>
  );
}
