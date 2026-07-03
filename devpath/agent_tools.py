"""Deterministic tool wrappers for future Google ADK orchestration."""

from typing import Any

from devpath.core.privacy import mask_personal_data
from devpath.core.report_builder import create_mock_report
from devpath.core.scoring import (
    calculate_mock_match_score,
    collect_project_evidence,
    extract_job_requirements,
)


def analyze_job_posting_tool(job_text: str) -> dict[str, Any]:
    """Extract deterministic job requirements from a job posting."""

    return extract_job_requirements(job_text)


def summarize_portfolio_tool(projects: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarize portfolio projects and detected evidence."""

    evidence_by_skill = collect_project_evidence(projects)
    project_names = [str(project.get("name") or f"Project {index + 1}") for index, project in enumerate(projects)]
    return {
        "project_count": len(projects),
        "project_names": project_names,
        "evidence_by_skill": evidence_by_skill,
        "summary": (
            "Deterministic portfolio summary based on project fields. "
            f"Detected evidence for {len(evidence_by_skill)} skill area(s)."
        ),
    }


def calculate_match_score_tool(
    job_text: str,
    profile: dict[str, Any],
    projects: list[dict[str, Any]],
) -> dict[str, Any]:
    """Return deterministic match scoring output."""

    return calculate_mock_match_score(job_text=job_text, profile=profile, projects=projects)


def build_mock_report_tool(
    job_text: str,
    profile: dict[str, Any],
    projects: list[dict[str, Any]],
    cv_text: str = "",
    output_style: str = "Concise",
) -> dict[str, Any]:
    """Build the deterministic career strategy report."""

    return create_mock_report(
        job_text=job_text,
        profile=profile,
        projects=projects,
        cv_text=cv_text,
        output_style=output_style,
    )


def mask_personal_data_tool(text: str) -> str:
    """Mask sensitive personal data."""

    return mask_personal_data(text)
