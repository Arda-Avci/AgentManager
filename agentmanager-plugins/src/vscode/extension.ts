import * as vscode from "vscode";
import { AgentManagerClient } from "../mcp-client/index";

let client: AgentManagerClient;
let statusBarItem: vscode.StatusBarItem;
let panel: vscode.WebviewPanel | undefined;

export function activate(context: vscode.ExtensionContext) {
  const config = vscode.workspace.getConfiguration("agentmanager");
  const coreUrl = config.get<string>("coreUrl", "http://localhost:3010");
  const apiKey = config.get<string>("apiKey", "");

  client = new AgentManagerClient(coreUrl, apiKey);

  // Status bar
  statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
  statusBarItem.command = "agentmanager.openPanel";
  context.subscriptions.push(statusBarItem);
  updateStatusBar();

  // Commands
  context.subscriptions.push(
    vscode.commands.registerCommand("agentmanager.openPanel", openPanel)
  );
  context.subscriptions.push(
    vscode.commands.registerCommand("agentmanager.refresh", refreshAll)
  );

  // Periodic refresh
  const interval = setInterval(updateStatusBar, 30000);
  context.subscriptions.push({ dispose: () => clearInterval(interval) });

  vscode.window.showInformationMessage("AgentManager is active");
}

export function deactivate() {
  if (panel) {
    panel.dispose();
  }
  statusBarItem?.dispose();
}

async function updateStatusBar() {
  try {
    const health = await client.health();
    const agents = await client.listAgents();
    const activeCount = agents.filter((a) => a.is_active).length;
    statusBarItem.text = `$(link) AM: ${activeCount} agents`;
    statusBarItem.tooltip = `AgentManager Core v${health.version} - ${agents.length} total agents`;
    statusBarItem.backgroundColor = undefined;
    statusBarItem.show();
  } catch {
    statusBarItem.text = `$(warning) AM: disconnected`;
    statusBarItem.tooltip = "Cannot connect to AgentManager Core";
    statusBarItem.backgroundColor = new vscode.ThemeColor(
      "statusBarItem.errorBackground"
    );
    statusBarItem.show();
  }
}

async function refreshAll() {
  await updateStatusBar();
  if (panel) {
    panel.webview.html = getPanelHtml(await getPanelData());
  }
}

async function openPanel() {
  const column = vscode.window.activeTextEditor
    ? vscode.window.activeTextEditor.viewColumn
    : vscode.ViewColumn.One;

  if (panel) {
    panel.reveal(column);
    return;
  }

  panel = vscode.window.createWebviewPanel(
    "agentmanager",
    "AgentManager Control Panel",
    column || vscode.ViewColumn.One,
    { enableScripts: true, retainContextWhenHidden: true }
  );

  panel.onDidDispose(() => {
    panel = undefined;
  });

  panel.webview.onDidReceiveMessage(async (msg) => {
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
          vscode.window.showErrorMessage(`Failed to delete agent: ${err}`);
        }
        break;
    }
  });

  panel.webview.html = getPanelHtml(await getPanelData());
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
      <td>${esc(a.status)}</td>
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
    ? `<div class="error">⚠️ Connection error: ${esc(data.error)}</div>`
    : `<div class="ok">✅ Connected v${esc(data.health?.version || "")}</div>`;

  return `<!DOCTYPE html>
<html>
<head>
<style>
  body { font-family: system-ui, sans-serif; padding: 16px; color: var(--vscode-foreground); }
  h1 { font-size: 1.4em; margin: 0 0 8px; }
  h2 { font-size: 1.1em; margin: 16px 0 8px; }
  table { width: 100%; border-collapse: collapse; }
  th, td { padding: 6px 8px; text-align: left; border-bottom: 1px solid var(--vscode-panel-border); }
  th { font-weight: 600; }
  .error { color: var(--vscode-errorForeground); padding: 8px; background: var(--vscode-inputValidation-errorBackground); }
  .ok { color: var(--vscode-testing-iconPassedForeground); padding: 8px; }
  button { cursor: pointer; }
  .toolbar { margin-bottom: 12px; }
</style>
</head>
<body>
  <div class="toolbar">
    <button onclick="refresh()">🔄 Refresh</button>
    ${errorHtml}
  </div>
  <h1>Agents</h1>
  <table>
    <thead><tr><th>Name</th><th>Role</th><th>Status</th><th>Active</th><th></th></tr></thead>
    <tbody>${agentRows || "<tr><td colspan='5'>No agents found</td></tr>"}</tbody>
  </table>
  <h1>Tools</h1>
  <table>
    <thead><tr><th>Name</th><th>Type</th><th>Active</th></tr></thead>
    <tbody>${toolRows || "<tr><td colspan='3'>No tools found</td></tr>"}</tbody>
  </table>
<script>
const vscode = acquireVsCodeApi();
function refresh() { vscode.postMessage({ command: "refresh" }); }
function deleteAgent(id) { if (confirm('Delete agent?')) vscode.postMessage({ command: "deleteAgent", agentId: id }); }
</script>
</body>
</html>`;
}

function esc(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
