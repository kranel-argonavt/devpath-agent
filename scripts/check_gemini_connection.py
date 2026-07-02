"""Local smoke test for optional Gemini-assisted summaries.

Run from the project root:
    python scripts/check_gemini_connection.py
"""

from collections.abc import Callable
from pathlib import Path
import sys
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from devpath.core.config import AppConfig, get_app_config
from devpath.core.report_builder import create_mock_report
from devpath.services.file_service import load_json_file, load_text_file
from devpath.services.gemini_service import generate_gemini_career_summary


def main(
    config: AppConfig | None = None,
    summary_generator: Callable[[dict[str, Any], str, str], str] | None = None,
) -> int:
    """Run a local Gemini smoke test without exposing secrets."""

    app_config = config or get_app_config()
    generator = summary_generator or generate_gemini_career_summary

    if not app_config.gemini_enabled or not app_config.google_api_key:
        print(
            "Gemini API key is not configured. Create a local .env file with "
            "GOOGLE_API_KEY or GEMINI_API_KEY."
        )
        print("Mock deterministic mode still works without a Gemini API key.")
        return 0

    print("Gemini API key detected. Running local Gemini smoke test.")
    print("Gemini is used only for narrative summary generation. Deterministic scoring remains the source of truth.")

    job_text = load_text_file(PROJECT_ROOT / "data" / "sample_job_posting.txt")
    profile = load_json_file(PROJECT_ROOT / "data" / "sample_profile.json")
    projects = load_json_file(PROJECT_ROOT / "data" / "sample_projects.json")

    if not isinstance(profile, dict):
        print("Sample profile JSON must contain an object.")
        return 1
    if not isinstance(projects, list):
        print("Sample projects JSON must contain a list.")
        return 1

    report = create_mock_report(
        job_text=job_text,
        profile=profile,
        projects=projects,
        output_style="Concise",
    )
    try:
        summary = generator(
            report=report,
            api_key=app_config.google_api_key,
            model=app_config.gemini_model,
        )
    except RuntimeError as exc:
        print(f"Gemini smoke test failed: {exc}")
        return 1

    print("Gemini smoke test succeeded.")
    print(f"Model: {app_config.gemini_model}")
    print("Summary preview:")
    print(summary[:800].strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
