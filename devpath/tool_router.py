"""Local tool backend router for deterministic report generation."""

from typing import Any

from devpath.agent_tools import build_mock_report_tool


DIRECT_BACKEND = "Direct Python services"
MCP_STYLE_BACKEND = "Local MCP-style tools"


def list_tool_backends() -> list[str]:
    """Return supported local tool backend names."""

    return [DIRECT_BACKEND, MCP_STYLE_BACKEND]


def normalize_tool_backend(value: str | None) -> str:
    """Normalize an optional backend name to a supported backend."""

    if value in list_tool_backends():
        return str(value)
    return DIRECT_BACKEND


def build_report_with_backend(
    job_text: str,
    profile: dict[str, Any],
    projects: list[dict[str, Any]],
    cv_text: str = "",
    output_style: str = "Concise",
    tool_backend: str = DIRECT_BACKEND,
) -> dict[str, Any]:
    """Build a deterministic career report using the selected local backend."""

    backend = normalize_tool_backend(tool_backend)
    if backend == MCP_STYLE_BACKEND:
        return _build_report_with_mcp_style_tools(
            job_text=job_text,
            profile=profile,
            projects=projects,
            cv_text=cv_text,
            output_style=output_style,
        )

    return build_mock_report_tool(
        job_text=job_text,
        profile=profile,
        projects=projects,
        cv_text=cv_text,
        output_style=output_style,
    )


def _build_report_with_mcp_style_tools(
    job_text: str,
    profile: dict[str, Any],
    projects: list[dict[str, Any]],
    cv_text: str,
    output_style: str,
) -> dict[str, Any]:
    try:
        from mcp_server.tools import MCP_TOOL_REGISTRY

        tool = MCP_TOOL_REGISTRY["build_career_report"]
        return tool(
            job_text=job_text,
            profile=profile,
            projects=projects,
            cv_text=cv_text,
            output_style=output_style,
        )
    except Exception as exc:
        raise RuntimeError("Local MCP-style tools could not build the deterministic report.") from exc
