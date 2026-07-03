# Architecture

DevPath Agent is deterministic-first. Scoring, evidence, gaps, and category details are calculated locally and remain the source of truth. Gemini, ADK, and MCP layers are currently used as optional narrative, skeleton, or tool-contract layers around that deterministic core.

## Runtime Path Today

```text
Streamlit UI
   |
WorkflowInput
   |
run_career_strategy_workflow
   |
tool_router
   |-- Direct Python services
   |-- Local MCP-style tool registry
   |
deterministic report
   |
optional Gemini insights
   |
UI tabs + Markdown export
```

Direct Python services are the default backend. Local MCP-style tools run in-process through `MCP_TOOL_REGISTRY`; no MCP transport is started.

## Deterministic Source Of Truth

The following values are deterministic:

- Overall score
- Category scores
- Category details
- Strong matches
- Partial matches
- Missing skills
- Evidence by skill
- Prioritized gaps

Gemini and future agents can explain, summarize, or orchestrate these values, but they must not overwrite them.

## Workflow Layer

- `devpath/agent_workflow.py` receives `WorkflowInput` from Streamlit.
- It builds the deterministic report through `devpath/tool_router.py`.
- It optionally attaches Gemini structured insights.
- It returns `WorkflowResult` with the final report and user-facing warnings.

If Gemini is selected but no API key is configured, the workflow returns the deterministic report and a warning. If Gemini fails, the workflow also falls back safely.

## Tool Router

`devpath/tool_router.py` supports two local backends:

- `Direct Python services`
- `Local MCP-style tools`

The direct backend calls deterministic Python helpers. The MCP-style backend calls the local MCP tool registry in-process. Unknown backend names normalize to the direct backend.

## ADK Layer

- `devpath/agent.py` exports `root_agent`.
- `devpath/sub_agents/` contains planned specialized agents.
- `devpath/agent_tools.py` exposes deterministic tools for future agent orchestration.
- `scripts/check_adk_agent.py` validates the local ADK-compatible skeleton.

ADK runtime routing is not the default app runtime yet.

## MCP Layer

- `mcp_server/server.py` exposes the MCP server skeleton.
- `mcp_server/tools/` contains deterministic MCP-style wrappers.
- `MCP_TOOL_REGISTRY` exposes stable tool names.
- `scripts/check_mcp_tools.py` validates the local MCP-style tool layer.

No MCP stdio, HTTP, SSE, or Streamable HTTP transport is started automatically or during tests.

## Gemini Layer

- Gemini is optional.
- Gemini calls only happen when the user selects Gemini-assisted mode and provides a local API key.
- Gemini returns structured narrative sections such as summary, top actions, portfolio positioning, gap strategy, and interview focus.
- Gemini does not calculate or modify deterministic scores.

## Current Smoke Tests

```powershell
python scripts/check_gemini_connection.py
python scripts/check_adk_agent.py
python scripts/check_mcp_tools.py
```

These scripts validate integration readiness without changing the deterministic source of truth. Automated tests do not require real API keys.

## Future Architecture

```text
Streamlit UI
   |
ADK root_agent
   |
sub-agents
   |
MCP runtime tools
   |
deterministic services + optional Gemini narrative
```

GitHub public repository import is planned later and should remain public-repo-only unless a secure permission model is added.
