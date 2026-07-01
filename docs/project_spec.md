# Project Specification

DevPath Agent is a Kaggle capstone project for junior software developers who want a clearer path from job posting to preparation plan. The app compares a target role with a candidate profile and portfolio evidence, then creates a structured career strategy report.

## Current Mock MVP

The current Step 1D MVP is a polished Streamlit workflow using deterministic local logic only. It can load sample data, let the user edit profile fields, display project evidence, generate a mock match report, and export Markdown.

## Planned Final System

The final system is planned as an agent-assisted career copilot with a Google ADK root agent, specialized sub-agents, MCP tools, Gemini-based reasoning, and optional public GitHub repository import.

## Inputs

- Job posting text
- Optional job source URL
- Candidate profile fields
- Portfolio projects
- Optional CV context
- Analysis settings

## Outputs

- Job analysis summary
- Profile match score
- Category scores
- Strong matches and partial matches
- Missing skills
- Preparation plan
- Application draft text
- Interview prep questions
- Markdown export

## Non-Goals For Current MVP

- No real LLM calls
- No Gemini API integration
- No Google ADK runtime logic
- No real MCP server behavior
- No GitHub API calls
- No LinkedIn scraping
