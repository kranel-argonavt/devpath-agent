"""Deterministic match scoring logic for comparing profiles and job requirements."""

from collections.abc import Iterable
import re
from typing import Any


REQUIRED_KEYWORDS = ["C#", ".NET", "ASP.NET Core", "SQL", "Git", "REST API", "English"]
NICE_TO_HAVE_KEYWORDS = ["Docker", "Azure", "Unit Testing", "Entity Framework", "Cloud"]
PORTFOLIO_EVIDENCE_KEYWORDS = [
    "C#",
    ".NET",
    "WPF",
    "SQLite",
    "EF Core",
    "Unity",
    "FFmpeg",
    "Git",
    "ASP.NET Core",
    "REST API",
    "SQL",
]

CATEGORY_WEIGHTS = {
    "required_technical_skills": 35,
    "portfolio_evidence": 25,
    "nice_to_have_skills": 15,
    "experience_seniority_fit": 10,
    "language_location_fit": 10,
    "education_domain_relevance": 5,
}


def calculate_skill_overlap(candidate_skills: Iterable[str], required_skills: Iterable[str]) -> float:
    """Return a simple normalized overlap score between 0.0 and 1.0."""

    candidate = {skill.strip().lower() for skill in candidate_skills if skill and skill.strip()}
    required = {skill.strip().lower() for skill in required_skills if skill and skill.strip()}
    if not required:
        return 0.0
    return round(len(candidate & required) / len(required), 2)


def calculate_mock_match_score(
    job_text: str,
    profile: dict[str, Any],
    projects: list[dict[str, Any]],
) -> dict[str, Any]:
    """Calculate an approximate keyword-based mock match score."""

    job_required = _find_keywords(job_text, REQUIRED_KEYWORDS)
    job_nice_to_have = _find_keywords(job_text, NICE_TO_HAVE_KEYWORDS)
    profile_text = _profile_to_text(profile)
    project_text = _projects_to_text(projects)
    candidate_text = f"{profile_text}\n{project_text}"

    required_matches = _find_keywords(candidate_text, job_required)
    nice_matches = _find_keywords(candidate_text, job_nice_to_have)
    portfolio_matches = _find_keywords(project_text, PORTFOLIO_EVIDENCE_KEYWORDS)
    missing_skills = [skill for skill in job_required if skill not in required_matches]

    category_scores = {
        "required_technical_skills": _weighted_score(
            len(required_matches), len(job_required), CATEGORY_WEIGHTS["required_technical_skills"]
        ),
        "portfolio_evidence": _weighted_score(
            len(portfolio_matches), 6, CATEGORY_WEIGHTS["portfolio_evidence"]
        ),
        "nice_to_have_skills": _weighted_score(
            len(nice_matches), len(job_nice_to_have), CATEGORY_WEIGHTS["nice_to_have_skills"]
        ),
        "experience_seniority_fit": _experience_score(job_text, profile),
        "language_location_fit": _language_location_score(job_text, profile),
        "education_domain_relevance": _education_score(profile),
    }

    overall_score = min(100, sum(category_scores.values()))
    partial_matches = _partial_matches(job_required, required_matches, candidate_text)

    return {
        "overall_score": overall_score,
        "category_scores": category_scores,
        "strong_matches": sorted(set(required_matches + portfolio_matches)),
        "partial_matches": partial_matches,
        "missing_skills": missing_skills,
        "explanation": (
            f"Mock score based on {len(required_matches)} of {len(job_required)} required keywords, "
            f"{len(portfolio_matches)} portfolio evidence signals, and local profile fit checks."
        ),
    }


def _find_keywords(text: str, keywords: Iterable[str]) -> list[str]:
    """Return keywords that appear in text, preserving the provided keyword order."""

    return [keyword for keyword in keywords if _contains_keyword(text, keyword)]


def _contains_keyword(text: str, keyword: str) -> bool:
    normalized_text = _normalize(text)
    normalized_keyword = _normalize(keyword)
    return re.search(rf"(?<!\w){re.escape(normalized_keyword)}(?!\w)", normalized_text) is not None


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().replace("rest apis", "rest api").strip())


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


def _experience_score(job_text: str, profile: dict[str, Any]) -> int:
    experience_level = str(profile.get("experience_level", "")).lower()
    if "junior" in job_text.lower() and "junior" in experience_level:
        return CATEGORY_WEIGHTS["experience_seniority_fit"]
    if "junior" in experience_level:
        return 7
    return 4


def _language_location_score(job_text: str, profile: dict[str, Any]) -> int:
    profile_text = _profile_to_text(profile)
    score = 0
    if _contains_keyword(job_text, "English") and _contains_keyword(profile_text, "English"):
        score += 5
    if any(_contains_keyword(job_text, place) and _contains_keyword(profile_text, place) for place in ["Germany", "Remote", "EU"]):
        score += 5
    return min(score, CATEGORY_WEIGHTS["language_location_fit"])


def _education_score(profile: dict[str, Any]) -> int:
    education = str(profile.get("education", ""))
    if any(_contains_keyword(education, keyword) for keyword in ["Software Engineering", "Computer Science", "Informatics"]):
        return CATEGORY_WEIGHTS["education_domain_relevance"]
    return 2 if education else 0


def _partial_matches(job_required: list[str], required_matches: list[str], candidate_text: str) -> list[str]:
    partial: list[str] = []
    if "SQL" in job_required and "SQL" not in required_matches and _contains_keyword(candidate_text, "SQLite"):
        partial.append("SQL via SQLite experience")
    if "ASP.NET Core" in job_required and "ASP.NET Core" not in required_matches and _contains_keyword(candidate_text, ".NET"):
        partial.append("ASP.NET Core foundation via .NET experience")
    return partial
