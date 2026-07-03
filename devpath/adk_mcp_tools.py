"""ADK-style wrappers for selected DevPath MCP runtime tools.

These wrappers are an experimental bridge for future ADK orchestration. They
call selected deterministic MCP tools through the local stdio runtime only when
the wrapper function is invoked.
"""

from __future__ import annotations

from typing import Any, Callable

from devpath.mcp_runtime import MCPRuntimeCallResult, call_mcp_tool_stdio


ADK_MCP_TOOL_NAMES = [
    "mask_personal_data",
    "analyze_job_posting",
    "calculate_match_score",
]

RuntimeCaller = Callable[..., Any]


def list_adk_mcp_tools() -> list[str]:
    """Return stable MCP tool names exposed through ADK-style wrappers."""

    return list(ADK_MCP_TOOL_NAMES)


def mask_personal_data_via_mcp_tool(
    text: str,
    *,
    runtime_caller: RuntimeCaller | None = None,
) -> str:
    """Mask sensitive text by calling the local MCP runtime privacy tool."""

    data = _call_runtime_tool(
        "mask_personal_data",
        {"text": text},
        runtime_caller=runtime_caller,
    )
    if isinstance(data, dict) and set(data) == {"result"}:
        data = data["result"]
    if not isinstance(data, str):
        raise RuntimeError("MCP tool mask_personal_data returned an unexpected result shape.")
    return data


def analyze_job_posting_via_mcp_tool(
    job_text: str,
    *,
    runtime_caller: RuntimeCaller | None = None,
) -> dict[str, Any]:
    """Analyze a job posting by calling the local MCP runtime scoring tool."""

    data = _call_runtime_tool(
        "analyze_job_posting",
        {"job_text": job_text},
        runtime_caller=runtime_caller,
    )
    if not isinstance(data, dict):
        raise RuntimeError("MCP tool analyze_job_posting returned an unexpected result shape.")
    return data


def calculate_match_score_via_mcp_tool(
    job_text: str,
    profile: dict[str, Any],
    projects: list[dict[str, Any]],
    *,
    runtime_caller: RuntimeCaller | None = None,
) -> dict[str, Any]:
    """Calculate deterministic match score through the local MCP runtime."""

    data = _call_runtime_tool(
        "calculate_match_score",
        {"job_text": job_text, "profile": profile, "projects": projects},
        runtime_caller=runtime_caller,
    )
    if not isinstance(data, dict):
        raise RuntimeError("MCP tool calculate_match_score returned an unexpected result shape.")
    return data


def _call_runtime_tool(
    tool_name: str,
    arguments: dict[str, Any],
    *,
    runtime_caller: RuntimeCaller | None,
) -> Any:
    caller = runtime_caller or call_mcp_tool_stdio
    try:
        result = caller(tool_name, arguments)
    except Exception as exc:
        raise RuntimeError(f"ADK-MCP bridge failed while calling {tool_name}: {exc}") from exc

    if isinstance(result, MCPRuntimeCallResult):
        return result.data

    if hasattr(result, "data"):
        return result.data

    return result
