# cli.py — Click CLI entry point
import click
from core import load_all, save_all, get_by_path, set_by_path, delete_by_path, search_keys, search_values
from config import (load_config, save_config, build_default_map,
                    config_path_local, config_path_global, FLAG_COMMANDS, SUBCOMMANDS)


def _load_merged_config():
    return build_default_map(
        load_config(config_path_local()),
        load_config(config_path_global()),
    )


@click.group()
@click.option("--i18n-dir", default=None, help="Path to i18n JSON directory.")
@click.option("--dry-run", is_flag=True, help="Print actions without writing files.")
@click.pass_context
def cli(ctx, i18n_dir, dry_run):
    """i18n CLI tool — manage translation keys across JSON files."""
    ctx.ensure_object(dict)
    merged = _load_merged_config()
    # default_map for subcommand-level options
    ctx.default_map = merged
    # For group-level options, apply config if user didn't pass a flag
    ctx.obj["i18n_dir"] = i18n_dir or merged.get("i18n_dir")
    ctx.obj["dry_run"] = dry_run or merged.get("dry_run", False)


# --- config subcommand group ---

VALID_KEYS = set(FLAG_COMMANDS.keys()) | {
    f"{cmd}.{key}" for key, cmds in FLAG_COMMANDS.items() for cmd in cmds
}
BOOL_KEYS = {"dry_run", "no_normalize", "yes", "cleanup"}


def _parse_value(key, value):
    """Convert string value to appropriate type."""
    base_key = key.split(".")[-1] if "." in key else key
    if base_key in BOOL_KEYS:
        if value.lower() in ("true", "1", "yes"):
            return True
        if value.lower() in ("false", "0", "no"):
            return False
        raise click.BadParameter(f"Boolean flag '{key}' must be true/false.")
    return value


@cli.group("config")
def config_cmd():
    """Manage persistent configuration."""


@config_cmd.command("set")
@click.argument("key")
@click.argument("value")
@click.option("--global", "use_global", is_flag=True, help="Write to global config.")
def config_set(key, value, use_global):
    """Set a config value. Use dotted keys for per-command settings (e.g. delete.cleanup)."""
    if key not in VALID_KEYS:
        raise click.ClickException(f"Unknown config key '{key}'. Valid: {sorted(VALID_KEYS)}")
    path = config_path_global() if use_global else config_path_local()
    cfg = load_config(path)
    parsed = _parse_value(key, value)
    if "." in key:
        cmd, k = key.split(".", 1)
        cfg.setdefault(cmd, {})[k] = parsed
    else:
        cfg[key] = parsed
    save_config(path, cfg)
    click.echo(f"Set {key} = {parsed}")


@config_cmd.command("get")
@click.argument("key")
@click.option("--global", "use_global", is_flag=True, help="Read from global config only.")
def config_get(key, use_global):
    """Get a config value."""
    if use_global:
        cfg = load_config(config_path_global())
    else:
        local_cfg = load_config(config_path_local())
        global_cfg = load_config(config_path_global())
        cfg = {**global_cfg, **local_cfg}
    if "." in key:
        cmd, k = key.split(".", 1)
        val = cfg.get(cmd, {}).get(k)
    else:
        val = cfg.get(key)
    if val is None:
        click.echo(f"{key}: (not set)")
    else:
        click.echo(f"{key} = {val}")


@config_cmd.command("delete")
@click.argument("key")
@click.option("--global", "use_global", is_flag=True, help="Delete from global config.")
def config_delete(key, use_global):
    """Delete a config key."""
    path = config_path_global() if use_global else config_path_local()
    cfg = load_config(path)
    if "." in key:
        cmd, k = key.split(".", 1)
        if cmd in cfg and isinstance(cfg[cmd], dict) and k in cfg[cmd]:
            del cfg[cmd][k]
            if not cfg[cmd]:
                del cfg[cmd]
        else:
            raise click.ClickException(f"Key '{key}' not found in config.")
    elif key in cfg:
        del cfg[key]
    else:
        raise click.ClickException(f"Key '{key}' not found in config.")
    save_config(path, cfg)
    click.echo(f"Deleted {key}")


def _require_i18n_dir(ctx):
    d = ctx.obj["i18n_dir"]
    if not d:
        raise click.ClickException("--i18n-dir is required. Pass it as a flag or set it via: i18n-tool config set i18n_dir <path>")
    return d


@cli.command()
@click.argument("query")
@click.option("--by-value", is_flag=True, help="Search by value instead of key.")
@click.pass_context
def search(ctx, query, by_value):
    """Search translation keys or values."""
    files = load_all(_require_i18n_dir(ctx))
    seen = set()
    for data in files.values():
        for path in (search_values(data, query) if by_value else search_keys(data, query)):
            if path not in seen:
                seen.add(path)
                click.echo(path)


