"""Local file loading helpers for profiles, projects, job postings, and outputs."""

import json
from pathlib import Path
from typing import Any


def load_json_file(path: str | Path) -> dict[str, Any] | list[dict[str, Any]]:
    """Load and return JSON data from a file."""

    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(f"JSON file not found: {source}")

    try:
        data = json.loads(source.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {source}: {exc.msg}") from exc

    return data


def load_text_file(path: str | Path) -> str:
    """Load and return text content from a file."""

    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(f"Text file not found: {source}")

    return source.read_text(encoding="utf-8")


def read_text_file(path: str | Path) -> str:
    """Backward-compatible alias for loading UTF-8 text files."""

    return load_text_file(path)
