import { useEffect, useRef, useState } from "react";
import { api, type Agent } from "../api/client";
import { connectLogStream } from "../api/ws";

interface LogEntry {
  time: string;
  event: string;
  data: string;
}

export default function LogStream() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [selectedAgent, setSelectedAgent] = useState<string>("");
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    api.listAgents().then(setAgents);
  }, []);

  useEffect(() => {
    if (!selectedAgent) return;

    wsRef.current = connectLogStream(
      selectedAgent,
      (event, data) => {
        setLogs((prev) => [
          ...prev,
          {
            time: new Date().toISOString(),
            event,
            data: typeof data === "string" ? data : JSON.stringify(data),
          },
        ]);
        setConnected(true);
      },
      () => setConnected(false)
    );

    return () => {
      wsRef.current?.close();
      wsRef.current = null;
      setConnected(false);
    };
  }, [selectedAgent]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  const clearLogs = () => setLogs([]);

  return (
    <div>
      <h1>Log Stream</h1>

      <div className="log-controls">
        <select
          value={selectedAgent}
          onChange={(e) => {
            setSelectedAgent(e.target.value);
            setLogs([]);
          }}
        >
          <option value="">-- Select Agent --</option>
          {agents.map((a) => (
            <option key={a.id} value={a.id}>
              {a.name}
            </option>
          ))}
        </select>

        <button className="btn" onClick={clearLogs} disabled={logs.length === 0}>
          Clear
        </button>

        {selectedAgent && (
          <span className={`connection-status ${connected ? "connected" : "disconnected"}`}>
            {connected ? "● Connected" : "○ Disconnected"}
          </span>
        )}
      </div>

      <div className="log-container">
        {logs.length === 0 ? (
          <div className="empty-state">
            {selectedAgent
              ? "Waiting for logs..."
              : "Select an agent to view logs"}
          </div>
        ) : (
          logs.map((entry, i) => (
            <div key={i} className="log-entry">
              <span className="log-time">
                {new Date(entry.time).toLocaleTimeString()}
              </span>
              <span className="log-event">{entry.event}</span>
              <span className="log-data">{entry.data}</span>
            </div>
          ))
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