@cli.command()
@click.argument("path")
@click.argument("lang")
@click.argument("value")
@click.option("--no-normalize", is_flag=True, help="Preserve original casing.")
@click.pass_context
def create(ctx, path, lang, value, no_normalize):
    """Create a new translation key in a specific language file."""
    i18n_dir = _require_i18n_dir(ctx)
    files = load_all(i18n_dir)
    if lang not in files:
        raise click.ClickException(f"Language file '{lang}' not found.")
    if get_by_path(files[lang], path) is not None:
        raise click.ClickException(f"Key '{path}' already exists in '{lang}'.")
    val = value if no_normalize else value.lower()
    if ctx.obj["dry_run"]:
        click.echo(f"[dry-run] Would create '{path}' in '{lang}' with value '{val}'")
        return
    set_by_path(files[lang], path, val)
    save_all(i18n_dir, files)


@cli.command()
@click.argument("path")
@click.argument("lang")
@click.argument("value")
@click.pass_context
def update(ctx, path, lang, value):
    """Update an existing translation key in a specific language file."""
    i18n_dir = _require_i18n_dir(ctx)
    files = load_all(i18n_dir)
    if lang not in files:
        raise click.ClickException(f"Language file '{lang}' not found.")
    old = get_by_path(files[lang], path)
    if old is None:
        raise click.ClickException(f"Key '{path}' does not exist in '{lang}'.")
    if ctx.obj["dry_run"]:
        click.echo(f"[dry-run] Would update '{path}' in '{lang}': '{old}' → '{value}'")
        return
    set_by_path(files[lang], path, value)
    save_all(i18n_dir, files)


@cli.command()
@click.argument("path")
@click.option("--yes", is_flag=True, help="Skip confirmation prompt.")
@click.option("--cleanup", is_flag=True, help="Auto-clean empty parent objects.")
@click.pass_context
def delete(ctx, path, yes, cleanup):
    """Delete a translation key across all language files."""
    i18n_dir = _require_i18n_dir(ctx)
    files = load_all(i18n_dir)
    if not yes:
        if not click.confirm(f"Delete '{path}' from all language files?"):
            return
    dry_run = ctx.obj["dry_run"]
    for lang, data in files.items():
        if get_by_path(data, path) is None:
            click.echo(f"Warning: '{path}' missing in '{lang}', skipping.")
            continue
        if dry_run:
            click.echo(f"[dry-run] Would delete '{path}' from '{lang}'")
            continue
        parent_empty = delete_by_path(data, path)
        has_parent = "." in path
        if parent_empty and has_parent and not cleanup:
            if not click.confirm(f"Parent of '{path}' is empty in '{lang}'. Clean up?"):
                continue
        if parent_empty and has_parent and cleanup:
            # Walk up and remove empty parents
            parts = path.split(".")
            while len(parts) > 1:
                parts.pop()
                parent = get_by_path(data, ".".join(parts))
                if isinstance(parent, dict) and not parent:
                    delete_by_path(data, ".".join(parts))
                else:
                    break
    if not dry_run:
        save_all(i18n_dir, files)


@cli.command()
@click.argument("source")
@click.argument("target")
@click.option("--cleanup", is_flag=True, help="Auto-clean empty parent objects.")
@click.pass_context
def move(ctx, source, target, cleanup):
    """Move a translation key from source to target across all language files."""
    i18n_dir = _require_i18n_dir(ctx)
    dry_run = ctx.obj["dry_run"]
    files = load_all(i18n_dir)
    # Check if target exists in any file — prompt for overwrite
    target_exists = any(get_by_path(data, target) is not None for data in files.values())
    if target_exists:
        if not click.confirm(f"Target '{target}' already exists. Overwrite?"):
            return
    for lang, data in files.items():
        val = get_by_path(data, source)
        if val is None:
            click.echo(f"Warning: '{source}' missing in '{lang}', skipping.")
            continue
        if dry_run:
            click.echo(f"[dry-run] Would move '{source}' → '{target}' in '{lang}'")
            continue
        set_by_path(data, target, val)
        parent_empty = delete_by_path(data, source)
        if parent_empty and "." in source:
            if cleanup:
                parts = source.split(".")
                while len(parts) > 1:
                    parts.pop()
                    parent = get_by_path(data, ".".join(parts))
                    if isinstance(parent, dict) and not parent:
                        delete_by_path(data, ".".join(parts))
                    else:
                        break
            elif not click.confirm(f"Parent of '{source}' is empty in '{lang}'. Clean up?"):
                pass
    if not dry_run:
        save_all(i18n_dir, files)


if __name__ == "__main__":
    cli()
