"""Tests for the career strategy workflow facade."""

from devpath.agent_workflow import (
    GEMINI_MODE,
    MOCK_MODE,
    DETERMINISTIC_PROFILE_MATCH_FIELDS,
    WorkflowInput,
    run_career_strategy_workflow,
)
from devpath.core.config import AppConfig
from devpath.tool_router import DIRECT_BACKEND, MCP_STYLE_BACKEND, build_report_with_backend


def test_workflow_mock_mode_returns_deterministic_report_without_gemini() -> None:
    result = run_career_strategy_workflow(_workflow_input(analysis_mode=MOCK_MODE))

    assert result.mode_used == MOCK_MODE
    assert result.warnings == []
    assert "overall_score" in result.report["profile_match"]
    assert "gemini_insights" not in result.report


def test_workflow_uses_direct_backend_by_default() -> None:
    workflow_input = _workflow_input(analysis_mode=MOCK_MODE)

    assert workflow_input.tool_backend == DIRECT_BACKEND


def test_workflow_can_use_mcp_style_backend() -> None:
    direct_result = run_career_strategy_workflow(_workflow_input(analysis_mode=MOCK_MODE))
    mcp_result = run_career_strategy_workflow(
        _workflow_input(analysis_mode=MOCK_MODE, tool_backend=MCP_STYLE_BACKEND)
    )

    assert mcp_result.mode_used == MOCK_MODE
    assert mcp_result.warnings == []
    assert mcp_result.report["profile_match"]["overall_score"] == direct_result.report["profile_match"]["overall_score"]


def test_workflow_falls_back_if_mcp_style_backend_fails(monkeypatch) -> None:
    def fake_build_report_with_backend(**kwargs):
        if kwargs["tool_backend"] == MCP_STYLE_BACKEND:
            raise RuntimeError("MCP-style backend failed")
        return build_report_with_backend(**kwargs)

    monkeypatch.setattr(
        "devpath.agent_workflow.build_report_with_backend",
        fake_build_report_with_backend,
    )

    result = run_career_strategy_workflow(
        _workflow_input(analysis_mode=MOCK_MODE, tool_backend=MCP_STYLE_BACKEND)
    )

    assert result.mode_used == MOCK_MODE
    assert "overall_score" in result.report["profile_match"]
    assert result.warnings == [
        "Local MCP-style tools could not be used. Falling back to direct deterministic services."
    ]


def test_workflow_gemini_mode_without_api_key_falls_back_without_calling_gemini() -> None:
    def fail_if_called(report, api_key, model):
        raise AssertionError("Gemini generator should not be called without an API key.")

    result = run_career_strategy_workflow(
        _workflow_input(analysis_mode=GEMINI_MODE),
        config=AppConfig(google_api_key=None, gemini_model="gemini-2.5-flash", gemini_enabled=False),
        gemini_generator=fail_if_called,
    )

    assert result.mode_used == MOCK_MODE
    assert "overall_score" in result.report["profile_match"]
    assert "gemini_insights" not in result.report
    assert result.warnings == ["Gemini API key is not configured. The app continued in deterministic mode."]


def test_workflow_gemini_mode_with_fake_key_attaches_fake_insights() -> None:
    calls = []

    def fake_generator(report, api_key, model):
        calls.append((api_key, model, report["profile_match"]["overall_score"]))
        return {
            "career_summary": "Fake structured summary",
            "top_actions": ["Action one", "Action two", "Action three"],
            "portfolio_positioning": [],
            "skill_gap_strategy": [],
            "interview_focus": [],
            "raw_response": "{}",
        }

    result = run_career_strategy_workflow(
        _workflow_input(analysis_mode=GEMINI_MODE),
        config=AppConfig(google_api_key="fake-key", gemini_model="gemini-2.5-flash", gemini_enabled=True),
        gemini_generator=fake_generator,
    )

    assert result.mode_used == GEMINI_MODE
    assert calls == [("fake-key", "gemini-2.5-flash", result.report["profile_match"]["overall_score"])]
    assert result.report["gemini_insights"]["career_summary"] == "Fake structured summary"
    assert result.warnings == []
    assert "fake-key" not in str(result.report)
    assert "fake-key" not in str(result.warnings)


