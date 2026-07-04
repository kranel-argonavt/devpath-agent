"""Manual full deterministic agent workflow smoke test."""

from pathlib import Path
import sys
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from devpath.full_agent_workflow import AGENT_STAGE_NAMES, FullAgentWorkflowInput, run_full_agent_workflow
from devpath.services.file_service import load_json_file, load_text_file


def main() -> int:
    """Run the deterministic full agent workflow against sample data."""

    print("DevPath full agent workflow smoke test")
    try:
        job_text = load_text_file(PROJECT_ROOT / "data" / "sample_job_posting.txt")
        profile = load_json_file(PROJECT_ROOT / "data" / "sample_profile.json")
        projects = load_json_file(PROJECT_ROOT / "data" / "sample_projects.json")
        if not isinstance(profile, dict) or not isinstance(projects, list):
            raise RuntimeError("Sample profile/projects are not in the expected shape.")

        result = run_full_agent_workflow(
            FullAgentWorkflowInput(
                job_text=job_text,
                profile=profile,
                projects=projects,
                target_role="Junior .NET Developer",
            )
        )
        _validate_result(result.report, result.agent_trace)
    except Exception as exc:
        print(f"Full agent workflow smoke test failed: {exc}")
        return 1

    for agent_name in AGENT_STAGE_NAMES:
        print(f"Agent stage: {agent_name} OK")
    print("Full agent workflow smoke test succeeded.")
    return 0


def _validate_result(report: dict[str, Any], trace: list[Any]) -> None:
    if "overall_score" not in report.get("profile_match", {}):
        raise RuntimeError("Report does not contain deterministic score.")
    workflow = report.get("agent_workflow", {})
    if workflow.get("scoring_source") != "deterministic":
        raise RuntimeError("Scoring source is not deterministic.")
    if workflow.get("llm_score_modification") is not False:
        raise RuntimeError("LLM score modification flag must be False.")
    trace_names = [step.agent_name for step in trace]
    if trace_names != AGENT_STAGE_NAMES:
        raise RuntimeError(f"Unexpected agent trace order: {trace_names}")


if __name__ == "__main__":
    raise SystemExit(main())
