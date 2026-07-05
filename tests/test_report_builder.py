"""Tests for deterministic report assembly helpers."""

from devpath.core.report_builder import create_mock_report


def test_frontend_report_fallback_copy_is_role_aware() -> None:
    report = create_mock_report(
        job_text=(
            "Junior Frontend Developer requiring React, TypeScript, JavaScript, HTML, CSS, Git, REST API, "
            "and English. Nice to have: Docker and Unit Testing."
        ),
        profile={
            "target_roles": ["Junior Frontend React Developer"],
            "experience_level": "Junior",
            "skills": ["React", "TypeScript", "JavaScript", "HTML", "CSS", "Git", "REST API"],
            "languages": ["English B2"],
        },
        projects=[
            {
                "name": "TaskBoard React Dashboard",
                "summary": "React dashboard with REST API integration.",
                "technologies": ["React", "TypeScript", "JavaScript", "HTML", "CSS", "REST API", "Git"],
            }
        ],
    )

    assert "React" in report["job_analysis"]["required_skills"]
    assert "Portfolio evidence is strongest where projects show React" in report["portfolio_evidence"]["summary"]
    assert "Refresh React" in report["preparation_plan"]["7_day_plan"][1]
    assert "frontend project area" in report["preparation_plan"]["14_day_plan"][0]
    assert "C#/.NET" not in report["application_drafts"]["recruiter_message_draft"]
    assert "C#, .NET" not in report["application_drafts"]["cover_letter_draft"]
    assert report["interview_prep"]["questions"][0] == "How do you structure reusable React components?"
