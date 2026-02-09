"""
Test suite for path sanitization security controls.

Tests CWE-22 path traversal prevention and path validation.
"""

import pytest
import tempfile
from pathlib import Path

from code_migration.core.security import PathSanitizer, SecurityError


class TestPathSanitizer:
    """Test path traversal protection and sanitization."""
    
    @pytest.fixture
    def temp_base_dir(self):
        """Create a temporary base directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    def test_safe_path_acceptance(self, temp_base_dir):
        """Test that safe paths are accepted."""
        # Create some test files
        (temp_base_dir / "safe_file.py").touch()
        (temp_base_dir / "safe_dir").mkdir()
        (temp_base_dir / "safe_dir" / "nested_file.py").touch()
        
        safe_paths = [
            "safe_file.py",
            "safe_dir/nested_file.py",
            "safe_dir",
            "config/settings.yaml",
            "tests/test_migration.py"
        ]
        
        for path_str in safe_paths:
            path_obj = PathSanitizer.sanitize(path_str, temp_base_dir)
            assert isinstance(path_obj, Path)
            assert path_obj.is_relative_to(temp_base_dir)
            assert path_obj.exists()
    
    def test_path_traversal_rejection(self, temp_base_dir):
        """Test that path traversal attempts are rejected."""
        traversal_paths = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32\\config\\sam",
            "safe_file.py/../../../etc/passwd",
            "safe_dir/../../../root/.ssh/id_rsa",
            "~/.ssh/id_rsa",
            "/etc/passwd",
            "C:\\Windows\\System32\\config\\sam"
        ]
        
        for path_str in traversal_paths:
            with pytest.raises(SecurityError, match="Dangerous pattern"):
                PathSanitizer.sanitize(path_str, temp_base_dir)
    
    def test_dangerous_pattern_detection(self, temp_base_dir):
        """Test detection of dangerous path patterns."""
        dangerous_patterns = [
            "file.py~",  # Backup file
            "script.sh",  # Shell script
            "malicious.exe",
            "virus.bat",
            "trojan.com",
            "rootkit.dll",
            "malware.so",
            "backdoor.dylib"
        ]
        
        for pattern in dangerous_patterns:
            with pytest.raises(SecurityError, match="File extension not allowed"):
                PathSanitizer.sanitize(pattern, temp_base_dir)
    
    def test_path_length_limits(self, temp_base_dir):
        """Test enforcement of path length limits."""
        # Create extremely long path
        long_path = "a" * 5000  # Over 4096 character limit
        
        with pytest.raises(SecurityError, match="Invalid path length"):
            PathSanitizer.sanitize(long_path, temp_base_dir)
    
    def test_nonexistent_file_handling(self, temp_base_dir):
        """Test handling of non-existent files."""
        nonexistent_paths = [
            "nonexistent_file.py",
            "nonexistent_dir/file.py",
            "deep/nonexistent/path/file.py"
        ]
        
        for path_str in nonexistent_paths:
            with pytest.raises(SecurityError, match="Path resolution failed"):
                PathSanitizer.sanitize(path_str, temp_base_dir)
    
    def test_directory_sanitization(self, temp_base_dir):
        """Test directory path sanitization."""
        # Create test directory
        test_dir = temp_base_dir / "test_directory"
        test_dir.mkdir()
        
        # Safe directory path
        safe_dir = PathSanitizer.sanitize_directory("test_directory", temp_base_dir)
        assert safe_dir == test_dir
        assert safe_dir.is_relative_to(temp_base_dir)
        
        # Traversal attempt in directory
        with pytest.raises(SecurityError):
            PathSanitizer.sanitize_directory("../etc", temp_base_dir)
    
    def test_safe_filename_validation(self):
        """Test safe filename validation."""
        safe_filenames = [
            "normal_file.py",
            "file-with-dashes.js",
            "file_with_underscores.ts",
            "file123.py",
            "UPPERCASE.PY"
        ]
        
        for filename in safe_filenames:
            assert PathSanitizer.is_safe_filename(filename) is True
        
        unsafe_filenames = [
            "../../../etc/passwd",
            "file/with/slashes",
            "file\\with\\backslashes",
            " file ",  # Leading/trailing spaces
            "file.",  # Trailing dot
            "CON",  # Windows reserved name
            "PRN",
            "AUX",
            "COM1",
            "LPT1"
        ]
        
        for filename in unsafe_filenames:
            assert PathSanitizer.is_safe_filename(filename) is False
    
    def test_relative_path_extraction(self, temp_base_dir):
        """Test safe relative path extraction."""
        # Create test file
        test_file = temp_base_dir / "subdir" / "test_file.py"
        test_file.parent.mkdir(parents=True)
        test_file.touch()
        
        # Test relative path extraction
        abs_path = test_file.resolve()
        rel_path = PathSanitizer.get_relative_path(abs_path, temp_base_dir)
        
        assert rel_path == "subdir/test_file.py"
        
        # Test with non-relative path
        unrelated_path = Path("/etc/passwd")
        fallback_path = PathSanitizer.get_relative_path(unrelated_path, temp_base_dir)
        assert fallback_path == "passwd"
    
    def test_allowed_extensions_whitelist(self, temp_base_dir):
        """Test that only allowed file extensions are accepted."""
        allowed_extensions = [
            ".py", ".js", ".jsx", ".ts", ".tsx", ".vue", ".html",
            ".css", ".scss", ".less", ".json", ".yaml", ".yml",
            ".md", ".txt", ".xml", ".sql", ".sh", ".bash"
        ]
        
        # Create test files with allowed extensions
        for ext in allowed_extensions:
            test_file = temp_base_dir / f"test{ext}"
            test_file.touch()
            
            sanitized_path = PathSanitizer.sanitize(f"test{ext}", temp_base_dir)
            assert sanitized_path == test_file
            assert sanitized_path.suffix.lower() == ext.lower()
        
        # Test disallowed extensions
        disallowed_extensions = [
            ".exe", ".bat", ".cmd", ".com", ".pif", ".scr",
            ".vbs", ".jar", ".app", ".deb", ".rpm",
            ".dmg", ".pkg", ".msi", ".dll", ".so", ".dylib"
        ]
        
        for ext in disallowed_extensions:
            with pytest.raises(SecurityError, match="File extension not allowed"):
                PathSanitizer.sanitize(f"test{ext}", temp_base_dir)


class TestPathSanitizerEdgeCases:
    """Test edge cases and boundary conditions."""
    
    @pytest.fixture
    def temp_base_dir(self):
        """Create a temporary base directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    def test_empty_path_handling(self, temp_base_dir):
        """Test handling of empty paths."""
        with pytest.raises(SecurityError, match="Invalid path length"):
            PathSanitizer.sanitize("", temp_base_dir)
    
    def test_unicode_path_handling(self, temp_base_dir):
        """Test proper handling of Unicode in paths."""
        # Create test file with Unicode name
        unicode_file = temp_base_dir / "测试文件.py"
        unicode_file.touch()
        
        # Should be accepted
        sanitized_path = PathSanitizer.sanitize("测试文件.py", temp_base_dir)
        assert sanitized_path == unicode_file
        
        # Control characters should be rejected
        with pytest.raises(SecurityError):
            PathSanitizer.sanitize("file\x00.py", temp_base_dir)
    
    def test_case_sensitive_extensions(self, temp_base_dir):
        """Test case-sensitive extension handling."""
        # Create files with mixed case extensions
        (temp_base_dir / "test.PY").touch()
        (temp_base_dir / "test.JS").touch()
        (temp_base_dir / "test.EXE").touch()
        
        # Allowed extensions should work regardless of case
        assert PathSanitizer.sanitize("test.PY", temp_base_dir).exists()
        assert PathSanitizer.sanitize("test.JS", temp_base_dir).exists()
        
        # Disallowed extensions should be rejected regardless of case
        with pytest.raises(SecurityError):
            PathSanitizer.sanitize("test.EXE", temp_base_dir)
    
    def test_symlink_handling(self, temp_base_dir):
        """Test safe handling of symbolic links."""
        if not temp_base_dir.exists():
            temp_base_dir.mkdir(parents=True)
        
        # Create a file and a symlink
        original_file = temp_base_dir / "original.py"
        original_file.touch()
        
        try:
            # Create symlink (may not work on all systems)
            symlink_path = temp_base_dir / "symlink.py"
            symlink_path.symlink_to(original_file)
            
            # Should resolve to the original file
            sanitized_path = PathSanitizer.sanitize("symlink.py", temp_base_dir)
            assert sanitized_path.resolve() == original_file.resolve()
            
        except (OSError, NotImplementedError):
            # Symlinks not supported on this system
            pass
    
    def test_max_path_length_boundary(self, temp_base_dir):
        """Test boundary conditions for path length."""
        # Test exactly at the limit
        max_length_path = "a" * 4096
        
        with pytest.raises(SecurityError, match="Invalid path length"):
            PathSanitizer.sanitize(max_length_path, temp_base_dir)
        
        # Test just under the limit
        under_limit_path = "a" * 100
        # This should not raise length error, but may raise other errors
        try:
            PathSanitizer.sanitize(under_limit_path, temp_base_dir)
        except SecurityError as e:
            # Should not be a length error
            assert "Invalid path length" not in str(e)
    
    def test_nested_directory_traversal(self, temp_base_dir):
        """Test complex nested traversal attempts."""
        complex_traversal_paths = [
            "safe_dir/../../../etc/passwd",
            "safe_dir/nested/../../root/.ssh",
            "a/b/c/../../../etc/passwd",
            "very/deep/nested/path/../../../windows/system32"
        ]
        
        for path_str in complex_traversal_paths:
            with pytest.raises(SecurityError, match="Dangerous pattern"):
                PathSanitizer.sanitize(path_str, temp_base_dir)
    
    def test_path_with_special_characters(self, temp_base_dir):
        """Test paths with various special characters."""
        # Create test files with special characters
        special_files = [
            "file-with-dashes.py",
            "file_with_underscores.py",
            "file.with.dots.py",
            "file123.py"
        ]
        
        for filename in special_files:
            test_file = temp_base_dir / filename
            test_file.touch()
            
            sanitized_path = PathSanitizer.sanitize(filename, temp_base_dir)
            assert sanitized_path == test_file
        
        # Test dangerous special characters
        dangerous_chars = [
            "file`malicious.py",
            "file|dangerous.py",
            "file;rm -rf.py",
            "file&malicious.py"
        ]
        
        for filename in dangerous_chars:
            with pytest.raises(SecurityError, match="Dangerous pattern"):
                PathSanitizer.sanitize(filename, temp_base_dir)
