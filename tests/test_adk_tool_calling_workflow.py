"""Tests for the visible ADK/Gemini tool-calling workflow."""

from devpath.adk_tool_calling_workflow import (
    MCP_STYLE_REGISTRY_BACKEND,
    ToolCallingWorkflowInput,
    run_adk_tool_calling_workflow,
)
from devpath.core.config import AppConfig


def test_tool_calling_workflow_builds_report_with_trace() -> None:
    result = run_adk_tool_calling_workflow(
        _workflow_input(),
        config=AppConfig(google_api_key=None, gemini_model="gemini-2.5-flash", gemini_enabled=False),
        runtime_caller=_failing_runtime,
    )

    assert result.report["profile_match"]["overall_score"] >= 0
    assert result.report["tool_call_trace"]
    assert result.report["agent_workflow"]["orchestration"] == "Gemini/ADK tool-calling agent workflow"
    assert result.report["runtime_route"]["fallback_used"] is True


def test_tool_calling_trace_contains_mcp_style_fallback_steps() -> None:
    result = run_adk_tool_calling_workflow(
        _workflow_input(),
        config=AppConfig(google_api_key=None, gemini_model="gemini-2.5-flash", gemini_enabled=False),
        runtime_caller=_failing_runtime,
    )

    trace = result.report["tool_call_trace"]
    tool_names = [step["tool_name"] for step in trace]
    assert "mask_personal_data" in tool_names
    assert "analyze_job_posting" in tool_names
    assert "build_portfolio_summary" in tool_names
    assert "calculate_match_score" in tool_names
    assert "build_career_report" in tool_names
    assert "extract_job_requirements_with_gemini" in tool_names
    assert "validate_job_requirements" in tool_names
    assert "extract_candidate_context_with_gemini" in tool_names
    assert "validate_candidate_context" in tool_names
    assert "generate_gap_narrative" in tool_names
    assert "generate_action_plan_narrative" in tool_names
    assert "generate_application_drafts" in tool_names
    assert "generate_interview_prep" in tool_names
    assert any(step["backend_used"] == MCP_STYLE_REGISTRY_BACKEND for step in trace)


def test_tool_calling_skips_gemini_without_api_key() -> None:
    result = run_adk_tool_calling_workflow(
        _workflow_input(),
        config=AppConfig(google_api_key=None, gemini_model="gemini-2.5-flash", gemini_enabled=False),
        runtime_caller=_failing_runtime,
    )

    gemini_step = result.report["tool_call_trace"][-1]
    assert gemini_step["tool_name"] == "generate_gemini_career_insights"
    assert gemini_step["status"] == "skipped"
    assert result.mode_used == "Mock deterministic mode"
    assert result.warnings == [
        "Gemini API key is not configured. Tool-calling workflow continued with deterministic report."
    ]


def test_gemini_cannot_modify_deterministic_score_fields() -> None:
    def mutating_generator(report, api_key, model):
        report["profile_match"]["overall_score"] = 1
        return {"career_summary": "Narrative only."}

    result = run_adk_tool_calling_workflow(
        _workflow_input(),
        config=AppConfig(google_api_key="fake-key", gemini_model="gemini-2.5-flash", gemini_enabled=True),
        runtime_caller=_failing_runtime,
        gemini_generator=mutating_generator,
    )

    assert result.mode_used == "Gemini-assisted summary"
    assert result.report["profile_match"]["overall_score"] != 1
    assert result.report["gemini_insights"]["career_summary"] == "Narrative only."


def test_gemini_structured_extraction_and_writers_attach_enhancements() -> None:
    result = run_adk_tool_calling_workflow(
        _workflow_input(),
        config=AppConfig(google_api_key="fake-key", gemini_model="gemini-2.5-flash", gemini_enabled=True),
        runtime_caller=_failing_runtime,
        gemini_tool_generator=_fake_gemini_tool_generator,
        gemini_generator=lambda report, api_key, model: {"career_summary": "Final narrative."},
    )

    extracted = result.report["gemini_extracted_context"]
    assert extracted["job_requirements"]["source"] == "gemini_validated"
    assert extracted["candidate_context"]["source"] == "gemini_validated"
    assert result.report["skill_gaps"]["llm_gap_narrative"]["summary"] == "Focus on production API evidence."
    assert result.report["preparation_plan"]["llm_enhanced_plan"]["7_day_plan"]
    assert result.report["preparation_plan"]["llm_enhanced_plan"]["done_criteria"]
    assert result.report["application_drafts"]["llm_enhanced_drafts"]["cv_bullets"]
    assert result.report["application_drafts"]["llm_enhanced_drafts"]["project_positioning"]
    assert result.report["interview_prep"]["llm_enhanced_prep"]["questions"]
    assert result.report["interview_prep"]["llm_enhanced_prep"]["technical_questions"][0]["answer_focus"]
    assert result.report["gemini_insights"]["career_summary"]


