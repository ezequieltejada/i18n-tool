# PRD — i18n CLI Tool

## Problem Statement

Managing translations across multiple JSON files (`es.json`, `eu.json`) in an Angular `@ngx-translate` project is tedious and error-prone. A CLI tool is needed to move, delete, create, update, and search translation keys across all language files simultaneously, with safety features like dry-run, confirmations, and normalization.

## Scope

- Standalone Python CLI tool in `/tmp/i18n-tool/`
- Operates on JSON translation files in a configurable i18n directory (default: `/workspaces/laned-flanbidehome/public/i18n`)
- Uses `click` as the only external dependency
- TDD approach — every feature must have tests written before implementation, using `pytest`

## Architecture

```
i18n-tool/
├── cli.py            # Click CLI entry point, command group, global options
├── core.py           # Pure functions for JSON manipulation
├── tests/
│   ├── test_core.py  # Unit tests for core functions
│   └── test_cli.py   # Integration tests for CLI commands
├── requirements.txt  # click, pytest
└── README.md         # Usage examples
```

- **`cli.py`** — Click command group with global `--i18n-dir` and `--dry-run` options. Subcommands: `move`, `delete`, `create`, `update`, `search`.
- **`core.py`** — Pure, stateless functions for all JSON manipulation. No I/O side effects in logic functions (I/O isolated to `load_all`/`save_all`).

## Functional Requirements

### FR-1: Move (`move <source> <target>`)

- Moves a translation key from one dot-path to another across **all** language files.
- If the target key already exists → prompt for overwrite confirmation.
- If the source key is missing in some language files → **warn** and continue with the rest.
- After removing the source, if the parent object becomes empty → prompt to clean up empty parents (or auto-clean with `--cleanup` flag).
- Supports `--dry-run`.

### FR-2: Delete (`delete <path>`)

- Deletes a translation key across **all** language files.
- Prompts for confirmation before deleting (skip with `--yes` flag).
- If the parent object becomes empty after deletion → prompt to clean up (auto with `--cleanup` flag).
- Warns if the key is missing in some language files but continues with the rest.
- Supports `--dry-run`.

### FR-3: Create (`create <path> <lang> <value>`)

- Creates a new translation entry for a **specific** language file.
- Normalizes the value to **lowercase** by default. Use `--no-normalize` flag to preserve the value exactly as provided.
- Errors if the key already exists in the specified language file.
- Supports `--dry-run`.

### FR-4: Update (`update <path> <lang> <value>`)

- Updates an existing translation entry for a **specific** language file.
- Errors if the key does **not** exist in the specified language file.
- Supports `--dry-run`.

### FR-5: Search (`search <query>`)

- Default: search by **key** — partial substring match on dot-paths.
- `--by-value` flag: search by **value** — partial substring match on leaf values.
- Normalizes both query and targets to lowercase before matching.
- Output: one matching dot-path per line (simple list).

## Cross-Cutting Concerns

| Concern | Behavior |
|---|---|
| `--dry-run` | All mutating commands print what would happen without writing any files |
| JSON formatting | 2-space indentation, no trailing newline (matches existing files) |
| Dot-notation paths | e.g., `EMPLEO.DETALLE.TIPO_LABEL` to address nested keys |
| Multi-language ops | `move` and `delete` operate on all files; `create` and `update` target a single language |
| Missing keys | Warn when a key is absent in some language files, continue with the rest |

## Architectural Decisions

| Decision | Rationale |
|---|---|
| Standalone Python project | Decoupled from the Angular project; portable and reusable |
| `click` for CLI | Lightweight, well-documented, handles prompts/confirmations natively |
| `pytest` for testing | Standard Python test framework, good for TDD workflow |
| Pure functions in `core.py` | Testable without filesystem; I/O isolated to `load_all`/`save_all` |
| Move: warn + continue on missing keys | Avoids blocking the entire operation for partial inconsistencies |
| Delete: prompt for empty parent cleanup | Safe default; `--cleanup` flag for automation |
| Create: lowercase normalization by default | Consistent with project conventions; `--no-normalize` for exceptions |
| Search: simple list output | Minimal, scriptable output format |
