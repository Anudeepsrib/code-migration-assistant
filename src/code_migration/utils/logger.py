"""
Structured Logging Factory for Code Migration Assistant.

Uses structlog to provide JSON or text-based telemetry.

Usage:
    from code_migration.utils.logger import get_logger

    logger = get_logger(__name__)
    logger.info("analyzing_file", path=str(file_path), rule="react-hooks")
"""

import logging
import sys
import structlog
from typing import Any

from code_migration.config import settings

def _configure_structlog():
    """Configure structlog based on environment settings."""
    if structlog.is_configured():
        return

    log_level = getattr(logging, settings.observability.log_level.upper(), logging.INFO)
    
    # Configure stdlib logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )

    processors = [
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    # Add appropriate renderer based on configuration
    if settings.observability.log_format.lower() == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

# Run configuration exactly once upon import
_configure_structlog()

def get_logger(name: str) -> Any:
    """Return a structlog logger bound to the specific module name."""
    return structlog.get_logger(name)
