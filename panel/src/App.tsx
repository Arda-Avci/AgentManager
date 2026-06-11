import { Link, Route, Routes } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import AgentCreator from "./pages/AgentCreator";
import LogStream from "./pages/LogStream";

export default function App() {
  return (
    <div className="app-layout">
      <nav className="sidebar">
        <div className="sidebar-header">
          <h2>AgentManager</h2>
        </div>
        <ul className="sidebar-nav">
          <li>
            <Link to="/">Dashboard</Link>
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
          <Route path="/" element={<Dashboard />} />
          <Route path="/create" element={<AgentCreator />} />
          <Route path="/logs" element={<LogStream />} />
        </Routes>
      </main>
    </div>
  );
}
