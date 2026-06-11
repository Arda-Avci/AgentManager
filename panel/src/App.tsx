import { Link, Route, Routes, useLocation } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import AgentCreator from "./pages/AgentCreator";
import LogStream from "./pages/LogStream";
import Landing from "./pages/Landing";

export default function App() {
  const location = useLocation();
  const isLanding = location.pathname === "/";

  if (isLanding) {
    return (
      <Routes>
        <Route path="/" element={<Landing />} />
      </Routes>
    );
  }

  return (
    <div className="app-layout">
      <nav className="sidebar">
        <div className="sidebar-header">
          <h2>AgentManager</h2>
        </div>
        <ul className="sidebar-nav">
          <li>
            <Link to="/">Landing Page</Link>
          </li>
          <li>
            <Link to="/dashboard">Dashboard</Link>
          </li>
          <li>
            <Link to="/create">Create Agent</Link>
          </li>
          <li>
            <Link to="/logs">Log Stream</Link>
          </li>
        </ul>
      </nav>
      <main className="main-content">
        <Routes>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/create" element={<AgentCreator />} />
          <Route path="/logs" element={<LogStream />} />
        </Routes>
      </main>
    </div>
  );
}

