# Architecture

DevPath Agent is deterministic-first. Scoring, evidence, gaps, and category details are calculated locally and remain the source of truth. Gemini, ADK, and MCP layers explain, orchestrate, or route deterministic tools around that core.

## Runtime Path Today

```text
Streamlit UI
   |
Analysis workflow selector
   |-- Gemini/ADK tool-calling agent
   |-- Standard workflow
   |-- Full agent workflow
   |
portfolio source: sample projects, manual JSON input, or public GitHub metadata
   |
WorkflowInput
   |
run_career_strategy_workflow
   |-- Gemini/ADK tool-calling agent mode
   |      |-- MCP runtime preferred
   |      |-- Local MCP-style registry fallback
   |      |-- Direct deterministic fallback
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

The default demo workflow is now `Gemini/ADK tool-calling agent`. It requests MCP runtime first, falls back to the local MCP-style registry, and finally falls back to direct deterministic services. Local MCP-style tools run in-process through `MCP_TOOL_REGISTRY`; no MCP transport is started for that fallback backend.

For the final capstone demo, Streamlit defaults to Gemini/ADK tool-calling, Gemini-assisted summary, deterministic scoring, and Local sample projects. This shows agent/tool/MCP orchestration while keeping the core demo offline-safe and reproducible when no API key is configured.

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

## Manual Portfolio JSON Input

```text
Manual project JSON array
   |
Streamlit JSON parser and validator
   |
project dictionaries
   |
existing scoring/report workflow
```

Manual JSON input is intended for judge/custom testing when a user wants to provide exact portfolio projects without relying on GitHub usernames, network access, or API rate limits. The parser requires a JSON array of project objects with `name`, optional `summary` or `description`, `technologies`, and optional `url`.

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

Gemini and agents can explain, summarize, or orchestrate these values, but they must not overwrite them.

## Workflow Layer

- `devpath/agent_workflow.py` receives `WorkflowInput` from Streamlit.
- It can run the Gemini/ADK tool-calling mode through `devpath/adk_tool_calling_workflow.py`.
- It can build the deterministic report through `devpath/tool_router.py`.
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

Live deployed ADK runtime routing is not required by the local app. The new tool-calling workflow and the full agent workflow are ADK-style orchestration facades that remain import-safe and testable without a live ADK server.

## Agent Runtime Upgrade Tool-Calling Mode

```text
Gemini/ADK tool-calling agent
   |
privacy_guard -> mask_personal_data
   |
job_analyzer -> extract_job_requirements_with_gemini
   |
job_analyzer -> analyze_job_posting
   |
job_analyzer -> validate_job_requirements
   |
portfolio_evidence -> build_portfolio_summary
   |
profile_matcher -> extract_candidate_context_with_gemini
   |
profile_matcher -> validate_candidate_context
   |
profile_matcher -> calculate_match_score
   |
career_report_builder -> build_career_report
   |
gap_planner -> generate_gap_narrative
   |
gap_planner -> generate_action_plan_narrative
   |
application_writer -> generate_application_drafts
   |
interview_coach -> generate_interview_prep
   |
gemini_narrative -> generate_gemini_career_insights
```

`devpath/adk_tool_calling_workflow.py` coordinates the capstone-grade visible tool-calling route. For deterministic tools, the workflow attempts:

1. MCP runtime through `devpath.mcp_runtime.call_mcp_tool_stdio`
2. Local MCP-style registry through `mcp_server.tools.MCP_TOOL_REGISTRY`
3. Direct deterministic Python tool wrapper

Every tool call records safe metadata in `tool_call_trace`: tool name, agent name, backend used, status, input summary, output summary, fallback flag, and warnings. Raw job posting text, CV text, API keys, and full private inputs are not displayed in the trace.

Gemini structured extraction is bounded: it can extract job/profile/CV facts, but deterministic validators normalize those facts and fall back to deterministic extraction if output is missing or invalid. Gemini narrative writers can enhance Gaps, Action Plan, Application, and Interview sections. Gemini never calculates score fields. After Gemini calls, deterministic profile-match fields are restored from a snapshot.

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

## Step 7D Streamlit Full Agent Mode

```text
Streamlit
   |
Analysis workflow selector
   |-- Standard workflow
   |-- Full agent workflow
       |
       privacy_guard
       job_analyzer
       portfolio_evidence
       profile_matcher
       gap_planner
       application_writer
       interview_coach
   |
report + agent trace + export
```

Step 7D exposed the full deterministic agent workflow in Streamlit. The Agent Runtime Upgrade makes `Gemini/ADK tool-calling agent` the recommended default demo path. The `Agent Workflow Trace` section shows agent metadata, deterministic scoring source, and disabled LLM score modification. The `AI Tool-Calling Trace` section shows the MCP-aware tool route. Exported Markdown includes the same trace metadata when present.

## Step 8A Demo Polish

```text
Load demo scenario
   |
Gemini/ADK tool-calling agent
   |
Generate Career Strategy
   |
Results Dashboard
   |
Evidence + Gaps + Agent Trace + AI Tool-Calling Trace + Runtime + Export
```

The demo path is intentionally local and stable. Optional GitHub import and Gemini narrative output remain available, but they are not required for the main recording.

## MCP Layer

- `mcp_server/server.py` exposes the MCP server skeleton.
- `mcp_server/tools/` contains deterministic MCP-style wrappers.
- `MCP_TOOL_REGISTRY` exposes stable tool names.
- `scripts/check_mcp_tools.py` validates the local MCP-style tool layer.
- `devpath/mcp_runtime.py` can call selected MCP tools through a local stdio runtime for manual smoke testing.

Current MCP-style tools cover local profile/project loading, public GitHub repository metadata, explicit public README fetch, portfolio summary, scoring, report generation, privacy detection/masking, and Markdown export.

MCP stdio is requested by the default tool-calling workflow and can fall back safely if unavailable. Automated tests use dependency injection and do not require a live MCP transport.

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

`scripts/check_mcp_runtime.py` is a controlled local runtime proof. It starts a local stdio MCP server process only when explicitly run and calls selected deterministic tools through the installed MCP SDK. Streamlit's tool-calling mode also requests this runtime first, then falls back safely when unavailable.

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

`scripts/check_adk_mcp_tools.py` validates that selected ADK-style wrappers can call local MCP runtime tools. Deterministic scoring remains the source of truth.

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

The Step 6C backend remains available as a legacy selector path. The newer tool-calling workflow uses the same fallback principle across the whole career workflow and exposes each tool call in the Runtime tab.

## Step 6D Runtime Transparency

Step 6D made the experimental ADK-MCP route visible and demo-friendly in Streamlit. The Agent Runtime Upgrade makes the MCP-aware tool-calling route the default demo workflow.

The report now carries safe `runtime_route` metadata:

- Selected/requested backend
- Actual backend used
- MCP runtime usage
- Experimental route status
- Fallback status
- Selected tools
- Human-readable notes

This metadata is displayed in the Streamlit `Workflow Runtime` section and exported to Markdown. The `AI Tool-Calling Trace` adds safe per-tool summaries. Neither section includes raw tool inputs, secrets, API keys, or private user data.

## Gemini Layer

- Gemini is optional.
- Gemini-assisted mode is selected by default for the capstone demo, but calls only succeed when a local API key is configured.
- Gemini returns structured extraction and narrative sections such as job requirements, candidate context, gap narrative, action plan, application drafts, and interview prep.
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

The Kaggle writeup and video script are planned next. GitHub features should remain public-repo-only unless a secure permission model is added.
