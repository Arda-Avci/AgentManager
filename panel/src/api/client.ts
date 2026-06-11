const BASE = "/api/v1";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `HTTP ${res.status}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

export interface Agent {
  id: string;
  name: string;
  role: string;
  status: string;
  provider: string;
  model: string;
  is_active: boolean;
  created_at: string;
}

export interface CreateAgentInput {
  name: string;
  role?: string;
  provider?: string;
  model?: string;
  system_prompt?: string;
}

export interface Task {
  id: string;
  agent_id: string;
  goal: string;
  status: string;
  result: string | null;
  created_at: string;
}

export const api = {
  listAgents: () => request<Agent[]>("/agents"),

  getAgent: (id: string) => request<Agent>(`/agents/${id}`),

  createAgent: (data: CreateAgentInput) =>
    request<Agent>("/agents", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  deleteAgent: (id: string) =>
    request<void>(`/agents/${id}`, { method: "DELETE" }),

  listTasks: () => request<Task[]>("/tasks"),

  createTask: (agentId: string, goal: string) =>
    request<Task>("/tasks", {
      method: "POST",
      body: JSON.stringify({ agent_id: agentId, goal }),
    }),

  health: () => request<{ status: string; version: string }>("/health"),
};
