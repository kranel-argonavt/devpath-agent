# Demo Checklist

## Before Recording

- [ ] `.env` exists locally only if Gemini demo is needed.
- [ ] `.env` is not visible in Git changes.
- [ ] Tests pass.
- [ ] Gemini/ADK tool-calling workflow test passes.
- [ ] Full agent workflow smoke test passes.
- [ ] ADK-MCP bridge smoke test passes or is skipped as optional.
- [ ] GitHub import works or backup sample path is ready.
- [ ] Manual portfolio JSON input works for custom judge-style testing.
- [ ] Streamlit starts.
- [ ] Demo data loads.
- [ ] Export works.
- [ ] Generated reports do not appear in Git changes.
- [ ] Video plan fits under 5 minutes.
- [ ] Cover image is prepared.
- [ ] Public repo link is ready.

## Commands

```powershell
python -m pytest --basetemp .pytest_tmp_demo
python -m pytest tests/test_adk_tool_calling_workflow.py --basetemp .pytest_tmp_tool_calling_demo
python scripts/check_full_agent_workflow.py
python scripts/check_adk_mcp_tools.py
python scripts/check_github_public_import.py octocat
streamlit run app.py
```

## Main UI Points

- [ ] Click `Load sample React frontend scenario`.
- [ ] Confirm Gemini/ADK tool-calling agent is selected by default.
- [ ] Confirm `Runtime details for judges` shows structured Gemini behavior and MCP-first tool route.
- [ ] Confirm deterministic score source is visible.
- [ ] Confirm Local sample projects is selected by default.
- [ ] Generate Career Strategy.
- [ ] Show Results Dashboard.
- [ ] Show Match Score.
- [ ] Show Evidence tab.
- [ ] Show Gaps tab.
- [ ] Show Agent Workflow Trace section.
- [ ] Show AI Tool-Calling Trace section.
- [ ] Show Gemini extraction steps and deterministic validation steps.
- [ ] Show Gemini-enhanced Gaps, Action Plan, Application, and Interview if API key is configured.
- [ ] Show deterministic scoring source.
- [ ] Show LLM score modification disabled.
- [ ] Show Workflow Runtime section.
- [ ] Show MCP runtime preferred route and fallback status.
- [ ] Capture the recommended screenshots under `assets/screenshots/`.
- [ ] Export Markdown and verify Workflow Runtime section.
- [ ] Export Markdown and verify Agent Workflow Trace section.
- [ ] Export Markdown and verify AI Tool-Calling Trace section.

## Optional UI Points

- [ ] Test Manual JSON input with the built-in React frontend sample.
- [ ] Confirm manual projects appear as portfolio cards.
- [ ] Test GitHub public username import.
- [ ] Confirm no token is shown or required.
- [ ] Confirm imported repos appear as portfolio projects.
- [ ] Show GitHub repo language/topics.
- [ ] Show GitHub URL in evidence.
- [ ] Show GitHub Repository Evidence in exported Markdown.
- [ ] Show Gemini-assisted Career Strategy if API key is configured.
- [ ] Mention Antigravity / AI-assisted vibe coding in the build story.

## Safety Checks

- [ ] Do not show `.env`.
- [ ] Do not show API keys.
- [ ] Do not show private personal data.
- [ ] Do not rely on GitHub or Gemini for the core demo.
- [ ] Confirm exported reports are ignored by Git.
