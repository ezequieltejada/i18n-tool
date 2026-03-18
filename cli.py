# cli.py — Click CLI entry point
import click
from core import load_all, save_all, get_by_path, set_by_path, delete_by_path, search_keys, search_values


@click.group()
@click.option("--i18n-dir", default="/workspaces/laned-flanbidehome/public/i18n",
              help="Path to i18n JSON directory.")
@click.option("--dry-run", is_flag=True, help="Print actions without writing files.")
@click.pass_context
def cli(ctx, i18n_dir, dry_run):
    """i18n CLI tool — manage translation keys across JSON files."""
    ctx.ensure_object(dict)
    ctx.obj["i18n_dir"] = i18n_dir
    ctx.obj["dry_run"] = dry_run


@cli.command()
@click.argument("query")
@click.option("--by-value", is_flag=True, help="Search by value instead of key.")
@click.pass_context
def search(ctx, query, by_value):
    """Search translation keys or values."""
    files = load_all(ctx.obj["i18n_dir"])
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
    i18n_dir = ctx.obj["i18n_dir"]
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
    i18n_dir = ctx.obj["i18n_dir"]
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
    i18n_dir = ctx.obj["i18n_dir"]
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
        if parent_empty and not cleanup:
            if not click.confirm(f"Parent of '{path}' is empty in '{lang}'. Clean up?"):
                continue
        if parent_empty and cleanup:
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
    i18n_dir = ctx.obj["i18n_dir"]
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
        if parent_empty:
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
