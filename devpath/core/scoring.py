"""Deterministic match scoring logic for comparing profiles and job requirements."""

from collections.abc import Iterable
import re
from typing import Any


SKILL_ALIASES = {
    "C#": ["c#", "c sharp", "csharp"],
    ".NET": [".net", "dotnet", ".net 8", ".net core"],
    "ASP.NET Core": ["asp.net core", "asp net core", "aspnetcore"],
    "SQL": ["sql", "sqlite", "ms sql", "mysql", "postgresql"],
    "Git": ["git", "github"],
    "REST API": ["rest api", "restful", "api integration", "web api"],
    "English": ["english", "b1", "b2"],
    "Entity Framework": ["entity framework", "ef core"],
    "WPF": ["wpf"],
    "Unity": ["unity"],
    "Docker": ["docker"],
    "Azure": ["azure"],
    "Unit Testing": ["unit testing", "pytest", "xunit", "nunit", "tests"],
    "Cloud": ["cloud"],
}

REQUIRED_SKILLS = ["C#", ".NET", "ASP.NET Core", "SQL", "Git", "REST API", "English"]
NICE_TO_HAVE_SKILLS = ["Docker", "Azure", "Unit Testing", "Entity Framework", "Cloud"]

CATEGORY_WEIGHTS = {
    "required_technical_skills": 35,
    "portfolio_evidence": 25,
    "nice_to_have_skills": 15,
    "experience_seniority_fit": 10,
    "language_location_fit": 10,
    "education_domain_relevance": 5,
}

GAP_RECOMMENDATIONS = {
    "ASP.NET Core": "Build a small ASP.NET Core REST API project and add it to the portfolio.",
    "REST API": "Add a project README section that explains REST endpoints, requests, and responses.",
    "SQL": "Practice relational queries and document database work in a portfolio project.",
    "Git": "Show a public repository with clear commits, branches, and README documentation.",
    "English": "Prepare concise English project explanations and interview answers.",
    "Docker": "Containerize a small .NET app and document the Docker workflow.",
    "Azure": "Deploy or describe a small cloud-hosted .NET demo when ready.",
    "Unit Testing": "Add xUnit or NUnit tests to a project and mention what they verify.",
    "Entity Framework": "Use EF Core in a small CRUD project and document the data model.",
    ".NET": "Create a focused .NET project that shows framework fundamentals.",
    "C#": "Strengthen C# examples with clean classes, collections, and error handling.",
}


def calculate_skill_overlap(candidate_skills: Iterable[str], required_skills: Iterable[str]) -> float:
    """Return a simple normalized overlap score between 0.0 and 1.0."""

    candidate = {skill.strip().lower() for skill in candidate_skills if skill and skill.strip()}
    required = {skill.strip().lower() for skill in required_skills if skill and skill.strip()}
    if not required:
        return 0.0
    return round(len(candidate & required) / len(required), 2)


def normalize_text(text: str) -> str:
    """Normalize text for deterministic matching."""

    normalized = text.lower().replace("rest apis", "rest api")
    normalized = normalized.replace("c-sharp", "c sharp")
    return re.sub(r"\s+", " ", normalized).strip()


def detect_skills_in_text(text: str) -> set[str]:
    """Detect canonical skills in text using deterministic aliases."""

    normalized = normalize_text(text)
    return {
        canonical
        for canonical, aliases in SKILL_ALIASES.items()
        if any(_alias_found(normalized, alias, canonical) for alias in aliases)
    }


def extract_job_requirements(job_text: str) -> dict[str, Any]:
    """Extract heuristic job requirements from a posting."""

    detected_skills = detect_skills_in_text(job_text)
    nice_context = _extract_nice_to_have_context(job_text)
    nice_skills = detect_skills_in_text(nice_context) & set(NICE_TO_HAVE_SKILLS)
    required_skills = [skill for skill in REQUIRED_SKILLS if skill in detected_skills and skill not in nice_skills]

    return {
        "required_skills": required_skills,
        "nice_to_have_skills": [skill for skill in NICE_TO_HAVE_SKILLS if skill in nice_skills],
        "responsibilities": _extract_responsibilities(job_text),
        "detected_seniority": _detect_seniority(job_text),
        "detected_languages": [skill for skill in ["English"] if skill in detected_skills],
    }


