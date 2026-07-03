"""Tests for ADK-style wrappers that can call local MCP runtime tools."""

from __future__ import annotations

import importlib

import pytest

from devpath.adk_mcp_tools import (
    list_adk_mcp_tools,
    analyze_job_posting_via_mcp_tool,
    calculate_match_score_via_mcp_tool,
    mask_personal_data_via_mcp_tool,
)
from devpath.mcp_runtime import MCPRuntimeCallResult
from scripts.check_adk_mcp_tools import main as adk_mcp_smoke_main


def test_list_adk_mcp_tools_returns_expected_names() -> None:
    assert list_adk_mcp_tools() == [
        "mask_personal_data",
        "analyze_job_posting",
        "calculate_match_score",
    ]


def test_mask_personal_data_via_mcp_tool_uses_injected_runtime() -> None:
    def fake_runtime_caller(tool_name, arguments):
        assert tool_name == "mask_personal_data"
        assert arguments == {"text": "Contact test@example.com"}
        return MCPRuntimeCallResult(tool_name, "Contact [EMAIL_REDACTED]")

    result = mask_personal_data_via_mcp_tool(
        "Contact test@example.com",
        runtime_caller=fake_runtime_caller,
    )

    assert result == "Contact [EMAIL_REDACTED]"


def test_mask_personal_data_via_mcp_tool_unwraps_fastmcp_result_dict() -> None:
    def fake_runtime_caller(tool_name, arguments):
        return MCPRuntimeCallResult(tool_name, {"result": "Contact [EMAIL_REDACTED]"})

    result = mask_personal_data_via_mcp_tool(
        "Contact test@example.com",
        runtime_caller=fake_runtime_caller,
    )

    assert result == "Contact [EMAIL_REDACTED]"


def test_analyze_job_posting_via_mcp_tool_uses_injected_runtime() -> None:
    def fake_runtime_caller(tool_name, arguments):
        assert tool_name == "analyze_job_posting"
        assert "job_text" in arguments
        return MCPRuntimeCallResult(tool_name, {"required_skills": ["C#", ".NET"]})

    result = analyze_job_posting_via_mcp_tool(
        "Junior .NET role requiring C#.",
        runtime_caller=fake_runtime_caller,
    )

    assert result["required_skills"] == ["C#", ".NET"]


def test_calculate_match_score_via_mcp_tool_uses_injected_runtime() -> None:
    def fake_runtime_caller(tool_name, arguments):
        assert tool_name == "calculate_match_score"
        assert arguments["profile"]["skills"] == ["C#"]
        return MCPRuntimeCallResult(tool_name, {"overall_score": 76})

    result = calculate_match_score_via_mcp_tool(
        "Junior C# role.",
        {"skills": ["C#"]},
        [{"name": "Sample", "technologies": ["C#"]}],
        runtime_caller=fake_runtime_caller,
    )

    assert result["overall_score"] == 76


def test_wrappers_raise_clear_runtime_error_when_runtime_fails() -> None:
    def fake_runtime_caller(tool_name, arguments):
        raise RuntimeError("runtime unavailable")

    with pytest.raises(RuntimeError, match="ADK-MCP bridge failed while calling mask_personal_data"):
        mask_personal_data_via_mcp_tool("Contact test@example.com", runtime_caller=fake_runtime_caller)


def test_adk_mcp_smoke_script_with_fake_runtime_caller(capsys) -> None:
    def fake_runtime_caller(tool_name, arguments):
        if tool_name == "mask_personal_data":
            return MCPRuntimeCallResult(tool_name, "Contact [EMAIL_REDACTED] with GOOGLE_API_KEY=[REDACTED]")
        if tool_name == "analyze_job_posting":
            return MCPRuntimeCallResult(tool_name, {"required_skills": ["C#", ".NET"]})
        if tool_name == "calculate_match_score":
            return MCPRuntimeCallResult(tool_name, {"overall_score": 82})
        raise AssertionError(f"Unexpected tool call: {tool_name}")

    result = adk_mcp_smoke_main(runtime_caller=fake_runtime_caller)
    output = capsys.readouterr().out

    assert result == 0
    assert "DevPath ADK-MCP tool bridge smoke test" in output
    assert "ADK-MCP tool bridge smoke test succeeded" in output
    assert "test@example.com" not in output
    assert "abc123" not in output


def test_importing_adk_mcp_tools_and_agent_is_safe() -> None:
    adk_mcp_tools = importlib.import_module("devpath.adk_mcp_tools")
    agent = importlib.import_module("devpath.agent")

    assert hasattr(adk_mcp_tools, "list_adk_mcp_tools")
    assert hasattr(agent, "root_agent")
