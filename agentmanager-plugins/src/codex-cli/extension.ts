import { AgentManagerClient } from "../mcp-client/index";

// ── Codex CLI API types ──────────────────────────────────────────
interface CodexCLIConfig {
  get<T>(key: string, defaultValue?: T): T;
}

interface CodexCLICommandHandler {
  (args: string[], context: CodexCLIContext): Promise<string | void>;
}

interface CodexCLICommand {
  name: string;
  description: string;
  handler: CodexCLICommandHandler;
}

interface CodexCLIContext {
  config: CodexCLIConfig;
  log: (level: string, message: string) => void;
  input: string;
  output: (text: string) => void;
  error: (text: string) => void;
}

interface CodexCLIExtension {
  name: string;
  version: string;
  onActivate: (ctx: { config: CodexCLIConfig; log: (level: string, message: string) => void }) => Promise<void>;
  onDeactivate: () => Promise<void>;
  commands: CodexCLICommand[];
  mcpServers?: { name: string; command: string; args: string[] }[];
}

// ── Commands ─────────────────────────────────────────────────────

async function handleListAgents(args: string[], ctx: CodexCLIContext): Promise<string> {
  try {
    const agents = await client.listAgents();
    if (agents.length === 0) {
      return "No agents found. Create one via the API first.";
    }

    const rows = agents.map(
      (a) =>
        `${a.is_active ? "●" : "○"} ${a.name.padEnd(20)} ${a.role.padEnd(12)} ${a.status.padEnd(8)} ${a.provider}/${a.model}`
    );
    return [" Agents:", "", ...rows].join("\n");
  } catch (e: unknown) {
    const err = e instanceof Error ? e.message : String(e);
    return `Error fetching agents: ${err}`;
  }
}

async function handleChat(args: string[], ctx: CodexCLIContext): Promise<string> {
  if (args.length < 2) {
    return "Usage: /agent chat <name> <message>";
  }

  const agentName = args[0];
  const message = args.slice(1).join(" ");

  try {
    const agents = await client.listAgents();
    const agent = agents.find((a) => a.name === agentName);
    if (!agent) {
      const names = agents.map((a) => a.name).join(", ");
      return `Agent '${agentName}' not found. Available: ${names || "(none)"}`;
    }

    const result = await client.chat(agent.id, message);
    return `[${agent.name} via ${result.used_model}]\n${result.response}`;
  } catch (e: unknown) {
    const err = e instanceof Error ? e.message : String(e);
    return `Chat failed: ${err}`;
  }
}

async function handleTask(args: string[], ctx: CodexCLIContext): Promise<string> {
  if (args.length < 2) {
    return "Usage: /agent task <name> <goal>";
  }

  const agentName = args[0];
  const goal = args.slice(1).join(" ");

  try {
    const agents = await client.listAgents();
    const agent = agents.find((a) => a.name === agentName);
    if (!agent) {
      const names = agents.map((a) => a.name).join(", ");
      return `Agent '${agentName}' not found. Available: ${names || "(none)"}`;
    }

    const task = await client.createTask({ agent_id: agent.id, goal });
    return `Task created for ${agent.name}: [${task.id.slice(0, 8)}] ${task.goal} (${task.status})`;
  } catch (e: unknown) {
    const err = e instanceof Error ? e.message : String(e);
    return `Task creation failed: ${err}`;
  }
}

async function handleStatus(args: string[], ctx: CodexCLIContext): Promise<string> {
  try {
    const health = await client.health();
    const agents = await client.listAgents();
    const activeCount = agents.filter((a) => a.is_active).length;
    return [
      " AgentManager Status",
      "",
      `  Core:     v${health.version} (${health.status})`,
      `  Agents:   ${agents.length} total, ${activeCount} active`,
      `  API:      ${coreUrl}`,
    ].join("\n");
  } catch (e: unknown) {
    const err = e instanceof Error ? e.message : String(e);
    return `Cannot connect to AgentManager Core at ${coreUrl}: ${err}`;
  }
}

// ── Extension lifecycle ──────────────────────────────────────────

let client: AgentManagerClient;
let coreUrl: string;

const extension: CodexCLIExtension = {
  name: "agentmanager-codex-cli",
  version: "0.1.0",

  async onActivate(ctx) {
    const cfg = ctx.config;
    coreUrl = cfg.get<string>("agentmanager-codex-cli.coreUrl", "http://localhost:3010");
    const apiKey = cfg.get<string>("agentmanager-codex-cli.apiKey", "");
    client = new AgentManagerClient(coreUrl, apiKey);

    ctx.log("info", `AgentManager Codex CLI extension activated (core: ${coreUrl})`);

    try {
      const health = await client.health();
      ctx.log("info", `Connected to AgentManager Core v${health.version}`);
    } catch (e) {
      ctx.log("error", `Cannot connect to AgentManager Core: ${e}`);
    }
  },

  async onDeactivate() {
    // cleanup if needed
  },

  commands: [
    {
      name: "agent.list",
      description: "List all agents registered in AgentManager",
      handler: handleListAgents,
    },
    {
      name: "agent.chat",
      description: "Send a message to an agent. Usage: /agent chat <name> <message>",
      handler: handleChat,
    },
    {
      name: "agent.task",
      description: "Assign a task to an agent. Usage: /agent task <name> <goal>",
      handler: handleTask,
    },
    {
      name: "agent.status",
      description: "Show AgentManager connection status and agent count",
      handler: handleStatus,
    },
  ],

  mcpServers: [
    {
      name: "agentmanager",
      command: "python",
      args: ["-m", "src.cli.codex_handler"],
    },
  ],
};

export default extension;
