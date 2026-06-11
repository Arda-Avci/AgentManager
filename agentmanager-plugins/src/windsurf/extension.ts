import { AgentManagerClient } from "../mcp-client/index";

interface WindsurfAPI {
  window: {
    showInformationMessage(message: string): void;
    showErrorMessage(message: string): void;
    showQuickPick(items: { label: string; description?: string }[], options?: { placeHolder?: string }): Promise<{ label: string; description?: string } | undefined>;
    createStatusBarItem(alignment?: "left" | "right", priority?: number): {
      text: string;
      tooltip?: string;
      command?: string;
      backgroundColor?: string;
      show(): void;
      dispose(): void;
    };
    createWebviewPanel(viewType: string, title: string, options?: { enableScripts?: boolean }): {
      html: string;
      onDidReceiveMessage(cb: (msg: any) => void): void;
      postMessage(msg: any): void;
      dispose(): void;
      onDidDispose(cb: () => void): void;
    };
  };
  commands: {
    registerCommand(id: string, handler: () => void): { dispose(): void };
  };
  workspace: {
    getConfiguration(section: string): {
      get<T>(key: string, defaultValue?: T): T;
    };
  };
  subscriptions: { dispose(): void }[];
}

declare const windsurf: WindsurfAPI;

let client: AgentManagerClient;
let statusBarItem: ReturnType<WindsurfAPI["window"]["createStatusBarItem"]>;
let panel: ReturnType<WindsurfAPI["window"]["createWebviewPanel"]> | undefined;

export function activate(context: { subscriptions: { dispose(): void }[] }) {
  const config = windsurf.workspace.getConfiguration("agentmanager-windsurf");
  const coreUrl = config.get<string>("coreUrl", "http://localhost:3010");
  const apiKey = config.get<string>("apiKey", "");

  client = new AgentManagerClient(coreUrl, apiKey);

  statusBarItem = windsurf.window.createStatusBarItem("right", 100);
  statusBarItem.command = "agentmanager-windsurf.openPanel";
  context.subscriptions.push(statusBarItem);
  updateStatusBar();

  context.subscriptions.push(
    windsurf.commands.registerCommand("agentmanager-windsurf.openPanel", openPanel)
  );
  context.subscriptions.push(
    windsurf.commands.registerCommand("agentmanager-windsurf.refresh", refreshAll)
  );
  context.subscriptions.push(
    windsurf.commands.registerCommand("agentmanager-windsurf.quickAgent", quickAgent)
  );

  const interval = setInterval(updateStatusBar, 30000);
  context.subscriptions.push({ dispose: () => clearInterval(interval) });

  windsurf.window.showInformationMessage("AgentManager for Windsurf is active");
}

export function deactivate() {
  if (panel) panel.dispose();
  statusBarItem?.dispose();
}

async function updateStatusBar() {
  try {
    const health = await client.health();
    const agents = await client.listAgents();
    const activeCount = agents.filter((a) => a.is_active).length;
    statusBarItem.text = `AM: ${activeCount} agents`;
    statusBarItem.tooltip = `AgentManager v${health.version} - ${agents.length} total`;
    statusBarItem.backgroundColor = undefined;
    statusBarItem.show();
  } catch {
    statusBarItem.text = "AM: disconnected";
    statusBarItem.tooltip = "Cannot connect to AgentManager Core";
    statusBarItem.show();
  }
}

async function refreshAll() {
  await updateStatusBar();
  if (panel) {
    panel.html = getPanelHtml(await getPanelData());
  }
}

async function quickAgent() {
  try {
    const agents = await client.listAgents();
    if (agents.length === 0) {
      windsurf.window.showInformationMessage("No agents available.");
      return;
    }
    const items = agents.map((a) => ({
      label: a.name,
      description: `${a.role} (${a.status})`,
    }));
    const picked = await windsurf.window.showQuickPick(items, {
      placeHolder: "Select an agent",
    });
    if (!picked) return;

    const action = await windsurf.window.showQuickPick([
      { label: "Chat", description: "Send a message" },
      { label: "Pause", description: "Pause agent" },
      { label: "Resume", description: "Resume agent" },
    ], { placeHolder: `Action for ${picked.label}` });
    if (!action) return;

    const agent = agents.find((a) => a.name === picked.label);
    if (!agent) return;

    switch (action.label) {
      case "Pause":
        await client.updateAgent(agent.id, { status: "paused" });
        windsurf.window.showInformationMessage(`Agent ${agent.name} paused`);
        break;
      case "Resume":
        await client.updateAgent(agent.id, { status: "idle" });
        windsurf.window.showInformationMessage(`Agent ${agent.name} resumed`);
        break;
    }
    await updateStatusBar();
  } catch (e: unknown) {
    const err = e instanceof Error ? e.message : String(e);
    windsurf.window.showErrorMessage(`AgentManager error: ${err}`);
  }
}

