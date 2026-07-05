# Demo Script

This script is designed for a 2-4 minute capstone video.

## 1. Problem

Junior developers often struggle to understand whether a job posting is realistic for them, which portfolio evidence to highlight, and what to prepare before applying.

DevPath Agent turns a job posting, profile, and portfolio into an evidence-based career strategy.

## 2. Open DevPath Agent

Run:

```powershell
streamlit run app.py
```

Show the header and capability line:

```text
Deterministic scoring | GitHub evidence | ADK-style agent workflow | MCP tools | Optional Gemini insights | Markdown export
```

## 3. Load Demo Scenario

Click:

```text
Load sample React frontend scenario
```

Explain that the core demo works offline and without API keys.

Default settings:

- Analysis workflow: Gemini/ADK tool-calling agent
- Analysis mode: Gemini-assisted summary
- Tool route: MCP runtime first, local MCP-style registry fallback, direct deterministic fallback
- Portfolio source: Local sample projects

## 4. Show Inputs

Briefly show:

- Job Posting
- Candidate Profile
- Portfolio
- AI Agent Demo Settings

Keep Runtime details collapsed unless you want to point out the defaults.

## 5. Generate Career Strategy

Click:

```text
Generate Career Strategy
```

Show the Results Dashboard:

- Match Score
- Top Strengths
- Priority Gaps
- Evidence Items
- Recommended next action

Explain that the numeric score is deterministic and auditable.

## 6. Show Evidence And Gaps

Open:

- Overview: score breakdown and missing skills
- Evidence: portfolio evidence and evidence by skill
- Gaps: prioritized gaps and recommendations
- Action Plan: 7-day, 14-day, and 30-day plan

Explain that the app connects job requirements to candidate evidence instead of just generating generic advice.

## 7. Show Agent And Tool-Calling Trace

Open the Runtime tab and show:

- `Agent Workflow Trace`
- `AI Tool-Calling Trace`
- `Workflow Runtime`

Point out:

- Scoring source: deterministic
- LLM score modification: disabled
- Agents orchestrate the workflow, but do not invent numeric scores.
- Tool calls show backend used, status, fallback status, input summary, output summary, and warnings.

In `AI Tool-Calling Trace`, show the career workflow tools:

- `mask_personal_data`
- `extract_job_requirements_with_gemini`
- `validate_job_requirements`
- `analyze_job_posting`
- `build_portfolio_summary`
- `extract_candidate_context_with_gemini`
- `validate_candidate_context`
- `calculate_match_score`
- `build_career_report`
- `generate_gap_narrative`
- `generate_action_plan_narrative`
- `generate_application_drafts`
- `generate_interview_prep`
- `generate_gemini_career_insights`

Explain that MCP runtime is preferred. If unavailable, the trace clearly shows fallback to the local MCP-style registry or direct deterministic services.

## 8. Show Workflow Runtime

In the Runtime tab, show:

- Workflow backend
- MCP runtime status
- Fallback status
- Selected tools

Explain that Gemini extracts and explains in bounded JSON steps. Deterministic validators and scoring tools still own canonical score, evidence, and gaps. If no key is configured, Gemini steps are shown as skipped and the deterministic report still works.

## 9. Optional GitHub Evidence

For custom judge-style testing without network access:

1. Select `Manual JSON input`.
2. Paste a JSON array of projects or use the React frontend sample button.
3. Generate the report again.
4. Show that evidence is built from the pasted project technologies and summaries.

If internet access is available:

1. Select `GitHub public repositories`.
2. Enter a public username such as `octocat`.
3. Fetch public repositories.
4. Generate the report again.
5. Show GitHub Repository Evidence.

Explain that only public metadata is used: language, topics, description, URL, stars, forks, and timestamps. No token, private repo access, cloning, or source-code download is used.

## 10. Optional Gemini Narrative

If a local key is configured and hidden:

1. Ensure `Gemini-assisted summary` is selected.
2. Generate the report with local `GOOGLE_API_KEY`.
3. Show structured Gemini sections.

Explain that Gemini can enhance Gaps, Action Plan, Application, and Interview narrative. It does not calculate or modify the match score.

## 11. Export Markdown

Open Export, click:

```text
Export Markdown Report
```

Mention that exported Markdown is privacy-masked and includes:

- Workflow Runtime
- Agent Workflow Trace
- AI Tool-Calling Trace
- GitHub Repository Evidence when available

## 12. Close With Architecture

Summarize:

- Track fit: Concierge Agents
- ADK-style multi-agent workflow coordinates the career strategy stages.
- MCP tools are used through a visible MCP-first tool-calling route with safe fallback.
- Security features protect secrets and privacy.
- Optional Gemini provides structured extraction and narrative assistance.
- Deterministic scoring remains the source of truth.
- The project was built through AI-assisted vibe coding / Antigravity-style iteration for the capstone.
