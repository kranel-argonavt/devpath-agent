"""MCP-style deterministic report tools."""

from typing import Any

from devpath.agent_tools import build_mock_report_tool


def build_career_report(
    job_text: str,
    profile: dict[str, Any],
    projects: list[dict[str, Any]],
    cv_text: str = "",
    output_style: str = "Concise",
) -> dict[str, Any]:
    """Build deterministic career strategy report."""

    return build_mock_report_tool(
        job_text=job_text,
        profile=profile,
        projects=projects,
        cv_text=cv_text,
        output_style=output_style,
    )
