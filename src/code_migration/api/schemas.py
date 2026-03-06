from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ErrorDetails(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    error: ErrorDetails


class HealthResponse(BaseModel):
    status: str
    migrators: List[str]


class AnalyzeRequest(BaseModel):
    path: str = Field(..., description="Absolute path to the file or project directory")
    migration_type: str = Field(default="react-hooks", description="Migration type identifier")


class MigrateRequest(AnalyzeRequest):
    dry_run: bool = Field(default=True, description="If True, preview changes without writing to disk")


class MigrateResultItem(BaseModel):
    file: str
    changed: bool = False
    applied: bool = False
    error: Optional[str] = None


class MigrateResponse(BaseModel):
    migration_type: str
    dry_run: bool
    total_candidates: int
    results: List[MigrateResultItem]


class ComplianceScanRequest(BaseModel):
    path: str = Field(..., description="Absolute path to the project directory")


class PluginInfoSchema(BaseModel):
    name: str
    description: str
    version: str
    supported_extensions: List[str]
    tags: List[str]
    source: str