def collect_profile_skills(profile: dict[str, Any]) -> set[str]:
    """Collect normalized profile skills from flexible profile dictionaries."""

    return detect_skills_in_text(_profile_to_text(profile))


def collect_project_evidence(projects: list[dict[str, Any]]) -> dict[str, list[str]]:
    """Map detected skills to project names that provide portfolio evidence."""

    evidence: dict[str, list[str]] = {}
    for index, project in enumerate(projects):
        name = str(project.get("name") or f"Project {index + 1}")
        project_text = " ".join(_flatten(project))
        for skill in detect_skills_in_text(project_text):
            evidence.setdefault(skill, [])
            if name not in evidence[skill]:
                evidence[skill].append(name)
    return evidence


def calculate_mock_match_score(
    job_text: str,
    profile: dict[str, Any],
    projects: list[dict[str, Any]],
) -> dict[str, Any]:
    """Calculate an evidence-based deterministic mock match score."""

    job_requirements = extract_job_requirements(job_text)
    required_skills = job_requirements["required_skills"]
    nice_skills = job_requirements["nice_to_have_skills"]
    profile_skills = collect_profile_skills(profile)
    project_evidence = collect_project_evidence(projects)
    candidate_skills = profile_skills | set(project_evidence)

    evidence_by_skill = _build_evidence_by_skill(profile_skills, project_evidence)
    full_required_matches = [skill for skill in required_skills if skill in candidate_skills]
    nice_matches = [skill for skill in nice_skills if skill in candidate_skills]
    missing_skills = [skill for skill in required_skills if skill not in candidate_skills]
    partial_matches = _build_partial_matches(required_skills, candidate_skills, profile, projects)
    prioritized_gaps = _build_prioritized_gaps(missing_skills, nice_skills, nice_matches)

    category_scores = {
        "required_technical_skills": _weighted_score(
            len(full_required_matches), len(required_skills), CATEGORY_WEIGHTS["required_technical_skills"]
        ),
        "portfolio_evidence": _portfolio_score(required_skills, project_evidence),
        "nice_to_have_skills": _weighted_score(
            len(nice_matches), len(nice_skills), CATEGORY_WEIGHTS["nice_to_have_skills"]
        ),
        "experience_seniority_fit": _experience_score(job_requirements, profile),
        "language_location_fit": _language_location_score(job_text, job_requirements, profile),
        "education_domain_relevance": _education_score(profile),
    }
    overall_score = max(0, min(100, sum(category_scores.values())))

    category_details = _build_category_details(
        category_scores=category_scores,
        required_skills=required_skills,
        full_required_matches=full_required_matches,
        missing_skills=missing_skills,
        project_evidence=project_evidence,
        nice_skills=nice_skills,
        nice_matches=nice_matches,
        job_requirements=job_requirements,
        profile=profile,
    )

    return {
        "overall_score": overall_score,
        "category_scores": category_scores,
        "category_details": category_details,
        "job_requirements": job_requirements,
        "strong_matches": sorted(set(full_required_matches + nice_matches)),
        "partial_matches": partial_matches,
        "missing_skills": missing_skills,
        "evidence_by_skill": evidence_by_skill,
        "prioritized_gaps": prioritized_gaps,
        "explanation": (
            f"Deterministic score based on {len(full_required_matches)} of {len(required_skills)} required skills, "
            f"{len(project_evidence)} portfolio evidence skill areas, and profile fit signals. "
            "No LLM or external API calls were used."
        ),
    }


def _alias_found(normalized_text: str, alias: str, canonical: str) -> bool:
    normalized_alias = normalize_text(alias)
    if canonical == ".NET":
        return re.search(r"(?<![a-z0-9])(?:\.net(?:\s+(?:8|core))?|dotnet)(?![a-z0-9])", normalized_text) is not None
    if canonical == "C#":
        return re.search(r"(?<![a-z0-9])(?:c#|c sharp|csharp)(?![a-z0-9])", normalized_text) is not None
    if canonical == "ASP.NET Core":
        return re.search(r"(?<![a-z0-9])(?:asp\.net core|asp net core|aspnetcore)(?![a-z0-9])", normalized_text) is not None
    if canonical == "SQL" and normalized_alias == "sql":
        return re.search(r"(?<![a-z0-9])sql(?![a-z0-9])", normalized_text) is not None
    return re.search(rf"(?<![a-z0-9]){re.escape(normalized_alias)}(?![a-z0-9])", normalized_text) is not None


