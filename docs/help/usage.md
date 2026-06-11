# Usage Guide

## Quick Start

After installing AgentManager, follow these steps:

### 1. Add an LLM Provider

```bash
agentmanager provider add
# Name: my-openai
# Type: openai
# API Key: sk-xxx
# Default model: gpt-4
```

Add multiple providers:

```bash
agentmanager provider add --name my-claude --type anthropic --key sk-ant-xxx
agentmanager provider add --name local-llama --type ollama --url http://localhost:11434
agentmanager provider add --name router --type openrouter --key sk-or-xxx
```

### 2. Create Agents

From the web panel or CLI:

```bash
agentmanager agent create \
  --name "Lawyer-1" \
  --role lawyer \
  --provider my-claude \
  --model claude-3-opus
```

```bash
agentmanager agent create \
  --name "Dev-1" \
  --role developer \
  --provider my-openai \
  --model gpt-4
```

### 3. Assign Tasks

```bash
agentmanager task assign \
  --agent Lawyer-1 \
  --input "Analyze data processing requirements under GDPR"
```

### 4. Monitoring

Open the web panel: `http://localhost:3010`

On the panel you can see:
- Real-time status of all agents
- Live chain-of-thought streaming
- Token usage and quota information
- Task history

## Web Panel Usage

### Agent Cards
Each agent is displayed as a card:
- **Name** and **role** badge
- **Model** and **provider** info
- **Status** indicator (🟢 running / 🟡 idle / 🔴 error / ⏸ paused)
- Last task summary
- Control buttons (▶ start / ⏸ pause / ⏹ stop)

### Live Log Stream
Clicking an agent opens a detail modal:
- **Chain-of-Thought**: The agent's current reasoning process
- **LLM Logs**: API calls, token counts
- **Timeline**: Step-by-step task progress

### Provider Management
- Add new API keys
- Edit/remove existing keys
- Assign different providers/models to each agent

## MCP Usage (For AI Platforms)

From platforms like Antigravity, Codex CLI, or Claude Code:

```
list_agents → List all agents
assign_task(agent_id="lawyer-1", input="...") → Assign a task
pause_agent(agent_id="dev-1") → Pause an agent
resume_agent(agent_id="dev-1") → Resume an agent
```

## CLI Reference

```bash
agentmanager
├── start           Start the core
├── stop            Stop the core
├── restart         Restart the core
├── status          Show status
├── web             Open web panel
│
├── provider
│   ├── add         Add new provider
│   ├── list        List providers
│   ├── update      Update provider
│   └── remove      Remove provider
│
├── agent
│   ├── create      Create new agent
│   ├── list        List agents
│   ├── show        Show agent detail
│   ├── update      Update agent
│   ├── remove      Remove agent
│   ├── pause       Pause agent
│   └── resume      Resume agent
│
└── task
    ├── assign      Assign task
    ├── list        List tasks
    └── cancel      Cancel task
```
