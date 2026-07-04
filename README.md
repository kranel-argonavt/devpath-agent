# DevPath Agent

DevPath Agent is an AI Career Copilot for junior software developers. It analyzes a job posting, candidate profile, project portfolio, and optional CV context, then produces a deterministic match score, evidence-based gaps, a preparation plan, application drafts, interview prep, and optional Gemini-assisted narrative insights.

## Problem

Junior developers often struggle to translate broad job postings into a concrete preparation plan. Requirements are mixed with nice-to-have skills, seniority signals, language expectations, and vague responsibilities. Candidate evidence is also scattered across profile notes, CV text, and portfolio projects.

DevPath Agent turns that comparison into a structured, explainable workflow that helps a junior developer decide what to highlight, what to improve, and how to prepare before applying.

## Current Architecture

```text
Streamlit UI
   |
Analysis workflow selector
   |-- Standard workflow
   |-- Full agent workflow
   |
agent_workflow.run_career_strategy_workflow
   |
tool_router
   |-- Direct Python services
   |-- Local MCP-style tool registry
   |-- Experimental ADK-MCP runtime tools
   |
deterministic report
   |
optional Gemini structured insights
   |
Markdown export
```

The deterministic report remains the source of truth. Gemini can add concise narrative insight only when explicitly selected and configured with a local API key.

## Current Status

Current status: **Step 7D - Streamlit full agent mode + trace.**

Implemented today:

- Streamlit mock workflow UI
- Editable job posting, candidate profile, portfolio source, CV context, and analysis settings
- Deterministic evidence-based match scoring
- Category score breakdown and category reasons
- Strong, partial, and missing skill classification
- Evidence by skill and portfolio evidence map
- Prioritized skill gaps with recommendations
- Preparation plan, application drafts, and interview prep
- Rich privacy-masked Markdown export
- Optional Gemini-assisted structured insights
- Google ADK-compatible `root_agent` skeleton and sub-agent definitions
- Deterministic agent tools
- MCP-compatible server skeleton and MCP-style tool registry
- Tool backend selector: direct Python services, local MCP-style tools, or experimental ADK-MCP runtime tools
- Experimental MCP stdio runtime adapter for selected manual tool calls
- Local MCP runtime smoke test succeeds with selected deterministic tools
- Experimental ADK-MCP bridge wrappers for selected deterministic tools
- Experimental ADK-MCP runtime tool backend with safe direct fallback
- Workflow runtime metadata in the UI and exported Markdown
- GitHub public repository metadata import as a portfolio source
- GitHub public repository metadata mapped into portfolio evidence
- Full ADK-style deterministic agent workflow with named stages and trace metadata
- Streamlit `Analysis workflow` selector for standard or full agent workflow mode
- Agent Workflow Trace display in Streamlit and exported Markdown
- Local Gemini, ADK, and MCP smoke-test scripts
- Pytest suite for deterministic helpers, workflow, tools, and smoke scripts

Not implemented yet:

- Live ADK runtime routing in Streamlit
- Full MCP runtime workflow integration
- GitHub source-code evidence mapping
- GitHub private repository access
- Source-code repository inspection
- Production deployment

## Agent And Tool Layers

- `devpath/agent.py` exports an ADK-compatible `root_agent` skeleton.
- `devpath/sub_agents/` contains planned specialized agents for job analysis, portfolio evidence, matching, gap planning, application writing, interview coaching, and privacy review.
- `devpath/agent_tools.py` exposes deterministic tool wrappers for future agent orchestration.
- `mcp_server/server.py` exposes an import-safe MCP server skeleton or fallback metadata.
- `mcp_server/tools/` contains MCP-style wrappers around deterministic project logic.
- `devpath/tool_router.py` lets the workflow use direct deterministic services, the local MCP-style registry in-process, or experimental ADK-MCP runtime wrappers.

Streamlit does **not** yet run a full ADK runtime. The experimental ADK-MCP backend is selected manually and only routes selected deterministic tools through local MCP stdio with safe fallback.

## Full Agent Workflow Orchestration

The project includes a full ADK-style deterministic workflow facade in `devpath/full_agent_workflow.py`. Streamlit can now run either the standard deterministic workflow or the full agent workflow through the `Analysis workflow` selector. The full workflow runs the career strategy process through named stages:

- `privacy_guard`
- `job_analyzer`
- `portfolio_evidence`
- `profile_matcher`
- `gap_planner`
- `application_writer`
- `interview_coach`

