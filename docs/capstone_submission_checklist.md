# Capstone Submission Checklist

## Track

Recommended track: Concierge Agents

DevPath Agent acts as a personal career copilot for junior developers. It helps one user understand job fit, portfolio evidence, skill gaps, application positioning, and interview preparation.

## Required Submission Assets

- [x] Kaggle writeup draft
- [ ] Media Gallery cover image
- [x] Architecture diagram image or Mermaid diagram
- [x] App screenshots
- [x] YouTube video under 5 minutes
- [x] Public project link or public GitHub repository
- [x] Setup instructions
- [x] Clear demo path that works without API keys

## Course Concepts Demonstrated

- [x] Agent / multi-agent system using ADK-style architecture and visible tool-calling workflow
- [x] MCP server and MCP tool layer with MCP-first runtime route and safe fallback
- [x] Security features
- [x] Agent tools / skills
- [x] Deployability / reproducible setup
- [x] Optional Gemini-assisted narrative insights

## Manual Kaggle Actions

- [ ] Create or update Kaggle Writeup from `docs/kaggle_writeup.md`.
- [ ] Attach Media Gallery cover image.
- [ ] Attach YouTube demo video.
- [ ] Add public project link: `https://github.com/kranel-argonavt/devpath-agent`.
- [ ] Select `Concierge Agents` track.
- [ ] Submit the Writeup before the deadline.

## Evaluation Alignment

### Pitch

- [x] Problem statement: junior developers struggle to understand job fit and prepare efficiently.
- [x] Solution value: deterministic match score, evidence, gaps, plan, drafts, interview prep.
- [x] Why agents: staged career workflow with specialized responsibilities.
- [x] Demo clarity: one-click sample scenario and offline default path.
- [x] Visual evidence: screenshots or diagram show UI, runtime trace, and architecture.

### Implementation

- [x] Streamlit app starts locally.
- [x] Gemini/ADK tool-calling agent mode is visible.
- [x] `Runtime details for judges` shows the locked MCP-first tool route in capstone mode.
- [x] Agent Workflow Trace is visible.
- [x] AI Tool-Calling Trace is visible.
- [x] Workflow Runtime metadata is visible.
- [x] Gemini-enhanced Action Plan, Application, and Interview sections are visible when API key is configured.
- [x] Markdown export works.
- [x] Tests pass.
- [x] Smoke scripts pass or have clear optional-network notes.

### Documentation

- [x] README explains setup and capstone fit.
- [x] Architecture docs explain ADK-style workflow and MCP layers.
- [x] Security docs explain secrets, privacy masking, and test boundaries.
- [x] Demo script and checklist are up to date.

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

- [x] `.env` is not committed.
- [x] No API keys are shown in screenshots or video.
- [x] Exported reports are ignored by Git.
- [x] GitHub import uses public metadata only.
- [x] Automated tests do not call external APIs.
