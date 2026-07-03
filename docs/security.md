# Security

DevPath Agent is designed around cautious handling of candidate data. The current MVP runs locally by default and avoids external calls unless the user explicitly enables optional Gemini-assisted mode with a local API key.

## Secrets

- Do not commit real API keys.
- `.env` is ignored by Git.
- `.env.example` is committed with empty placeholder values only.
- Gemini API keys must stay in local `.env` files or environment variables.
- Never paste API keys into prompts, commits, README files, screenshots, exported reports, or demo videos.

## User Data

- Do not paste secrets, passwords, private tokens, or sensitive personal data into the app.
- Do not pass secrets into MCP-style tool inputs.
- Avoid showing private data during demos or screenshots.
- Future GitHub import should use public repositories only unless a secure permission model is added.

## Export Safety

- Generated Markdown reports in `outputs/*.md` are ignored by Git.
- Exported Markdown reports are passed through deterministic privacy masking.
- MCP export tools use the same privacy-masked Markdown export path.
- `devpath/core/privacy.py` masks emails, phone-like strings, and API-key-like values.

## Gemini Safety

- Gemini is optional.
- Gemini calls only happen when explicitly selected.
- Missing API keys fall back to deterministic mode.
- Gemini failures fall back to deterministic mode.
- Gemini-assisted output must not overwrite deterministic scores, missing skills, prioritized gaps, or evidence mappings.

## Runtime Boundaries

- Tests do not make real Gemini calls.
- Tests do not start ADK runtime.
- Tests do not start MCP runtime transports.
- Tests do not call GitHub or other external APIs.
- MCP-style tools do not call external APIs in the current implementation.

## Current Non-Goals

- No LinkedIn scraping.
- No private repository access.
- No production secret storage.
- No automatic LLM calls.
- No MCP runtime transport execution.
