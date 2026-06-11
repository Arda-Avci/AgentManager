export class AgentManagerClient {
  private baseUrl: string;
  private apiKey: string;

  constructor(baseUrl: string = "http://localhost:3010", apiKey: string = "") {
    this.baseUrl = baseUrl.replace(/\/+$/, "");
    this.apiKey = apiKey;
  }

  private get headers(): Record<string, string> {
    const h: Record<string, string> = { "Content-Type": "application/json" };
    if (this.apiKey) {
      h["Authorization"] = `Bearer ${this.apiKey}`;
    }
    return h;
  }

  private async request<T>(
    method: string,
    path: string,
    body?: unknown
  ): Promise<T> {
    const url = `${this.baseUrl}/api/v1${path}`;
    const res = await fetch(url, {
      method,
      headers: this.headers,
      body: body ? JSON.stringify(body) : undefined,
    });
    if (!res.ok) {
      const text = await res.text();
      throw new Error(`AgentManager API error ${res.status}: ${text}`);
    }
    if (res.status === 204) return undefined as T;
    return res.json() as Promise<T>;
  }

  // ── Agent CRUD ──────────────────────────────────────────────

  async listAgents(): Promise<AgentResponse[]> {
    return this.request<AgentResponse[]>("GET", "/agents");
  }

  async getAgent(id: string): Promise<AgentResponse> {
    return this.request<AgentResponse>("GET", `/agents/${id}`);
  }

  async createAgent(data: AgentCreate): Promise<AgentResponse> {
    return this.request<AgentResponse>("POST", "/agents", data);
  }

  async updateAgent(id: string, data: AgentUpdate): Promise<AgentResponse> {
    return this.request<AgentResponse>("PATCH", `/agents/${id}`, data);
  }

  async deleteAgent(id: string): Promise<void> {
    return this.request<void>("DELETE", `/agents/${id}`);
  }

  // ── Chat ────────────────────────────────────────────────────

  async chat(agentId: string, message: string): Promise<ChatResponse> {
    return this.request<ChatResponse>("POST", "/chat", {
      agent_id: agentId,
      message,
    });
  }

  // ── Tasks ───────────────────────────────────────────────────

  async listTasks(): Promise<TaskResponse[]> {
    return this.request<TaskResponse[]>("GET", "/tasks");
  }

  async createTask(data: TaskCreate): Promise<TaskResponse> {
    return this.request<TaskResponse>("POST", "/tasks", data);
  }

  // ── Tools ───────────────────────────────────────────────────

  async listTools(): Promise<ToolResponse[]> {
    return this.request<ToolResponse[]>("GET", "/tools");
  }

  async createTool(data: ToolCreate): Promise<ToolResponse> {
    return this.request<ToolResponse>("POST", "/tools", data);
  }

  async callTool(toolId: string, args: Record<string, unknown>): Promise<{ result: unknown }> {
    return this.request<{ result: unknown }>("POST", `/tools/${toolId}/call`, { arguments: args });
  }

  // ── Providers ───────────────────────────────────────────────

  async listProviders(): Promise<ProviderResponse[]> {
    return this.request<ProviderResponse[]>("GET", "/providers");
  }

  async createProvider(data: ProviderCreate): Promise<ProviderResponse> {
    return this.request<ProviderResponse>("POST", "/providers", data);
  }

  // ── Health ──────────────────────────────────────────────────

  async health(): Promise<{ status: string; version: string }> {
    return this.request<{ status: string; version: string }>("GET", "/health");
  }
}

// ── Type Definitions ──────────────────────────────────────────

export interface AgentResponse {
  id: string;
  name: string;
  role: string;
  status: string;
  provider: string;
  model: string;
  is_active: boolean;
  created_at: string;
}

export interface AgentCreate {
  name: string;
  role?: string;
  system_prompt?: string;
  provider?: string;
  model?: string;
  fallback_providers?: Record<string, unknown>[];
  config?: Record<string, unknown>;
}

export interface AgentUpdate {
  name?: string;
  role?: string;
  system_prompt?: string;
  provider?: string;
  model?: string;
  status?: string;
  fallback_providers?: Record<string, unknown>[];
  config?: Record<string, unknown>;
}

export interface TaskCreate {
  agent_id: string;
  goal: string;
  parent_task_id?: string;
}

export interface TaskResponse {
  id: string;
  agent_id: string;
  goal: string;
  status: string;
  result: string | null;
  created_at: string;
}

export interface ToolCreate {
  name: string;
  description?: string;
  tool_type?: string;
  mcp_server_url?: string;
  agent_id?: string;
  config?: Record<string, unknown>;
}

export interface ToolResponse {
  id: string;
  name: string;
  description: string;
  tool_type: string;
  mcp_server_url: string | null;
  agent_id: string | null;
  is_active: boolean;
  config: Record<string, unknown>;
  created_at: string;
}

export interface ProviderCreate {
  name: string;
  provider_type: string;
  api_key?: string;
  base_url?: string;
  config?: Record<string, unknown>;
}

export interface ProviderResponse {
  name: string;
  provider_type: string;
  is_enabled: boolean;
  created_at: string;
}

export interface ChatResponse {
  response: string;
  used_model: string;
}
