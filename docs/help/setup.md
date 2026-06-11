# Setup Guide

## Requirements

- **Python 3.11+**
- **Node.js 18+** (for VS Code extension and web panel)
- **VS Code** (optional, for extension usage)
- An **AI API key** (OpenAI, Anthropic, Google, or OpenRouter)

## 1. Install Python Core

### Via pip

```bash
pip install agentmanager-core
```

### From source

```bash
git clone https://github.com/your-org/agentmanager.git
cd agentmanager/core
pip install -r requirements.txt
```

## 2. VS Code Extension

### From VS Code Marketplace

1. Open VS Code
2. Press `Ctrl+Shift+X` to open Extensions
3. Search "AgentManager"
4. Click **Install**

### From source

```bash
cd plugin/vscode
npm install
npm run package
code --install-extension agentmanager-*.vsix
```

## 3. Web Panel

```bash
cd plugin/web-panel
npm install
npm run build
```

## 4. First Run

```bash
# Start the core
agentmanager start

# Open web panel
# http://localhost:3010

# Add your first LLM provider
agentmanager provider add
# > Provider name: my-openai
# > Type: openai
# > API Key: sk-...
# > Model: gpt-4
```

## 5. Verification

Run in your terminal:

```bash
agentmanager status
```

Output:
```
✓ AgentManager Core is running
  Web Panel: http://localhost:3010
  MCP Server: http://localhost:3010/mcp
  
  Providers:
  - my-openai (openai) ✅
  
  Agents: (no agents created yet)
```

## 6. Enable Platform Plugins

### VS Code
Press `Ctrl+Shift+P` → "AgentManager: Open Panel"

### Antigravity
Add as an MCP server in Antigravity settings:
```
Server Address: http://localhost:3010/mcp
```

### Codex CLI
```bash
codex --mcp-server http://localhost:3010/mcp
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `agentmanager` command not found | Make sure Python's Scripts folder is in your PATH |
| Port 3010 in use | Use `agentmanager start --port 3011` to change port |
| API key error | Check providers with `agentmanager provider list` |
