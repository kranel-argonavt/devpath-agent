"""MCP-style deterministic portfolio tools."""

from typing import Any

from devpath.agent_tools import summarize_portfolio_tool


def summarize_portfolio(projects: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarize portfolio projects and detected evidence."""

    return summarize_portfolio_tool(projects)


def build_portfolio_summary(projects: list[dict[str, Any]]) -> dict[str, Any]:
    """Backward-compatible planned MCP tool name for portfolio summary."""

    return summarize_portfolio(projects)
