"""Optional Gemini service wrapper for narrative assistance."""

import json
import re
from typing import Any


EMPTY_GEMINI_INSIGHTS = {
    "career_summary": "",
    "top_actions": [],
    "portfolio_positioning": [],
    "skill_gap_strategy": [],
    "interview_focus": [],
    "raw_response": "",
}


def is_gemini_available(api_key: str | None) -> bool:
    """Return True if a non-empty Gemini API key is available."""

    return bool(api_key and api_key.strip())


def build_career_strategy_prompt(report: dict[str, Any]) -> str:
    """Build a backward-compatible prompt for Gemini-assisted narrative improvement."""

    return build_structured_career_strategy_prompt(report)


def build_structured_career_strategy_prompt(report: dict[str, Any]) -> str:
    """Build a strict JSON prompt from deterministic career strategy data."""

    profile_match = report.get("profile_match", {})
    skill_gaps = report.get("skill_gaps", {})
    preparation_plan = report.get("preparation_plan", {})

    return "\n".join(
        [
            "You are improving the narrative explanation of a deterministic career strategy report.",
            "",
            "The deterministic report is the source of truth.",
            "",
            "Do not change, recalculate, reinterpret, or invent:",
            "- numeric match score",
            "- category scores",
            "- strong matches",
            "- partial matches",
            "- missing skills",
            "- prioritized gaps",
            "- evidence by skill",
            "",
            "Only summarize and explain the provided data.",
            "Do not change the numeric match score. Use the deterministic score as the source of truth.",
            "Return valid JSON only.",
            "Do not wrap JSON in Markdown.",
            "Do not add commentary before or after JSON.",
            "",
            "If there are no missing skills or prioritized gaps, say the user should focus on polishing evidence "
            "and interview stories rather than inventing fake gaps.",
            "If there are missing skills, explain only those gaps that exist in the deterministic report.",
            "Keep the output concise.",
            "",
            "Required JSON output format:",
            "{",
            '  "career_summary": "2-4 concise sentences",',
            '  "top_actions": ["action 1", "action 2", "action 3"],',
            '  "portfolio_positioning": ["how to present project evidence 1", "how to present project evidence 2"],',
            '  "skill_gap_strategy": ["gap strategy 1", "gap strategy 2"],',
            '  "interview_focus": ["interview focus 1", "interview focus 2", "interview focus 3"]',
            "}",
            "",
            "Deterministic report data:",
            f"Overall score: {profile_match.get('overall_score', 'Unknown')} / 100",
            f"Category scores: {profile_match.get('category_scores', {})}",
            f"Strong matches: {profile_match.get('strong_matches', [])}",
            f"Partial matches: {profile_match.get('partial_matches', [])}",
            f"Missing skills: {skill_gaps.get('missing_skills') or profile_match.get('missing_skills', [])}",
            f"Prioritized gaps: {skill_gaps.get('prioritized_gaps') or profile_match.get('prioritized_gaps', [])}",
            f"Evidence by skill: {profile_match.get('evidence_by_skill', {})}",
            f"Preparation plan: {preparation_plan}",
        ]
    )


def parse_gemini_structured_response(response_text: str) -> dict[str, Any]:
    """Parse Gemini JSON output into a safe structured insights dictionary."""

    raw_response = response_text or ""
    cleaned = _strip_json_fences(raw_response.strip())
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        fallback = dict(EMPTY_GEMINI_INSIGHTS)
        fallback["career_summary"] = raw_response.strip()
        fallback["raw_response"] = raw_response
        return fallback

    if not isinstance(parsed, dict):
        fallback = dict(EMPTY_GEMINI_INSIGHTS)
        fallback["career_summary"] = raw_response.strip()
        fallback["raw_response"] = raw_response
        return fallback

    insights = dict(EMPTY_GEMINI_INSIGHTS)
    insights["career_summary"] = str(parsed.get("career_summary", "")).strip()
    insights["top_actions"] = _as_string_list(parsed.get("top_actions", []))
    insights["portfolio_positioning"] = _as_string_list(parsed.get("portfolio_positioning", []))
    insights["skill_gap_strategy"] = _as_string_list(parsed.get("skill_gap_strategy", []))
    insights["interview_focus"] = _as_string_list(parsed.get("interview_focus", []))
    insights["raw_response"] = raw_response
    return insights


def generate_gemini_text(prompt: str, api_key: str, model: str) -> str:
    """Generate text using Gemini. This function should be isolated and easy to mock in tests."""

    if not is_gemini_available(api_key):
        raise RuntimeError("Gemini API key is not configured.")

    try:
        from google import genai

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(model=model, contents=prompt)
    except Exception as exc:  # pragma: no cover - real network/API path is not used in tests.
        raise RuntimeError(f"Gemini request failed: {exc}") from exc

    text = getattr(response, "text", None)
    if not text:
        raise RuntimeError("Gemini returned an empty response.")
    return text


def generate_gemini_career_insights(
    report: dict[str, Any],
    api_key: str,
    model: str,
) -> dict[str, Any]:
    """Generate optional structured Gemini insights from deterministic scoring output."""

    prompt = build_structured_career_strategy_prompt(report)
    response_text = generate_gemini_text(prompt=prompt, api_key=api_key, model=model)
    return parse_gemini_structured_response(response_text)


def generate_gemini_career_summary(report: dict[str, Any], api_key: str, model: str) -> str:
    """Generate an optional Gemini-assisted summary based on deterministic scoring output."""

    insights = generate_gemini_career_insights(report=report, api_key=api_key, model=model)
    return insights.get("career_summary") or insights.get("raw_response", "")


def _strip_json_fences(text: str) -> str:
    fenced = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", text, flags=re.DOTALL | re.IGNORECASE)
    if fenced:
        return fenced.group(1).strip()
    return text


def _as_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]
