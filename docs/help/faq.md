# Frequently Asked Questions (FAQ)

## General

### What is AgentManager?
AgentManager is a platform-independent multi-agent orchestration component that lets you manage multiple AI models under one roof. It installs as a plugin or MCP server on platforms like VS Code, Antigravity, and Codex CLI.

### Which AI models does it support?
OpenAI (GPT-4, GPT-4o, o1), Anthropic (Claude 3.5, 4), Google (Gemini Pro, Ultra), OpenRouter (all models), and Ollama (local models: Llama 3, Mistral, etc.). Any OpenAI-compatible API endpoint is also supported.

### Can I change an agent's model later?
Yes. You can change any agent's model and provider at runtime. If a task is in progress, it completes with the current model.

### How many agents can I create?
Unlimited. The only constraint is your providers' API quotas and rate limits.

## Setup

### I don't have Python 3.11, will 3.10 work?
Python 3.10+ works, but 3.11 is recommended (asyncio improvements, ExceptionGroups).

### Which VS Code versions are supported?
VS Code 1.85+ (2024). Modern HTML/CSS support is required for the webview panel.

### Does it work on Windows?
Yes. Python Core is fully supported on Windows. The VS Code extension is also tested on Windows.

## Usage

### Why isn't my agent responding?
1. Check if the core is running: `agentmanager status`
2. Verify the provider API key is correct: `agentmanager provider list`
3. Check agent status in the web panel
4. Inspect logs: Web panel > Agent detail > Logs

### I hit the token limit, what should I do?
1. Assign smaller tasks
2. Try a different model (e.g., gpt-4o-mini instead of gpt-4)
3. Monitor usage via the "Token Usage" section in the panel
4. Request higher limits from your provider

### I accidentally deleted an agent, can I restore it?
When an agent is deleted, its task history is archived, but the agent itself is permanently removed. You can create a new agent with the same settings.

## Performance

### Will running many agents slow down my computer?
AgentManager itself is lightweight (FastAPI + asyncio). The main load is from LLM API calls — which run on the provider's servers, not your computer. If you use local models (Ollama), GPU/CPU usage will increase.

### Can agents run in parallel?
Yes. All agents run asynchronously in parallel. Each agent executes independently in its own `asyncio.Task`.

## Security

### Are my API keys safe?
API keys are encrypted with AES-256-GCM and stored in the database. They are decrypted only at runtime and are never logged.

### Does AgentManager require internet?
Yes for LLM APIs (except Ollama). However, the core runs locally. The web panel and VS Code extension connect via localhost.

### Can agents see each other's data?
No. Each agent works in isolation. You must manually relay data between agents.

## Troubleshooting

### Core won't start
```
Log: Address already in use
```
→ Port 3010 might be in use: `agentmanager start --port 3011`

### WebSocket keeps disconnecting
→ Check firewall settings
→ If using a web proxy, make sure WebSocket connections are allowed

### "Provider not found" error
→ Make sure the provider exists: `agentmanager provider list`
→ Check you're using the correct provider name when creating agents

### API rate limit error
→ Reduce the number of agents using the same provider
→ Add a different provider for lower-priority tasks
