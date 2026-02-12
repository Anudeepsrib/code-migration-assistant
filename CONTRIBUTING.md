# Contributing to Code Migration Assistant

Thank you for your interest in contributing! This guide covers everything you need to get started — from environment setup to pull request submission.

> **Related docs:** [README](README.md) · [User Guide](docs/USER_GUIDE.md) · [Installation Guide](docs/INSTALLATION.md) · [Security Policy](docs/security/SECURITY.md)

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Workflow](#development-workflow)
3. [Code Standards](#code-standards)
4. [Testing Guidelines](#testing-guidelines)
5. [Security Requirements](#security-requirements)
6. [Documentation](#documentation)
7. [Pull Request Process](#pull-request-process)
8. [Community Guidelines](#community-guidelines)

---

## Getting Started

### Prerequisites

- Python 3.8+
- Git 2.x+
- Familiarity with Python, AST analysis, and security best practices

### Environment Setup

```bash
# 1. Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/code-migration-assistant.git
cd code-migration-assistant

# 2. Add upstream remote
git remote add upstream https://github.com/anudeepsrib/code-migration-assistant.git

# 3. Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 4. Install with development dependencies
pip install -e ".[dev]"
```

### Verify Your Setup

```bash
# Run the test suite
pytest tests/ -v

# Run security linter
bandit -r src/code_migration/

# Run code formatter check
black --check src/code_migration/
isort --check-only src/code_migration/
```

All checks must pass before you submit a PR.

---

## Development Workflow

### 1. Create an Issue

Before starting, create a GitHub issue to track your work:
- **Bug reports** — use the bug report template
- **Feature requests** — use the feature request template
- **Documentation** — describe what's missing or incorrect

### 2. Create a Branch

```bash
# Sync with upstream
git fetch upstream
git checkout main
git merge upstream/main

# Branch naming convention:
git checkout -b feature/short-description    # New features
git checkout -b fix/issue-42-description     # Bug fixes
git checkout -b docs/update-user-guide       # Documentation
```

### 3. Make Your Changes

Follow the [Code Standards](#code-standards) and [Testing Guidelines](#testing-guidelines) below.

### 4. Commit

Use [Conventional Commits](https://www.conventionalcommits.org/):

```bash
git commit -m "feat: add Angular migration support"
git commit -m "fix: resolve path traversal edge case on Windows"
git commit -m "docs: update installation guide for Python 3.12"
git commit -m "test: add integration tests for rollback engine"
```

### 5. Push and Open a PR

```bash
git push origin feature/short-description
```

Then open a pull request on GitHub. Follow the [PR checklist](#pull-request-checklist).

---

## Code Standards

### Formatting

We use **Black** for formatting and **isort** for import sorting. Both run automatically if you install pre-commit hooks.

```bash
# Format
black src/code_migration/
isort src/code_migration/

# Check (CI will run these)
black --check src/code_migration/
isort --check-only src/code_migration/
flake8 src/code_migration/
```

### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Classes | PascalCase | `MigrationAnalyzer` |
| Functions / variables | snake_case | `calculate_confidence()` |
| Constants | UPPER_SNAKE_CASE | `MAX_FILE_SIZE` |
| Private members | Leading underscore | `self._internal_state` |
| Modules | snake_case | `path_sanitizer.py` |

### Type Hints

All public functions must include type hints:

```python
from typing import Dict, List, Optional
from pathlib import Path

def analyze_migration(
    project_path: Path,
    migration_type: str,
    options: Optional[Dict[str, str]] = None
) -> Dict[str, int]:
    """Analyze migration with type hints."""
    return {"status": 0, "files": 10}
```

### Docstrings

Use Google-style docstrings on all public classes and functions:

```python
def calculate_confidence_score(
    project_path: Path,
    migration_type: str,
    team_experience: int
) -> float:
    """Calculate migration confidence score.
    
    Args:
        project_path: Path to the project to analyze.
        migration_type: Type of migration (react-hooks, vue3, etc.).
        team_experience: Team experience level (0–100).
        
    Returns:
        Confidence score between 0 and 100.
        
    Raises:
        ValueError: If migration_type is not supported.
        FileNotFoundError: If project_path does not exist.
    """
    ...
```

### File Organization

```python
"""Module docstring."""

# Standard library imports
import ast
from pathlib import Path
from typing import Dict, List

# Third-party imports
import networkx as nx
import yaml

# Local imports
from code_migration.core.security import PathSanitizer

# Constants
DEFAULT_TIMEOUT = 300
MAX_FILE_SIZE = 10 * 1024 * 1024

# Classes
class MyAnalyzer:
    ...

# Functions
def helper():
    ...
```

---

## Testing Guidelines

### Test Structure

```
tests/
├── compliance/      # PII/PHI detection tests
├── integration/     # End-to-end workflow tests
├── performance/     # Benchmarks and stress tests
├── security/        # Input validation, path traversal tests
└── __init__.py      # Test configuration
```

### Writing Tests

- Every new feature needs at least one test
- Every bug fix needs a regression test
- Use `pytest` fixtures and `tmp_path` for file system tests
- Use descriptive test names: `test_scan_directory_detects_email_pii`

```python
import pytest
from pathlib import Path
from code_migration.core.compliance import PIIDetector


class TestPIIDetector:
    """Tests for PII detection."""
    
    def test_detects_email_addresses(self, tmp_path):
        """Email addresses are detected and reported."""
        test_file = tmp_path / "config.py"
        test_file.write_text('email = "user@example.com"\n')
        
        with PIIDetector(tmp_path) as detector:
            results = detector.scan_directory(file_extensions=['.py'])
        
        assert results['total_findings'] >= 1
    
    def test_empty_project_returns_zero_findings(self, tmp_path):
        """Empty directories produce zero findings."""
        with PIIDetector(tmp_path) as detector:
            results = detector.scan_directory(file_extensions=['.py'])
        
        assert results['total_findings'] == 0
```

### Running Tests

```bash
# All tests
pytest tests/ -v

# By category
pytest tests/security/ -v
pytest tests/compliance/ -v
pytest tests/performance/ -v
pytest tests/integration/ -v

# Skip slow tests (recommended during development)
pytest -m "not slow"

# With coverage
pytest tests/ --cov=src/code_migration --cov-report=term-missing
```

### Test Markers

| Marker | Usage |
|--------|-------|
| `@pytest.mark.slow` | Tests that take >10 seconds |
| `@pytest.mark.performance` | Benchmarks and stress tests |
| `@pytest.mark.security` | Security control validation |
| `@pytest.mark.compliance` | PII/PHI and regulatory tests |
| `@pytest.mark.integration` | End-to-end workflow tests |

---

## Security Requirements

**Security is a first-class concern in this project.** All contributions must pass security review. See the full [Security Policy](docs/security/SECURITY.md) for architectural details.

### Rules

1. **No code execution** — never use `eval()`, `exec()`, or `__import__()` on user-supplied input
2. **Always validate input** — use `InputValidator` for user-provided data
3. **Always sanitize paths** — use `PathSanitizer` for all file system operations
4. **Never disclose internals** — error messages must not reveal file paths, stack traces, or system info
5. **Log security events** — use `SecurityAuditLogger` for all security-relevant actions

### Examples

```python
# ✅ Correct: Use PathSanitizer
from code_migration.core.security import PathSanitizer

def read_project_file(file_path: str) -> str:
    safe_path = PathSanitizer.sanitize(file_path, allowed_base=Path.cwd())
    return safe_path.read_text()

# ❌ Wrong: Direct path usage
def read_project_file(file_path: str) -> str:
    return Path(file_path).read_text()  # Path traversal risk!
```

```python
# ✅ Correct: AST-only analysis
import ast
tree = ast.parse(code)
for node in ast.walk(tree):
    ...

# ❌ Wrong: Code execution
result = eval(code)  # Remote code execution risk!
```

### Security Review Checklist

Every PR is checked against this list:

- [ ] No `eval`, `exec`, or `__import__` usage
- [ ] All file paths go through `PathSanitizer`
- [ ] All external input goes through `InputValidator`
- [ ] Error handling does not disclose sensitive information
- [ ] Security-relevant actions are audit-logged
- [ ] New security tests are included if applicable

---

## Documentation

When adding or modifying features, update the relevant documentation:

| Change Type | Update Required |
|-------------|----------------|
| New CLI command | [User Guide](docs/USER_GUIDE.md) command reference |
| New core module | [README](README.md) architecture table, [User Guide](docs/USER_GUIDE.md) |
| Security change | [Security Policy](docs/security/SECURITY.md) |
| New dependency | [Installation Guide](docs/INSTALLATION.md) |
| Configuration change | [User Guide](docs/USER_GUIDE.md) configuration section |

### Documentation Standards

- Write in clear, concise English
- Include code examples for all new features
- Use tables for structured data
- Cross-link related documentation

---

## Pull Request Process

### Pull Request Checklist

Before submitting, verify all items:

**Code Quality:**
- [ ] Code follows the [Code Standards](#code-standards)
- [ ] All existing tests pass (`pytest tests/ -v`)
- [ ] New tests added for new functionality
- [ ] No linting errors (`flake8`, `black --check`, `isort --check-only`)

**Security:**
- [ ] Security review checklist complete (see [Security Requirements](#security-requirements))
- [ ] `bandit -r src/code_migration/` passes with no new findings

**Documentation:**
- [ ] Relevant docs updated (see [Documentation](#documentation) table)
- [ ] Docstrings added for new public APIs

### PR Template

```markdown
## Description
Brief description of what this PR does and why.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Security tests pass
- [ ] Performance tests pass (if applicable)

## Security
- [ ] No new eval/exec usage
- [ ] All paths sanitized
- [ ] Input validation added
- [ ] Security-relevant actions logged

## Checklist
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] All CI checks pass
```

### Review Process

1. **Automated CI** — tests, linting, security scanning must all pass
2. **Peer review** — at least one maintainer approval required
3. **Security review** — required for any changes to `core/security/` or `core/compliance/`
4. **Merge** — squash-and-merge preferred for clean history

---

## Community Guidelines

### Code of Conduct

We are committed to a welcoming, inclusive environment. Be respectful, constructive, and empathetic in all interactions.

### Getting Help

- **Questions:** Open a [GitHub Discussion](https://github.com/anudeepsrib/code-migration-assistant/discussions)
- **Bugs:** Open a [GitHub Issue](https://github.com/anudeepsrib/code-migration-assistant/issues)
- **Security:** See [Reporting Vulnerabilities](docs/security/SECURITY.md#reporting-vulnerabilities)

### Recognition

Contributors are recognized in the GitHub contributor statistics and in release changelogs for significant contributions.

---

Thank you for contributing to the Code Migration Assistant! 🚀
