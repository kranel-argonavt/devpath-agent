"""Dataclass placeholder for a structured job posting analysis result."""

from dataclasses import dataclass, field


@dataclass
class JobPostingAnalysis:
    """Structured representation of extracted job requirements."""

    title: str = ""
    company: str = ""
    required_skills: list[str] = field(default_factory=list)
    preferred_skills: list[str] = field(default_factory=list)
    responsibilities: list[str] = field(default_factory=list)
    language_requirements: list[str] = field(default_factory=list)
