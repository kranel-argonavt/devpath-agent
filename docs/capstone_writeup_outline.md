# Capstone Writeup Outline

## Project Title

DevPath Agent - AI Career Copilot for Junior Software Developers

## Problem

Describe why junior developers struggle to compare job postings with their skills and portfolio evidence.

## Target Users

Junior developers, career changers, and portfolio-driven candidates applying for software roles.

## Solution Overview

Explain the Streamlit workflow, deterministic score, gap analysis, preparation plan, application drafts, interview prep, optional Gemini insights, ADK skeleton, and MCP-style tool layer.

## Agent Architecture

Describe the workflow facade, tool router, ADK root agent skeleton, sub-agent responsibilities, and future runtime path.

## Gemini Usage

Explain optional structured narrative insights and the rule that Gemini does not calculate or modify scores.

## ADK Usage

Explain `root_agent`, sub-agent modules, deterministic agent tools, and local ADK smoke testing.

## MCP/Tool Usage

Explain MCP server skeleton, MCP-style deterministic tools, `MCP_TOOL_REGISTRY`, local MCP smoke testing, and future runtime transport plans.

## Deterministic Scoring

Describe skill normalization, evidence by skill, weighted categories, partial matches, missing skills, and prioritized gaps.

## Privacy And Safety

Describe `.env`, ignored generated reports, privacy masking, no external calls in tests, and careful handling of secrets.

## Demo Flow

Outline the Streamlit demo from sample job posting to Markdown export.

## What Is Implemented

List the current MVP features and smoke tests.

## What Is Planned Next

List MCP runtime adapter, ADK+MCP workflow route, GitHub public repository import, and final Kaggle demo polish.

## Links

Add Kaggle notebook, repository, demo video, and exported sample report links when available.
