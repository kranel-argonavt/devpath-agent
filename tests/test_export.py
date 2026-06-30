"""Tests for markdown report export helpers."""

from pathlib import Path

from devpath.services.export_service import export_markdown_report


def test_export_markdown_report_writes_markdown_file(tmp_path: Path) -> None:
    report = {
        "job_analysis": {"target_role": "Junior .NET Developer"},
        "profile_match": {"overall_score": 72},
        "privacy_notice": "Contact test@example.com before sharing.",
    }

    result = export_markdown_report(report, output_dir=tmp_path, filename="career_report")
    output_path = Path(result)
    content = output_path.read_text(encoding="utf-8")

    assert output_path.exists()
    assert result.endswith(".md")
    assert "# DevPath Agent Career Strategy Report" in content
    assert "## Job Analysis" in content
    assert "## Profile Match" in content
    assert "[EMAIL_REDACTED]" in content
