"""Future configuration loader for environment variables and project settings."""

from dataclasses import dataclass
import os


@dataclass
class AppConfig:
    """Minimal configuration placeholder for future runtime settings."""

    google_api_key: str = ""
    github_token: str = ""


def load_config() -> AppConfig:
    """Load reserved environment variables without using them yet."""

    return AppConfig(
        google_api_key=os.getenv("GOOGLE_API_KEY", ""),
        github_token=os.getenv("GITHUB_TOKEN", ""),
    )
