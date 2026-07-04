# Demo Script

This script is designed for a 2-4 minute capstone video.

## 1. Introduce The Problem

Junior developers often see job postings with many requirements and do not know what they match, what they lack, or what to prepare first. DevPath Agent turns a job posting, profile, and portfolio into a focused career preparation plan.

## 2. Open The App

Run:

```powershell
streamlit run app.py
```

Show the header and explain that the default mode is deterministic and local.

## 3. Load Sample Inputs

1. In `1. Job Posting`, select `Load sample job posting`.
2. In `2. Candidate Profile`, select `Load sample profile`.
3. In `3. Portfolio Source`, keep `Local sample projects`.
4. Briefly expand one project card.
5. Keep a junior target role.
6. Leave CV context empty or use short non-sensitive sample text.

## 4. Generate Deterministic Report

Keep:

- Analysis mode: `Mock deterministic mode`
- Analysis workflow: `Standard workflow`
- Tool backend: `Direct Python services`

Click `Generate Career Strategy`.

Show:

- `Workflow Runtime` section with backend used and fallback status
- `Profile Match` overall score and category breakdown
- `Evidence by Skill`
- `Skill Gaps` and prioritized recommendations
- `Preparation Plan`

Explain that scoring, gaps, and evidence are deterministic.

## 5. Show Full Agent Workflow Mode

Switch:

```text
Analysis workflow -> Full agent workflow
```

Click `Generate Career Strategy`.

Show:

- `Agent Workflow Trace`
- `privacy_guard`
- `job_analyzer`
- `portfolio_evidence`
- `profile_matcher`
- `gap_planner`
- `application_writer`
- `interview_coach`
- Scoring source: deterministic
- LLM score modification: disabled

Explain that agents orchestrate the workflow and produce trace metadata, but deterministic scoring remains the source of truth.

## 6. Show MCP-Style Backend

Switch `Tool backend` to `Local MCP-style tools` and generate again.

Explain:

- This path uses the local MCP-style registry in-process.
- No MCP transport is started.
- The `Workflow Runtime` section shows backend metadata.
- The deterministic score remains the source of truth.

Optionally switch `Tool backend` to `Experimental ADK-MCP runtime tools` and generate again.

Explain:

- This path routes selected job-analysis and match-score calls through ADK-style wrappers and local MCP stdio runtime.
- Direct Python services remain the default.
- If the runtime path fails, the workflow falls back to direct deterministic services with a warning.
- The `Workflow Runtime` section shows whether MCP runtime was used, which tools were selected, and whether fallback happened.
- The deterministic score remains the source of truth.

## 7. Optional Full Agent Workflow Smoke Test

Run:

```powershell
python scripts/check_full_agent_workflow.py
```

Show that the full ADK-style workflow executes each named stage:

- `privacy_guard`
- `job_analyzer`
- `portfolio_evidence`
- `profile_matcher`
- `gap_planner`
- `application_writer`
- `interview_coach`

Explain that this is deterministic orchestration and trace generation. It does not require a live ADK runtime, and `profile_matcher` still uses deterministic scoring as the source of truth.

## 8. Optional GitHub Public Repository Import

In `3. Portfolio Source`, select `GitHub public repositories`.

Demo steps:

1. Enter a public GitHub username such as `octocat`.
2. Click `Fetch public repositories`.
3. Show the imported public repo metadata table.
4. Show how imported GitHub repositories become portfolio evidence through language, topics, description, URL, and repository signals.
5. Explain that no token is required, private repos are not accessed, repos are not cloned, and source code is not downloaded.
6. Generate a career strategy using the imported repositories as portfolio projects.
7. Open `Portfolio Evidence` and show `GitHub Repository Evidence`.

## 9. Optional Gemini Demo

If a local API key is configured:

1. Select `Gemini-assisted summary`.
2. Generate the report.
3. Show `Gemini-assisted Career Strategy`.
4. Point out AI career summary, top actions, portfolio positioning, skill gap strategy, and interview focus areas.

If no key is configured, show the warning and explain that the app continues in deterministic mode.

## 10. Export Markdown

Open `Export`, click `Export Markdown Report`, and show the generated path. Mention that exported Markdown is privacy-masked, includes the `Workflow Runtime` section, includes `Agent Workflow Trace` when full agent mode was used, and `outputs/*.md` is ignored by Git.

## 11. Mention Smoke Tests

Run or mention:

```powershell
python scripts/check_gemini_connection.py
python scripts/check_adk_agent.py
python scripts/check_mcp_tools.py
python scripts/check_mcp_runtime.py
python scripts/check_adk_mcp_tools.py
python scripts/check_full_agent_workflow.py
```

Explain that these validate optional Gemini connectivity, ADK skeleton structure, MCP-style deterministic tools, selected local MCP runtime calls, the selected ADK-MCP bridge, and the full ADK-style deterministic workflow without requiring production runtime integration.

## 12. Close With Architecture

Summarize:

- Streamlit calls a workflow facade.
- The workflow uses a tool router.
- The tool router can use direct Python services or local MCP-style tools.
- Full ADK-style deterministic orchestration now exists with trace metadata.
- Streamlit can show standard workflow or full agent workflow mode.
- Deterministic scoring remains the source of truth.

## Optional Step 6A.1 Runtime Proof

Run:

```powershell
python scripts/check_mcp_runtime.py
```

Explain that selected tools are called through a local MCP stdio runtime using the installed MCP SDK while deterministic scoring remains the source of truth. If the local SDK/runtime is unavailable, show the clean diagnostic message and explain that the default Streamlit workflow is unaffected.

## Optional Step 6B ADK-MCP Bridge Proof

Run:

```powershell
python scripts/check_adk_mcp_tools.py
```

Explain that selected ADK-style tool wrappers now call local MCP runtime tools. This proves the bridge path without routing the full Streamlit workflow through ADK or MCP runtime yet.

## Optional Step 6C Workflow Backend Demo

In the app, select:

```text
Tool backend -> Experimental ADK-MCP runtime tools
```

Generate the report and explain that the workflow can now use the selected ADK-MCP runtime route while still preserving deterministic scoring and safe fallback behavior.

## Optional Step 6D Runtime Metadata Demo

Show:

- Tool backend selector.
- A generated report with `Direct Python services`.
- The `Workflow Runtime` section.
- A generated report with `Experimental ADK-MCP runtime tools`.
- Whether MCP runtime was used or fallback happened.
- Exported Markdown with the `Workflow Runtime` section.