def test_final_gemini_summary_is_not_called_when_writer_outputs_exist() -> None:
    def fail_if_called(report, api_key, model):
        raise AssertionError("Final Gemini summary should be synthesized from writer outputs.")

    result = run_adk_tool_calling_workflow(
        _workflow_input(),
        config=AppConfig(google_api_key="fake-key", gemini_model="gemini-2.5-flash", gemini_enabled=True),
        runtime_caller=_failing_runtime,
        gemini_tool_generator=_fake_gemini_tool_generator,
        gemini_generator=fail_if_called,
    )

    final_step = result.report["tool_call_trace"][-1]
    assert final_step["tool_name"] == "generate_gemini_career_insights"
    assert final_step["backend_used"] == "Local synthesis"
    assert final_step["status"] == "completed"
    assert result.mode_used == "Gemini-assisted summary"
    assert not result.warnings


def test_invalid_gemini_extraction_falls_back_to_deterministic_context() -> None:
    def invalid_generator(tool_name, payload, api_key, model):
        if tool_name.startswith("extract_"):
            return {"raw_response": "not-json", "warnings": ["Invalid JSON"]}
        return _fake_gemini_tool_generator(tool_name, payload, api_key, model)

    result = run_adk_tool_calling_workflow(
        _workflow_input(),
        config=AppConfig(google_api_key="fake-key", gemini_model="gemini-2.5-flash", gemini_enabled=True),
        runtime_caller=_failing_runtime,
        gemini_tool_generator=invalid_generator,
        gemini_generator=lambda report, api_key, model: {"career_summary": "Final narrative."},
    )

    extracted = result.report["gemini_extracted_context"]
    assert extracted["job_requirements"]["source"] == "deterministic_fallback"
    assert extracted["candidate_context"]["source"] == "deterministic_fallback"
    validator_steps = [
        step for step in result.report["tool_call_trace"] if step["tool_name"] in {"validate_job_requirements", "validate_candidate_context"}
    ]
    assert all(step["fallback_used"] for step in validator_steps)


def test_gemini_step_trace_includes_safe_error_detail() -> None:
    def failing_generator(tool_name, payload, api_key, model):
        raise RuntimeError("429 RESOURCE_EXHAUSTED quota exceeded")

    result = run_adk_tool_calling_workflow(
        _workflow_input(),
        config=AppConfig(google_api_key="fake-key", gemini_model="gemini-2.5-flash", gemini_enabled=True),
        runtime_caller=_failing_runtime,
        gemini_tool_generator=failing_generator,
        gemini_generator=lambda report, api_key, model: {
            "career_summary": "Fallback summary.",
            "top_actions": ["Polish the API README."],
            "portfolio_positioning": ["Lead with the Backend API project."],
            "skill_gap_strategy": ["Clarify Docker evidence."],
            "interview_focus": ["REST API design"],
        },
    )

    failed_step = next(step for step in result.report["tool_call_trace"] if step["tool_name"] == "extract_job_requirements_with_gemini")
    assert "429 RESOURCE_EXHAUSTED" in failed_step["warnings"][0]
    assert result.report["preparation_plan"]["llm_enhanced_plan"]["7_day_plan"] == ["Polish the API README."]
    assert result.report["interview_prep"]["llm_enhanced_prep"]["practice_focus"] == ["REST API design"]


def test_narrative_writers_cannot_mutate_deterministic_score_fields() -> None:
    result = run_adk_tool_calling_workflow(
        _workflow_input(),
        config=AppConfig(google_api_key="fake-key", gemini_model="gemini-2.5-flash", gemini_enabled=True),
        runtime_caller=_failing_runtime,
        gemini_tool_generator=_fake_gemini_tool_generator,
        gemini_generator=lambda report, api_key, model: {"career_summary": "Final narrative."},
    )

    snapshot = result.report["canonical_profile_match_snapshot"]
    for field, value in snapshot.items():
        assert result.report["profile_match"][field] == value
    assert result.report["llm_score_modification"] is False


def test_tool_calling_trace_does_not_include_raw_sensitive_inputs() -> None:
    result = run_adk_tool_calling_workflow(
        ToolCallingWorkflowInput(
            job_text="Junior Python role requiring Python and Git. Contact hr@example.com.",
            profile={"experience_level": "Junior", "skills": ["Python", "Git"], "languages": ["English"]},
            projects=[],
            cv_text="GOOGLE_API_KEY=abc123",
        ),
        config=AppConfig(google_api_key=None, gemini_model="gemini-2.5-flash", gemini_enabled=False),
        runtime_caller=_failing_runtime,
    )

    trace_text = str(result.report["tool_call_trace"])
    assert "hr@example.com" not in trace_text
    assert "GOOGLE_API_KEY=abc123" not in trace_text
    assert "job_text" in trace_text
    assert "cv_text" in trace_text


