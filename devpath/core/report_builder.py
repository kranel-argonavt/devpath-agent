"""Report assembly helpers for mock career strategy outputs."""

from typing import Any

from devpath.core.scoring import calculate_mock_match_score


def create_mock_report(
    job_text: str,
    profile: dict[str, Any],
    projects: list[dict[str, Any]],
    cv_text: str = "",
    output_style: str = "Concise",
) -> dict[str, Any]:
    """Create a structured mock career strategy report."""

    score = calculate_mock_match_score(job_text, profile, projects)
    target_roles = profile.get("target_roles", [])
    primary_role = target_roles[0] if target_roles else "Junior Developer"
    project_names = [project.get("name", "Portfolio project") for project in projects]
    missing_skills = score["missing_skills"]
    prioritized_gaps = score.get("prioritized_gaps", [])
    gap_recommendations = [gap["recommendation"] for gap in prioritized_gaps[:3]]
    job_requirements = score.get("job_requirements", {})

    return {
        "job_analysis": {
            "target_role": _first_line(job_text),
            "detected_focus": _detected_focus(job_requirements),
            "required_skills": job_requirements.get("required_skills", []),
            "nice_to_have_skills": job_requirements.get("nice_to_have_skills", []),
            "detected_seniority": job_requirements.get("detected_seniority", "Unknown"),
            "detected_languages": job_requirements.get("detected_languages", []),
            "output_style": output_style,
            "cv_context_provided": bool(cv_text.strip()),
        },
        "gemini_summary": "",
        "profile_match": {
            "target_candidate_role": primary_role,
            "overall_score": score["overall_score"],
            "category_scores": score["category_scores"],
            "category_details": score.get("category_details", {}),
            "strong_matches": score["strong_matches"],
            "partial_matches": score["partial_matches"],
            "missing_skills": missing_skills,
            "evidence_by_skill": score.get("evidence_by_skill", {}),
            "prioritized_gaps": prioritized_gaps,
            "explanation": score["explanation"],
        },
        "portfolio_evidence": {
            "summary": "Portfolio evidence is strongest where projects show C#, .NET, database work, version control, or API concepts.",
            "projects_to_highlight": project_names[:3],
            "suggested_evidence_points": _portfolio_points(projects),
            "evidence_by_skill": score.get("evidence_by_skill", {}),
            "github_evidence": score.get("github_evidence", []),
        },
        "skill_gaps": {
            "missing_skills": missing_skills,
            "priority": missing_skills[:3],
            "prioritized_gaps": prioritized_gaps,
            "recommendations": gap_recommendations,
            "message": _gap_message(missing_skills),
        },
        "preparation_plan": {
            "7_day_plan": [
                "Review the job posting and map each requirement to profile or project evidence.",
                "Refresh C#, .NET, Git, SQL, and REST API basics with short notes.",
                "Prepare one portfolio story for each strong match.",
            ],
            "14_day_plan": [
                "Build or polish a small ASP.NET Core endpoint if backend evidence is weak.",
                "Add concise README sections that explain technologies, responsibilities, and outcomes.",
                "Practice explaining project tradeoffs in English.",
            ],
            "30_day_roadmap": [
                "Create a focused backend portfolio improvement project.",
                "Add tests or validation logic to one existing project.",
                "Prepare a reusable interview answer bank for junior .NET roles.",
            ],
            "gap_recommendations": gap_recommendations,
        },
        "application_drafts": {
            "cover_letter_draft": (
                f"Dear Hiring Team,\n\nI am applying for the {primary_role} opportunity because my background "
                "in C#, .NET, Git, and software engineering projects aligns with the junior developer profile. "
                "My portfolio shows hands-on practice with desktop, backend, and database concepts, and I am "
                "motivated to grow in a collaborative engineering team.\n\nKind regards"
            ),
            "recruiter_message_draft": (
                f"Hello, I am interested in the junior .NET role. I have practical C#/.NET experience, "
                f"portfolio projects such as {', '.join(project_names[:2])}, and I am looking for a junior "
                "developer opportunity in Germany or remote within the EU."
            ),
        },
        "interview_prep": {
            "questions": [
                "How would you explain the difference between C# and .NET?",
                "How have you used Git in your projects?",
                "What is a REST API, and how would you design a simple endpoint?",
                "How would you model and query data in SQL?",
                "Which portfolio project best proves you are ready for this role?",
            ],
            "practice_focus": missing_skills[:3] or ["C# fundamentals", ".NET project explanation", "Git workflow"],
            "prioritized_gaps": prioritized_gaps,
        },
        "privacy_notice": (
            "This mock report is generated locally from provided sample data. Review personal details before exporting "
            "or sharing any generated content."
        ),
    }


def _first_line(text: str) -> str:
    return next((line.strip() for line in text.splitlines() if line.strip()), "Unknown role")


def _portfolio_points(projects: list[dict[str, Any]]) -> list[str]:
    points: list[str] = []
    for project in projects[:3]:
        name = project.get("name", "Portfolio project")
        technologies = ", ".join(project.get("technologies", []))
        if technologies:
            points.append(f"{name}: evidence of {technologies}.")
        else:
            points.append(f"{name}: add clearer technology and outcome evidence.")
    return points


def _gap_message(missing_skills: list[str]) -> str:
    if not missing_skills:
        return "No major required keyword gaps were detected in the mock analysis."
    return "Focus first on the missing required keywords that appear in the job posting."


def _detected_focus(job_requirements: dict[str, Any]) -> str:
    required = job_requirements.get("required_skills", [])
    seniority = job_requirements.get("detected_seniority", "Unknown")
    if required:
        return f"{seniority} role with detected requirements: {', '.join(required)}."
    return f"{seniority} role with no structured required skills detected by the mock scorer."
