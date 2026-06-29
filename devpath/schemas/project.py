"""Dataclass placeholder for a portfolio project used as candidate evidence."""

from dataclasses import dataclass, field


@dataclass
class Project:
    """Structured representation of a portfolio project."""

    name: str = ""
    summary: str = ""
    technologies: list[str] = field(default_factory=list)
    highlights: list[str] = field(default_factory=list)
    repository_url: str = ""
