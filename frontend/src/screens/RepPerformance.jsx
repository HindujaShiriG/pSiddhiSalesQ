import { useEffect, useState, useMemo } from "react";
import {
  Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis, ReferenceLine,
} from "recharts";
import { api } from "../api/client.js";
import { ErrorState, Kpi, Loading, inr } from "../components/common.jsx";

export default function RepPerformance() {
  const [reps, setReps] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [regionFilter, setRegionFilter] = useState("ALL");
  const [segmentFilter, setSegmentFilter] = useState("ALL");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedRep, setSelectedRep] = useState(null);

  async function load() {
    try {
      setError(null);
      const data = await api.reps();
      setReps(data);
      if (data.length > 0) setSelectedRep(data[0]);
    } catch (e) {
      setError(e);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  const filteredReps = useMemo(() => {
    return reps.filter((r) => {
      const matchRegion = regionFilter === "ALL" || r.region === regionFilter;
      const matchSegment = segmentFilter === "ALL" || r.segment === segmentFilter;
      const matchSearch =
        !searchQuery ||
        r.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        r.rep_id.toLowerCase().includes(searchQuery.toLowerCase());
      return matchRegion && matchSegment && matchSearch;
    });
  }, [reps, regionFilter, segmentFilter, searchQuery]);

  const stats = useMemo(() => {
    if (!reps.length) return null;
    const totalReps = reps.length;
    const avgAttainment =
      reps.reduce((acc, r) => acc + (r.attainment_pct || 0), 0) / totalReps;
    const avgWinRate =
      reps.reduce((acc, r) => acc + (r.historical_win_rate || 0), 0) / totalReps;
    const avgCycle =
      reps.reduce((acc, r) => acc + (r.avg_deal_cycle_days || 0), 0) / totalReps;
    const overachievers = reps.filter((r) => (r.attainment_pct || 0) >= 1.0).length;

    return {
      totalReps,
      avgAttainment: Math.round(avgAttainment * 100),
      avgWinRate: Math.round(avgWinRate * 100),
      avgCycle: Math.round(avgCycle),
      overachievers,
    };
  }, [reps]);

  // Top 10 reps by attainment for the chart
  const attainmentChartData = useMemo(() => {
    return [...filteredReps]
      .sort((a, b) => b.attainment_pct - a.attainment_pct)
      .slice(0, 10)
      .map((r) => ({
        name: r.name.split(" ")[0],
        attainment: Math.round(r.attainment_pct * 100),
        winRate: Math.round(r.historical_win_rate * 100),
      }));
  }, [filteredReps]);

  // Efficiency breakdown (Win Rate vs Deal Cycle)
  const efficiencyChartData = useMemo(() => {
    return [...filteredReps]
      .sort((a, b) => b.historical_win_rate - a.historical_win_rate)
      .slice(0, 10)
      .map((r) => ({
        name: r.name.split(" ")[0],
        "Win Rate (%)": Math.round(r.historical_win_rate * 100),
        "Cycle (days)": r.avg_deal_cycle_days,
      }));
  }, [filteredReps]);

  if (error) return <ErrorState error={error} />;
  if (loading) return <Loading what="rep performance analytics" />;

  const getStatusBadge = (attainment) => {
    if (attainment >= 1.0) {
      return <span className="badge Healthy">President's Club ({Math.round(attainment * 100)}%)</span>;
    }
    if (attainment >= 0.75) {
      return <span className="badge" style={{ background: "rgba(79,140,255,0.15)", color: "var(--accent)" }}>On Track ({Math.round(attainment * 100)}%)</span>;
    }
    return <span className="badge At-Risk">Needs Coaching ({Math.round(attainment * 100)}%)</span>;
  };

  return (
    <>
      <div className="toolbar">
        <div>
          <h1 className="page-title">Rep Performance & Coaching</h1>
          <p className="page-sub">
            Sales rep quota attainment, historical win rates, velocity benchmarks, and cross-domain signal
          </p>
        </div>
      </div>

      {stats && (
        <div className="kpi-row">
          <Kpi label="Active Sales Reps" value={stats.totalReps} sub={`${stats.overachievers} over 100% quota`} />
          <Kpi label="Team Avg Attainment" value={`${stats.avgAttainment}%`} sub="Target: ≥85%" />
          <Kpi label="Historical Win Rate" value={`${stats.avgWinRate}%`} sub="Cross-domain ML feature" />
          <Kpi label="Avg Deal Cycle" value={`${stats.avgCycle} days`} sub="From creation to close" />
        </div>
      )}

      {/* Filter Controls */}
      <div className="card filter-bar" style={{ marginBottom: 20 }}>
        <div style={{ display: "flex", gap: 14, flexWrap: "wrap", alignItems: "center" }}>
          <div style={{ flex: 1, minWidth: 200 }}>
            <input
              type="text"
              placeholder="Search rep name or ID…"
              className="search-input"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <span style={{ fontSize: 12, color: "var(--muted)" }}>Region:</span>
            {["ALL", "North", "South", "East", "West"].map((reg) => (
              <button
                key={reg}
                className={`filter-pill ${regionFilter === reg ? "active" : ""}`}
                onClick={() => setRegionFilter(reg)}
              >
                {reg}
              </button>
            ))}
          </div>
          <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <span style={{ fontSize: 12, color: "var(--muted)" }}>Segment:</span>
            {["ALL", "Enterprise", "Mid-Market", "SMB"].map((seg) => (
              <button
                key={seg}
                className={`filter-pill ${segmentFilter === seg ? "active" : ""}`}
                onClick={() => setSegmentFilter(seg)}
              >
                {seg}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Visual Analytics */}
      <div className="grid-2" style={{ marginBottom: 24 }}>
        <div className="card">
          <h3>Quota Attainment (%) — Top Reps</h3>
          <p style={{ fontSize: 12, color: "var(--muted)", margin: "-6px 0 12px" }}>
            Dashed line represents 100% quota baseline
          </p>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={attainmentChartData} margin={{ top: 12, right: 12, left: 0, bottom: 8 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2c3547" />
              <XAxis dataKey="name" tick={{ fontSize: 11, fill: "#9aa7bd" }} />
              <YAxis tick={{ fontSize: 11, fill: "#9aa7bd" }} unit="%" />
              <Tooltip
                formatter={(val) => [`${val}%`, "Attainment"]}
                contentStyle={{ background: "#1a2130", border: "1px solid #2c3547" }}
              />
              <ReferenceLine y={100} stroke="#35c48a" strokeDasharray="4 4" label={{ value: "Quota", fill: "#35c48a", fontSize: 11 }} />
              <Bar dataKey="attainment" fill="#4f8cff" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h3>Win Rate vs Deal Velocity</h3>
          <p style={{ fontSize: 12, color: "var(--muted)", margin: "-6px 0 12px" }}>
            Comparing historical win conversion vs average cycle duration (days)
          </p>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={efficiencyChartData} margin={{ top: 12, right: 12, left: 0, bottom: 8 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2c3547" />
              <XAxis dataKey="name" tick={{ fontSize: 11, fill: "#9aa7bd" }} />
              <YAxis tick={{ fontSize: 11, fill: "#9aa7bd" }} />
              <Tooltip contentStyle={{ background: "#1a2130", border: "1px solid #2c3547" }} />
              <Legend wrapperStyle={{ fontSize: 12 }} />
              <Bar dataKey="Win Rate (%)" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
              <Bar dataKey="Cycle (days)" fill="#f2b03d" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Rep Leaderboard Table */}
      <div className="card">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
          <h3>Rep Roster & Operational Benchmarks ({filteredReps.length} reps)</h3>
        </div>
        <table>
          <thead>
            <tr>
              <th>Rep Name</th>
              <th>Region</th>
              <th>Segment</th>
              <th>Quota</th>
              <th>Attainment</th>
              <th>Win Rate</th>
              <th>30d Activity</th>
              <th>Avg Cycle</th>
              <th>Coaching Signal</th>
            </tr>
          </thead>
          <tbody>
            {filteredReps.map((r) => (
              <tr
                key={r.rep_id}
                onClick={() => setSelectedRep(r)}
                style={{ cursor: "pointer", background: selectedRep?.rep_id === r.rep_id ? "var(--panel-2)" : undefined }}
              >
                <td>
                  <strong>{r.name}</strong>
                  <div style={{ fontSize: 11, color: "var(--muted)" }}>{r.rep_id}</div>
                </td>
                <td>{r.region}</td>
                <td>{r.segment}</td>
                <td>{inr(r.quota)}</td>
                <td>
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <div style={{ width: 60, height: 6, background: "#2c3547", borderRadius: 3, overflow: "hidden" }}>
                      <div
                        style={{
                          width: `${Math.min(100, r.attainment_pct * 100)}%`,
                          height: "100%",
                          background: r.attainment_pct >= 1.0 ? "var(--good)" : r.attainment_pct >= 0.75 ? "var(--accent)" : "var(--warn)",
                        }}
                      />
                    </div>
                    <span>{Math.round(r.attainment_pct * 100)}%</span>
                  </div>
                </td>
                <td>{Math.round(r.historical_win_rate * 100)}%</td>
                <td>{r.activities_last_30d} touches</td>
                <td>{r.avg_deal_cycle_days} days</td>
                <td>{getStatusBadge(r.attainment_pct)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
