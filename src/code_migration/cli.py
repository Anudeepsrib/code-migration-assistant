import typer
import sys
import os
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from code_migration.migrators.react_hooks import ReactHooksMigrator
from code_migration.utils.file_handler import safe_read_file, safe_write_file, SecurityError
from code_migration.utils.sanitizer import validate_path
from code_migration.utils.logger import setup_logger

app = typer.Typer()
console = Console()

# Register migrators (Simple registry for now)
MIGRATORS = {
    "react-hooks": ReactHooksMigrator()
}

@app.command()
def analyze(
    path: str = typer.Argument(..., help="Path to file or directory"),
    type: str = typer.Option(..., help="Migration type (e.g., react-hooks)")
):
    """
    Analyze a codebase for potential migrations.
    """
    if type not in MIGRATORS:
        console.print(f"[bold red]Error:[/bold red] Unknown migration type: {type}")
        raise typer.Exit(code=1)

    migrator = MIGRATORS[type]
    console.print(Panel(f"Analyzing [bold]{path}[/bold] for [cyan]{type}[/cyan]", title="Code Migration Assistant"))

    try:
        target_path = validate_path(path)
    except SecurityError as e:
        console.print(f"[bold red]Security Error:[/bold red] {e}")
        raise typer.Exit(code=1)

    files_found = 0
    if target_path.is_file():
        files = [target_path]
    else:
        files = list(target_path.rglob("*"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task(description="Scanning files...", total=None)
        
        candidates = []
        for file in files:
            if file.is_file() and migrator.can_migrate(file):
                candidates.append(file)
                files_found += 1

    console.print(f"[green]Found {files_found} candidate files for migration.[/green]")
    for f in candidates:
        console.print(f"  - {f}")

@app.command()
def run(
    path: str = typer.Argument(..., help="Path to file or directory"),
    type: str = typer.Option(..., help="Migration type"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview changes without applying"),
    verbose: bool = typer.Option(False, "--verbose", help="Enable verbose logging")
):
    """
    Execute the migration.
    """
    logger = setup_logger(verbose=verbose)
    
    if type not in MIGRATORS:
        console.print(f"[bold red]Error:[/bold red] Unknown migration type: {type}")
        raise typer.Exit(code=1)

    migrator = MIGRATORS[type]
    
    try:
        target_path = validate_path(path)
    except SecurityError as e:
        console.print(f"[bold red]Security Error:[/bold red] {e}")
        raise typer.Exit(code=1)

    if target_path.is_file():
        files = [target_path]
    else:
        files = list(target_path.rglob("*"))

    files_to_process = [f for f in files if f.is_file() and migrator.can_migrate(f)]
    
    if not files_to_process:
        console.print("[yellow]No matching files found.[/yellow]")
        return

    with Progress() as progress:
        task = progress.add_task("[cyan]Migrating...", total=len(files_to_process))
        
        for file_path in files_to_process:
            try:
                content = safe_read_file(str(file_path))
                new_content = migrator.migrate(content, file_path)
                
                if content != new_content:
                    if dry_run:
                        console.print(f"[blue][Dry Run][/blue] Would migrate: {file_path}")
                        # Could print diff here
                    else:
                        safe_write_file(str(file_path), new_content)
                        console.print(f"[green]Migrated:[/green] {file_path}")
                
            except Exception as e:
                console.print(f"[red]Failed to migrate {file_path}: {e}[/red]")
            
            progress.advance(task)

    console.print(Panel("Migration Complete!", style="bold green"))

if __name__ == "__main__":
    app()
