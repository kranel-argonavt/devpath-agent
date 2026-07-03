"""Tests for deterministic agent tool wrappers."""

from devpath.agent_tools import (
    analyze_job_posting_tool,
    build_mock_report_tool,
    calculate_match_score_tool,
    mask_personal_data_tool,
    summarize_portfolio_tool,
)


def test_calculate_match_score_tool_returns_overall_score() -> None:
    result = calculate_match_score_tool(_job_text(), _profile(), _projects())

    assert "overall_score" in result
    assert 0 <= result["overall_score"] <= 100


def test_build_mock_report_tool_returns_report_sections() -> None:
    report = build_mock_report_tool(_job_text(), _profile(), _projects())

    assert "job_analysis" in report
    assert "profile_match" in report
    assert "portfolio_evidence" in report
    assert "privacy_notice" in report


def test_mask_personal_data_tool_masks_email_and_api_key() -> None:
    masked = mask_personal_data_tool("Email test@example.com and GOOGLE_API_KEY=abc123")

    assert "[EMAIL_REDACTED]" in masked
    assert "GOOGLE_API_KEY=[REDACTED]" in masked
    assert "test@example.com" not in masked
    assert "abc123" not in masked


def test_analyze_job_posting_tool_returns_required_skill_data() -> None:
    result = analyze_job_posting_tool(_job_text())

    assert "required_skills" in result
    assert "C#" in result["required_skills"]
    assert ".NET" in result["required_skills"]


def test_summarize_portfolio_tool_returns_evidence_map() -> None:
    result = summarize_portfolio_tool(_projects())

    assert result["project_count"] == 1
    assert "TaskFlow Desktop" in result["project_names"]
    assert "C#" in result["evidence_by_skill"]


def _job_text() -> str:
    return """
    Junior .NET Developer
    Requirements: C#, .NET, ASP.NET Core, SQL, Git, REST API, English.
    Nice to have: Docker and Azure.
    """


def _profile() -> dict:
    return {
        "experience_level": "Junior",
        "skills": ["C#", ".NET", "Git", "SQLite"],
        "education": "Software Engineering",
        "languages": ["English B1-B2"],
        "location_preference": "Germany / Remote EU",
        "target_roles": ["Junior .NET Developer"],
    }


def _projects() -> list[dict]:
    return [
        {
            "name": "TaskFlow Desktop",
            "technologies": ["C#", ".NET", "WPF", "SQLite", "Git"],
            "description": "Desktop task manager with local database storage.",
        }
    ]
