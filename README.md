# Claude Playground

A workspace for experimenting with Claude Code, configured with development standards and MCP tool integrations.

## Structure

```
.
├── .claude/
│   └── settings.json     # MCP server configuration for Claude Code
├── CLAUDE.md             # Project instructions auto-loaded by Claude Code
└── README.md
```

## Claude Code Configuration

### CLAUDE.md
Project-level instructions that Claude Code loads automatically on startup. Defines:
- Development standards (Python, uv, pytest, Docker, project structure)
- Mandatory MCP tool usage rules

### .mcp.json
MCP server definitions. Claude Code connects to these servers to give the agent access to external tools and services.

## MCP Servers

### Active (no configuration needed)

| Server | Package | Purpose |
|--------|---------|---------|
| context7 | `@upstash/context7-mcp` | Fetch current library documentation before writing code |
| fetch | `mcp-server-fetch` | Retrieve URLs and documentation pages |
| docker | `docker-mcp` | Manage Docker containers, images, and volumes |
| memory | `@modelcontextprotocol/server-memory` | Persist project decisions across sessions |
| playwright | `@playwright/mcp@latest` | Browser automation and end-to-end testing |

### Needs API key

| Server | Package | What to set |
|--------|---------|-------------|
| brave-search | `@modelcontextprotocol/server-brave-search` | `BRAVE_API_KEY` in `.mcp.json` — get a free key at [brave.com/search/api](https://brave.com/search/api/) |
| github | `@modelcontextprotocol/server-github` | `GITHUB_PERSONAL_ACCESS_TOKEN` in `.mcp.json` |
| alphavantage | `marketdata-mcp-server` | API key passed as the final argument to `marketdata-mcp` in `.mcp.json` |

## Prerequisites

- [Claude Code](https://claude.ai/claude-code) CLI installed
- [Node.js](https://nodejs.org) (for `npx`-based servers) — installed via Homebrew at `/opt/homebrew/bin/npx`
- [uv](https://docs.astral.sh/uv/) (for `uvx`-based servers) — installed via Homebrew at `/opt/homebrew/bin/uvx`
