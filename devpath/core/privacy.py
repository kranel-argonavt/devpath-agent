"""Deterministic privacy masking utilities for local data sanitization."""

import re


EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_PATTERN = re.compile(r"(?<!\w)(?:\+?\d[\d\s().-]{7,}\d)(?!\w)")
API_KEY_PATTERN = re.compile(
    r"\b(?P<name>GOOGLE_API_KEY|GITHUB_TOKEN)\s*=\s*(?P<value>[^\s#]+)",
    re.IGNORECASE,
)


def mask_email(text: str) -> str:
    """Mask email addresses in text."""

    return EMAIL_PATTERN.sub("[EMAIL_REDACTED]", text)


def mask_phone(text: str) -> str:
    """Mask phone-like numbers in text."""

    return PHONE_PATTERN.sub("[PHONE_REDACTED]", text)


def mask_api_keys(text: str) -> str:
    """Mask API-key-like strings in text."""

    return API_KEY_PATTERN.sub(lambda match: f"{match.group('name')}=[REDACTED]", text)


def mask_personal_data(text: str) -> str:
    """Apply all privacy masking rules."""

    masked = mask_email(text)
    masked = mask_phone(masked)
    return mask_api_keys(masked)
