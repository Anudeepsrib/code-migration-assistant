# Contributing to Code Migration Assistant

We welcome contributions! This guide will help you add new migration types.

## Adding a New Migrator

1.  **Create a new file** in `scripts/migrators/` (e.g., `vue3_migrator.py`).
2.  **Inherit from `BaseMigrator`**:
    ```python
    from .base_migrator import BaseMigrator
    
    class Vue3Migrator(BaseMigrator):
        @property
        def name(self): return "vue3"
        
        def can_migrate(self, path): ...
        def migrate(self, content, path): ...
    ```
3.  **Register the migrator** in `scripts/migrate.py`:
    ```python
    MIGRATORS = {
        "react-hooks": ReactHooksMigrator(),
        "vue3": Vue3Migrator() # Add yours here
    }
    ```
4.  **Add Tests**: Create a test file in `tests/` verifying your logic.

## Testing

Run the test suite to ensure no regressions:

```bash
pytest tests/
```

## Code Style

- Use `black` for formatting.
- Ensure type hints are used.
