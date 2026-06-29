"""Future deterministic privacy masking utilities for local data sanitization."""


def mask_email(email: str) -> str:
    """Mask the local part of an email address while keeping the domain visible."""

    if "@" not in email:
        return email
    local_part, domain = email.split("@", 1)
    if len(local_part) <= 2:
        masked_local = "*" * len(local_part)
    else:
        masked_local = local_part[0] + "*" * (len(local_part) - 2) + local_part[-1]
    return f"{masked_local}@{domain}"
