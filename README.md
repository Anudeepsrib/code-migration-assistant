# Code Migration Assistant

[![Build Status](https://img.shields.io/github/workflow/status/yourusername/code-migration-assistant/CI)](https://github.com/yourusername/code-migration-assistant/actions)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Agent Skills Standard](https://img.shields.io/badge/Agent_Skills-Standard-green)](https://agentskills.io)

> Intelligent AI-powered code migration across frameworks and languages. Secure, extensible, and production-ready.

## Features

- 🚀 **Fast Automated Migrations**: AST-based transformations for React, Python, Vue, and more.
- 🔒 **Enterprise-Grade Security**: Strict input validation, safe file operations, and no unsafe execution.
- 📊 **Detailed Reporting**: Comprehensive migration reports with before/after diffs.
- 🎨 **Beautiful CLI**: Rich terminal output with progress bars and interactive prompts.
- 🧩 **Extensible**: Plugin system to add custom migration logic easily.

## Quick Start

### Installation

```bash
# Via pip (Python)
pip install code-migration-assistant

# Via Skills CLI (for AI Agents)
npx skills add yourusername/code-migration-assistant --skill code-migration
```

### Usage

```bash
# Analyze a project
migrate analyze src/ --type react-hooks

# Run a migration (dry run)
migrate run src/components/ --type react-hooks --dry-run
```

## Supported Migrations

| Migration Type | Source | Target | Status |
|----------------|--------|--------|--------|
| `react-hooks` | React Class Components | Functional Components + Hooks | ✅ Stable |
| `python3` | Python 2.7 | Python 3.x | 🚧 Beta |
| `vue3` | Vue 2 Options API | Vue 3 Composition API | 📅 Planned |
| `typescript` | JavaScript | TypeScript | 📅 Planned |

## Documentation

- [User Guide](skills/code-migration/docs/usage.md)
- [Installation](skills/code-migration/docs/installation.md)
- [Security Policy](.github/SECURITY.md)
- [Contributing](skills/code-migration/CONTRIBUTING.md)

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](skills/code-migration/CONTRIBUTING.md) for details on how to add new migration types.

## License

This project is licensed under the Apache-2.0 License - see the [LICENSE](LICENSE) file for details.