async function openPanel() {
  if (panel) {
    panel.html = getPanelHtml(await getPanelData());
    return;
  }

  panel = windsurf.window.createWebviewPanel("agentmanagerWindsurf", "AgentManager (Windsurf)", {
    enableScripts: true,
  });

  panel.onDidDispose(() => {
    panel = undefined;
  });

  panel.onDidReceiveMessage(async (msg) => {
    switch (msg.command) {
      case "refresh":
        await refreshAll();
        break;
      case "deleteAgent":
        try {
          await client.deleteAgent(msg.agentId);
          await refreshAll();
        } catch (e: unknown) {
          const err = e instanceof Error ? e.message : String(e);
          windsurf.window.showErrorMessage(`Delete failed: ${err}`);
        }
        break;
    }
  });

  panel.html = getPanelHtml(await getPanelData());
}

async function getPanelData() {
  try {
    const [health, agents, tools] = await Promise.all([
      client.health(),
      client.listAgents(),
      client.listTools(),
    ]);
    return { health, agents, tools, error: null };
  } catch (e: unknown) {
    return {
      health: null,
      agents: [],
      tools: [],
      error: e instanceof Error ? e.message : String(e),
    };
  }
}

function getPanelHtml(data: {
  health: { status: string; version: string } | null;
  agents: { id: string; name: string; role: string; status: string; is_active: boolean }[];
  tools: { id: string; name: string; tool_type: string; is_active: boolean }[];
  error: string | null;
}): string {
  const agentRows = data.agents
    .map(
      (a) => `
    <tr>
      <td>${esc(a.name)}</td>
      <td>${esc(a.role)}</td>
      <td><span class="s-${a.status}">${esc(a.status)}</span></td>
      <td>${a.is_active ? "✅" : "❌"}</td>
      <td><button onclick="deleteAgent('${a.id}')">Delete</button></td>
    </tr>`
    )
    .join("");

  const toolRows = data.tools
    .map(
      (t) => `
    <tr>
      <td>${esc(t.name)}</td>
      <td>${esc(t.tool_type)}</td>
      <td>${t.is_active ? "✅" : "❌"}</td>
    </tr>`
    )
    .join("");

  const errorHtml = data.error
    ? `<div class="error">⚠️ ${esc(data.error)}</div>`
    : `<div class="ok">✅ Connected v${esc(data.health?.version || "")}</div>`;

  return `<!DOCTYPE html>
<html>
<head>
<style>
  body { font-family: system-ui, sans-serif; padding: 16px; color: #d4d4d4; background: #1e1e1e; }
  h1 { font-size: 1.4em; margin: 0 0 8px; color: #e0e0e0; }
  h2 { font-size: 1.1em; margin: 16px 0 8px; }
  table { width: 100%; border-collapse: collapse; }
  th, td { padding: 6px 8px; text-align: left; border-bottom: 1px solid #333; }
  th { font-weight: 600; color: #9cdcfe; }
  .error { color: #f48771; padding: 8px; background: #2d1b1b; border-radius: 4px; }
  .ok { color: #6a9955; padding: 8px; }
  .s-idle { color: #6a9955; }
  .s-running { color: #dcdcaa; }
  .s-paused { color: #f48771; }
  button { cursor: pointer; background: #0e639c; color: white; border: none; padding: 4px 12px; border-radius: 3px; }
  button:hover { background: #1177bb; }
  .toolbar { margin-bottom: 12px; display: flex; gap: 8px; align-items: center; }
</style>
</head>
<body>
  <div class="toolbar">
    <button onclick="refresh()">🔄 Refresh</button>
    ${errorHtml}
  </div>
  <h1>Agents</h1>
  <table>
    <thead><tr><th>Name</th><th>Role</th><th>Status</th><th>Active</th><th>Actions</th></tr></thead>
    <tbody>${agentRows || "<tr><td colspan='5'>No agents</td></tr>"}</tbody>
  </table>
  <h1>Tools</h1>
  <table>
    <thead><tr><th>Name</th><th>Type</th><th>Active</th></tr></thead>
    <tbody>${toolRows || "<tr><td colspan='3'>No tools</td></tr>"}</tbody>
  </table>
<script>
function refresh() { postMessage({ command: "refresh" }); }
function deleteAgent(id) { if (confirm('Delete agent?')) postMessage({ command: "deleteAgent", agentId: id }); }
</script>
</body>
</html>`;
}

function esc(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
