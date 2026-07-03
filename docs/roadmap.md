# Roadmap

- [x] Step 1A - Project skeleton
- [x] Step 1B - Core helper functions and tests
- [x] Step 1C - Streamlit mock workflow
- [x] Step 1D - UI polish and README update
- [x] Step 2A - Evidence-based deterministic scoring
- [x] Step 2B - Richer scoring displayed in Streamlit
- [x] Step 2C - Rich Markdown export
- [x] Step 3A - Gemini integration foundation
- [x] Step 3B - Local Gemini smoke test
- [x] Step 3C - Structured Gemini-assisted output
- [x] Step 4A - ADK root agent skeleton and deterministic tools
- [x] Step 4B - Local ADK smoke test and agent validation workflow
- [x] Step 4C - Agent workflow facade for Streamlit integration
- [x] Step 5A - MCP server skeleton and deterministic tool contracts
- [x] Step 5B - Local MCP smoke test
- [x] Step 5C - Connect MCP-style tools to workflow/tool layer
- [ ] Step 5D - Route selected ADK tools through MCP runtime
- [ ] Step 6 - GitHub public repo import
- [ ] Step 7 - Demo video and Kaggle writeup

## Current Focus

The project is still deterministic-first. The current focus is the local tool backend selector: direct Python services by default, with optional in-process MCP-style tools for future runtime integration.

## Later Quality Improvements

- Improve requirement extraction from job postings.
- Add richer portfolio evidence mapping.
- Expand report exports and demo assets.
- Route selected Streamlit actions through the ADK root agent when the workflow facade is stable.
- Add MCP runtime routing and GitHub integrations only after deterministic tools remain reliable.
