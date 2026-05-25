"""Tests for the OandaClient and OandaAPIError."""

import pytest
from pytest_httpx import HTTPXMock

from oanda_mcp.client import OandaAPIError, OandaClient
from oanda_mcp.config import Settings


@pytest.fixture
def practice_settings(monkeypatch: pytest.MonkeyPatch) -> Settings:
    monkeypatch.setenv("OANDA_API_KEY", "test-api-key")
    monkeypatch.setenv("OANDA_ACCOUNT_ID", "001-001-12345-001")
    monkeypatch.setenv("OANDA_ENVIRONMENT", "practice")
    return Settings()


@pytest.fixture
def live_settings(monkeypatch: pytest.MonkeyPatch) -> Settings:
    monkeypatch.setenv("OANDA_API_KEY", "live-api-key")
    monkeypatch.setenv("OANDA_ACCOUNT_ID", "001-001-99999-001")
    monkeypatch.setenv("OANDA_ENVIRONMENT", "live")
    return Settings()


# --- OandaAPIError tests ---


def test_oanda_api_error_carries_status_code() -> None:
    """OandaAPIError stores the HTTP status code."""
    err = OandaAPIError(status_code=404, error_code="ACCOUNT_NOT_FOUND", message="Not found")
    assert err.status_code == 404


def test_oanda_api_error_carries_error_code() -> None:
    """OandaAPIError stores the OANDA error code string."""
    err = OandaAPIError(status_code=400, error_code="INVALID_REQUEST", message="Bad input")
    assert err.error_code == "INVALID_REQUEST"


def test_oanda_api_error_carries_message() -> None:
    """OandaAPIError stores the human-readable error message."""
    err = OandaAPIError(status_code=500, error_code=None, message="Internal error")
    assert err.message == "Internal error"


def test_oanda_api_error_is_exception() -> None:
    """OandaAPIError can be raised and caught as an Exception."""
    with pytest.raises(OandaAPIError):
        raise OandaAPIError(status_code=403, error_code="FORBIDDEN", message="Forbidden")


# --- OandaClient construction tests ---


async def test_client_uses_practice_base_url(
    practice_settings: Settings, httpx_mock: HTTPXMock
) -> None:
    """OandaClient sends requests to the practice base URL."""
    httpx_mock.add_response(url="https://api-fxpractice.oanda.com/v3/ping", json={})

    async with OandaClient(practice_settings) as client:
        await client.get("/ping")


async def test_client_uses_live_base_url(
    live_settings: Settings, httpx_mock: HTTPXMock
) -> None:
    """OandaClient sends requests to the live base URL when environment is live."""
    httpx_mock.add_response(url="https://api-fxtrade.oanda.com/v3/ping", json={})

    async with OandaClient(live_settings) as client:
        await client.get("/ping")


async def test_client_sets_authorization_header(
    practice_settings: Settings, httpx_mock: HTTPXMock
) -> None:
    """OandaClient sets Authorization: Bearer header on every request."""
    httpx_mock.add_response(url="https://api-fxpractice.oanda.com/v3/ping", json={})

    async with OandaClient(practice_settings) as client:
        await client.get("/ping")

    request = httpx_mock.get_request()
    assert request is not None
    assert request.headers["Authorization"] == "Bearer test-api-key"


async def test_client_sets_content_type_header(
    practice_settings: Settings, httpx_mock: HTTPXMock
) -> None:
    """OandaClient sets Content-Type: application/json on every request."""
    httpx_mock.add_response(url="https://api-fxpractice.oanda.com/v3/ping", json={})

    async with OandaClient(practice_settings) as client:
        await client.get("/ping")

    request = httpx_mock.get_request()
    assert request is not None
    assert "application/json" in request.headers.get("Content-Type", "")


# --- HTTP method tests ---


async def test_get_returns_json(
    practice_settings: Settings, httpx_mock: HTTPXMock
) -> None:
    """get() returns parsed JSON from the response body."""
    httpx_mock.add_response(
        url="https://api-fxpractice.oanda.com/v3/accounts",
        json={"accounts": []},
    )

    async with OandaClient(practice_settings) as client:
        result = await client.get("/accounts")

    assert result == {"accounts": []}


async def test_post_sends_json_body(
    practice_settings: Settings, httpx_mock: HTTPXMock
) -> None:
    """post() sends a JSON body and returns parsed JSON response."""
    httpx_mock.add_response(
        url="https://api-fxpractice.oanda.com/v3/accounts/001-001-12345-001/orders",
        json={"orderCreateTransaction": {}},
        status_code=201,
    )

    async with OandaClient(practice_settings) as client:
        result = await client.post(
            "/accounts/001-001-12345-001/orders",
            json={"order": {"type": "MARKET"}},
        )

    assert "orderCreateTransaction" in result
    request = httpx_mock.get_request()
    assert request is not None
    assert request.method == "POST"


