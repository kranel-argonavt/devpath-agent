"""Tests for deterministic privacy masking helpers."""

from devpath.core.privacy import mask_api_keys, mask_email, mask_personal_data, mask_phone


def test_mask_email_redacts_email_addresses() -> None:
    assert mask_email("Contact me at test@example.com") == "Contact me at [EMAIL_REDACTED]"


def test_mask_phone_redacts_phone_like_numbers() -> None:
    assert mask_phone("Phone: +49 123 456 7890") == "Phone: [PHONE_REDACTED]"


def test_mask_api_keys_redacts_google_api_key() -> None:
    assert mask_api_keys("GOOGLE_API_KEY=abc123") == "GOOGLE_API_KEY=[REDACTED]"


def test_mask_personal_data_redacts_github_token() -> None:
    text = "Email test@example.com, phone +49 123 456 7890, GITHUB_TOKEN=abc123"
    masked = mask_personal_data(text)

    assert "[EMAIL_REDACTED]" in masked
    assert "[PHONE_REDACTED]" in masked
    assert "GITHUB_TOKEN=[REDACTED]" in masked
