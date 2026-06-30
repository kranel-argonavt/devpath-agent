"""Future GitHub public repository integration for portfolio evidence gathering."""


def is_github_username_provided(username: str | None) -> bool:
    """Return True if a non-empty GitHub username was provided."""

    return bool(username and username.strip())


class GitHubService:
    """Placeholder service for future GitHub API interactions."""

    def fetch_public_repositories(self, username: str) -> list[dict]:
        """Placeholder for future public repository retrieval."""

        raise NotImplementedError("GitHub integration will be implemented in a later step.")
