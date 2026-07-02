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
11. Optionally switch to `Gemini-assisted summary` and show the warning if no API key is configured.
12. Later, when an API key is configured locally, show that Gemini adds a narrative summary without changing the deterministic score.
13. Open the `Profile Match` tab and show the overall score, progress bar, category score breakdown, and category reasons.
14. In `Profile Match`, show strong matches, partial matches, missing skills, and evidence by skill.
15. Open the `Skill Gaps` tab and show prioritized recommendations.
16. Open `Portfolio Evidence` and show the project cards plus portfolio evidence map.
17. Open `Preparation Plan`, `Application Drafts`, and `Interview Prep` to show the mock guidance.
18. Open `Export`, click `Export Markdown Report`, and show the generated file path.
19. Open the exported Markdown report briefly.
20. Point out the score breakdown, evidence by skill, prioritized recommendations, and privacy notice.
21. Remind viewers that generated reports in `outputs/*.md` are ignored by Git.
