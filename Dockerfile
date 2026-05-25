# --------------------------------------------------------------------------- #
# Builder — install uv and sync all production dependencies                   #
# --------------------------------------------------------------------------- #
FROM python:3.13-slim AS builder

WORKDIR /app

# Install uv from its official image layer
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install runtime deps first (layer-cached separately from source code)
# README.md is required by hatchling to build the package metadata
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev --no-install-project

# Copy source, then install the project itself into the venv
COPY src/ src/
RUN uv sync --frozen --no-dev

# --------------------------------------------------------------------------- #
# Runtime — minimal image, non-root user                                      #
# --------------------------------------------------------------------------- #
FROM python:3.13-slim AS runtime

WORKDIR /app

# Create non-root user
RUN groupadd --gid 1000 appgroup \
    && useradd --uid 1000 --gid appgroup --no-create-home appuser

# Copy venv and source from builder (editable install references src/ directly)
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

USER appuser

ARG MCP_PORT=8000
EXPOSE ${MCP_PORT}

CMD ["python", "-m", "oanda_mcp.server"]
