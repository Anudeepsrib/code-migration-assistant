"""
Unified Configuration System for Code Migration Assistant.

Loads configuration in the following order (last wins):
1. Default values defined in Pydantic models
2. YAML configuration file (`config/defaults.yaml` or via `MIGRATION_CONFIG_FILE`)
3. Environment variables (prefix: `MIGRATION_`)

Usage:
    from code_migration.config import settings

    if settings.security.level == "high":
        ...
"""

import os
from pathlib import Path
from typing import Dict, List, Optional

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SecuritySettings(BaseSettings):
    level: str = Field(default="high", description="Security mode: high, medium, low")
    audit_logging: bool = Field(default=True, description="Enable audit trail")
    max_file_size_kb: int = Field(default=5000, description="Max file size for analysis")
    rate_limit_per_minute: int = Field(default=60, description="API rate limit")


class AnalysisSettings(BaseSettings):
    confidence_weights: Dict[str, float] = Field(
        default={
            "complexity": 0.25,
            "test_coverage": 0.25,
            "dependency_health": 0.25,
            "breaking_changes": 0.25,
        }
    )
    cost_rate_per_hour: float = Field(default=100.0, description="Hourly rate for estimates")
    max_workers: int = Field(default=4, description="Concurrent analysis workers")
    timeout_seconds: int = Field(default=300, description="Operation timeout")


class ServerSettings(BaseSettings):
    host: str = Field(default="127.0.0.1")
    port: int = Field(default=8000)
    cors_origins: List[str] = Field(default=["*"])


class ObservabilitySettings(BaseSettings):
    log_level: str = Field(default="INFO", description="DEBUG, INFO, WARNING, ERROR, CRITICAL")
    log_format: str = Field(default="text", description="text or json")


def _load_yaml_config(file_path: Optional[str]) -> dict:
    """Load configuration from a YAML file if it exists."""
    if not file_path:
        # Default fallback locations
        locations = [
            Path("config/defaults.yaml"),
            Path("config.defaults.yaml"),
            Path(os.path.dirname(__file__)).parent.parent / "config.defaults.yaml"
        ]
        for loc in locations:
            if loc.exists():
                file_path = str(loc)
                break

    if not file_path or not Path(file_path).exists():
        return {}

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data or {}
    except Exception as e:
        # Logging might not be initialized yet, print to stderr
        import sys
        print(f"Warning: Failed to load config file {file_path}: {e}", file=sys.stderr)
        return {}


class MigrationSettings(BaseSettings):
    """Main configuration model combining all sub-settings."""

    security: SecuritySettings = Field(default_factory=SecuritySettings)
    analysis: AnalysisSettings = Field(default_factory=AnalysisSettings)
    server: ServerSettings = Field(default_factory=ServerSettings)
    observability: ObservabilitySettings = Field(default_factory=ObservabilitySettings)

    model_config = SettingsConfigDict(
        env_prefix="MIGRATION_",
        env_nested_delimiter="__",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @classmethod
    def load(cls) -> "MigrationSettings":
        """Load settings taking YAML files into account before parsing env vars."""
        # Check standard env var for config file path
        config_file = os.environ.get("MIGRATION_CONFIG_FILE")
        yaml_data = _load_yaml_config(config_file)
        
        # Pydantic will merge yaml_data with default fields, then 
        # override with environment variables (due to SettingsConfigDict)
        return cls(**yaml_data)


# Global settings instance
settings = MigrationSettings.load()
