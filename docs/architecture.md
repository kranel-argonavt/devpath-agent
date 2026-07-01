# Architecture

The current architecture is intentionally simple so the MVP is easy to test, demo, and explain.

```text
Streamlit UI
   ↓
Local file services
   ↓
Deterministic scoring + privacy + report builder
   ↓
Markdown export
```

The planned future architecture introduces agent orchestration and external integrations:

```text
Future:
Streamlit UI
   ↓
ADK Root Agent
   ↓
Sub-agents + MCP tools
   ↓
Gemini + GitHub public repo import
```

## Current Modules

- `app.py` renders the Streamlit mock workflow.
- `devpath/services/file_service.py` loads local JSON and text files.
- `devpath/core/scoring.py` calculates deterministic mock scores.
- `devpath/core/privacy.py` masks emails, phone-like strings, and API-key-like values.
- `devpath/core/report_builder.py` assembles structured mock reports.
- `devpath/services/export_service.py` writes Markdown reports.
- `devpath/services/github_service.py` remains placeholder-only for future GitHub work.

## Future Agent Modules

- `devpath/agent.py` will become the ADK root agent entry point.
- `devpath/sub_agents/` will contain role-focused sub-agents.
- `mcp_server/` will expose selected tools through a future MCP server.
