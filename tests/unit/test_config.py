"""Tests for the Settings configuration class."""

import pytest
from pydantic import ValidationError


def test_settings_requires_api_key(monkeypatch):
    """Settings raises ValidationError when OANDA_API_KEY is missing."""
    monkeypatch.delenv("OANDA_API_KEY", raising=False)
    monkeypatch.delenv("OANDA_ACCOUNT_ID", raising=False)
    monkeypatch.setenv("OANDA_ACCOUNT_ID", "123-456")

    from oanda_mcp.config import Settings

    with pytest.raises(ValidationError):
        Settings()


def test_settings_requires_account_id(monkeypatch):
    """Settings raises ValidationError when OANDA_ACCOUNT_ID is missing."""
    monkeypatch.setenv("OANDA_API_KEY", "test-key")
    monkeypatch.delenv("OANDA_ACCOUNT_ID", raising=False)

    from oanda_mcp.config import Settings

    with pytest.raises(ValidationError):
        Settings()


def test_settings_environment_defaults_to_practice(monkeypatch):
    """OANDA_ENVIRONMENT defaults to 'practice' when not set."""
    monkeypatch.setenv("OANDA_API_KEY", "test-key")
    monkeypatch.setenv("OANDA_ACCOUNT_ID", "123-456")
    monkeypatch.delenv("OANDA_ENVIRONMENT", raising=False)

    from oanda_mcp.config import Settings

    settings = Settings()
    assert settings.oanda_environment == "practice"


def test_settings_environment_can_be_live(monkeypatch):
    """OANDA_ENVIRONMENT can be set to 'live'."""
    monkeypatch.setenv("OANDA_API_KEY", "test-key")
    monkeypatch.setenv("OANDA_ACCOUNT_ID", "123-456")
    monkeypatch.setenv("OANDA_ENVIRONMENT", "live")

    from oanda_mcp.config import Settings

    settings = Settings()
    assert settings.oanda_environment == "live"


def test_settings_rejects_invalid_environment(monkeypatch):
    """Settings raises ValidationError for unsupported OANDA_ENVIRONMENT values."""
    monkeypatch.setenv("OANDA_API_KEY", "test-key")
    monkeypatch.setenv("OANDA_ACCOUNT_ID", "123-456")
    monkeypatch.setenv("OANDA_ENVIRONMENT", "staging")

    from oanda_mcp.config import Settings

    with pytest.raises(ValidationError):
        Settings()


def test_settings_mcp_port_defaults_to_8000(monkeypatch):
    """MCP_PORT defaults to 8000 when not set."""
    monkeypatch.setenv("OANDA_API_KEY", "test-key")
    monkeypatch.setenv("OANDA_ACCOUNT_ID", "123-456")
    monkeypatch.delenv("MCP_PORT", raising=False)

    from oanda_mcp.config import Settings

    settings = Settings()
    assert settings.mcp_port == 8000


def test_settings_mcp_port_is_configurable(monkeypatch):
    """MCP_PORT can be overridden via environment variable."""
    monkeypatch.setenv("OANDA_API_KEY", "test-key")
    monkeypatch.setenv("OANDA_ACCOUNT_ID", "123-456")
    monkeypatch.setenv("MCP_PORT", "9000")

    from oanda_mcp.config import Settings

    settings = Settings()
    assert settings.mcp_port == 9000


def test_settings_base_url_practice(monkeypatch):
    """base_url returns the OANDA practice API URL for practice environment."""
    monkeypatch.setenv("OANDA_API_KEY", "test-key")
    monkeypatch.setenv("OANDA_ACCOUNT_ID", "123-456")
    monkeypatch.setenv("OANDA_ENVIRONMENT", "practice")

    from oanda_mcp.config import Settings

    settings = Settings()
    assert settings.base_url == "https://api-fxpractice.oanda.com/v3"


def test_settings_base_url_live(monkeypatch):
    """base_url returns the OANDA live API URL for live environment."""
    monkeypatch.setenv("OANDA_API_KEY", "test-key")
    monkeypatch.setenv("OANDA_ACCOUNT_ID", "123-456")
    monkeypatch.setenv("OANDA_ENVIRONMENT", "live")

    from oanda_mcp.config import Settings

    settings = Settings()
    assert settings.base_url == "https://api-fxtrade.oanda.com/v3"


def test_settings_stores_credentials(monkeypatch):
    """Settings correctly stores API key and account ID."""
    monkeypatch.setenv("OANDA_API_KEY", "my-api-key")
    monkeypatch.setenv("OANDA_ACCOUNT_ID", "001-001-12345-001")

    from oanda_mcp.config import Settings

    settings = Settings()
    assert settings.oanda_api_key == "my-api-key"
    assert settings.oanda_account_id == "001-001-12345-001"
