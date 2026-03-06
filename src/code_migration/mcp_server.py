"""
MCP (Model Context Protocol) server for Code Migration Assistant.

Exposes core migration tools over stdio transport so that AI applications
(Claude Desktop, VS Code Copilot, Cursor, etc.) can invoke them directly.

Usage:
    python -m code_migration.mcp_server          # stdio transport (default)
    code-migration-mcp                            # via installed entry point
"""

import json
import traceback
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Server instance
# ---------------------------------------------------------------------------

mcp = FastMCP(
    "Code Migration Assistant",
    instructions=(
        "Enterprise-grade code migration assistant with AI-powered risk "
        "assessment, visual dependency planning, surgical rollback, and "
        "regulatory compliance scanning."
    ),
)

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _resolve_path(path: str) -> Path:
    """Resolve and validate a user-supplied path."""
    p = Path(path).resolve()
    if not p.exists():
        raise FileNotFoundError(f"Path does not exist: {p}")
    return p


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@mcp.tool()
def analyze(
    path: str,
    migration_type: str = "react-hooks",
    team_experience: int = 50,
) -> str:
    """Analyze a codebase and calculate migration confidence score.

    Evaluates complexity, test coverage, dependency health, and breaking
    changes to produce a risk-level assessment (LOW → CRITICAL) with
    cost/time estimates.

    Args:
        path: Absolute path to the project directory.
        migration_type: One of react-hooks, vue3, python3, typescript,
                        graphql, angular, svelte.
        team_experience: Team experience level from 0 to 100.
    """
    from code_migration.core.confidence import MigrationConfidenceAnalyzer

    project = _resolve_path(path)

    with MigrationConfidenceAnalyzer(project, allowed_base=project) as analyzer:
        score = analyzer.calculate_confidence(
            migration_type=migration_type,
            team_experience=team_experience,
        )

    return json.dumps(
        {
            "overall_score": score.overall_score,
            "risk_level": score.risk_level,
            "migration_complexity": score.migration_complexity,
            "estimated_hours": score.estimated_hours,
            "estimated_cost": score.estimated_cost,
            "factors": score.factors,
            "blockers": score.blockers,
            "warnings": score.warnings,
            "recommendations": score.recommendations,
        },
        indent=2,
        default=str,
    )


@mcp.tool()
def list_migrators() -> str:
    """List all available migration plugins.

    Returns metadata for every registered migrator including name,
    description, version, supported file extensions, and tags.
    """
    from code_migration.registry import create_registry

    registry = create_registry()
    return json.dumps(
        [
            {
                "name": info.name,
                "description": info.description,
                "version": info.version,
                "supported_extensions": info.supported_extensions,
                "tags": info.tags,
                "source": info.source,
            }
            for info in registry.list_all()
        ],
        indent=2,
    )


@mcp.tool()
def run_migration(
    path: str,
    migration_type: str = "react-hooks",
    dry_run: bool = True,
) -> str:
    """Execute a code migration on the target project.

    Identifies candidate files and applies AST-based rewrites.
    Defaults to **dry-run mode** so changes are previewed, not applied.

    Args:
        path: Absolute path to the file or project directory.
        migration_type: Migration type identifier (e.g. react-hooks).
        dry_run: If True, preview changes without writing to disk.
    """
    from code_migration.registry import create_registry
    from code_migration.utils.file_handler import safe_read_file, safe_write_file
    from code_migration.utils.sanitizer import validate_path

    target = validate_path(path)

    registry = create_registry()
    migrator = registry.get(migration_type)

    if migrator is None:
        available = registry.names()
        return json.dumps({
            "error": f"Unknown migration type: {migration_type}",
            "available_types": available,
        })

    files = [target] if target.is_file() else list(target.rglob("*"))
    candidates = [f for f in files if f.is_file() and migrator.can_migrate(f)]

    results = []
    for fp in candidates:
        try:
            content = safe_read_file(str(fp))
            new_content = migrator.migrate(content, fp)
            changed = content != new_content

            if changed and not dry_run:
                safe_write_file(str(fp), new_content)

            results.append(
                {
                    "file": str(fp),
                    "changed": changed,
                    "applied": changed and not dry_run,
                }
            )
        except Exception as exc:
            results.append({"file": str(fp), "error": str(exc)})

    return json.dumps(
        {
            "migration_type": migration_type,
            "dry_run": dry_run,
            "total_candidates": len(candidates),
            "results": results,
        },
        indent=2,
        default=str,
    )


@mcp.tool()
def compliance_scan(path: str) -> str:
    """Scan a project for PII/PHI regulatory violations.

    Detects sensitive data patterns (emails, SSNs, credit cards, medical
    records, etc.) and maps findings to GDPR, HIPAA, and PCI-DSS
    regulations.

    Args:
        path: Absolute path to the project directory.
    """
    from code_migration.core.compliance import PIIDetector

    project = _resolve_path(path)

    with PIIDetector(project) as detector:
        findings = detector.scan_directory()
        report = detector.generate_compliance_report()

    return json.dumps(
        {
            "total_findings": len(findings),
            "findings": findings[:50],  # cap to avoid huge payloads
            "report": report,
        },
        indent=2,
        default=str,
    )


@mcp.tool()
def visualize(path: str) -> str:
    """Generate a dependency graph and migration-wave plan.

    Builds an interactive graph of file-level import dependencies and
    computes topologically-sorted migration waves so that dependencies
    are migrated before dependents.

    Args:
        path: Absolute path to the project directory.
    """
    from code_migration.core.visualizer import VisualMigrationPlanner

    project = _resolve_path(path)

    planner = VisualMigrationPlanner(project, allowed_base=project)
    planner.build_dependency_graph()
    waves = planner.calculate_migration_waves()

    graph_data = {
        "nodes": [
            {"id": n, **planner.graph.nodes[n]}
            for n in planner.graph.nodes()
        ],
        "edges": [
            {"source": u, "target": v, **d}
            for u, v, d in planner.graph.edges(data=True)
        ],
    }

    return json.dumps(
        {
            "total_nodes": planner.graph.number_of_nodes(),
            "total_edges": planner.graph.number_of_edges(),
            "migration_waves": waves,
            "graph": graph_data,
        },
        indent=2,
        default=str,
    )


@mcp.tool()
def rollback(
    path: str,
    checkpoint_id: Optional[str] = None,
    description: str = "MCP-triggered checkpoint",
) -> str:
    """Create or restore a rollback checkpoint.

    If *checkpoint_id* is provided, the project is restored to that
    snapshot.  Otherwise a **new checkpoint** is created with the given
    description.

    Args:
        path: Absolute path to the project directory.
        checkpoint_id: ID of an existing checkpoint to restore (omit to
                       create a new one).
        description: Description for a newly created checkpoint.
    """
    from code_migration.core.rollback import TimeMachineRollback

    project = _resolve_path(path)

    with TimeMachineRollback(project, allowed_base=project) as tm:
        if checkpoint_id:
            result = tm.rollback_to_checkpoint(checkpoint_id)
            return json.dumps(
                {"action": "rollback", "checkpoint_id": checkpoint_id, "result": result},
                indent=2,
                default=str,
            )
        else:
            new_id = tm.create_checkpoint(description)
            return json.dumps(
                {"action": "create_checkpoint", "checkpoint_id": new_id, "description": description},
                indent=2,
                default=str,
            )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    """Run the MCP server with stdio transport."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
