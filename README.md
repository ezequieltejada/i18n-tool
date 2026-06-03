[![Tests](https://github.com/ezequieltejada/i18n-tool/actions/workflows/tests.yml/badge.svg)](https://github.com/ezequieltejada/i18n-tool/actions/workflows/tests.yml)

# i18n CLI Tool

A CLI tool for managing translation keys across multiple JSON files in an Angular `@ngx-translate` project.

## Installation

Install the latest release directly from GitHub:

```bash
pip install git+https://github.com/ezequieltejada/i18n-tool.git@v1.0.0
```

Or install from a local clone:

```bash
pip install .
```

After installation, the `i18n-tool` command is available globally:

```bash
i18n-tool --help
```

For development:

```bash
pip install -r requirements.txt
```

## Updating

Update to the latest release:

```bash
i18n-tool self-update
```

Force reinstall even if already on the latest version:

```bash
i18n-tool self-update --force
```

Preview what would happen without installing:

```bash
i18n-tool self-update --dry-run
```

## Usage

```bash
i18n-tool --i18n-dir ./public/i18n [--dry-run] <command> [options]
```

### Search

Search translation keys by dot-path (default) or by value (`--by-value`).

```bash
# Search by key
python cli.py --i18n-dir ./i18n search "EMPLEO"

# Search by value
python cli.py --i18n-dir ./i18n search --by-value "oferta"
```

### Create

Create a new translation key in a specific language file. Values are lowercased by default; use `--no-normalize` to preserve casing.

```bash
python cli.py --i18n-dir ./i18n create "EMPLEO.SUBTITULO" es "subtítulo"

# Preserve original casing
python cli.py --i18n-dir ./i18n create --no-normalize "EMPLEO.SUBTITULO" es "Subtítulo"
```

### Update

Update an existing translation key in a specific language file.

```bash
python cli.py --i18n-dir ./i18n update "EMPLEO.TITULO" es "nueva oferta"
```

### Delete

Delete a translation key across all language files. Prompts for confirmation (skip with `--yes`). If the parent becomes empty, prompts for cleanup (auto with `--cleanup`).

```bash
python cli.py --i18n-dir ./i18n delete "EMPLEO.DETALLE.TIPO_LABEL"

# Skip confirmation and auto-clean empty parents
python cli.py --i18n-dir ./i18n delete --yes --cleanup "EMPLEO.DETALLE.TIPO_LABEL"
```

### Move

Move a translation key from one path to another across all language files. Prompts if the target already exists. Use `--cleanup` to auto-remove empty parents after the move.

```bash
python cli.py --i18n-dir ./i18n move "EMPLEO.DETALLE.TIPO_LABEL" "COMMON.TIPO_LABEL"

# Auto-clean empty parents
python cli.py --i18n-dir ./i18n move --cleanup "EMPLEO.DETALLE.TIPO_LABEL" "COMMON.TIPO_LABEL"
```

### Dry Run

All write commands support `--dry-run` to preview what would happen:

```bash
python cli.py --i18n-dir ./i18n --dry-run delete --yes "EMPLEO.TITULO"
python cli.py --i18n-dir ./i18n --dry-run move "A.B" "C.D"
```

## Testing

```bash
python -m pytest -q
```

## Architecture

- `core.py` — Pure functions for JSON manipulation with post-write validation and rollback
- `cli.py` — Click CLI entry point with subcommands
- `config.py` — Persistent configuration (local and global)
- `tests/test_core.py` — Unit tests for core functions
- `tests/test_cli.py` — Integration tests for CLI commands

## Releases

Releases are automated via [release-please](https://github.com/googleapis/release-please). Commits to `master` using [Conventional Commits](https://www.conventionalcommits.org/) format will automatically generate a Release PR with version bump and changelog. Merging that PR creates a GitHub release and tag.

Commit prefixes:
- `fix:` → patch bump (1.0.0 → 1.0.1)
- `feat:` → minor bump (1.0.0 → 1.1.0)
- `feat!:` or `fix!:` → major bump (1.0.0 → 2.0.0)
