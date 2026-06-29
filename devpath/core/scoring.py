"""Future deterministic match scoring logic for comparing profiles and job requirements."""

from collections.abc import Iterable


def calculate_skill_overlap(candidate_skills: Iterable[str], required_skills: Iterable[str]) -> float:
    """Return a simple normalized overlap score between 0.0 and 1.0."""

    candidate = {skill.strip().lower() for skill in candidate_skills if skill and skill.strip()}
    required = {skill.strip().lower() for skill in required_skills if skill and skill.strip()}
    if not required:
        return 0.0
    return round(len(candidate & required) / len(required), 2)
