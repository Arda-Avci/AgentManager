import { AgentManagerClient } from "../mcp-client/index";

interface AntigravityContext {
  config: Record<string, string>;
  log: (level: string, message: string) => void;
}

interface AntigravityTool {
  name: string;
  description: string;
  handler: (args: Record<string, unknown>) => Promise<unknown>;
}

interface AntigravityPlugin {
  name: string;
  version: string;
  onActivate: (ctx: AntigravityContext) => Promise<void>;
  onDeactivate: () => Promise<void>;
  tools: AntigravityTool[];
}

let client: AgentManagerClient;
let context: AntigravityContext;

const plugin: AntigravityPlugin = {
  name: "agentmanager",
  version: "0.1.0",

  async onActivate(ctx: AntigravityContext) {
    context = ctx;
    const coreUrl = ctx.config["AGENTMANAGER_CORE_URL"] || "http://localhost:3010";
    const apiKey = ctx.config["AGENTMANAGER_API_KEY"] || "";
    client = new AgentManagerClient(coreUrl, apiKey);

    ctx.log("info", `AgentManager plugin activated (core: ${coreUrl})`);

    try {
      const health = await client.health();
      ctx.log("info", `Connected to AgentManager Core v${health.version}`);
    } catch (e) {
      ctx.log("error", `Cannot connect to AgentManager Core: ${e}`);
    }
  },

  async onDeactivate() {
    context?.log("info", "AgentManager plugin deactivated");
  },

  tools: [
    {
      name: "agentmanager_list_agents",
      description: "List all agents registered in AgentManager Core",
      async handler(args: Record<string, unknown>) {
        if (!client) throw new Error("AgentManager not connected");
        const agents = await client.listAgents();
        return { agents };
      },
    },
    {
      name: "agentmanager_get_agent",
      description: "Get detailed information about a specific agent by ID",
      async handler(args: Record<string, unknown>) {
        if (!client) throw new Error("AgentManager not connected");
        const agent = await client.getAgent(args.id as string);
        return { agent };
      },
    },
    {
      name: "agentmanager_create_agent",
      description:
        "Create a new agent in AgentManager Core. Requires name, optional role/provider/model.",
      async handler(args: Record<string, unknown>) {
        if (!client) throw new Error("AgentManager not connected");
        const agent = await client.createAgent({
          name: args.name as string,
          role: (args.role as string) || "assistant",
          provider: (args.provider as string) || "openai",
          model: (args.model as string) || "gpt-4o",
          system_prompt: (args.system_prompt as string) || "",
        });
        return { agent };
      },
    },
    {
      name: "agentmanager_chat",
      description: "Send a message to an agent and get a response",
      async handler(args: Record<string, unknown>) {
        if (!client) throw new Error("AgentManager not connected");
        const result = await client.chat(args.agent_id as string, args.message as string);
        return { response: result.response, model: result.used_model };
      },
    },
    {
      name: "agentmanager_list_tasks",
      description: "List all tasks in AgentManager Core",
      async handler(args: Record<string, unknown>) {
        if (!client) throw new Error("AgentManager not connected");
        const tasks = await client.listTasks();
        return { tasks };
      },
    },
    {
      name: "agentmanager_list_tools",
      description: "List all registered tools in AgentManager Core",
      async handler(args: Record<string, unknown>) {
        if (!client) throw new Error("AgentManager not connected");
        const tools = await client.listTools();
        return { tools };
      },
    },
    {
      name: "agentmanager_health",
      description: "Check AgentManager Core health status",
      async handler(args: Record<string, unknown>) {
        if (!client) throw new Error("AgentManager not connected");
        const health = await client.health();
        return { status: health.status, version: health.version };
      },
    },
  ],
};

export default plugin;
