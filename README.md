# DevPath Agent

DevPath Agent is an AI career copilot designed to help junior software developers understand how well they match a job posting, identify missing skills, and build a focused improvement plan.

## Problem Statement

Junior developers often struggle to translate their profile and portfolio into evidence that fits a real job posting. Requirements are spread across job ads, project repositories, CVs, and personal notes, which makes gap analysis slow and inconsistent.

## Planned Solution

DevPath Agent will eventually:

- analyze a job posting and extract structured requirements;
- compare those requirements against a candidate profile and portfolio projects;
- identify strengths, missing skills, and evidence gaps;
- generate a personalized career strategy, application materials, and interview preparation guidance.

## Planned Architecture

The project is organized around a future root agent in `devpath/agent.py`, supported by specialized sub-agents for job analysis, portfolio evidence extraction, profile matching, gap planning, application writing, interview coaching, and privacy checks.

Supporting modules are grouped into:

- `devpath/core/` for deterministic utilities like scoring, configuration, reports, and privacy;
- `devpath/schemas/` for shared dataclass models;
- `devpath/services/` for future integrations such as file handling, exports, and GitHub access;
- `mcp_server/` for future MCP server placeholders and tool modules;
- `data/` for sample inputs;
- `docs/` for project planning and design notes.

## Current Status

Current status: **Project skeleton**

This repository currently contains:

- a minimal Streamlit app;
- placeholder modules and future architecture stubs;
- realistic sample data for local development;
- starter documentation and lightweight tests.

No real LLM calls, Gemini API logic, Google ADK logic, MCP server logic, or GitHub API integration are implemented yet.

## Setup

### 1. Create and activate a virtual environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Create a local environment file

```powershell
Copy-Item .env.example .env
```

## Run The Minimal App

```powershell
streamlit run app.py
```

The app currently shows a title, subtitle, and a short Step 1A status message.

## Environment Variables

The project reserves these variables for future integration work:

- `GOOGLE_API_KEY`
- `GITHUB_TOKEN`

They are intentionally unused in this step.

## Security Notes

- Do not commit `.env` files or real API keys.
- Sample data is synthetic and safe for local development.
- Privacy and masking logic is not complete yet; current privacy utilities are placeholders only.

## Planned Next Steps

1. Build the first real Streamlit workflow for loading sample inputs.
2. Add deterministic job-to-profile matching utilities.
3. Expand reports and scoring outputs.
4. Introduce controlled integration layers for Gemini, ADK, MCP, and GitHub in later phases.
