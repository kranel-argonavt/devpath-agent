"""Tests for markdown report export helpers."""

from pathlib import Path

from devpath.services.export_service import export_markdown_report


def test_export_markdown_report_writes_rich_markdown_file(tmp_path: Path) -> None:
    report = {
        "job_analysis": {
            "target_role": "Junior .NET Developer",
            "detected_focus": "Junior role with detected requirements: C#, .NET.",
            "required_skills": ["C#", ".NET"],
            "nice_to_have_skills": ["Docker"],
            "output_style": "Concise",
        },
        "profile_match": {
            "overall_score": 74,
            "category_scores": {"required_technical_skills": 28},
            "category_details": {
                "required_technical_skills": {
                    "earned": 28,
                    "max": 35,
                    "reason": "Matched C# and .NET. Missing ASP.NET Core.",
                }
            },
            "strong_matches": ["C#", ".NET"],
            "partial_matches": ["SQL: related evidence found through SQLite."],
            "missing_skills": ["ASP.NET Core"],
            "evidence_by_skill": {
                "C#": ["Profile skills", "Project: TaskFlow Desktop"],
                ".NET": ["Profile skills", "Project: Student API Demo"],
            },
            "prioritized_gaps": [
                {
                    "skill": "ASP.NET Core",
                    "priority": "High",
                    "reason": "Required by the job posting but not found in profile or project evidence.",
                    "recommendation": "Build a small ASP.NET Core REST API project and add it to the portfolio.",
                }
            ],
            "explanation": "Deterministic score based on local evidence.",
        },
        "portfolio_evidence": {
            "summary": "Portfolio evidence summary.",
            "projects_to_highlight": ["TaskFlow Desktop"],
            "suggested_evidence_points": ["TaskFlow Desktop: evidence of C#."],
            "evidence_by_skill": {"C#": ["Profile skills", "Project: TaskFlow Desktop"]},
            "github_evidence": [
                {
                    "project_name": "Student API",
                    "project_url": "https://github.com/example/student-api",
                    "source": "github",
                    "matched_skills": ["C#", "REST API"],
                    "language": "C#",
                    "topics": ["dotnet", "api"],
                    "description_matches": ["REST API"],
                    "signals": {
                        "stars": 5,
                        "forks": 1,
                        "recently_updated": True,
                        "archived": False,
                        "fork": False,
                    },
                    "evidence_notes": [
                        "Primary language is C#.",
                        "Topic contains api.",
                        "Repository is public and non-archived.",
                    ],
                }
            ],
        },
        "skill_gaps": {
            "missing_skills": ["ASP.NET Core"],
            "prioritized_gaps": [
                {
                    "skill": "ASP.NET Core",
                    "priority": "High",
                    "reason": "Required by the job posting but not found in profile or project evidence.",
                    "recommendation": "Build a small ASP.NET Core REST API project and add it to the portfolio.",
                }
            ],
        },
        "preparation_plan": {
            "7_day_plan": ["Review requirements."],
            "14_day_plan": ["Build a small API."],
            "30_day_roadmap": ["Polish the portfolio."],
        },
        "application_drafts": {
            "cover_letter_draft": "Contact me at test@example.com.",
            "recruiter_message_draft": "GOOGLE_API_KEY=abc123",
        },
        "interview_prep": {"questions": ["What is .NET?"], "practice_focus": ["ASP.NET Core"]},
        "runtime_route": {
            "tool_backend": "Direct Python services",
            "requested_tool_backend": "Experimental ADK-MCP runtime tools",
            "mcp_runtime_used": False,
            "experimental": True,
            "fallback_used": True,
            "selected_tools": [],
            "notes": [
                "Experimental ADK-MCP runtime tools could not be used.",
                "Fell back to direct deterministic services.",
            ],
        },
        "agent_workflow": {
            "enabled": True,
            "orchestration": "Full ADK-style deterministic agent workflow",
            "agents": ["privacy_guard", "job_analyzer", "profile_matcher"],
            "scoring_source": "deterministic",
            "llm_score_modification": False,
        },
        "agent_trace": [
            {
                "agent_name": "privacy_guard",
                "status": "completed",
                "summary": "Masked sensitive context before analysis.",
                "tools_used": ["mask_personal_data"],
                "warnings": [],
            },
            {
                "agent_name": "profile_matcher",
                "status": "completed",
                "summary": "Calculated deterministic match score.",
                "tools_used": ["calculate_match_score", "create_mock_report"],
                "warnings": [],
            },
        ],
        "gemini_insights": {
            "career_summary": "Optional Gemini-assisted narrative summary.",
            "top_actions": ["Apply with API evidence", "Update README", "Practice interviews"],
            "portfolio_positioning": ["Lead with TaskFlow Desktop."],
            "skill_gap_strategy": ["Build ASP.NET Core evidence."],
            "interview_focus": ["REST API design"],
            "raw_response": "{}",
        },
        "privacy_notice": "Review personal details before sharing.",
    }

    result = export_markdown_report(report, output_dir=tmp_path, filename="career_report")
    output_path = Path(result)
    content = output_path.read_text(encoding="utf-8")

    assert output_path.exists()
    assert result.endswith(".md")
    assert "# DevPath Agent Career Strategy Report" in content
    assert "## Workflow Runtime" in content
    assert "- Requested backend: Experimental ADK-MCP runtime tools" in content
    assert "- Backend used: Direct Python services" in content
    assert "- Fallback used: Yes" in content
    assert "## Agent Workflow Trace" in content
    assert "- Agent: privacy_guard" in content
    assert "- Agent: profile_matcher" in content
    assert "## Agent Workflow Metadata" in content
    assert "- Scoring source: deterministic" in content
    assert "- LLM score modification: Disabled" in content
    assert "### Overall Match Score" in content
    assert "### Category Breakdown" in content
    assert "## 3. Evidence by Skill" in content
    assert "## 4. Prioritized Skill Gaps" in content
    assert "## 9. Privacy Notice" in content
    assert "## Gemini-assisted Career Strategy" in content
    assert "### AI Career Strategy Summary" in content
    assert "Optional Gemini-assisted narrative summary." in content
    assert "Apply with API evidence" in content
    assert "| Required Technical Skills | 28 | 35 |" in content
    assert "Project: TaskFlow Desktop" in content
    assert "### GitHub Repository Evidence" in content
    assert "https://github.com/example/student-api" in content
    assert "Language: C#" in content
    assert "Topics: dotnet, api" in content
    assert "High Priority: ASP.NET Core" in content
    assert "[EMAIL_REDACTED]" in content
    assert "GOOGLE_API_KEY=[REDACTED]" in content
    assert "test@example.com" not in content
    assert "GOOGLE_API_KEY=abc123" not in content
