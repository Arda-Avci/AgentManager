import * as vscode from "vscode";
import { AgentManagerClient } from "../mcp-client/index";

let client: AgentManagerClient;
let statusBarItem: vscode.StatusBarItem;
let panel: vscode.WebviewPanel | undefined;

export function activate(context: vscode.ExtensionContext) {
  const config = vscode.workspace.getConfiguration("agentmanager-cursor");
  const coreUrl = config.get<string>("coreUrl", "http://localhost:3010");
  const apiKey = config.get<string>("apiKey", "");

  client = new AgentManagerClient(coreUrl, apiKey);

  statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
  statusBarItem.command = "agentmanager-cursor.openPanel";
  context.subscriptions.push(statusBarItem);
  updateStatusBar();

  context.subscriptions.push(
    vscode.commands.registerCommand("agentmanager-cursor.openPanel", openPanel)
  );
  context.subscriptions.push(
    vscode.commands.registerCommand("agentmanager-cursor.refresh", refreshAll)
  );
  context.subscriptions.push(
    vscode.commands.registerCommand("agentmanager-cursor.quickAgent", quickAgent)
  );
  context.subscriptions.push(
    vscode.commands.registerCommand("agentmanager-cursor.chatWithAgent", chatWithAgent)
  );

  const interval = setInterval(updateStatusBar, 30000);
  context.subscriptions.push({ dispose: () => clearInterval(interval) });

  vscode.window.showInformationMessage("AgentManager for Cursor is active");
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
    statusBarItem.text = `$(link) AM: ${activeCount} agents`;
    statusBarItem.tooltip = `AgentManager v${health.version} - ${agents.length} agents`;
    statusBarItem.backgroundColor = undefined;
    statusBarItem.show();
  } catch {
    statusBarItem.text = `$(warning) AM: disconnected`;
    statusBarItem.tooltip = "Cannot connect to AgentManager Core";
    statusBarItem.backgroundColor = new vscode.ThemeColor("statusBarItem.errorBackground");
    statusBarItem.show();
  }
}

async function refreshAll() {
  await updateStatusBar();
  if (panel) {
    panel.webview.html = getPanelHtml(await getPanelData());
  }
}

async function quickAgent() {
  try {
    const agents = await client.listAgents();
    if (agents.length === 0) {
      vscode.window.showInformationMessage("No agents available. Create one first.");
      return;
    }
    const items = agents.map((a) => ({
      label: a.name,
      description: `${a.role} (${a.status})`,
      detail: `${a.provider}/${a.model}`,
      agent: a,
    }));
    const picked = await vscode.window.showQuickPick(items, {
      placeHolder: "Select an agent to command",
    });
    if (!picked) return;

    const action = await vscode.window.showQuickPick(
      [
        { label: "Chat", description: "Send a message to this agent" },
        { label: "Pause", description: "Pause this agent" },
        { label: "Resume", description: "Resume this agent" },
        { label: "Status", description: "Show agent details" },
      ],
      { placeHolder: `What to do with ${picked.agent.name}?` }
    );
    if (!action) return;

    switch (action.label) {
      case "Chat": {
        const message = await vscode.window.showInputBox({
          prompt: `Message to ${picked.agent.name}`,
          placeHolder: "Type your message...",
        });
        if (message) {
          const result = await client.chat(picked.agent.id, message);
          vscode.window.showInformationMessage(`Response: ${result.response.slice(0, 200)}`);
        }
        break;
      }
      case "Pause":
        await client.updateAgent(picked.agent.id, { status: "paused" });
        vscode.window.showInformationMessage(`Agent ${picked.agent.name} paused`);
        break;
      case "Resume":
        await client.updateAgent(picked.agent.id, { status: "idle" });
        vscode.window.showInformationMessage(`Agent ${picked.agent.name} resumed`);
        break;
      case "Status":
        const detail = await client.getAgent(picked.agent.id);
        vscode.window.showInformationMessage(
          `${detail.name}: ${detail.role} | ${detail.status} | ${detail.provider}/${detail.model}`
        );
        break;
    }
    await updateStatusBar();
  } catch (e: unknown) {
    const err = e instanceof Error ? e.message : String(e);
    vscode.window.showErrorMessage(`AgentManager error: ${err}`);
  }
}

