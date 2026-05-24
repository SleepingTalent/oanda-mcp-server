"""Application configuration loaded from environment variables and .env file."""

from typing import Literal

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

_PRACTICE_BASE_URL = "https://api-fxpractice.oanda.com/v3"
_LIVE_BASE_URL = "https://api-fxtrade.oanda.com/v3"


class Settings(BaseSettings):
    """Application settings sourced from environment variables or a .env file.

    Required variables: OANDA_API_KEY, OANDA_ACCOUNT_ID
    Optional variables: OANDA_ENVIRONMENT (default: practice), MCP_PORT (default: 8000)
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    oanda_api_key: str
    oanda_account_id: str
    oanda_environment: Literal["practice", "live"] = "practice"
    mcp_port: int = 8000

    @computed_field  # type: ignore[prop-decorator]
    @property
    def base_url(self) -> str:
        """Return the OANDA V20 REST API base URL for the configured environment."""
        if self.oanda_environment == "live":
            return _LIVE_BASE_URL
        return _PRACTICE_BASE_URL
