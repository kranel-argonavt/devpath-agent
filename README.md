# DevPath Agent

DevPath Agent is an AI Career Copilot for junior software developers. It helps a candidate compare a job posting against their profile and portfolio, identify skill gaps, and generate a focused preparation plan.

## Problem Statement

Junior developers often struggle to understand whether they are truly ready for a role. Job postings mix required skills, preferred skills, responsibilities, language expectations, and vague seniority signals. Candidate evidence is also scattered across CV text, profile notes, and portfolio projects. DevPath Agent turns that comparison into a structured, explainable workflow.

## Solution Overview

The current MVP runs fully locally in Streamlit. It loads sample job, profile, and project data, applies deterministic keyword-based scoring, builds a mock career strategy report, and exports the result as Markdown.

The final planned system will add Gemini-powered reasoning, a Google ADK root agent with specialized sub-agents, MCP tools, and public GitHub repository import.

## Current Status

Current status: **Step 1D - polished mock MVP with deterministic local logic.**

No Gemini API calls, Google ADK runtime logic, MCP server logic, real GitHub API calls, or real LLM calls are implemented yet.

## Implemented Features

- Streamlit mock workflow UI
- Sample job posting/profile/projects
- Editable candidate profile
- Deterministic keyword-based match scoring
- Skill gap summary
- Portfolio evidence display
- Preparation plan
- Application draft mock output
- Interview prep mock output
- Markdown report export
- Privacy masking utilities
- Pytest test suite

## Planned Features

- Gemini API integration
- Google ADK root agent and sub-agents
- MCP server tools
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

## Environment Variables

The project reserves these variables for future integration work:

- `GOOGLE_API_KEY`
- `GITHUB_TOKEN`

Use `.env.example` as the safe template. The current mock MVP does not use these values.

## Security Notes

- `.env` is ignored and should contain local secrets only.
- `.env.example` is safe to commit because it contains empty placeholders.
- Generated reports in `outputs/*.md` are ignored by Git.
- The current MVP makes no real external API calls.
- Do not paste secrets, passwords, private tokens, or sensitive personal data into the app.

## Architecture Overview

Current local flow:

```text
Streamlit UI
   -> local file services
   -> deterministic scoring + privacy + report builder
   -> Markdown export
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
- `devpath/core/` contains deterministic scoring, privacy, config, and report helpers.
- `devpath/services/` contains local file loading, export, and future GitHub service placeholders.
- `devpath/sub_agents/` contains placeholders for future specialized agents.
- `mcp_server/` contains placeholders for future MCP server tools.
- `docs/` contains project specification, architecture, security, scoring, roadmap, and demo notes.
- `tests/` contains deterministic helper tests.

## Kaggle Capstone Concepts Planned

The project is designed to demonstrate practical agent planning, explainable scoring, privacy-aware data handling, human-centered career guidance, and staged delivery from deterministic MVP to agent-assisted workflow.
