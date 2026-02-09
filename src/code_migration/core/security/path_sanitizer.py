"""
Path sanitization to prevent directory traversal attacks.

Implements CWE-22: Path Traversal prevention.
Follows OWASP File Path validation guidelines.
"""

import os
from pathlib import Path
from typing import Union

from .input_validator import SecurityError


class PathSanitizer:
    """
    Prevent directory traversal attacks (CWE-22).
    
    Security Controls:
    - Resolve to absolute path
    - Check against whitelist base directory
    - Detect path traversal attempts
    - Validate length limits
    - Block dangerous characters
    """
    
    # Dangerous patterns that indicate traversal attempts
    DANGEROUS_PATTERNS = ['..', '~', '$', '`', '|', ';', '&', '\x00']
    
    # Maximum path length to prevent buffer overflow attacks
    MAX_PATH_LENGTH = 4096
    
    # Allowed file extensions (whitelist approach)
    ALLOWED_EXTENSIONS = {
        '.py', '.js', '.jsx', '.ts', '.tsx', '.vue', '.html',
        '.css', '.scss', '.less', '.json', '.yaml', '.yml',
        '.md', '.txt', '.xml', '.sql', '.sh', '.bash'
    }
    
    @staticmethod
    def sanitize(path: str, allowed_base: Union[str, Path]) -> Path:
        """
        Validate and sanitize file paths.
        
        Args:
            path: User-provided path to sanitize
            allowed_base: Base directory that paths must stay within
            
        Raises:
            SecurityError: If path validation fails
            
        Returns:
            Path: Sanitized absolute Path object
        """
        # Input validation
        if not path or len(path) > PathSanitizer.MAX_PATH_LENGTH:
            raise SecurityError("Invalid path length")
        
        # Check for dangerous patterns
        for pattern in PathSanitizer.DANGEROUS_PATTERNS:
            if pattern in path:
                raise SecurityError(f"Dangerous pattern detected: {pattern}")
        
        # Resolve to canonical absolute path
        try:
            abs_path = Path(path).resolve(strict=True)
        except (OSError, RuntimeError) as e:
            raise SecurityError(f"Path resolution failed: {e}")
        
        # Verify within allowed base directory
        allowed_base_resolved = Path(allowed_base).resolve()
        if not abs_path.is_relative_to(allowed_base_resolved):
            raise SecurityError("Path outside allowed directory")
        
        # Validate file extension
        if abs_path.suffix:
            if abs_path.suffix.lower() not in PathSanitizer.ALLOWED_EXTENSIONS:
                raise SecurityError(f"File extension not allowed: {abs_path.suffix}")
        
        return abs_path
    
    @staticmethod
    def sanitize_directory(path: str, allowed_base: Union[str, Path]) -> Path:
        """
        Validate and sanitize directory paths.
        
        Similar to sanitize() but for directories.
        """
        if not path or len(path) > PathSanitizer.MAX_PATH_LENGTH:
            raise SecurityError("Invalid directory path length")
        
        # Check for dangerous patterns
        for pattern in PathSanitizer.DANGEROUS_PATTERNS:
            if pattern in path:
                raise SecurityError(f"Dangerous pattern detected: {pattern}")
        
        # Resolve to canonical absolute path
        try:
            abs_path = Path(path).resolve(strict=False)  # Directory may not exist yet
        except (OSError, RuntimeError) as e:
            raise SecurityError(f"Directory path resolution failed: {e}")
        
        # Verify within allowed base directory
        allowed_base_resolved = Path(allowed_base).resolve()
        if not abs_path.is_relative_to(allowed_base_resolved):
            raise SecurityError("Directory path outside allowed base")
        
        return abs_path
    
    @staticmethod
    def is_safe_filename(filename: str) -> bool:
        """
        Check if a filename is safe (no directory components).
        
        Args:
            filename: Just the filename, no path
            
        Returns:
            bool: True if filename is safe
        """
        if not filename:
            return False
        
        # No path separators
        if '/' in filename or '\\' in filename:
            return False
        
        # No dangerous patterns
        for pattern in PathSanitizer.DANGEROUS_PATTERNS:
            if pattern in filename:
                return False
        
        # No leading/trailing spaces or dots
        if filename.strip() != filename:
            return False
        
        # Not reserved names (Windows)
        reserved_names = {
            'CON', 'PRN', 'AUX', 'NUL',
            'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
            'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
        }
        
        name_without_ext = filename.split('.')[0].upper()
        if name_without_ext in reserved_names:
            return False
        
        return True
    
    @staticmethod
    def get_relative_path(path: Path, base: Path) -> str:
        """
        Get relative path safely for logging/display.
        
        Args:
            path: Absolute path
            base: Base directory
            
        Returns:
            str: Safe relative path representation
        """
        try:
            return str(path.relative_to(base))
        except ValueError:
            # If not relative, just return the name
            return path.name
