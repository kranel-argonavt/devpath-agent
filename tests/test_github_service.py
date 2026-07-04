"""Tests for public GitHub repository metadata helpers."""

from __future__ import annotations

import pytest

from devpath.services.github_service import (
    GitHubService,
    build_github_repos_api_url,
    convert_github_repos_to_projects,
    fetch_public_github_repositories,
    is_github_username_provided,
    is_valid_github_username,
    normalize_github_username,
    parse_github_repo,
    parse_github_repositories,
)
from scripts.check_github_public_import import main as github_public_import_main


class FakeResponse:
    def __init__(self, status_code: int, payload):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload


def test_is_github_username_provided_returns_true_for_non_empty_username() -> None:
    assert is_github_username_provided("octocat") is True


def test_is_github_username_provided_returns_false_for_empty_values() -> None:
    assert is_github_username_provided("") is False
    assert is_github_username_provided("   ") is False
    assert is_github_username_provided(None) is False


def test_normalize_github_username() -> None:
    assert normalize_github_username("  @octocat  ") == "octocat"
    assert normalize_github_username("dev-user") == "dev-user"


def test_is_valid_github_username() -> None:
    assert is_valid_github_username("octocat") is True
    assert is_valid_github_username("dev-user-1") is True
    assert is_valid_github_username("-bad") is False
    assert is_valid_github_username("bad-") is False
    assert is_valid_github_username("bad_name") is False
    assert is_valid_github_username("bad--name") is False
    assert is_valid_github_username("") is False


def test_build_github_repos_api_url() -> None:
    url = build_github_repos_api_url("@octocat", per_page=150)

    assert url == "https://api.github.com/users/octocat/repos?type=public&sort=pushed&direction=desc&per_page=100"


def test_build_github_repos_api_url_rejects_invalid_username() -> None:
    with pytest.raises(ValueError, match="Invalid GitHub username"):
        build_github_repos_api_url("bad_name")


def test_parse_github_repo_handles_public_metadata() -> None:
    repo = parse_github_repo(_repo("taskflow", language="C#", topics=["dotnet", "sqlite"]))

    assert repo["name"] == "taskflow"
    assert repo["description"] == "A C# .NET REST API with SQL."
    assert repo["html_url"] == "https://github.com/octocat/taskflow"
    assert repo["language"] == "C#"
    assert repo["topics"] == ["dotnet", "sqlite"]
    assert repo["stars"] == 12
    assert repo["forks"] == 3
    assert repo["updated_at"] == "2026-01-02T00:00:00Z"
    assert repo["pushed_at"] == "2026-01-03T00:00:00Z"
    assert repo["fork"] is False
    assert repo["archived"] is False


def test_parse_github_repositories_normalizes_list() -> None:
    repos = parse_github_repositories([_repo("one"), _repo("two", language="Python")])

    assert [repo["name"] for repo in repos] == ["one", "two"]
    assert repos[1]["language"] == "Python"


def test_convert_github_repos_to_projects_returns_project_compatible_shape() -> None:
    repos = parse_github_repositories([_repo("taskflow", language="C#", topics=["dotnet"])])

    projects = convert_github_repos_to_projects(repos)

    assert projects == [
        {
            "name": "taskflow",
            "description": "A C# .NET REST API with SQL.",
            "technologies": ["C#", "dotnet", ".NET", "REST API", "SQL"],
            "url": "https://github.com/octocat/taskflow",
            "source": "github",
            "github": {
                "language": "C#",
                "topics": ["dotnet"],
                "stars": 12,
                "forks": 3,
                "updated_at": "2026-01-02T00:00:00Z",
                "pushed_at": "2026-01-03T00:00:00Z",
                "fork": False,
                "archived": False,
            },
        }
    ]


def test_fetch_public_github_repositories_uses_injected_http_get() -> None:
    calls = []

    def fake_get(url, headers, timeout):
        calls.append((url, headers["User-Agent"], timeout))
        return FakeResponse(200, [_repo("new"), _repo("old", pushed_at="2025-01-01T00:00:00Z")])

    repos = fetch_public_github_repositories("octocat", max_repos=1, http_get=fake_get)

    assert len(repos) == 1
    assert repos[0]["name"] == "new"
    assert calls[0][0].startswith("https://api.github.com/users/octocat/repos")
    assert calls[0][1] == "DevPath-Agent-Capstone"
    assert calls[0][2] == 10


def test_fetch_public_github_repositories_excludes_forks_and_archived_by_default() -> None:
    def fake_get(url, headers, timeout):
        return FakeResponse(200, [_repo("main"), _repo("forked", fork=True), _repo("archived", archived=True)])

    repos = fetch_public_github_repositories("octocat", http_get=fake_get)

    assert [repo["name"] for repo in repos] == ["main"]


def test_fetch_public_github_repositories_can_include_forks_and_archived() -> None:
    def fake_get(url, headers, timeout):
        return FakeResponse(200, [_repo("main"), _repo("forked", fork=True), _repo("archived", archived=True)])

    repos = fetch_public_github_repositories(
        "octocat",
        include_forks=True,
        include_archived=True,
        http_get=fake_get,
    )

    assert [repo["name"] for repo in repos] == ["main", "forked", "archived"]


def test_fetch_public_github_repositories_raises_clear_http_errors() -> None:
    def fake_get(url, headers, timeout):
        return FakeResponse(404, {"message": "Not Found"})

    with pytest.raises(RuntimeError, match="was not found"):
        fetch_public_github_repositories("octocat", http_get=fake_get)


def test_fetch_public_github_repositories_rejects_non_list_payload() -> None:
    def fake_get(url, headers, timeout):
        return FakeResponse(200, {"message": "bad payload"})

    with pytest.raises(RuntimeError, match="repository list"):
        fetch_public_github_repositories("octocat", http_get=fake_get)


def test_github_service_wrapper_fetches_public_repositories(monkeypatch) -> None:
    def fake_fetch(username, max_repos=10):
        return [{"name": username, "stars": max_repos}]

    monkeypatch.setattr("devpath.services.github_service.fetch_public_github_repositories", fake_fetch)

    assert GitHubService().fetch_public_repositories("octocat", max_repos=5) == [{"name": "octocat", "stars": 5}]


def test_github_public_import_smoke_script_with_fake_fetcher(capsys) -> None:
    def fake_fetcher(username):
        assert username == "octocat"
        return [parse_github_repo(_repo("taskflow", language="C#"))]

    result = github_public_import_main(["octocat"], fetcher=fake_fetcher)
    output = capsys.readouterr().out

    assert result == 0
    assert "DevPath GitHub public import smoke test" in output
    assert "Imported repositories: 1" in output
    assert "taskflow | C#" in output
    assert "GitHub public import smoke test succeeded" in output


def _repo(
    name: str,
    *,
    language: str = "C#",
    topics: list[str] | None = None,
    fork: bool = False,
    archived: bool = False,
    pushed_at: str = "2026-01-03T00:00:00Z",
) -> dict:
    return {
        "name": name,
        "description": "A C# .NET REST API with SQL.",
        "html_url": f"https://github.com/octocat/{name}",
        "language": language,
        "topics": topics or [],
        "stargazers_count": 12,
        "forks_count": 3,
        "updated_at": "2026-01-02T00:00:00Z",
        "pushed_at": pushed_at,
        "fork": fork,
        "archived": archived,
    }
