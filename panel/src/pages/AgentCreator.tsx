import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client";

const PROVIDERS = ["openai", "anthropic", "gemini", "ollama", "mock"];
const MODELS: Record<string, string[]> = {
  openai: ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
  anthropic: ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
  gemini: ["gemini-1.5-pro", "gemini-1.5-flash"],
  ollama: ["llama3", "mistral", "mixtral", "codellama"],
  mock: ["mock-model"],
};

export default function AgentCreator() {
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [role, setRole] = useState("assistant");
  const [provider, setProvider] = useState("openai");
  const [model, setModel] = useState("gpt-4o");
  const [systemPrompt, setSystemPrompt] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const availableModels = MODELS[provider] || MODELS.openai;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await api.createAgent({
        name,
        role,
        provider,
        model,
        system_prompt: systemPrompt,
      });
      navigate(`/`);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to create agent");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div>
      <h1>Create Agent</h1>
      {error && <div className="error-banner">{error}</div>}
      <form onSubmit={handleSubmit} className="agent-form">
        <div className="form-group">
          <label htmlFor="name">Name *</label>
          <input
            id="name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            placeholder="my-agent"
          />
        </div>

        <div className="form-group">
          <label htmlFor="role">Role</label>
          <input
            id="role"
            value={role}
            onChange={(e) => setRole(e.target.value)}
            placeholder="assistant, analyst, coder, ..."
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="provider">Provider</label>
            <select
              id="provider"
              value={provider}
              onChange={(e) => {
                setProvider(e.target.value);
                setModel(MODELS[e.target.value]?.[0] || "");
              }}
            >
              {PROVIDERS.map((p) => (
                <option key={p} value={p}>
                  {p}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="model">Model</label>
            <select
              id="model"
              value={model}
              onChange={(e) => setModel(e.target.value)}
            >
              {availableModels.map((m) => (
                <option key={m} value={m}>
                  {m}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="system-prompt">System Prompt</label>
          <textarea
            id="system-prompt"
            value={systemPrompt}
            onChange={(e) => setSystemPrompt(e.target.value)}
            rows={5}
            placeholder="You are a helpful assistant..."
          />
        </div>

        <div className="form-actions">
          <button type="submit" className="btn btn-primary" disabled={submitting}>
            {submitting ? "Creating..." : "Create Agent"}
          </button>
          <button type="button" className="btn" onClick={() => navigate("/")}>
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
