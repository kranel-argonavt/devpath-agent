# Demo Script

This is the current mock MVP demo script. It is not the final Kaggle video script yet.

1. Open the project and run `streamlit run app.py`.
2. Point out the mock mode notice: deterministic local logic only, with external API calls disabled.
3. In `1. Job Posting`, select `Load sample job posting`.
4. In `2. Candidate Profile`, select `Load sample profile` and briefly show the editable fields.
5. In `3. Portfolio Source`, show the local sample projects and expand one project card.
6. Optionally open the GitHub source option and explain that it is placeholder-only for now.
7. In `4. Target Role`, keep or choose the target junior developer role.
8. Leave CV context empty or paste short non-sensitive sample text.
9. Review the analysis settings and click `Generate Career Strategy`.
10. Show that mock deterministic mode is the default.
11. Optionally run `python scripts/check_gemini_connection.py` to show the local Gemini smoke-test workflow.
12. If no key is configured, show the clear no-key message and explain that mock deterministic mode still works.
13. Optionally switch to `Gemini-assisted summary` in Streamlit and show the warning if no API key is configured.
14. Later, when an API key is configured locally, select `Gemini-assisted summary`, generate the career strategy, and show the structured Gemini sections.
15. Point out `AI Career Strategy Summary`, `Top 3 Application Actions`, `Best Portfolio Evidence to Mention`, `Skill Gap Strategy`, and `Interview Focus Areas`.
16. Explain that the score, evidence, matches, and gaps are deterministic; Gemini only improves the narrative explanation.
17. Open the `Profile Match` tab and show the overall score, progress bar, category score breakdown, and category reasons.
18. In `Profile Match`, show strong matches, partial matches, missing skills, and evidence by skill.
19. Open the `Skill Gaps` tab and show prioritized recommendations.
20. Open `Portfolio Evidence` and show the project cards plus portfolio evidence map.
21. Open `Preparation Plan`, `Application Drafts`, and `Interview Prep` to show the mock guidance.
22. Open `Export`, click `Export Markdown Report`, and show the generated file path.
23. Open the exported Markdown report briefly.
24. Point out the Gemini-assisted section, score breakdown, evidence by skill, prioritized recommendations, and privacy notice.
25. Remind viewers that generated reports in `outputs/*.md` are ignored by Git.
26. Optional Step 4A code walkthrough: open `devpath/agent.py` and show that `root_agent` now exists.
27. Open `devpath/agent_tools.py` and explain that deterministic scoring, report building, portfolio summaries, and privacy masking are ready for ADK orchestration.
28. Explain that the Streamlit app still uses deterministic services directly; full ADK runtime routing is planned for a later step.
