"""Starter tests for the future GitHub service placeholder."""

import pytest

from devpath.services.github_service import GitHubService


def test_github_service_placeholder_raises_not_implemented() -> None:
    service = GitHubService()

    with pytest.raises(NotImplementedError):
        service.fetch_public_repositories("example-user")