These stages orchestrate existing deterministic tools and services, produce an agent trace, and attach workflow metadata to the report. The UI displays `Agent Workflow Trace`, and Markdown export includes the same trace when present. Deterministic scoring remains the source of truth; agents must not invent or modify numeric match scores.

## Setup

Windows PowerShell:

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

## Commands

Run tests:

```powershell
python -m pytest --basetemp .pytest_tmp
```

If `.pytest_tmp` is locked on Windows:

```powershell
python -m pytest --basetemp .pytest_tmp_local
```

Run the app:

```powershell
streamlit run app.py
```

Run local smoke tests:

```powershell
python scripts/check_gemini_connection.py
python scripts/check_adk_agent.py
python scripts/check_mcp_tools.py
python scripts/check_mcp_runtime.py
python scripts/check_adk_mcp_tools.py
python scripts/check_full_agent_workflow.py
python scripts/check_github_public_import.py octocat
```

## MCP Runtime Smoke Test

Run the experimental local MCP runtime smoke test:

```powershell
python scripts/check_mcp_runtime.py
```

This starts a local MCP stdio server process and calls selected deterministic tools through MCP runtime. It is separate from the default Streamlit workflow. Step 6A.1 verifies this path against the installed MCP SDK using `ClientSession`, `StdioServerParameters`, `stdio_client`, and `FastMCP.run(transport="stdio")`.

## ADK-MCP Tool Bridge Smoke Test

Run the selected-tool ADK-to-MCP bridge smoke test:

```powershell
python scripts/check_adk_mcp_tools.py
```

This validates that selected ADK-style tool wrappers can call deterministic tools through the local MCP stdio runtime. The default Streamlit workflow does not use this runtime path yet.

The Streamlit workflow can also select `Experimental ADK-MCP runtime tools` as a tool backend. Direct Python services remain the default, and the experimental route falls back to direct deterministic services if the local runtime cannot be used.

The UI now displays workflow runtime metadata, including selected backend, backend used, MCP runtime usage, experimental route status, fallback status, selected tools, and notes. The same safe metadata is included in exported Markdown reports.

## GitHub Public Repository Import

Users can import public repository metadata by GitHub username and use those repositories as portfolio projects.

- No GitHub token is required.
- Only public metadata is used: name, description, URL, language, topics, stars, forks, update timestamps, fork flag, and archived flag.
- Private repositories are not accessed.
- Repositories are not cloned.
- Source code is not downloaded in this step.
- GitHub public repository metadata is mapped into portfolio evidence through language, topics, description, URL, and repository signals.
- Stars and forks are shown as public repository signals, not direct skill proof.

Manual smoke test:

```powershell
python scripts/check_github_public_import.py octocat
```

## Optional Gemini Setup

Mock deterministic mode works without an API key. To test Gemini-assisted summaries locally:

```powershell
Copy-Item .env.example .env
```

Then edit `.env` locally:

```text
GOOGLE_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.5-flash
```

Do not commit `.env`.

## Safety Notes

- `.env` is ignored by Git and must not be committed.
- `.env.example` is safe because it contains empty placeholders.
- Gemini is optional and only runs when explicitly selected.
- The deterministic score, evidence, gaps, and category details are the source of truth.
- Gemini, ADK, and MCP layers may explain or orchestrate, but must not overwrite deterministic score fields.
- Exported Markdown is privacy-masked.
- Generated reports in `outputs/*.md` are ignored by Git.
- Do not paste secrets, passwords, private tokens, or sensitive personal data into the app, prompts, screenshots, or exported reports.

## Project Structure

- `app.py`: Streamlit mock workflow.
- `data/`: sample job posting, profile, and portfolio projects.
- `devpath/agent_workflow.py`: single workflow facade used by Streamlit.
- `devpath/full_agent_workflow.py`: opt-in full ADK-style deterministic workflow with agent trace.
- `devpath/tool_router.py`: local backend selector for direct services or MCP-style tools.
- `devpath/core/`: deterministic scoring, privacy, config, and report helpers.
- `devpath/services/`: file loading, export, Gemini wrapper, and public GitHub metadata import.
- `devpath/agent.py`: ADK-compatible root agent skeleton.
- `devpath/sub_agents/`: ADK-compatible sub-agent skeletons.
- `devpath/agent_tools.py`: deterministic tools for future agent orchestration.
- `mcp_server/`: MCP server skeleton and MCP-style deterministic tools.
- `devpath/mcp_runtime.py`: experimental local MCP stdio runtime adapter.
- `scripts/`: local smoke-test scripts.
- `docs/`: project specification, architecture, security, scoring, roadmap, and demo notes.
- `tests/`: deterministic test suite.
