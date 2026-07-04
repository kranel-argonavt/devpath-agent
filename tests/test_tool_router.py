"""Tests for local deterministic tool backend routing."""

from devpath.tool_router import (
    ADK_MCP_RUNTIME_BACKEND,
    DIRECT_BACKEND,
    MCP_STYLE_BACKEND,
    build_report_with_backend,
    list_tool_backends,
    normalize_tool_backend,
)


def test_list_tool_backends_contains_direct_and_mcp_style() -> None:
    assert DIRECT_BACKEND in list_tool_backends()
    assert MCP_STYLE_BACKEND in list_tool_backends()
    assert ADK_MCP_RUNTIME_BACKEND in list_tool_backends()


def test_normalize_tool_backend_defaults_to_direct() -> None:
    assert normalize_tool_backend(None) == DIRECT_BACKEND
    assert normalize_tool_backend("Unknown backend") == DIRECT_BACKEND
    assert normalize_tool_backend(ADK_MCP_RUNTIME_BACKEND) == ADK_MCP_RUNTIME_BACKEND


def test_build_report_with_direct_backend_returns_profile_match_data() -> None:
    report = build_report_with_backend(
        _job_text(),
        _profile(),
        _projects(),
        tool_backend=DIRECT_BACKEND,
    )

    assert "profile_match" in report
    assert "overall_score" in report["profile_match"]
    assert report["runtime_route"] == {
        "tool_backend": DIRECT_BACKEND,
        "mcp_runtime_used": False,
    }


def test_build_report_with_mcp_style_backend_returns_profile_match_data() -> None:
    report = build_report_with_backend(
        _job_text(),
        _profile(),
        _projects(),
        tool_backend=MCP_STYLE_BACKEND,
    )

    assert "profile_match" in report
    assert "overall_score" in report["profile_match"]
    assert report["runtime_route"] == {
        "tool_backend": MCP_STYLE_BACKEND,
        "mcp_runtime_used": False,
    }


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


def test_build_report_with_experimental_adk_mcp_backend_uses_wrappers(monkeypatch) -> None:
    direct_report = build_report_with_backend(
        _job_text(),
        _profile(),
        _projects(),
        tool_backend=DIRECT_BACKEND,
    )
    calls = []

    def fake_analyze(job_text):
        calls.append(("analyze", job_text))
        return {"required_skills": ["C#", ".NET"]}

    def fake_score(job_text, profile, projects):
        calls.append(("score", job_text))
        return direct_report["profile_match"]

    monkeypatch.setattr("devpath.adk_mcp_tools.analyze_job_posting_via_mcp_tool", fake_analyze)
    monkeypatch.setattr("devpath.adk_mcp_tools.calculate_match_score_via_mcp_tool", fake_score)

    report = build_report_with_backend(
        _job_text(),
        _profile(),
        _projects(),
        tool_backend=ADK_MCP_RUNTIME_BACKEND,
    )

    assert "profile_match" in report
    assert report["profile_match"]["overall_score"] == direct_report["profile_match"]["overall_score"]
    assert report["runtime_route"]["tool_backend"] == ADK_MCP_RUNTIME_BACKEND
    assert report["runtime_route"]["mcp_runtime_used"] is True
    assert report["runtime_route"]["selected_tools"] == ["analyze_job_posting", "calculate_match_score"]
    assert report["runtime_route"]["score_consistent"] is True
    assert calls == [("analyze", _job_text()), ("score", _job_text())]


def test_experimental_adk_mcp_backend_raises_for_wrapper_failure(monkeypatch) -> None:
    def fake_analyze(job_text):
        raise RuntimeError("runtime failed")

    monkeypatch.setattr("devpath.adk_mcp_tools.analyze_job_posting_via_mcp_tool", fake_analyze)

    try:
        build_report_with_backend(
            _job_text(),
            _profile(),
            _projects(),
            tool_backend=ADK_MCP_RUNTIME_BACKEND,
        )
    except RuntimeError as exc:
        assert "Experimental ADK-MCP runtime tools could not build" in str(exc)
    else:
        raise AssertionError("Expected RuntimeError for experimental backend wrapper failure.")


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
