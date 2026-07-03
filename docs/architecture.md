# Architecture

The current architecture remains simple and testable. Deterministic scoring is still the source of truth, Gemini is only an optional narrative layer, Step 4A added an ADK-compatible skeleton, and Step 4B adds a local validation workflow without changing the Streamlit runtime path.

## Current App Runtime

```text
Streamlit UI
   |
Deterministic services
   |
Scoring/report/privacy
   |
Markdown export
```

## Optional Gemini Layer

```text
Streamlit UI
   |
Deterministic scoring/report/export
   |
Optional Gemini-assisted narrative summary
```

Gemini-assisted mode can improve the written career summary, but it must not change the numeric match score, category scores, missing skills, or evidence mapping.

## Step 4A Agent Foundation

```text
ADK root_agent
   |
Deterministic tools
   |
Scoring/report/privacy
```

The root agent and sub-agents are importable skeletons. They expose planned responsibilities and deterministic tools, but the Streamlit app does not fully route generation through ADK yet.

## Step 4B Local Validation

```text
scripts/check_adk_agent.py
   |
root_agent import + sub-agent factories
   |
deterministic tool smoke checks
```

The smoke test validates project structure, ADK availability or fallback metadata, deterministic tools, and basic scoring/privacy behavior. It does not start `adk run`, `adk web`, Gemini, MCP, GitHub, or any external API.

## Future Agent Flow

```text
ADK Root Agent
   |
Sub-agents
   |
MCP tools
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
- `devpath/agent.py` exposes the ADK-compatible root agent skeleton.
- `devpath/agent_tools.py` wraps deterministic scoring, report, portfolio, and privacy helpers as future ADK tools.
- `scripts/check_adk_agent.py` validates the local ADK skeleton without starting an ADK runtime server.

## Agent Modules

- `devpath/agent.py` is the ADK root agent entry point.
- `devpath/sub_agents/` contains role-focused sub-agent skeletons.
- `mcp_server/` will expose selected tools through a future MCP server.

When ready for manual ADK runtime exploration, use ADK CLI commands such as `adk run` or `adk web` according to the official ADK documentation. Those commands are intentionally outside the automated test suite.
