"""Tests for the deterministic full ADK-style agent workflow."""

from devpath.agent_workflow import MOCK_MODE, WorkflowInput, run_career_strategy_agent_workflow, run_career_strategy_workflow
from devpath.full_agent_workflow import (
    AGENT_STAGE_NAMES,
    FullAgentWorkflowInput,
    run_full_agent_workflow,
)
from scripts.check_full_agent_workflow import main as full_agent_workflow_smoke_main


def test_run_full_agent_workflow_returns_report_with_score() -> None:
    result = run_full_agent_workflow(_workflow_input())

    assert "overall_score" in result.report["profile_match"]
    assert 0 <= result.report["profile_match"]["overall_score"] <= 100


def test_report_contains_agent_workflow_metadata_and_trace() -> None:
    result = run_full_agent_workflow(_workflow_input())

    assert result.report["agent_workflow"]["enabled"] is True
    assert result.report["agent_workflow"]["scoring_source"] == "deterministic"
    assert result.report["agent_workflow"]["llm_score_modification"] is False
    assert result.report["agent_workflow"]["agents"] == AGENT_STAGE_NAMES
    assert [step["agent_name"] for step in result.report["agent_trace"]] == AGENT_STAGE_NAMES


def test_trace_includes_all_expected_agents() -> None:
    result = run_full_agent_workflow(_workflow_input())

    assert [step.agent_name for step in result.agent_trace] == AGENT_STAGE_NAMES
    assert all(step.status == "completed" for step in result.agent_trace)


def test_profile_matcher_trace_uses_deterministic_scoring_tools() -> None:
    result = run_full_agent_workflow(_workflow_input())
    profile_matcher = next(step for step in result.agent_trace if step.agent_name == "profile_matcher")

    assert "calculate_match_score" in profile_matcher.tools_used
    assert "create_mock_report" in profile_matcher.tools_used


def test_github_style_project_metadata_is_included_in_portfolio_evidence() -> None:
    result = run_full_agent_workflow(_workflow_input(projects=[_github_project()]))

    github_evidence = result.report["portfolio_evidence"]["github_evidence"]
    assert github_evidence
    assert github_evidence[0]["project_name"] == "Student API"
    assert "REST API" in github_evidence[0]["matched_skills"]


def test_optional_fake_summary_generator_attaches_narrative_without_score_change() -> None:
    mock_result = run_full_agent_workflow(_workflow_input())

    def fake_summary(report):
        report["profile_match"]["overall_score"] = 1
        return {"career_summary": "Fake full workflow summary"}

    result = run_full_agent_workflow(_workflow_input(), summary_generator=fake_summary)

    assert result.report["gemini_insights"]["career_summary"] == "Fake full workflow summary"
    assert result.report["profile_match"]["overall_score"] == mock_result.report["profile_match"]["overall_score"]


def test_cv_context_is_masked_and_marked_as_report_context() -> None:
    result = run_full_agent_workflow(
        FullAgentWorkflowInput(
            job_text=_job_text(),
            profile=_profile(),
            projects=_projects(),
            cv_text="CV contact test@example.com and GOOGLE_API_KEY=abc123",
            target_role="Junior .NET Developer",
        )
    )

    privacy_guard = next(step for step in result.agent_trace if step.agent_name == "privacy_guard")

    assert result.report["job_analysis"]["cv_context_provided"] is True
    assert privacy_guard.warnings == ["Potential personal data or secret-like text was masked before analysis."]
    assert "overall_score" in result.report["profile_match"]


def test_existing_direct_workflow_still_works() -> None:
    result = run_career_strategy_workflow(
        WorkflowInput(
            job_text=_job_text(),
            profile=_profile(),
            projects=_projects(),
            analysis_mode=MOCK_MODE,
        )
    )

    assert "overall_score" in result.report["profile_match"]
    assert "agent_workflow" not in result.report


def test_agent_workflow_wrapper_returns_workflow_result_compatible_report() -> None:
    result = run_career_strategy_agent_workflow(
        WorkflowInput(
            job_text=_job_text(),
            profile=_profile(),
            projects=_projects(),
            analysis_mode=MOCK_MODE,
        )
    )

    assert result.mode_used == MOCK_MODE
    assert "overall_score" in result.report["profile_match"]
    assert result.report["agent_workflow"]["enabled"] is True


def test_full_agent_workflow_smoke_script_succeeds(capsys) -> None:
    result = full_agent_workflow_smoke_main()
    output = capsys.readouterr().out

    assert result == 0
    assert "DevPath full agent workflow smoke test" in output
    assert "Agent stage: privacy_guard OK" in output
    assert "Agent stage: interview_coach OK" in output
    assert "Full agent workflow smoke test succeeded" in output


def _workflow_input(projects=None) -> FullAgentWorkflowInput:
    return FullAgentWorkflowInput(
        job_text=_job_text(),
        profile=_profile(),
        projects=projects or _projects(),
        target_role="Junior .NET Developer",
    )


def _job_text() -> str:
    return "Junior .NET Developer role requiring C#, .NET, ASP.NET Core, SQL, Git, REST API, and English."


def _profile() -> dict:
    return {
        "experience_level": "Junior",
        "skills": ["C#", ".NET", "Git"],
        "languages": ["English B1-B2"],
        "education": "Software Engineering",
    }


def _projects() -> list[dict]:
    return [
        {
            "name": "TaskFlow Desktop",
            "technologies": ["C#", ".NET", "WPF", "SQLite", "Git"],
            "description": "Desktop app with local database storage.",
        }
    ]


def _github_project() -> dict:
    return {
        "name": "Student API",
        "description": "REST API with SQL persistence.",
        "url": "https://github.com/example/student-api",
        "source": "github",
        "github": {
            "language": "C#",
            "topics": ["dotnet", "api"],
            "stars": 4,
            "forks": 1,
            "updated_at": "2026-01-02T00:00:00Z",
            "pushed_at": "2026-01-03T00:00:00Z",
            "fork": False,
            "archived": False,
        },
    }
