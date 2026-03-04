import os
import asyncio
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

from code_migration.migrators.react_hooks import ReactHooksMigrator
from code_migration.utils.file_handler import safe_read_file, safe_write_file, SecurityError
from code_migration.utils.sanitizer import validate_path
import uvicorn

app = FastAPI(title="Code Migration Assistant API")

# Allow CORS for development (Vite dev server)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MIGRATORS = {
    "react-hooks": ReactHooksMigrator()
}

@app.get("/api/analyze")
async def analyze(path: str, type: str = "react-hooks", request: Request = None):
    async def event_generator():
        if type not in MIGRATORS:
            yield {"data": f"Error: Unknown migration type: {type}"}
            return

        migrator = MIGRATORS[type]
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
            # Let the event loop breathe for UI responsiveness during large scans
            await asyncio.sleep(0.001) 
            if file.is_file() and migrator.can_migrate(file):
                candidates.append(file)
                files_found += 1
                yield {"data": f"Found candidate: {file}"}

        yield {"data": f"Scan Complete. Found {files_found} candidate files for migration."}
        yield {"data": "DONE"}

    return EventSourceResponse(event_generator())


@app.get("/api/run")
async def run_migration(path: str, type: str = "react-hooks", dry_run: str = "false", request: Request = None):
    is_dry_run = dry_run.lower() == "true"
    async def event_generator():
        if type not in MIGRATORS:
            yield {"data": f"Error: Unknown migration type: {type}"}
            return

        migrator = MIGRATORS[type]
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
            await asyncio.sleep(0.01) # UI responsiveness
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


# Serve React app
# We will serve the dist folder built by Vite.
STATIC_DIR = Path(__file__).parent.parent.parent / "ui" / "dist"
if STATIC_DIR.exists():
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
else:
    @app.get("/")
    async def index():
        return HTMLResponse("UI Not Built. Run 'npm install && npm run build' in the /ui directory.")

if __name__ == "__main__":
    uvicorn.run("code_migration.web:app", host="0.0.0.0", port=8000, reload=True)
