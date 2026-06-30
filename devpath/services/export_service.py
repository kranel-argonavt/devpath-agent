"""Export helpers for saving reports to markdown deliverable formats."""

from datetime import datetime
from pathlib import Path
from typing import Any

from devpath.core.privacy import mask_personal_data


def export_markdown_report(
    report: dict[str, Any],
    output_dir: str | Path = "outputs",
    filename: str | None = None,
) -> str:
    """Export a report dictionary to a Markdown file and return the file path."""

    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    target_name = filename or f"devpath_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    if not target_name.endswith(".md"):
        target_name = f"{target_name}.md"

    target = target_dir / target_name
    target.write_text(_report_to_markdown(report), encoding="utf-8")
    return str(target)


def _report_to_markdown(report: dict[str, Any]) -> str:
    sections = ["# DevPath Agent Career Strategy Report", ""]
    for key, value in report.items():
        sections.append(f"## {_titleize(key)}")
        sections.append("")
        sections.extend(_render_value(value))
        sections.append("")
    return mask_personal_data("\n".join(sections).strip() + "\n")


def _render_value(value: Any) -> list[str]:
    if isinstance(value, dict):
        lines: list[str] = []
        for key, nested_value in value.items():
            lines.append(f"### {_titleize(key)}")
            lines.extend(_render_value(nested_value))
            lines.append("")
        return lines
    if isinstance(value, list):
        if not value:
            return ["- None"]
        return [f"- {item}" for item in value]
    return [str(value)]


def _titleize(key: str) -> str:
    return key.replace("_", " ").title()
