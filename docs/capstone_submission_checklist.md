# Capstone Submission Checklist

## Track

Recommended track: Concierge Agents

DevPath Agent acts as a personal career copilot for junior developers. It helps one user understand job fit, portfolio evidence, skill gaps, application positioning, and interview preparation.

## Required Submission Assets

- [ ] Kaggle writeup
- [ ] Media Gallery cover image
- [ ] Architecture diagram image or Mermaid diagram
- [ ] App screenshots
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
- [ ] Visual evidence: screenshots or diagram show UI, runtime trace, and architecture.

### Implementation

- [ ] Streamlit app starts locally.
- [ ] Gemini/ADK tool-calling agent mode is visible.
- [ ] `Runtime details for judges` shows the locked MCP-first tool route in capstone mode.
- [ ] Agent Workflow Trace is visible.
- [ ] AI Tool-Calling Trace is visible.
- [ ] Workflow Runtime metadata is visible.
- [ ] Gemini-enhanced Action Plan, Application, and Interview sections are visible when API key is configured.
- [ ] Markdown export works.
- [ ] Tests pass.
- [ ] Smoke scripts pass or have clear optional-network notes.

### Documentation

- [ ] README explains setup and capstone fit.
- [ ] Architecture docs explain ADK-style workflow and MCP layers.
- [ ] Security docs explain secrets, privacy masking, and test boundaries.
- [ ] Demo script and checklist are up to date.

## Recommended Screenshots

Save these files under `assets/screenshots/`:

- [x] `01a-input-job-posting.png` - sample React job posting loaded.
- [x] `01b-input-candidate-profile.png` - candidate profile, skills, languages, summary, and optional CV context.
- [x] `01c-input-portfolio.png` - local sample portfolio projects.
- [x] `01d-input-agent-settings.png` - AI Agent Demo Settings with `Runtime details for judges` open.
- [x] `02a-results-overview-AI-Summary.png` - Results Dashboard and Gemini-assisted career summary.
- [x] `02b-results-overview-ProfileMatch.png` - deterministic match score and category breakdown.
- [x] `03-gemini-action-plan.png` - Gemini-enhanced Action Plan or Interview Prep with detailed recommendations.
- [x] `03-gemini-action-SkillGaps.png` - Gemini-enhanced gap narrative and deterministic gap details.
- [x] `04a-runtime-tool-AgentWorkflowTrace.png` - Runtime tab Agent Workflow Trace.
- [x] `04b-runtime-tool-AI-Tool-Calling-Trace.png` - Runtime tab AI Tool-Calling Trace.
- [x] `04c-runtime-tool-Workflow-Runtime.png` - Runtime tab Workflow Runtime.

Optional architecture asset:

- [x] Render `assets/architecture/devpath-agent-architecture.mmd` to `assets/architecture/devpath-agent-architecture.png` for the Kaggle Media Gallery or writeup.

### Security

- [ ] `.env` is not committed.
- [ ] No API keys are shown in screenshots or video.
- [ ] Exported reports are ignored by Git.
- [ ] GitHub import uses public metadata only.
- [ ] Automated tests do not call external APIs.
