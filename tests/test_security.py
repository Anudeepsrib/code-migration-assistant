import pytest
import os
from pathlib import Path
import sys

# Helper to verify imports works from test dir
sys.path.append(str(Path(__file__).parent.parent))

from scripts.utils.sanitizer import validate_path, SecurityError
from scripts.utils.file_handler import safe_write_file

class TestSecurity:
    def test_validate_path_valid(self, tmp_path):
        # Create a file in tmp_path
        f = tmp_path / "test.txt"
        f.touch()
        
        # Should pass
        validated = validate_path(str(f), base_dir=str(tmp_path))
        assert validated == f.resolve()

    def test_validate_path_traversal(self, tmp_path):
        # Try to access parent of tmp_path
        parent = tmp_path.parent
        target = parent / "secret.txt"
        
        with pytest.raises(SecurityError):
            validate_path(f"../{target.name}", base_dir=str(tmp_path))

    def test_safe_write_backup(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("original")
        
        # Function under test
        safe_write_file(str(f), "new_content", base_dir=str(tmp_path))
        
        assert f.read_text() == "new_content"
        
        # Check if backup exists
        backup_dir = tmp_path / ".migration-backups"
        assert backup_dir.exists()
        backups = list(backup_dir.glob("*.bak"))
        assert len(backups) == 1
        assert backups[0].read_text() == "original"
