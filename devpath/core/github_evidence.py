"""Deterministic evidence extraction from public GitHub repository metadata."""

from __future__ import annotations

from datetime import datetime, timezone
import re
from typing import Any


GITHUB_SKILL_ALIASES = {
    "C#": ["c#", "c sharp", "csharp"],
    ".NET": [".net", "dotnet", "netcore", ".net core"],
    "ASP.NET Core": ["asp.net core", "asp net core", "aspnetcore"],
    "SQL": ["sql", "sqlite", "postgres", "mysql"],
    "Git": ["git", "github"],
    "REST API": ["rest api", "restful", "api", "web api"],
    "Entity Framework": ["entity framework", "ef core"],
    "WPF": ["wpf"],
    "Unity": ["unity"],
    "Docker": ["docker"],
    "Azure": ["azure"],
    "Unit Testing": ["unit testing", "xunit", "nunit", "pytest", "tests"],
    "Cloud": ["cloud"],
}


def normalize_skill_name(value: str) -> str:
    """Return a canonical skill name when the value matches a known alias."""

    normalized = _normalize(value)
    for skill, aliases in GITHUB_SKILL_ALIASES.items():
        if normalized == _normalize(skill) or normalized in {_normalize(alias) for alias in aliases}:
            return skill
    return str(value or "").strip()


def extract_github_project_evidence(project: dict[str, Any]) -> dict[str, Any]:
    """Extract deterministic GitHub evidence from one project entry."""

    github = project.get("github") if isinstance(project.get("github"), dict) else {}
    name = str(project.get("name") or github.get("name") or "GitHub repository")
    url = str(project.get("url") or github.get("html_url") or "")
    language = str(github.get("language") or "").strip()
    topics = _clean_list(github.get("topics", []))
    description = str(project.get("description") or "")

    matched_skills: list[str] = []
    description_matches: list[str] = []
    evidence_notes: list[str] = []

    if language:
        skill = normalize_skill_name(language)
        if skill in GITHUB_SKILL_ALIASES:
            matched_skills.append(skill)
            evidence_notes.append(f"Primary language is {language}.")

    for topic in topics:
        skill = normalize_skill_name(topic)
        if skill in GITHUB_SKILL_ALIASES:
            matched_skills.append(skill)
            evidence_notes.append(f"Topic contains {topic}.")

    for skill, aliases in GITHUB_SKILL_ALIASES.items():
        if any(_contains_term(description, alias) for alias in aliases):
            matched_skills.append(skill)
            description_matches.append(skill)
            evidence_notes.append(f"Description mentions {skill}.")

    archived = bool(github.get("archived", False))
    fork = bool(github.get("fork", False))
    recently_updated = _is_recently_updated(str(github.get("pushed_at") or github.get("updated_at") or ""))
    if archived:
        evidence_notes.append("Repository is archived.")
    else:
        evidence_notes.append("Repository is public and non-archived.")
    if fork:
        evidence_notes.append("Repository is a fork.")
    if recently_updated:
        evidence_notes.append("Repository was updated recently.")

    return {
        "project_name": name,
        "project_url": url,
        "source": "github",
        "matched_skills": sorted(set(matched_skills)),
        "language": language,
        "topics": topics,
        "description_matches": sorted(set(description_matches)),
        "signals": {
            "stars": int(github.get("stars") or 0),
            "forks": int(github.get("forks") or 0),
            "recently_updated": recently_updated,
            "archived": archived,
            "fork": fork,
        },
        "evidence_notes": list(dict.fromkeys(evidence_notes)),
    }


def extract_github_evidence_for_projects(projects: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Extract GitHub evidence for all GitHub-sourced project entries."""

    return [
        extract_github_project_evidence(project)
        for project in projects
        if project.get("source") == "github" or isinstance(project.get("github"), dict)
    ]


def github_project_matches_skill(project: dict[str, Any], skill: str) -> dict[str, Any]:
    """Return deterministic match details for one GitHub project and skill."""

    evidence = extract_github_project_evidence(project)
    canonical = normalize_skill_name(skill)
    return {
        "project_name": evidence["project_name"],
        "project_url": evidence["project_url"],
        "skill": canonical,
        "matched": canonical in evidence["matched_skills"],
        "evidence_notes": [
            note for note in evidence["evidence_notes"] if canonical.lower() in note.lower()
        ],
        "signals": evidence["signals"],
    }


def _clean_list(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    return [str(value).strip() for value in values if str(value).strip()]


def _normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9#+.]+", " ", str(value or "").lower()).strip()


def _contains_term(text: str, term: str) -> bool:
    normalized_text = _normalize(text)
    normalized_term = _normalize(term)
    if not normalized_term:
        return False
    return re.search(rf"(?<![a-z0-9]){re.escape(normalized_term)}(?![a-z0-9])", normalized_text) is not None


def _is_recently_updated(value: str) -> bool:
    if not value:
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    now = datetime.now(timezone.utc)
    return (now - parsed.astimezone(timezone.utc)).days <= 365
