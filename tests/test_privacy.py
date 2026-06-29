"""Starter tests for privacy masking placeholders."""

from devpath.core.privacy import mask_email


def test_mask_email_keeps_domain_and_obscures_local_part() -> None:
    assert mask_email("junior.dev@example.com") == "j********v@example.com"
