# Code Migration Assistant

[![CI](https://github.com/anudeepsrib/code-migration-assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/anudeepsrib/code-migration-assistant/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Agent Skills Standard](https://img.shields.io/badge/Agent_Skills-Standard-green)](https://agentskills.io)

**Enterprise-grade, security-first code migration tool** with AI-powered risk assessment, visual dependency planning, surgical rollback, and regulatory compliance scanning. Designed for teams that need to modernize large codebases with confidence — not guesswork.

---

## Table of Contents

- [Why Code Migration Assistant?](#why-code-migration-assistant)
- [Architecture Overview](#architecture-overview)
- [Core Capabilities](#core-capabilities)
- [Supported Migrations](#supported-migrations)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

---

## Why Code Migration Assistant?

Migrating legacy codebases is one of the highest-risk engineering activities. A single missed dependency, an uncaught breaking change, or an incomplete rollback can cascade into production outages, data loss, or compliance violations.

**Code Migration Assistant** eliminates that risk by combining:

- 🔒 **Security-first AST analysis** — zero code execution, ever
- 📊 **Quantified confidence scoring** — know your risk before you start
- 🗺️ **Visual dependency graphs** — see the blast radius of every change
- ⏪ **Git-based time-machine rollback** — surgical undo at any checkpoint
- 🛡️ **Regulatory compliance scanning** — GDPR, HIPAA, PCI-DSS, SOC2 out of the box
- 🤖 **AI co-pilot with RAG** — context-aware migration guidance via natural language
- 💰 **Cost & ROI estimation** — executive-ready reports and budget planning

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        CLI Interface                        │
│                    (Typer + Rich Console)                    │
├─────────────┬───────────┬───────────┬───────────┬───────────┤
│  Analyzers  │ Migrators │  Copilot  │  Visualizer│Cost Est. │
│  (AST-based)│ (React,   │  (AI+RAG) │  (D3.js,  │(ROI,     │
│             │  Vue, Py) │           │  NetworkX) │ Budget)  │
├─────────────┴───────────┴───────────┴───────────┴───────────┤
│                        Core Engine                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────────┐ │
│  │ Security │ │Compliance│ │ Rollback │ │ Live Migration │ │
│  │ Module   │ │  Suite   │ │  Engine  │ │  (Canary/A-B)  │ │
│  └──────────┘ └──────────┘ └──────────┘ └────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                    Test Generation Engine                    │
│              (Unit, Integration, E2E + Mocks)               │
└─────────────────────────────────────────────────────────────┘
```

The system is organized into **10 independent core modules**, each with a single responsibility and clean interfaces:

| Module | Purpose |
|--------|---------|
| `security` | Input validation, path sanitization, sandboxed AST analysis, secrets detection, audit logging, rate limiting |
| `compliance` | PII/PHI detection, data lineage tracking, anonymization, audit reporting |
| `confidence` | Pre-migration risk scoring, complexity calculation, cost & time estimation |
| `copilot` | AI chat interface with RAG knowledge retrieval for migration guidance |
| `cost_estimator` | Migration cost calculation, ROI analysis, executive reporting, budget planning |
| `live_migration` | Canary deployments, auto-rollback, health checking, monitoring |
| `rollback` | Git-based checkpoints, snapshot management, selective file restoration |
| `test_generation` | Automated test creation, coverage analysis, mock generation, templates |
| `visualizer` | Dependency graph building, migration wave planning, timeline visualization |
| `marketplace` | Migration pattern marketplace (extensible) |

---

## Core Capabilities

### 🔒 Security-First Architecture

Every operation passes through a hardened security layer before touching the filesystem.

| Control | Standard | Implementation |
|---------|----------|---------------|
| Injection Prevention | OWASP A03:2021 | Input validation on all user-supplied paths and parameters |
| Path Traversal Protection | CWE-22 | Whitelist-based path sanitization with symlink resolution |
| Static Analysis Only | — | Python `ast` module for parsing; **no code is ever executed** |
| Atomic File Operations | — | Write-rename pattern prevents partial corruption |
| Audit Logging | SOC2 / GDPR / HIPAA | Append-only JSON structured logs with 90-day configurable retention |
| Rate Limiting | — | Token bucket algorithm for DoS prevention |
| Secrets Detection | — | Pre-commit scanning for API keys, tokens, and credentials |

### 📊 Migration Confidence Analyzer

Before any migration begins, the confidence analyzer produces a **quantified risk assessment**:

- **Codebase complexity scoring** — cyclomatic complexity across all files
- **Dependency health evaluation** — outdated, deprecated, or vulnerable packages
- **Breaking change estimation** — identifies API surfaces at risk
- **Test coverage evaluation** — flags under-tested migration targets
- **Cost and time predictions** — hours and dollar estimates by file, module, and project

Output: a `ConfidenceScore` object with `overall_score` (0–100), `risk_level` (LOW / MEDIUM / HIGH / CRITICAL), `estimated_hours`, and `estimated_cost`.

### 🗺️ Visual Migration Planner

Transforms your codebase into an interactive dependency graph:

- **Dependency graph construction** using NetworkX — nodes represent files, edges represent imports
- **Topological sort** produces ordered **migration waves** — files with no downstream dependents migrate first
- **Gantt chart scheduling** — timeline visualization for project management
- **D3.js export** — interactive HTML graphs for stakeholder review

### ⏪ Time Machine Rollback

Git-based checkpoint system with surgical precision:

- **Automatic checkpoints** — full project snapshot before any migration step
- **Integrity verification** — SHA-256 checksums on every snapshot
- **Selective rollback** — restore individual files without reverting the entire project
- **One-command recovery** — `migrate rollback <checkpoint-id>` restores instantly
- **Checkpoint listing** — browse all snapshots with timestamps and descriptions

### 🤖 Migration Co-pilot (AI + RAG)

Interactive AI assistant for migration guidance:

- **Natural language chat** — ask questions about migration patterns, best practices, and tradeoffs
- **RAG knowledge retrieval** — semantic search over migration documentation and patterns
- **Pattern recognition** — automatic detection of migration-relevant code patterns
- **Context-aware recommendations** — suggestions grounded in your actual codebase

### 🚀 Live Migration Mode

Production-safe migration with traffic management:

- **Canary deployments** — gradual traffic splitting (e.g., 5% → 25% → 100%)
- **Health monitoring** — real-time endpoint checks with configurable thresholds
- **Auto-rollback** — automatic revert on error rate or latency spikes
- **Observability** — structured metrics and alerting throughout the migration

### 🧪 Test Generation Engine

Automated test scaffolding for migrated code:

- **Unit test generation** — creates test cases based on function signatures and AST analysis
- **Integration test templates** — API and service-level test scaffolds
- **Mock generation** — automated mocking for external dependencies and APIs
- **Coverage tracking** — line, branch, and function coverage analysis

### 🛡️ Compliance Suite

Regulatory scanning built for regulated industries:

- **PII Detection** — email, SSN, phone, credit card, passport, driver's license, IP address, date of birth, address
- **PHI Detection** — medical record numbers, diagnosis codes (ICD-9/10), patient IDs, CPT codes, health insurance numbers
- **Regulation mapping** — each finding is tagged with GDPR, HIPAA, PCI-DSS, or CCPA
- **Severity classification** — CRITICAL / HIGH / MEDIUM / LOW with confidence scores
- **Data lineage tracking** — complete data flow analysis and mapping
- **Compliance reports** — formatted reports ready for audit review

### 💰 Cost Estimator & ROI Analyzer

Data-driven migration budgeting:

- **Cost calculation** — per-file and per-module migration cost estimates
- **ROI analysis** — projected return on investment with break-even timeline
- **Executive reporting** — stakeholder-ready summaries with charts and metrics
- **Budget planning** — resource allocation recommendations by sprint/phase

---

## Supported Migrations

| Migration Type | Source | Target | Status | Confidence Score |
|:-:|:-:|:-:|:-:|:-:|
| `react-hooks` | React Class Components | Functional Components + Hooks | ✅ Enterprise | 85–95% |
| `vue3` | Vue 2 Options API | Vue 3 Composition API | ✅ Enterprise | 80–90% |
| `python3` | Python 2.7 | Python 3.x | ✅ Enterprise | 90–98% |
| `typescript` | JavaScript | TypeScript | 🧪 Beta | 70–85% |
| `graphql` | REST APIs | GraphQL Schemas | 📋 Planned | — |
| `angular` | AngularJS | Angular 2+ | 📋 Planned | — |

---

## Getting Started

### Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.8+ | CPython recommended |
| Git | 2.x+ | Required for rollback functionality |
| RAM | 8 GB+ | Recommended for large codebase analysis |

### Installation

```bash
# Clone the repository
git clone https://github.com/anudeepsrib/code-migration-assistant.git
cd code-migration-assistant

# Install core dependencies
pip install -r requirements.txt

# Install the package in editable mode
pip install -e .

# (Optional) Install development dependencies
pip install -e ".[dev]"

# Verify installation
python -m code_migration --version
```

### Environment Configuration

Copy the example environment file and configure as needed:

```bash
cp .env.example .env
```

---

## Usage

### Analyze Migration Confidence

```bash
# Get a risk assessment before starting any migration
migrate analyze ./my-project --type react-hooks --confidence
```

### Visualize Dependencies

```bash
# Generate an interactive dependency graph
migrate visualize ./my-project --output migration-graph.html
```

### Execute Migration

```bash
# Always dry-run first
migrate run ./my-project --type react-hooks --dry-run

# Execute with canary deployment and auto-rollback
migrate live-migration ./my-project --type react-hooks --canary --auto-rollback
```

### Generate Tests

```bash
# Scaffold tests for migrated components
migrate generate-tests ./src/components --type react-hooks
```

### Compliance Scanning

```bash
# Scan for PII and secrets
migrate compliance scan ./my-project --pii --secrets
```

### AI Co-pilot

```bash
# Interactive migration guidance
migrate copilot ./my-project
```

---

## Testing

The test suite is organized into four categories, each targeting a different quality dimension.

```bash
# Fast tests only (recommended during development)
pytest -m "not slow"

# Security tests — input validation, path traversal, injection prevention
pytest tests/security/

# Compliance tests — PII/PHI detection, regulatory scanning
pytest tests/compliance/

# Performance tests — large codebase analysis, concurrent throughput, memory usage
pytest tests/performance/

# Integration tests — end-to-end migration workflows
pytest tests/integration/

# Full suite
pytest tests/
```

### Test Configuration

Tests are configured via `pytest.ini` with the following defaults:

| Setting | Value | Description |
|---------|-------|-------------|
| `--timeout` | `300s` | Per-test timeout (configurable via `--timeout=<seconds>`) |
| `--cov` | `src/code_migration` | Coverage target |
| `--strict-markers` | enabled | Prevents typos in marker names |

Performance tests generate large temporary projects (1000+ files) and run compute-intensive analysis. They require:

- **8 GB+ RAM** — multiple analyzers run concurrently during stress tests
- **Adequate CPU** — regex scanning and AST parsing across many files
- **Sufficient timeout** — increase to `--timeout=600` on slower CI runners if needed

### Test Markers

| Marker | Description |
|--------|-------------|
| `slow` | Long-running tests (performance, complex integrations) |
| `performance` | Benchmarks, stress tests, memory profiling |
| `security` | Input validation, path traversal, injection prevention |
| `compliance` | PII/PHI detection, regulatory compliance |
| `integration` | End-to-end migration workflow tests |

---

## Project Structure

```
code-migration-assistant/
├── src/code_migration/
│   ├── analyzers/          # Language-specific AST analyzers
│   ├── cli.py              # Typer CLI entrypoint
│   ├── core/
│   │   ├── compliance/     # PII/PHI detection, audit reports, anonymization
│   │   ├── confidence/     # Risk scoring, complexity analysis
│   │   ├── copilot/        # AI chat, RAG system, knowledge base
│   │   ├── cost_estimator/ # ROI analysis, budget planning, executive reports
│   │   ├── live_migration/ # Canary deployment, health checks, auto-rollback
│   │   ├── marketplace/    # Migration pattern marketplace
│   │   ├── rollback/       # Git checkpoints, snapshot management
│   │   ├── security/       # Sandboxed analysis, path sanitization, audit logging
│   │   ├── test_generation/# Automated test scaffolding, mock generation
│   │   └── visualizer/     # Dependency graphs, migration waves, timelines
│   ├── migrators/          # Migration execution engines
│   └── utils/              # Shared utilities
├── tests/
│   ├── compliance/         # PII/PHI detection tests
│   ├── integration/        # End-to-end workflow tests
│   ├── performance/        # Stress tests and benchmarks
│   └── security/           # Security control validation
├── docs/
│   ├── INSTALLATION.md     # Detailed setup guide
│   ├── USER_GUIDE.md       # Comprehensive usage documentation
│   └── security/           # Security architecture and policies
├── .github/workflows/      # CI/CD pipeline
├── CONTRIBUTING.md          # Contribution guidelines
├── SKILL.md                 # Agent Skills Standard manifest
├── pyproject.toml           # Build configuration and dependencies
├── pytest.ini               # Test configuration
└── requirements.txt         # Runtime dependencies
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [User Guide](docs/USER_GUIDE.md) | Complete usage documentation with examples |
| [Installation Guide](docs/INSTALLATION.md) | Detailed setup instructions for all platforms |
| [Security Policy](docs/security/SECURITY.md) | Security architecture, threat model, and controls |
| [Contributing Guide](CONTRIBUTING.md) | Development setup, coding standards, and PR process |
| [Agent Skills Manifest](SKILL.md) | Integration specification for AI agent platforms |

---

## Contributing

We welcome contributions of all kinds — new migration types, security improvements, documentation, and bug fixes.

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Development environment setup
- Coding standards and style guide
- How to add a new migration type
- Pull request process and review expectations

---

## License

This project is licensed under the **Apache License 2.0** — see the [LICENSE](LICENSE) file for details.
