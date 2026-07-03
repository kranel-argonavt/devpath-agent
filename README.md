# DevPath Agent

DevPath Agent is an AI Career Copilot for junior software developers. It helps a candidate compare a job posting against their profile and portfolio, identify skill gaps, and generate a focused preparation plan.

## Problem Statement

Junior developers often struggle to understand whether they are truly ready for a role. Job postings mix required skills, preferred skills, responsibilities, language expectations, and vague seniority signals. Candidate evidence is also scattered across CV text, profile notes, and portfolio projects. DevPath Agent turns that comparison into a structured, explainable workflow.

## Solution Overview

The current MVP runs in Streamlit. It loads sample job, profile, and project data, applies deterministic evidence-based scoring, builds a mock career strategy report, and exports the result as structured Markdown. Gemini-assisted structured insights are optional and disabled by default. Step 4 added the ADK-compatible agent foundation and workflow facade. Step 5 adds MCP-compatible tool contracts, local MCP validation, and an in-process tool backend selector.

The final planned system will add Gemini-powered reasoning, a Google ADK root agent with specialized sub-agents, MCP tools, and public GitHub repository import.

## Current Status

Current status: **Step 5C - workflow backend selector for direct services or local MCP-style tools.**

Gemini calls only happen if the user explicitly selects Gemini-assisted summary mode and configures an API key. The Streamlit app calls `devpath.agent_workflow.run_career_strategy_workflow`, which still uses deterministic report generation as the source of truth. The workflow can use direct deterministic services or local MCP-style tools in-process. No MCP transport is started yet. Full ADK/MCP runtime routing and real GitHub API calls are planned for later steps.

## Implemented Features

- Streamlit mock workflow UI
- Sample job posting/profile/projects
- Editable candidate profile
- Deterministic evidence-based match scoring
- Evidence-based score breakdown
- Category-level scoring details
- Evidence by skill
- Prioritized skill gaps with recommendations
- Skill gap summary
- Portfolio evidence display
- Preparation plan
- Application draft mock output
- Interview prep mock output
- Markdown report export
- Rich Markdown report export
- Exported evidence-based score breakdown
- Exported prioritized skill gaps and recommendations
- Optional structured Gemini-assisted career summary
- AI career summary, top actions, portfolio positioning, skill gap strategy, and interview focus areas
- Local Gemini connection smoke-test script
- Google ADK-compatible root agent skeleton
- Planned sub-agent architecture
- Deterministic tools exposed for future agent use
- Local ADK agent smoke-test script
- Agent workflow facade used by Streamlit
- Optional Gemini insights attached as narrative-only report output
- MCP-compatible server skeleton
- MCP-style deterministic tool contracts
- Local tool registry for scoring, report, privacy, portfolio, and export tools
- Local MCP smoke-test script
- Workflow backend selector for direct deterministic services or local MCP-style tools
- Local MCP-style tools run in-process through the registry
- Privacy masking utilities
- Pytest test suite

## Planned Features

- Full Google ADK runtime routing from the Streamlit workflow
- Full MCP runtime integration with ADK tools
- GitHub public repository import
- Better evidence-based scoring
- Kaggle demo assets and video

## Setup On Windows PowerShell

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

## Run Tests

```powershell
python -m pytest --basetemp .pytest_tmp
```

## Optional Gemini Local Test

Mock deterministic mode works without a Gemini API key. To test the optional Gemini-assisted summary locally:

```powershell
Copy-Item .env.example .env
```

Manually edit `.env` and add your local key:

```text
GOOGLE_API_KEY=your_key_here
GEMINI_MODEL=gemini-3.5-flash/gemini-2.5-flash/...
```

Then run:

```powershell
python scripts/check_gemini_connection.py
```

`.env` is ignored by Git. Do not commit API keys. Gemini is used only for structured narrative explanation; deterministic scoring remains the source of truth.

## ADK Local Smoke Test

Validate the local ADK-compatible agent skeleton and deterministic tools:

