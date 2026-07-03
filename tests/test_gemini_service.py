"""Tests for the optional Gemini service wrapper."""

from devpath.core.config import AppConfig
from devpath.services.gemini_service import (
    build_structured_career_strategy_prompt,
    is_gemini_available,
    parse_gemini_structured_response,
)
from scripts.check_gemini_connection import main as gemini_smoke_main


def test_is_gemini_available_handles_missing_values() -> None:
    assert is_gemini_available(None) is False
    assert is_gemini_available("") is False
    assert is_gemini_available("   ") is False


def test_is_gemini_available_returns_true_for_non_empty_key() -> None:
    assert is_gemini_available("abc") is True


def test_build_structured_prompt_includes_score_rules_and_gaps() -> None:
    report = _sample_report()

    prompt = build_structured_career_strategy_prompt(report)

    assert "74" in prompt
    assert "ASP.NET Core" in prompt
    assert "Do not change the numeric match score" in prompt
    assert "Return valid JSON only" in prompt
    assert "Do not wrap JSON in Markdown" in prompt
    assert "prioritized gaps" in prompt.lower()


def test_parse_gemini_structured_response_parses_valid_json() -> None:
    response = """
    {
      "career_summary": "You are close to this role.",
      "top_actions": ["Build API", "Update README", "Practice English"],
      "portfolio_positioning": ["Lead with the API demo"],
      "skill_gap_strategy": ["Focus ASP.NET Core"],
      "interview_focus": ["REST APIs", "SQL", "Git"]
    }
    """

    parsed = parse_gemini_structured_response(response)

    assert parsed["career_summary"] == "You are close to this role."
    assert parsed["top_actions"] == ["Build API", "Update README", "Practice English"]
    assert parsed["interview_focus"] == ["REST APIs", "SQL", "Git"]
    assert parsed["raw_response"] == response


def test_parse_gemini_structured_response_handles_markdown_fences() -> None:
    response = """```json
{
  "career_summary": "Use the deterministic evidence.",
  "top_actions": ["Action"],
  "portfolio_positioning": ["Project evidence"],
  "skill_gap_strategy": ["Gap strategy"],
  "interview_focus": ["Interview focus"]
}
```"""

    parsed = parse_gemini_structured_response(response)

    assert parsed["career_summary"] == "Use the deterministic evidence."
    assert parsed["top_actions"] == ["Action"]


def test_parse_gemini_structured_response_returns_safe_fallback_for_invalid_json() -> None:
    response = "This is not JSON, but it is still useful narrative text."

    parsed = parse_gemini_structured_response(response)

    assert parsed["career_summary"] == response
    assert parsed["top_actions"] == []
    assert parsed["portfolio_positioning"] == []
    assert parsed["skill_gap_strategy"] == []
    assert parsed["interview_focus"] == []
    assert parsed["raw_response"] == response


def test_local_smoke_script_without_api_key_exits_cleanly(capsys) -> None:
    config = AppConfig(
        google_api_key=None,
        gemini_model="gemini-2.5-flash",
        gemini_enabled=False,
    )

    result = gemini_smoke_main(config=config)
    output = capsys.readouterr().out

    assert result == 0
    assert "Gemini API key is not configured" in output


def test_local_smoke_script_with_fake_key_uses_injected_generator(capsys) -> None:
    def fake_generator(report, api_key, model):
        assert report["profile_match"]["overall_score"] >= 0
        assert api_key == "fake-key"
        assert model == "gemini-2.5-flash"
        return {
            "career_summary": "Fake Gemini summary",
            "top_actions": ["First action", "Second action", "Third action"],
            "portfolio_positioning": [],
            "skill_gap_strategy": [],
            "interview_focus": [],
            "raw_response": "{}",
        }

    config = AppConfig(
        google_api_key="fake-key",
        gemini_model="gemini-2.5-flash",
        gemini_enabled=True,
    )

    result = gemini_smoke_main(config=config, summary_generator=fake_generator)
    output = capsys.readouterr().out

    assert result == 0
    assert "Gemini smoke test succeeded" in output
    assert "Fake Gemini summary" in output
    assert "1. First action" in output
    assert "fake-key" not in output


def _sample_report() -> dict:
    return {
        "profile_match": {
            "overall_score": 74,
            "category_scores": {"required_technical_skills": 28},
            "strong_matches": ["C#", ".NET"],
            "partial_matches": ["SQL: related evidence found through SQLite."],
            "missing_skills": ["ASP.NET Core"],
            "evidence_by_skill": {"C#": ["Profile skills", "Project: TaskFlow Desktop"]},
        },
        "skill_gaps": {
            "missing_skills": ["ASP.NET Core"],
            "prioritized_gaps": [
                {
                    "skill": "ASP.NET Core",
                    "priority": "High",
                    "recommendation": "Build a small ASP.NET Core REST API project.",
                }
            ],
        },
        "preparation_plan": {"7_day_plan": ["Review requirements."]},
    }
