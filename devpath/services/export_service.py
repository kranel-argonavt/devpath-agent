"""Future export helpers for saving reports to markdown or other deliverable formats."""

from pathlib import Path


def export_markdown_report(content: str, output_path: str | Path) -> Path:
    """Write markdown content to disk as a simple local export placeholder."""

    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return target
