"""
Test suite for Code Migration Assistant.

Comprehensive test coverage for:
- Security controls and validation
- Compliance scanning and reporting
- Migration confidence analysis
- Visual planning tools
- Rollback functionality
- Performance and integration
"""

# Test configuration
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))



# Test settings
pytest_timeout = 300  # 5 minutes timeout for integration tests
pytest_addopts = [
    "--cov=skills/code_migration",
    "--cov-report=html",
    "--cov-report=term-missing",
    "--cov-fail-under=80",
    "--strict-markers",
    "--disable-warnings"
]

# Test markers
markers = [
    "security: Security-related tests",
    "compliance: Compliance scanning tests", 
    "performance: Performance and load tests",
    "integration: End-to-end integration tests",
    "slow: Tests that take longer to run"
]

# Minimum test coverage
COVERAGE_THRESHOLD = 80
