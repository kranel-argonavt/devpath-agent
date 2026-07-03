"""MCP-compatible server skeleton for exposing deterministic DevPath tools."""

from typing import Any

from mcp_server.tools import MCP_TOOL_REGISTRY, list_mcp_tools

try:  # pragma: no cover - exercised only when the optional SDK is installed.
    from mcp.server.fastmcp import FastMCP
except ImportError:  # pragma: no cover - fallback metadata is covered by tests.
    FastMCP = None  # type: ignore[assignment]


SERVER_NAME = "DevPath MCP Server"
SERVER_DESCRIPTION = (
    "Import-safe MCP skeleton exposing deterministic DevPath scoring, report, privacy, "
    "portfolio, and export tool contracts."
)

MCP_SERVER_METADATA = {
    "name": SERVER_NAME,
    "description": SERVER_DESCRIPTION,
    "tools": list_mcp_tools(),
}


def create_mcp_server() -> Any:
    """Create a FastMCP server if available, otherwise return fallback metadata."""

    if FastMCP is None:
        return dict(MCP_SERVER_METADATA)

    try:
        mcp_server = FastMCP(SERVER_NAME)
        for tool in MCP_TOOL_REGISTRY.values():
            mcp_server.tool()(tool)
        _attach_metadata(mcp_server)
        return mcp_server
    except Exception:
        return dict(MCP_SERVER_METADATA)


def _attach_metadata(mcp_server: Any) -> None:
    try:
        setattr(mcp_server, "devpath_metadata", dict(MCP_SERVER_METADATA))
    except Exception:
        # Some SDK objects may block dynamic attributes; metadata remains available
        # through MCP_SERVER_METADATA for local validation.
        return


server = create_mcp_server()
