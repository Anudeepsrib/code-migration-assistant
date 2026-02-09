# Code Migration Skill

This skill provides automated code migration capabilities for AI agents and developers.

## Features

- **React Hooks**: Automated conversion of Class components.
- **Safety First**: Atomic writes, path validation, and automatic backups.
- **CLI Interface**: Rich terminal output for easy usage.

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

## Usage

### CLI Usage

The skill includes a powerful CLI tool `migrate.py`.

```bash
# Analyze a file
python scripts/migrate.py analyze src/components/Button.jsx --type react-hooks

# Run migration (Dry Run)
python scripts/migrate.py run src/components/Button.jsx --type react-hooks --dry-run

# Execute migration
python scripts/migrate.py run src/components/Button.jsx --type react-hooks
```

### Configuration

Security settings can be configured in `config/security_config.yaml`.

## Adding New Migrators

See [CONTRIBUTING.md](CONTRIBUTING.md) for a guide on implementing new migration logic.
