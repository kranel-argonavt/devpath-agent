"""MCP-style deterministic privacy tools."""

from devpath.agent_tools import mask_personal_data_tool


def mask_personal_data(text: str) -> str:
    """Mask email, phone, and API key-like secrets."""

    return mask_personal_data_tool(text)
