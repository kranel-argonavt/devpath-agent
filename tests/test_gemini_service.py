"""Tests for the optional Gemini service wrapper."""

from devpath.services.gemini_service import build_career_strategy_prompt, is_gemini_available


def test_is_gemini_available_handles_missing_values() -> None:
    assert is_gemini_available(None) is False
    assert is_gemini_available("") is False
    assert is_gemini_available("   ") is False


def test_is_gemini_available_returns_true_for_non_empty_key() -> None:
    assert is_gemini_available("abc") is True


def test_build_career_strategy_prompt_includes_deterministic_score_and_gaps() -> None:
    report = {
        "profile_match": {
            "overall_score": 74,
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

    prompt = build_career_strategy_prompt(report)

    assert "74" in prompt
    assert "ASP.NET Core" in prompt
    assert "Do not change the numeric match score" in prompt
    assert "deterministic score as the source of truth" in prompt
