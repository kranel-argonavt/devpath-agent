"""Starter tests for deterministic scoring placeholders."""

from devpath.core.scoring import calculate_skill_overlap


def test_calculate_skill_overlap_returns_expected_ratio() -> None:
    score = calculate_skill_overlap(
        candidate_skills=["C#", ".NET", "Git"],
        required_skills=["C#", ".NET", "SQL", "Git"],
    )

    assert score == 0.75
