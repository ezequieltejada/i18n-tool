# core.py — Pure functions for JSON manipulation
import json
import os


def load_all(i18n_dir):
    result = {}
    for f in os.listdir(i18n_dir):
        if f.endswith(".json"):
            with open(os.path.join(i18n_dir, f)) as fh:
                result[f[:-5]] = json.load(fh)
    return result


def save_all(i18n_dir, files):
    for name, data in files.items():
        with open(os.path.join(i18n_dir, f"{name}.json"), "w") as fh:
            fh.write(json.dumps(data, indent=2, ensure_ascii=False))


def get_by_path(data, dot_path):
    node = data
    for key in dot_path.split("."):
        if not isinstance(node, dict) or key not in node:
            return None
        node = node[key]
    return node


def set_by_path(data, dot_path, value):
    keys = dot_path.split(".")
    node = data
    for key in keys[:-1]:
        node = node.setdefault(key, {})
    node[keys[-1]] = value


def delete_by_path(data, dot_path):
    keys = dot_path.split(".")
    node = data
    for key in keys[:-1]:
        if not isinstance(node, dict) or key not in node:
            return False
        node = node[key]
    if keys[-1] not in node:
        return False
    del node[keys[-1]]
    return len(node) == 0


def flatten_keys(data, prefix=""):
    result = {}
    for k, v in data.items():
        key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            result.update(flatten_keys(v, key))
        else:
            result[key] = v
    return result


def search_keys(data, query):
    q = query.lower()
    return [k for k in flatten_keys(data) if q in k.lower()]


def search_values(data, query):
    q = query.lower()
    return [k for k, v in flatten_keys(data).items() if isinstance(v, str) and q in v.lower()]
