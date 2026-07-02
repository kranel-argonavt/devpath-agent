"""Tests for app configuration helpers."""

from devpath.core.config import DEFAULT_GEMINI_MODEL, get_app_config


def test_get_app_config_without_api_key_disables_gemini(monkeypatch) -> None:
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_MODEL", raising=False)

    config = get_app_config(load_env_file=False)

    assert config.google_api_key is None
    assert config.gemini_enabled is False
    assert config.gemini_model == DEFAULT_GEMINI_MODEL


def test_get_app_config_uses_google_api_key(monkeypatch) -> None:
    monkeypatch.setenv("GOOGLE_API_KEY", "google-key")
    monkeypatch.setenv("GEMINI_API_KEY", "gemini-key")

    config = get_app_config(load_env_file=False)

    assert config.google_api_key == "google-key"
    assert config.gemini_enabled is True


def test_get_app_config_uses_gemini_api_key_fallback(monkeypatch) -> None:
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.setenv("GEMINI_API_KEY", "gemini-key")

    config = get_app_config(load_env_file=False)

    assert config.google_api_key == "gemini-key"
    assert config.gemini_enabled is True


def test_get_app_config_uses_default_model(monkeypatch) -> None:
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_MODEL", raising=False)

    config = get_app_config(load_env_file=False)

    assert config.gemini_model == "gemini-2.5-flash"


def test_get_app_config_uses_custom_model(monkeypatch) -> None:
    monkeypatch.setenv("GEMINI_MODEL", "gemini-custom")

    config = get_app_config(load_env_file=False)

    assert config.gemini_model == "gemini-custom"