def _extract_nice_to_have_context(job_text: str) -> str:
    markers = ["nice to have", "bonus", "preferred", "plus"]
    normalized = normalize_text(job_text)
    positions = [normalized.find(marker) for marker in markers if marker in normalized]
    if not positions:
        return ""
    return normalized[min(positions) :]


def _extract_responsibilities(job_text: str) -> list[str]:
    lines = [line.strip(" -\t") for line in job_text.splitlines()]
    return [line for line in lines if line and _looks_like_responsibility(line)][:8]


def _looks_like_responsibility(line: str) -> bool:
    starts = ("develop", "build", "work", "collaborate", "use", "participate", "maintain", "support")
    return normalize_text(line).startswith(starts)


def _detect_seniority(job_text: str) -> str:
    normalized = normalize_text(job_text)
    if "intern" in normalized:
        return "Intern"
    if "junior" in normalized:
        return "Junior"
    if "senior" in normalized:
        return "Senior"
    if "mid" in normalized:
        return "Mid"
    return "Unknown"


def _profile_to_text(profile: dict[str, Any]) -> str:
    return " ".join(_flatten(profile.values()))


def _projects_to_text(projects: list[dict[str, Any]]) -> str:
    return " ".join(_flatten(projects))


def _flatten(value: Any) -> list[str]:
    if isinstance(value, dict):
        return _flatten(value.values())
    if isinstance(value, list | tuple | set):
        flattened: list[str] = []
        for item in value:
            flattened.extend(_flatten(item))
        return flattened
    if value is None:
        return []
    return [str(value)]


def _weighted_score(matches: int, total: int, weight: int) -> int:
    if total <= 0:
        return 0
    return round((matches / total) * weight)


def _portfolio_score(required_skills: list[str], project_evidence: dict[str, list[str]]) -> int:
    if not required_skills or not project_evidence:
        return 0
    project_matches = [skill for skill in required_skills if skill in project_evidence]
    return _weighted_score(len(project_matches), len(required_skills), CATEGORY_WEIGHTS["portfolio_evidence"])


def _experience_score(job_requirements: dict[str, Any], profile: dict[str, Any]) -> int:
    detected_seniority = str(job_requirements.get("detected_seniority", "Unknown")).lower()
    experience_level = str(profile.get("experience_level", "")).lower()
    if detected_seniority and detected_seniority != "unknown" and detected_seniority in experience_level:
        return CATEGORY_WEIGHTS["experience_seniority_fit"]
    if "junior" in experience_level and detected_seniority in {"unknown", "intern"}:
        return 7
    if experience_level:
        return 4
    return 0


def _language_location_score(job_text: str, job_requirements: dict[str, Any], profile: dict[str, Any]) -> int:
    profile_text = _profile_to_text(profile)
    score = 0
    if "English" in job_requirements.get("detected_languages", []) and "English" in detect_skills_in_text(profile_text):
        score += 5
    if any(_contains_plain_term(job_text, place) and _contains_plain_term(profile_text, place) for place in ["Germany", "Remote", "EU"]):
        score += 5
    return min(score, CATEGORY_WEIGHTS["language_location_fit"])


def _education_score(profile: dict[str, Any]) -> int:
    education = str(profile.get("education", ""))
    if any(_contains_plain_term(education, keyword) for keyword in ["Software Engineering", "Computer Science", "Informatics"]):
        return CATEGORY_WEIGHTS["education_domain_relevance"]
    return 2 if education else 0


def _contains_plain_term(text: str, term: str) -> bool:
    return re.search(rf"(?<![a-z0-9]){re.escape(normalize_text(term))}(?![a-z0-9])", normalize_text(text)) is not None


def _build_evidence_by_skill(profile_skills: set[str], project_evidence: dict[str, list[str]]) -> dict[str, list[str]]:
    evidence: dict[str, list[str]] = {}
    for skill in sorted(profile_skills | set(project_evidence)):
        sources: list[str] = []
        if skill in profile_skills:
            sources.append("Profile skills")
        sources.extend(f"Project: {project}" for project in project_evidence.get(skill, []))
        evidence[skill] = sources
    return evidence