async function chatWithAgent() {
  try {
    const agents = await client.listAgents();
    if (agents.length === 0) {
      vscode.window.showInformationMessage("No agents available.");
      return;
    }
    const items = agents.map((a) => ({
      label: a.name,
      description: `${a.role} (${a.status})`,
      agent: a,
    }));
    const picked = await vscode.window.showQuickPick(items, {
      placeHolder: "Select an agent to chat with",
    });
    if (!picked) return;

    const message = await vscode.window.showInputBox({
      prompt: `Message to ${picked.agent.name}`,
      placeHolder: "Type your message...",
    });
    if (!message) return;

    const result = await client.chat(picked.agent.id, message);
    const doc = await vscode.workspace.openTextDocument({
      content: `## ${picked.agent.name} Response\n\n**You:** ${message}\n\n**Agent:** ${result.response}\n\n---\n*Model: ${result.used_model}*`,
      language: "markdown",
    });
    vscode.window.showTextDocument(doc);
  } catch (e: unknown) {
    const err = e instanceof Error ? e.message : String(e);
    vscode.window.showErrorMessage(`Chat failed: ${err}`);
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
    "agentmanagerCursor",
    "AgentManager (Cursor)",
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
      case "chat":
        try {
          const result = await client.chat(msg.agentId, msg.message);
          panel?.webview.postMessage({ command: "chatResult", result });
        } catch (e: unknown) {
          const err = e instanceof Error ? e.message : String(e);
          panel?.webview.postMessage({ command: "chatError", error: err });
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
      <td><span class="status-${a.status}">${esc(a.status)}</span></td>
      <td>${a.is_active ? "✅" : "❌"}</td>
      <td><button onclick="chat('${a.id}')">Chat</button> <button onclick="deleteAgent('${a.id}')">Delete</button></td>
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
  body { font-family: system-ui, sans-serif; padding: 16px; color: var(--vscode-foreground); }
  h1 { font-size: 1.4em; margin: 0 0 8px; }
  h2 { font-size: 1.1em; margin: 16px 0 8px; }
  table { width: 100%; border-collapse: collapse; }
  th, td { padding: 6px 8px; text-align: left; border-bottom: 1px solid var(--vscode-panel-border); }
  th { font-weight: 600; }
  .error { color: var(--vscode-errorForeground); padding: 8px; background: var(--vscode-inputValidation-errorBackground); }
  .ok { color: var(--vscode-testing-iconPassedForeground); padding: 8px; }
  .status-idle { color: var(--vscode-testing-iconPassedForeground); }
  .status-running { color: var(--vscode-charts-yellow); }
  .status-paused { color: var(--vscode-errorForeground); }
  button { cursor: pointer; margin: 2px; }
  .toolbar { margin-bottom: 12px; display: flex; gap: 8px; align-items: center; }
  #chat-area { margin-top: 16px; border-top: 1px solid var(--vscode-panel-border); padding-top: 12px; }
  #chat-messages { height: 200px; overflow-y: auto; border: 1px solid var(--vscode-panel-border); padding: 8px; margin-bottom: 8px; font-size: 0.9em; }
  #chat-input { width: calc(100% - 80px); }
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
    <tbody>${agentRows || "<tr><td colspan='5'>No agents found</td></tr>"}</tbody>
  </table>
  <h1>Tools</h1>
  <table>
    <thead><tr><th>Name</th><th>Type</th><th>Active</th></tr></thead>
    <tbody>${toolRows || "<tr><td colspan='3'>No tools found</td></tr>"}</tbody>
  </table>
  <div id="chat-area">
    <h2>Quick Chat</h2>
    <div id="chat-messages"><em>Select an agent and click Chat to begin.</em></div>
    <input id="chat-input" type="text" placeholder="Type a message..." onkeydown="if(event.key==='Enter')sendChat()"/>
    <button onclick="sendChat()">Send</button>
  </div>
<script>
const vscode = acquireVsCodeApi();
let currentAgentId = null;
function refresh() { vscode.postMessage({ command: "refresh" }); }
function deleteAgent(id) { if (confirm('Delete agent?')) vscode.postMessage({ command: "deleteAgent", agentId: id }); }
function chat(id) {
  currentAgentId = id;
  document.getElementById('chat-messages').innerHTML = '<em>Ready to chat. Type a message and press Enter.</em>';
  document.getElementById('chat-input').focus();
}
function sendChat() {
  const input = document.getElementById('chat-input');
  const msg = input.value.trim();
  if (!msg || !currentAgentId) return;
  const msgs = document.getElementById('chat-messages');
  msgs.innerHTML += '<div><strong>You:</strong> ' + esc(msg) + '</div>';
  input.value = '';
  vscode.postMessage({ command: "chat", agentId: currentAgentId, message: msg });
}
window.addEventListener('message', event => {
  const msg = event.data;
  if (msg.command === 'chatResult') {
    const msgs = document.getElementById('chat-messages');
    msgs.innerHTML += '<div><strong>Agent:</strong> ' + esc(msg.result.response) + ' <em>(' + msg.result.used_model + ')</em></div>';
    msgs.scrollTop = msgs.scrollHeight;
  } else if (msg.command === 'chatError') {
    const msgs = document.getElementById('chat-messages');
    msgs.innerHTML += '<div style="color: var(--vscode-errorForeground);"><strong>Error:</strong> ' + esc(msg.error) + '</div>';
  }
});
function esc(s) { return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
</script>
</body>
</html>`;
}

function esc(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
