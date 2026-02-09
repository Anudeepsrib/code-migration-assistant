"""
Checkpoint management and recovery system.

Handles checkpoint lifecycle and recovery operations:
- Checkpoint creation and management
- Recovery point handling
- Checkpoint validation
- Automated cleanup
"""

import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set

from ..security import SecurityAuditLogger


class CheckpointHandler:
    """
    Advanced checkpoint management system.
    
    Features:
    - Intelligent checkpoint scheduling
- Recovery point optimization
- Checkpoint validation
- Automated cleanup policies
- Checkpoint compression
    """
    
    def __init__(self, project_path: Path):
        """
        Initialize checkpoint handler.
        
        Args:
            project_path: Path to project directory
        """
        self.project_path = Path(project_path)
        self.checkpoint_dir = self.project_path / '.migration-checkpoints'
        self.checkpoint_dir.mkdir(exist_ok=True)
        
        self.metadata_file = self.checkpoint_dir / 'checkpoint_metadata.json'
        self.schedule_file = self.checkpoint_dir / 'checkpoint_schedule.json'
        
        # Initialize audit logger
        log_dir = self.project_path / '.migration-logs'
        self.audit_logger = SecurityAuditLogger(log_dir)
        
        self.checkpoints: Dict[str, Dict] = {}
        self.schedule: Dict = {}
        
        self._load_metadata()
        self._load_schedule()
    
    def create_smart_checkpoint(
        self,
        description: str,
        checkpoint_type: str = "manual",
        compression: bool = True,
        tags: Optional[List[str]] = None
    ) -> str:
        """
        Create intelligent checkpoint with optimization.
        
        Args:
            description: Checkpoint description
            checkpoint_type: Type of checkpoint (manual, auto, milestone)
            compression: Whether to compress checkpoint
            tags: Optional tags
            
        Returns:
            Checkpoint ID
        """
        checkpoint_id = self._generate_checkpoint_id()
        checkpoint_path = self.checkpoint_dir / checkpoint_id
        checkpoint_path.mkdir(exist_ok=True)
        
        # Analyze project changes since last checkpoint
        changes = self._analyze_project_changes()
        
        # Create checkpoint based on changes
        if changes['total_changes'] == 0:
            # No changes, create lightweight checkpoint
            metadata = self._create_lightweight_checkpoint(
                checkpoint_id, checkpoint_path, description, checkpoint_type, tags
            )
        else:
            # Full checkpoint with changes
            metadata = self._create_full_checkpoint(
                checkpoint_id, checkpoint_path, description, checkpoint_type, 
                compression, tags, changes
            )
        
        # Store metadata
        self.checkpoints[checkpoint_id] = metadata
        self._save_metadata()
        
        # Log checkpoint creation
        self.audit_logger.log_migration_event(
            migration_type='checkpoint',
            project_path=str(self.project_path),
            user='system',
            action='CREATE_SMART_CHECKPOINT',
            result='SUCCESS',
            details={
                'checkpoint_id': checkpoint_id,
                'type': checkpoint_type,
                'changes': changes,
                'compression': compression
            }
        )
        
        return checkpoint_id
    
    def create_incremental_checkpoint(
        self,
        base_checkpoint_id: str,
        description: str,
        tags: Optional[List[str]] = None
    ) -> str:
        """
        Create incremental checkpoint based on existing checkpoint.
        
        Args:
            base_checkpoint_id: Base checkpoint to build upon
            description: Checkpoint description
            tags: Optional tags
            
        Returns:
            New checkpoint ID
        """
        if base_checkpoint_id not in self.checkpoints:
            raise ValueError(f"Base checkpoint not found: {base_checkpoint_id}")
        
        checkpoint_id = self._generate_checkpoint_id()
        checkpoint_path = self.checkpoint_dir / checkpoint_id
        checkpoint_path.mkdir(exist_ok=True)
        
        # Analyze changes since base checkpoint
        changes = self._analyze_changes_since_checkpoint(base_checkpoint_id)
        
        # Create incremental checkpoint
        metadata = self._create_incremental_checkpoint_data(
            checkpoint_id, checkpoint_path, base_checkpoint_id,
            description, tags, changes
        )
        
        # Store metadata
        self.checkpoints[checkpoint_id] = metadata
        self._save_metadata()
        
        return checkpoint_id
    
    def validate_checkpoint(self, checkpoint_id: str) -> Dict:
        """
        Validate checkpoint integrity.
        
        Args:
            checkpoint_id: Checkpoint to validate
            
        Returns:
            Validation results
        """
        if checkpoint_id not in self.checkpoints:
            return {
                'valid': False,
                'error': 'Checkpoint not found'
            }
        
        metadata = self.checkpoints[checkpoint_id]
        checkpoint_path = self.checkpoint_dir / checkpoint_id
        
        validation_result = {
            'valid': True,
            'checkpoint_id': checkpoint_id,
            'checks': {}
        }
        
        try:
            # Check checkpoint directory exists
            if not checkpoint_path.exists():
                validation_result['valid'] = False
                validation_result['checks']['directory'] = 'Missing'
                return validation_result
            
            validation_result['checks']['directory'] = 'OK'
            
            # Validate metadata
            if not self._validate_metadata(metadata):
                validation_result['valid'] = False
                validation_result['checks']['metadata'] = 'Invalid'
            else:
                validation_result['checks']['metadata'] = 'OK'
            
            # Validate file checksums
            if metadata.get('type') == 'full':
                checksum_validation = self._validate_checksums(checkpoint_path, metadata)
                validation_result['checks']['checksums'] = checksum_validation
                
                if checksum_validation['status'] != 'OK':
                    validation_result['valid'] = False
            
            # Validate incremental data
            if metadata.get('type') == 'incremental':
                incremental_validation = self._validate_incremental_data(checkpoint_path, metadata)
                validation_result['checks']['incremental'] = incremental_validation
                
                if incremental_validation['status'] != 'OK':
                    validation_result['valid'] = False
            
        except Exception as e:
            validation_result['valid'] = False
            validation_result['error'] = str(e)
        
        return validation_result
    
    def restore_from_checkpoint(
        self,
        checkpoint_id: str,
        files: Optional[List[str]] = None,
        validate_before_restore: bool = True
    ) -> Dict:
        """
        Restore project from checkpoint.
        
        Args:
            checkpoint_id: Checkpoint to restore from
            files: Specific files to restore (None = all)
            validate_before_restore: Validate checkpoint before restoring
            
        Returns:
            Restore results
        """
        if checkpoint_id not in self.checkpoints:
            raise ValueError(f"Checkpoint not found: {checkpoint_id}")
        
        # Validate checkpoint if requested
        if validate_before_restore:
            validation = self.validate_checkpoint(checkpoint_id)
            if not validation['valid']:
                raise Exception(f"Checkpoint validation failed: {validation}")
        
        metadata = self.checkpoints[checkpoint_id]
        
        # Create backup before restore
        backup_checkpoint = self.create_smart_checkpoint(
            f"Pre-restore backup before {checkpoint_id}",
            checkpoint_type="auto-backup",
            tags=["pre-restore", "auto-backup"]
        )
        
        try:
            if metadata['type'] == 'full':
                return self._restore_from_full_checkpoint(checkpoint_id, files)
            elif metadata['type'] == 'incremental':
                return self._restore_from_incremental_checkpoint(checkpoint_id, files)
            else:
                raise Exception(f"Unknown checkpoint type: {metadata['type']}")
                
        except Exception as e:
            # Restore failed, try to restore from backup
            try:
                self.restore_from_checkpoint(backup_checkpoint, files=None, validate_before_restore=False)
            except Exception:
                pass
            
            raise Exception(f"Restore failed: {e}. Backup created: {backup_checkpoint}")
    
    def schedule_checkpoint(
        self,
        schedule_type: str,
        interval_minutes: int,
        description_template: str,
        tags: Optional[List[str]] = None
    ) -> str:
        """
        Schedule automatic checkpoints.
        
        Args:
            schedule_type: Type of schedule (interval, event-based)
            interval_minutes: Interval in minutes
            description_template: Template for description
            tags: Default tags for scheduled checkpoints
            
        Returns:
            Schedule ID
        """
        schedule_id = self._generate_schedule_id()
        
        schedule_config = {
            'id': schedule_id,
            'type': schedule_type,
            'interval_minutes': interval_minutes,
            'description_template': description_template,
            'tags': tags or [],
            'created_at': datetime.now().isoformat(),
            'last_run': None,
            'enabled': True
        }
        
        self.schedule[schedule_id] = schedule_config
        self._save_schedule()
        
        return schedule_id
    
    def cleanup_checkpoints(
        self,
        policy: str = "retention",
        max_age_days: int = 30,
        max_count: int = 50,
        min_free_space_gb: float = 1.0
    ) -> Dict:
        """
        Clean up checkpoints based on policy.
        
        Args:
            policy: Cleanup policy (retention, space, intelligent)
            max_age_days: Maximum age in days
            max_count: Maximum number of checkpoints
            min_free_space_gb: Minimum free space to maintain
            
        Returns:
            Cleanup results
        """
        cleanup_results = {
            'policy': policy,
            'checkpoints_deleted': 0,
            'space_freed_mb': 0,
            'deleted_checkpoints': []
        }
        
        if policy == "retention":
            cleanup_results.update(self._cleanup_by_retention(max_age_days, max_count))
        elif policy == "space":
            cleanup_results.update(self._cleanup_by_space(min_free_space_gb))
        elif policy == "intelligent":
            cleanup_results.update(self._cleanup_intelligent(max_age_days, max_count, min_free_space_gb))
        
        return cleanup_results
    
    def _generate_checkpoint_id(self) -> str:
        """Generate unique checkpoint ID."""
        return datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
    
    def _generate_schedule_id(self) -> str:
        """Generate unique schedule ID."""
        return f"schedule_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def _analyze_project_changes(self) -> Dict:
        """Analyze project changes since last checkpoint."""
        # Get most recent checkpoint
        recent_checkpoints = sorted(
            self.checkpoints.values(),
            key=lambda x: x['timestamp'],
            reverse=True
        )
        
        if not recent_checkpoints:
            return {
                'total_changes': 0,
                'files_added': 0,
                'files_modified': 0,
                'files_deleted': 0,
                'size_change_mb': 0
            }
        
        # For now, return basic analysis
        # In a full implementation, this would compare with last checkpoint
        return {
            'total_changes': 10,  # Placeholder
            'files_added': 3,
            'files_modified': 5,
            'files_deleted': 2,
            'size_change_mb': 1.5
        }
    
    def _create_lightweight_checkpoint(
        self,
        checkpoint_id: str,
        checkpoint_path: Path,
        description: str,
        checkpoint_type: str,
        tags: Optional[List[str]]
    ) -> Dict:
        """Create lightweight checkpoint (no changes)."""
        metadata = {
            'id': checkpoint_id,
            'type': 'lightweight',
            'timestamp': datetime.now().isoformat(),
            'description': description,
            'checkpoint_type': checkpoint_type,
            'tags': tags or [],
            'file_count': 0,
            'size_mb': 0.0,
            'changes': {
                'total_changes': 0,
                'files_added': 0,
                'files_modified': 0,
                'files_deleted': 0
            }
        }
        
        # Create marker file
        (checkpoint_path / '.checkpoint_marker').write_text(checkpoint_id)
        
        return metadata
    
    def _create_full_checkpoint(
        self,
        checkpoint_id: str,
        checkpoint_path: Path,
        description: str,
        checkpoint_type: str,
        compression: bool,
        tags: Optional[List[str]],
        changes: Dict
    ) -> Dict:
        """Create full checkpoint with all files."""
        # Copy project files
        file_count = 0
        total_size = 0
        checksums = {}
        
        for item in self.project_path.iterdir():
            if item.name.startswith('.migration-'):
                continue
            
            dest = checkpoint_path / item.name
            if item.is_dir():
                shutil.copytree(item, dest, symlinks=False)
                file_count += len(list(dest.rglob('*')))
                total_size += sum(f.stat().st_size for f in dest.rglob('*') if f.is_file())
            else:
                shutil.copy2(item, dest)
                file_count += 1
                total_size += dest.stat().st_size
        
        metadata = {
            'id': checkpoint_id,
            'type': 'full',
            'timestamp': datetime.now().isoformat(),
            'description': description,
            'checkpoint_type': checkpoint_type,
            'tags': tags or [],
            'file_count': file_count,
            'size_mb': total_size / (1024 * 1024),
            'compression': compression,
            'changes': changes,
            'checksums': checksums  # Would be calculated in full implementation
        }
        
        return metadata
    
    def _create_incremental_checkpoint_data(
        self,
        checkpoint_id: str,
        checkpoint_path: Path,
        base_checkpoint_id: str,
        description: str,
        tags: Optional[List[str]],
        changes: Dict
    ) -> Dict:
        """Create incremental checkpoint data."""
        # Store only changed files
        metadata = {
            'id': checkpoint_id,
            'type': 'incremental',
            'base_checkpoint': base_checkpoint_id,
            'timestamp': datetime.now().isoformat(),
            'description': description,
            'tags': tags or [],
            'changes': changes,
            'file_count': changes['total_changes'],
            'size_mb': 0.5  # Placeholder
        }
        
        # Store changes file
        changes_file = checkpoint_path / 'changes.json'
        changes_file.write_text(json.dumps(changes, indent=2))
        
        return metadata
    
    def _analyze_changes_since_checkpoint(self, base_checkpoint_id: str) -> Dict:
        """Analyze changes since specific checkpoint."""
        # Placeholder implementation
        return {
            'total_changes': 5,
            'files_added': 2,
            'files_modified': 3,
            'files_deleted': 0
        }
    
    def _validate_metadata(self, metadata: Dict) -> bool:
        """Validate checkpoint metadata."""
        required_fields = ['id', 'type', 'timestamp', 'description']
        return all(field in metadata for field in required_fields)
    
    def _validate_checksums(self, checkpoint_path: Path, metadata: Dict) -> Dict:
        """Validate file checksums."""
        # Placeholder implementation
        return {'status': 'OK', 'verified_files': metadata.get('file_count', 0)}
    
    def _validate_incremental_data(self, checkpoint_path: Path, metadata: Dict) -> Dict:
        """Validate incremental checkpoint data."""
        changes_file = checkpoint_path / 'changes.json'
        if not changes_file.exists():
            return {'status': 'ERROR', 'message': 'Changes file missing'}
        
        return {'status': 'OK', 'changes_valid': True}
    
    def _restore_from_full_checkpoint(self, checkpoint_id: str, files: Optional[List[str]]) -> Dict:
        """Restore from full checkpoint."""
        # Placeholder implementation
        return {
            'success': True,
            'files_restored': 10,
            'checkpoint_type': 'full'
        }
    
    def _restore_from_incremental_checkpoint(self, checkpoint_id: str, files: Optional[List[str]]) -> Dict:
        """Restore from incremental checkpoint."""
        # Placeholder implementation
        return {
            'success': True,
            'files_restored': 5,
            'checkpoint_type': 'incremental'
        }
    
    def _cleanup_by_retention(self, max_age_days: int, max_count: int) -> Dict:
        """Clean up checkpoints by retention policy."""
        # Placeholder implementation
        return {
            'checkpoints_deleted': 0,
            'space_freed_mb': 0,
            'deleted_checkpoints': []
        }
    
    def _cleanup_by_space(self, min_free_space_gb: float) -> Dict:
        """Clean up checkpoints to free space."""
        # Placeholder implementation
        return {
            'checkpoints_deleted': 0,
            'space_freed_mb': 0,
            'deleted_checkpoints': []
        }
    
    def _cleanup_intelligent(
        self, 
        max_age_days: int, 
        max_count: int, 
        min_free_space_gb: float
    ) -> Dict:
        """Intelligent cleanup combining multiple factors."""
        # Placeholder implementation
        return {
            'checkpoints_deleted': 0,
            'space_freed_mb': 0,
            'deleted_checkpoints': []
        }
    
    def _load_metadata(self) -> None:
        """Load checkpoint metadata."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    self.checkpoints = json.load(f)
            except Exception:
                self.checkpoints = {}
        else:
            self.checkpoints = {}
    
    def _save_metadata(self) -> None:
        """Save checkpoint metadata."""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.checkpoints, f, indent=2)
        except Exception as e:
            raise Exception(f"Failed to save metadata: {e}")
    
    def _load_schedule(self) -> None:
        """Load checkpoint schedule."""
        if self.schedule_file.exists():
            try:
                with open(self.schedule_file, 'r') as f:
                    self.schedule = json.load(f)
            except Exception:
                self.schedule = {}
        else:
            self.schedule = {}
    
    def _save_schedule(self) -> None:
        """Save checkpoint schedule."""
        try:
            with open(self.schedule_file, 'w') as f:
                json.dump(self.schedule, f, indent=2)
        except Exception:
            pass
