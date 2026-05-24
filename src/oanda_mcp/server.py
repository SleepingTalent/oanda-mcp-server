"""FastMCP server entrypoint — tool registration and HTTP transport."""

from fastmcp import FastMCP

from oanda_mcp.config import Settings

mcp = FastMCP("OANDA V20 MCP Server")


def main() -> None:
    settings = Settings()
    mcp.run(transport="http", host="0.0.0.0", port=settings.mcp_port)


if __name__ == "__main__":
    main()
