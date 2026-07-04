# Architecture

DevPath Agent is deterministic-first. Scoring, evidence, gaps, and category details are calculated locally and remain the source of truth. Gemini, ADK, and MCP layers explain, orchestrate, or route deterministic tools around that core.

## Runtime Path Today

```text
Streamlit UI
   |
portfolio source: sample projects or public GitHub metadata
   |
WorkflowInput
   |
run_career_strategy_workflow
   |
tool_router
   |-- Direct Python services
   |-- Local MCP-style tool registry
   |-- Experimental ADK-MCP runtime tools
   |
deterministic report
   |
optional Gemini insights
   |
UI tabs + Markdown export
```

Direct Python services are the default backend. Local MCP-style tools run in-process through `MCP_TOOL_REGISTRY`; no MCP transport is started for that backend. The experimental ADK-MCP backend can start a local MCP stdio runtime for selected deterministic tools and falls back safely through the workflow if unavailable.

## GitHub Public Repository Import

```text
GitHub username
   |
github_service.fetch_public_github_repositories
   |
public repo metadata
   |
convert_github_repos_to_projects
   |
GitHub evidence mapper
   |
existing scoring/report workflow
```

GitHub import feeds the portfolio source in Streamlit. GitHub public metadata is mapped into deterministic evidence through language, topics, description, URL, and repository signals, then passed into the existing scoring/report/export workflow. It uses public repository metadata only and does not require a token, access private repositories, scrape HTML, clone repositories, or download source code. It does not replace deterministic scoring.

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

`devpath/tool_router.py` supports three local backends:

- `Direct Python services`
- `Local MCP-style tools`
- `Experimental ADK-MCP runtime tools`

The direct backend calls deterministic Python helpers. The MCP-style backend calls the local MCP tool registry in-process. The experimental backend validates selected ADK-MCP runtime calls and falls back safely through the workflow if unavailable. Unknown backend names normalize to the direct backend.

## ADK Layer

- `devpath/agent.py` exports `root_agent`.
- `devpath/sub_agents/` contains planned specialized agents.
- `devpath/agent_tools.py` exposes deterministic tools for future agent orchestration.
- `devpath/adk_mcp_tools.py` exposes selected experimental wrappers that can call MCP runtime tools.
- `devpath/full_agent_workflow.py` runs the full ADK-style deterministic workflow and records an agent trace.
- `scripts/check_adk_agent.py` validates the local ADK-compatible skeleton.
- `scripts/check_full_agent_workflow.py` validates the deterministic full agent workflow.

Live ADK runtime routing is not the default app runtime yet. The full agent workflow is an ADK-style deterministic orchestration facade that remains import-safe and testable without a live ADK server.

## Step 7C Full ADK-Style Workflow

```text
Full ADK-style workflow
   |
privacy_guard
   |
job_analyzer
   |
portfolio_evidence
   |
profile_matcher
   |
deterministic scoring tool
   |
gap_planner
   |
application_writer
   |
interview_coach
   |
final report
```

`run_full_agent_workflow` coordinates the named stages, calls deterministic services, and adds `agent_workflow` plus serialized `agent_trace` metadata to the report. Automated tests do not require live ADK runtime execution. MCP runtime can still be used by selected backends, but the full workflow defaults to deterministic direct behavior unless configured otherwise.

## MCP Layer

- `mcp_server/server.py` exposes the MCP server skeleton.
- `mcp_server/tools/` contains deterministic MCP-style wrappers.
- `MCP_TOOL_REGISTRY` exposes stable tool names.
- `scripts/check_mcp_tools.py` validates the local MCP-style tool layer.
- `devpath/mcp_runtime.py` can call selected MCP tools through a local stdio runtime for manual smoke testing.

No MCP stdio, HTTP, SSE, or Streamable HTTP transport is started automatically or during tests.

## Step 6A.1 MCP Runtime Proof

```text
Manual MCP runtime smoke test
   |
devpath.mcp_runtime
   |
local MCP stdio server
   |
MCP tools
   |
deterministic services
```

`scripts/check_mcp_runtime.py` is a controlled local runtime proof. It starts a local stdio MCP server process only when explicitly run and calls selected deterministic tools through the installed MCP SDK. Streamlit still does not use MCP runtime by default, and ADK tools are not routed through MCP runtime yet.

## Step 6B ADK-MCP Tool Bridge

```text
ADK-style tool wrapper
   |
devpath.mcp_runtime
   |
local MCP stdio server
   |
MCP deterministic tools
   |
core scoring/privacy logic
```

`scripts/check_adk_mcp_tools.py` validates that selected ADK-style wrappers can call local MCP runtime tools. This is selected-tool bridging only: Streamlit is not routed through full ADK runtime orchestration yet, and deterministic scoring remains the source of truth.

## Step 6C Experimental Workflow Backend

```text
Streamlit UI
   |
agent_workflow
   |
tool_router
   |
Experimental ADK-MCP runtime tools
   |
ADK-style wrappers
   |
MCP runtime adapter
   |
local MCP stdio server
   |
deterministic tools
```

The Step 6C backend is opt-in. It builds the report shape through deterministic report logic, validates selected job-analysis and match-score calls through ADK-MCP wrappers, records runtime route metadata, and falls back to direct deterministic services if runtime startup or tool calls fail.

## Step 6D Runtime Transparency

Step 6D makes the experimental ADK-MCP route visible and demo-friendly in Streamlit, while keeping Direct Python services as the default.

The report now carries safe `runtime_route` metadata:

- Selected/requested backend
- Actual backend used
- MCP runtime usage
- Experimental route status
- Fallback status
- Selected tools
- Human-readable notes

This metadata is displayed in the Streamlit `Workflow Runtime` section and exported to Markdown. It does not include tool inputs, secrets, API keys, or private user data.

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
python scripts/check_mcp_runtime.py
python scripts/check_adk_mcp_tools.py
python scripts/check_full_agent_workflow.py
python scripts/check_github_public_import.py octocat
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

Streamlit full agent mode and trace polish are planned next. GitHub features should remain public-repo-only unless a secure permission model is added.
