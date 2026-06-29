"""Starter tests for markdown export placeholders."""

from pathlib import Path

from devpath.services.export_service import export_markdown_report


def test_export_markdown_report_writes_file(tmp_path: Path) -> None:
    output_path = tmp_path / "report.md"
    result = export_markdown_report("# Report", output_path)

    assert result == output_path
    assert output_path.read_text(encoding="utf-8") == "# Report"
