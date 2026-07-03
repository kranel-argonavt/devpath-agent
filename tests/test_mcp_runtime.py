"""Tests for the MCP runtime adapter without starting a real MCP server."""

from devpath.mcp_runtime import MCPRuntimeCallResult, call_mcp_tool_stdio, extract_mcp_result_data
from scripts.check_mcp_runtime import main as mcp_runtime_smoke_main


def test_extract_mcp_result_data_handles_simple_values() -> None:
    assert extract_mcp_result_data({"ok": True}) == {"ok": True}
    assert extract_mcp_result_data(["a", "b"]) == ["a", "b"]
    assert extract_mcp_result_data("plain text") == "plain text"


def test_extract_mcp_result_data_handles_structured_content() -> None:
    class FakeResult:
        structured_content = {"score": 72}

    assert extract_mcp_result_data(FakeResult()) == {"score": 72}


def test_extract_mcp_result_data_handles_text_content_json() -> None:
    class FakeContent:
        text = '{"overall_score": 88}'

    class FakeResult:
        content = [FakeContent()]

    assert extract_mcp_result_data(FakeResult()) == {"overall_score": 88}


def test_extract_mcp_result_data_handles_text_content_plain_text() -> None:
    class FakeContent:
        text = "masked text"

    class FakeResult:
        content = [FakeContent()]

    assert extract_mcp_result_data(FakeResult()) == "masked text"


def test_call_mcp_tool_stdio_uses_async_adapter(monkeypatch) -> None:
    async def fake_async(tool_name, arguments, *, server_command=None, server_args=None):
        return MCPRuntimeCallResult(tool_name=tool_name, data={"arguments": arguments}, raw_result=None)

    monkeypatch.setattr("devpath.mcp_runtime.call_mcp_tool_stdio_async", fake_async)

    result = call_mcp_tool_stdio("sample_tool", {"value": 1})

    assert result.tool_name == "sample_tool"
    assert result.data == {"arguments": {"value": 1}}


def test_mcp_runtime_smoke_script_with_fake_runtime_caller(capsys) -> None:
    def fake_runtime_caller(tool_name, arguments):
        if tool_name == "mask_personal_data":
            return MCPRuntimeCallResult(tool_name, "Contact [EMAIL_REDACTED] with GOOGLE_API_KEY=[REDACTED]")
        if tool_name == "analyze_job_posting":
            return MCPRuntimeCallResult(tool_name, {"required_skills": ["C#", ".NET"]})
        if tool_name == "calculate_match_score":
            return MCPRuntimeCallResult(tool_name, {"overall_score": 80})
        raise AssertionError(f"Unexpected tool call: {tool_name}")

    result = mcp_runtime_smoke_main(runtime_caller=fake_runtime_caller)
    output = capsys.readouterr().out

    assert result == 0
    assert "DevPath MCP runtime smoke test" in output
    assert "MCP runtime smoke test succeeded" in output
    assert "test@example.com" not in output
    assert "abc123" not in output
