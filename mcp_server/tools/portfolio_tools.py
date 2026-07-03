"""MCP-style deterministic portfolio tools."""

from typing import Any

from devpath.agent_tools import summarize_portfolio_tool


def summarize_portfolio(projects: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarize portfolio projects and detected evidence."""

    return summarize_portfolio_tool(projects)
