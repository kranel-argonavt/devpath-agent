"""Public GitHub repository metadata import helpers.

This module intentionally uses only public GitHub REST API metadata. It does
not require tokens, access private repositories, scrape HTML, clone repos, or
download source code.
"""

from __future__ import annotations

import re
from typing import Any, Callable

import requests


GITHUB_REPOS_API_BASE = "https://api.github.com/users"
_USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$")


def is_github_username_provided(username: str | None) -> bool:
    """Return True if a non-empty GitHub username was provided."""

    return bool(username and username.strip())


def normalize_github_username(username: str) -> str:
    """Trim common GitHub username input noise."""

    value = str(username or "").strip()
    if value.startswith("@"):
        value = value[1:]
    return value.strip()


def is_valid_github_username(username: str) -> bool:
    """Return True if the value looks like a valid GitHub username."""

    value = normalize_github_username(username)
    return bool(value and _USERNAME_PATTERN.match(value) and "--" not in value)


def build_github_repos_api_url(username: str, *, per_page: int = 30) -> str:
    """Build the public GitHub user repositories API URL."""

    normalized = normalize_github_username(username)
    if not is_valid_github_username(normalized):
        raise ValueError("Invalid GitHub username. Use only letters, numbers, or hyphens.")

    page_size = max(1, min(int(per_page), 100))
    return f"{GITHUB_REPOS_API_BASE}/{normalized}/repos?type=public&sort=pushed&direction=desc&per_page={page_size}"


def parse_github_repo(repo: dict[str, Any]) -> dict[str, Any]:
    """Normalize one GitHub public repository API object."""

    return {
        "name": str(repo.get("name") or ""),
        "description": repo.get("description") or "",
        "html_url": repo.get("html_url") or "",
        "language": repo.get("language") or "",
        "topics": _clean_list(repo.get("topics", [])),
        "stars": int(repo.get("stargazers_count") or 0),
        "forks": int(repo.get("forks_count") or 0),
        "updated_at": repo.get("updated_at") or "",
        "pushed_at": repo.get("pushed_at") or "",
        "fork": bool(repo.get("fork", False)),
        "archived": bool(repo.get("archived", False)),
    }


def parse_github_repositories(repos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Normalize a list of GitHub public repository API objects."""

    return [parse_github_repo(repo) for repo in repos]


def convert_github_repos_to_projects(repos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Convert normalized GitHub repos into portfolio project entries."""

    projects: list[dict[str, Any]] = []
    for repo in repos:
        normalized = parse_github_repo(repo) if "stargazers_count" in repo else repo
        technologies = _repo_technologies(normalized)
        projects.append(
            {
                "name": normalized.get("name", ""),
                "description": normalized.get("description", ""),
                "technologies": technologies,
                "url": normalized.get("html_url", ""),
                "source": "github",
                "github": {
                    "language": normalized.get("language", ""),
                    "topics": normalized.get("topics", []),
                    "stars": normalized.get("stars", 0),
                    "forks": normalized.get("forks", 0),
                    "updated_at": normalized.get("updated_at", ""),
                    "pushed_at": normalized.get("pushed_at", ""),
                    "fork": normalized.get("fork", False),
                    "archived": normalized.get("archived", False),
                },
            }
        )
    return projects


def fetch_public_github_repositories(
    username: str,
    *,
    max_repos: int = 10,
    include_forks: bool = False,
    include_archived: bool = False,
    http_get: Callable[..., Any] | None = None,
) -> list[dict[str, Any]]:
    """Fetch public GitHub repository metadata for a user.

    The `http_get` parameter is injectable so tests can avoid network calls.
    """

    normalized = normalize_github_username(username)
    if not is_valid_github_username(normalized):
        raise ValueError("Invalid GitHub username. Use only letters, numbers, or hyphens.")

    limit = max(1, int(max_repos))
    url = build_github_repos_api_url(normalized, per_page=min(limit, 100))
    getter = http_get or requests.get

    try:
        response = getter(
            url,
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "DevPath-Agent-Capstone",
            },
            timeout=10,
        )
    except Exception as exc:
        raise RuntimeError(f"Could not fetch public GitHub repositories for {normalized}: {exc}") from exc

    status_code = int(getattr(response, "status_code", 0) or 0)
    if status_code == 404:
        raise RuntimeError(f"GitHub user '{normalized}' was not found.")
    if status_code == 403:
        raise RuntimeError("GitHub API request was rate limited or forbidden. Try again later.")
    if status_code >= 400:
        raise RuntimeError(f"GitHub API request failed with status {status_code}.")

    try:
        payload = response.json()
    except Exception as exc:
        raise RuntimeError("GitHub API response was not valid JSON.") from exc

    if not isinstance(payload, list):
        raise RuntimeError("GitHub API response did not contain a repository list.")

    repos = parse_github_repositories(payload)
    repos = [
        repo
        for repo in repos
        if (include_forks or not repo.get("fork")) and (include_archived or not repo.get("archived"))
    ]
    repos.sort(key=lambda repo: repo.get("pushed_at") or repo.get("updated_at") or "", reverse=True)
    return repos[:limit]


class GitHubService:
    """Small service wrapper for public GitHub repository metadata."""

    def fetch_public_repositories(self, username: str, max_repos: int = 10) -> list[dict[str, Any]]:
        """Fetch public repositories for a username."""

        return fetch_public_github_repositories(username, max_repos=max_repos)


def _clean_list(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    return [str(value).strip() for value in values if str(value).strip()]


def _repo_technologies(repo: dict[str, Any]) -> list[str]:
    technologies: list[str] = []
    language = str(repo.get("language") or "").strip()
    if language:
        technologies.append(language)
    technologies.extend(_clean_list(repo.get("topics", [])))

    description = str(repo.get("description") or "").lower()
    description_keywords = {
        "C#": ["c#", "c sharp", "csharp"],
        ".NET": [".net", "dotnet"],
        "ASP.NET Core": ["asp.net core", "asp net core"],
        "REST API": ["rest api", "restful"],
        "SQL": ["sql", "sqlite", "postgres"],
        "Unity": ["unity"],
        "Docker": ["docker"],
        "Azure": ["azure"],
    }
    for canonical, aliases in description_keywords.items():
        if any(alias in description for alias in aliases):
            technologies.append(canonical)

    return list(dict.fromkeys(technologies))
