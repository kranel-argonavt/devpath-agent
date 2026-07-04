"""Workflow facade for career strategy generation.

This module gives Streamlit a single orchestration entry point while keeping
deterministic scoring as the source of truth. Full ADK runtime routing is
planned for a later step.
"""

from collections.abc import Callable
from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from devpath.core.config import AppConfig, get_app_config
from devpath.services.gemini_service import generate_gemini_career_insights
from devpath.tool_router import (
    ADK_MCP_RUNTIME_BACKEND,
    DIRECT_BACKEND,
    MCP_STYLE_BACKEND,
    build_report_with_backend,
)


MOCK_MODE = "Mock deterministic mode"
GEMINI_MODE = "Gemini-assisted summary"

DETERMINISTIC_PROFILE_MATCH_FIELDS = [
    "overall_score",
    "category_scores",
    "category_details",
    "strong_matches",
    "partial_matches",
    "missing_skills",
    "evidence_by_skill",
    "prioritized_gaps",
]


@dataclass(frozen=True)
class WorkflowInput:
    """Input payload for the career strategy workflow facade."""

    job_text: str
    profile: dict[str, Any]
    projects: list[dict[str, Any]]
    cv_text: str = ""
    target_role: str = "Junior Software Developer"
    output_style: str = "Concise"
    analysis_mode: str = MOCK_MODE
    tool_backend: str = DIRECT_BACKEND


@dataclass(frozen=True)
class WorkflowResult:
    """Result payload returned by the career strategy workflow facade."""

    report: dict[str, Any]
    mode_used: str
    warnings: list[str]


def run_career_strategy_workflow(
    workflow_input: WorkflowInput,
    *,
    config: AppConfig | None = None,
    gemini_generator: Callable[[dict[str, Any], str, str], dict[str, Any]] | None = None,
) -> WorkflowResult:
    """Run deterministic career strategy generation with optional Gemini insights."""

    warnings: list[str] = []
    profile = _profile_with_target_role(workflow_input.profile, workflow_input.target_role)
    try:
        deterministic_report = build_report_with_backend(
            job_text=workflow_input.job_text,
            profile=profile,
            projects=workflow_input.projects,
            cv_text=workflow_input.cv_text,
            output_style=workflow_input.output_style,
            tool_backend=workflow_input.tool_backend,
        )
    except RuntimeError:
        if workflow_input.tool_backend == MCP_STYLE_BACKEND:
            warnings.append("Local MCP-style tools could not be used. Falling back to direct deterministic services.")
            deterministic_report = build_report_with_backend(
                job_text=workflow_input.job_text,
                profile=profile,
                projects=workflow_input.projects,
                cv_text=workflow_input.cv_text,
                output_style=workflow_input.output_style,
                tool_backend=DIRECT_BACKEND,
            )
            _mark_backend_fallback(
                deterministic_report,
                requested_backend=MCP_STYLE_BACKEND,
                notes=[
                    "Local MCP-style tools could not be used.",
                    "Fell back to direct deterministic services.",
                ],
                experimental=False,
            )
        elif workflow_input.tool_backend == ADK_MCP_RUNTIME_BACKEND:
            warnings.append(
                "Experimental ADK-MCP runtime tools could not be used. Falling back to direct deterministic services."
            )
            deterministic_report = build_report_with_backend(
                job_text=workflow_input.job_text,
                profile=profile,
                projects=workflow_input.projects,
                cv_text=workflow_input.cv_text,
                output_style=workflow_input.output_style,
                tool_backend=DIRECT_BACKEND,
            )
            _mark_backend_fallback(
                deterministic_report,
                requested_backend=ADK_MCP_RUNTIME_BACKEND,
                notes=[
                    "Experimental ADK-MCP runtime tools could not be used.",
                    "Fell back to direct deterministic services.",
                ],
                experimental=True,
            )
        else:
            raise
    report = deepcopy(deterministic_report)
    deterministic_fields = _deterministic_profile_match_snapshot(report)

    if workflow_input.analysis_mode == MOCK_MODE:
        return WorkflowResult(report=report, mode_used=MOCK_MODE, warnings=warnings)

    if workflow_input.analysis_mode != GEMINI_MODE:
        warnings.append("Unknown analysis mode. The app continued in deterministic mode.")
        return WorkflowResult(report=report, mode_used=MOCK_MODE, warnings=warnings)

    app_config = config or get_app_config()
    if not app_config.gemini_enabled or not app_config.google_api_key:
        warnings.append("Gemini API key is not configured. The app continued in deterministic mode.")
        return WorkflowResult(report=report, mode_used=MOCK_MODE, warnings=warnings)

    generator = gemini_generator or generate_gemini_career_insights
    try:
        insights = generator(
            deepcopy(report),
            app_config.google_api_key,
            app_config.gemini_model,
        )
    except Exception:
        warnings.append("Gemini-assisted insights could not be generated. Continuing with deterministic report.")
        return WorkflowResult(report=report, mode_used=MOCK_MODE, warnings=warnings)

    report["gemini_insights"] = insights
    report["gemini_summary"] = str(insights.get("career_summary", "")) if isinstance(insights, dict) else ""
    _restore_deterministic_profile_match_fields(report, deterministic_fields)
    return WorkflowResult(report=report, mode_used=GEMINI_MODE, warnings=warnings)


def run_career_strategy_agent_workflow(
    workflow_input: WorkflowInput,
) -> WorkflowResult:
    """Run the deterministic full ADK-style agent workflow as an opt-in path."""

    from devpath.full_agent_workflow import FullAgentWorkflowInput, run_full_agent_workflow

    result = run_full_agent_workflow(
        FullAgentWorkflowInput(
            job_text=workflow_input.job_text,
            profile=workflow_input.profile,
            projects=workflow_input.projects,
            target_role=workflow_input.target_role,
            cv_text=workflow_input.cv_text,
            tool_backend=workflow_input.tool_backend,
            analysis_mode=workflow_input.analysis_mode,
        )
    )
    return WorkflowResult(report=result.report, mode_used=MOCK_MODE, warnings=result.warnings)


def _profile_with_target_role(profile: dict[str, Any], target_role: str) -> dict[str, Any]:
    profile_copy = deepcopy(profile)
    if target_role:
        profile_copy["target_roles"] = [target_role]
    return profile_copy


def _deterministic_profile_match_snapshot(report: dict[str, Any]) -> dict[str, Any]:
    profile_match = report.get("profile_match", {})
    return {field: deepcopy(profile_match.get(field)) for field in DETERMINISTIC_PROFILE_MATCH_FIELDS}


def _restore_deterministic_profile_match_fields(report: dict[str, Any], snapshot: dict[str, Any]) -> None:
    profile_match = report.setdefault("profile_match", {})
    for field, value in snapshot.items():
        profile_match[field] = deepcopy(value)


def _mark_backend_fallback(
    report: dict[str, Any],
    *,
    requested_backend: str,
    notes: list[str],
    experimental: bool,
) -> None:
    report["runtime_route"] = {
        "tool_backend": DIRECT_BACKEND,
        "requested_tool_backend": requested_backend,
        "mcp_runtime_used": False,
        "experimental": experimental,
        "fallback_used": True,
        "selected_tools": [],
        "notes": notes,
    }
