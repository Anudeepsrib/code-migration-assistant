"""
Input validation and sanitization for security.

Prevents code injection and malicious input patterns.
Follows OWASP A03:2021 - Injection prevention guidelines.
"""

import ast
import re
from typing import List


class SecurityError(Exception):
    """Raised when security validation fails."""
    pass


class CodeValidator:
    """
    Validate user-provided code patterns and inputs.
    
    Security Controls:
    - Keyword blacklist for dangerous functions
    - AST parsing only (no execution)
    - Pattern validation
    - Length limits
    """
    
    # Dangerous Python keywords and functions
    FORBIDDEN_KEYWORDS = [
        'eval', 'exec', 'compile', '__import__',
        'open', 'file', 'input', 'raw_input',
        'execfile', 'reload', '__builtins__',
        'globals()', 'locals()', 'vars()', 'dir()',
        'hasattr', 'getattr', 'setattr', 'delattr',
        'callable', 'isinstance', 'issubclass'
    ]
    
    # Dangerous modules
    FORBIDDEN_MODULES = [
        'os', 'sys', 'subprocess', 'socket',
        'urllib', 'http', 'ftplib', 'smtplib',
        'pickle', 'marshal', 'shelve', 'dbm',
        'ctypes', 'threading', 'multiprocessing'
    ]
    
    # Maximum sizes to prevent DoS
    MAX_PATTERN_SIZE = 10_000  # 10KB
    MAX_LINE_LENGTH = 1_000   # 1KB per line
    MAX_LINES = 1_000         # Max lines per pattern
    
    @staticmethod
    def validate_pattern(pattern: str) -> bool:
        """
        Validate migration pattern for security.
        
        Args:
            pattern: Code pattern to validate
            
        Raises:
            SecurityError: If pattern contains dangerous code
            
        Returns:
            bool: True if pattern is safe
        """
        # Size limits
        if not pattern or len(pattern) > CodeValidator.MAX_PATTERN_SIZE:
            raise SecurityError("Pattern size exceeds security limits")
        
        # Line limits
        lines = pattern.split('\n')
        if len(lines) > CodeValidator.MAX_LINES:
            raise SecurityError("Pattern has too many lines")
        
        for line in lines:
            if len(line) > CodeValidator.MAX_LINE_LENGTH:
                raise SecurityError("Pattern line exceeds maximum length")
        
        # Check for forbidden keywords
        pattern_lower = pattern.lower()
        for keyword in CodeValidator.FORBIDDEN_KEYWORDS:
            if keyword in pattern_lower:
                raise SecurityError(f"Forbidden keyword detected: {keyword}")
        
        # Check for forbidden modules
        for module in CodeValidator.FORBIDDEN_MODULES:
            if f'import {module}' in pattern_lower:
                raise SecurityError(f"Forbidden module import: {module}")
        
        # Validate it's parseable (but never execute)
        try:
            ast.parse(pattern)
        except SyntaxError as e:
            raise SecurityError(f"Invalid Python syntax: {e}")
        
        return True
    
    @staticmethod
    def validate_file_path(path: str) -> bool:
        """
        Validate file path for security.
        
        Args:
            path: File path to validate
            
        Raises:
            SecurityError: If path is suspicious
            
        Returns:
            bool: True if path appears safe
        """
        if not path or len(path) > 4096:
            raise SecurityError("Invalid path length")
        
        # Check for dangerous patterns
        dangerous_patterns = ['..', '~', '$', '`', '|', ';', '&', '\x00']
        for pattern in dangerous_patterns:
            if pattern in path:
                raise SecurityError(f"Dangerous pattern in path: {pattern}")
        
        # Check for suspicious extensions
        suspicious_extensions = [
            '.exe', '.bat', '.cmd', '.com', '.pif', '.scr',
            '.vbs', '.js', '.jar', '.app', '.deb', '.rpm',
            '.dmg', '.pkg', '.msi', '.dll', '.so', '.dylib'
        ]
        
        path_lower = path.lower()
        for ext in suspicious_extensions:
            if path_lower.endswith(ext):
                raise SecurityError(f"Suspicious file extension: {ext}")
        
        return True
    
    @staticmethod
    def validate_migration_type(migration_type: str) -> bool:
        """
        Validate migration type parameter.
        
        Args:
            migration_type: Type of migration to perform
            
        Raises:
            SecurityError: If migration type is invalid
            
        Returns:
            bool: True if migration type is allowed
        """
        if not migration_type:
            raise SecurityError("Migration type cannot be empty")
        
        # Allowed migration types (whitelist approach)
        allowed_types = {
            'react-hooks', 'vue3', 'python3', 'typescript',
            'graphql', 'angular', 'svelte', 'nextjs', 'nuxtjs'
        }
        
        if migration_type not in allowed_types:
            raise SecurityError(f"Unsupported migration type: {migration_type}")
        
        return True
    
    @staticmethod
    def sanitize_user_input(input_str: str) -> str:
        """
        Sanitize user input for logging/display.
        
        Args:
            input_str: Raw user input
            
        Returns:
            str: Sanitized input safe for display
        """
        if not input_str:
            return ""
        
        # Remove control characters (including newlines/tabs for safe logging)
        sanitized = re.sub(r'[\x00-\x1F\x7F]', '', input_str)
        
        # Limit length
        if len(sanitized) > 200:
            sanitized = sanitized[:200] + "..."
        
        return sanitized.strip()