def test_workflow_gemini_generator_failure_returns_deterministic_report_with_warning() -> None:
    def failing_generator(report, api_key, model):
        raise RuntimeError("Simulated Gemini failure")

    result = run_career_strategy_workflow(
        _workflow_input(analysis_mode=GEMINI_MODE),
        config=AppConfig(google_api_key="fake-key", gemini_model="gemini-2.5-flash", gemini_enabled=True),
        gemini_generator=failing_generator,
    )

    assert result.mode_used == MOCK_MODE
    assert "overall_score" in result.report["profile_match"]
    assert "gemini_insights" not in result.report
    assert result.warnings == [
        "Gemini-assisted insights could not be generated. Continuing with deterministic report."
    ]


def test_workflow_preserves_deterministic_score_fields_when_gemini_runs() -> None:
    mock_result = run_career_strategy_workflow(_workflow_input(analysis_mode=MOCK_MODE))

    def mutating_generator(report, api_key, model):
        report["profile_match"]["overall_score"] = 1
        report["profile_match"]["missing_skills"] = ["Invented Skill"]
        return {
            "career_summary": "Narrative only",
            "top_actions": [],
            "portfolio_positioning": [],
            "skill_gap_strategy": [],
            "interview_focus": [],
            "raw_response": "{}",
        }

    gemini_result = run_career_strategy_workflow(
        _workflow_input(analysis_mode=GEMINI_MODE),
        config=AppConfig(google_api_key="fake-key", gemini_model="gemini-2.5-flash", gemini_enabled=True),
        gemini_generator=mutating_generator,
    )

    for field in DETERMINISTIC_PROFILE_MATCH_FIELDS:
        assert gemini_result.report["profile_match"][field] == mock_result.report["profile_match"][field]


def test_workflow_gemini_fake_generator_works_with_mcp_style_backend() -> None:
    def fake_generator(report, api_key, model):
        return {
            "career_summary": "Fake MCP-backed Gemini summary",
            "top_actions": [],
            "portfolio_positioning": [],
            "skill_gap_strategy": [],
            "interview_focus": [],
            "raw_response": "{}",
        }

    result = run_career_strategy_workflow(
        _workflow_input(analysis_mode=GEMINI_MODE, tool_backend=MCP_STYLE_BACKEND),
        config=AppConfig(google_api_key="fake-key", gemini_model="gemini-2.5-flash", gemini_enabled=True),
        gemini_generator=fake_generator,
    )

    assert result.mode_used == GEMINI_MODE
    assert result.report["gemini_insights"]["career_summary"] == "Fake MCP-backed Gemini summary"
    assert result.warnings == []


def _workflow_input(analysis_mode: str, tool_backend: str = DIRECT_BACKEND) -> WorkflowInput:
    return WorkflowInput(
        job_text=(
            "Junior .NET Developer role requiring C#, .NET, ASP.NET Core, SQL, Git, "
            "REST API, and English."
        ),
        profile={
            "experience_level": "Junior",
            "skills": ["C#", ".NET", "Git", "SQLite"],
            "education": "Software Engineering",
            "languages": ["English B1-B2"],
            "location_preference": "Germany / Remote EU",
        },
        projects=[
            {
                "name": "TaskFlow Desktop",
                "technologies": ["C#", ".NET", "WPF", "SQLite", "Git"],
                "description": "Desktop task manager with local database storage.",
            }
        ],
        target_role="Junior .NET Developer",
        output_style="Concise",
        analysis_mode=analysis_mode,
        tool_backend=tool_backend,
    )
