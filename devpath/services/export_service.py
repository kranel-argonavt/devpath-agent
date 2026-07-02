"""Export helpers for saving reports to markdown deliverable formats."""

from datetime import datetime
from pathlib import Path
from typing import Any

from devpath.core.privacy import mask_personal_data


def export_markdown_report(
    report: dict[str, Any],
    output_dir: str | Path = "outputs",
    filename: str | None = None,
) -> str:
    """Export a report dictionary to a Markdown file and return the file path."""

    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    target_name = filename or f"devpath_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    if not target_name.endswith(".md"):
        target_name = f"{target_name}.md"

    target = target_dir / target_name
    target.write_text(_report_to_markdown(report), encoding="utf-8")
    return str(target)


def _report_to_markdown(report: dict[str, Any]) -> str:
    profile_match = report.get("profile_match", {})
    skill_gaps = report.get("skill_gaps", {})
    portfolio_evidence = report.get("portfolio_evidence", {})
    preparation_plan = report.get("preparation_plan", {})
    application_drafts = report.get("application_drafts", {})
    interview_prep = report.get("interview_prep", {})

    sections = [
        "# DevPath Agent Career Strategy Report",
        "",
        "## 1. Job Analysis",
        *_render_job_analysis(report.get("job_analysis", {})),
        "",
        "## 2. Profile Match",
        *_render_profile_match(profile_match, skill_gaps),
        "",
        "## 3. Evidence by Skill",
        *_render_evidence_by_skill(
            profile_match.get("evidence_by_skill") or portfolio_evidence.get("evidence_by_skill", {})
        ),
        "",
        "## 4. Prioritized Skill Gaps",
        *_render_prioritized_gaps(
            skill_gaps.get("prioritized_gaps") or profile_match.get("prioritized_gaps", []),
            skill_gaps.get("missing_skills") or profile_match.get("missing_skills", []),
        ),
        "",
        "## 5. Portfolio Evidence",
        *_render_portfolio_evidence(portfolio_evidence),
        "",
        "## 6. Preparation Plan",
        *_render_preparation_plan(preparation_plan),
        "",
        "## 7. Application Drafts",
        *_render_application_drafts(application_drafts),
        "",
        "## 8. Interview Prep",
        *_render_interview_prep(interview_prep),
        "",
        "## 9. Privacy Notice",
        str(report.get("privacy_notice", "Review personal details before exporting or sharing this report.")),
        "",
    ]
    return mask_personal_data("\n".join(sections).strip() + "\n")


def _render_job_analysis(job_analysis: dict[str, Any]) -> list[str]:
    lines = [
        f"**Target role:** {job_analysis.get('target_role', 'Unknown')}",
        f"**Detected focus:** {job_analysis.get('detected_focus', 'No job analysis available.')}",
        f"**Detected seniority:** {job_analysis.get('detected_seniority', 'Unknown')}",
        f"**Output style:** {job_analysis.get('output_style', 'Concise')}",
        f"**CV context provided:** {'Yes' if job_analysis.get('cv_context_provided') else 'No'}",
        "",
        "### Required Skills",
        *_render_bullets(job_analysis.get("required_skills", []), "No required skills detected."),
        "",
        "### Nice-To-Have Skills",
        *_render_bullets(job_analysis.get("nice_to_have_skills", []), "No nice-to-have skills detected."),
    ]
    if job_analysis.get("job_source_url"):
        lines.insert(2, f"**Source URL:** {job_analysis['job_source_url']}")
    return lines


def _render_profile_match(profile_match: dict[str, Any], skill_gaps: dict[str, Any]) -> list[str]:
    overall_score = profile_match.get("overall_score", 0)
    lines = [
        "### Overall Match Score",
        f"**Score:** {overall_score} / 100",
        "",
        str(profile_match.get("explanation", "No explanation available.")),
        "",
        "### Category Breakdown",
        *_render_category_breakdown(
            profile_match.get("category_details", {}),
            profile_match.get("category_scores", {}),
        ),
        "",
        "### Strong Matches",
        *_render_bullets(profile_match.get("strong_matches", []), "No strong matches detected yet."),
        "",
        "### Partial Matches",
        *_render_bullets(profile_match.get("partial_matches", []), "No partial matches detected yet."),
        "",
        "### Missing Skills",
        *_render_bullets(
            skill_gaps.get("missing_skills") or profile_match.get("missing_skills", []),
            "No missing skills detected.",
        ),
    ]
    return lines


def _render_category_breakdown(category_details: dict[str, Any], category_scores: dict[str, Any]) -> list[str]:
    if category_details:
        lines = ["| Category | Score | Max | Reason |", "|---|---:|---:|---|"]
        for key, detail in category_details.items():
            lines.append(
                "| "
                f"{_titleize(key)} | "
                f"{detail.get('earned', category_scores.get(key, 0))} | "
                f"{detail.get('max', '')} | "
                f"{_table_cell(detail.get('reason', 'No reason provided.'))} |"
            )
        return lines

    if category_scores:
        lines = ["| Category | Score |", "|---|---:|"]
        for key, value in category_scores.items():
            lines.append(f"| {_titleize(key)} | {value} |")
        return lines

    return ["No category scores available."]


