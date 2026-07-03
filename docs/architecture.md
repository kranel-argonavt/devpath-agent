# Architecture

The current architecture remains simple and testable. Deterministic scoring is still the source of truth, Gemini is only an optional narrative layer, Step 4 added the ADK-compatible workflow foundation, and Step 5 connects the workflow to either direct services or local MCP-style tools without starting a runtime transport.

## Current App Runtime

```text
Streamlit UI
   |
agent_workflow.run_career_strategy_workflow
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

## Current Step 4C Runtime

```text
Streamlit UI
   |
devpath.agent_workflow.run_career_strategy_workflow
   |
deterministic report builder / agent tools
   |
optional Gemini structured insights
   |
final report
   |
Markdown export
```

The workflow facade gives the app one stable orchestration entry point. Mock deterministic mode and Gemini-assisted mode both use the same workflow path. Gemini insights are attached as narrative-only output and do not modify deterministic score fields.

## Step 5A Tool Layer

```text
MCP server skeleton
   |
MCP-style deterministic tools
   |
core scoring / report / privacy / export services
```

The MCP server skeleton is importable and testable. It exposes stable tool contracts for scoring, portfolio evidence, report building, privacy masking, and Markdown export. The Streamlit app does not yet route through MCP runtime, and tests do not start stdio, HTTP, SSE, or Streamable HTTP transports.

## Step 5B Local Validation

```text
scripts/check_mcp_tools.py
   |
MCP server metadata + tool registry
   |
deterministic scoring / report / privacy / export checks
```

The MCP smoke test validates the local MCP-compatible tool layer without starting a real MCP transport. Streamlit still uses `agent_workflow.run_career_strategy_workflow` directly.

## Step 5C Workflow Routing

```text
Streamlit UI
   |
agent_workflow
   |
tool_router
   |-- Direct Python services
   |-- Local MCP-style tool registry
   |
deterministic report
   |
optional Gemini structured insights
```

The local MCP-style backend calls `MCP_TOOL_REGISTRY` in-process. It does not start stdio, HTTP, SSE, or Streamable HTTP transports. Direct Python services remain the default backend.

## Future Agent Flow

```text
ADK Root Agent
   |
Sub-agents
   |
MCP tools
   |
deterministic services + optional Gemini narrative
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
- `devpath/agent_workflow.py` coordinates deterministic report generation and optional Gemini insights for the Streamlit app.
- `devpath/tool_router.py` selects direct deterministic services or local MCP-style tools.
- `scripts/check_adk_agent.py` validates the local ADK skeleton without starting an ADK runtime server.
- `mcp_server/server.py` exposes an import-safe MCP server skeleton or fallback metadata.
- `mcp_server/tools/` exposes MCP-style deterministic tool contracts and a local registry.
- `scripts/check_mcp_tools.py` validates MCP-style tools locally with temporary export output only.

## Agent Modules

- `devpath/agent.py` is the ADK root agent entry point.
- `devpath/sub_agents/` contains role-focused sub-agent skeletons.
- `mcp_server/` exposes MCP-style deterministic tool contracts. Runtime transport integration is planned later.

When ready for manual ADK runtime exploration, use ADK CLI commands such as `adk run` or `adk web` according to the official ADK documentation. Those commands are intentionally outside the automated test suite.
