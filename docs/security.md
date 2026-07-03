# Security

DevPath Agent is designed around cautious handling of candidate data. The current MVP runs locally by default. Gemini calls only happen when the user explicitly selects Gemini-assisted summary mode and configures an API key.

## Current Safeguards

- `.env` is ignored by Git.
- `.env.example` is committed with empty placeholder values only.
- Gemini API keys must stay in local `.env` files or environment variables, never in Git.
- Gemini API keys must never be pasted into prompts, commits, README files, screenshots, or exported reports.
- Generated Markdown reports in `outputs/*.md` are ignored by Git.
- Exported Markdown reports, including Gemini-assisted sections, are passed through deterministic privacy masking before they are written.
- MCP export tools use the same privacy-masked Markdown export path.
- MCP-style tools do not call external APIs in Step 5A.
- MCP runtime transports are not started in automated tests.
- The Streamlit app warns users not to paste secrets or sensitive personal data.
- Do not paste secrets into job posting, CV, profile, or project fields.
- Do not pass secrets into MCP tool inputs.
- `devpath/core/privacy.py` provides deterministic masking utilities for emails, phone-like strings, and API-key-like values.
- Gemini-assisted output must not overwrite deterministic scores, missing skills, prioritized gaps, or evidence mappings.

## Privacy Module Roles

- `devpath/core/privacy.py` contains deterministic masking utilities used by local helpers such as Markdown export.
- `devpath/sub_agents/privacy_guard.py` is a future placeholder for agent-level privacy review and safer export decisions.

## Current Non-Goals

- No secret storage beyond local `.env` conventions.
- No LinkedIn scraping.
- No private repository access.
- No real GitHub API calls.
- No automatic Gemini or other LLM calls.
- No MCP runtime transport execution.

## Future Integration Rules

Future GitHub import should use public repositories only unless the project explicitly adds a secure permission model. Any LLM integration should avoid sending secrets, private tokens, or unnecessary personal data.
