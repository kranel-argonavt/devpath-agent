"""Stable MCP-style deterministic tool registry for DevPath."""

from mcp_server.tools.export_tools import export_markdown_report
from mcp_server.tools.github_tools import fetch_github_repositories, fetch_repository_readme
from mcp_server.tools.portfolio_tools import build_portfolio_summary, summarize_portfolio
from mcp_server.tools.privacy_tools import detect_sensitive_data, mask_personal_data
from mcp_server.tools.profile_tools import read_profile
from mcp_server.tools.project_tools import read_local_projects
from mcp_server.tools.report_tools import build_career_report
from mcp_server.tools.scoring_tools import analyze_job_posting, calculate_match_score


MCP_TOOL_REGISTRY = {
    "analyze_job_posting": analyze_job_posting,
    "read_profile": read_profile,
    "read_local_projects": read_local_projects,
    "fetch_github_repositories": fetch_github_repositories,
    "fetch_repository_readme": fetch_repository_readme,
    "summarize_portfolio": summarize_portfolio,
    "build_portfolio_summary": build_portfolio_summary,
    "calculate_match_score": calculate_match_score,
    "build_career_report": build_career_report,
    "detect_sensitive_data": detect_sensitive_data,
    "mask_personal_data": mask_personal_data,
    "export_markdown_report": export_markdown_report,
}


def list_mcp_tools() -> list[str]:
    """Return stable MCP-style tool names for future runtime integration."""

    return sorted(MCP_TOOL_REGISTRY)
