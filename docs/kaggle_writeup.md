# DevPath Agent - AI Career Copilot for Junior Software Developers

## Subtitle

An explainable concierge agent that turns a job posting, candidate profile, portfolio projects, and optional CV context into a practical career strategy for junior software developers.

## Track

Concierge Agents

DevPath Agent fits the Concierge Agents track because it is a personal assistant for an individual user. It helps junior developers understand where they stand against a specific role, what evidence they should highlight, and what they should prepare next, while keeping personal data handling cautious and transparent.

## Project Links

- Public project link: https://github.com/kranel-argonavt/devpath-agent
- Demo video: https://youtu.be/kvx_5-GBpkg
- Architecture diagram: `assets/architecture/devpath-agent-architecture.png`

## Problem

Junior developers often struggle to understand whether they are ready for a role. Job postings mix required skills, nice-to-have skills, responsibilities, seniority expectations, language requirements, and vague signals such as "good communication" or "portfolio projects preferred." At the same time, a candidate's evidence is spread across a profile, CV text, GitHub repositories, and project descriptions.

This creates a practical problem: candidates do not just need a match score. They need to know why they match, where their evidence is weak, what to highlight in an application, and what to improve before an interview.

## Solution

DevPath Agent is a Streamlit-based AI career copilot for junior software developers. The user provides:

- a pasted job posting,
- a candidate profile,
- local sample projects, manual portfolio JSON, or public GitHub repositories,
- optional CV context.

The app produces:

- a deterministic match score,
- extracted job requirements,
- strong and partial matches,
- missing or weak skills,
- portfolio evidence by skill,
- prioritized gaps,
- a 7-day, 14-day, and 30-day preparation plan,
- cover letter and recruiter message drafts,
- interview questions and practice focus areas,
- a privacy-masked Markdown export.

The default demo scenario is a Junior Frontend React Developer role. It is designed so judges can run the app locally without private data, accounts, or a required paid service.

## Why Agents?

This project is useful as an agent system because the career workflow naturally has multiple responsibilities:

- a privacy guard masks sensitive input,
- a job analyzer extracts role requirements,
- a portfolio evidence agent maps projects to skills,
- a profile matcher calculates evidence-based fit,
- a gap planner turns missing evidence into a preparation roadmap,
- an application writer drafts job-specific messages,
- an interview coach creates role-specific practice questions.

Instead of presenting one monolithic LLM response, DevPath Agent exposes a staged workflow with visible trace metadata. This makes the system easier to inspect, explain, test, and demonstrate.

## Architecture

The architecture is deterministic-first. Gemini, ADK-style agents, and MCP tools are used to orchestrate, extract, explain, or route work around a deterministic core. The score, evidence, and canonical gaps remain local and auditable.

High-level flow:

1. Streamlit collects job, profile, portfolio, CV, and demo settings.
2. The workflow runs in the default Gemini/ADK tool-calling agent mode.
3. Privacy masking is applied before sensitive context is used.
4. Gemini can perform bounded structured extraction for job and candidate context.
5. Deterministic validators normalize or reject Gemini output.
6. MCP-first deterministic tools build the portfolio summary, score, evidence, and report.
7. Gemini narrative writers can improve Gaps, Action Plan, Application, and Interview sections.
8. The Runtime tab displays Agent Workflow Trace, AI Tool-Calling Trace, and Workflow Runtime metadata.
9. Markdown export includes the report and safe trace metadata.

The important boundary is that Gemini may explain, but it cannot change the numeric score or canonical evidence fields.

## Course Concepts Demonstrated

This submission demonstrates more than the minimum three required course concepts. The strongest evidence is in the public codebase and the Runtime tab of the demo UI.

### 1. Agent / Multi-Agent System With ADK-Style Architecture

The repository includes an ADK-compatible `root_agent` in `devpath/agent.py` and specialized sub-agent modules under `devpath/sub_agents/`. Streamlit also exposes a full ADK-style deterministic workflow and a capstone-grade Gemini/ADK tool-calling mode.

The visible agent stages include:

- `privacy_guard`
- `job_analyzer`
- `portfolio_evidence`
- `profile_matcher`
- `career_report_builder`
- `gap_planner`
- `application_writer`
- `interview_coach`
- `gemini_narrative`

The Runtime tab shows these stages so judges can see how the career workflow is coordinated.

### 2. MCP Server And Tool Use

The project includes an MCP server skeleton in `mcp_server/server.py` and MCP-style tools under `mcp_server/tools/`. The default tool-calling workflow requests MCP runtime first, then falls back to the local MCP-style registry, and finally to direct deterministic Python services.

The AI Tool-Calling Trace shows tool calls such as:

