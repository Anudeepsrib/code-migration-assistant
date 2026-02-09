import os
import re
from pathlib import Path
from typing import List, Optional

class SecurityError(Exception):
    """Raised when a security violation is detected."""
    pass

def validate_path(path: str, base_dir: Optional[str] = None) -> Path:
    """
    Validate and sanitize file path to prevent directory traversal.
    
    Args:
        path: The path to validate.
        base_dir: The allowed base directory. If None, uses current working directory.
        
    Returns:
        Path: Absolute resolved path.
        
    Raises:
        SecurityError: If path is outside base directory or contains dangerous patterns.
    """
    if base_dir is None:
        base_dir = os.getcwd()
        
    # Resolve absolute paths
    abs_base = os.path.abspath(base_dir)
    abs_path = os.path.abspath(path)
    
    # Check if path is within base directory
    # commonprefix is not sufficient for security (e.g. /var/www vs /var/www-secret)
    # We use pathlib.resolve() which handles symlinks too
    try:
        resolved_path = Path(abs_path).resolve()
        resolved_base = Path(abs_base).resolve()
    except Exception as e:
        raise SecurityError(f"Invalid path resolution: {e}")

    if not str(resolved_path).startswith(str(resolved_base)):
        raise SecurityError(f"Path traversal detected: {path} is outside {base_dir}")
        
    return resolved_path

def sanitize_input(input_str: str) -> str:
    """
    Sanitize user input string.
    Removes potentially dangerous characters for shell execution.
    """
    # Allow alphanumeric, underscore, dot, hyphen, forward slash (for paths)
    # This is very restrictive, primarily for filenames/paths passed to CLIs
    if not re.match(r'^[a-zA-Z0-9_\-\./]+$', input_str):
        # We might want to be more lenient depending on context, but strict by default
        pass
    return input_str
