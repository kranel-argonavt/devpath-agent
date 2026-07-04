"""Deterministic full ADK-style career strategy workflow orchestration."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass, field
from typing import Any, Callable

from devpath.core.github_evidence import extract_github_evidence_for_projects
from devpath.core.privacy import mask_personal_data
from devpath.core.scoring import collect_project_evidence, extract_job_requirements
from devpath.tool_router import DIRECT_BACKEND, build_report_with_backend


AGENT_STAGE_NAMES = [
    "privacy_guard",
    "job_analyzer",
    "portfolio_evidence",
    "profile_matcher",
    "gap_planner",
    "application_writer",
    "interview_coach",
]


@dataclass
class AgentTraceStep:
    """One deterministic stage in the ADK-style workflow trace."""

    agent_name: str
    status: str
    summary: str
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    tools_used: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class FullAgentWorkflowInput:
    """Input payload for the full deterministic agent workflow."""

    job_text: str
    profile: dict[str, Any]
    projects: list[dict[str, Any]]
    target_role: str = "Junior Software Developer"
    cv_text: str = ""
    output_style: str = "Concise"
    tool_backend: str = DIRECT_BACKEND
    analysis_mode: str = "Mock deterministic mode"


@dataclass
class FullAgentWorkflowResult:
    """Output payload from the full deterministic agent workflow."""

    report: dict[str, Any]
    agent_trace: list[AgentTraceStep]
    warnings: list[str] = field(default_factory=list)


def run_full_agent_workflow(
    workflow_input: FullAgentWorkflowInput,
    *,
    summary_generator: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
) -> FullAgentWorkflowResult:
    """Run all deterministic ADK-style agent stages and return a report."""

    state: dict[str, Any] = {
        "job_text": workflow_input.job_text,
        "cv_text": workflow_input.cv_text,
        "profile": _profile_with_target_role(workflow_input.profile, workflow_input.target_role),
        "projects": deepcopy(workflow_input.projects),
        "tool_backend": workflow_input.tool_backend,
        "analysis_mode": workflow_input.analysis_mode,
        "output_style": workflow_input.output_style,
        "warnings": [],
    }
    trace = [
        run_privacy_guard_stage(state),
        run_job_analyzer_stage(state),
        run_portfolio_evidence_stage(state),
        run_profile_matcher_stage(state),
        run_gap_planner_stage(state),
        run_application_writer_stage(state),
        run_interview_coach_stage(state),
    ]

    report = deepcopy(state["report"])
    report["agent_workflow"] = {
        "enabled": True,
        "orchestration": "Full ADK-style deterministic agent workflow",
        "agents": AGENT_STAGE_NAMES,
        "scoring_source": "deterministic",
        "llm_score_modification": False,
    }
    report["agent_trace"] = [asdict(step) for step in trace]

    if summary_generator is not None:
        insights = summary_generator(deepcopy(report))
        report["gemini_insights"] = insights
        report["gemini_summary"] = str(insights.get("career_summary", "")) if isinstance(insights, dict) else ""

    return FullAgentWorkflowResult(report=report, agent_trace=trace, warnings=list(state["warnings"]))


def run_privacy_guard_stage(state: dict[str, Any]) -> AgentTraceStep:
    """Mask sensitive data before downstream deterministic stages."""

    state["masked_job_text"] = mask_personal_data(state["job_text"])
    state["masked_cv_text"] = mask_personal_data(state["cv_text"])
    warnings = []
    if state["masked_job_text"] != state["job_text"] or state["masked_cv_text"] != state["cv_text"]:
        warnings.append("Potential personal data or secret-like text was masked before analysis.")
        state["warnings"].extend(warnings)
    return AgentTraceStep(
        agent_name="privacy_guard",
        status="completed",
        summary="Applied deterministic privacy masking to job and CV context.",
        inputs=["job_text", "cv_text"],
        outputs=["masked_job_text", "masked_cv_text"],
        tools_used=["mask_personal_data"],
        warnings=warnings,
    )


def run_job_analyzer_stage(state: dict[str, Any]) -> AgentTraceStep:
    """Extract deterministic job requirements."""

    requirements = extract_job_requirements(state["masked_job_text"])
    state["job_requirements"] = requirements
    return AgentTraceStep(
        agent_name="job_analyzer",
        status="completed",
        summary=f"Detected {len(requirements.get('required_skills', []))} required skills.",
        inputs=["masked_job_text"],
        outputs=["job_requirements"],
        tools_used=["analyze_job_posting"],
    )


def run_portfolio_evidence_stage(state: dict[str, Any]) -> AgentTraceStep:
    """Collect deterministic project and GitHub portfolio evidence."""

    project_evidence = collect_project_evidence(state["projects"])
    github_evidence = extract_github_evidence_for_projects(state["projects"])
    state["project_evidence"] = project_evidence
    state["github_evidence"] = github_evidence
    return AgentTraceStep(
        agent_name="portfolio_evidence",
        status="completed",
        summary=(
            f"Collected {len(project_evidence)} skill evidence areas and "
            f"{len(github_evidence)} GitHub repository evidence records."
        ),
        inputs=["projects"],
        outputs=["project_evidence", "github_evidence"],
        tools_used=["collect_project_evidence", "extract_github_evidence_for_projects"],
    )


def run_profile_matcher_stage(state: dict[str, Any]) -> AgentTraceStep:
    """Build the deterministic report and score."""

    try:
        report = build_report_with_backend(
            job_text=state["masked_job_text"],
            profile=state["profile"],
            projects=state["projects"],
            cv_text=state["masked_cv_text"],
            output_style=state["output_style"],
            tool_backend=state["tool_backend"],
        )
    except RuntimeError:
        state["warnings"].append("Selected tool backend failed. Full agent workflow used direct deterministic services.")
        report = build_report_with_backend(
            job_text=state["masked_job_text"],
            profile=state["profile"],
            projects=state["projects"],
            cv_text=state["masked_cv_text"],
            output_style=state["output_style"],
            tool_backend=DIRECT_BACKEND,
        )
    state["report"] = report
    score = report.get("profile_match", {}).get("overall_score", 0)
    return AgentTraceStep(
        agent_name="profile_matcher",
        status="completed",
        summary=f"Calculated deterministic match score: {score}/100.",
        inputs=["job_requirements", "profile", "project_evidence"],
        outputs=["report", "profile_match"],
        tools_used=["calculate_match_score", "create_mock_report"],
    )


def run_gap_planner_stage(state: dict[str, Any]) -> AgentTraceStep:
    """Summarize deterministic skill gaps from the report."""

    gaps = state["report"].get("skill_gaps", {}).get("prioritized_gaps", [])
    return AgentTraceStep(
        agent_name="gap_planner",
        status="completed",
        summary=f"Reviewed {len(gaps)} prioritized gaps from deterministic scoring.",
        inputs=["report.skill_gaps"],
        outputs=["prioritized_gaps"],
        tools_used=["read_deterministic_report"],
    )


def run_application_writer_stage(state: dict[str, Any]) -> AgentTraceStep:
    """Summarize application draft generation from the report."""

    drafts = state["report"].get("application_drafts", {})
    generated = [key for key, value in drafts.items() if value]
    return AgentTraceStep(
        agent_name="application_writer",
        status="completed",
        summary=f"Prepared {len(generated)} deterministic application draft sections.",
        inputs=["report.application_drafts"],
        outputs=generated,
        tools_used=["read_deterministic_report"],
    )


def run_interview_coach_stage(state: dict[str, Any]) -> AgentTraceStep:
    """Summarize interview preparation from the report."""

    questions = state["report"].get("interview_prep", {}).get("questions", [])
    return AgentTraceStep(
        agent_name="interview_coach",
        status="completed",
        summary=f"Prepared {len(questions)} deterministic interview questions.",
        inputs=["report.interview_prep"],
        outputs=["questions", "practice_focus"],
        tools_used=["read_deterministic_report"],
    )


def _profile_with_target_role(profile: dict[str, Any], target_role: str) -> dict[str, Any]:
    profile_copy = deepcopy(profile)
    if target_role:
        profile_copy["target_roles"] = [target_role]
    return profile_copy
