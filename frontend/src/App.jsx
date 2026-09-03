import { NavLink, Route, Routes } from "react-router-dom";
import PipelineOverview from "./screens/PipelineOverview.jsx";
import AccountDetail from "./screens/AccountDetail.jsx";
import RepPerformance from "./screens/RepPerformance.jsx";
import AIIntelligence from "./screens/AIIntelligence.jsx";

function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="brand">Sales<span>IQ</span></div>
      <div className="tagline">Unified Sales Operations</div>
      <nav className="nav">
        <NavLink to="/" end className={({ isActive }) => (isActive ? "active" : "")}>
          Pipeline Overview
        </NavLink>
        <NavLink to="/accounts" className={({ isActive }) => (isActive ? "active" : "")}>
          Account Detail
        </NavLink>
        <NavLink to="/reps" className={({ isActive }) => (isActive ? "active" : "")}>
          Rep Performance
        </NavLink>
        <NavLink to="/intelligence" className={({ isActive }) => (isActive ? "active" : "")}>
          AI Intelligence
        </NavLink>
      </nav>
    </aside>
  );
}

export default function App() {
  return (
    <div className="app">
      <Sidebar />
      <main className="main">
        <Routes>
          <Route path="/" element={<PipelineOverview />} />
          <Route path="/accounts" element={<AccountDetail />} />
          <Route path="/accounts/:accountId" element={<AccountDetail />} />
          <Route path="/reps" element={<RepPerformance />} />
          <Route path="/intelligence" element={<AIIntelligence />} />
        </Routes>
      </main>
    </div>
  );
}
