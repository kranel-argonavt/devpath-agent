"""ADK-compatible gap planner sub-agent skeleton."""

from typing import Any

from devpath.agent_tools import build_mock_report_tool

try:  # pragma: no cover - exercised only when google-adk is installed.
    from google.adk.agents import Agent
except ImportError:  # pragma: no cover
    try:
        from google.adk.agents.llm_agent import Agent
    except ImportError:
        Agent = None  # type: ignore[assignment]


NAME = "gap_planner_agent"
DESCRIPTION = "Creates prioritized 7/14/30-day improvement plans from deterministic gaps."
INSTRUCTION = """
Create realistic 7-day, 14-day, and 30-day plans from deterministic gaps and report data.
Prioritize required skill gaps before nice-to-have skills. Do not create fake gaps or add
missing skills that are not present in the deterministic report.
"""
TOOLS = [build_mock_report_tool]


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