- `mask_personal_data`
- `analyze_job_posting`
- `build_portfolio_summary`
- `calculate_match_score`
- `build_career_report`
- `generate_gap_narrative`
- `generate_action_plan_narrative`
- `generate_application_drafts`
- `generate_interview_prep`

Each trace entry displays the tool name, agent name, backend used, status, input summary, output summary, fallback status, and warnings.

### 3. Security And Privacy Features

The app is designed to avoid accidental exposure of sensitive data:

- `.env` is ignored by Git.
- Gemini API keys are loaded from local environment variables.
- Exported reports are privacy-masked.
- Runtime traces do not show raw job text, raw CV text, API keys, private tokens, or full private tool inputs.
- GitHub import uses public repository metadata only.
- Tests do not make real external Gemini calls.

This is especially important for a Concierge Agents submission because the user may paste personal career information.

### 4. Deployability And Reproducible Setup

The project includes:

- `requirements.txt`,
- `.env.example`,
- `Dockerfile`,
- Streamlit run instructions,
- local smoke-test scripts,
- pytest coverage for deterministic logic, tools, workflow, MCP, export, privacy, and GitHub parsing.

The project does not require a live public deployment for judging. If a live demo is not used, the public GitHub repository and setup instructions allow judges to run it locally.

### 5. AI-Assisted Vibe Coding

The project was built through iterative AI-assisted development. The demo video explains how the workflow evolved from a deterministic career report into a traceable agent system with Gemini structured extraction, MCP-first tool routing, safe fallbacks, and clearer judge-facing UI.

## Evaluation Rubric Fit

For the pitch category, DevPath Agent focuses on a clear individual user problem: junior developers need practical, evidence-based career guidance before applying to jobs. The value is not only a score, but a complete preparation workflow that helps the user decide what to highlight, what to improve, and how to prepare for interviews.

For the implementation category, the project emphasizes traceable architecture and meaningful tool use. The agent workflow is visible in the UI, MCP-aware tool calls are displayed in the Runtime tab and documentation explains how to run and verify the system locally.

## Deterministic Scoring

The score is not generated by an LLM. It uses a weighted scoring matrix:

- required technical skills: 35%,
- portfolio evidence: 25%,
- nice-to-have skills: 15%,
- experience and seniority fit: 10%,
- language and location fit: 10%,
- education or domain relevance: 5%.

The scorer normalizes skill aliases, maps portfolio evidence to requirements, classifies strong and partial matches, and creates prioritized gaps. Gemini can enrich the explanation, but deterministic scoring remains the source of truth.

This design makes the output more trustworthy. A candidate can see not only "82/100," but also which projects support React, TypeScript, Git, REST API, English, or missing nice-to-have skills such as Docker and unit testing.

## Gemini Usage

Gemini is used in a bounded way:

- structured job extraction,
- structured candidate/CV extraction,
- narrative gap explanation,
- detailed preparation plans,
- application drafts,
- interview preparation.

Gemini output is validated before being used as context. If the API key is missing or Gemini returns invalid output, the app falls back to deterministic extraction and report generation. The demo remains usable without an API key.

## Demo Flow

The demo starts with the built-in React frontend sample scenario. The user clicks the sample-load button, keeps the default AI Agent Demo Settings, and generates a career strategy.

The video shows:

1. input workspace with job posting, candidate profile, portfolio projects, and CV context;
2. AI Agent Demo Settings with Gemini/ADK tool-calling and deterministic scoring;
3. Results Overview with match score and Gemini-assisted career summary;
4. Profile Match with deterministic category score breakdown;
5. Gaps and Action Plan with Gemini-enhanced narrative;
6. Runtime tab with Agent Workflow Trace and AI Tool-Calling Trace;
7. Workflow Runtime metadata showing MCP-first routing and safe fallback behavior;
8. Markdown export.

## What Is Implemented

Implemented features include:

- Streamlit app,
- editable inputs and local sample scenario,
- manual portfolio JSON input,
- optional public GitHub repository import,
- deterministic scoring and evidence mapping,
- privacy masking utilities,
- Markdown export,
- Gemini structured extraction and narrative writers,
- ADK-compatible root agent and sub-agent skeletons,
- ADK-style deterministic workflow,
- MCP server skeleton and MCP-style tools,
- MCP runtime adapter and safe fallback route,
- Runtime trace for judges,
- tests and documentation.

## Closing

DevPath Agent demonstrates a practical concierge agent: it helps a junior developer make sense of a real job posting and turn scattered career evidence into an action plan. The project applies agent-style orchestration, MCP tools, privacy-aware design, optional Gemini assistance, and deterministic scoring in a way that is visible, testable, and useful.
