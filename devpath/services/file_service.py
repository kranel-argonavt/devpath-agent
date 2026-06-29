"""Future local file loading helpers for profiles, projects, job postings, and outputs."""

from pathlib import Path


def read_text_file(path: str | Path) -> str:
    """Read a text file as UTF-8 for local development utilities."""

    return Path(path).read_text(encoding="utf-8")