```powershell
python scripts/check_adk_agent.py
```

This imports `root_agent`, validates sub-agent factories, checks deterministic tools, and runs a tiny scoring/privacy smoke check. It does not start the ADK runtime, does not run `adk run` or `adk web`, and does not make external API calls.

When ready for manual ADK runtime exploration, use ADK CLI commands such as `adk run` or `adk web` according to the official ADK documentation. These commands are not required for the current MVP tests.

## MCP Local Smoke Test

Validate the MCP-compatible tool registry and deterministic tool wrappers:

```powershell
python scripts/check_mcp_tools.py
```

This checks MCP server metadata, the local tool registry, scoring, portfolio, report, privacy, and export tools. It does not start an MCP transport and does not make external API calls.

## Environment Variables

The project reserves these variables for future integration work:

- `GOOGLE_API_KEY`
- `GEMINI_API_KEY`
- `GEMINI_MODEL`
- `GITHUB_TOKEN`

Use `.env.example` as the safe template. For optional Gemini-assisted summaries, create a local `.env` file like:

```text
GOOGLE_API_KEY=your_key_here
GEMINI_MODEL=gemini-3.5-flash/gemini-2.5-flash/...
```

`GEMINI_API_KEY` is also supported as a fallback. Do not commit real keys. Gemini does not calculate the match score. The deterministic score remains the source of truth even when Gemini-assisted summary mode is enabled.

## Security Notes

- `.env` is ignored and should contain local secrets only.
- `.env.example` is safe to commit because it contains empty placeholders.
- Gemini API keys must never be committed, pasted into prompts, shared in screenshots, or included in exported reports.
- Generated reports in `outputs/*.md` are ignored by Git.
- The current MVP makes no real external API calls unless Gemini-assisted summary mode is explicitly selected with an API key configured.
- Do not paste secrets, passwords, private tokens, or sensitive personal data into the app.

## Architecture Overview

Current local flow:

```text
Streamlit UI
   -> local file services
   -> deterministic scoring + privacy + report builder
   -> Markdown export
```

Step 4A agent foundation:

```text
ADK root_agent
   -> deterministic tools
   -> scoring/report/privacy
```

Current Step 4C runtime:

```text
Streamlit UI
   -> agent_workflow.run_career_strategy_workflow
   -> deterministic report builder / agent tools
   -> optional Gemini structured insights
   -> Markdown export
```

Step 5A tool layer:

```text
MCP server skeleton
   -> MCP-style deterministic tools
   -> core scoring / report / privacy / export services
```

Step 5C workflow routing:

```text
Streamlit UI
   -> agent_workflow
   -> tool_router
      -> Direct Python services
      -> Local MCP-style tool registry
   -> deterministic report
   -> optional Gemini structured insights
```

Future agent flow:

```text
Streamlit UI
   -> ADK root agent
   -> specialized sub-agents + MCP tools
   -> Gemini + public GitHub repository import
```

## Project Structure Summary

- `app.py` contains the Streamlit mock workflow.
- `data/` contains sample job, profile, and project inputs.
- `devpath/agent.py` exposes the ADK-compatible `root_agent` skeleton.
- `devpath/agent_tools.py` exposes deterministic tools for future agent orchestration.
- `devpath/tool_router.py` selects direct deterministic services or local MCP-style tools.
- `devpath/core/` contains deterministic scoring, privacy, config, and report helpers.
- `devpath/services/` contains local file loading, export, and future GitHub service placeholders.
- `devpath/sub_agents/` contains ADK-compatible specialized agent skeletons.
- `mcp_server/` contains the MCP-compatible server skeleton and deterministic tool registry.
- `docs/` contains project specification, architecture, security, scoring, roadmap, and demo notes.
- `tests/` contains deterministic helper tests.

## Kaggle Capstone Concepts Planned

The project is designed to demonstrate practical agent planning, explainable scoring, privacy-aware data handling, human-centered career guidance, and staged delivery from deterministic MVP to agent-assisted workflow.
