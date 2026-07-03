"""MCP-style deterministic export tools."""

from pathlib import Path
from typing import Any

from devpath.services.export_service import export_markdown_report as _export_markdown_report


def export_markdown_report(
    report: dict[str, Any],
    output_dir: str | Path = "outputs",
    filename: str | None = None,
) -> str:
    """Export a privacy-masked Markdown report and return the file path."""

    return _export_markdown_report(report=report, output_dir=output_dir, filename=filename)
