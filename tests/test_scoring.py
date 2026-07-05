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


def test_extract_job_requirements_detects_python_backend_skills() -> None:
    requirements = extract_job_requirements(
        "Junior Python Backend Developer requirements: Python, FastAPI, SQL, Git, REST API, English."
    )

    assert requirements["required_skills"] == ["Python", "FastAPI", "SQL", "Git", "REST API", "English"]


def test_extract_job_requirements_detects_frontend_react_skills() -> None:
    requirements = extract_job_requirements(
        "Junior Frontend Developer requiring React, TypeScript, JavaScript, HTML, CSS, Git, REST API, and English. "
        "Nice to have: Next.js, Figma, Docker, Unit Testing with Jest."
    )

    assert requirements["required_skills"] == [
        "React",
        "JavaScript",
        "TypeScript",
        "HTML",
        "CSS",
        "Git",
        "REST API",
        "English",
    ]
    assert requirements["nice_to_have_skills"] == ["Docker", "Unit Testing", "Next.js", "Figma"]


def test_frontend_project_evidence_detects_react_stack() -> None:
    evidence = collect_project_evidence(
        [
            {
                "name": "TaskBoard React Dashboard",
                "summary": "React TypeScript dashboard with responsive layout and REST API integration.",
                "technologies": ["React", "TypeScript", "JavaScript", "HTML", "CSS", "REST API", "Git"],
            }
        ]
    )

    assert "TaskBoard React Dashboard" in evidence["React"]
    assert "TaskBoard React Dashboard" in evidence["TypeScript"]
    assert "TaskBoard React Dashboard" in evidence["HTML"]
    assert "TaskBoard React Dashboard" in evidence["CSS"]


def test_portfolio_evidence_does_not_require_language_project_evidence() -> None:
    result = calculate_mock_match_score(
        job_text="Junior role requiring Python, SQL, Git, REST API, English.",
        profile={
            "experience_level": "Junior",
            "skills": ["Python", "SQL", "Git", "REST API"],
            "languages": ["English B2"],
        },
        projects=[
            {
                "name": "Backend API",
                "summary": "Python REST API with SQL persistence and Git workflow.",
                "technologies": ["Python", "SQL", "Git", "REST API"],
            }
        ],
    )

    portfolio_reason = result["category_details"]["portfolio_evidence"]["reason"]
    assert "English" not in portfolio_reason
    assert portfolio_reason == (
        "Matched portfolio evidence: Python, SQL, Git, REST API. "
        "Required skills without project evidence: none."
    )


def test_internal_does_not_count_as_intern_seniority() -> None:
    requirements = extract_job_requirements(
        "Junior .NET Developer building internal web services with C#, .NET, SQL, Git, and English."
    )

    assert requirements["detected_seniority"] == "Junior"


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


def test_github_language_can_support_required_skill() -> None:
    result = calculate_mock_match_score(
        job_text="Junior role requiring C#.",
        profile={"experience_level": "Junior", "skills": []},
        projects=[_github_project(language="C#", topics=[], description="Small portfolio project.")],
    )

    assert "C#" in result["strong_matches"]
    assert "Project: Student API (GitHub: https://github.com/example/student-api)" in result["evidence_by_skill"]["C#"]


def test_github_topic_can_support_required_skill() -> None:
    result = calculate_mock_match_score(
        job_text="Junior role requiring .NET.",
        profile={"experience_level": "Junior", "skills": []},
        projects=[_github_project(language="", topics=["dotnet"], description="Small portfolio project.")],
    )

    assert ".NET" in result["strong_matches"]
    assert ".NET" in result["evidence_by_skill"]


def test_github_description_can_support_required_skill() -> None:
    result = calculate_mock_match_score(
        job_text="Junior role requiring REST API.",
        profile={"experience_level": "Junior", "skills": []},
        projects=[_github_project(language="", topics=[], description="A REST API with SQL persistence.")],
    )

    assert "REST API" in result["strong_matches"]
    assert "REST API" in result["evidence_by_skill"]


def test_github_evidence_is_returned_in_scoring_result() -> None:
    result = calculate_mock_match_score(
        job_text="Junior role requiring C#, .NET, REST API.",
        profile={"experience_level": "Junior", "skills": []},
        projects=[_github_project()],
    )

    assert result["github_evidence"][0]["project_name"] == "Student API"
    assert result["github_evidence"][0]["project_url"] == "https://github.com/example/student-api"
    assert "Repository is public and non-archived." in result["github_evidence"][0]["evidence_notes"]


def test_local_project_evidence_still_works() -> None:
    evidence = collect_project_evidence(
        [{"name": "Local API", "technologies": ["C#", "REST API"], "description": "Local project."}]
    )

    assert evidence["C#"] == ["Local API"]
    assert evidence["REST API"] == ["Local API"]


def _github_project(
    *,
    language: str = "C#",
    topics: list[str] | None = None,
    description: str = "REST API with SQL persistence.",
) -> dict:
    return {
        "name": "Student API",
        "description": description,
        "technologies": [language, *(topics or [])],
        "url": "https://github.com/example/student-api",
        "source": "github",
        "github": {
            "name": "student-api",
            "html_url": "https://github.com/example/student-api",
            "language": language,
            "topics": topics or ["dotnet"],
            "stars": 5,
            "forks": 1,
            "updated_at": "2026-01-02T00:00:00Z",
            "pushed_at": "2026-01-03T00:00:00Z",
            "fork": False,
            "archived": False,
        },
    }
