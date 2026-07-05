"""MCP-style deterministic tools for local portfolio project data."""

from pathlib import Path
from typing import Any

from devpath.services.file_service import load_json_file


DEFAULT_PROJECTS_PATH = Path("data") / "sample_projects.json"


def read_local_projects(path: str = str(DEFAULT_PROJECTS_PATH)) -> list[dict[str, Any]]:
    """Read local portfolio projects from a JSON list."""

    data = load_json_file(path)
    if not isinstance(data, list):
        raise ValueError("Projects JSON must contain a list of project objects.")
    if not all(isinstance(project, dict) for project in data):
        raise ValueError("Each project entry must be an object.")
    return data
