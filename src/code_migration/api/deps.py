from typing import Generator
from fastapi import Depends
from code_migration.registry import MigratorRegistry, create_registry

# Global registry instance to avoid reloading entry_points on every request
_registry = create_registry()

def get_registry() -> MigratorRegistry:
    """Dependency injection for the central plugin registry."""
    return _registry
