from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any

class MigrationResult:
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.changes: List[str] = []
        self.success = False
        self.error: str = None
        self.diff: str = None

class BaseMigrator(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the migrator (e.g., 'react-hooks')."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Description of what the migrator does."""
        pass

    @abstractmethod
    def can_migrate(self, file_path: Path) -> bool:
        """Check if this migrator can handle the file."""
        pass

    @abstractmethod
    def migrate(self, content: str, file_path: Path) -> str:
        """
        Perform the migration.
        Returns the new content.
        Raises exception on failure.
        """
        pass
