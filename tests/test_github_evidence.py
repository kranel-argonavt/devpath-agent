"""Tests for deterministic GitHub metadata evidence extraction."""

from devpath.core.github_evidence import (
    extract_github_project_evidence,
    extract_github_evidence_for_projects,
    github_project_matches_skill,
    normalize_skill_name,
)


def test_normalize_skill_name_maps_known_aliases() -> None:
    assert normalize_skill_name("dotnet") == ".NET"
    assert normalize_skill_name("api") == "REST API"
    assert normalize_skill_name("C#") == "C#"


def test_primary_language_topic_and_description_match_skills() -> None:
    evidence = extract_github_project_evidence(_github_project())

    assert set(evidence["matched_skills"]) == {"C#", ".NET", "REST API", "SQL"}
    assert "Primary language is C#." in evidence["evidence_notes"]
    assert "Topic contains dotnet." in evidence["evidence_notes"]
    assert "Description mentions REST API." in evidence["evidence_notes"]
    assert "Description mentions SQL." in evidence["evidence_notes"]


def test_url_source_and_signals_are_preserved() -> None:
    evidence = extract_github_project_evidence(_github_project(archived=True, fork=True))

    assert evidence["project_url"] == "https://github.com/example/student-api"
    assert evidence["source"] == "github"
    assert evidence["signals"]["stars"] == 4
    assert evidence["signals"]["forks"] == 2
    assert evidence["signals"]["archived"] is True
    assert evidence["signals"]["fork"] is True
    assert "Repository is archived." in evidence["evidence_notes"]
    assert "Repository is a fork." in evidence["evidence_notes"]


def test_stars_do_not_create_skill_evidence_by_themselves() -> None:
    project = _github_project(description="", language="", topics=[])
    project["github"]["stars"] = 999

    evidence = extract_github_project_evidence(project)

    assert evidence["matched_skills"] == []


def test_empty_metadata_is_handled_safely() -> None:
    evidence = extract_github_project_evidence({"name": "Empty Repo", "source": "github"})

    assert evidence["project_name"] == "Empty Repo"
    assert evidence["matched_skills"] == []
    assert evidence["signals"]["archived"] is False


def test_extract_github_evidence_for_projects_filters_non_github_projects() -> None:
    evidence = extract_github_evidence_for_projects(
        [_github_project(), {"name": "Local Project", "technologies": ["C#"]}]
    )

    assert len(evidence) == 1
    assert evidence[0]["project_name"] == "Student API"


def test_github_project_matches_skill_returns_match_details() -> None:
    result = github_project_matches_skill(_github_project(), "REST API")

    assert result["matched"] is True
    assert result["project_name"] == "Student API"
    assert result["skill"] == "REST API"


def _github_project(
    *,
    description: str = "REST API with SQL persistence.",
    language: str = "C#",
    topics: list[str] | None = None,
    archived: bool = False,
    fork: bool = False,
) -> dict:
    return {
        "name": "Student API",
        "description": description,
        "url": "https://github.com/example/student-api",
        "source": "github",
        "github": {
            "name": "student-api",
            "html_url": "https://github.com/example/student-api",
            "language": language,
            "topics": topics if topics is not None else ["dotnet"],
            "stars": 4,
            "forks": 2,
            "updated_at": "2026-01-02T00:00:00Z",
            "pushed_at": "2026-01-03T00:00:00Z",
            "fork": fork,
            "archived": archived,
        },
    }
