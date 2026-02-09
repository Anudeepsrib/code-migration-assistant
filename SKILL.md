---
name: code-migration
description: |
  Intelligent code migration assistant for framework upgrades, language 
  conversions, and modernization. Trigger when user mentions: migrate, 
  upgrade, convert, modernize, refactor, transform, or asks about moving 
  from one technology to another.
version: 1.0.0
author: Open Source Contributor
license: Apache-2.0
---

# Code Migration Assistant

## When to Use This Skill

Activate when the user wants to:
- Migrate React class components to hooks
- Upgrade frameworks (Vue 2->3, Python 2->3)
- Modernize legacy codebases
- Refactor code patterns

## How to Use

1.  **Analyze**: First, analyze the codebase to understand the scope.
    - Use `migrate analyze <path> --type <type>`
    - Identify potential breaking changes and dependencies.

2.  **Plan**: Propose a migration plan to the user.
    - List affected files.
    - Explain the strategy.

3.  **Execute**: Run the migration tool.
    - Use `migrate run <path> --type <type>`
    - ALWAYS suggest `--dry-run` first for verification.
    - Confirm with the user before applying changes.

## Supported Migrations

- `react-hooks`: Converts React Class components to Functional components.
  - Handles `this.props`, formatting.
  - *Note*: State and Lifecycle methods may require manual review (marked with TODOs).

## Security & Safety

- **Backups**: The tool automatically creates backups in `.migration-backups/` before any write.
- **Validation**: All paths are sanitized to prevent directory traversal.
- **Atomic Writes**: Writes are atomic to prevent data corruption.

## Error Handling

If a migration fails:
1.  Check the logs.
2.  Restore from backup if necessary.
3.  Report the issue using the `analyze` command details.
