"""Manual GitHub public repository import smoke test.

Run from the project root:
    python scripts/check_github_public_import.py octocat
"""

from pathlib import Path
import sys
from typing import Any, Callable


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from devpath.services.github_service import (
    convert_github_repos_to_projects,
    fetch_public_github_repositories,
    normalize_github_username,
)


RepoFetcher = Callable[[str], list[dict[str, Any]]]


def main(argv: list[str] | None = None, fetcher: RepoFetcher | None = None) -> int:
    """Fetch public GitHub repo metadata and print a compact smoke-test summary."""

    args = list(argv if argv is not None else sys.argv[1:])
    username = normalize_github_username(args[0]) if args else "octocat"
    repo_fetcher = fetcher or (lambda value: fetch_public_github_repositories(value, max_repos=5))

    print("DevPath GitHub public import smoke test")
    print("Only public repository metadata is imported. No tokens, cloning, or source downloads are used.")

    try:
        repos = repo_fetcher(username)
        projects = convert_github_repos_to_projects(repos)
    except Exception as exc:
        print(f"GitHub public import smoke test failed: {exc}")
        return 1

    print(f"Imported repositories: {len(projects)}")
    for project in projects:
        github = project.get("github", {})
        language = github.get("language") or "Unknown"
        print(f"- {project.get('name', '')} | {language} | {project.get('url', '')}")

    print("GitHub public import smoke test succeeded.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
