# Capstone Submission Checklist

## Track

Recommended track: Concierge Agents

DevPath Agent acts as a personal career copilot for junior developers. It helps one user understand job fit, portfolio evidence, skill gaps, application positioning, and interview preparation.

## Required Submission Assets

- [ ] Kaggle writeup
- [ ] Media Gallery cover image
- [ ] YouTube video under 5 minutes
- [ ] Public project link or public GitHub repository
- [ ] Setup instructions
- [ ] Clear demo path that works without API keys

## Course Concepts Demonstrated

- [x] Agent / multi-agent system using ADK-style architecture and visible tool-calling workflow
- [x] MCP server and MCP tool layer with MCP-first runtime route and safe fallback
- [x] Security features
- [x] Agent tools / skills
- [x] Deployability / reproducible setup
- [x] Optional Gemini-assisted narrative insights


## Evaluation Alignment

### Pitch

- [ ] Problem statement: junior developers struggle to understand job fit and prepare efficiently.
- [ ] Solution value: deterministic match score, evidence, gaps, plan, drafts, interview prep.
- [ ] Why agents: staged career workflow with specialized responsibilities.
- [ ] Demo clarity: one-click sample scenario and offline default path.

### Implementation

- [ ] Streamlit app starts locally.
- [ ] Gemini/ADK tool-calling agent mode is visible.
- [ ] Agent Workflow Trace is visible.
- [ ] AI Tool-Calling Trace is visible.
- [ ] Workflow Runtime metadata is visible.
- [ ] Markdown export works.
- [ ] Tests pass.
- [ ] Smoke scripts pass or have clear optional-network notes.

### Documentation

- [ ] README explains setup and capstone fit.
- [ ] Architecture docs explain ADK-style workflow and MCP layers.
- [ ] Security docs explain secrets, privacy masking, and test boundaries.
- [ ] Demo script and checklist are up to date.

### Security

- [ ] `.env` is not committed.
- [ ] No API keys are shown in screenshots or video.
- [ ] Exported reports are ignored by Git.
- [ ] GitHub import uses public metadata only.
- [ ] Automated tests do not call external APIs.
