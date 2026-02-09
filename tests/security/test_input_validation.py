"""
Test suite for input validation security controls.

Tests OWASP A03:2021 injection prevention and input sanitization.
"""

import pytest
from pathlib import Path

from code_migration.core.security import CodeValidator, SecurityError


class TestCodeValidator:
    """Test input validation security controls."""
    
    def test_valid_pattern_acceptance(self):
        """Test that valid patterns are accepted."""
        valid_patterns = [
            "def hello_world():\n    print('Hello, World!')",
            "class MyClass:\n    def __init__(self):\n        pass",
            "import os\nimport sys",
            "x = 5 + 3\ny = x * 2"
        ]
        
        for pattern in valid_patterns:
            assert CodeValidator.validate_pattern(pattern) is True
    
    def test_forbidden_keywords_rejection(self):
        """Test that forbidden keywords are rejected."""
        forbidden_patterns = [
            "eval('print(1)')",
            "exec('print(1)')",
            "compile('print(1)', '', 'exec')",
            "__import__('os')",
            "open('file.txt', 'r')",
            "globals()",
            "locals()",
            "dir()",
            "hasattr(obj, 'attr')",
            "getattr(obj, 'attr')",
            "setattr(obj, 'attr', 'value')",
            "delattr(obj, 'attr')",
            "callable(obj)",
            "isinstance(obj, cls)",
            "issubclass(Sub, Base)"
        ]
        
        for pattern in forbidden_patterns:
            with pytest.raises(SecurityError, match="Forbidden keyword"):
                CodeValidator.validate_pattern(pattern)
    
    def test_forbidden_modules_rejection(self):
        """Test that forbidden modules are rejected."""
        forbidden_module_patterns = [
            "import os",
            "import sys",
            "import subprocess",
            "import socket",
            "import urllib",
            "import http",
            "import ftplib",
            "import smtplib",
            "import pickle",
            "import marshal",
            "import shelve",
            "import dbm",
            "import ctypes",
            "import threading",
            "import multiprocessing"
        ]
        
        for pattern in forbidden_module_patterns:
            with pytest.raises(SecurityError, match="Forbidden module"):
                CodeValidator.validate_pattern(pattern)
    
    def test_size_limit_enforcement(self):
        """Test that size limits are enforced."""
        # Test oversized pattern
        oversized_pattern = "x = 1\n" * 1001  # Over 1000 lines
        
        with pytest.raises(SecurityError, match="too many lines"):
            CodeValidator.validate_pattern(oversized_pattern)
        
        # Test oversized single line
        oversized_line = "x = " + "a" * 1001  # Over 1000 characters
        
        with pytest.raises(SecurityError, match="line exceeds maximum"):
            CodeValidator.validate_pattern(oversized_line)
        
        # Test oversized total size
        oversized_content = "x = 1" * 10000  # Over 10KB
        
        with pytest.raises(SecurityError, match="Pattern size exceeds"):
            CodeValidator.validate_pattern(oversized_content)
    
    def test_invalid_syntax_rejection(self):
        """Test that invalid Python syntax is rejected."""
        invalid_patterns = [
            "def invalid_syntax(\n    # Missing closing parenthesis",
            "if True\n    print('no colon')",
            "x = 1 + + 2",  # Invalid operator
            "class InvalidClass\n    def __init__(self\n        pass"  # Missing colon
        ]
        
        for pattern in invalid_patterns:
            with pytest.raises(SecurityError, match="Invalid Python syntax"):
                CodeValidator.validate_pattern(pattern)
    
    def test_valid_file_path_acceptance(self):
        """Test that valid file paths are accepted."""
        valid_paths = [
            "src/components/Button.jsx",
            "lib/utils.py",
            "tests/test_migration.py",
            "config/settings.yaml",
            "docs/README.md"
        ]
        
        for path in valid_paths:
            assert CodeValidator.validate_file_path(path) is True
    
    def test_dangerous_path_rejection(self):
        """Test that dangerous paths are rejected."""
        dangerous_paths = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32\\config\\sam",
            "~/.ssh/id_rsa",
            "$HOME/.bashrc",
            "`rm -rf /`",
            "|cat /etc/passwd",
            "; rm -rf /",
            "& malicious_command",
            "\x00malicious",
            "file.exe",
            "script.bat",
            "malicious.com"
        ]
        
        for path in dangerous_paths:
            with pytest.raises(SecurityError):
                CodeValidator.validate_file_path(path)
    
    def test_valid_migration_types(self):
        """Test that valid migration types are accepted."""
        valid_types = [
            "react-hooks",
            "vue3", 
            "python3",
            "typescript",
            "graphql",
            "angular",
            "svelte",
            "nextjs",
            "nuxtjs"
        ]
        
        for migration_type in valid_types:
            assert CodeValidator.validate_migration_type(migration_type) is True
    
    def test_invalid_migration_type_rejection(self):
        """Test that invalid migration types are rejected."""
        invalid_types = [
            "",
            "invalid-type",
            "react hooks",  # Space not allowed
            "malicious;rm -rf",
            "../etc/passwd"
        ]
        
        for migration_type in invalid_types:
            with pytest.raises(SecurityError):
                CodeValidator.validate_migration_type(migration_type)
    
    def test_user_input_sanitization(self):
        """Test user input sanitization."""
        test_cases = [
            ("Normal input", "Normal input"),
            ("Input with\nnewlines", "Input withnewlines"),
            ("Input with\ttabs", "Input withtabs"),
            ("Very long input that should be truncated " * 10, "Very long input that should be truncated ..."),
            ("", ""),
            (None, "")
        ]
        
        for input_str, expected in test_cases:
            result = CodeValidator.sanitize_user_input(input_str)
            assert result == expected
            assert len(result) <= 200  # Should be truncated if too long


class TestSecurityEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_empty_inputs(self):
        """Test handling of empty inputs."""
        with pytest.raises(SecurityError):
            CodeValidator.validate_pattern("")
        
        with pytest.raises(SecurityError):
            CodeValidator.validate_file_path("")
        
        with pytest.raises(SecurityError):
            CodeValidator.validate_migration_type("")
    
    def test_unicode_handling(self):
        """Test proper handling of Unicode characters."""
        # Valid Unicode should be accepted
        unicode_pattern = "def hello_世界():\n    print('Hello, 世界!')"
        assert CodeValidator.validate_pattern(unicode_pattern) is True
        
        # Control characters should be rejected
        control_char_pattern = "x = 1\x00"  # Null byte
        with pytest.raises(SecurityError):
            CodeValidator.validate_pattern(control_char_pattern)
    
    def test_case_insensitive_detection(self):
        """Test case-insensitive detection of forbidden patterns."""
        case_variants = [
            "EVAL('print(1)')",
            "Exec('print(1)')",
            "IMPORT OS",
            "OPEN('file.txt')",
            "GLOBALS()",
            "GETATTR(OBJ, 'ATTR')"
        ]
        
        for variant in case_variants:
            with pytest.raises(SecurityError, match="Forbidden keyword"):
                CodeValidator.validate_pattern(variant)
    
    def test_nested_forbidden_patterns(self):
        """Test detection of nested forbidden patterns."""
        nested_patterns = [
            "def func():\n    # This looks safe\n    eval('print(1)')  # But contains eval",
            "class Safe:\n    def method(self):\n        import os  # Forbidden import in method",
            "if True:\n        x = 1\n    else:\n        exec('print(1)')  # Forbidden in else block"
        ]
        
        for pattern in nested_patterns:
            with pytest.raises(SecurityError):
                CodeValidator.validate_pattern(pattern)
    
    def test_comment_obfuscation_attempts(self):
        """Test detection of forbidden patterns in comments."""
        obfuscated_patterns = [
            "# eval('print(1)')  # Forbidden in comment",
            "''' \nexec('print(1)')\n '''  # Forbidden in multiline string",
            "x = 1  # eval('safe')  # Still contains eval keyword"
        ]
        
        for pattern in obfuscated_patterns:
            with pytest.raises(SecurityError):
                CodeValidator.validate_pattern(pattern)
