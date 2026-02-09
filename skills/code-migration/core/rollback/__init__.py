"""
Time Machine rollback module.

Provides Git-based rollback with surgical precision:
- Automatic checkpoints before changes
- One-command rollback
- Partial rollback (selected files only)
- History browser
- Integrity verification
"""

from .snapshot_manager import TimeMachineRollback
from .checkpoint_handler import CheckpointHandler
from .partial_rollback import PartialRollbackManager

__all__ = [
    'TimeMachineRollback',
    'CheckpointHandler',
    'PartialRollbackManager'
]
