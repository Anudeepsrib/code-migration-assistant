# Contributing to Code Migration Assistant

Thank you for your interest in contributing to the Code Migration Assistant! This document provides comprehensive guidelines for contributors.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Workflow](#development-workflow)
3. [Code Standards](#code-standards)
4. [Testing Guidelines](#testing-guidelines)
5. [Security Requirements](#security-requirements)
6. [Documentation](#documentation)
7. [Pull Request Process](#pull-request-process)
8. [Community Guidelines](#community-guidelines)

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic knowledge of Python, JavaScript, and migration concepts
- Familiarity with security best practices

### Development Environment Setup

```bash
# Fork the repository
git clone https://github.com/YOUR_USERNAME/code-migration-assistant.git
cd code-migration-assistant

# Add upstream remote
git remote add upstream https://github.com/anudeepsrib/code-migration-assistant.git

# Create development environment
python -m venv venv-dev
source venv-dev/bin/activate  # On Windows: venv-dev\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```

### Verify Setup

```bash
# Run tests to ensure everything works
pytest

# Run security checks
bandit -r skills/code_migration/
safety check

# Run code formatting checks
black --check skills/code_migration/
isort --check-only skills/code_migration/
```

## Development Workflow

### 1. Create Issue

Before starting development, create an issue to track your work:

- **Bug Reports**: Use bug report template
- **Feature Requests**: Use feature request template
- **Documentation**: Use documentation template

### 2. Create Branch

```bash
# Sync with upstream
git fetch upstream
git checkout main
git merge upstream/main

# Create feature branch
git checkout -b feature/your-feature-name

# Or bug fix branch
git checkout -b fix/issue-number-description
```

### 3. Development

Follow the [Code Standards](#code-standards) and [Testing Guidelines](#testing-guidelines).

### 4. Commit Changes

```bash
# Stage changes
git add .

# Commit with conventional commits
git commit -m "feat: add new migration type support"

# Or for bug fixes
git commit -m "fix: resolve path traversal vulnerability"
```

### 5. Push and Create PR

```bash
# Push to your fork
git push origin feature/your-feature-name

# Create pull request on GitHub
# Follow the [Pull Request Process](#pull-request-process)
```

## Code Standards

### Python Code Style

We follow PEP 8 with additional guidelines:

#### Formatting

```bash
# Format code with Black
black skills/code_migration/

# Sort imports with isort
isort skills/code_migration/

# Lint with flake8
flake8 skills/code_migration/

# Type check with mypy
mypy skills/code_migration/
```

#### Naming Conventions

```python
# Classes: PascalCase
class MigrationAnalyzer:
    pass

# Functions and variables: snake_case
def analyze_migration():
    migration_type = "react-hooks"
    return migration_type

# Constants: UPPER_SNAKE_CASE
MAX_FILE_SIZE = 10 * 1024 * 1024

# Private members: prefix with underscore
class MyClass:
    def __init__(self):
        self._private_var = "private"
        self.__very_private = "very private"
```

#### Type Hints

```python
from typing import Dict, List, Optional, Union
from pathlib import Path

def analyze_migration(
    project_path: Path,
    migration_type: str,
    options: Optional[Dict[str, str]] = None
) -> Dict[str, Union[str, int]]:
    """Analyze migration with type hints."""
    return {"status": "success", "files": 10}
```

#### Documentation Strings

```python
def calculate_confidence_score(
    project_path: Path,
    migration_type: str,
    team_experience: int
) -> float:
    """Calculate migration confidence score.
    
    Args:
        project_path: Path to the project to analyze
        migration_type: Type of migration (react-hooks, vue3, etc.)
        team_experience: Team experience level (0-100)
        
    Returns:
        Confidence score between 0 and 100
        
    Raises:
        ValueError: If migration_type is not supported
        FileNotFoundError: If project_path does not exist
        
    Example:
        >>> score = calculate_confidence_score(Path("./project"), "react-hooks", 70)
        >>> print(f"Confidence: {score}%")
    """
    pass
```

### JavaScript/TypeScript Code Style

#### Formatting

```bash
# Use Prettier for JS/TS files
prettier --write "skills/code_migration/**/*.js"
prettier --write "skills/code_migration/**/*.ts"
prettier --write "skills/code_migration/**/*.jsx"
prettier --write "skills/code_migration/**/*.tsx"
```

#### Naming Conventions

```javascript
// Variables and functions: camelCase
const migrationType = "react-hooks";
function analyzeMigration() {
    return migrationType;
}

// Classes: PascalCase
class MigrationAnalyzer {
    constructor() {
        this.projectPath = null;
    }
}

// Constants: UPPER_SNAKE_CASE
const MAX_FILE_SIZE = 10 * 1024 * 1024;

// Private members: prefix with underscore
class MyClass {
    constructor() {
        this._privateVar = "private";
    }
}
```

### File Organization

#### Python Files

```python
# Standard file structure
"""Module docstring."""

# Standard library imports
import os
import sys
from pathlib import Path
from typing import Dict, List

# Third-party imports
import networkx as nx
import yaml

# Local imports
from ..security import PathSanitizer
from ..utils import helper_function

# Constants
DEFAULT_TIMEOUT = 300
MAX_FILE_SIZE = 10 * 1024 * 1024

# Classes
class MigrationAnalyzer:
    """Class docstring."""
    
    def __init__(self) -> None:
        self.project_path: Optional[Path] = None
    
    def analyze(self) -> Dict[str, str]:
        """Method docstring."""
        return {"status": "success"}

# Functions
def helper_function() -> str:
    """Function docstring."""
    return "helper"

# Main execution block
if __name__ == "__main__":
    main()
```

#### JavaScript/TypeScript Files

```javascript
/**
 * Module docstring
 */

// Imports
import { analyzeMigration } from './analyzer';
import { MigrationType } from './types';

// Constants
const DEFAULT_TIMEOUT = 300;
const MAX_FILE_SIZE = 10 * 1024 * 1024;

// Classes
export class MigrationAnalyzer {
    /**
     * Class docstring
     */
    constructor() {
        this.projectPath = null;
    }
    
    /**
     * Method docstring
     * @returns {Object} Analysis result
     */
    analyze() {
        return { status: "success" };
    }
}

// Functions
export function helperFunction() {
    return "helper";
}

// Exports
export { MigrationAnalyzer as default };
```

## Testing Guidelines

### Test Structure

```
tests/
├── unit/                    # Unit tests
│   ├── test_security/
│   ├── test_confidence/
│   └── test_visualizer/
├── integration/             # Integration tests
├── performance/             # Performance tests
├── fixtures/               # Test data and fixtures
└── conftest.py           # Pytest configuration
```

### Writing Tests

#### Unit Tests

```python
# tests/unit/test_analyzer.py
import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from skills.code_migration.core.confidence import MigrationConfidenceAnalyzer


class TestMigrationConfidenceAnalyzer:
    """Test MigrationConfidenceAnalyzer class."""
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer fixture."""
        return MigrationConfidenceAnalyzer()
    
    @pytest.fixture
    def sample_project(self, tmp_path):
        """Create sample project fixture."""
        project_dir = tmp_path / "sample_project"
        project_dir.mkdir()
        
        # Create test files
        (project_dir / "test.py").write_text("def hello(): pass")
        (project_dir / "test.js").write_text("function hello() {}")
        
        return project_dir
    
    def test_calculate_confidence_success(self, analyzer, sample_project):
        """Test successful confidence calculation."""
        result = analyzer.calculate_confidence("react-hooks", team_experience=70)
        
        assert 0 <= result.overall_score <= 100
        assert result.risk_level in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        assert result.estimated_hours > 0
    
    def test_calculate_confidence_invalid_type(self, analyzer, sample_project):
        """Test confidence calculation with invalid migration type."""
        with pytest.raises(ValueError, match="Invalid migration type"):
            analyzer.calculate_confidence("invalid-type")
    
    @patch("skills.code_migration.core.confidence.analyzer.os.path.exists")
    def test_calculate_confidence_project_not_found(self, mock_exists, analyzer):
        """Test confidence calculation with non-existent project."""
        mock_exists.return_value = False
        
        with pytest.raises(FileNotFoundError):
            analyzer.calculate_confidence("react-hooks")
    
    @pytest.mark.parametrize("team_experience,expected_range", [
        (0, (0, 40)),
        (50, (40, 70)),
        (100, (70, 100))
    ])
    def test_calculate_confidence_team_experience_impact(
        self, analyzer, sample_project, team_experience, expected_range
    ):
        """Test team experience impact on confidence score."""
        result = analyzer.calculate_confidence("react-hooks", team_experience=team_experience)
        
        assert expected_range[0] <= result.overall_score <= expected_range[1]
```

#### Integration Tests

```python
# tests/integration/test_full_migration.py
import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

from skills.code_migration.core.confidence import MigrationConfidenceAnalyzer
from skills.code_migration.core.visualizer import VisualMigrationPlanner
from skills.code_migration.core.rollback import TimeMachineRollback


class TestFullMigrationWorkflow:
    """Test complete migration workflow."""
    
    @pytest.fixture
    def react_project(self):
        """Create React project fixture."""
        with TemporaryDirectory() as tmp_dir:
            project_path = Path(tmp_dir) / "react_project"
            project_path.mkdir()
            
            # Create React component
            (project_path / "src" / "components").mkdir(parents=True)
            (project_path / "src" / "components" / "Button.jsx").write_text("""
                import React, { Component } from 'react';
                
                class Button extends Component {
                    render() {
                        return <button>Click me</button>;
                    }
                }
            """)
            
            yield project_path
    
    def test_end_to_end_migration(self, react_project):
        """Test complete end-to-end migration."""
        # Analyze confidence
        analyzer = MigrationConfidenceAnalyzer(react_project)
        confidence = analyzer.calculate_confidence("react-hooks")
        
        assert confidence.overall_score > 0
        
        # Create visual plan
        planner = VisualMigrationPlanner(react_project)
        planner.build_dependency_graph()
        waves = planner.calculate_migration_waves()
        
        assert len(waves) > 0
        
        # Create checkpoint
        rollback = TimeMachineRollback(react_project)
        checkpoint_id = rollback.create_checkpoint("Pre-migration")
        
        assert checkpoint_id is not None
        
        # Verify rollback works
        rollback_result = rollback.rollback(checkpoint_id)
        assert rollback_result['success'] is True
```

#### Performance Tests

```python
# tests/performance/test_large_codebase.py
import pytest
import time
from pathlib import Path

from skills.code_migration.core.security import SafeCodeAnalyzer


class TestPerformance:
    """Performance tests for large codebases."""
    
    @pytest.mark.performance
    def test_large_project_analysis_performance(self):
        """Test analysis performance with large project."""
        # Create large test project
        # ... setup code ...
        
        analyzer = SafeCodeAnalyzer()
        
        start_time = time.time()
        result = analyzer.analyze_directory(large_project)
        end_time = time.time()
        
        analysis_time = end_time - start_time
        
        # Performance assertions
        assert analysis_time < 30.0  # Should complete within 30 seconds
        assert result['files_analyzed'] > 1000
        
        print(f"Analyzed {result['files_analyzed']} files in {analysis_time:.2f}s")
```

### Test Configuration

#### pytest.ini

```ini
[tool:pytest]
minversion = 6.0
addopts = 
    --cov=skills/code_migration
    --cov-report=html
    --cov-report=term-missing
    --strict-markers
    --disable-warnings
    --timeout=300
    --tb=short

markers =
    security: Security-related tests
    compliance: Compliance scanning tests
    performance: Performance tests
    integration: End-to-end tests
    slow: Tests that take longer to run

testpaths = [
    skills/code-migration/tests
]

filterwarnings =
    ignore::UserWarning
    ignore::DeprecationWarning
```

#### conftest.py

```python
# tests/conftest.py
import pytest
import tempfile
from pathlib import Path


@pytest.fixture(scope="session")
def temp_dir():
    """Create temporary directory for all tests."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def sample_project(temp_dir):
    """Create sample project for testing."""
    project_dir = temp_dir / "sample_project"
    project_dir.mkdir()
    
    # Create basic project structure
    (project_dir / "src").mkdir()
    (project_dir / "tests").mkdir()
    
    # Create sample files
    (project_dir / "src" / "main.py").write_text("def main(): pass")
    (project_dir / "tests" / "test_main.py").write_text("def test_main(): pass")
    
    return project_dir


@pytest.fixture
def mock_analyzer():
    """Create mock analyzer for testing."""
    from unittest.mock import Mock
    return Mock(spec=MigrationConfidenceAnalyzer)
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=skills/code_migration --cov-report=html

# Run specific test categories
pytest -m security
pytest -m integration
pytest -m performance

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_analyzer.py

# Run with specific markers
pytest -m "not slow"  # Skip slow tests
```

## Security Requirements

### Security-First Development

All code must follow security-first principles:

#### Input Validation

```python
# ✅ Good: Always validate input
def process_file_path(file_path: str) -> Path:
    """Process file path with validation."""
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string")
    
    # Use PathSanitizer for validation
    return PathSanitizer.sanitize(file_path, allowed_base=Path.cwd())

# ❌ Bad: No validation
def process_file_path(file_path: str) -> Path:
    return Path(file_path)  # Dangerous!
```

#### No Code Execution

```python
# ✅ Good: AST-only analysis
def analyze_code(code: str) -> Dict:
    """Analyze code using AST only."""
    try:
        tree = ast.parse(code)
        return {"valid": True, "nodes": len(ast.walk(tree))}
    except SyntaxError:
        return {"valid": False, "error": "Invalid syntax"}

# ❌ Bad: Code execution
def analyze_code(code: str) -> Dict:
    """Never execute user code!"""
    return eval(code)  # Dangerous!
```

#### Path Traversal Prevention

```python
# ✅ Good: Use PathSanitizer
def read_file(file_path: str) -> str:
    """Read file with path sanitization."""
    safe_path = PathSanitizer.sanitize(file_path, allowed_base=Path.cwd())
    return safe_path.read_text()

# ❌ Bad: Direct path usage
def read_file(file_path: str) -> str:
    return Path(file_path).read_text()  # Dangerous!
```

### Security Testing

All code must pass security tests:

```bash
# Run security tests
pytest tests/security/

# Run static analysis
bandit -r skills/code_migration/
safety check

# Run dependency audit
pip-audit
```

### Security Code Review Checklist

- [ ] No code execution (`eval`, `exec`, `__import__`)
- [ ] Input validation for all external inputs
- [ ] Path traversal prevention
- [ ] SQL injection prevention
- [ ] XSS prevention
- [ ] Proper error handling without information disclosure
- [ ] Secure file operations
- [ ] Rate limiting where appropriate
- [ ] Audit logging for security events

## Documentation

### Code Documentation

All public APIs must have comprehensive documentation:

#### Python Documentation

```python
def calculate_migration_confidence(
    project_path: Path,
    migration_type: str,
    team_experience: int = 70,
    options: Optional[Dict[str, Any]] = None
) -> ConfidenceScore:
    """
    Calculate migration confidence score using multiple factors.
    
    This function analyzes the project to determine the confidence level
    for a successful migration based on test coverage, code complexity,
    dependencies, and team experience.
    
    Args:
        project_path: Path to the project directory to analyze
        migration_type: Type of migration (react-hooks, vue3, python3, etc.)
        team_experience: Team's experience level with the target technology (0-100)
        options: Optional additional configuration options
        
    Returns:
        ConfidenceScore object containing detailed analysis results
        
    Raises:
        ValueError: If migration_type is not supported
        FileNotFoundError: If project_path does not exist
        SecurityError: If security validation fails
        
    Example:
        >>> from pathlib import Path
        >>> analyzer = MigrationConfidenceAnalyzer(Path("./my-project"))
        >>> score = analyzer.calculate_confidence("react-hooks", team_experience=80)
        >>> print(f"Confidence: {score.overall_score}/100")
        
    Note:
        This function performs static analysis only and does not execute
        any code from the project. All file operations are validated
        through PathSanitizer to prevent path traversal attacks.
    """
    pass
```

#### JavaScript/TypeScript Documentation

```javascript
/**
 * Analyzes migration confidence for a given project.
 * 
 * @param projectPath - Path to the project directory
 * @param migrationType - Type of migration to analyze
 * @param teamExperience - Team experience level (0-100)
 * @param options - Optional configuration options
 * @returns Promise<ConfidenceScore> Confidence analysis results
 * 
 * @example
 * ```javascript
 * const analyzer = new MigrationConfidenceAnalyzer('./my-project');
 * const score = await analyzer.analyze('react-hooks', 80);
 * console.log(`Confidence: ${score.overallScore}/100`);
 * ```
 * 
 * @throws {Error} When project path doesn't exist
 * @throws {ValidationError} When migration type is invalid
 */
export class MigrationConfidenceAnalyzer {
    /**
     * Analyzes migration confidence.
     */
    async analyze(
        projectPath: string,
        migrationType: string,
        teamExperience: number = 70,
        options?: AnalysisOptions
    ): Promise<ConfidenceScore> {
        // Implementation
    }
}
```

### Documentation Updates

When adding new features:

1. Update relevant sections in USER_GUIDE.md
2. Add API documentation to docs/api/
3. Update CHANGELOG.md
4. Add examples to docs/examples/
5. Update README.md if needed

### Documentation Standards

- Use clear, concise language
- Provide code examples
- Include parameter descriptions
- Document return values and exceptions
- Add usage examples
- Include performance considerations

## Pull Request Process

### Before Submitting PR

1. **Code Quality**
   - [ ] Code follows style guidelines
   - [ ] All tests pass
   - [ ] Security tests pass
   - [ ] Documentation updated

2. **Testing**
   - [ ] Unit tests added for new features
   - [ ] Integration tests updated
   - [ ] Performance tests if applicable
   - [ ] Test coverage maintained or improved

3. **Security**
   - [ ] Security review completed
   - [ ] No new security vulnerabilities
   - [ ] Input validation added
   - [ ] Path traversal prevention

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Security tests pass
- [ ] Performance tests pass

## Security
- [ ] Security review completed
- [ ] No new vulnerabilities
- [ ] Input validation added
- [ ] Path traversal prevention

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Tests added/updated
- [ ] All tests pass
```

### Review Process

1. **Automated Checks**
   - CI/CD pipeline runs tests
   - Security scanning
   - Code quality checks
   - Documentation build

2. **Peer Review**
   - At least one maintainer review
   - Security review for security changes
   - Performance review for performance changes

3. **Approval**
   - All checks must pass
   - No merge conflicts
   - Maintainer approval required

### Merge Requirements

- All automated checks must pass
- At least one approval from maintainer
- No outstanding security concerns
- Documentation complete
- Tests adequate

## Community Guidelines

### Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

### Communication

- Be respectful and constructive
- Welcome newcomers and help them learn
- Focus on what is best for the community
- Show empathy towards other community members

### Getting Help

- Create an issue for questions
- Join our Slack community
- Check documentation first
- Search existing issues

### Recognition

Contributors are recognized in:
- README.md contributors section
- CHANGELOG.md for significant contributions
- Annual contributor awards
- GitHub contributor statistics

---

## Need Help?

- **Documentation**: https://docs.code-migration.ai
- **Discussions**: https://github.com/anudeepsrib/code-migration-assistant/discussions
- **Issues**: https://github.com/anudeepsrib/code-migration-assistant/issues
- **Security**: security@code-migration.ai

Thank you for contributing to the Code Migration Assistant! 🚀
