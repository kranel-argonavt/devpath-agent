# DevPath Agent

DevPath Agent is an AI Career Copilot for junior software developers. It analyzes a job posting, candidate profile, project portfolio, and optional CV context, then produces a deterministic match score, evidence-based gaps, a preparation plan, application drafts, interview prep, and optional Gemini-assisted narrative insights.

## Problem

Junior developers often struggle to translate broad job postings into a concrete preparation plan. Requirements are mixed with nice-to-have skills, seniority signals, language expectations, and vague responsibilities. Candidate evidence is also scattered across profile notes, CV text, and portfolio projects.

DevPath Agent turns that comparison into a structured, explainable workflow that helps a junior developer decide what to highlight, what to improve, and how to prepare before applying.

## Current Architecture

```text
Streamlit UI
   |
agent_workflow.run_career_strategy_workflow
   |
tool_router
   |-- Direct Python services
   |-- Local MCP-style tool registry
   |
deterministic report
   |
optional Gemini structured insights
   |
Markdown export
```

The deterministic report remains the source of truth. Gemini can add concise narrative insight only when explicitly selected and configured with a local API key.

## Current Status

Current status: **Step 6A - MCP runtime adapter and selected tool smoke test.**

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
- Tool backend selector: direct Python services or local MCP-style tools
- Experimental MCP stdio runtime adapter for selected manual tool calls
- Local Gemini, ADK, and MCP smoke-test scripts
- Pytest suite for deterministic helpers, workflow, tools, and smoke scripts

Not implemented yet:

- Full ADK runtime routing
- MCP runtime transport integration
- GitHub API integration
- Source-code repository inspection
- Production deployment

## Agent And Tool Layers

- `devpath/agent.py` exports an ADK-compatible `root_agent` skeleton.
- `devpath/sub_agents/` contains planned specialized agents for job analysis, portfolio evidence, matching, gap planning, application writing, interview coaching, and privacy review.
- `devpath/agent_tools.py` exposes deterministic tool wrappers for future agent orchestration.
- `mcp_server/server.py` exposes an import-safe MCP server skeleton or fallback metadata.
- `mcp_server/tools/` contains MCP-style wrappers around deterministic project logic.
- `devpath/tool_router.py` lets the workflow use either direct deterministic services or the local MCP-style registry in-process.

Streamlit does **not** yet run a full ADK or MCP runtime. That routing is planned for later.

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
```

## MCP Runtime Smoke Test

Run the experimental local MCP runtime smoke test:

```powershell
python scripts/check_mcp_runtime.py
```

This starts a local MCP stdio server process and calls selected deterministic tools through MCP runtime. It is separate from the default Streamlit workflow. If the installed MCP SDK/runtime behaves differently, the script should print a clean diagnostic message instead of exposing secrets.

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
- `devpath/tool_router.py`: local backend selector for direct services or MCP-style tools.
- `devpath/core/`: deterministic scoring, privacy, config, and report helpers.
- `devpath/services/`: file loading, export, Gemini wrapper, and future GitHub placeholder.
- `devpath/agent.py`: ADK-compatible root agent skeleton.
- `devpath/sub_agents/`: ADK-compatible sub-agent skeletons.
- `devpath/agent_tools.py`: deterministic tools for future agent orchestration.
- `mcp_server/`: MCP server skeleton and MCP-style deterministic tools.
- `devpath/mcp_runtime.py`: experimental local MCP stdio runtime adapter.
- `scripts/`: local smoke-test scripts.
- `docs/`: project specification, architecture, security, scoring, roadmap, and demo notes.
- `tests/`: deterministic test suite.
