"""Local smoke test for MCP-style deterministic DevPath tools.

Run from the project root:
    python scripts/check_mcp_tools.py
"""

from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


EXPECTED_TOOL_NAMES = {
    "analyze_job_posting",
    "read_profile",
    "read_local_projects",
    "fetch_github_repositories",
    "fetch_repository_readme",
    "summarize_portfolio",
    "build_portfolio_summary",
    "calculate_match_score",
    "build_career_report",
    "detect_sensitive_data",
    "mask_personal_data",
    "export_markdown_report",
}


def main() -> int:
    """Validate the local MCP-style tool layer without starting a transport."""

    print("DevPath MCP smoke test")
    try:
        from mcp_server.server import FastMCP, create_mcp_server, server
        from mcp_server.tools import MCP_TOOL_REGISTRY, list_mcp_tools

        created_server = create_mcp_server()
        tool_names = set(list_mcp_tools())
        missing_tools = EXPECTED_TOOL_NAMES - tool_names
        if missing_tools:
            raise RuntimeError(f"Missing MCP tool(s): {', '.join(sorted(missing_tools))}")

        _validate_registry(MCP_TOOL_REGISTRY)
        _run_tool_smoke_checks(MCP_TOOL_REGISTRY)

        print(f"MCP server: {_server_name(server or created_server)}")
        print(f"MCP SDK available: {_yes_no(FastMCP is not None)}")
        print(f"Registered tools: {', '.join(sorted(tool_names))}")
        print("MCP smoke test succeeded.")
        return 0
    except Exception as exc:
        print(f"MCP smoke test failed: {exc}")
        return 1


def _validate_registry(registry: dict[str, Any]) -> None:
    for tool_name in EXPECTED_TOOL_NAMES:
        tool = registry.get(tool_name)
        if not callable(tool):
            raise RuntimeError(f"MCP tool is not callable: {tool_name}")


def _run_tool_smoke_checks(registry: dict[str, Any]) -> None:
    job_text = _job_text()
    profile = _profile()
    projects = _projects()

    job_analysis = registry["analyze_job_posting"](job_text)
    if "required_skills" not in job_analysis:
        raise RuntimeError("analyze_job_posting did not return required skill data.")

    score = registry["calculate_match_score"](job_text, profile, projects)
    if "overall_score" not in score:
        raise RuntimeError("calculate_match_score did not return overall_score.")

    portfolio = registry["summarize_portfolio"](projects)
    if portfolio.get("project_count") != len(projects):
        raise RuntimeError("summarize_portfolio did not return the expected project count.")

    portfolio_alias = registry["build_portfolio_summary"](projects)
    if portfolio_alias.get("project_count") != len(projects):
        raise RuntimeError("build_portfolio_summary did not return the expected project count.")

    sample_profile = registry["read_profile"]()
    if not isinstance(sample_profile, dict) or "skills" not in sample_profile:
        raise RuntimeError("read_profile did not return sample profile data.")

    sample_projects = registry["read_local_projects"]()
    if not isinstance(sample_projects, list) or not sample_projects:
        raise RuntimeError("read_local_projects did not return sample project data.")

    report = registry["build_career_report"](job_text, profile, projects)
    if "profile_match" not in report or "overall_score" not in report["profile_match"]:
        raise RuntimeError("build_career_report did not return profile match score data.")

    detected = registry["detect_sensitive_data"]("Email test@example.com and GOOGLE_API_KEY=abc123")
    if not detected.get("has_sensitive_data"):
        raise RuntimeError("detect_sensitive_data did not detect sensitive values.")

    masked = registry["mask_personal_data"]("Email test@example.com and GOOGLE_API_KEY=abc123")
    if "test@example.com" in masked or "abc123" in masked:
        raise RuntimeError("mask_personal_data did not mask sensitive values.")

    with TemporaryDirectory() as temp_dir:
        exported_path = Path(registry["export_markdown_report"](report, output_dir=temp_dir, filename="mcp_smoke"))
        if not exported_path.exists() or exported_path.suffix != ".md":
            raise RuntimeError("export_markdown_report did not create a Markdown file in the temporary directory.")


def _server_name(server: Any) -> str:
    if isinstance(server, dict):
        return str(server.get("name", "unknown"))
    metadata = getattr(server, "devpath_metadata", {})
    return str(metadata.get("name") or getattr(server, "name", "unknown"))


def _yes_no(value: bool) -> str:
    return "yes" if value else "no"


def _job_text() -> str:
    return """
    Junior .NET Developer
    Requirements: C#, .NET, ASP.NET Core, SQL, Git, REST API, English.
    Nice to have: Docker and Azure.
    """


def _profile() -> dict[str, Any]:
    return {
        "experience_level": "Junior",
        "skills": ["C#", ".NET", "Git", "SQLite"],
        "education": "Software Engineering",
        "languages": ["English B1-B2"],
        "location_preference": "Germany / Remote EU",
        "target_roles": ["Junior .NET Developer"],
    }


def _projects() -> list[dict[str, Any]]:
    return [
        {
            "name": "TaskFlow Desktop",
            "technologies": ["C#", ".NET", "WPF", "SQLite", "Git"],
            "description": "Desktop task manager with local database storage.",
        }
    ]


if __name__ == "__main__":
    raise SystemExit(main())
