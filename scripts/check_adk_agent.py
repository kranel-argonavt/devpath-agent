"""Local smoke test for the DevPath ADK-compatible agent skeleton.

Run from the project root:
    python scripts/check_adk_agent.py
"""

from importlib import import_module
from pathlib import Path
import sys
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


SUB_AGENT_MODULES = [
    "devpath.sub_agents.job_analyzer",
    "devpath.sub_agents.portfolio_evidence",
    "devpath.sub_agents.profile_matcher",
    "devpath.sub_agents.gap_planner",
    "devpath.sub_agents.application_writer",
    "devpath.sub_agents.interview_coach",
    "devpath.sub_agents.privacy_guard",
]

EXPECTED_TOOLS = [
    "analyze_job_posting_tool",
    "summarize_portfolio_tool",
    "calculate_match_score_tool",
    "build_mock_report_tool",
    "mask_personal_data_tool",
]


def main() -> int:
    """Validate local ADK skeleton imports and deterministic tools."""

    print("DevPath ADK agent smoke test")
    try:
        import devpath.agent as agent_module
        from devpath.agent_tools import (
            analyze_job_posting_tool,
            build_mock_report_tool,
            calculate_match_score_tool,
            mask_personal_data_tool,
            summarize_portfolio_tool,
        )

        root_agent = agent_module.root_agent
        adk_available = _is_adk_available(agent_module, root_agent)
        fallback_metadata = isinstance(root_agent, dict)
        root_name = _agent_value(root_agent, "name") or "unknown"
        tool_names = _tool_names(root_agent)
        sub_agent_names = _validate_sub_agents()

        tools = {
            "analyze_job_posting_tool": analyze_job_posting_tool,
            "summarize_portfolio_tool": summarize_portfolio_tool,
            "calculate_match_score_tool": calculate_match_score_tool,
            "build_mock_report_tool": build_mock_report_tool,
            "mask_personal_data_tool": mask_personal_data_tool,
        }
        _validate_tools(tools)
        _run_deterministic_tool_checks(calculate_match_score_tool, mask_personal_data_tool)

        print(f"Root agent: {root_name}")
        print(f"ADK available: {_yes_no(adk_available)}")
        print(f"Fallback metadata: {_yes_no(fallback_metadata)}")
        print(f"Deterministic tools: {', '.join(sorted(tool_names or set(EXPECTED_TOOLS)))}")
        print(f"Sub-agents: {', '.join(sub_agent_names)}")
        print("ADK smoke test succeeded.")
        return 0
    except Exception as exc:
        print(f"ADK smoke test failed: {exc}")
        return 1


def _is_adk_available(agent_module: Any, root_agent: Any) -> bool:
    if isinstance(root_agent, dict) and "adk_available" in root_agent:
        return bool(root_agent["adk_available"])
    return getattr(agent_module, "Agent", None) is not None


def _validate_sub_agents() -> list[str]:
    names: list[str] = []
    for module_name in SUB_AGENT_MODULES:
        module = import_module(module_name)
        factory = getattr(module, "create_agent", None)
        if factory is None:
            raise RuntimeError(f"{module_name} does not expose create_agent().")

        sub_agent = factory()
        name = _agent_value(sub_agent, "name")
        description = _agent_value(sub_agent, "description")
        if not name or not description:
            raise RuntimeError(f"{module_name} did not create a valid sub-agent or metadata object.")
        names.append(str(name))
    return names


def _validate_tools(tools: dict[str, Any]) -> None:
    missing = [name for name in EXPECTED_TOOLS if name not in tools or not callable(tools[name])]
    if missing:
        raise RuntimeError(f"Missing deterministic tool(s): {', '.join(missing)}")


def _run_deterministic_tool_checks(calculate_match_score_tool, mask_personal_data_tool) -> None:
    score = calculate_match_score_tool(
        job_text=(
            "Junior .NET Developer role requiring C#, .NET, ASP.NET Core, SQL, Git, "
            "REST API, and English."
        ),
        profile={
            "experience_level": "Junior",
            "skills": ["C#", ".NET", "Git", "SQLite"],
            "education": "Software Engineering",
            "languages": ["English B1-B2"],
            "location_preference": "Germany / Remote EU",
        },
        projects=[
            {
                "name": "Local Portfolio Project",
                "technologies": ["C#", ".NET", "SQLite", "Git"],
                "description": "Desktop app with local database storage.",
            }
        ],
    )
    if "overall_score" not in score:
        raise RuntimeError("calculate_match_score_tool did not return overall_score.")

    masked = mask_personal_data_tool("Contact test@example.com with GOOGLE_API_KEY=abc123")
    if "test@example.com" in masked or "abc123" in masked:
        raise RuntimeError("mask_personal_data_tool did not mask sensitive values.")


def _agent_value(agent: Any, key: str) -> Any:
    if isinstance(agent, dict):
        return agent.get(key)
    return getattr(agent, key, None)


def _tool_names(agent: Any) -> set[str]:
    tools = _agent_value(agent, "tools") or []
    names: set[str] = set()
    for tool in tools:
        if isinstance(tool, str):
            names.add(tool)
            continue
        names.add(str(tool))
        for attr in ("__name__", "name"):
            value = getattr(tool, attr, None)
            if value:
                names.add(str(value))
        wrapped_func = getattr(tool, "func", None) or getattr(tool, "_func", None)
        if wrapped_func is not None and getattr(wrapped_func, "__name__", None):
            names.add(wrapped_func.__name__)
    return names


def _yes_no(value: bool) -> str:
    return "yes" if value else "no"


if __name__ == "__main__":
    raise SystemExit(main())
