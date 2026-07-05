# Security

DevPath Agent is designed around cautious handling of candidate data. The current MVP runs locally by default and avoids external calls unless Gemini-assisted narrative mode is selected and a local API key is configured.

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
- The main capstone demo should use local sample data and avoid private personal details.
- GitHub import uses public repositories only unless a secure permission model is added later.
- GitHub usernames are not secrets, but avoid showing private personal context in screenshots.

## GitHub Safety

- No GitHub token is required for Step 7A.
- Only public repository metadata is imported.
- GitHub evidence mapping uses metadata only: language, topics, description, URL, and public repository signals.
- Public README text may be fetched only through the explicit GitHub README helper.
- Private repositories are not accessed.
- GitHub HTML pages are not scraped.
- Repositories are not cloned.
- Source code is not downloaded.
- Stars and forks are public metadata signals, not private data or direct skill proof.
- Automated tests mock GitHub responses and do not call the real GitHub API.

## Export Safety

- Generated Markdown reports in `outputs/*.md` are ignored by Git.
- Exported Markdown reports are passed through deterministic privacy masking.
- MCP export tools use the same privacy-masked Markdown export path.
- `devpath/core/privacy.py` detects and masks emails, phone-like strings, and API-key-like values without returning raw sensitive matches.

## Gemini Safety

- Gemini is optional.
- Gemini-assisted mode is selected by default for the capstone demo, but calls only succeed when a local API key is configured.
- Missing API keys fall back to deterministic mode.
- Gemini failures fall back to deterministic mode.
- Gemini-assisted output must not overwrite deterministic scores, missing skills, prioritized gaps, or evidence mappings.
- Gemini structured extraction must be validated before it is used as context.
- Gemini narrative writers may update narrative-only fields for Gaps, Action Plan, Application, and Interview.

## AI Tool-Calling Trace Safety

- The default tool-calling workflow records safe metadata only.
- Trace entries may include tool name, agent name, backend used, status, input summary, output summary, fallback status, and warnings.
- Trace entries must not include raw job posting text, full CV text, API keys, private tokens, passwords, or full secret-bearing inputs.
- `mask_personal_data` runs before analysis/report tool calls in the tool-calling workflow.
- Gemini extraction receives masked job/CV context only.
- Gemini writer steps receive the deterministic report only after deterministic score fields are created.
- Deterministic score fields are restored after Gemini generation to prevent LLM score mutation.

## Full Agent Workflow Safety

- The full ADK-style workflow does not require API keys.
- The full workflow is deterministic orchestration around local tools and services.
- Agents record trace metadata but must not expose raw secrets or private tokens.
- Agent trace is safe metadata: stage names, summaries, selected tool names, status, and warnings.
- Agent trace must not include raw job text, full CV text, API keys, private tokens, or other secret-bearing inputs.
- `profile_matcher` uses deterministic scoring and must not invent or modify numeric scores.
- Agents do not modify numeric scores; scoring remains deterministic and auditable.
- Automated tests for the full workflow do not call external APIs or live ADK runtime services.

## Runtime Boundaries

- Tests do not make real Gemini calls.
- Tests do not start ADK runtime.
- Tests do not require live MCP runtime transports.
- Tests do not call GitHub or other external APIs.
- MCP-style local tools do not call external APIs unless using explicit public GitHub helper functions.
- The MCP runtime smoke test is local stdio only and must be run explicitly.
- The ADK-MCP bridge uses local stdio runtime only for selected deterministic tools.
- The Gemini/ADK tool-calling workflow requests local MCP stdio first and falls back to the local MCP-style registry and direct deterministic services on failure.
- Automated tests use dependency injection for the ADK-MCP bridge and do not start runtime transports.
- Do not pass secrets into MCP runtime tool arguments.
- Runtime metadata is safe to display because it contains backend names, selected tool names, and status flags only.
- Exported runtime metadata must not include tool inputs, secrets, API keys, or pasted user content.

## Current Non-Goals

- No LinkedIn scraping.
- No private repository access.
- No production secret storage.
- No automatic LLM calls.
- No deployed ADK runtime dependency.
- No required MCP runtime transport for successful demo execution.
