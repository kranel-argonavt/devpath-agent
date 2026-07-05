"""Capstone-grade ADK/Gemini tool-calling workflow facade.

This module keeps deterministic scoring as the source of truth while making
agent/tool/MCP participation visible for the Streamlit runtime tab.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass, field
from typing import Any, Callable

from devpath.agent_tools import (
    analyze_job_posting_tool,
    build_mock_report_tool,
    calculate_match_score_tool,
    mask_personal_data_tool,
    summarize_portfolio_tool,
)
from devpath.core.config import AppConfig, get_app_config
from devpath.core.gemini_enhancements import (
    apply_narrative_enhancements,
    sanitize_action_plan,
    sanitize_application_drafts,
    sanitize_gap_narrative,
    sanitize_interview_prep,
    validate_candidate_context,
    validate_job_requirements,
)
from devpath.services.gemini_service import generate_gemini_agent_payload, generate_gemini_career_insights
from devpath.tool_router import DIRECT_BACKEND


TOOL_CALLING_WORKFLOW = "Gemini/ADK tool-calling agent"
MCP_RUNTIME_BACKEND = "MCP runtime"
MCP_STYLE_REGISTRY_BACKEND = "Local MCP-style registry"
DIRECT_FALLBACK_BACKEND = "Direct deterministic fallback"

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
class ToolCallingWorkflowInput:
    """Input payload for the ADK/Gemini tool-calling facade."""

    job_text: str
    profile: dict[str, Any]
    projects: list[dict[str, Any]]
    target_role: str = "Junior Software Developer"
    cv_text: str = ""
    output_style: str = "Concise"
    analysis_mode: str = "Gemini-assisted summary"


@dataclass
class ToolCallTraceStep:
    """One visible tool call in the capstone runtime trace."""

    agent_name: str
    tool_name: str
    backend_used: str
    status: str
    input_summary: str
    output_summary: str
    fallback_used: bool = False
    warnings: list[str] = field(default_factory=list)


@dataclass
class ToolCallingWorkflowResult:
    """Output payload from the ADK/Gemini tool-calling facade."""

    report: dict[str, Any]
    tool_call_trace: list[ToolCallTraceStep]
    warnings: list[str] = field(default_factory=list)
    mode_used: str = "Mock deterministic mode"


ToolRuntimeCaller = Callable[[str, dict[str, Any]], Any]
GeminiGenerator = Callable[[dict[str, Any], str, str], dict[str, Any]]
GeminiToolGenerator = Callable[[str, dict[str, Any], str, str], Any]


def run_adk_tool_calling_workflow(
    workflow_input: ToolCallingWorkflowInput,
    *,
    config: AppConfig | None = None,
    runtime_caller: ToolRuntimeCaller | None = None,
    gemini_generator: GeminiGenerator | None = None,
    gemini_tool_generator: GeminiToolGenerator | None = None,
) -> ToolCallingWorkflowResult:
    """Run the visible ADK/Gemini tool-calling workflow with safe fallbacks."""

    profile = _profile_with_target_role(workflow_input.profile, workflow_input.target_role)
    trace: list[ToolCallTraceStep] = []
    warnings: list[str] = []
    app_config = config or get_app_config()

    masked_job_text = _call_tool(
        tool_name="mask_personal_data",
        arguments={"text": workflow_input.job_text},
        direct_callable=mask_personal_data_tool,
        direct_args=(workflow_input.job_text,),
        agent_name="privacy_guard",
        input_summary="job_text",
        output_summarizer=lambda value: "Job posting privacy masking completed."
        if value == workflow_input.job_text
        else "Job posting contained sensitive or secret-like text and was masked.",
        trace=trace,
        runtime_caller=runtime_caller,
    )
    masked_cv_text = _call_tool(
        tool_name="mask_personal_data",
        arguments={"text": workflow_input.cv_text},
        direct_callable=mask_personal_data_tool,
        direct_args=(workflow_input.cv_text,),
        agent_name="privacy_guard",
        input_summary="cv_text",
        output_summarizer=lambda value: "CV context privacy masking completed."
        if value == workflow_input.cv_text
        else "CV context contained sensitive or secret-like text and was masked.",
        trace=trace,
        runtime_caller=runtime_caller,
    )
    if masked_job_text != workflow_input.job_text or masked_cv_text != workflow_input.cv_text:
        warnings.append("Potential personal data or secret-like text was masked before tool-calling analysis.")

    gemini_job_requirements = _call_gemini_agent_step(
        tool_name="extract_job_requirements_with_gemini",
        payload={
            "masked_job_text": masked_job_text,
            "target_role": workflow_input.target_role,
            "output_style": workflow_input.output_style,
        },
        agent_name="job_analyzer",
        input_summary="masked_job_text + target_role",
        output_summary="Gemini structured job extraction returned candidate requirements.",
        workflow_input=workflow_input,
        app_config=app_config,
        trace=trace,
        warnings=warnings,
        gemini_tool_generator=gemini_tool_generator,
    )

    job_requirements = _call_tool(
        tool_name="analyze_job_posting",
        arguments={"job_text": masked_job_text},
        direct_callable=analyze_job_posting_tool,
        direct_args=(masked_job_text,),
        agent_name="job_analyzer",
        input_summary="masked_job_text",
        output_summarizer=_summarize_job_requirements,
        trace=trace,
        runtime_caller=runtime_caller,
    )

    validated_job_context = _call_validator_step(
        tool_name="validate_job_requirements",
        agent_name="job_analyzer",
        input_summary="gemini_job_requirements + deterministic_job_requirements",
        validator=lambda: validate_job_requirements(
            gemini_job_requirements,
            job_requirements if isinstance(job_requirements, dict) else {},
            workflow_input.target_role,
        ),
        output_summarizer=lambda value: "Validated job context from "
        f"{value.get('source', 'unknown')} with {len(value.get('required_skills', []))} required skill(s).",
        trace=trace,
    )

    portfolio_summary = _call_tool(
        tool_name="build_portfolio_summary",
        arguments={"projects": workflow_input.projects},
        direct_callable=summarize_portfolio_tool,
        direct_args=(workflow_input.projects,),
        agent_name="portfolio_evidence",
        input_summary=f"{len(workflow_input.projects)} portfolio project(s)",
        output_summarizer=_summarize_portfolio,
        trace=trace,
        runtime_caller=runtime_caller,
    )

    gemini_candidate_context = _call_gemini_agent_step(
        tool_name="extract_candidate_context_with_gemini",
        payload={
            "profile": profile,
            "masked_cv_context_provided": bool(str(masked_cv_text).strip()),
            "masked_cv_text": masked_cv_text,
            "portfolio_summary": portfolio_summary if isinstance(portfolio_summary, dict) else {},
        },
        agent_name="profile_matcher",
        input_summary="profile + masked_cv_text + portfolio_summary",
        output_summary="Gemini structured candidate extraction returned candidate context.",
        workflow_input=workflow_input,
        app_config=app_config,
        trace=trace,
        warnings=warnings,
        gemini_tool_generator=gemini_tool_generator,
    )

    validated_candidate_context = _call_validator_step(
        tool_name="validate_candidate_context",
        agent_name="profile_matcher",
        input_summary="gemini_candidate_context + profile + portfolio_summary",
        validator=lambda: validate_candidate_context(
            gemini_candidate_context,
            profile,
            workflow_input.projects,
            portfolio_summary if isinstance(portfolio_summary, dict) else {},
        ),
        output_summarizer=lambda value: "Validated candidate context from "
        f"{value.get('source', 'unknown')} with {len(value.get('candidate_skills', []))} candidate skill(s).",
        trace=trace,
    )

    score = _call_tool(
        tool_name="calculate_match_score",
        arguments={"job_text": masked_job_text, "profile": profile, "projects": workflow_input.projects},
        direct_callable=calculate_match_score_tool,
        direct_args=(masked_job_text, profile, workflow_input.projects),
        agent_name="profile_matcher",
        input_summary="masked_job_text + profile + projects",
        output_summarizer=lambda value: f"Deterministic score returned: {value.get('overall_score', 0)}/100."
        if isinstance(value, dict)
        else "Deterministic score returned.",
        trace=trace,
        runtime_caller=runtime_caller,
    )

    report = _call_tool(
        tool_name="build_career_report",
        arguments={
            "job_text": masked_job_text,
            "profile": profile,
            "projects": workflow_input.projects,
            "cv_text": masked_cv_text,
            "output_style": workflow_input.output_style,
        },
        direct_callable=build_mock_report_tool,
        direct_args=(masked_job_text, profile, workflow_input.projects, masked_cv_text, workflow_input.output_style),
        agent_name="career_report_builder",
        input_summary="masked_job_text + profile + projects + masked_cv_text",
        output_summarizer=lambda value: "Structured career report created with deterministic score "
        f"{value.get('profile_match', {}).get('overall_score', 0)}/100."
        if isinstance(value, dict)
        else "Structured career report created.",
        trace=trace,
        runtime_caller=runtime_caller,
    )

    report = deepcopy(report)
    _attach_tool_calling_metadata(report, trace, job_requirements, portfolio_summary, score)
    report["gemini_extracted_context"] = {
        "job_requirements": validated_job_context,
        "candidate_context": validated_candidate_context,
    }

    deterministic_fields = _deterministic_profile_match_snapshot(report)
    report["canonical_profile_match_snapshot"] = deepcopy(deterministic_fields)
    narrative_enhancements = _run_gemini_narrative_writers(
        report=report,
        extracted_context=report["gemini_extracted_context"],
        workflow_input=workflow_input,
        app_config=app_config,
        trace=trace,
        warnings=warnings,
        gemini_tool_generator=gemini_tool_generator,
    )
    if narrative_enhancements:
        apply_narrative_enhancements(report, narrative_enhancements)
        _restore_deterministic_profile_match_fields(report, deterministic_fields)

    mode_used = "Mock deterministic mode"
    if workflow_input.analysis_mode != "Gemini-assisted summary":
        trace.append(
            ToolCallTraceStep(
                agent_name="gemini_narrative",
                tool_name="generate_gemini_career_insights",
                backend_used="Gemini API",
                status="skipped",
                input_summary="deterministic report",
                output_summary="Gemini narrative skipped because mock deterministic mode was selected.",
                fallback_used=False,
            )
        )
    elif not app_config.gemini_enabled or not app_config.google_api_key:
        _append_missing_key_warning_once(warnings)
        trace.append(
            ToolCallTraceStep(
                agent_name="gemini_narrative",
                tool_name="generate_gemini_career_insights",
                backend_used="Gemini API",
                status="skipped",
                input_summary="deterministic report",
                output_summary="Gemini narrative skipped because no local API key is configured.",
                fallback_used=True,
                warnings=["GOOGLE_API_KEY or GEMINI_API_KEY is not configured."],
            )
        )
    elif narrative_enhancements:
        insights = _synthesize_gemini_insights_from_enhancements(report)
        report["gemini_insights"] = insights
        report["gemini_summary"] = insights.get("career_summary", "")
        mode_used = "Gemini-assisted summary"
        trace.append(
            ToolCallTraceStep(
                agent_name="gemini_narrative",
                tool_name="generate_gemini_career_insights",
                backend_used="Local synthesis",
                status="completed",
                input_summary="Gemini-enhanced narrative sections",
                output_summary=(
                    "Summary synthesized from Gemini extraction/writer outputs; no extra Gemini API call was needed."
                ),
                fallback_used=False,
            )
        )
    else:
        generator = gemini_generator or generate_gemini_career_insights
        try:
            insights = generator(deepcopy(report), app_config.google_api_key, app_config.gemini_model)
            report["gemini_insights"] = insights
            report["gemini_summary"] = str(insights.get("career_summary", "")) if isinstance(insights, dict) else ""
            fallback_enhancements = _fallback_enhancements_from_insights(insights, report)
            if fallback_enhancements:
                apply_narrative_enhancements(report, fallback_enhancements)
            _restore_deterministic_profile_match_fields(report, deterministic_fields)
            mode_used = "Gemini-assisted summary"
            trace.append(
                ToolCallTraceStep(
                    agent_name="gemini_narrative",
                    tool_name="generate_gemini_career_insights",
                    backend_used="Gemini API",
                    status="completed",
                    input_summary="deterministic report",
                    output_summary="Gemini narrative insights generated without modifying deterministic score fields.",
                    fallback_used=False,
                )
            )
        except Exception as exc:
            detail = _short_error(exc)
            warnings.append(
                f"Gemini-assisted insights could not be generated ({detail}). Tool-calling workflow continued."
            )
            _restore_deterministic_profile_match_fields(report, deterministic_fields)
            trace.append(
                ToolCallTraceStep(
                    agent_name="gemini_narrative",
                    tool_name="generate_gemini_career_insights",
                    backend_used="Gemini API",
                    status="fallback",
                    input_summary="deterministic report",
                    output_summary="Gemini narrative failed; deterministic report preserved.",
                    fallback_used=True,
                    warnings=[f"Gemini request failed or returned invalid output: {detail}"],
                )
            )

    _refresh_tool_calling_runtime_route(report, trace)
    report["tool_call_trace"] = [asdict(step) for step in trace]
    return ToolCallingWorkflowResult(report=report, tool_call_trace=trace, warnings=warnings, mode_used=mode_used)


def _call_tool(
    *,
    tool_name: str,
    arguments: dict[str, Any],
    direct_callable: Callable[..., Any],
    direct_args: tuple[Any, ...],
    agent_name: str,
    input_summary: str,
    output_summarizer: Callable[[Any], str],
    trace: list[ToolCallTraceStep],
    runtime_caller: ToolRuntimeCaller | None,
) -> Any:
    step_warnings: list[str] = []
    try:
        value = _normalize_tool_output(_call_mcp_runtime(tool_name, arguments, runtime_caller=runtime_caller))
        trace.append(
            ToolCallTraceStep(
                agent_name=agent_name,
                tool_name=tool_name,
                backend_used=MCP_RUNTIME_BACKEND,
                status="completed",
                input_summary=input_summary,
                output_summary=output_summarizer(value),
                fallback_used=False,
            )
        )
        return value
    except Exception as exc:
        step_warnings.append(f"MCP runtime unavailable: {_short_error(exc)}")

    try:
        value = _normalize_tool_output(_call_mcp_style_registry(tool_name, arguments))
        trace.append(
            ToolCallTraceStep(
                agent_name=agent_name,
                tool_name=tool_name,
                backend_used=MCP_STYLE_REGISTRY_BACKEND,
                status="fallback",
                input_summary=input_summary,
                output_summary=output_summarizer(value),
                fallback_used=True,
                warnings=step_warnings,
            )
        )
        return value
    except Exception as exc:
        step_warnings.append(f"Local MCP-style registry unavailable: {_short_error(exc)}")

    value = _normalize_tool_output(direct_callable(*direct_args))
    trace.append(
        ToolCallTraceStep(
            agent_name=agent_name,
            tool_name=tool_name,
            backend_used=DIRECT_FALLBACK_BACKEND,
            status="fallback",
            input_summary=input_summary,
            output_summary=output_summarizer(value),
            fallback_used=True,
            warnings=step_warnings,
        )
    )
    return value


def _call_gemini_agent_step(
    *,
    tool_name: str,
    payload: dict[str, Any],
    agent_name: str,
    input_summary: str,
    output_summary: str,
    workflow_input: ToolCallingWorkflowInput,
    app_config: AppConfig,
    trace: list[ToolCallTraceStep],
    warnings: list[str],
    gemini_tool_generator: GeminiToolGenerator | None,
) -> Any:
    if workflow_input.analysis_mode != "Gemini-assisted summary":
        trace.append(
            ToolCallTraceStep(
                agent_name=agent_name,
                tool_name=tool_name,
                backend_used="Gemini API",
                status="skipped",
                input_summary=input_summary,
                output_summary="Gemini step skipped because mock deterministic mode was selected.",
                fallback_used=False,
            )
        )
        return None

    if not app_config.gemini_enabled or not app_config.google_api_key:
        _append_missing_key_warning_once(warnings)
        trace.append(
            ToolCallTraceStep(
                agent_name=agent_name,
                tool_name=tool_name,
                backend_used="Gemini API",
                status="skipped",
                input_summary=input_summary,
                output_summary="Gemini step skipped because no local API key is configured.",
                fallback_used=True,
                warnings=["GOOGLE_API_KEY or GEMINI_API_KEY is not configured."],
            )
        )
        return None

    generator = gemini_tool_generator or generate_gemini_agent_payload
    try:
        value = generator(tool_name, deepcopy(payload), app_config.google_api_key, app_config.gemini_model)
        trace.append(
            ToolCallTraceStep(
                agent_name=agent_name,
                tool_name=tool_name,
                backend_used="Gemini API",
                status="completed",
                input_summary=input_summary,
                output_summary=output_summary,
                fallback_used=False,
                warnings=_extract_payload_warnings(value),
            )
        )
        return value
    except Exception as exc:
        detail = _short_error(exc)
        trace.append(
            ToolCallTraceStep(
                agent_name=agent_name,
                tool_name=tool_name,
                backend_used="Gemini API",
                status="fallback",
                input_summary=input_summary,
                output_summary="Gemini step failed; deterministic fallback data was preserved.",
                fallback_used=True,
                warnings=[f"Gemini request failed or returned invalid output: {detail}"],
            )
        )
        return None


def _call_validator_step(
    *,
    tool_name: str,
    agent_name: str,
    input_summary: str,
    validator: Callable[[], dict[str, Any]],
    output_summarizer: Callable[[dict[str, Any]], str],
    trace: list[ToolCallTraceStep],
) -> dict[str, Any]:
    value = validator()
    trace.append(
        ToolCallTraceStep(
            agent_name=agent_name,
            tool_name=tool_name,
            backend_used="Deterministic validator",
            status="completed" if value.get("source") == "gemini_validated" else "fallback",
            input_summary=input_summary,
            output_summary=output_summarizer(value),
            fallback_used=value.get("source") != "gemini_validated",
            warnings=value.get("warnings", []),
        )
    )
    return value


def _run_gemini_narrative_writers(
    *,
    report: dict[str, Any],
    extracted_context: dict[str, Any],
    workflow_input: ToolCallingWorkflowInput,
    app_config: AppConfig,
    trace: list[ToolCallTraceStep],
    warnings: list[str],
    gemini_tool_generator: GeminiToolGenerator | None,
) -> dict[str, dict[str, Any]]:
    writer_specs = [
        (
            "generate_gap_narrative",
            "gap_planner",
            sanitize_gap_narrative,
            "Gemini gap narrative generated from canonical gaps.",
        ),
        (
            "generate_action_plan_narrative",
            "gap_planner",
            sanitize_action_plan,
            "Gemini action plan narrative generated from canonical report.",
        ),
        (
            "generate_application_drafts",
            "application_writer",
            sanitize_application_drafts,
            "Gemini application drafts generated from canonical evidence.",
        ),
        (
            "generate_interview_prep",
            "interview_coach",
            sanitize_interview_prep,
            "Gemini interview preparation generated from canonical gaps and evidence.",
        ),
    ]
    output_keys = {
        "generate_gap_narrative": "gaps",
        "generate_action_plan_narrative": "action_plan",
        "generate_application_drafts": "application",
        "generate_interview_prep": "interview",
    }
    enhancements: dict[str, dict[str, Any]] = {}
    payload = {
        "canonical_report": _report_for_gemini_writer(report),
        "gemini_extracted_context": extracted_context,
        "output_style": workflow_input.output_style,
    }
    for tool_name, agent_name, sanitizer, output_summary in writer_specs:
        raw_value = _call_gemini_agent_step(
            tool_name=tool_name,
            payload=payload,
            agent_name=agent_name,
            input_summary="canonical deterministic report + validated extracted context",
            output_summary=output_summary,
            workflow_input=workflow_input,
            app_config=app_config,
            trace=trace,
            warnings=warnings,
            gemini_tool_generator=gemini_tool_generator,
        )
        sanitized = sanitizer(raw_value, report) if tool_name == "generate_gap_narrative" else sanitizer(raw_value)
        if sanitized:
            enhancements[output_keys[tool_name]] = sanitized
    return enhancements


def _call_mcp_runtime(
    tool_name: str,
    arguments: dict[str, Any],
    *,
    runtime_caller: ToolRuntimeCaller | None,
) -> Any:
    caller = runtime_caller
    if caller is None:
        from devpath.mcp_runtime import call_mcp_tool_stdio

        caller = call_mcp_tool_stdio
    result = caller(tool_name, arguments)
    return result.data if hasattr(result, "data") else result


def _call_mcp_style_registry(tool_name: str, arguments: dict[str, Any]) -> Any:
    from mcp_server.tools import MCP_TOOL_REGISTRY

    return MCP_TOOL_REGISTRY[tool_name](**arguments)


def _normalize_tool_output(value: Any) -> Any:
    if isinstance(value, dict) and set(value) == {"result"}:
        return value["result"]
    return value


def _attach_tool_calling_metadata(
    report: dict[str, Any],
    trace: list[ToolCallTraceStep],
    job_requirements: Any,
    portfolio_summary: Any,
    score: Any,
) -> None:
    backend_names = [step.backend_used for step in trace]
    report["agent_workflow"] = {
        "enabled": True,
        "orchestration": "Gemini/ADK tool-calling agent workflow",
        "agents": [
            "privacy_guard",
            "job_analyzer",
            "portfolio_evidence",
            "profile_matcher",
            "career_report_builder",
            "gap_planner",
            "application_writer",
            "interview_coach",
            "gemini_narrative",
        ],
        "scoring_source": "deterministic",
        "llm_score_modification": False,
    }
    report["runtime_route"] = {
        "tool_backend": _primary_backend(backend_names),
        "requested_tool_backend": MCP_RUNTIME_BACKEND,
        "mcp_runtime_used": MCP_RUNTIME_BACKEND in backend_names,
        "experimental": True,
        "fallback_used": any(step.fallback_used for step in trace),
        "selected_tools": [step.tool_name for step in trace],
        "notes": [
            "Gemini/ADK tool-calling mode requested MCP runtime first.",
            "Local MCP-style registry and direct deterministic services are safe fallbacks.",
            "Numeric score, gaps, and evidence remain deterministic.",
        ],
    }
    report["tool_calling_context"] = {
        "job_required_skills": job_requirements.get("required_skills", []) if isinstance(job_requirements, dict) else [],
        "portfolio_project_count": portfolio_summary.get("project_count", 0) if isinstance(portfolio_summary, dict) else 0,
        "score": score.get("overall_score", 0) if isinstance(score, dict) else report.get("profile_match", {}).get("overall_score", 0),
    }


def _refresh_tool_calling_runtime_route(report: dict[str, Any], trace: list[ToolCallTraceStep]) -> None:
    backend_names = [step.backend_used for step in trace]
    runtime_route = dict(report.get("runtime_route", {}))
    runtime_route.update(
        {
            "tool_backend": _primary_backend(backend_names),
            "requested_tool_backend": MCP_RUNTIME_BACKEND,
            "mcp_runtime_used": MCP_RUNTIME_BACKEND in backend_names,
            "experimental": True,
            "fallback_used": any(step.fallback_used for step in trace),
            "selected_tools": [step.tool_name for step in trace],
        }
    )
    report["runtime_route"] = runtime_route


def _primary_backend(backends: list[str]) -> str:
    if MCP_RUNTIME_BACKEND in backends:
        return MCP_RUNTIME_BACKEND
    if MCP_STYLE_REGISTRY_BACKEND in backends:
        return MCP_STYLE_REGISTRY_BACKEND
    return DIRECT_BACKEND


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


def _report_for_gemini_writer(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "job_analysis": report.get("job_analysis", {}),
        "profile_match": report.get("profile_match", {}),
        "portfolio_evidence": report.get("portfolio_evidence", {}),
        "skill_gaps": report.get("skill_gaps", {}),
        "preparation_plan": report.get("preparation_plan", {}),
        "application_drafts": report.get("application_drafts", {}),
        "interview_prep": report.get("interview_prep", {}),
    }


def _synthesize_gemini_insights_from_enhancements(report: dict[str, Any]) -> dict[str, Any]:
    enhancements = report.get("gemini_narrative_enhancements", {})
    gaps = enhancements.get("gaps", {}) if isinstance(enhancements, dict) else {}
    action_plan = enhancements.get("action_plan", {}) if isinstance(enhancements, dict) else {}
    application = enhancements.get("application", {}) if isinstance(enhancements, dict) else {}
    interview = enhancements.get("interview", {}) if isinstance(enhancements, dict) else {}

    career_summary_parts = [
        gaps.get("summary", "") if isinstance(gaps, dict) else "",
        action_plan.get("summary", "") if isinstance(action_plan, dict) else "",
        interview.get("focus_summary", "") if isinstance(interview, dict) else "",
    ]
    career_summary = " ".join(part for part in career_summary_parts if part).strip()
    if not career_summary:
        career_summary = "Gemini-enhanced narrative sections were generated from the deterministic report."

    return {
        "career_summary": career_summary,
        "top_actions": action_plan.get("7_day_plan", [])[:3] if isinstance(action_plan, dict) else [],
        "portfolio_positioning": application.get("cv_bullets", [])[:3] if isinstance(application, dict) else [],
        "skill_gap_strategy": [
            item.get("next_step", "")
            for item in gaps.get("gap_explanations", [])
            if isinstance(item, dict) and item.get("next_step")
        ]
        if isinstance(gaps, dict)
        else [],
        "interview_focus": interview.get("practice_focus", [])[:3] if isinstance(interview, dict) else [],
        "raw_response": "",
    }


def _fallback_enhancements_from_insights(insights: Any, report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    if not isinstance(insights, dict):
        return {}
    existing = report.get("gemini_narrative_enhancements", {})
    enhancements: dict[str, dict[str, Any]] = {}
    if not isinstance(existing, dict) or not existing.get("gaps"):
        strategy = [str(item).strip() for item in insights.get("skill_gap_strategy", []) if str(item).strip()]
        if strategy:
            gaps = report.get("skill_gaps", {}).get("prioritized_gaps", [])
            skill = gaps[0].get("skill", "Portfolio positioning") if gaps else "Portfolio positioning"
            enhancements["gaps"] = {
                "summary": insights.get("career_summary", ""),
                "gap_explanations": [
                    {
                        "skill": skill,
                        "explanation": strategy[0],
                        "next_step": strategy[1] if len(strategy) > 1 else strategy[0],
                    }
                ],
            }
    if not isinstance(existing, dict) or not existing.get("action_plan"):
        top_actions = [str(item).strip() for item in insights.get("top_actions", []) if str(item).strip()]
        if top_actions:
            enhancements["action_plan"] = {
                "summary": "Gemini-assisted action priorities based on the deterministic report.",
                "7_day_plan": top_actions[:3],
                "14_day_plan": top_actions[1:4] or top_actions[:3],
                "30_day_roadmap": top_actions[:3],
            }
    if not isinstance(existing, dict) or not existing.get("application"):
        positioning = [str(item).strip() for item in insights.get("portfolio_positioning", []) if str(item).strip()]
        if positioning:
            enhancements["application"] = {
                "cover_letter_draft": "",
                "recruiter_message_draft": "",
                "cv_bullets": positioning[:3],
            }
    if not isinstance(existing, dict) or not existing.get("interview"):
        focus = [str(item).strip() for item in insights.get("interview_focus", []) if str(item).strip()]
        if focus:
            enhancements["interview"] = {
                "focus_summary": "Gemini-assisted interview focus based on deterministic gaps and evidence.",
                "questions": [f"How would you explain your experience with {item}?" for item in focus[:5]],
                "practice_focus": focus[:5],
            }
    return enhancements


def _append_missing_key_warning_once(warnings: list[str]) -> None:
    warning = "Gemini API key is not configured. Tool-calling workflow continued with deterministic report."
    if warning not in warnings:
        warnings.append(warning)


def _extract_payload_warnings(value: Any) -> list[str]:
    if isinstance(value, dict):
        warnings = value.get("warnings", [])
        if isinstance(warnings, list):
            return [str(item).strip() for item in warnings if str(item).strip()]
    return []


def _summarize_job_requirements(value: Any) -> str:
    if not isinstance(value, dict):
        return "Job requirements extracted."
    skills = value.get("required_skills", [])
    nice = value.get("nice_to_have_skills", [])
    return f"Detected {len(skills)} required skill(s) and {len(nice)} nice-to-have skill(s)."


def _summarize_portfolio(value: Any) -> str:
    if not isinstance(value, dict):
        return "Portfolio summary created."
    return (
        f"Summarized {value.get('project_count', 0)} project(s) with "
        f"{len(value.get('evidence_by_skill', {}))} evidence skill area(s)."
    )


def _short_error(exc: Exception) -> str:
    message = str(exc).strip().replace("\n", " ")
    return message[:180] or exc.__class__.__name__
