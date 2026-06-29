"""Dataclass placeholder for the final career report produced by DevPath Agent."""

from dataclasses import dataclass, field


@dataclass
class CareerReport:
    """Structured representation of a candidate-job comparison report."""

    match_score: float = 0.0
    strengths: list[str] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    summary: str = ""
