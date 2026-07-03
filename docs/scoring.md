# Scoring

DevPath Agent uses deterministic scoring so the candidate can see why a score was produced. The score is explainable, testable, and stable across runs.

## Why Deterministic Scoring

The project uses deterministic scoring because career guidance should not depend on hidden or shifting LLM judgment. Gemini and future agents may explain the report, but the score, gaps, evidence, and category details are calculated locally.

## Scoring Flow

```text
job posting requirements
   |
normalized skills
   |
profile evidence + portfolio evidence
   |
strong / partial / missing classification
   |
weighted category scores
   |
prioritized gaps
   |
explanation
```

## Weighted Categories

- Required technical skills: 35%
- Portfolio evidence: 25%
- Nice-to-have skills: 15%
- Experience/seniority fit: 10%
- Language/location fit: 10%
- Education/domain relevance: 5%

Category scores are deterministic and capped so the overall score stays between 0 and 100.

## Skill Normalization

The scorer maps aliases to canonical skills. Examples:

- `c#`, `c sharp`, and `csharp` map to `C#`.
- `.net`, `dotnet`, `.net 8`, and `.net core` map to `.NET`.
- `asp.net core`, `asp net core`, and `aspnetcore` map to `ASP.NET Core`.
- `sqlite`, `mysql`, and `postgresql` are treated as SQL-related evidence.
- `ef core` maps to `Entity Framework`.

Important boundary: `.NET` or `Entity Framework` evidence does not count as `ASP.NET Core` evidence.

## Evidence By Skill

The scorer builds `evidence_by_skill` from:

- Profile skills and languages
- Portfolio project technologies
- Project descriptions, summaries, features, stack, and highlights

Evidence is shown in the UI and exported Markdown so users can connect claims to concrete projects.

## Match Classification

- Strong matches are required or nice-to-have skills found in candidate evidence.
- Partial matches are related evidence that helps but does not fully satisfy a requirement.
- Missing skills are required skills from the job posting that are not found in the profile or portfolio evidence.

Partial examples:

- SQLite can support SQL-related evidence.
- Generic API work can partially support REST API evidence.
- Desktop `.NET` evidence helps for .NET readiness but does not satisfy ASP.NET Core.

## Prioritized Gaps

Required missing skills become high-priority gaps. Missing nice-to-have skills become medium-priority gaps. Each prioritized gap includes a reason and recommendation.

## Gemini, ADK, And MCP

- Gemini does not modify scores.
- ADK agent skeletons can orchestrate deterministic tools in future steps.
- MCP-style tools wrap the same deterministic scoring and report logic.
- The Streamlit tool backend selector can call direct services or local MCP-style tools, but both paths preserve the same deterministic scoring behavior.

## Limitations

- The scorer is heuristic and keyword-based.
- It does not inspect source code or commit history.
- It may miss synonyms or context.
- It should support career preparation, not replace human judgment or hiring advice.
