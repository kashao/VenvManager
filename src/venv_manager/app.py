from __future__ import annotations

import tkinter as tk
from importlib.resources import as_file, files

import ttkbootstrap as ttk

from venv_manager.config import ConfigStore
from venv_manager.ui.main_window import MainWindow
from venv_manager.ui.styles import LIGHT_THEME, WINDOW_MIN_SIZE, WINDOW_SIZE, configure_styles
from venv_manager.venv_service import VenvService


def create_app() -> ttk.Window:
    config_store = ConfigStore()
    config = config_store.load()
    window = ttk.Window(title="VenvManager", themename=config.theme or LIGHT_THEME)
    window.geometry(WINDOW_SIZE)
    window.minsize(*WINDOW_MIN_SIZE)
    _set_window_icon(window)
    configure_styles(ttk.Style())
    MainWindow(window, config_store, VenvService(), config)
    return window


def _set_window_icon(window: ttk.Window) -> None:
    try:
        icon_path = files("venv_manager.assets").joinpath("app.ico")
        with as_file(icon_path) as resolved_icon:
            window.iconbitmap(str(resolved_icon))
    except (FileNotFoundError, ModuleNotFoundError, OSError, RuntimeError, tk.TclError):
        return


def main() -> None:
    app = create_app()
    app.mainloop()
