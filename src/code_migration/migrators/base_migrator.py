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
    """Base class for all migration plugins.

    Subclasses must implement ``name``, ``description``, ``can_migrate``,
    and ``migrate``.  The optional properties ``version``,
    ``supported_extensions``, and ``tags`` improve discoverability in the
    plugin registry and marketplace.
    """

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

    @property
    def version(self) -> str:
        """Semantic version of this migrator plugin."""
        return "0.1.0"

    @property
    def supported_extensions(self) -> List[str]:
        """File extensions this migrator can handle (e.g. ['.jsx', '.tsx'])."""
        return []

    @property
    def tags(self) -> List[str]:
        """Searchable tags for marketplace discovery."""
        return []

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

    def validate(self) -> bool:
        """Self-test hook called on plugin load. Return True if healthy."""
        return True

