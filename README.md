<div align="center">
  <img src="public/shiftiq_logo.png" alt="ShiftIQ Logo" width="150" style="border-radius: 20%; margin-bottom: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);" />
  
  <h1 style="margin-top: 0;">ShiftIQ ⚡</h1>
  
  <p><b>"Analyze it. Migrate it. Own it. Your codebase never leaves your machine."</b></p>
  
  <p>An enterprise-grade, security-first code migration assistant with AI-powered risk assessment, visual dependency planning, surgical rollback, and regulatory compliance scanning.</p>

  <p>
    <a href="https://github.com/Anudeepsrib/code-migration-assistant">
      <img src="https://img.shields.io/github/stars/Anudeepsrib/code-migration-assistant?style=for-the-badge&logo=github" alt="GitHub stars" />
    </a>
    <a href="https://github.com/Anudeepsrib/code-migration-assistant">
      <img src="https://img.shields.io/github/forks/Anudeepsrib/code-migration-assistant?style=for-the-badge&logo=github" alt="GitHub forks" />
    </a>
    <a href="https://github.com/Anudeepsrib/code-migration-assistant/blob/main/LICENSE">
      <img src="https://img.shields.io/github/license/Anudeepsrib/code-migration-assistant?style=for-the-badge" alt="License" />
    </a>
    <a href="https://github.com/Anudeepsrib/code-migration-assistant/actions/workflows/ci.yml">
      <img src="https://img.shields.io/github/actions/workflow/status/Anudeepsrib/code-migration-assistant/ci.yml?style=for-the-badge&logo=githubactions&label=CI" alt="CI Status" />
    </a>
  </p>

  <p>
    <a href="#-core-features">Features</a> •
    <a href="#-quick-start">Quick Start</a> •
    <a href="#%EF%B8%8F-tech-stack">Tech Stack</a> •
    <a href="#-mcp-integration">MCP</a> •
    <a href="#-cli-reference">CLI</a>
  </p>
  
  <a href="https://github.com/Anudeepsrib/code-migration-assistant">
    <img src="https://github-readme-stats.vercel.app/api/pin/?username=Anudeepsrib&repo=code-migration-assistant&theme=radical&show_owner=true" alt="Readme Card" />
  </a>
</div>

---

## 🔒 The Security-First Promise

ShiftIQ is built on the philosophy of zero-trust code analysis. Your source code never leaves your machine, and no line of your code is ever executed during analysis.

<table>
  <tr>
    <td width="50%" valign="top">
      <h3>🧩 Sandboxed AST Parsing</h3>
      <p>All analysis uses Python's Abstract Syntax Tree — your legacy code is parsed, <b>never executed</b>. Zero runtime side-effects, guaranteed.</p>
    </td>
    <td width="50%" valign="top">
      <h3>🛡️ Injection Prevention</h3>
      <p>Built-in path traversal guards, input sanitization, and allowlist-only file access. Hardened against adversarial codebases.</p>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <h3>📋 Regulatory Compliance</h3>
      <p>Integrated PII/PHI scanners for <b>GDPR, HIPAA, PCI-DSS</b>. Detects SSNs, medical IDs, credit cards, and 15+ sensitive data markers with auto-anonymization.</p>
    </td>
    <td width="50%" valign="top">
      <h3>⏪ Surgical Rollback</h3>
      <p>Atomic Git snapshots before every migration. Revert per-file or per-checkpoint — a true <b>Git Time Machine</b> for your codebase.</p>
    </td>
  </tr>
</table>

---

## ✨ Core Features

<table>
  <tr>
    <td width="33%" valign="top">
      <b>📊 Confidence Analyzer</b><br/>
      Scores cyclomatic complexity, API surface area, and dependency health. Assigns risk levels from LOW to CRITICAL before a single line is touched.
    </td>
    <td width="33%" valign="top">
      <b>🕸️ Visual Dependency Graph</b><br/>
      Interactive NetworkX & D3.js visualizations. See the blast radius, topological migration waves, and dependency constraints in your browser.
    </td>
    <td width="33%" valign="top">
      <b>🤖 AI Co-pilot & RAG</b><br/>
      Context-aware migration queries grounded against your actual workspace codebase. Powered by local LLMs via the MCP protocol.
    </td>
  </tr>
  <tr>
    <td width="33%" valign="top">
      <b>💰 Cost Estimator</b><br/>
      Projects ROI with sprint-level breakdowns. Know the engineering hours before you commit to the migration.
    </td>
    <td width="33%" valign="top">
      <b>🧪 Test Scaffolding</b><br/>
      Auto-generates unit, integration, and mock tests from AST analysis over modified files. Safety nets, automated.
    </td>
    <td width="33%" valign="top">
      <b>🚦 Live Canary Migration</b><br/>
      A/B traffic splitting with health checks and auto-revert on latency spikes. Ship with confidence, not prayers.
    </td>
  </tr>
</table>

---

## 🚀 Quick Start

Get up and running locally in under 5 minutes.

### 1. Clone & Install
```bash
git clone https://github.com/Anudeepsrib/code-migration-assistant.git
cd code-migration-assistant
pip install -r requirements.txt
pip install -e .
```

### 2. Launch the Dashboard
Launch two terminal windows to start the backend engine and frontend interface.

**Terminal 1 — FastAPI Backend (localhost:8000):**
```bash
uvicorn code_migration.api.app:app --reload
```

**Terminal 2 — React + Vite Frontend (localhost:5173):**
```bash
cd ui
npm install
npm run dev
```

