"""Google ADK-compatible root agent skeleton for DevPath Agent."""

from typing import Any

from devpath.agent_tools import (
    analyze_job_posting_tool,
    build_mock_report_tool,
    calculate_match_score_tool,
    mask_personal_data_tool,
    summarize_portfolio_tool,
)
from devpath.sub_agents.application_writer import create_agent as create_application_writer_agent
from devpath.sub_agents.gap_planner import create_agent as create_gap_planner_agent
from devpath.sub_agents.interview_coach import create_agent as create_interview_coach_agent
from devpath.sub_agents.job_analyzer import create_agent as create_job_analyzer_agent
from devpath.sub_agents.portfolio_evidence import create_agent as create_portfolio_evidence_agent
from devpath.sub_agents.privacy_guard import create_agent as create_privacy_guard_agent
from devpath.sub_agents.profile_matcher import create_agent as create_profile_matcher_agent

try:  # pragma: no cover - exercised only when google-adk is installed.
    from google.adk.agents import Agent
except ImportError:  # pragma: no cover - fallback is covered by structure tests.
    try:
        from google.adk.agents.llm_agent import Agent
    except ImportError:
        Agent = None  # type: ignore[assignment]


ROOT_AGENT_NAME = "devpath_root_agent"
ROOT_AGENT_DESCRIPTION = "Orchestrates the DevPath career copilot workflow with deterministic tools."
ROOT_AGENT_INSTRUCTION = """
You are the DevPath Root Agent for junior software developer career preparation.

Responsibilities:
- Orchestrate job analysis, portfolio evidence review, profile matching, skill gap planning,
  application preparation, interview coaching, and privacy checks.
- Coordinate the career strategy workflow through privacy_guard, job_analyzer, portfolio_evidence,
  profile_matcher, gap_planner, application_writer, and interview_coach.
- Use deterministic scoring tools as the source of truth. Do not invent or modify numeric match scores.
- Prefer structured evidence from the provided profile, projects, CV context, and job posting.
- Do not call external APIs unless a future integration explicitly provides an approved tool.
- Selected ADK-style wrappers can route deterministic calls through the local MCP runtime
  experimentally, but direct deterministic tools remain the primary safe path.
"""

ROOT_AGENT_TOOLS = [
    analyze_job_posting_tool,
    summarize_portfolio_tool,
    calculate_match_score_tool,
    build_mock_report_tool,
    mask_personal_data_tool,
]


def create_root_agent() -> Any:
    """Create the ADK root agent if ADK is available, otherwise return metadata."""

    sub_agents = [
        create_job_analyzer_agent(),
        create_portfolio_evidence_agent(),
        create_profile_matcher_agent(),
        create_gap_planner_agent(),
        create_application_writer_agent(),
        create_interview_coach_agent(),
        create_privacy_guard_agent(),
    ]
    if Agent is None:
        return _metadata(sub_agents=sub_agents, adk_available=False)

    try:
        return Agent(
            name=ROOT_AGENT_NAME,
            model="gemini-2.5-flash",
            description=ROOT_AGENT_DESCRIPTION,
            instruction=ROOT_AGENT_INSTRUCTION,
            tools=ROOT_AGENT_TOOLS,
            sub_agents=sub_agents,
        )
    except Exception:
        return _metadata(sub_agents=sub_agents, adk_available=True)


def get_agent_status() -> str:
    """Return a simple status for the ADK-compatible root agent skeleton."""

    return "DevPath root agent skeleton available"


def _metadata(sub_agents: list[Any], adk_available: bool) -> dict[str, Any]:
    return {
        "name": ROOT_AGENT_NAME,
        "description": ROOT_AGENT_DESCRIPTION,
        "instruction": ROOT_AGENT_INSTRUCTION,
        "tools": [tool.__name__ for tool in ROOT_AGENT_TOOLS],
        "experimental_mcp_runtime_tools": [
            "mask_personal_data",
            "analyze_job_posting",
            "calculate_match_score",
        ],
        "full_agent_workflow": [
            "privacy_guard",
            "job_analyzer",
            "portfolio_evidence",
            "profile_matcher",
            "gap_planner",
            "application_writer",
            "interview_coach",
        ],
        "sub_agents": sub_agents,
        "adk_available": adk_available,
    }


root_agent = create_root_agent()
