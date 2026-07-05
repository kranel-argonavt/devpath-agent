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
Deterministic scoring · GitHub evidence · ADK-style agent workflow · MCP tools · Gemini-assisted insights · Markdown export
```

## 3. Load Demo Scenario

Click:

```text
Load sample React frontend scenario
```

Explain that the core demo works offline and without API keys.

Default settings:

- Demo workflow: Capstone agent mode: Gemini/ADK tool-calling + MCP trace
- Gemini behavior: Structured extraction + narrative writers
- Tool route: MCP runtime first -> local MCP registry -> direct deterministic fallback
- Portfolio source: Local sample projects

## 4. Show Inputs

Briefly show:

- Job Posting
- Candidate Profile
- Portfolio
- AI Agent Demo Settings

Open `Runtime details for judges` briefly to show that the capstone mode locks the MCP-first tool route and keeps deterministic scoring as the source of truth.

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
- Gaps: Gemini-enhanced gap narrative plus deterministic gap details
- Action Plan: Gemini-enhanced 7-day, 14-day, 30-day plan, portfolio tasks, study tasks, interview drills, and done criteria
- Application: tailored drafts, CV bullets, project positioning, application checklist
- Interview: technical questions with answer focus, behavioral questions, project story prompts, weak-area drills

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

1. Use the default capstone workflow with `Gemini behavior: Structured extraction + narrative writers`.
2. Generate the report with local `GOOGLE_API_KEY`.
3. Show structured Gemini sections in Gaps, Action Plan, Application, and Interview.

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

## Screenshot Checklist

Capture these after the final smoke test and save them under `assets/screenshots/`:

1. `01a-input-job-posting.png` - sample React job posting.
2. `01b-input-candidate-profile.png` - candidate profile and optional CV context.
3. `01c-input-portfolio.png` - local sample portfolio projects.
4. `01d-input-agent-settings.png` - AI Agent Demo Settings with Runtime details open.
5. `02a-results-overview-AI-Summary.png` - Results Dashboard and Gemini-assisted summary.
6. `02b-results-overview-ProfileMatch.png` - deterministic match score and category breakdown.
7. `03-gemini-action-plan.png` - Gemini-enhanced Action Plan.
8. `03-gemini-action-SkillGaps.png` - Gemini-enhanced gap narrative.
9. `04a-runtime-tool-AgentWorkflowTrace.png` - Agent Workflow Trace.
10. `04b-runtime-tool-AI-Tool-Calling-Trace.png` - AI Tool-Calling Trace.
11. `04c-runtime-tool-Workflow-Runtime.png` - Workflow Runtime metadata.

Optional:

- `05-export-preview.png` - Export tab with Markdown preview, if there is time to capture it after the main capstone evidence screenshots.
