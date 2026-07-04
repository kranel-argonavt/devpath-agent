"""ADK-compatible profile matcher sub-agent skeleton."""

from typing import Any

from devpath.agent_tools import calculate_match_score_tool

try:  # pragma: no cover - exercised only when google-adk is installed.
    from google.adk.agents import Agent
except ImportError:  # pragma: no cover
    try:
        from google.adk.agents.llm_agent import Agent
    except ImportError:
        Agent = None  # type: ignore[assignment]


NAME = "profile_matcher_agent"
DESCRIPTION = "Compares candidate evidence against a target job using deterministic scoring."
INSTRUCTION = """
Call deterministic scoring tools and explain score categories, strong matches, partial matches,
and gaps. Use deterministic scoring tools as the source of truth. Never invent or modify
numeric match scores. In the full workflow, this stage is responsible for producing the
report's deterministic profile_match section.
"""
TOOLS = [calculate_match_score_tool]


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
