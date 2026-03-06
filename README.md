# Code Migration Assistant

**Enterprise-grade, security-first code migration tool** with AI-powered risk assessment, visual dependency planning, surgical rollback, and regulatory compliance scanning. Designed for teams that need to modernize large codebases with confidence — not guesswork.

[![CI](https://github.com/anudeepsrib/code-migration-assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/anudeepsrib/code-migration-assistant/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Agent Skills Standard](https://img.shields.io/badge/Agent_Skills-Standard-green)](https://agentskills.io)

---

## Highlights

- **[Live Dashboard](docs/USER_GUIDE.md#dashboard)** — real-time web UI powered by FastAPI and React with SSE log streaming.
- **[Security-first AST Analysis](docs/security/SECURITY.md)** — zero code execution, sandboxed Python AST parsing, and injection prevention.
- **[Visual Dependency Graph](docs/USER_GUIDE.md#visualize)** — build interactive NetworkX & D3.js project dependency nodes to see the blast radius before executing.
- **[Git Time Machine](docs/USER_GUIDE.md#rollback)** — atomic snapshots and surgical rollback support per-file.
- **[Regulatory Compliance](docs/security/SECURITY.md#compliance)** — out-of-the-box PII/PHI detection (GDPR, HIPAA, PCI-DSS) integrated directly into the migration stream.
- **[AI Co-pilot + RAG](docs/USER_GUIDE.md#copilot)** — context-aware migration queries mapped against your actual workspace codebase.

## Everything we built so far

### Core Platform
- **[Confidence Analyzer](docs/USER_GUIDE.md#analyze)** with cyclomatic complexity scoring, API surface evaluation, and risk assignments (LOW to CRITICAL).
- **[Cost Estimator](docs/USER_GUIDE.md#cost)** to project return on investment (ROI) with sprint planning breakdowns.
- **[Task Scaffolding](docs/USER_GUIDE.md#tests)** with automated unit, integration, and mock generation based on abstract syntax trees.
- **[Live Canary Migration](docs/USER_GUIDE.md#live-migration)** with traffic splitting, health checks, and automated reversion on latency spikes.

### Analyzers & Migrators 
- **React-Hooks Migration**: `react-hooks` targeting functional rewrites of Class API.
- **Vue Composition Migration**: `vue3` targeting Vue 2 Option API.
- **Python Modernization**: `python3` targeting Python 2.7 to 3.x transitions.
- **Extensible Registry**: A customizable `marketplace` pattern architecture allows easy injections of TypeScript and GraphQL rules.

### Interfaces
- **Web Dashboard**: Deep integrations across FastAPI, `sse-starlette`, React, Vite, and glassmorphic Vanilla CSS. `python -m code_migration.web`.
- **Rich Typer CLI**: Built-in terminal commands with rich console outputs and `[Dry Run]` previews.
- **MCP Server**: Model Context Protocol server for AI application integration (Claude Desktop, VS Code, Cursor, etc.).

---

## How it works (short)

```text
 Legacy Repository (React, Vue, Python)
                   │
                   ▼
  ┌─────────────────────────────────┐
  │ Code Migration Assistant        │
  │ (AST Parsers & Risk Analyzers)  │
  └─────────────┬───────────────────┘
                │
 ├─ Live Dashboard (localhost:8000)
 ├─ Typer CLI (migrate run ...)
 ├─ MCP Server (stdio transport)
 ├─ Visualizer Graph (D3.js)
 └─ Core Engine (Rollbacks / Security / Tests)
```

## Key subsystems

- **[Confidence Core](docs/USER_GUIDE.md#analyze)** — scores codebase complexity and dependency health prior to any execution.
- **[Visual Planner](docs/USER_GUIDE.md#visualize)** — implements topological sorts to define the exact order ("waves") of modules to migrate based on dependency constraints.
- **[FastAPI Control Plane](src/code_migration/web.py)** — unidirectional `EventSourceResponse` wrapping standard CLI functions for UI streaming.
- **[Compliance Suite](docs/security/SECURITY.md)** — regex pattern and heuristic scanning for over 15+ sensitive data markers (SSN, medical ids, credit cards) with auto-anonymization.

---

## Quick Start (Installation)

1. Clone and install the application:
```bash
git clone https://github.com/anudeepsrib/code-migration-assistant.git
cd code-migration-assistant
pip install -r requirements.txt
pip install -e .
```

2. Start the real-time Web Dashboard:
```bash
python -m code_migration.web
# Access the UI via browser at http://localhost:8000
```

3. Alternatively, invoke the CLI for an analysis:
```bash
migrate analyze ./my-project --type react-hooks --confidence
```

---

## MCP Integration

The Code Migration Assistant ships with a built-in [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server, allowing AI applications to use migration tools directly.

### Available MCP Tools

| Tool | Description |
|------|-------------|
| `analyze` | Evaluate codebase complexity, risk level, and cost estimates |
| `run_migration` | Execute AST-based code migrations (dry-run by default) |
| `compliance_scan` | Scan for PII/PHI (GDPR, HIPAA, PCI-DSS) |
| `visualize` | Generate dependency graphs and migration-wave plans |
| `rollback` | Create or restore rollback checkpoints |

### Quick Start (MCP)

```bash
# Install with MCP support
pip install -e .

# Test the server locally with the MCP inspector
mcp dev src/code_migration/mcp_server.py
```

### Connecting from Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "code-migration-assistant": {
      "command": "python",
      "args": ["-m", "code_migration.mcp_server"],
      "cwd": "/path/to/code-migration-assistant"
    }
  }
}
```

### Connecting from VS Code / Cursor

Add to your workspace `.vscode/mcp.json` (or Cursor equivalent):

```json
{
  "mcpServers": {
    "code-migration-assistant": {
      "command": "python",
      "args": ["-m", "code_migration.mcp_server"],
      "cwd": "${workspaceFolder}"
    }
  }
}
```

### Connecting Programmatically

Any MCP-compatible client can connect by spawning the process:

```python
# Example with mcp client SDK
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

server_params = StdioServerParameters(
    command="python",
    args=["-m", "code_migration.mcp_server"],
)

async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        tools = await session.list_tools()
        result = await session.call_tool("analyze", {
            "path": "/path/to/project",
            "migration_type": "react-hooks"
        })
```

See [`mcp.json`](mcp.json) for a ready-to-use configuration template.

---

## CLI Options

Code Migration Assistant operates strictly on command signatures with the `migrate` entrypoint.

- `migrate analyze [path]` — evaluate files, score complexity, report candidate lists.
- `migrate visualize [path]` — export interactive HTML network dependency maps.
- `migrate run [path] --type [id]` — invoke AST rewrites (append `--dry-run` to preview).
- `migrate live-migration [path]` — execute with A/B canaries and auto-revert protocols.
- `migrate generate-tests [path]` — emit safety scaffolding (tests & mocks) over modified files.
- `migrate compliance scan [path]` — scan for regulatory violations.
- `migrate rollback [checkpoint]` — revert repository state.

---

## Operations & Testing
OpenClaw architectures respect high-fidelity observability and rigorous testing matrices. Code Migration Assistant enforces four tiers of testing protocols.

- **Fast & Unit:** `pytest -m "not slow"`
- **Security Control:** `pytest tests/security/` (prevents path traversing & injections)
- **Compliance:** `pytest tests/compliance/` (validates PII/PHI scanners)
- **Performance Stress:** `pytest tests/performance/` (8GB+ RAM requested for large file volume generation)

Configure timeouts natively via `pytest.ini`.

---

## Docs & Deep Dives

Use these when you're past the onboarding flow and want the deeper reference. 

- [Setup & Prerequisites](docs/INSTALLATION.md)
- [Comprehensive User Usage Guide](docs/USER_GUIDE.md)
- [Security Threat Model & Policy](docs/security/SECURITY.md)
- [Skill Integration Manifest](SKILL.md)
- [Contributing Standards](CONTRIBUTING.md)

## License & Community

This project is licensed under the **Apache License 2.0**.
See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines, PR formatting instructions, and how to define custom migration classes.
