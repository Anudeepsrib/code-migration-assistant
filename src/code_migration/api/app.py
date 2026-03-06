from pathlib import Path
from fastapi import FastAPI, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from code_migration.config import settings
from code_migration.api.errors import (
    APIError, api_error_handler,
    SecurityError, security_error_handler,
    global_exception_handler
)
from code_migration.api.auth import verify_api_key
from code_migration.api.v1.router import router as v1_router
from code_migration.api.deps import get_registry

def create_app() -> FastAPI:
    """Factory function to create the FastAPI application."""
    
    app = FastAPI(
        title="Code Migration Assistant API",
        version="1.0.0",
        description="Enterprise Code Migration API with Plugin Support"
    )

    # Add Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.server.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register Exception Handlers
    app.add_exception_handler(APIError, api_error_handler)
    app.add_exception_handler(SecurityError, security_error_handler)
    app.add_exception_handler(Exception, global_exception_handler)

    # Include V1 API Router with Authentication Dependency
    app.include_router(
        v1_router,
        prefix="/api/v1",
        tags=["V1 API"],
        dependencies=[Depends(verify_api_key)]
    )

    # Add general health check without auth
    @app.get("/healthz", tags=["System"])
    async def healthz(registry = Depends(get_registry)):
        """Health check endpoint for load balancers."""
        return {"status": "ok", "migrators": registry.names()}

    # Also map the old /api endpoints temporarily if needed for UI compatibility
    # But for a proper hard-cutover as requested, we only mount /api/v1
    # We will mount the static UI at the root
    
    static_dir = Path(__file__).parent.parent.parent.parent / "ui" / "dist"
    if static_dir.exists():
        app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
    else:
        @app.get("/")
        async def index():
            return HTMLResponse("UI Not Built. Run 'npm install && npm run build' in the /ui directory.")

    return app

# The instance uvicorn looks for
app = create_app()
