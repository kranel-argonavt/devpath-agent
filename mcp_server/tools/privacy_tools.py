"""MCP-style deterministic privacy tools."""

from devpath.core.privacy import detect_sensitive_data as _detect_sensitive_data
from devpath.agent_tools import mask_personal_data_tool


def mask_personal_data(text: str) -> str:
    """Mask email, phone, and API key-like secrets."""

    return mask_personal_data_tool(text)


def detect_sensitive_data(text: str) -> dict[str, object]:
    """Detect supported sensitive data patterns without returning raw matches."""

    return _detect_sensitive_data(text)
