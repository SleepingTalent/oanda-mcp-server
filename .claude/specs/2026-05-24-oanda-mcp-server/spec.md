# Spec Requirements Document

> Spec: OANDA V20 MCP Server
> Created: 2026-05-24
> Status: Approved

## Overview

A FastMCP server that wraps the OANDA V20 REST API and exposes it as MCP tools over HTTP/SSE, enabling AI coding agents to read account state, price instruments, and manage the full order/trade/position lifecycle. The server runs in Docker, is published to Docker Hub via GitHub Actions, and is covered by a full unit/integration/smoke test pyramid.

## User Stories

### AI Agent Managing Trades

As an AI coding agent, I want to call MCP tools to open, monitor, and close forex trades on OANDA, so that I can manage a trading portfolio programmatically without needing to understand the raw OANDA REST API.

The agent connects to the MCP server over HTTP/SSE, calls tools such as `get_account_summary`, `get_prices`, `create_order`, `list_trades`, and `close_position`. The server validates inputs, forwards requests to the OANDA V20 REST API using the configured credentials and environment, and returns structured results. The agent receives typed responses it can reason over and act on.

### Developer Running the Server Locally

As a developer, I want to start the MCP server locally with a single command and connect an agent to it for manual testing, so that I can validate tool behaviour without deploying to a remote environment.

The developer runs `task serve` which starts the server via `docker-compose up`. The server reads credentials from a local `.env` file and connects to the OANDA practice environment by default. The developer then points Claude Desktop or another agent at `http://localhost:8000` (or the configured `MCP_PORT`).

### CI/CD Pipeline Validating and Publishing

As a developer pushing code, I want every branch and PR to be automatically built and tested, and every merge to `main` to produce a published Docker image, so that the server is always deployable from a known-good state.

GitHub Actions runs lint, type-check, and unit tests on every push. It also builds the Docker image and runs integration tests via Testcontainers. On merge to `main` or a version tag push, it pushes the image to Docker Hub tagged as `latest` or the version number respectively.

## Spec Scope

1. **MCP Tool Suite** - Expose all OANDA V20 domains as MCP tools: account, instruments, pricing, orders, trades, positions, and transactions.
2. **FastMCP HTTP/SSE Server** - Run as a persistent HTTP service on a configurable port (`MCP_PORT`, default 8000), using FastMCP's streamable HTTP transport.
3. **OANDA V20 Client** - Async httpx client that targets OANDA V20 REST API (`/v3/` paths only), switching between practice and live base URLs via `OANDA_ENVIRONMENT`.
4. **Docker Packaging** - Multi-stage Dockerfile producing a lean `python:3.11-slim` image; `docker-compose.yml` for local manual testing.
5. **Test Pyramid** - Unit tests (mocked client), integration tests (Testcontainers), and a local-only smoke test (`task smoke-test`) that hits the live OANDA practice endpoint read-only.
6. **GitHub Actions CI/CD** - Build and test on every branch/PR; push to Docker Hub on `main` merges and version tags only.

## Out of Scope

- OANDA v1 API — all endpoints use `/v3/` paths exclusively
- Streaming prices or events (OANDA streaming endpoints)
- Multi-account support — single account ID from config only
- Order types beyond Market, Limit, and Stop (with TakeProfit, StopLoss, TrailingStop as dependent orders)
- Smoke test running in CI — local only, can be wired in later
- Authentication beyond API key (OAuth etc.)

## Expected Deliverables

1. `uv run pytest tests/unit/ tests/integration/` passes fully in CI with no live credentials required for integration tests (practice environment via Testcontainers).
2. `docker compose up` starts the MCP server locally and an agent can call `get_account_summary` successfully against the OANDA practice environment.
3. A Docker image is published to Docker Hub on every merge to `main`, tagged `latest` and with the commit SHA or version tag.