def _build_partial_matches(
    required_skills: list[str],
    candidate_skills: set[str],
    profile: dict[str, Any],
    projects: list[dict[str, Any]],
) -> list[str]:
    candidate_text = normalize_text(f"{_profile_to_text(profile)} {_projects_to_text(projects)}")
    partial: list[str] = []
    if "SQL" in required_skills and "sqlite" in candidate_text:
        partial.append("SQL: related evidence found through SQLite.")
    if "REST API" in required_skills and "REST API" not in candidate_skills and _contains_plain_term(candidate_text, "API"):
        partial.append("REST API: generic API evidence found, but REST-specific evidence is weak.")
    if ".NET" in required_skills and ".NET" in candidate_skills and "ASP.NET Core" in required_skills and "ASP.NET Core" not in candidate_skills:
        partial.append(".NET: desktop or general .NET evidence helps, but it is not ASP.NET Core evidence.")
    return partial


def _build_prioritized_gaps(
    missing_skills: list[str],
    nice_skills: list[str],
    nice_matches: list[str],
) -> list[dict[str, str]]:
    gaps = [
        {
            "skill": skill,
            "priority": "High",
            "reason": "Required by the job posting but not found in profile or project evidence.",
            "recommendation": GAP_RECOMMENDATIONS.get(skill, f"Add clear portfolio evidence for {skill}."),
        }
        for skill in missing_skills
    ]
    for skill in nice_skills:
        if skill not in nice_matches:
            gaps.append(
                {
                    "skill": skill,
                    "priority": "Medium",
                    "reason": "Listed as a nice-to-have skill but not found in current evidence.",
                    "recommendation": GAP_RECOMMENDATIONS.get(skill, f"Consider adding light evidence for {skill}."),
                }
            )
    return gaps


def _build_category_details(
    category_scores: dict[str, int],
    required_skills: list[str],
    full_required_matches: list[str],
    missing_skills: list[str],
    project_evidence: dict[str, list[str]],
    nice_skills: list[str],
    nice_matches: list[str],
    job_requirements: dict[str, Any],
    profile: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    project_required_matches = [skill for skill in required_skills if skill in project_evidence]
    return {
        "required_technical_skills": {
            "earned": category_scores["required_technical_skills"],
            "max": CATEGORY_WEIGHTS["required_technical_skills"],
            "reason": _match_reason(full_required_matches, missing_skills, "required skill"),
        },
        "portfolio_evidence": {
            "earned": category_scores["portfolio_evidence"],
            "max": CATEGORY_WEIGHTS["portfolio_evidence"],
            "reason": _match_reason(project_required_matches, [skill for skill in required_skills if skill not in project_evidence], "portfolio skill"),
        },
        "nice_to_have_skills": {
            "earned": category_scores["nice_to_have_skills"],
            "max": CATEGORY_WEIGHTS["nice_to_have_skills"],
            "reason": _match_reason(nice_matches, [skill for skill in nice_skills if skill not in nice_matches], "nice-to-have skill"),
        },
        "experience_seniority_fit": {
            "earned": category_scores["experience_seniority_fit"],
            "max": CATEGORY_WEIGHTS["experience_seniority_fit"],
            "reason": f"Job seniority: {job_requirements.get('detected_seniority', 'Unknown')}; profile level: {profile.get('experience_level', 'Unknown')}.",
        },
        "language_location_fit": {
            "earned": category_scores["language_location_fit"],
            "max": CATEGORY_WEIGHTS["language_location_fit"],
            "reason": "Checks English plus Germany/Remote/EU alignment when those signals are present.",
        },
        "education_domain_relevance": {
            "earned": category_scores["education_domain_relevance"],
            "max": CATEGORY_WEIGHTS["education_domain_relevance"],
            "reason": f"Education signal: {profile.get('education', 'Not provided')}.",
        },
    }


def _match_reason(matches: list[str], missing: list[str], label: str) -> str:
    matched_text = ", ".join(matches) if matches else "none"
    missing_text = ", ".join(missing) if missing else "none"
    return f"Matched {label}s: {matched_text}. Missing or weak {label}s: {missing_text}."
