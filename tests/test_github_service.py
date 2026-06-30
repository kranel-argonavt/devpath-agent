"""Tests for GitHub service placeholders."""

import pytest

from devpath.services.github_service import GitHubService, is_github_username_provided


def test_is_github_username_provided_returns_true_for_non_empty_username() -> None:
    assert is_github_username_provided("octocat") is True


def test_is_github_username_provided_returns_false_for_empty_values() -> None:
    assert is_github_username_provided("") is False
    assert is_github_username_provided("   ") is False
    assert is_github_username_provided(None) is False


def test_github_service_placeholder_raises_not_implemented() -> None:
    service = GitHubService()

    with pytest.raises(NotImplementedError):
        service.fetch_public_repositories("example-user")
