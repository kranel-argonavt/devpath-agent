# Architecture

The current architecture remains simple and testable. Deterministic scoring is still the source of truth, and Gemini is only an optional narrative layer.

## Current Flow

```text
Streamlit UI
   |
Deterministic scoring/report/export
```

## Step 3A Flow

```text
Streamlit UI
   |
Deterministic scoring/report/export
   |
Optional Gemini-assisted narrative summary
```

Gemini-assisted mode can improve the written career summary, but it must not change the numeric match score, category scores, missing skills, or evidence mapping.

## Future Agent Flow

```text
ADK Root Agent
   |
Sub-agents + MCP tools
   |
Gemini + deterministic tools
```

## Current Modules

- `app.py` renders the Streamlit mock workflow and optional Gemini-assisted summary mode.
- `devpath/core/config.py` loads optional Gemini configuration from environment variables.
- `devpath/services/gemini_service.py` isolates Gemini calls behind a small wrapper.
- `devpath/services/file_service.py` loads local JSON and text files.
- `devpath/core/scoring.py` calculates deterministic evidence-based scores.
- `devpath/core/privacy.py` masks emails, phone-like strings, and API-key-like values.
- `devpath/core/report_builder.py` assembles structured mock reports.
- `devpath/services/export_service.py` writes privacy-masked Markdown reports.
- `devpath/services/github_service.py` remains placeholder-only for future GitHub work.

## Future Agent Modules

- `devpath/agent.py` will become the ADK root agent entry point.
- `devpath/sub_agents/` will contain role-focused sub-agents.
- `mcp_server/` will expose selected tools through a future MCP server.
