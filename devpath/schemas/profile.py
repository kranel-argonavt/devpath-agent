"""Dataclass placeholder for a candidate profile used across the DevPath workflow."""

from dataclasses import dataclass, field


@dataclass
class CandidateProfile:
    """Structured representation of a candidate's profile and preferences."""

    target_roles: list[str] = field(default_factory=list)
    experience_level: str = ""
    skills: list[str] = field(default_factory=list)
    languages: list[str] = field(default_factory=list)
    education: str = ""
    location_preference: str = ""
