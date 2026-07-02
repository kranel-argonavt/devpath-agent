# Security

DevPath Agent is designed around cautious handling of candidate data. The current MVP runs locally by default. Gemini calls only happen when the user explicitly selects Gemini-assisted summary mode and configures an API key.

## Current Safeguards

- `.env` is ignored by Git.
- `.env.example` is committed with empty placeholder values only.
- Gemini API keys must stay in local `.env` files or environment variables, never in Git.
- Gemini API keys must never be pasted into prompts, commits, README files, screenshots, or exported reports.
- Generated Markdown reports in `outputs/*.md` are ignored by Git.
- Exported Markdown reports are passed through deterministic privacy masking before they are written.
- The Streamlit app warns users not to paste secrets or sensitive personal data.
- `devpath/core/privacy.py` provides deterministic masking utilities for emails, phone-like strings, and API-key-like values.
- Gemini-assisted summaries must not overwrite deterministic scores, missing skills, or evidence mappings.

## Privacy Module Roles

- `devpath/core/privacy.py` contains deterministic masking utilities used by local helpers such as Markdown export.
- `devpath/sub_agents/privacy_guard.py` is a future placeholder for agent-level privacy review and safer export decisions.

## Current Non-Goals

- No secret storage beyond local `.env` conventions.
- No LinkedIn scraping.
- No private repository access.
- No real GitHub API calls.
- No automatic Gemini or other LLM calls.

## Future Integration Rules

Future GitHub import should use public repositories only unless the project explicitly adds a secure permission model. Any LLM integration should avoid sending secrets, private tokens, or unnecessary personal data.
