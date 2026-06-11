import { useEffect, useState } from "react";
import { api, type Agent } from "../api/client";

const statusColor: Record<string, string> = {
  idle: "#6b7280",
  busy: "#3b82f6",
  paused: "#f59e0b",
  error: "#ef4444",
};

export default function Dashboard() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .listAgents()
      .then(setAgents)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  const handleDelete = async (id: string, name: string) => {
    if (!confirm(`Delete agent "${name}"?`)) return;
    try {
      await api.deleteAgent(id);
      setAgents((prev) => prev.filter((a) => a.id !== id));
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Delete failed");
    }
  };

  if (loading) return <div className="loading">Loading agents...</div>;

  return (
    <div>
      <h1>Agent Dashboard</h1>
      {error && <div className="error-banner">{error}</div>}

      {agents.length === 0 ? (
        <div className="empty-state">
          <p>No agents yet.</p>
          <a href="/create">Create your first agent →</a>
        </div>
      ) : (
        <div className="agent-grid">
          {agents.map((agent) => (
            <div key={agent.id} className="agent-card">
              <div className="agent-card-header">
                <span
                  className="status-dot"
                  style={{ backgroundColor: statusColor[agent.status] || "#6b7280" }}
                />
                <strong>{agent.name}</strong>
              </div>
              <div className="agent-card-body">
                <div className="agent-detail">
                  <span className="label">Role</span>
                  <span>{agent.role}</span>
                </div>
                <div className="agent-detail">
                  <span className="label">Status</span>
                  <span className={`status-badge ${agent.status}`}>{agent.status}</span>
                </div>
                <div className="agent-detail">
                  <span className="label">Provider</span>
                  <span>{agent.provider}</span>
                </div>
                <div className="agent-detail">
                  <span className="label">Model</span>
                  <span>{agent.model}</span>
                </div>
                <div className="agent-detail">
                  <span className="label">Created</span>
                  <span>{new Date(agent.created_at).toLocaleDateString()}</span>
                </div>
              </div>
              <div className="agent-card-actions">
                <button
                  className="btn btn-danger"
                  onClick={() => handleDelete(agent.id, agent.name)}
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
