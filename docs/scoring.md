# Scoring

Step 2A improved DevPath Agent scoring while keeping it fully deterministic. Step 2B exposes that richer scoring output in the Streamlit UI. The current scorer does not use Gemini, Google ADK, MCP tools, GitHub APIs, or any real LLM calls.

## Current Deterministic Approach

The scoring flow is:

```text
job posting requirements
-> normalized skills
-> profile evidence
-> portfolio evidence
-> match categories
-> score breakdown
-> prioritized gaps
-> explanation
```

`devpath/core/scoring.py` extracts heuristic requirements from the job text, normalizes skills through aliases, collects evidence from the candidate profile and portfolio projects, and returns an explainable score object.

## Skill Normalization

The scorer maps common aliases to canonical skill names. Examples:

- `c#`, `c sharp`, and `csharp` map to `C#`.
- `.net`, `dotnet`, `.net 8`, and `.net core` map to `.NET`.
- `asp.net core`, `asp net core`, and `aspnetcore` map to `ASP.NET Core`.
- `sqlite`, `mysql`, and `postgresql` are treated as SQL-related evidence.
- `ef core` maps to `Entity Framework`.

Important boundary: general `.NET` or `Entity Framework` evidence does not count as `ASP.NET Core` evidence. If a job requires ASP.NET Core, the scorer expects ASP.NET Core-specific evidence.

## Evidence-Based Scoring

The result includes:

- `overall_score`;
- `category_scores`;
- `category_details`;
- `strong_matches`;
- `partial_matches`;
- `missing_skills`;
- `evidence_by_skill`;
- `prioritized_gaps`;
- `explanation`.

Profile evidence comes from candidate fields such as skills, languages, education, and location preference. Portfolio evidence comes from flexible project fields such as name, technologies, summary, description, stack, features, and highlights.

## Streamlit Display In Step 2B

The Streamlit mock workflow now displays:

- overall score and progress;
- category scores with earned/max values and reasons;
- strong matches, partial matches, and missing skills in separate columns;
- evidence by skill;
- portfolio evidence mapped to projects;
- prioritized gaps with recommendations.

These UI sections consume the deterministic report data and remain safe if optional keys are missing.

## Weighted Matrix

- Required technical skills: 35%
- Portfolio evidence: 25%
- Nice-to-have skills: 15%
- Experience/seniority fit: 10%
- Language/location fit: 10%
- Education/domain relevance: 5%

Category scores are deterministic and sum to the overall score, capped between 0 and 100.

## Partial Matches

Partial matches are called out separately so related evidence is visible without overstating readiness. Examples:

- SQLite can support SQL-related evidence.
- Generic API work can partially support REST API evidence when REST-specific wording is missing.
- General or desktop `.NET` evidence helps for .NET readiness but does not satisfy ASP.NET Core.

## Limitations

- The scorer is still heuristic and keyword-based.
- It can miss synonyms, context, seniority nuance, and quality of implementation.
- It does not inspect source code or repository history.
- It should not be treated as hiring advice.

## Future Gemini And ADK Role

Future steps can use Gemini and Google ADK agents to improve requirement extraction, evidence reasoning, recommendations, and natural-language explanations. The deterministic scorer should remain useful as a transparent baseline and fallback.
