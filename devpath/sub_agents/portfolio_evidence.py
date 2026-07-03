"""ADK-compatible portfolio evidence sub-agent skeleton."""

from typing import Any

from devpath.agent_tools import summarize_portfolio_tool

try:  # pragma: no cover - exercised only when google-adk is installed.
    from google.adk.agents import Agent
except ImportError:  # pragma: no cover
    try:
        from google.adk.agents.llm_agent import Agent
    except ImportError:
        Agent = None  # type: ignore[assignment]


NAME = "portfolio_evidence_agent"
DESCRIPTION = "Maps profile and project evidence to role requirements."
INSTRUCTION = """
Review candidate projects and identify project-based proof for skills. Use deterministic
portfolio evidence tools first. Future GitHub public repository summaries may be used only
through approved tools.
"""
TOOLS = [summarize_portfolio_tool]


def create_agent() -> Any:
    """Create the ADK sub-agent if ADK is available, otherwise return metadata."""

    if Agent is None:
        return _metadata(adk_available=False)
    try:
        return Agent(
            name=NAME,
            model="gemini-2.5-flash",
            description=DESCRIPTION,
            instruction=INSTRUCTION,
            tools=TOOLS,
        )
    except Exception:
        return _metadata(adk_available=True)


def _metadata(adk_available: bool) -> dict[str, Any]:
    return {
        "name": NAME,
        "description": DESCRIPTION,
        "instruction": INSTRUCTION,
        "tools": [tool.__name__ for tool in TOOLS],
        "adk_available": adk_available,
    }


agent = create_agent()
