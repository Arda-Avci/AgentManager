# Agent Management

## Agent Roles

AgentManager comes with 5 default roles:

| Role | Description | Default Capabilities |
|------|-------------|---------------------|
| **lawyer** | Legal analysis, compliance auditing | KVKK, GDPR, contract analysis |
| **developer** | Backend development, API design | Python, TypeScript, SQL, REST |
| **frontend** | UI/UX development | React, Tailwind, CSS, UX |
| **reviewer** | Code review, security audit | Code review, security analysis |
| **tester** | Test scenarios, integration testing | Unit test, E2E, integration test |

## Creating Agents

### From Web Panel
1. Click "New Agent" button
2. Select name, role, and model
3. Optionally enter custom system instructions
4. Click "Create"

### Via CLI

```bash
agentmanager agent create \
  --name "Backend-Dev" \
  --role developer \
  --provider my-openai \
  --model gpt-4 \
  --system-prompt "You are a backend development expert..."
```

### Via MCP (Antigravity/Codex CLI)

```
create_agent(name="Backend-Dev", role="developer", provider="my-openai", model="gpt-4")
```

## Managing Agents

### Pause and Resume

When you pause an agent:
- Current task is **frozen** (state preserved)
- Any ongoing LLM call completes first
- Other agents are unaffected

When you resume:
- Continues where it left off
- Chain-of-thought is preserved

### Changing Roles

You can change an agent's role at runtime:

```bash
agentmanager agent update Backend-Dev --role reviewer
```

This:
- Updates the agent's system prompt to the new role
- Waits for current task completion
- New role activates on the next task

### Changing Models

```bash
agentmanager agent update Backend-Dev --model claude-4 --provider my-claude
```

This:
- New model activates immediately
- Ongoing tasks complete with the current model
- Token counter is not reset

## Removing Agents

```bash
agentmanager agent remove Backend-Dev
```

When deleted:
- Task history is archived (not deleted)
- Active tasks are cancelled first
- Record is removed from the database

## Custom Roles

Create via the "Role Manager" in the web panel or directly as a template file:

```yaml
# core/agents/templates/data-analyst.yaml
name: data-analyst
display_name: Data Analyst
description: Data analysis, reporting, and visualization
system_prompt: |
  You are a data analyst assistant.
  Your task: analyze datasets, extract meaningful insights,
  and prepare visual reports.
capabilities:
  - data analysis
  - visualization
  - reporting
default_model: gpt-4
```

## Agent Communication

There is no direct agent-to-agent communication. The flow is:

```
YOU → Assign task to Agent-1
YOU → Receive Agent-1 output
YOU → Feed Agent-1's output as input to Agent-2
```

This means:
- Each agent works in isolation
- Token consumption is controlled
- Errors don't cascade between agents
- Prompt injection risk is minimized
