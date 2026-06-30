"""Tests for deterministic mock scoring helpers."""

from devpath.core.scoring import calculate_mock_match_score


def test_calculate_mock_match_score_returns_explainable_result() -> None:
    job_text = """
    Junior .NET Developer
    Requirements: C#, .NET, ASP.NET Core, SQL, Git, REST API, English.
    """
    profile = {
        "experience_level": "Junior",
        "skills": ["C#", ".NET", "WPF", "SQLite", "Git"],
        "languages": ["English B1-B2"],
        "education": "Software Engineering",
        "location_preference": "Germany / Remote EU",
    }
    projects = [
        {
            "name": "TaskFlow Desktop",
            "summary": "Desktop project with local SQLite persistence.",
            "technologies": ["C#", ".NET", "WPF", "SQLite", "Git"],
        }
    ]

    result = calculate_mock_match_score(job_text, profile, projects)

    assert "overall_score" in result
    assert 0 <= result["overall_score"] <= 100
    assert "C#" in result["strong_matches"] or ".NET" in result["strong_matches"]
    assert "ASP.NET Core" in result["missing_skills"]


def test_calculate_mock_match_score_uses_project_evidence() -> None:
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

    assert result["overall_score"] > 50
    assert "REST API" in result["strong_matches"]
