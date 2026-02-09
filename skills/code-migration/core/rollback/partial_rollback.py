"""
Partial rollback manager for surgical file restoration.

Provides granular rollback capabilities:
- Selective file restoration
- File version comparison
- Conflict resolution
- Safe partial rollbacks
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from ..security import SecurityAuditLogger, SecureFileHandler


class PartialRollbackManager:
    """
    Surgical partial rollback system.
    
    Features:
    - Selective file restoration
    - File version comparison
    - Conflict resolution
    - Safe partial rollbacks
    - Rollback preview
    """
    
    def __init__(self, project_path: Path, checkpoint_dir: Path):
        """
        Initialize partial rollback manager.
        
        Args:
            project_path: Path to project directory
            checkpoint_dir: Directory containing checkpoints
        """
        self.project_path = Path(project_path)
        self.checkpoint_dir = Path(checkpoint_dir)
        
        # Initialize security components
        self.secure_handler = SecureFileHandler(project_path)
        
        # Initialize audit logger
        log_dir = self.project_path / '.migration-logs'
        self.audit_logger = SecurityAuditLogger(log_dir)
    
    def preview_partial_rollback(
        self,
        checkpoint_id: str,
        files: List[str],
        include_dependencies: bool = False
    ) -> Dict:
        """
        Preview partial rollback without applying changes.
        
        Args:
            checkpoint_id: Checkpoint to rollback from
            files: List of files to rollback
            include_dependencies: Whether to include dependent files
            
        Returns:
            Preview results with changes
        """
        checkpoint_path = self.checkpoint_dir / checkpoint_id
        
        if not checkpoint_path.exists():
            raise ValueError(f"Checkpoint not found: {checkpoint_id}")
        
        # Analyze changes
        changes = self._analyze_file_changes(checkpoint_id, files)
        
        # Include dependencies if requested
        if include_dependencies:
            dependency_files = self._find_file_dependencies(files)
            changes['dependency_files'] = dependency_files
            changes['total_files'] = len(files) + len(dependency_files)
        
        # Calculate impact
        impact = self._calculate_rollback_impact(changes)
        
        # Detect potential conflicts
        conflicts = self._detect_rollback_conflicts(checkpoint_id, files)
        
        preview = {
            'checkpoint_id': checkpoint_id,
            'requested_files': files,
            'changes': changes,
            'impact': impact,
            'conflicts': conflicts,
            'timestamp': datetime.now().isoformat()
        }
        
        return preview
    
    def execute_partial_rollback(
        self,
        checkpoint_id: str,
        files: List[str],
        conflict_resolution: str = "checkpoint",
        create_backup: bool = True,
        include_dependencies: bool = False
    ) -> Dict:
        """
        Execute partial rollback with conflict resolution.
        
        Args:
            checkpoint_id: Checkpoint to rollback from
            files: List of files to rollback
            conflict_resolution: How to handle conflicts (checkpoint, current, manual)
            create_backup: Whether to create backup before rollback
            include_dependencies: Whether to include dependent files
            
        Returns:
            Rollback execution results
        """
        # Log rollback attempt
        self.audit_logger.log_migration_event(
            migration_type='partial_rollback',
            project_path=str(self.project_path),
            user='system',
            action='EXECUTE_PARTIAL_ROLLBACK',
            result='STARTED',
            details={
                'checkpoint_id': checkpoint_id,
                'files': files,
                'conflict_resolution': conflict_resolution
            }
        )
        
        try:
            # Create backup if requested
            backup_checkpoint = None
            if create_backup:
                from .snapshot_manager import TimeMachineRollback
                tm = TimeMachineRollback(self.project_path)
                backup_checkpoint = tm.create_checkpoint(
                    f"Pre-partial-rollback backup for {checkpoint_id}",
                    tags=['partial-rollback-backup']
                )
            
            # Get all files to rollback
            files_to_rollback = set(files)
            if include_dependencies:
                dependency_files = self._find_file_dependencies(files)
                files_to_rollback.update(dependency_files)
            
            # Execute rollback
            results = {
                'checkpoint_id': checkpoint_id,
                'backup_checkpoint': backup_checkpoint,
                'files_requested': files,
                'files_processed': list(files_to_rollback),
                'results': {},
                'conflicts_resolved': [],
                'errors': []
            }
            
            for file_path in files_to_rollback:
                try:
                    file_result = self._rollback_single_file(
                        checkpoint_id, file_path, conflict_resolution
                    )
                    results['results'][file_path] = file_result
                    
                    if file_result.get('conflict_resolved'):
                        results['conflicts_resolved'].append(file_path)
                        
                except Exception as e:
                    results['errors'].append({
                        'file': file_path,
                        'error': str(e)
                    })
            
            # Calculate summary
            successful = sum(1 for r in results['results'].values() if r.get('success', False))
            results['summary'] = {
                'total_files': len(files_to_rollback),
                'successful': successful,
                'failed': len(results['errors']),
                'conflicts_resolved': len(results['conflicts_resolved'])
            }
            
            # Log completion
            self.audit_logger.log_migration_event(
                migration_type='partial_rollback',
                project_path=str(self.project_path),
                user='system',
                action='EXECUTE_PARTIAL_ROLLBACK',
                result='SUCCESS' if results['summary']['failed'] == 0 else 'PARTIAL',
                details={
                    'checkpoint_id': checkpoint_id,
                    'summary': results['summary']
                }
            )
            
            return results
            
        except Exception as e:
            self.audit_logger.log_migration_event(
                migration_type='partial_rollback',
                project_path=str(self.project_path),
                user='system',
                action='EXECUTE_PARTIAL_ROLLBACK',
                result='FAILURE',
                details={
                    'checkpoint_id': checkpoint_id,
                    'error': str(e)
                }
            )
            raise
    
    def compare_file_versions(
        self,
        checkpoint_id: str,
        file_path: str
    ) -> Dict:
        """
        Compare file versions between checkpoint and current.
        
        Args:
            checkpoint_id: Checkpoint to compare
            file_path: File to compare
            
        Returns:
            Comparison results
        """
        checkpoint_path = self.checkpoint_dir / checkpoint_id
        checkpoint_file = checkpoint_path / file_path
        current_file = self.project_path / file_path
        
        comparison = {
            'file_path': file_path,
            'checkpoint_id': checkpoint_id,
            'checkpoint_exists': checkpoint_file.exists(),
            'current_exists': current_file.exists()
        }
        
        if not checkpoint_file.exists():
            comparison['status'] = 'FILE_NOT_IN_CHECKPOINT'
            return comparison
        
        if not current_file.exists():
            comparison['status'] = 'FILE_NOT_IN_CURRENT'
            comparison['action'] = 'restore'
            return comparison
        
        try:
            # Calculate checksums
            checkpoint_checksum = self.secure_handler.calculate_checksum(checkpoint_file)
            current_checksum = self.secure_handler.calculate_checksum(current_file)
            
            comparison['checkpoint_checksum'] = checkpoint_checksum
            comparison['current_checksum'] = current_checksum
            
            if checkpoint_checksum == current_checksum:
                comparison['status'] = 'IDENTICAL'
                comparison['action'] = 'none'
            else:
                comparison['status'] = 'DIFFERENT'
                comparison['action'] = 'restore'
                
                # Get file stats
                checkpoint_stats = checkpoint_file.stat()
                current_stats = current_file.stat()
                
                comparison.update({
                    'checkpoint_size': checkpoint_stats.st_size,
                    'current_size': current_stats.st_size,
                    'checkpoint_modified': datetime.fromtimestamp(checkpoint_stats.st_mtime).isoformat(),
                    'current_modified': datetime.fromtimestamp(current_stats.st_mtime).isoformat(),
                    'size_difference': current_stats.st_size - checkpoint_stats.st_size
                })
                
                # Basic content diff (for text files)
                if self._is_text_file(file_path):
                    comparison['content_diff'] = self._generate_content_diff(
                        checkpoint_file, current_file
                    )
        
        except Exception as e:
            comparison['status'] = 'ERROR'
            comparison['error'] = str(e)
        
        return comparison
    
    def get_rollback_history(
        self,
        file_path: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """
        Get rollback history for files.
        
        Args:
            file_path: Specific file to get history for (None = all files)
            limit: Maximum number of entries
            
        Returns:
            List of rollback history entries
        """
        # This would read from audit logs in a full implementation
        # For now, return placeholder data
        return [
            {
                'timestamp': datetime.now().isoformat(),
                'checkpoint_id': '20231201_120000',
                'file_path': file_path or 'example.py',
                'action': 'rollback',
                'success': True
            }
        ]
    
    def _analyze_file_changes(self, checkpoint_id: str, files: List[str]) -> Dict:
        """Analyze changes for specified files."""
        changes = {
            'files_to_restore': [],
            'files_to_delete': [],
            'files_to_create': [],
            'conflicts': []
        }
        
        checkpoint_path = self.checkpoint_dir / checkpoint_id
        
        for file_path in files:
            checkpoint_file = checkpoint_path / file_path
            current_file = self.project_path / file_path
            
            if checkpoint_file.exists() and current_file.exists():
                # File exists in both - check if different
                if self.secure_handler.calculate_checksum(checkpoint_file) != \
                   self.secure_handler.calculate_checksum(current_file):
                    changes['files_to_restore'].append(file_path)
                    
            elif checkpoint_file.exists() and not current_file.exists():
                # File exists in checkpoint but not current - needs to be created
                changes['files_to_create'].append(file_path)
                
            elif not checkpoint_file.exists() and current_file.exists():
                # File exists in current but not checkpoint - needs to be deleted
                changes['files_to_delete'].append(file_path)
        
        changes['total_files'] = len(files)
        changes['files_to_process'] = (
            len(changes['files_to_restore']) + 
            len(changes['files_to_create']) + 
            len(changes['files_to_delete'])
        )
        
        return changes
    
    def _find_file_dependencies(self, files: List[str]) -> List[str]:
        """Find files that depend on the specified files."""
        # Simplified dependency detection
        dependencies = set()
        
        for file_path in files:
            if file_path.endswith('.py'):
                # Look for files that import this module
                module_name = Path(file_path).stem
                
                for other_file in self.project_path.rglob('*.py'):
                    if str(other_file.relative_to(self.project_path)) == file_path:
                        continue
                    
                    try:
                        content = other_file.read_text(encoding='utf-8', errors='ignore')
                        if f'import {module_name}' in content or f'from {module_name}' in content:
                            dependencies.add(str(other_file.relative_to(self.project_path)))
                    except Exception:
                        continue
        
        return list(dependencies)
    
    def _calculate_rollback_impact(self, changes: Dict) -> Dict:
        """Calculate the impact of the rollback."""
        impact = {
            'risk_level': 'LOW',
            'estimated_time_minutes': 0,
            'affected_components': [],
            'potential_issues': []
        }
        
        total_files = changes.get('files_to_process', 0)
        
        # Estimate time (30 seconds per file)
        impact['estimated_time_minutes'] = max(1, total_files * 0.5)
        
        # Determine risk level
        if total_files > 20:
            impact['risk_level'] = 'HIGH'
            impact['potential_issues'].append('Large number of files may cause conflicts')
        elif total_files > 10:
            impact['risk_level'] = 'MEDIUM'
        else:
            impact['risk_level'] = 'LOW'
        
        # Identify affected components
        file_types = set()
        for file_list in [changes.get('files_to_restore', []), 
                         changes.get('files_to_create', []),
                         changes.get('files_to_delete', [])]:
            for file_path in file_list:
                ext = Path(file_path).suffix
                if ext:
                    file_types.add(ext)
        
        impact['affected_components'] = list(file_types)
        
        return impact
    
    def _detect_rollback_conflicts(self, checkpoint_id: str, files: List[str]) -> List[Dict]:
        """Detect potential conflicts in rollback."""
        conflicts = []
        
        for file_path in files:
            comparison = self.compare_file_versions(checkpoint_id, file_path)
            
            if comparison.get('status') == 'DIFFERENT':
                # Check if current file has been modified since checkpoint
                if 'current_modified' in comparison and 'checkpoint_modified' in comparison:
                    current_time = datetime.fromisoformat(comparison['current_modified'])
                    checkpoint_time = datetime.fromisoformat(comparison['checkpoint_modified'])
                    
                    if current_time > checkpoint_time:
                        conflicts.append({
                            'file_path': file_path,
                            'type': 'MODIFIED_SINCE_CHECKPOINT',
                            'description': 'Current file has been modified since checkpoint',
                            'resolution_options': ['checkpoint', 'current', 'manual']
                        })
        
        return conflicts
    
    def _rollback_single_file(
        self,
        checkpoint_id: str,
        file_path: str,
        conflict_resolution: str
    ) -> Dict:
        """Rollback a single file."""
        checkpoint_path = self.checkpoint_dir / checkpoint_id
        checkpoint_file = checkpoint_path / file_path
        current_file = self.project_path / file_path
        
        result = {
            'file_path': file_path,
            'success': False,
            'action_taken': None,
            'conflict_resolved': False
        }
        
        try:
            if checkpoint_file.exists():
                # File exists in checkpoint
                if current_file.exists():
                    # Check for conflict
                    if self.secure_handler.calculate_checksum(checkpoint_file) != \
                       self.secure_handler.calculate_checksum(current_file):
                        
                        # Conflict detected
                        if conflict_resolution == 'checkpoint':
                            # Restore from checkpoint
                            current_file.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(checkpoint_file, current_file)
                            result['action_taken'] = 'restored_from_checkpoint'
                            result['conflict_resolved'] = True
                            
                        elif conflict_resolution == 'current':
                            # Keep current file
                            result['action_taken'] = 'kept_current'
                            result['conflict_resolved'] = True
                            
                        elif conflict_resolution == 'manual':
                            # Manual resolution required
                            result['action_taken'] = 'manual_resolution_required'
                            result['success'] = False
                            return result
                    else:
                        # No conflict, files are identical
                        result['action_taken'] = 'no_action_needed'
                else:
                    # File doesn't exist, restore it
                    current_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(checkpoint_file, current_file)
                    result['action_taken'] = 'created_from_checkpoint'
                
                result['success'] = True
                
            else:
                # File doesn't exist in checkpoint, delete current if it exists
                if current_file.exists():
                    current_file.unlink()
                    result['action_taken'] = 'deleted_current_file'
                    result['success'] = True
                else:
                    result['action_taken'] = 'no_action_needed'
                    result['success'] = True
        
        except Exception as e:
            result['error'] = str(e)
            result['success'] = False
        
        return result
    
    def _is_text_file(self, file_path: str) -> bool:
        """Check if file is likely a text file."""
        text_extensions = {
            '.py', '.js', '.jsx', '.ts', '.tsx', '.vue', '.html', '.css',
            '.json', '.yaml', '.yml', '.md', '.txt', '.xml', '.sql',
            '.sh', '.bash', '.zsh', '.fish'
        }
        
        return Path(file_path).suffix.lower() in text_extensions
    
    def _generate_content_diff(self, file1: Path, file2: Path) -> Dict:
        """Generate basic content diff between two files."""
        try:
            content1 = file1.read_text(encoding='utf-8', errors='ignore')
            content2 = file2.read_text(encoding='utf-8', errors='ignore')
            
            lines1 = content1.splitlines()
            lines2 = content2.splitlines()
            
            # Simple diff statistics
            return {
                'lines_in_file1': len(lines1),
                'lines_in_file2': len(lines2),
                'line_difference': len(lines2) - len(lines1),
                'size_difference': len(content2) - len(content1),
                'has_changes': content1 != content2
            }
            
        except Exception:
            return {
                'error': 'Failed to generate content diff'
            }