def _workflow_input() -> ToolCallingWorkflowInput:
    return ToolCallingWorkflowInput(
        job_text="Junior Python Backend Developer requiring Python, SQL, Git, REST API, and English.",
        profile={
            "experience_level": "Junior",
            "skills": ["Python", "SQL", "Git", "REST API"],
            "languages": ["English B2"],
            "education": "Software Engineering",
            "location_preference": "Remote EU",
        },
        projects=[
            {
                "name": "Backend API",
                "summary": "Python REST API with SQL persistence and Git workflow.",
                "technologies": ["Python", "SQL", "Git", "REST API"],
            }
        ],
        target_role="Junior Python Developer",
    )


def _failing_runtime(tool_name: str, arguments: dict) -> object:
    raise RuntimeError("Simulated MCP runtime outage")


def _fake_gemini_tool_generator(tool_name: str, payload: dict, api_key: str, model: str) -> dict:
    if tool_name == "extract_job_requirements_with_gemini":
        return {
            "role_title": "Junior Python Backend Developer",
            "required_skills": ["Python", "SQL", "Git", "REST API", "English"],
            "nice_to_have_skills": ["Docker"],
            "responsibilities": ["Build API features"],
            "seniority": "Junior",
            "languages": ["English"],
            "location_remote": "Remote EU",
            "hidden_expectations": ["Explain project tradeoffs"],
            "confidence": 0.9,
            "warnings": [],
        }
    if tool_name == "extract_candidate_context_with_gemini":
        return {
            "candidate_skills": ["Python", "SQL", "Git", "REST API", "English"],
            "experience_signals": ["Junior portfolio backend API"],
            "project_evidence_mentions": ["Backend API"],
            "languages": ["English B2"],
            "education_signals": ["Software Engineering"],
            "location_preferences": ["Remote EU"],
            "weak_or_unclear_areas": ["Docker production usage"],
            "confidence": 0.88,
            "warnings": [],
        }
    if tool_name == "generate_gap_narrative":
        return {
            "summary": "Focus on production API evidence.",
            "gap_explanations": [
                {
                    "skill": "Docker",
                    "explanation": "Docker is useful for repeatable backend demos.",
                    "next_step": "Containerize the API and document the workflow.",
                }
            ],
        }
    if tool_name == "generate_action_plan_narrative":
        return {
            "summary": "Use the first week to make evidence visible.",
            "7_day_plan": ["Add API endpoint examples to the README."],
            "14_day_plan": ["Add Docker notes and a small test suite."],
            "30_day_roadmap": ["Publish a polished backend case study."],
            "portfolio_tasks": ["Add request and response examples to the Backend API README."],
            "study_tasks": ["Review Python API error handling and SQL query basics."],
            "interview_drills": ["Practice a two-minute walkthrough of the API architecture."],
            "done_criteria": ["README shows setup, endpoint examples, and one project tradeoff."],
        }
    if tool_name == "generate_application_drafts":
        return {
            "cover_letter_draft": "Dear Hiring Team, I can connect Python API evidence to your junior backend needs.",
            "recruiter_message_draft": "Hello, I have Python REST API portfolio evidence for this role.",
            "cv_bullets": ["Built a Python REST API with SQL persistence and Git workflow."],
            "project_positioning": ["Lead with Backend API as proof of Python, SQL, Git, and REST API experience."],
            "what_to_emphasize": ["Mention concrete endpoint behavior and database persistence."],
            "what_to_avoid": ["Do not claim production Docker experience unless the repository shows it."],
            "application_checklist": ["Check that the README link is visible before sending the application."],
        }
    if tool_name == "generate_interview_prep":
        return {
            "focus_summary": "Prepare concise backend API stories.",
            "questions": ["How did you design your API endpoints?"],
            "practice_focus": ["REST API tradeoffs", "SQL persistence story"],
            "technical_questions": [
                {
                    "question": "How would you design pagination for a REST endpoint?",
                    "answer_focus": "Explain request parameters, validation, SQL limits, and response metadata.",
                }
            ],
            "behavioral_questions": [
                {
                    "question": "Tell me about a time you improved a project after feedback.",
                    "answer_focus": "Use the Backend API README or testing improvements as the story evidence.",
                }
            ],
            "project_story_prompts": ["Walk through Backend API from user problem to endpoint implementation."],
            "weak_area_drills": ["Explain what Docker would add to the current API demo."],
            "answer_guidance": ["Use concrete project evidence first, then name what you would improve next."],
        }
    return {}
