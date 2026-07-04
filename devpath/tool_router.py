"""Local tool backend router for deterministic report generation."""

from typing import Any

from devpath.agent_tools import build_mock_report_tool


DIRECT_BACKEND = "Direct Python services"
MCP_STYLE_BACKEND = "Local MCP-style tools"
ADK_MCP_RUNTIME_BACKEND = "Experimental ADK-MCP runtime tools"


def list_tool_backends() -> list[str]:
    """Return supported local tool backend names."""

    return [DIRECT_BACKEND, MCP_STYLE_BACKEND, ADK_MCP_RUNTIME_BACKEND]


def normalize_tool_backend(value: str | None) -> str:
    """Normalize an optional backend name to a supported backend."""

    if value in list_tool_backends():
        return str(value)
    return DIRECT_BACKEND


def build_report_with_backend(
    job_text: str,
    profile: dict[str, Any],
    projects: list[dict[str, Any]],
    cv_text: str = "",
    output_style: str = "Concise",
    tool_backend: str = DIRECT_BACKEND,
) -> dict[str, Any]:
    """Build a deterministic career report using the selected local backend."""

    backend = normalize_tool_backend(tool_backend)
    if backend == MCP_STYLE_BACKEND:
        report = _build_report_with_mcp_style_tools(
            job_text=job_text,
            profile=profile,
            projects=projects,
            cv_text=cv_text,
            output_style=output_style,
        )
        return _attach_runtime_route(
            report,
            tool_backend=backend,
            mcp_runtime_used=False,
            experimental=False,
            fallback_used=False,
            selected_tools=["local MCP-style wrappers"],
            notes=["Uses local MCP-style registry without starting runtime transport."],
        )

    if backend == ADK_MCP_RUNTIME_BACKEND:
        return _build_report_with_adk_mcp_runtime_tools(
            job_text=job_text,
            profile=profile,
            projects=projects,
            cv_text=cv_text,
            output_style=output_style,
        )

    report = build_mock_report_tool(
        job_text=job_text,
        profile=profile,
        projects=projects,
        cv_text=cv_text,
        output_style=output_style,
    )
    return _attach_runtime_route(
        report,
        tool_backend=backend,
        mcp_runtime_used=False,
        experimental=False,
        fallback_used=False,
        selected_tools=[],
        notes=["Default deterministic backend."],
    )


def _build_report_with_mcp_style_tools(
    job_text: str,
    profile: dict[str, Any],
    projects: list[dict[str, Any]],
    cv_text: str,
    output_style: str,
) -> dict[str, Any]:
    try:
        from mcp_server.tools import MCP_TOOL_REGISTRY

        tool = MCP_TOOL_REGISTRY["build_career_report"]
        return tool(
            job_text=job_text,
            profile=profile,
            projects=projects,
            cv_text=cv_text,
            output_style=output_style,
        )
    except Exception as exc:
        raise RuntimeError("Local MCP-style tools could not build the deterministic report.") from exc


def _build_report_with_adk_mcp_runtime_tools(
    job_text: str,
    profile: dict[str, Any],
    projects: list[dict[str, Any]],
    cv_text: str,
    output_style: str,
) -> dict[str, Any]:
    """Build a report while validating selected tools through MCP runtime."""

    report = build_mock_report_tool(
        job_text=job_text,
        profile=profile,
        projects=projects,
        cv_text=cv_text,
        output_style=output_style,
    )

    try:
        from devpath.adk_mcp_tools import (
            analyze_job_posting_via_mcp_tool,
            calculate_match_score_via_mcp_tool,
        )

        job_analysis = analyze_job_posting_via_mcp_tool(job_text)
        runtime_score = calculate_match_score_via_mcp_tool(job_text, profile, projects)
    except Exception as exc:
        raise RuntimeError("Experimental ADK-MCP runtime tools could not build the deterministic report.") from exc

    base_score = report.get("profile_match", {}).get("overall_score")
    runtime_score_value = runtime_score.get("overall_score")
    score_consistent = runtime_score_value == base_score
    notes = ["Selected ADK-style wrappers routed through local MCP stdio runtime."]
    if _has_expected_score_fields(runtime_score):
        report["profile_match"] = runtime_score
    else:
        notes.append("Runtime score result was incompatible, so the original deterministic score was preserved.")

    runtime_route = {
        "tool_backend": ADK_MCP_RUNTIME_BACKEND,
        "mcp_runtime_used": True,
        "experimental": True,
        "fallback_used": False,
        "selected_tools": ["analyze_job_posting", "calculate_match_score"],
        "notes": notes,
    }
    if isinstance(job_analysis, dict):
        runtime_route["job_analysis_detected_skills"] = job_analysis.get("required_skills", [])
    if score_consistent is False:
        runtime_route["notes"].append("Runtime score differed from the direct deterministic pre-check.")

    report["runtime_route"] = runtime_route
    return report


def _has_expected_score_fields(score: dict[str, Any]) -> bool:
    return all(
        key in score
        for key in (
            "overall_score",
            "category_scores",
            "strong_matches",
            "partial_matches",
            "missing_skills",
            "evidence_by_skill",
            "prioritized_gaps",
        )
    )


def _attach_runtime_route(
    report: dict[str, Any],
    *,
    tool_backend: str,
    mcp_runtime_used: bool,
    experimental: bool,
    fallback_used: bool,
    selected_tools: list[str],
    notes: list[str],
) -> dict[str, Any]:
    report["runtime_route"] = {
        "tool_backend": tool_backend,
        "mcp_runtime_used": mcp_runtime_used,
        "experimental": experimental,
        "fallback_used": fallback_used,
        "selected_tools": selected_tools,
        "notes": notes,
    }
    return report
