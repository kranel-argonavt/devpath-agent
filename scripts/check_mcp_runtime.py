"""Manual local MCP runtime smoke test.

Run from the project root:
    python scripts/check_mcp_runtime.py
"""

from pathlib import Path
import sys
from typing import Any, Callable


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from devpath.mcp_runtime import MCPRuntimeCallResult, call_mcp_tool_stdio


RuntimeCaller = Callable[[str, dict[str, Any]], MCPRuntimeCallResult]


def main(runtime_caller: RuntimeCaller | None = None) -> int:
    """Run selected deterministic tools through local MCP stdio runtime."""

    print("DevPath MCP runtime smoke test")
    print("This test starts a local MCP stdio server process and calls selected deterministic tools through MCP runtime.")
    caller = runtime_caller or call_mcp_tool_stdio

    try:
        masked = caller(
            "mask_personal_data",
            {"text": "Contact test@example.com with GOOGLE_API_KEY=abc123"},
        ).data
        if "test@example.com" in str(masked) or "abc123" in str(masked):
            raise RuntimeError("mask_personal_data did not mask sensitive values.")
        print("MCP runtime tool call: mask_personal_data OK")

        job_analysis = caller("analyze_job_posting", {"job_text": _job_text()}).data
        if not _has_key(job_analysis, "required_skills"):
            raise RuntimeError("analyze_job_posting did not return requirement data.")
        print("MCP runtime tool call: analyze_job_posting OK")

        score = caller(
            "calculate_match_score",
            {"job_text": _job_text(), "profile": _profile(), "projects": _projects()},
        ).data
        if not _has_key(score, "overall_score"):
            raise RuntimeError("calculate_match_score did not return overall_score.")
        print("MCP runtime tool call: calculate_match_score OK")

        print("MCP runtime smoke test succeeded.")
        return 0
    except Exception as exc:
        print(f"MCP runtime smoke test failed: {exc}")
        return 1


def _has_key(value: Any, key: str) -> bool:
    return isinstance(value, dict) and key in value


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
