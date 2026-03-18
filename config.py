# config.py — Persistent configuration for i18n-tool
import json
import os

LOCAL_FILE = ".i18n-tool.json"
GLOBAL_FILE = os.path.join("~", ".config", "i18n-tool", "config.json")

# Which commands use each flag
FLAG_COMMANDS = {
    "i18n_dir": ["search", "create", "update", "delete", "move"],
    "dry_run": ["search", "create", "update", "delete", "move"],
    "no_normalize": ["create"],
    "yes": ["delete"],
    "cleanup": ["delete", "move"],
}

SUBCOMMANDS = {"search", "create", "update", "delete", "move"}


def config_path_local():
    return os.path.join(os.getcwd(), LOCAL_FILE)


def config_path_global():
    return os.path.expanduser(GLOBAL_FILE)


def load_config(path):
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_config(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def build_default_map(local_cfg, global_cfg):
    """Merge global and local configs into a Click default_map.

    Resolution: global_cfg → local_cfg (local wins).
    For each source, global keys propagate to all relevant subcommands,
    then per-command keys override.
    """
    result = {}

    for cfg in (global_cfg, local_cfg):
        # Apply global-level keys
        for key, val in cfg.items():
            if key in SUBCOMMANDS:
                continue
            if key in FLAG_COMMANDS:
                for cmd in FLAG_COMMANDS[key]:
                    result.setdefault(cmd, {})[key] = val
            # Also set at top level for group-level options
            result[key] = val

        # Apply per-command keys (override global)
        for cmd in SUBCOMMANDS:
            if cmd in cfg and isinstance(cfg[cmd], dict):
                for key, val in cfg[cmd].items():
                    result.setdefault(cmd, {})[key] = val

    return result
