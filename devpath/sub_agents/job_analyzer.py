"""ADK-compatible job analyzer sub-agent skeleton."""

from typing import Any

from devpath.agent_tools import analyze_job_posting_tool

try:  # pragma: no cover - exercised only when google-adk is installed.
    from google.adk.agents import Agent
except ImportError:  # pragma: no cover
    try:
        from google.adk.agents.llm_agent import Agent
    except ImportError:
        Agent = None  # type: ignore[assignment]


NAME = "job_analyzer_agent"
DESCRIPTION = "Extracts structured requirements from job postings."
INSTRUCTION = """
Extract required skills, nice-to-have skills, seniority, language, location, and responsibilities
from job postings. Use deterministic job analysis tools when available and do not invent
requirements that are not supported by the posting. In the full workflow, write structured
requirements into state for portfolio and profile matching stages.
"""
TOOLS = [analyze_job_posting_tool]


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
