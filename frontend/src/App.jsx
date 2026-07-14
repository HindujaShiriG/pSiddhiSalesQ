import { NavLink, Route, Routes } from "react-router-dom";
import PipelineOverview from "./screens/PipelineOverview.jsx";
import AccountDetail from "./screens/AccountDetail.jsx";

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
        <a className="soon">Rep Performance · Wk 11</a>
        <a className="soon">AI Intelligence · Wk 12</a>
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
        </Routes>
      </main>
    </div>
  );
}
