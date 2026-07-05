# Final Demo Notes

## Default Demo Mode

Use this path for the main recording because it works offline and does not require secrets:

- Analysis workflow: Gemini/ADK tool-calling agent
- Analysis mode: Gemini-assisted summary
- Tool route: MCP runtime first, local MCP-style registry fallback, direct deterministic fallback
- Portfolio source: Local sample projects

Start by clicking `Load sample React frontend scenario`, then generate the report.

## Backup Offline Path

If GitHub, Gemini, or MCP runtime checks are unavailable, use the default local sample path only:

1. Load sample scenario.
2. Generate career strategy.
3. Show Match Score, Evidence, Gaps, Agent Workflow Trace, AI Tool-Calling Trace, Workflow Runtime, and Markdown export.

This is the safest recording path.

## Optional GitHub Path

Use only if internet access is available:

1. Select `GitHub public repositories`.
2. Enter a public username, such as `octocat`.
3. Fetch public repositories.
4. Generate the report.
5. Show GitHub Repository Evidence.

Do not claim source-code analysis. Step 7B uses public metadata only.

## Optional Gemini Path

Use only if a local `.env` API key is configured and hidden:

1. Select `Gemini-assisted summary`.
2. Generate the report.
3. Show structured Gemini sections.
4. Explain that Gemini improves narrative only and does not modify deterministic scores.

## What To Show

- Problem: junior developers struggle to translate job postings into action.
- One-click demo scenario.
- Gemini/ADK tool-calling agent mode.
- Match score and category breakdown.
- Evidence by skill and portfolio evidence.
- Prioritized gaps and next action.
- Agent Workflow Trace.
- AI Tool-Calling Trace.
- Workflow Runtime.
- Markdown export.
- Optional GitHub public metadata import.
- AI-assisted vibe coding as part of the build story.

## What Not To Show

- `.env` files.
- API keys or tokens.
- Private repository data.
- Private personal data.
- Raw pasted CV text containing sensitive information.
- Generated reports that contain real personal data.

## Closing Message

DevPath Agent demonstrates a concierge-style AI agent workflow: specialized agent stages orchestrate deterministic tools, MCP tools participate through a visible MCP-first tool-calling route with safe fallback, optional Gemini improves the narrative, and deterministic scoring remains auditable and safe.
