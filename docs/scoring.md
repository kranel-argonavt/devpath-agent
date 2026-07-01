# Scoring

The current Step 1B/1C/1D scoring system is deterministic and keyword-based. It is useful for demos and early workflow validation, but it is not the final career-matching model.

## Current Mock Scoring

`devpath/core/scoring.py` looks for important keywords in the job posting, candidate profile, and portfolio projects. It returns:

- overall score;
- category scores;
- strong matches;
- partial matches;
- missing skills;
- short explanation.

The logic is intentionally simple and explainable. It should be improved later with better evidence extraction, structured requirement parsing, and agent-assisted reasoning.

## Planned Weighted Matrix

- Required technical skills: 35%
- Portfolio evidence: 25%
- Nice-to-have skills: 15%
- Experience/seniority fit: 10%
- Language/location fit: 10%
- Education/domain relevance: 5%

## Known Limitations

- Keyword matching can miss synonyms and context.
- Project evidence is approximate.
- The current scoring does not judge code quality.
- The score should not be treated as hiring advice.
