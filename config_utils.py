import copy
import os

import yaml

DEFAULT_CONFIG = {
    "active_profile": "default",
    "profiles": {
        "default": {
            "venv_root": "",
            "activate_workdir": "",
        }
    },
    "base_python": {
        "mode": "py",
        "py_version": "3.11",
        "path": "",
    },
}


def get_config_path():
    appdata = os.environ.get("APPDATA") or os.path.expanduser("~")
    config_dir = os.path.join(appdata, "VenvManager")
    os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, "config.yaml")


def _merge_defaults(data, defaults):
    merged = copy.deepcopy(data)
    for key, value in defaults.items():
        if key not in merged:
            merged[key] = copy.deepcopy(value)
        elif isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _merge_defaults(merged[key], value)
    return merged


def load_config():
    path = get_config_path()
    if not os.path.exists(path):
        config = copy.deepcopy(DEFAULT_CONFIG)
        save_config(config)
        return config

    with open(path, "r", encoding="utf-8") as file:
        loaded = yaml.safe_load(file) or {}
    config = _merge_defaults(loaded, DEFAULT_CONFIG)

    active_profile = config.get("active_profile", "default")
    profiles = config.get("profiles", {})
    if active_profile not in profiles:
        config["active_profile"] = "default"
        config["profiles"].setdefault("default", copy.deepcopy(DEFAULT_CONFIG["profiles"]["default"]))
    return config


def save_config(config):
    path = get_config_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as file:
        yaml.safe_dump(config, file, sort_keys=False, allow_unicode=True)