### 3. Or, Use the CLI
```bash
# Analyze a project for migration readiness
migrate analyze ./my-project --type react-hooks --confidence

# Visualize dependency graph
migrate visualize ./my-project

# Dry-run a migration
migrate run ./my-project --type react-hooks --dry-run
```

Open [http://localhost:5173](http://localhost:5173) to access the real-time dashboard.

---

## 🛠️ Tech Stack

<table>
  <tr>
    <th width="50%">Frontend (Dashboard)</th>
    <th width="50%">Backend (Analysis Engine)</th>
  </tr>
  <tr>
    <td valign="top">
      <ul>
        <li><b>Framework:</b> React 18 + Vite 5</li>
        <li><b>Styling:</b> Glassmorphic Vanilla CSS</li>
        <li><b>Streaming:</b> SSE (Server-Sent Events)</li>
        <li><b>Visualization:</b> D3.js + NetworkX</li>
        <li><b>Language:</b> TypeScript</li>
      </ul>
    </td>
    <td valign="top">
      <ul>
        <li><b>API:</b> FastAPI + Uvicorn</li>
        <li><b>Analysis:</b> Python AST (sandboxed)</li>
        <li><b>CLI:</b> Typer + Rich</li>
        <li><b>AI Protocol:</b> MCP (Model Context Protocol)</li>
        <li><b>Logging:</b> Structlog</li>
        <li><b>Config:</b> Pydantic Settings + YAML</li>
      </ul>
    </td>
  </tr>
</table>

---

## 🔌 MCP Integration

ShiftIQ ships with a built-in [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server, allowing AI applications like Claude Desktop, VS Code Copilot, and Cursor to invoke migration tools directly.

### Available MCP Tools

| Tool | Description |
|------|-------------|
| `analyze` | Evaluate codebase complexity, risk level, and cost estimates |
| `run_migration` | Execute AST-based code migrations (dry-run by default) |
| `compliance_scan` | Scan for PII/PHI (GDPR, HIPAA, PCI-DSS) |
| `visualize` | Generate dependency graphs and migration-wave plans |
| `rollback` | Create or restore rollback checkpoints |

### Connect from Claude Desktop

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

### Connect from VS Code / Cursor

Add to your workspace `.vscode/mcp.json`:
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

### Test Locally
```bash
pip install -e .
mcp dev src/code_migration/mcp_server.py
```

See [`mcp.json`](mcp.json) for a ready-to-use configuration template.

---

## 🧠 Supported Migrations

| Migration Type | Target | Description |
|----------------|--------|-------------|
| **React Hooks** | `react-hooks` | Class Component API → Functional Hooks rewrite |
| **Vue 3 Composition** | `vue3` | Vue 2 Options API → Composition API |
| **Python 3** | `python3` | Python 2.7 → 3.x modernization |
| **Custom** | `marketplace` | Extensible plugin registry for TypeScript, GraphQL, and more |

---

## ⌨️ CLI Reference

All commands use the `migrate` entrypoint:

| Command | Description |
|---------|-------------|
| `migrate analyze [path]` | Evaluate files, score complexity, report candidate lists |
| `migrate visualize [path]` | Export interactive HTML dependency maps |
| `migrate run [path] --type [id]` | Invoke AST rewrites (`--dry-run` to preview) |
| `migrate live-migration [path]` | Execute with A/B canaries and auto-revert |
| `migrate generate-tests [path]` | Emit safety scaffolding (tests & mocks) |
| `migrate compliance scan [path]` | Scan for regulatory violations |
| `migrate rollback [checkpoint]` | Revert repository state to a checkpoint |

---

## 🐳 Docker

Run the full analysis engine in a container:

```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000` with health checks at `/healthz`.

---

## 🧪 Testing

ShiftIQ enforces four tiers of testing protocols:

| Tier | Command | Scope |
|------|---------|-------|
| **Fast & Unit** | `pytest -m "not slow"` | Core logic and AST parsers |
| **Security** | `pytest tests/security/` | Path traversal & injection prevention |
| **Compliance** | `pytest tests/compliance/` | PII/PHI scanner validation |
| **Performance** | `pytest tests/performance/` | Large-file stress tests (8GB+ RAM) |

Configure timeouts via `pytest.ini`.

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [Setup & Prerequisites](docs/INSTALLATION.md) | Full installation and dependency guide |
| [User Guide](docs/USER_GUIDE.md) | Comprehensive usage documentation |
| [Security Model](docs/security/SECURITY.md) | Threat model, policies, and compliance |
| [Architecture Overview](docs/ARCHITECTURE.md) | System design and sequence flows |
| [Plugin Developer Guide](docs/PLUGIN_GUIDE.md) | Build custom migration plugins |
| [Contributing](CONTRIBUTING.md) | PR formatting, guidelines, and standards |
| [Skill Manifest](SKILL.md) | Agent integration specification |

---

## ⚠️ Disclaimer
**For Development Use Only:** ShiftIQ is an open-source development tool. While it includes compliance scanners, it does **not** replace professional security audits or legal compliance reviews. Always validate migration outputs with your team before deploying to production.

---

<div align="center">
  <p>Built with ⚡ for teams that modernize codebases with confidence.</p>
  <p>
    <a href="https://github.com/Anudeepsrib/code-migration-assistant">
      <img src="https://img.shields.io/badge/Apache--2.0-License-blue?style=flat-square" alt="License" />
    </a>
  </p>
</div>
