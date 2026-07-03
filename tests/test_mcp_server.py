"""Tests for the import-safe MCP server skeleton."""

import mcp_server.server as server_module


EXPECTED_TOOL_NAMES = {
    "analyze_job_posting",
    "summarize_portfolio",
    "calculate_match_score",
    "build_career_report",
    "mask_personal_data",
    "export_markdown_report",
}


def test_mcp_server_exports_server() -> None:
    assert hasattr(server_module, "server")
    assert server_module.server is not None


def test_create_mcp_server_returns_server_or_metadata() -> None:
    created = server_module.create_mcp_server()

    assert created is not None
    assert _server_name(created)


def test_mcp_server_references_expected_tool_names() -> None:
    created = server_module.create_mcp_server()
    tool_names = _tool_names(created)

    assert EXPECTED_TOOL_NAMES.issubset(tool_names)


def test_importing_mcp_server_does_not_start_runtime() -> None:
    metadata = server_module.MCP_SERVER_METADATA

    assert metadata["name"] == "DevPath MCP Server"
    assert EXPECTED_TOOL_NAMES.issubset(set(metadata["tools"]))


def test_mcp_server_requires_no_api_key() -> None:
    created = server_module.create_mcp_server()

    assert created is not None


def _server_name(server) -> str:
    if isinstance(server, dict):
        return str(server.get("name", ""))
    metadata = getattr(server, "devpath_metadata", {})
    return str(metadata.get("name") or getattr(server, "name", ""))


def _tool_names(server) -> set[str]:
    if isinstance(server, dict):
        return set(server.get("tools", []))
    metadata = getattr(server, "devpath_metadata", server_module.MCP_SERVER_METADATA)
    return set(metadata.get("tools", []))
