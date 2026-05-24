"""Async HTTP client for the OANDA V20 REST API."""

from types import TracebackType
from typing import Any

import httpx

from oanda_mcp.config import Settings

_TIMEOUT_SECONDS = 30.0


class OandaAPIError(Exception):
    """Raised when the OANDA V20 API returns a non-2xx response."""

    def __init__(self, *, status_code: int, error_code: str | None, message: str) -> None:
        self.status_code = status_code
        self.error_code = error_code
        self.message = message
        super().__init__(f"OANDA API error {status_code}: {error_code} — {message}")


class OandaClient:
    """Async wrapper around httpx.AsyncClient targeting the OANDA V20 REST API.

    Usage:
        async with OandaClient(settings) as client:
            data = await client.get("/accounts")
    """

    def __init__(self, settings: Settings) -> None:
        self._http = httpx.AsyncClient(
            base_url=settings.base_url,
            headers={
                "Authorization": f"Bearer {settings.oanda_api_key}",
                "Content-Type": "application/json",
            },
            timeout=_TIMEOUT_SECONDS,
        )

    async def __aenter__(self) -> "OandaClient":
        await self._http.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self._http.__aexit__(exc_type, exc_val, exc_tb)

    def _raise_for_status(self, response: httpx.Response) -> None:
        if response.is_success:
            return
        try:
            body = response.json()
        except Exception:
            body = {}
        raise OandaAPIError(
            status_code=response.status_code,
            error_code=body.get("errorCode"),
            message=body.get("errorMessage", response.text),
        )

    async def get(self, path: str, *, params: dict[str, Any] | None = None) -> Any:
        """Send a GET request and return parsed JSON."""
        response = await self._http.get(path, params=params)
        self._raise_for_status(response)
        return response.json()

    async def post(self, path: str, *, json: dict[str, Any] | None = None) -> Any:
        """Send a POST request with an optional JSON body and return parsed JSON."""
        response = await self._http.post(path, json=json)
        self._raise_for_status(response)
        return response.json()

    async def put(self, path: str, *, json: dict[str, Any] | None = None) -> Any:
        """Send a PUT request with an optional JSON body and return parsed JSON."""
        response = await self._http.put(path, json=json)
        self._raise_for_status(response)
        return response.json()
