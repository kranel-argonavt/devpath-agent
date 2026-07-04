# Demo Checklist

## Before Recording

- [ ] `.env` exists locally only if Gemini demo is needed.
- [ ] `.env` is not visible in Git changes.
- [ ] Tests pass.
- [ ] Streamlit starts.
- [ ] Sample flow works.
- [ ] Export works.
- [ ] Generated reports do not appear in Git changes.

## Commands

```powershell
python -m pytest --basetemp .pytest_tmp_demo
streamlit run app.py
python scripts/check_gemini_connection.py
python scripts/check_adk_agent.py
python scripts/check_mcp_tools.py
python scripts/check_mcp_runtime.py
python scripts/check_adk_mcp_tools.py
```

## UI Points To Show

- [ ] Job posting input.
- [ ] Candidate profile.
- [ ] Portfolio source.
- [ ] Analysis mode selector.
- [ ] Tool backend selector.
- [ ] Workflow Runtime section.
- [ ] Selected backend.
- [ ] MCP runtime used status.
- [ ] Fallback status.
- [ ] Profile Match tab.
- [ ] Evidence by Skill.
- [ ] Skill Gaps tab.
- [ ] Gemini-assisted Career Strategy if API key is configured.
- [ ] Markdown export.
- [ ] Export Markdown and verify Workflow Runtime section.

## Safety Checks

- [ ] Do not show `.env`.
- [ ] Do not show API keys.
- [ ] Do not show private personal data.
- [ ] Confirm exported reports are ignored by Git.
