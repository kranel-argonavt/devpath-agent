"""Adapter for selected local MCP runtime tool calls over stdio."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
import json
import sys
from typing import Any


DEFAULT_MCP_SERVER_ARGS = ("-m", "mcp_server.server")


@dataclass(frozen=True)
class MCPRuntimeCallResult:
    """Result returned after calling a tool through MCP runtime."""

    tool_name: str
    data: Any
    raw_result: Any | None = None


async def call_mcp_tool_stdio_async(
    tool_name: str,
    arguments: dict[str, Any],
    *,
    server_command: str | None = None,
    server_args: list[str] | None = None,
) -> MCPRuntimeCallResult:
    """Call a local MCP tool through a stdio server process."""

    command = server_command or sys.executable
    args = server_args or list(DEFAULT_MCP_SERVER_ARGS)

    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
    except ImportError as exc:
        raise RuntimeError("MCP client runtime is not available. Install dependencies with pip install -r requirements.txt.") from exc

    try:
        server_params = StdioServerParameters(command=command, args=args)
        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                raw_result = await session.call_tool(tool_name, arguments)
                return MCPRuntimeCallResult(
                    tool_name=tool_name,
                    data=extract_mcp_result_data(raw_result),
                    raw_result=raw_result,
                )
    except Exception as exc:
        raise RuntimeError(f"MCP stdio tool call failed for {tool_name}: {exc}") from exc


def call_mcp_tool_stdio(
    tool_name: str,
    arguments: dict[str, Any],
    *,
    server_command: str | None = None,
    server_args: list[str] | None = None,
) -> MCPRuntimeCallResult:
    """Synchronously call a local MCP tool through a stdio server process."""

    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(
            call_mcp_tool_stdio_async(
                tool_name,
                arguments,
                server_command=server_command,
                server_args=server_args,
            )
        )
    raise RuntimeError("call_mcp_tool_stdio cannot run inside an active event loop; use call_mcp_tool_stdio_async instead.")


def extract_mcp_result_data(raw_result: Any) -> Any:
    """Extract Python/JSON data from common MCP result shapes."""

    if raw_result is None or isinstance(raw_result, int | float | bool | dict):
        return raw_result

    if isinstance(raw_result, str):
        return _parse_json_if_possible(raw_result)

    if isinstance(raw_result, list):
        if all(_is_plain_value(item) for item in raw_result):
            return raw_result
        return [_extract_content_item(item) for item in raw_result]

    for attr in ("structured_content", "structuredContent"):
        value = getattr(raw_result, attr, None)
        if value is not None:
            return value

    content = getattr(raw_result, "content", None)
    if content is not None:
        extracted = [_extract_content_item(item) for item in content]
        extracted = [item for item in extracted if item is not None]
        if len(extracted) == 1:
            return extracted[0]
        return extracted

    if hasattr(raw_result, "model_dump"):
        try:
            return raw_result.model_dump()
        except Exception:
            pass

    if hasattr(raw_result, "dict"):
        try:
            return raw_result.dict()
        except Exception:
            pass

    return repr(raw_result)


def _extract_content_item(item: Any) -> Any:
    if item is None or isinstance(item, int | float | bool | dict):
        return item

    if isinstance(item, str):
        return _parse_json_if_possible(item)

    if isinstance(item, list):
        if all(_is_plain_value(value) for value in item):
            return item
        return [_extract_content_item(value) for value in item]

    text = getattr(item, "text", None)
    if text is not None:
        return _parse_json_if_possible(text)

    for attr in ("data", "resource", "contents"):
        value = getattr(item, attr, None)
        if value is not None:
            return value

    if hasattr(item, "model_dump"):
        try:
            return item.model_dump()
        except Exception:
            pass

    return repr(item)


def _is_plain_value(value: Any) -> bool:
    return value is None or isinstance(value, str | int | float | bool | list | dict)


def _parse_json_if_possible(value: str) -> Any:
    stripped = value.strip()
    if not stripped:
        return stripped
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        return value
