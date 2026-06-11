from __future__ import annotations

TASK_TEMPLATES: list[dict] = [
    {
        "name": "daily-standup",
        "description": "Daily standup update for team sync",
        "default_goal": "What was done yesterday, what is planned today, any blockers",
        "suggested_agent_role": "assistant",
    },
    {
        "name": "code-review",
        "description": "Review code changes for quality, security, and best practices",
        "default_goal": "Review the latest changes for code quality, security, and best practices",
        "suggested_agent_role": "reviewer",
    },
    {
        "name": "research-topic",
        "description": "Comprehensive research and summary on a given topic",
        "default_goal": "Research the following topic and provide a comprehensive summary",
        "suggested_agent_role": "researcher",
    },
    {
        "name": "write-docs",
        "description": "Write documentation for a feature or module",
        "default_goal": "Write documentation for the following feature/module",
        "suggested_agent_role": "writer",
    },
    {
        "name": "generate-tests",
        "description": "Generate unit tests for the given code",
        "default_goal": "Generate unit tests for the following code",
        "suggested_agent_role": "tester",
    },
]
