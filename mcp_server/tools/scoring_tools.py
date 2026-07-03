"""MCP-style deterministic scoring tools."""

from typing import Any

from devpath.agent_tools import analyze_job_posting_tool, calculate_match_score_tool


def analyze_job_posting(job_text: str) -> dict[str, Any]:
    """Extract deterministic requirements from job text."""

    return analyze_job_posting_tool(job_text)


def calculate_match_score(
    job_text: str,
    profile: dict[str, Any],
    projects: list[dict[str, Any]],
) -> dict[str, Any]:
    """Calculate deterministic match score."""

    return calculate_match_score_tool(job_text=job_text, profile=profile, projects=projects)
