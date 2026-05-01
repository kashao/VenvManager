from __future__ import annotations

import os
import sys
from pathlib import Path

APP_NAME = "VenvManager"


def get_user_config_dir() -> Path:
    """Return a writable per-user config directory that also works from onefile exe."""
    appdata = os.environ.get("APPDATA")
    if appdata:
        return Path(appdata) / APP_NAME

    xdg_config_home = os.environ.get("XDG_CONFIG_HOME")
    if xdg_config_home:
        return Path(xdg_config_home) / APP_NAME

    return Path.home() / ".config" / APP_NAME


def get_config_path() -> Path:
    return get_user_config_dir() / "config.json"


def get_default_venv_root() -> Path:
    return Path.home() / APP_NAME / "venvs"


def get_runtime_base_dir() -> Path:
    """Return the app folder during development, or the extracted folder in PyInstaller."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    return Path(__file__).resolve().parents[2]
