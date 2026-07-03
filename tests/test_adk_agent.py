"""Tests for the ADK-compatible agent skeleton."""

from importlib import import_module

import devpath.agent as root_module


SUB_AGENT_MODULES = [
    "devpath.sub_agents.job_analyzer",
    "devpath.sub_agents.portfolio_evidence",
    "devpath.sub_agents.profile_matcher",
    "devpath.sub_agents.gap_planner",
    "devpath.sub_agents.application_writer",
    "devpath.sub_agents.interview_coach",
    "devpath.sub_agents.privacy_guard",
]


def test_root_agent_is_exported() -> None:
    assert hasattr(root_module, "root_agent")
    assert root_module.root_agent is not None


def test_root_agent_name_identifies_devpath_root() -> None:
    name = _agent_value(root_module.root_agent, "name")

    assert name
    assert "devpath" in str(name).lower() or "root" in str(name).lower()


def test_root_agent_references_deterministic_tools() -> None:
    tools = _tool_names(root_module.root_agent)

    assert _has_tool(tools, "calculate_match_score_tool")
    assert _has_tool(tools, "build_mock_report_tool")
    assert _has_tool(tools, "mask_personal_data_tool")


def test_root_agent_instruction_preserves_deterministic_scores() -> None:
    instruction = str(_agent_value(root_module.root_agent, "instruction"))

    assert "deterministic scoring tools as the source of truth" in instruction
    assert "Do not invent or modify numeric match scores" in instruction


def test_sub_agent_factories_create_agents_without_api_key() -> None:
    for module_name in SUB_AGENT_MODULES:
        module = import_module(module_name)
        assert hasattr(module, "create_agent")

        sub_agent = module.create_agent()

        assert sub_agent is not None
        assert _agent_value(sub_agent, "name")
        assert _agent_value(sub_agent, "description")


def _agent_value(agent, key: str):
    if isinstance(agent, dict):
        return agent.get(key)
    return getattr(agent, key, None)


def _tool_names(agent) -> set[str]:
    tools = _agent_value(agent, "tools") or []
    names: set[str] = set()
    for tool in tools:
        if isinstance(tool, str):
            names.add(tool)
        else:
            names.add(str(tool))
            for attr in ("__name__", "name"):
                value = getattr(tool, attr, None)
                if value:
                    names.add(str(value))
            wrapped_func = getattr(tool, "func", None) or getattr(tool, "_func", None)
            if wrapped_func is not None and getattr(wrapped_func, "__name__", None):
                names.add(wrapped_func.__name__)
    return names


def _has_tool(tool_names: set[str], expected: str) -> bool:
    return expected in tool_names or any(expected in name for name in tool_names)
