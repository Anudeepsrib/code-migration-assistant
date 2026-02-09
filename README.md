# Code Migration Assistant

[![Build Status](https://img.shields.io/github/workflow/status/anudeepsrib/code-migration-assistant/CI)](https://github.com/anudeepsrib/code-migration-assistant/actions)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Agent Skills Standard](https://img.shields.io/badge/Agent_Skills-Standard-green)](https://agentskills.io)

Enterprise-grade, security-first code migration tool with AI-powered risk assessment, visual planning, and surgical rollback capabilities.

## Features

### Security-First Architecture
- **OWASP A03:2021 Compliance**: Injection prevention and input validation.
- **CWE-22 Protection**: Path traversal prevention with whitelist approach.
- **Zero Code Execution**: AST-only analysis with sandboxed processing.
- **Atomic File Operations**: No partial corruption with automatic backups.
- **Comprehensive Audit Logging**: GDPR/HIPAA/SOC2 compliant audit trails.
- **Rate Limiting**: DoS prevention with token bucket algorithm.

### Migration Co-pilot (AI + RAG)
- **Natural Language Chat**: Interactive AI assistance for migration guidance.
- **RAG Knowledge Retrieval**: Context-aware responses with semantic search.
- **Pattern Recognition**: Automatic detection of migration patterns.
- **Code Analysis**: AI-powered issue identification and recommendations.

### Live Migration Mode
- **Canary Deployments**: Gradual traffic splitting with health monitoring.
- **Auto-Rollback**: Automatic rollback on failure detection.
- **Health Checking**: Real-time endpoint monitoring with alerting.

### Test Generation Engine
- **Automated Test Creation**: Generate unit, integration, and E2E tests.
- **Coverage Analysis**: Line, branch, and function coverage tracking.
- **Mock Generation**: Automated mocking for dependencies and APIs.

### Visual Migration Planner
- **Interactive Graphs**: Dependency visualization using D3.js.
- **Migration Wave Planning**: Dependency ordering based on topological sort.
- **Timeline Builder**: Gantt chart migration scheduling.

### Time Machine Rollback
- **Git-Based Checkpoints**: Automatic snapshots with integrity verification.
- **Surgical Rollback**: Selective file restoration.
- **One-Command Recovery**: Instant rollback to any checkpoint.

### Comprehensive Compliance Suite
- **PII Detection**: GDPR/HIPAA/PCI-DSS compliance scanning.
- **Data Lineage**: Complete data flow analysis and mapping.
- **Audit Reports**: Generate compliance reports.

## Installation

### Prerequisites
- Python 3.8+
- Git (for rollback functionality)
- 8GB+ RAM (recommended for large codebases)

### Steps

```bash
# Clone the repository
git clone https://github.com/anudeepsrib/code-migration-assistant.git
cd code-migration-assistant

# Install dependencies
pip install -r requirements.txt

# Install security dependencies
pip install -r requirements-security.txt

# Verify installation
python -m code_migration --version
```

## Usage

```bash
# Analyze migration confidence
migrate analyze ./my-project --type react-hooks --confidence

# Visual migration planning
migrate visualize ./my-project --output migration-graph.html

# Live migration with canary deployment
migrate live-migration ./my-project --type react-hooks --canary --auto-rollback

# Generate tests
migrate generate-tests ./src/components --type react-hooks

# AI co-pilot assistance
migrate copilot ./my-project

# Compliance scanning
migrate compliance scan ./my-project --pii --secrets
```

## Supported Migrations

| Migration Type | Source | Target | Status | Confidence Score |
|----------------|--------|--------|--------|-----------------|
| `react-hooks` | React Class Components | Functional Components + Hooks | Enterprise | 85-95% |
| `vue3` | Vue 2 Options API | Vue 3 Composition API | Enterprise | 80-90% |
| `python3` | Python 2.7 | Python 3.x | Enterprise | 90-98% |
| `typescript` | JavaScript | TypeScript | Beta | 70-85% |
| `graphql` | REST APIs | GraphQL Schemas | Planned | - |
| `angular` | AngularJS | Angular 2+ | Planned | - |

## Documentation

- [User Guide](docs/USER_GUIDE.md) - Complete usage documentation.
- [Installation Guide](docs/INSTALLATION.md) - Detailed setup instructions.
- [Security Policy](docs/security/SECURITY.md) - Security architecture and controls.
- [Contributing Guide](CONTRIBUTING.md) - Development guidelines.
- [Architecture](README.md#-architecture) - System architecture overview.


## Testing

```bash
# Run security tests
pytest tests/security/

# Run compliance tests
pytest tests/compliance/

# Run integration tests
pytest tests/integration/

# Run all tests
pytest tests/
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](skills/code-migration/CONTRIBUTING.md) for details on how to add new migration types and features.

## License

This project is licensed under the Apache-2.0 License - see the [LICENSE](LICENSE) file for details.