async def test_put_sends_json_body(
    practice_settings: Settings, httpx_mock: HTTPXMock
) -> None:
    """put() sends a JSON body and returns parsed JSON response."""
    httpx_mock.add_response(
        url="https://api-fxpractice.oanda.com/v3/accounts/001-001-12345-001/orders/123/cancel",
        json={"orderCancelTransaction": {}},
    )

    async with OandaClient(practice_settings) as client:
        result = await client.put(
            "/accounts/001-001-12345-001/orders/123/cancel",
        )

    assert "orderCancelTransaction" in result
    request = httpx_mock.get_request()
    assert request is not None
    assert request.method == "PUT"


async def test_get_with_params(
    practice_settings: Settings, httpx_mock: HTTPXMock
) -> None:
    """get() passes query parameters to the request."""
    httpx_mock.add_response(
        url="https://api-fxpractice.oanda.com/v3/accounts/001-001-12345-001/trades?state=OPEN",
        json={"trades": []},
    )

    async with OandaClient(practice_settings) as client:
        result = await client.get(
            "/accounts/001-001-12345-001/trades", params={"state": "OPEN"}
        )

    assert result == {"trades": []}


# --- Error handling tests ---


async def test_raises_oanda_api_error_on_400(
    practice_settings: Settings, httpx_mock: HTTPXMock
) -> None:
    """OandaAPIError is raised for 400 responses with OANDA error body."""
    httpx_mock.add_response(
        url="https://api-fxpractice.oanda.com/v3/accounts/bad",
        status_code=400,
        json={"errorCode": "INVALID_ACCOUNT", "errorMessage": "Account ID is invalid"},
    )

    async with OandaClient(practice_settings) as client:
        with pytest.raises(OandaAPIError) as exc_info:
            await client.get("/accounts/bad")

    assert exc_info.value.status_code == 400
    assert exc_info.value.error_code == "INVALID_ACCOUNT"
    assert "invalid" in exc_info.value.message.lower()


async def test_raises_oanda_api_error_on_401(
    practice_settings: Settings, httpx_mock: HTTPXMock
) -> None:
    """OandaAPIError is raised for 401 Unauthorized responses."""
    httpx_mock.add_response(
        url="https://api-fxpractice.oanda.com/v3/accounts",
        status_code=401,
        json={"errorCode": "UNAUTHORIZED", "errorMessage": "Access denied"},
    )

    async with OandaClient(practice_settings) as client:
        with pytest.raises(OandaAPIError) as exc_info:
            await client.get("/accounts")

    assert exc_info.value.status_code == 401


async def test_raises_oanda_api_error_on_404(
    practice_settings: Settings, httpx_mock: HTTPXMock
) -> None:
    """OandaAPIError is raised for 404 Not Found responses."""
    httpx_mock.add_response(
        url="https://api-fxpractice.oanda.com/v3/accounts/missing",
        status_code=404,
        json={"errorCode": "NOT_FOUND", "errorMessage": "Resource not found"},
    )

    async with OandaClient(practice_settings) as client:
        with pytest.raises(OandaAPIError) as exc_info:
            await client.get("/accounts/missing")

    assert exc_info.value.status_code == 404


async def test_raises_oanda_api_error_on_500(
    practice_settings: Settings, httpx_mock: HTTPXMock
) -> None:
    """OandaAPIError is raised for 500 server errors, handling missing error body fields."""
    httpx_mock.add_response(
        url="https://api-fxpractice.oanda.com/v3/accounts",
        status_code=500,
        json={"errorMessage": "Internal server error"},
    )

    async with OandaClient(practice_settings) as client:
        with pytest.raises(OandaAPIError) as exc_info:
            await client.get("/accounts")

    assert exc_info.value.status_code == 500
    assert exc_info.value.error_code is None


async def test_successful_response_does_not_raise(
    practice_settings: Settings, httpx_mock: HTTPXMock
) -> None:
    """No exception is raised for 2xx responses."""
    httpx_mock.add_response(
        url="https://api-fxpractice.oanda.com/v3/accounts",
        status_code=200,
        json={"accounts": []},
    )

    async with OandaClient(practice_settings) as client:
        result = await client.get("/accounts")

    assert result == {"accounts": []}
