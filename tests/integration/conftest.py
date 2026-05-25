"""Session-scoped Testcontainers fixture for integration tests."""
import os

import pytest
from testcontainers.core.container import DockerContainer
from testcontainers.core.wait_strategies import LogMessageWaitStrategy

_MCP_IMAGE = "oanda-mcp:ci"
_MCP_PORT = 8000


@pytest.fixture(scope="session")
def mcp_base_url() -> str:
    """Start oanda-mcp:ci container and yield its MCP HTTP endpoint URL."""
    api_key = os.environ.get("OANDA_API_KEY")
    account_id = os.environ.get("OANDA_ACCOUNT_ID")
    if not api_key or not account_id:
        pytest.skip("OANDA_API_KEY / OANDA_ACCOUNT_ID not set — skipping integration tests")

    container = (
        DockerContainer(_MCP_IMAGE)
        .with_exposed_ports(_MCP_PORT)
        .with_env("OANDA_API_KEY", api_key)
        .with_env("OANDA_ACCOUNT_ID", account_id)
        .with_env("OANDA_ENVIRONMENT", os.environ.get("OANDA_ENVIRONMENT", "practice"))
        .with_env("MCP_PORT", str(_MCP_PORT))
        .with_env("MCP_TRANSPORT", "http")
    )
    container.waiting_for(LogMessageWaitStrategy("Application startup complete").with_startup_timeout(60))

    with container:
        host = container.get_container_host_ip()
        port = container.get_exposed_port(_MCP_PORT)
        yield f"http://{host}:{port}/mcp"
