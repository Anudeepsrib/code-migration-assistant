import logging
import sys
from rich.logging import RichHandler

def setup_logger(name: str = "code_migration", verbose: bool = False) -> logging.Logger:
    """
    Setup a structured logger with Rich handler for pretty output.
    """
    level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, markup=True)]
    )
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    return logger

# Default logger instance
logger = setup_logger()
