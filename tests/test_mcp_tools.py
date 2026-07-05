"""Tests for MCP-style deterministic tool contracts."""

from pathlib import Path

from mcp_server.tools import MCP_TOOL_REGISTRY, list_mcp_tools
from mcp_server.tools.export_tools import export_markdown_report
from mcp_server.tools.github_tools import fetch_github_repositories, fetch_repository_readme
from mcp_server.tools.portfolio_tools import summarize_portfolio
from mcp_server.tools.privacy_tools import detect_sensitive_data, mask_personal_data
from mcp_server.tools.profile_tools import read_profile
from mcp_server.tools.project_tools import read_local_projects
from mcp_server.tools.report_tools import build_career_report
from mcp_server.tools.scoring_tools import analyze_job_posting, calculate_match_score


EXPECTED_TOOL_NAMES = {
    "analyze_job_posting",
    "read_profile",
    "read_local_projects",
    "fetch_github_repositories",
    "fetch_repository_readme",
    "summarize_portfolio",
    "build_portfolio_summary",
    "calculate_match_score",
    "build_career_report",
    "detect_sensitive_data",
    "mask_personal_data",
    "export_markdown_report",
}


def test_list_mcp_tools_contains_expected_names() -> None:
    assert EXPECTED_TOOL_NAMES.issubset(set(list_mcp_tools()))
    assert EXPECTED_TOOL_NAMES.issubset(set(MCP_TOOL_REGISTRY))


def test_analyze_job_posting_returns_requirement_data() -> None:
    result = analyze_job_posting(_job_text())

    assert "required_skills" in result
    assert "C#" in result["required_skills"]
    assert ".NET" in result["required_skills"]


def test_calculate_match_score_returns_overall_score() -> None:
    result = calculate_match_score(_job_text(), _profile(), _projects())

    assert "overall_score" in result
    assert 0 <= result["overall_score"] <= 100


def test_summarize_portfolio_returns_project_evidence_summary() -> None:
    result = summarize_portfolio(_projects())

    assert result["project_count"] == 1
    assert "TaskFlow Desktop" in result["project_names"]
    assert "C#" in result["evidence_by_skill"]


def test_read_profile_loads_local_profile_json(tmp_path: Path) -> None:
    profile_path = tmp_path / "profile.json"
    profile_path.write_text('{"experience_level": "Junior", "skills": ["C#"]}', encoding="utf-8")

    result = read_profile(str(profile_path))

    assert result["experience_level"] == "Junior"
    assert result["skills"] == ["C#"]


def test_read_local_projects_loads_project_list_json(tmp_path: Path) -> None:
    projects_path = tmp_path / "projects.json"
    projects_path.write_text('[{"name": "TaskFlow Desktop"}]', encoding="utf-8")

    result = read_local_projects(str(projects_path))

    assert result == [{"name": "TaskFlow Desktop"}]


def test_fetch_github_repositories_tool_is_callable(monkeypatch) -> None:
    def fake_fetch(username, max_repos=10):
        return [{"name": username, "max_repos": max_repos}]

    monkeypatch.setattr("mcp_server.tools.github_tools.fetch_public_github_repositories", fake_fetch)

    assert fetch_github_repositories("octocat", max_repos=3) == [{"name": "octocat", "max_repos": 3}]


def test_fetch_repository_readme_tool_is_callable(monkeypatch) -> None:
    def fake_fetch(owner, repo, max_chars=12000):
        return {"owner": owner, "repo": repo, "max_chars": max_chars}

    monkeypatch.setattr("mcp_server.tools.github_tools.fetch_public_repository_readme", fake_fetch)

    assert fetch_repository_readme("octocat", "taskflow", max_chars=100) == {
        "owner": "octocat",
        "repo": "taskflow",
        "max_chars": 100,
    }


def test_build_career_report_returns_profile_match_data() -> None:
    report = build_career_report(_job_text(), _profile(), _projects())

    assert "profile_match" in report
    assert "overall_score" in report["profile_match"]


def test_mask_personal_data_masks_email_and_api_key() -> None:
    masked = mask_personal_data("Email test@example.com and GOOGLE_API_KEY=abc123")

    assert "[EMAIL_REDACTED]" in masked
    assert "GOOGLE_API_KEY=[REDACTED]" in masked
    assert "test@example.com" not in masked
    assert "abc123" not in masked


def test_detect_sensitive_data_reports_only_detected_types() -> None:
    result = detect_sensitive_data("Email test@example.com and GITHUB_TOKEN=abc123")

    assert result["has_sensitive_data"] is True
    assert result["detected_types"] == ["email", "api_key"]


def test_export_markdown_report_writes_to_tmp_path(tmp_path: Path) -> None:
    report = build_career_report(_job_text(), _profile(), _projects())

    result = export_markdown_report(report, output_dir=tmp_path, filename="mcp_report")
    output_path = Path(result)

    assert output_path.parent == tmp_path
    assert output_path.exists()
    assert output_path.suffix == ".md"
    assert "# DevPath Agent Career Strategy Report" in output_path.read_text(encoding="utf-8")


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
