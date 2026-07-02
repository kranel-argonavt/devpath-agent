"""Optional Gemini service wrapper for narrative assistance."""

from typing import Any


def is_gemini_available(api_key: str | None) -> bool:
    """Return True if a non-empty Gemini API key is available."""

    return bool(api_key and api_key.strip())


def build_career_strategy_prompt(report: dict[str, Any]) -> str:
    """Build a safe prompt from the deterministic report for Gemini-assisted narrative improvement."""

    profile_match = report.get("profile_match", {})
    skill_gaps = report.get("skill_gaps", {})
    preparation_plan = report.get("preparation_plan", {})

    return "\n".join(
        [
            "You are helping improve a career strategy report for a junior software developer.",
            "Use the deterministic report as the source of truth.",
            "Do not change the numeric match score. Use the deterministic score as the source of truth.",
            "",
            f"Overall score: {profile_match.get('overall_score', 'Unknown')} / 100",
            f"Strong matches: {profile_match.get('strong_matches', [])}",
            f"Partial matches: {profile_match.get('partial_matches', [])}",
            f"Missing skills: {skill_gaps.get('missing_skills') or profile_match.get('missing_skills', [])}",
            f"Prioritized gaps: {skill_gaps.get('prioritized_gaps') or profile_match.get('prioritized_gaps', [])}",
            f"Evidence by skill: {profile_match.get('evidence_by_skill', {})}",
            f"Preparation plan: {preparation_plan}",
            "",
            "Produce:",
            "1. A concise career strategy summary.",
            "2. The top 3 actions before applying.",
            "3. How to position the strongest project evidence.",
            "4. What to improve before applying.",
        ]
    )


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


def generate_gemini_career_summary(report: dict[str, Any], api_key: str, model: str) -> str:
    """Generate an optional Gemini-assisted summary based on deterministic scoring output."""

    prompt = build_career_strategy_prompt(report)
    return generate_gemini_text(prompt=prompt, api_key=api_key, model=model)
