"""Manual ADK-to-MCP bridge smoke test.

Run from the project root:
    python scripts/check_adk_mcp_tools.py
"""

from pathlib import Path
import sys
from typing import Any, Callable


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from devpath.adk_mcp_tools import (
    analyze_job_posting_via_mcp_tool,
    calculate_match_score_via_mcp_tool,
    mask_personal_data_via_mcp_tool,
)


RuntimeCaller = Callable[[str, dict[str, Any]], Any]


def main(runtime_caller: RuntimeCaller | None = None) -> int:
    """Run selected ADK-style wrappers through the local MCP runtime."""

    print("DevPath ADK-MCP tool bridge smoke test")
    print("This test calls selected ADK-style tool wrappers that route through the local MCP runtime.")

    try:
        masked = mask_personal_data_via_mcp_tool(
            "Contact test@example.com with GOOGLE_API_KEY=abc123",
            runtime_caller=runtime_caller,
        )
        if "test@example.com" in masked or "abc123" in masked:
            raise RuntimeError("mask_personal_data_via_mcp_tool did not mask sensitive values.")
        print("ADK-MCP tool bridge: mask_personal_data OK")

        job_analysis = analyze_job_posting_via_mcp_tool(_job_text(), runtime_caller=runtime_caller)
        if not isinstance(job_analysis, dict) or "required_skills" not in job_analysis:
            raise RuntimeError("analyze_job_posting_via_mcp_tool did not return requirement data.")
        print("ADK-MCP tool bridge: analyze_job_posting OK")

        score = calculate_match_score_via_mcp_tool(
            _job_text(),
            _profile(),
            _projects(),
            runtime_caller=runtime_caller,
        )
        if not isinstance(score, dict) or "overall_score" not in score:
            raise RuntimeError("calculate_match_score_via_mcp_tool did not return overall_score.")
        print("ADK-MCP tool bridge: calculate_match_score OK")

        print("ADK-MCP tool bridge smoke test succeeded.")
        return 0
    except Exception as exc:
        print(f"ADK-MCP tool bridge smoke test failed: {exc}")
        return 1


def _job_text() -> str:
    return "Junior .NET Developer role requiring C#, .NET, SQL, Git, REST API."


def _profile() -> dict[str, Any]:
    return {
        "name": "Sample Candidate",
        "skills": ["C#", ".NET", "SQL", "Git"],
        "languages": ["English"],
    }


def _projects() -> list[dict[str, Any]]:
    return [
        {
            "name": "Sample API Project",
            "description": "A REST API built with C# and .NET.",
            "technologies": ["C#", ".NET", "REST API", "SQL"],
        }
    ]


if __name__ == "__main__":
    raise SystemExit(main())
