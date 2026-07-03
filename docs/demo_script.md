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
- Tool backend: `Direct Python services`

Click `Generate Career Strategy`.

Show:

- `Profile Match` overall score and category breakdown
- `Evidence by Skill`
- `Skill Gaps` and prioritized recommendations
- `Preparation Plan`

Explain that scoring, gaps, and evidence are deterministic.

## 5. Show MCP-Style Backend

Switch `Tool backend` to `Local MCP-style tools` and generate again.

Explain:

- This path uses the local MCP-style registry in-process.
- No MCP transport is started.
- The deterministic score remains the source of truth.

## 6. Optional Gemini Demo

If a local API key is configured:

1. Select `Gemini-assisted summary`.
2. Generate the report.
3. Show `Gemini-assisted Career Strategy`.
4. Point out AI career summary, top actions, portfolio positioning, skill gap strategy, and interview focus areas.

If no key is configured, show the warning and explain that the app continues in deterministic mode.

## 7. Export Markdown

Open `Export`, click `Export Markdown Report`, and show the generated path. Mention that exported Markdown is privacy-masked and `outputs/*.md` is ignored by Git.

## 8. Mention Smoke Tests

Run or mention:

```powershell
python scripts/check_gemini_connection.py
python scripts/check_adk_agent.py
python scripts/check_mcp_tools.py
python scripts/check_mcp_runtime.py
```

Explain that these validate optional Gemini connectivity, ADK skeleton structure, MCP-style deterministic tools, and selected local MCP runtime calls without requiring production runtime integration.

## 9. Close With Architecture

Summarize:

- Streamlit calls a workflow facade.
- The workflow uses a tool router.
- The tool router can use direct Python services or local MCP-style tools.
- ADK and MCP runtime routing are planned next.
- Deterministic scoring remains the source of truth.

## Optional Step 6A Runtime Proof

Run:

```powershell
python scripts/check_mcp_runtime.py
```

Explain that selected tools are called through a local MCP stdio runtime while deterministic scoring remains the source of truth. If the local SDK/runtime is unavailable, show the clean diagnostic message and explain that the default Streamlit workflow is unaffected.
