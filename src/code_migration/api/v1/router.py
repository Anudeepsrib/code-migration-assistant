import asyncio
from typing import List
from pathlib import Path

from fastapi import APIRouter, Depends, Request
from sse_starlette.sse import EventSourceResponse

from code_migration.api.deps import get_registry
from code_migration.api.schemas import PluginInfoSchema
from code_migration.registry import MigratorRegistry
from code_migration.core.security.input_validator import SecurityError
from code_migration.utils.file_handler import safe_read_file, safe_write_file
from code_migration.utils.sanitizer import validate_path

router = APIRouter()

@router.get("/migrators", response_model=List[PluginInfoSchema])
async def list_migrators(registry: MigratorRegistry = Depends(get_registry)):
    """List all available migration plugins."""
    return registry.list_all()

@router.get("/analyze")
async def analyze(
    path: str,
    type: str = "react-hooks",
    request: Request = None,
    registry: MigratorRegistry = Depends(get_registry)
):
    """Streaming endpoint for analyzing a migration plan."""

    async def event_generator():
        migrator = registry.get(type)
        if not migrator:
            yield {"data": f"Error: Unknown migration type: {type}"}
            return

        yield {"data": f"Analyzing {path} for {type}..."}
        
        try:
            target_path = validate_path(path)
        except SecurityError as e:
            yield {"data": f"Security Error: {e}"}
            return

        files_found = 0
        if target_path.is_file():
            files = [target_path]
        else:
            files = list(target_path.rglob("*"))

        yield {"data": "Scanning files..."}
        
        candidates = []
        for file in files:
            await asyncio.sleep(0.001)  # Context switch for UI responsiveness
            if file.is_file() and migrator.can_migrate(file):
                candidates.append(file)
                files_found += 1
                yield {"data": f"Found candidate: {file}"}

        yield {"data": f"Scan Complete. Found {files_found} candidate files for migration."}
        yield {"data": "DONE"}

    return EventSourceResponse(event_generator())


@router.get("/run")
async def run_migration(
    path: str,
    type: str = "react-hooks",
    dry_run: str = "false",
    request: Request = None,
    registry: MigratorRegistry = Depends(get_registry)
):
    """Streaming endpoint to execute a migration."""
    is_dry_run = dry_run.lower() == "true"

    async def event_generator():
        migrator = registry.get(type)
        if not migrator:
            yield {"data": f"Error: Unknown migration type: {type}"}
            return

        yield {"data": f"Starting migration on {path} with type {type}..."}
        
        try:
            target_path = validate_path(path)
        except SecurityError as e:
            yield {"data": f"Security Error: {e}"}
            return

        if target_path.is_file():
            files = [target_path]
        else:
            files = list(target_path.rglob("*"))

        yield {"data": "Identifying candidate files..."}
        files_to_process = [f for f in files if f.is_file() and migrator.can_migrate(f)]
        
        if not files_to_process:
            yield {"data": "No matching files found."}
            yield {"data": "DONE"}
            return

        yield {"data": f"Found {len(files_to_process)} files to process."}

        for file_path in files_to_process:
            await asyncio.sleep(0.01)  # Context switch
            try:
                content = safe_read_file(str(file_path))
                new_content = migrator.migrate(content, file_path)
                
                if content != new_content:
                    if is_dry_run:
                        yield {"data": f"[Dry Run] Would migrate: {file_path}"}
                    else:
                        safe_write_file(str(file_path), new_content)
                        yield {"data": f"Migrated: {file_path}"}
                else:
                    yield {"data": f"No changes needed: {file_path}"}
                
            except Exception as e:
                yield {"data": f"Failed to migrate {file_path}: {e}"}
            
        yield {"data": "Migration Complete!"}
        yield {"data": "DONE"}

    return EventSourceResponse(event_generator())
