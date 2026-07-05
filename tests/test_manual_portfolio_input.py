"""Tests for Streamlit UI helper functions."""

from app import (
    has_content,
    has_enhanced_section,
    normalize_manual_project_technologies,
    parse_manual_projects_json,
)


def test_parse_manual_projects_json_accepts_project_array() -> None:
    result = parse_manual_projects_json(
        """
        [
          {
            "name": "TaskBoard React Dashboard",
            "description": "React dashboard with REST API integration.",
            "technologies": "React, TypeScript, REST API, Git"
          }
        ]
        """
    )

    assert result["ok"] is True
    assert result["projects"][0]["name"] == "TaskBoard React Dashboard"
    assert result["projects"][0]["summary"] == "React dashboard with REST API integration."
    assert result["projects"][0]["technologies"] == ["React", "TypeScript", "REST API", "Git"]
    assert result["projects"][0]["source"] == "manual"


def test_parse_manual_projects_json_rejects_invalid_json() -> None:
    result = parse_manual_projects_json("[")

    assert result["ok"] is False
    assert "Invalid portfolio JSON" in result["error"]


def test_parse_manual_projects_json_requires_project_names() -> None:
    result = parse_manual_projects_json('[{"summary": "Missing name"}]')

    assert result["ok"] is False
    assert "missing a non-empty 'name'" in result["error"]


def test_normalize_manual_project_technologies_deduplicates_values() -> None:
    assert normalize_manual_project_technologies(["React", "react", " Git ", ""]) == ["React", "Git"]


def test_has_content_ignores_empty_nested_values() -> None:
    assert has_content({"summary": "", "items": []}) is False
    assert has_content({"summary": "Ready", "items": []}) is True
    assert has_content([{}, "", ["Next step"]]) is True


def test_has_enhanced_section_checks_expected_fields() -> None:
    assert has_enhanced_section({"summary": "Gemini plan"}, ("summary", "items")) is True
    assert has_enhanced_section({"unused": "value"}, ("summary", "items")) is False
    assert has_enhanced_section(None, ("summary",)) is False
