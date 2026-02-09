"""
Secure file operations with integrity guarantees.

Features:
- Atomic writes (no partial corruption)
- Automatic backups before modification
- Checksum verification
- Permission preservation
- Rollback capability
"""

import hashlib
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional

from .input_validator import SecurityError


class SecureFileHandler:
    """
    Safe file operations with integrity guarantees.
    
    Security Features:
    - Atomic writes (no partial corruption)
    - Automatic backups before modification
    - Checksum verification
    - Permission preservation
    - Rollback capability
    """
    
    def __init__(self, base_dir: Path, backup_dir: Optional[Path] = None):
        """
        Initialize secure file handler.
        
        Args:
            base_dir: Base working directory
            backup_dir: Directory for backups (creates default if None)
        """
        self.base_dir = Path(base_dir)
        
        if backup_dir is None:
            self.backup_dir = self.base_dir / '.migration-backups'
        else:
            self.backup_dir = Path(backup_dir)
        
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def calculate_checksum(self, file_path: Path) -> str:
        """
        Calculate SHA-256 checksum for integrity.
        
        Args:
            file_path: Path to file
            
        Returns:
            SHA-256 hex digest
        """
        sha256 = hashlib.sha256()
        
        try:
            with open(file_path, 'rb') as f:
                # Read in chunks to handle large files
                for chunk in iter(lambda: f.read(8192), b''):
                    sha256.update(chunk)
        except (OSError, IOError) as e:
            raise SecurityError(f"Failed to calculate checksum: {e}")
        
        return sha256.hexdigest()
    
    def backup(self, file_path: Path) -> Path:
        """
        Create timestamped backup with checksum.
        
        Args:
            file_path: File to backup
            
        Returns:
            Path to backup file
        """
        if not file_path.exists():
            raise SecurityError(f"Cannot backup non-existent file: {file_path}")
        
        # Create timestamped backup name
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]  # Include milliseconds
        relative_path = file_path.relative_to(self.base_dir)
        backup_name = f"{relative_path}.{timestamp}.bak"
        backup_path = self.backup_dir / backup_name
        
        # Create backup directory structure
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy with metadata
        try:
            shutil.copy2(file_path, backup_path)
        except (OSError, IOError) as e:
            raise SecurityError(f"Failed to create backup: {e}")
        
        # Store checksum
        try:
            checksum = self.calculate_checksum(backup_path)
            checksum_path = backup_path.with_suffix('.sha256')
            checksum_path.write_text(checksum)
        except (OSError, IOError) as e:
            # If checksum fails, remove backup to maintain consistency
            backup_path.unlink(missing_ok=True)
            raise SecurityError(f"Failed to store checksum: {e}")
        
        return backup_path
    
    def atomic_write(self, file_path: Path, content: str, create_backup: bool = True) -> None:
        """
        Write file atomically to prevent corruption.
        
        Process:
        1. Create backup of original (optional)
        2. Write to temporary file
        3. Verify checksum
        4. Atomic rename (OS-level operation)
        
        Args:
            file_path: Target file path
            content: Content to write
            create_backup: Whether to backup existing file
        """
        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Backup original if exists and requested
        if create_backup and file_path.exists():
            self.backup(file_path)
        
        # Write to temp file first
        temp_fd, temp_path = tempfile.mkstemp(
            dir=file_path.parent,
            prefix='.tmp_',
            suffix=file_path.suffix
        )
        
        try:
            # Write content to temp file
            with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                f.write(content)
                f.flush()
                os.fsync(f.fileno())  # Force to disk
            
            # Preserve original permissions if file exists
            if file_path.exists():
                try:
                    shutil.copystat(file_path, temp_path)
                except (OSError, IOError):
                    # Non-critical, continue
                    pass
            
            # Verify content was written correctly
            with open(temp_path, 'r', encoding='utf-8') as f:
                written_content = f.read()
                if written_content != content:
                    raise SecurityError("Content verification failed")
            
            # Atomic rename (POSIX guarantees atomicity)
            os.replace(temp_path, file_path)
            
        except Exception as e:
            # Clean up temp file on error
            Path(temp_path).unlink(missing_ok=True)
            raise SecurityError(f"Atomic write failed: {e}")
    
    def verify_integrity(self, file_path: Path, expected_checksum: Optional[str] = None) -> bool:
        """
        Verify file integrity using checksum.
        
        Args:
            file_path: File to verify
            expected_checksum: Expected checksum (calculates if None)
            
        Returns:
            True if integrity verified
        """
        if not file_path.exists():
            return False
        
        try:
            actual_checksum = self.calculate_checksum(file_path)
            
            if expected_checksum is None:
                # Look for checksum file
                checksum_file = file_path.with_suffix('.sha256')
                if checksum_file.exists():
                    expected_checksum = checksum_file.read_text().strip()
                else:
                    # No checksum to verify against
                    return True
            
            return actual_checksum == expected_checksum
            
        except (OSError, IOError):
            return False
    
    def restore_from_backup(self, file_path: Path, backup_timestamp: Optional[str] = None) -> Path:
        """
        Restore file from backup.
        
        Args:
            file_path: File to restore
            backup_timestamp: Specific backup timestamp (uses latest if None)
            
        Returns:
            Path to restored file
        """
        relative_path = file_path.relative_to(self.base_dir)
        
        if backup_timestamp:
            backup_name = f"{relative_path}.{backup_timestamp}.bak"
            backup_path = self.backup_dir / backup_name
            
            if not backup_path.exists():
                raise SecurityError(f"Backup not found: {backup_path}")
        else:
            # Find latest backup
            backup_pattern = f"{relative_path}.*.bak"
            backup_files = list(self.backup_dir.glob(backup_pattern))
            
            if not backup_files:
                raise SecurityError(f"No backups found for: {file_path}")
            
            # Sort by modification time
            backup_path = max(backup_files, key=lambda p: p.stat().st_mtime)
        
        # Verify backup integrity
        if not self.verify_integrity(backup_path):
            raise SecurityError(f"Backup integrity check failed: {backup_path}")
        
        # Create backup of current file before restore
        if file_path.exists():
            self.backup(file_path)
        
        # Restore from backup
        try:
            shutil.copy2(backup_path, file_path)
        except (OSError, IOError) as e:
            raise SecurityError(f"Failed to restore from backup: {e}")
        
        return file_path
    
    def list_backups(self, file_path: Path) -> list:
        """
        List all backups for a file.
        
        Args:
            file_path: File to list backups for
            
        Returns:
            List of backup file paths sorted by timestamp
        """
        relative_path = file_path.relative_to(self.base_dir)
        backup_pattern = f"{relative_path}.*.bak"
        backup_files = list(self.backup_dir.glob(backup_pattern))
        
        # Sort by timestamp in filename
        backup_files.sort(key=lambda p: p.name, reverse=True)
        
        return backup_files
    
    def cleanup_old_backups(self, max_age_days: int = 30, max_count: int = 10) -> int:
        """
        Clean up old backups to save space.
        
        Args:
            max_age_days: Maximum age in days
            max_count: Maximum backups per file
            
        Returns:
            Number of backups deleted
        """
        deleted_count = 0
        cutoff_time = datetime.now().timestamp() - (max_age_days * 24 * 3600)
        
        # Group backups by original file
        backup_groups = {}
        for backup_file in self.backup_dir.glob('*.bak'):
            # Extract original filename (remove timestamp and .bak)
            name_parts = backup_file.name.split('.')
            if len(name_parts) >= 3:  # filename.timestamp.bak
                original_name = '.'.join(name_parts[:-2])
                if original_name not in backup_groups:
                    backup_groups[original_name] = []
                backup_groups[original_name].append(backup_file)
        
        # Clean up each group
        for original_name, backups in backup_groups.items():
            # Sort by modification time (newest first)
            backups.sort(key=lambda p: p.stat().st_mtime, reverse=True)
            
            # Keep only the newest max_count backups
            for backup in backups[max_count:]:
                backup.unlink(missing_ok=True)
                backup.with_suffix('.sha256').unlink(missing_ok=True)
                deleted_count += 1
            
            # Remove old backups
            for backup in backups:
                if backup.stat().st_mtime < cutoff_time:
                    backup.unlink(missing_ok=True)
                    backup.with_suffix('.sha256').unlink(missing_ok=True)
                    deleted_count += 1
        
        return deleted_count
