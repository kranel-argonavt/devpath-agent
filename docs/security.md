# Security

DevPath Agent is designed around cautious handling of candidate data. The current MVP runs locally and does not make real external API calls.

## Current Safeguards

- `.env` is ignored by Git.
- `.env.example` is committed with empty placeholder values only.
- Generated Markdown reports in `outputs/*.md` are ignored by Git.
- Exported Markdown reports are passed through deterministic privacy masking before they are written.
- The Streamlit app warns users not to paste secrets or sensitive personal data.
- `devpath/core/privacy.py` provides deterministic masking utilities for emails, phone-like strings, and API-key-like values.

## Privacy Module Roles

- `devpath/core/privacy.py` contains deterministic masking utilities used by local helpers such as Markdown export.
- `devpath/sub_agents/privacy_guard.py` is a future placeholder for agent-level privacy review and safer export decisions.

## Current Non-Goals

- No secret storage beyond local `.env` conventions.
- No LinkedIn scraping.
- No private repository access.
- No real GitHub API calls.
- No Gemini or other LLM calls.

## Future Integration Rules

Future GitHub import should use public repositories only unless the project explicitly adds a secure permission model. Any future LLM integration should avoid sending secrets, private tokens, or unnecessary personal data.
