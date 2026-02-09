# Installation Guide

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation Methods](#installation-methods)
3. [Configuration](#configuration)
4. [Verification](#verification)
5. [Troubleshooting](#troubleshooting)
6. [Docker Installation](#docker-installation)
7. [Development Setup](#development-setup)

## System Requirements

### Minimum Requirements

| Component | Minimum | Recommended |
|------------|---------|-------------|
| Python | 3.8 | 3.11 |
| RAM | 4GB | 8GB+ |
| Storage | 1GB | 5GB+ |
| OS | Linux/macOS/Windows | Linux/macOS |

### Supported Platforms

- **Linux**: Ubuntu 18.04+, CentOS 7+, Debian 10+
- **macOS**: 10.15+ (Catalina)
- **Windows**: Windows 10+ (with WSL2 recommended)
- **Docker**: Any platform with Docker Engine

### Python Version Compatibility

| Python Version | Status | Notes |
|----------------|--------|-------|
| 3.8 | ✅ Supported | Minimum version |
| 3.9 | ✅ Supported | Recommended |
| 3.10 | ✅ Supported | Recommended |
| 3.11 | ✅ Supported | Latest stable |
| 3.12 | 🚧 Experimental | May have compatibility issues |

## Installation Methods

### Method 1: pip Install (Recommended)

#### Standard Installation

```bash
# Install from PyPI
pip install code-migration-assistant

# Verify installation
migrate --version
```

#### Installation with Extra Dependencies

```bash
# Install with all optional dependencies
pip install code-migration-assistant[all]

# Install with security dependencies
pip install code-migration-assistant[security]

# Install with development dependencies
pip install code-migration-assistant[dev]
```

#### Installation from Source

```bash
# Clone repository
git clone https://github.com/anudeepsrib/code-migration-assistant.git
cd code-migration-assistant

# Install in development mode
pip install -e .

# Or install normally
pip install .
```

### Method 2: Docker Installation

#### Using Docker Hub Image

```bash
# Pull the latest image
docker pull code-migration-assistant:latest

# Run with mounted volume
docker run -v /path/to/project:/project code-migration-assistant \
  migrate analyze /project --type react-hooks

# Interactive shell
docker run -it -v /path/to/project:/project code-migration-assistant bash
```

#### Building from Dockerfile

```bash
# Clone repository
git clone https://github.com/anudeepsrib/code-migration-assistant.git
cd code-migration-assistant

# Build Docker image
docker build -t code-migration-assistant .

# Run container
docker run -v $(pwd)/project:/project code-migration-assistant \
  migrate analyze /project --type react-hooks
```

### Method 3: Conda Installation

```bash
# Create conda environment
conda create -n code-migration python=3.11
conda activate code-migration

# Install from PyPI
pip install code-migration-assistant

# Or install from conda-forge (if available)
conda install -c conda-forge code-migration-assistant
```

### Method 4: Package Manager Installation

#### Ubuntu/Debian (APT)

```bash
# Add repository
sudo apt-add-repository ppa:code-migration/stable
sudo apt update

# Install package
sudo apt install code-migration-assistant

# Verify installation
migrate --version
```

#### macOS (Homebrew)

```bash
# Tap the repository
brew tap code-migration/tap

# Install package
brew install code-migration-assistant

# Verify installation
migrate --version
```

#### Windows (Chocolatey)

```bash
# Install package
choco install code-migration-assistant

# Verify installation
migrate --version
```

## Configuration

### Basic Configuration

After installation, create a configuration directory:

```bash
# Create config directory
mkdir ~/.config/code-migration
cd ~/.config/code-migration

# Create default configuration
migrate config init
```

### Environment Variables

Create `.env` file in your project or set globally:

```bash
# API Configuration
export MIGRATION_API_URL="https://api.code-migration.ai"
export MIGRATION_API_KEY="your-api-key"

# Security Configuration
export MIGRATION_SECURITY_LEVEL="high"
export MIGRATION_AUDIT_LOGGING="true"

# Performance Configuration
export MIGRATION_MAX_WORKERS="4"
export MIGRATION_TIMEOUT="300"
export MIGRATION_CACHE_DIR="~/.cache/code-migration"

# Logging Configuration
export MIGRATION_LOG_LEVEL="INFO"
export MIGRATION_LOG_FILE="~/.local/share/code-migration/logs/migration.log"
```

### Configuration Files

#### Security Policy

Create `~/.config/code-migration/security.yaml`:

```yaml
security:
  input_validation:
    max_file_size: 10485760  # 10MB
    max_lines: 1000
    allowed_extensions: ['.py', '.js', '.jsx', '.ts', '.tsx', '.vue']
  
  path_sanitization:
    allowed_base: "./project"
    max_path_length: 4096
  
  rate_limiting:
    migrations_per_hour: 10
    file_ops_per_minute: 100
```

#### Migration Rules

Create `~/.config/code-migration/migration.yaml`:

```yaml
migrations:
  react-hooks:
    convert_lifecycle: true
    update_tests: true
    preserve_comments: true
    convert_state: true
  
  vue3:
    update_dependencies: true
    convert_options_api: true
    typescript_support: false
  
  python3:
    update_print_statements: true
    fix_integer_division: true
    update_imports: true
```

#### Compliance Settings

Create `~/.config/code-migration/compliance.yaml`:

```yaml
compliance:
  gdpr:
    pii_detection: true
    data_retention_days: 90
    consent_required: false
  
  hipaa:
    phi_detection: true
    audit_logging: true
    encryption_required: true
  
  soc2:
    audit_trail: true
    access_control: true
    monitoring: true
```

### IDE Integration

#### VS Code

Install the Code Migration Assistant extension:

```bash
# Install from VS Code marketplace
code --install-extension code-migration.assistant

# Or install from command line
code --install-extension code-migration.code-migration-assistant
```

Configure VS Code settings (`.vscode/settings.json`):

```json
{
  "codeMigration.securityLevel": "high",
  "codeMigration.defaultMigrationType": "react-hooks",
  "codeMigration.autoBackup": true,
  "codeMigration.showNotifications": true
}
```

#### JetBrains IDEs

Install the plugin from JetBrains Marketplace:

1. Open IDE
2. Go to `File` → `Settings` → `Plugins`
3. Search for "Code Migration Assistant"
4. Install and restart IDE

#### Vim/Neovim

Add to your `.vimrc` or `init.vim`:

```vim
" Code Migration Assistant integration
Plug 'code-migration/vim-plugin'

" Commands
:CodeMigrateAnalyze
:CodeMigrateRun
:CodeMigrateRollback
```

## Verification

### Basic Verification

```bash
# Check version
migrate --version

# Check system status
migrate status

# List available migration types
migrate list-types

# Run basic test
migrate analyze --help
```

### Functional Verification

```bash
# Create test project
mkdir test-project
cd test-project
echo "class Test { render() { return <div>Test</div>; }" > Test.jsx

# Test analysis
migrate analyze . --type react-hooks

# Test visualization
migrate visualize . --output test-graph.html

# Verify output
ls -la test-graph.html
```

### Security Verification

```bash
# Test security controls
echo "eval('malicious')" > test.py
migrate analyze test.py --type python3  # Should be blocked

# Test path sanitization
migrate analyze ../../../etc/passwd --type python3  # Should be blocked

# Test compliance scanning
migrate compliance scan . --pii
```

### Performance Verification

```bash
# Test with larger project
git clone https://github.com/facebook/react.git test-react
cd test-react

# Test performance
time migrate analyze . --type react-hooks --performance-mode

# Check memory usage
migrate analyze . --type react-hooks --memory-monitor
```

## Troubleshooting

### Common Installation Issues

#### Python Version Incompatible

**Problem**: `ERROR: Package requires a different Python`

**Solution**:
```bash
# Check Python version
python --version

# Install correct version
# For Ubuntu/Debian:
sudo apt install python3.11 python3.11-pip python3.11-venv

# For macOS:
brew install python@3.11

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate
pip install code-migration-assistant
```

#### Permission Denied

**Problem**: Permission errors during installation

**Solution**:
```bash
# Use user installation
pip install --user code-migration-assistant

# Or use virtual environment
python -m venv venv
source venv/bin/activate
pip install code-migration-assistant
```

#### Dependency Conflicts

**Problem**: Conflicts with existing packages

**Solution**:
```bash
# Create clean environment
python -m venv clean-env
source clean-env/bin/activate

# Install with --no-deps if needed
pip install --no-deps code-migration-assistant

# Then install dependencies manually
pip install click rich pyyaml networkx
```

#### Windows Path Issues

**Problem**: Command not found on Windows

**Solution**:
```bash
# Add to PATH
echo 'export PATH="$PATH:/c/Users/username/AppData/Local/Programs/Python/Python311/Scripts"' >> ~/.bashrc

# Or use Python launcher
python -m code_migration_assistant --version

# Or use full path
/c/Python311/Scripts/migrate --version
```

### Runtime Issues

#### Memory Errors

**Problem**: Out of memory on large projects

**Solution**:
```bash
# Reduce memory usage
migrate analyze ./large-project --memory-limit 2GB

# Use streaming mode
migrate analyze ./large-project --streaming

# Limit concurrent operations
migrate analyze ./large-project --workers 2
```

#### Security Blockages

**Problem**: Migration blocked by security controls

**Solution**:
```bash
# Check what's blocked
migrate analyze ./file.jsx --security-check

# Temporarily lower security level
export MIGRATION_SECURITY_LEVEL="medium"

# Add exceptions to security policy
migrate config security --add-exception "eval"
```

#### Performance Issues

**Problem**: Slow analysis on large codebases

**Solution**:
```bash
# Use performance mode
migrate analyze ./project --performance-mode

# Limit file types
migrate analyze ./project --include "*.py,*.js,*.jsx"

# Use caching
migrate analyze ./project --cache
```

### Docker Issues

#### Permission Errors

**Problem**: Permission denied when mounting volumes

**Solution**:
```bash
# Fix Docker permissions
sudo chown -R $USER:$USER ~/.local/share/code-migration

# Use different volume mount
docker run -v $(pwd):/workspace -w /workspace code-migration-assistant
```

#### Network Issues

**Problem**: Cannot download dependencies

**Solution**:
```bash
# Use different registry
docker build --build-arg REGISTRY=registry.mirrors.ustc.edu .

# Use offline mode
docker run --network=none code-migration-assistant
```

## Docker Installation

### Docker Compose Setup

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  code-migration:
    image: code-migration-assistant:latest
    container_name: code-migration
    volumes:
      - ./project:/project
      - ./config:/config
      - ./logs:/logs
      - ~/.cache/code-migration:/cache
    environment:
      - MIGRATION_SECURITY_LEVEL=high
      - MIGRATION_LOG_LEVEL=INFO
      - MIGRATION_CACHE_DIR=/cache
    working_dir: /project
    command: migrate --help

  postgres:
    image: postgres:15
    container_name: postgres
    environment:
      POSTGRES_DB: code_migration
      POSTGRES_USER: migration_user
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

### Multi-Stage Dockerfile

```dockerfile
# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
COPY requirements-security.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements-security.txt

# Copy source code
COPY . .

# Install package
RUN pip install -e .

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Create non-root user
RUN useradd -m -u 1000 migration
USER migration

# Create directories
RUN mkdir -p /app/logs /app/cache /app/config
RUN chown -R migration:migration /app

# Set environment
ENV MIGRATION_CACHE_DIR=/app/cache
ENV MIGRATION_LOG_DIR=/app/logs
ENV MIGRATION_CONFIG_DIR=/app/config

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD migrate --version || exit 1

# Expose port
EXPOSE 8000

# Default command
CMD ["migrate", "--help"]
```

### Docker Commands

```bash
# Build image
docker build -t code-migration-assistant .

# Run container
docker run -it --rm \
  -v $(pwd)/project:/project \
  -v $(pwd)/config:/config \
  code-migration-assistant \
  migrate analyze /project --type react-hooks

# Run with docker-compose
docker-compose up -d
docker-compose exec code-migration migrate analyze /project --type react-hooks

# View logs
docker-compose logs -f code-migration
```

## Development Setup

### Development Environment

```bash
# Clone repository
git clone https://github.com/anudeepsrib/code-migration-assistant.git
cd code-migration-assistant

# Create development environment
python -m venv venv-dev
source venv-dev/bin/activate  # On Windows: venv-dev\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```

### Development Dependencies

#### Core Development
```bash
pip install pytest pytest-cov pytest-timeout pytest-asyncio
pip install black isort flake8 mypy
pip install pre-commit
```

#### Security Testing
```bash
pip install bandit safety
pip install semgrep
pip install pip-audit
```

#### Performance Testing
```bash
pip install memory-profiler
pip install psutil
pip install pytest-benchmark
```

#### Documentation
```bash
pip install sphinx sphinx-rtd-theme
pip install mkdocs mkdocs-material
pip install mkdocs-mermaid2-plugin
```

### Pre-commit Setup

```bash
# Install pre-commit
pre-commit install

# Create .pre-commit-config.yaml
cat > .pre-commit-config.yaml << EOF
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
  
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
  
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
  
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
  
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: [-r, skills/code_migration/]
EOF
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=skills/code_migration --cov-report=html

# Run specific test categories
pytest tests/security/
pytest tests/compliance/
pytest tests/integration/
pytest tests/performance/

# Run performance tests
pytest -m performance --benchmark-only
```

### Building Documentation

```bash
# Build API docs
cd docs/api
make html

# Build user guide
cd docs
mkdocs build

# Serve documentation locally
mkdocs serve
```

### Contributing

```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes
# ... (your development work)

# Run tests and checks
pytest
pre-commit run --all-files
bandit -r skills/code_migration/
safety check

# Commit changes
git add .
git commit -m "Add new feature"

# Push and create PR
git push origin feature/new-feature
```

---

## Need Help?

- **Documentation**: https://docs.code-migration.ai
- **Issues**: https://github.com/anudeepsrib/code-migration-assistant/issues
- **Discussions**: https://github.com/anudeepsrib/code-migration-assistant/discussions
- **Support**: support@code-migration.ai

For installation issues, please check the [troubleshooting section](#troubleshooting) or create an issue on GitHub.
