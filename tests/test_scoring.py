"""Tests for deterministic evidence-based scoring helpers."""

from devpath.core.scoring import (
    calculate_mock_match_score,
    collect_project_evidence,
    extract_job_requirements,
)


def test_calculate_mock_match_score_returns_score_between_zero_and_one_hundred() -> None:
    result = calculate_mock_match_score(
        job_text="Junior .NET Developer requiring C#, .NET, ASP.NET Core, SQL, Git, REST API, English.",
        profile={
            "experience_level": "Junior",
            "skills": ["C#", ".NET", "Git"],
            "languages": ["English B1-B2"],
            "education": "Software Engineering",
            "location_preference": "Germany / Remote EU",
        },
        projects=[
            {
                "name": "TaskFlow Desktop",
                "summary": "Desktop project with local SQLite persistence.",
                "technologies": ["C#", ".NET", "WPF", "SQLite", "Git"],
            }
        ],
    )

    assert "overall_score" in result
    assert 0 <= result["overall_score"] <= 100


def test_extract_job_requirements_detects_required_skills() -> None:
    requirements = extract_job_requirements(
        "Junior .NET Developer requirements: C#, .NET, ASP.NET Core, SQL, Git, REST API, English."
    )

    assert requirements["required_skills"] == ["C#", ".NET", "ASP.NET Core", "SQL", "Git", "REST API", "English"]
    assert requirements["detected_seniority"] == "Junior"
    assert requirements["detected_languages"] == ["English"]


def test_dotnet_does_not_automatically_count_as_aspnet_core() -> None:
    result = calculate_mock_match_score(
        job_text="Junior backend role requiring ASP.NET Core.",
        profile={"experience_level": "Junior", "skills": [".NET", "C#"]},
        projects=[
            {
                "name": "Desktop Tool",
                "summary": ".NET desktop app using WPF.",
                "technologies": ["C#", ".NET", "WPF"],
            }
        ],
    )

    assert ".NET" in result["evidence_by_skill"]
    assert "ASP.NET Core" not in result["strong_matches"]
    assert "ASP.NET Core" in result["missing_skills"]


def test_missing_aspnet_core_appears_as_prioritized_gap() -> None:
    result = calculate_mock_match_score(
        job_text="Requirements: C#, .NET, ASP.NET Core, Git, English.",
        profile={"experience_level": "Junior", "skills": ["C#", ".NET", "Git"], "languages": ["English"]},
        projects=[
            {
                "name": "TaskFlow Desktop",
                "summary": "C# desktop project.",
                "technologies": ["C#", ".NET", "WPF"],
            }
        ],
    )

    assert "ASP.NET Core" in result["missing_skills"]
    assert any(gap["skill"] == "ASP.NET Core" for gap in result["prioritized_gaps"])


def test_collect_project_evidence_includes_project_names_for_matching_skills() -> None:
    evidence = collect_project_evidence(
        [
            {
                "name": "Student API Demo",
                "summary": "REST API backed by SQL and Git workflow.",
                "technologies": ["C#", ".NET", "ASP.NET Core", "SQL", "Git", "REST API"],
            }
        ]
    )

    assert "Student API Demo" in evidence["C#"]
    assert "Student API Demo" in evidence["ASP.NET Core"]
    assert "Student API Demo" in evidence["REST API"]


def test_evidence_by_skill_contains_project_sources() -> None:
    result = calculate_mock_match_score(
        job_text="Junior .NET Developer requiring C#, .NET, SQL, Git, REST API, English.",
        profile={"experience_level": "Junior", "skills": ["C#"], "languages": ["English"]},
        projects=[
            {
                "name": "Student API Demo",
                "summary": "REST API backed by SQL and Git workflow.",
                "technologies": [".NET", "SQL", "Git", "REST API"],
            }
        ],
    )

    assert "Project: Student API Demo" in result["evidence_by_skill"]["REST API"]
    assert "Project: Student API Demo" in result["evidence_by_skill"]["SQL"]


def test_prioritized_gaps_contain_recommendations() -> None:
    result = calculate_mock_match_score(
        job_text="Requirements: ASP.NET Core, REST API.",
        profile={"experience_level": "Junior", "skills": [".NET"]},
        projects=[],
    )

    assert result["prioritized_gaps"]
    assert all(gap["recommendation"] for gap in result["prioritized_gaps"])


def test_category_scores_are_present_and_numeric() -> None:
    result = calculate_mock_match_score(
        job_text="Junior role requiring C#, .NET, Git. Nice to have: Docker and Unit Testing.",
        profile={"experience_level": "Junior", "skills": ["C#", ".NET", "Git"]},
        projects=[{"name": "Tool", "summary": "C# .NET project", "technologies": ["C#", ".NET", "Git"]}],
    )

    assert set(result["category_scores"]) == {
        "required_technical_skills",
        "portfolio_evidence",
        "nice_to_have_skills",
        "experience_seniority_fit",
        "language_location_fit",
        "education_domain_relevance",
    }
    assert all(isinstance(score, int) for score in result["category_scores"].values())
    assert all("earned" in detail and "max" in detail for detail in result["category_details"].values())
