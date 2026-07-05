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
- GitHub public repository language, topics, and description when repos are imported

Evidence is shown in the UI and exported Markdown so users can connect claims to concrete projects.

## GitHub Evidence

For imported public GitHub repositories, deterministic evidence can come from:

- Primary language, such as `C#`
- Topics, such as `dotnet`, `api`, or `docker`
- Repository description mentions, such as `REST API` or `SQL`
- Public URL and source metadata for traceability

Stars, forks, archived status, fork status, and update timestamps are shown as repository signals. They do not create direct skill matches by themselves.

No source code, commit history, or private repository data is analyzed in Step 7B. Public README text can be fetched explicitly through the GitHub README helper, but default portfolio scoring still relies on public metadata and local project fields unless README content is intentionally passed into project evidence.

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
- Gemini may extract structured job/candidate context, but deterministic validators normalize or reject that context.
- Gemini may enhance narrative-only report sections for gaps, action plan, application drafts, and interview prep.
- ADK-style workflows orchestrate deterministic tools and expose trace metadata.
- MCP-style tools wrap the same deterministic scoring and report logic.
- The default Gemini/ADK tool-calling workflow requests MCP runtime first, then falls back to the local MCP-style registry and direct deterministic services.
- The Streamlit tool backend selector can still call direct services or local MCP-style tools in legacy workflow modes, but all paths preserve the same deterministic scoring behavior.
- GitHub metadata evidence feeds the same deterministic scoring path as local portfolio projects.

## Limitations

- The scorer is heuristic and keyword-based.
- It does not inspect source code or commit history.
- It may miss synonyms or context.
- It should support career preparation, not replace human judgment or hiring advice.
