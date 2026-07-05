"""Validation and application helpers for bounded Gemini enhancements."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from devpath.core.scoring import collect_profile_skills, collect_project_evidence, detect_skills_in_text


def validate_job_requirements(
    gemini_payload: Any,
    deterministic_requirements: dict[str, Any],
    target_role: str,
) -> dict[str, Any]:
    """Validate Gemini job extraction and fall back to deterministic requirements."""

    fallback = _job_fallback(deterministic_requirements, target_role)
    if not isinstance(gemini_payload, dict):
        fallback["source"] = "deterministic_fallback"
        fallback["warnings"].append("Gemini job extraction was unavailable or invalid.")
        return fallback

    required_skills = _normalize_skill_list(gemini_payload.get("required_skills", []))
    nice_to_have_skills = _normalize_skill_list(gemini_payload.get("nice_to_have_skills", []))
    if not required_skills and not nice_to_have_skills:
        fallback["source"] = "deterministic_fallback"
        fallback["warnings"].append("Gemini job extraction did not contain usable skills.")
        return fallback

    warnings = _string_list(gemini_payload.get("warnings", []))
    return {
        "role_title": _clean_string(gemini_payload.get("role_title")) or target_role or fallback["role_title"],
        "required_skills": required_skills,
        "nice_to_have_skills": nice_to_have_skills,
        "responsibilities": _string_list(gemini_payload.get("responsibilities", [])),
        "seniority": _clean_string(gemini_payload.get("seniority")) or fallback["seniority"],
        "languages": _normalize_skill_list(gemini_payload.get("languages", [])),
        "location_remote": _clean_string(gemini_payload.get("location_remote")),
        "hidden_expectations": _string_list(gemini_payload.get("hidden_expectations", [])),
        "confidence": _bounded_confidence(gemini_payload.get("confidence")),
        "warnings": warnings,
        "source": "gemini_validated",
    }


def validate_candidate_context(
    gemini_payload: Any,
    profile: dict[str, Any],
    projects: list[dict[str, Any]],
    portfolio_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate Gemini candidate extraction and fall back to deterministic profile/project signals."""

    fallback = build_deterministic_candidate_context(profile, projects, portfolio_summary)
    if not isinstance(gemini_payload, dict):
        fallback["source"] = "deterministic_fallback"
        fallback["warnings"].append("Gemini candidate extraction was unavailable or invalid.")
        return fallback

    candidate_skills = _normalize_skill_list(gemini_payload.get("candidate_skills", []))
    if not candidate_skills:
        fallback["source"] = "deterministic_fallback"
        fallback["warnings"].append("Gemini candidate extraction did not contain usable skills.")
        return fallback

    return {
        "candidate_skills": candidate_skills,
        "experience_signals": _string_list(gemini_payload.get("experience_signals", [])),
        "project_evidence_mentions": _string_list(gemini_payload.get("project_evidence_mentions", [])),
        "languages": _string_list(gemini_payload.get("languages", [])),
        "education_signals": _string_list(gemini_payload.get("education_signals", [])),
        "location_preferences": _string_list(gemini_payload.get("location_preferences", [])),
        "weak_or_unclear_areas": _string_list(gemini_payload.get("weak_or_unclear_areas", [])),
        "confidence": _bounded_confidence(gemini_payload.get("confidence")),
        "warnings": _string_list(gemini_payload.get("warnings", [])),
        "source": "gemini_validated",
    }