def _render_evidence_by_skill(evidence_by_skill: dict[str, list[str]]) -> list[str]:
    if not evidence_by_skill:
        return ["No skill evidence available."]

    lines: list[str] = []
    for skill, sources in sorted(evidence_by_skill.items()):
        lines.append(f"### {skill}")
        lines.extend(_render_bullets(sources, "No evidence sources listed."))
        lines.append("")
    return _strip_trailing_blank(lines)


def _render_prioritized_gaps(prioritized_gaps: list[dict[str, Any]], missing_skills: list[str]) -> list[str]:
    if prioritized_gaps:
        lines: list[str] = []
        for gap in prioritized_gaps:
            priority = gap.get("priority", "Priority")
            skill = gap.get("skill", "Unknown skill")
            lines.extend(
                [
                    f"### {priority} Priority: {skill}",
                    "",
                    f"**Reason:** {gap.get('reason', 'No reason provided.')}",
                    "",
                    f"**Recommendation:** {gap.get('recommendation', 'No recommendation provided.')}",
                    "",
                ]
            )
        return _strip_trailing_blank(lines)

    if missing_skills:
        return [f"### Missing: {skill}" for skill in missing_skills]

    return ["No prioritized gaps detected."]


def _render_portfolio_evidence(portfolio_evidence: dict[str, Any]) -> list[str]:
    lines = [
        str(portfolio_evidence.get("summary", "No portfolio summary available.")),
        "",
        "### Projects To Highlight",
        *_render_bullets(portfolio_evidence.get("projects_to_highlight", []), "No highlighted projects available."),
        "",
        "### Suggested Evidence Points",
        *_render_bullets(portfolio_evidence.get("suggested_evidence_points", []), "No evidence points available."),
    ]

    project_sources = _project_only_evidence(portfolio_evidence.get("evidence_by_skill", {}))
    if project_sources:
        lines.extend(["", "### Portfolio Evidence Map", *_render_evidence_by_skill(project_sources)])
    return lines


def _render_preparation_plan(preparation_plan: dict[str, Any]) -> list[str]:
    return [
        "### 7-Day Plan",
        *_render_bullets(preparation_plan.get("7_day_plan", []), "No 7-day plan available."),
        "",
        "### 14-Day Plan",
        *_render_bullets(preparation_plan.get("14_day_plan", []), "No 14-day plan available."),
        "",
        "### 30-Day Roadmap",
        *_render_bullets(preparation_plan.get("30_day_roadmap", []), "No 30-day roadmap available."),
        "",
        "### Gap Recommendations",
        *_render_bullets(preparation_plan.get("gap_recommendations", []), "No gap recommendations available."),
    ]


def _render_application_drafts(application_drafts: dict[str, Any]) -> list[str]:
    return [
        "### Cover Letter Draft",
        str(application_drafts.get("cover_letter_draft", "No cover letter draft available.")),
        "",
        "### Recruiter Message Draft",
        str(application_drafts.get("recruiter_message_draft", "No recruiter message draft available.")),
    ]


def _render_interview_prep(interview_prep: dict[str, Any]) -> list[str]:
    lines = [
        "### Interview Questions",
        *_render_numbered(interview_prep.get("questions", []), "No interview questions available."),
        "",
        "### Practice Focus",
        *_render_bullets(interview_prep.get("practice_focus", []), "No practice focus available."),
    ]

    prioritized_gaps = interview_prep.get("prioritized_gaps", [])
    if prioritized_gaps:
        lines.extend(["", "### Gap-Focused Practice", *_render_prioritized_gaps(prioritized_gaps, [])])
    return lines


def _render_bullets(items: list[Any], empty_message: str) -> list[str]:
    if not items:
        return [f"- {empty_message}"]
    return [f"- {item}" for item in items]


def _render_numbered(items: list[Any], empty_message: str) -> list[str]:
    if not items:
        return [f"1. {empty_message}"]
    return [f"{index}. {item}" for index, item in enumerate(items, start=1)]


def _project_only_evidence(evidence_by_skill: dict[str, list[str]]) -> dict[str, list[str]]:
    project_evidence: dict[str, list[str]] = {}
    for skill, sources in evidence_by_skill.items():
        project_sources = [source for source in sources if str(source).startswith("Project: ")]
        if project_sources:
            project_evidence[skill] = project_sources
    return project_evidence


def _table_cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def _titleize(key: str) -> str:
    return key.replace("_", " ").title()


def _strip_trailing_blank(lines: list[str]) -> list[str]:
    while lines and lines[-1] == "":
        lines.pop()
    return lines
