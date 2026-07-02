"""Tests for the optional Gemini service wrapper."""

from devpath.core.config import AppConfig
from devpath.services.gemini_service import build_career_strategy_prompt, is_gemini_available
from scripts.check_gemini_connection import main as gemini_smoke_main


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
    assert "Prioritized gaps" in prompt
    assert "Do not change the numeric match score" in prompt
    assert "deterministic score as the source of truth" in prompt


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
        return "Fake Gemini summary"

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
    assert "fake-key" not in output
