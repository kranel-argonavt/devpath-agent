"""MCP-style tools for controlled public GitHub metadata lookups."""

from typing import Any

from devpath.services.github_service import (
    fetch_public_github_repositories,
    fetch_public_repository_readme,
)


def fetch_github_repositories(username: str, max_repos: int = 10) -> list[dict[str, Any]]:
    """Fetch public GitHub repository metadata for a username."""

    return fetch_public_github_repositories(username=username, max_repos=max_repos)


def fetch_repository_readme(owner: str, repo: str, max_chars: int = 12000) -> dict[str, Any]:
    """Fetch README text for a public GitHub repository."""

    return fetch_public_repository_readme(owner=owner, repo=repo, max_chars=max_chars)
