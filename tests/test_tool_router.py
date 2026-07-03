"""Tests for local deterministic tool backend routing."""

from devpath.tool_router import (
    DIRECT_BACKEND,
    MCP_STYLE_BACKEND,
    build_report_with_backend,
    list_tool_backends,
    normalize_tool_backend,
)


def test_list_tool_backends_contains_direct_and_mcp_style() -> None:
    assert DIRECT_BACKEND in list_tool_backends()
    assert MCP_STYLE_BACKEND in list_tool_backends()


def test_normalize_tool_backend_defaults_to_direct() -> None:
    assert normalize_tool_backend(None) == DIRECT_BACKEND
    assert normalize_tool_backend("Unknown backend") == DIRECT_BACKEND


def test_build_report_with_direct_backend_returns_profile_match_data() -> None:
    report = build_report_with_backend(
        _job_text(),
        _profile(),
        _projects(),
        tool_backend=DIRECT_BACKEND,
    )

    assert "profile_match" in report
    assert "overall_score" in report["profile_match"]


def test_build_report_with_mcp_style_backend_returns_profile_match_data() -> None:
    report = build_report_with_backend(
        _job_text(),
        _profile(),
        _projects(),
        tool_backend=MCP_STYLE_BACKEND,
    )

    assert "profile_match" in report
    assert "overall_score" in report["profile_match"]


def test_direct_and_mcp_style_backends_preserve_same_overall_score() -> None:
    direct_report = build_report_with_backend(
        _job_text(),
        _profile(),
        _projects(),
        tool_backend=DIRECT_BACKEND,
    )
    mcp_report = build_report_with_backend(
        _job_text(),
        _profile(),
        _projects(),
        tool_backend=MCP_STYLE_BACKEND,
    )

    assert mcp_report["profile_match"]["overall_score"] == direct_report["profile_match"]["overall_score"]


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
