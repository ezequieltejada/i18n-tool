# TASKS — i18n CLI Tool

Progress tracker for the i18n CLI tool. TDD approach: write tests **before** implementation for every feature.

---

## Task 1: Project scaffolding and core JSON utilities ✅

- [x] Set up project structure: `cli.py`, `core.py`, `tests/`, `requirements.txt`
- [x] Write tests for `load_all(i18n_dir)` — discover and load all `*.json` files from a directory
- [x] Write tests for `save_all(i18n_dir, files)` — write JSON with 2-space indent, no trailing newline
- [x] Write tests for `get_by_path(data, dot_path)` — traverse nested dict, return value or `None`
- [x] Write tests for `set_by_path(data, dot_path, value)` — set value, creating intermediate dicts
- [x] Write tests for `delete_by_path(data, dot_path)` — delete key, return whether parent became empty
- [x] Implement all core functions to pass tests
- [x] Wire up `cli.py` Click group with `--i18n-dir` and `--dry-run` global options
- [x] Verify: `python cli.py --help` shows command group and global options

## Task 2: Search command ✅

- [x] Write tests: search by key substring match
- [x] Write tests: search by value substring match (`--by-value`)
- [x] Write tests: normalization (case-insensitive matching)
- [x] Write tests: no matches returns empty output
- [x] Implement `search` subcommand in `cli.py`
- [x] Implement `flatten_keys(data)` and `search_keys(data, query)` / `search_values(data, query)` in `core.py`
- [x] Verify: `python cli.py search "EMPLEO.DETALLE"` returns matching dot-paths

## Task 3: Create command ✅

- [x] Write tests: create new key at dot-path in a language file
- [x] Write tests: value normalized to lowercase by default
- [x] Write tests: `--no-normalize` preserves original casing
- [x] Write tests: error when key already exists
- [x] Write tests: `--dry-run` prints intent without writing
- [x] Implement `create` subcommand in `cli.py`
- [x] Verify: `python cli.py create "EMPLEO.SUBTITULO" es "Subtitulo"` adds key with lowercase value

## Task 4: Update command ✅

- [x] Write tests: update existing key with new value
- [x] Write tests: error when key does not exist
- [x] Write tests: `--dry-run` shows old → new value without writing
- [x] Implement `update` subcommand in `cli.py`
- [x] Verify: `python cli.py update "EMPLEO.SUBTITULO" es "Nuevo valor"` updates the value

## Task 5: Delete command ✅

- [x] Write tests: delete key across all language files
- [x] Write tests: confirmation prompt (default behavior)
- [x] Write tests: `--yes` flag skips confirmation
- [x] Write tests: empty parent cleanup prompt after deletion
- [x] Write tests: `--cleanup` flag auto-cleans empty parents
- [x] Write tests: warn when key missing in some files, continue with rest
- [x] Write tests: `--dry-run` shows what would be deleted without writing
- [x] Implement `delete` subcommand in `cli.py`
- [x] Verify: `python cli.py delete "EMPLEO.DETALLE.NOT_SPECIFIED"` removes from all files

## Task 6: Move command ✅

- [x] Write tests: move key from source to target across all language files
- [x] Write tests: prompt for overwrite when target exists
- [x] Write tests: warn when source missing in some files, continue with rest
- [x] Write tests: empty parent cleanup after source removal (prompt + `--cleanup`)
- [x] Write tests: `--dry-run` shows move plan without writing
- [x] Implement `move` subcommand in `cli.py`
- [x] Verify: `python cli.py move "EMPLEO.DETALLE.NOT_SPECIFIED" "COMMON.NOT_SPECIFIED"` moves in all files

## Task 7: README and final integration ✅

- [x] Write `README.md` with usage examples for all commands
- [x] End-to-end verification: search → create → update → move → delete on real files