def build_deterministic_candidate_context(
    profile: dict[str, Any],
    projects: list[dict[str, Any]],
    portfolio_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build deterministic candidate context from profile and project metadata."""

    profile_skills = sorted(collect_profile_skills(profile))
    project_evidence = collect_project_evidence(projects)
    portfolio_skills = sorted(project_evidence)
    languages = _string_list(profile.get("languages", []))
    if isinstance(profile.get("languages"), str):
        languages = [str(profile.get("languages")).strip()]

    return {
        "candidate_skills": _dedupe(profile_skills + portfolio_skills),
        "experience_signals": _string_list(
            [
                profile.get("experience_level", ""),
                profile.get("experience", ""),
                profile.get("summary", ""),
            ]
        ),
        "project_evidence_mentions": _project_mentions(projects, portfolio_summary),
        "languages": languages,
        "education_signals": _string_list([profile.get("education", "")]),
        "location_preferences": _string_list([profile.get("location_preference", "")]),
        "weak_or_unclear_areas": [],
        "confidence": 0.7,
        "warnings": [],
        "source": "deterministic",
    }


def sanitize_gap_narrative(payload: Any, report: dict[str, Any]) -> dict[str, Any]:
    """Return safe Gemini gap narrative fields."""

    if not isinstance(payload, dict):
        return {}
    missing = set(report.get("profile_match", {}).get("missing_skills", []))
    allowed_skills = missing | {gap.get("skill", "") for gap in report.get("skill_gaps", {}).get("prioritized_gaps", [])}
    explanations = []
    for item in payload.get("gap_explanations", []):
        if not isinstance(item, dict):
            continue
        skill = _clean_string(item.get("skill"))
        if allowed_skills and skill and skill not in allowed_skills:
            continue
        explanations.append(
            {
                "skill": skill or "Portfolio positioning",
                "explanation": _clean_string(item.get("explanation")),
                "next_step": _clean_string(item.get("next_step")),
            }
        )
    return {
        "summary": _clean_string(payload.get("summary")),
        "gap_explanations": [item for item in explanations if item["explanation"] or item["next_step"]],
    }


def sanitize_action_plan(payload: Any) -> dict[str, Any]:
    """Return safe Gemini action-plan narrative fields."""

    if not isinstance(payload, dict):
        return {}
    return {
        "summary": _clean_string(payload.get("summary")),
        "7_day_plan": _string_list(payload.get("7_day_plan", [])),
        "14_day_plan": _string_list(payload.get("14_day_plan", [])),
        "30_day_roadmap": _string_list(payload.get("30_day_roadmap", [])),
        "portfolio_tasks": _string_list(payload.get("portfolio_tasks", [])),
        "study_tasks": _string_list(payload.get("study_tasks", [])),
        "interview_drills": _string_list(payload.get("interview_drills", [])),
        "done_criteria": _string_list(payload.get("done_criteria", [])),
    }


def sanitize_application_drafts(payload: Any) -> dict[str, Any]:
    """Return safe Gemini application draft narrative fields."""

    if not isinstance(payload, dict):
        return {}
    return {
        "cover_letter_draft": _clean_string(payload.get("cover_letter_draft")),
        "recruiter_message_draft": _clean_string(payload.get("recruiter_message_draft")),
        "cv_bullets": _string_list(payload.get("cv_bullets", [])),
        "project_positioning": _string_list(payload.get("project_positioning", [])),
        "what_to_emphasize": _string_list(payload.get("what_to_emphasize", [])),
        "what_to_avoid": _string_list(payload.get("what_to_avoid", [])),
        "application_checklist": _string_list(payload.get("application_checklist", [])),
    }


def sanitize_interview_prep(payload: Any) -> dict[str, Any]:
    """Return safe Gemini interview prep narrative fields."""

    if not isinstance(payload, dict):
        return {}
    return {
        "focus_summary": _clean_string(payload.get("focus_summary")),
        "questions": _string_list(payload.get("questions", [])),
        "practice_focus": _string_list(payload.get("practice_focus", [])),
        "technical_questions": _question_guides(payload.get("technical_questions", [])),
        "behavioral_questions": _question_guides(payload.get("behavioral_questions", [])),
        "project_story_prompts": _string_list(payload.get("project_story_prompts", [])),
        "weak_area_drills": _string_list(payload.get("weak_area_drills", [])),
        "answer_guidance": _string_list(payload.get("answer_guidance", [])),
    }


def apply_narrative_enhancements(report: dict[str, Any], enhancements: dict[str, dict[str, Any]]) -> None:
    """Attach LLM narrative enhancements without touching canonical score/evidence fields."""

    cleaned = {key: value for key, value in enhancements.items() if value}
    report["gemini_narrative_enhancements"] = deepcopy(cleaned)
    report["llm_enhanced_sections"] = deepcopy(cleaned)
    report["llm_score_modification"] = False

    gaps = cleaned.get("gaps")
    if gaps:
        report.setdefault("skill_gaps", {})["llm_gap_narrative"] = gaps

    action_plan = cleaned.get("action_plan")
    if action_plan:
        report.setdefault("preparation_plan", {})["llm_enhanced_plan"] = action_plan

    application = cleaned.get("application")
    if application:
        report.setdefault("application_drafts", {})["llm_enhanced_drafts"] = application

    interview = cleaned.get("interview")
    if interview:
        report.setdefault("interview_prep", {})["llm_enhanced_prep"] = interview


def _job_fallback(deterministic_requirements: dict[str, Any], target_role: str) -> dict[str, Any]:
    return {
        "role_title": target_role or "Unknown role",
        "required_skills": _normalize_skill_list(deterministic_requirements.get("required_skills", [])),
        "nice_to_have_skills": _normalize_skill_list(deterministic_requirements.get("nice_to_have_skills", [])),
        "responsibilities": _string_list(deterministic_requirements.get("responsibilities", [])),
        "seniority": _clean_string(deterministic_requirements.get("detected_seniority")) or "Unknown",
        "languages": _normalize_skill_list(deterministic_requirements.get("detected_languages", [])),
        "location_remote": "",
        "hidden_expectations": [],
        "confidence": 0.65,
        "warnings": [],
        "source": "deterministic",
    }


def _project_mentions(projects: list[dict[str, Any]], portfolio_summary: dict[str, Any] | None) -> list[str]:
    if portfolio_summary and isinstance(portfolio_summary.get("project_names"), list):
        return _string_list(portfolio_summary.get("project_names", []))
    return _string_list([project.get("name", "") for project in projects])


def _normalize_skill_list(value: Any) -> list[str]:
    detected: list[str] = []
    for item in _string_list(value):
        skill_matches = sorted(detect_skills_in_text(item))
        detected.extend(skill_matches or [item])
    return _dedupe(detected)


def _string_list(value: Any) -> list[str]:
    if isinstance(value, str):
        values = [value]
    elif isinstance(value, list | tuple | set):
        values = list(value)
    else:
        values = []
    return _dedupe([_clean_string(item) for item in values if _clean_string(item)])


def _question_guides(value: Any) -> list[dict[str, str]]:
    if not isinstance(value, list | tuple | set):
        return []
    guides: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in value:
        if isinstance(item, dict):
            question = _clean_string(item.get("question"))
            answer_focus = _clean_string(item.get("answer_focus"))
        else:
            question = _clean_string(item)
            answer_focus = ""
        if not question:
            continue
        key = question.lower()
        if key in seen:
            continue
        seen.add(key)
        guides.append({"question": question, "answer_focus": answer_focus})
    return guides


def _clean_string(value: Any) -> str:
    return str(value or "").strip()


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        key = value.lower()
        if key not in seen:
            seen.add(key)
            result.append(value)
    return result


def _bounded_confidence(value: Any) -> float:
    try:
        confidence = float(value)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(1.0, confidence))
