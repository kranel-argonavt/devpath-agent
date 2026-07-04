# Project Specification

DevPath Agent is a Kaggle capstone project for junior software developers who want a clearer path from a job posting to a preparation strategy.

## Current MVP

The current MVP is a Streamlit app backed by deterministic local logic. It loads or accepts a job posting, candidate profile, portfolio projects, and optional CV context. It then generates a structured report with match scoring, evidence, gaps, recommendations, application drafts, interview prep, and Markdown export.

The app also includes optional Gemini-assisted structured insights, an ADK-compatible agent skeleton, a full ADK-style deterministic workflow facade exposed through Streamlit, MCP-style deterministic tool contracts, and smoke-test scripts for local validation.

GitHub public repositories can be imported as portfolio projects. Their public metadata is mapped into evidence through primary language, topics, description matches, URL, and repository signals.

## Target Users

- Junior software developers preparing for their first or next role.
- Candidates who need to connect portfolio projects to job requirements.
- Career changers who want a clear preparation plan before applying.
- Capstone reviewers evaluating explainable agent architecture.

## Inputs

- Job posting text
- Optional job source URL
- Candidate profile fields
- Portfolio project data from local samples or public GitHub repository metadata
- Optional CV context
- Target role
- Analysis mode
- Analysis workflow mode: standard workflow or full agent workflow
- Tool backend selection
- Optional full agent workflow execution in local smoke tests

## Outputs

- Job analysis summary
- Overall deterministic match score
- Category score breakdown
- Strong matches, partial matches, and missing skills
- Evidence by skill
- GitHub repository evidence when public repositories are imported
- Prioritized gaps and recommendations
- 7-day, 14-day, and 30-day preparation plan
- Cover letter and recruiter message drafts
- Interview questions and practice focus
- Optional Gemini-assisted narrative sections
- Full agent workflow metadata and serialized agent trace when the opt-in full workflow is used
- Agent Workflow Trace display in Streamlit and exported Markdown
- Privacy-masked Markdown report

## Current Non-Goals

- No live ADK runtime routing in the default Streamlit app.
- No MCP runtime transport.
- No private repository access.
- No GitHub source-code download or repository cloning.
- No GitHub token requirement.
- No LinkedIn scraping.
- No LLM-based score calculation.
- No automated tests that call real external APIs.

## Planned Final System

The planned final system will combine the Streamlit UI, Google ADK root agent, specialized sub-agents, MCP runtime tools, optional Gemini narrative assistance, and public GitHub repository evidence mapping. The current full agent workflow adds deterministic ADK-style orchestration through `privacy_guard`, `job_analyzer`, `portfolio_evidence`, `profile_matcher`, `gap_planner`, `application_writer`, and `interview_coach`, with trace visibility in Streamlit. Deterministic scoring should remain the transparent source of truth.
