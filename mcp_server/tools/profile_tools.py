"""MCP-style deterministic tools for candidate profile data."""

from pathlib import Path
from typing import Any

from devpath.services.file_service import load_json_file


DEFAULT_PROFILE_PATH = Path("data") / "sample_profile.json"


def read_profile(path: str = str(DEFAULT_PROFILE_PATH)) -> dict[str, Any]:
    """Read a candidate profile JSON object from a local file."""

    data = load_json_file(path)
    if not isinstance(data, dict):
        raise ValueError("Profile JSON must contain one object.")
    return data
