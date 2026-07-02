"""Configuration helpers for environment variables and project settings."""

from dataclasses import dataclass
import os

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - python-dotenv is in requirements, but keep import safe.
    load_dotenv = None


DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"


@dataclass(frozen=True)
class AppConfig:
    """Runtime configuration for optional external integrations."""

    google_api_key: str | None
    gemini_model: str
    gemini_enabled: bool


def get_app_config(load_env_file: bool = True) -> AppConfig:
    """Load app configuration without exposing secrets."""

    if load_env_file and load_dotenv is not None:
        load_dotenv()

    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    api_key = api_key.strip() if api_key else None
    model = os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL).strip() or DEFAULT_GEMINI_MODEL

    return AppConfig(
        google_api_key=api_key,
        gemini_model=model,
        gemini_enabled=bool(api_key),
    )


def load_config() -> AppConfig:
    """Backward-compatible config loader."""

    return get_app_config()
