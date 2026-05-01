from __future__ import annotations

from tkinter import font

from ttkbootstrap import Style

LIGHT_THEME = "flatly"
DARK_THEME = "darkly"

WINDOW_SIZE = "900x600"
WINDOW_MIN_SIZE = (760, 480)

PAD = 12
SMALL_PAD = 6
CARD_PAD = 10


def configure_styles(style: Style) -> None:
    default_font = font.nametofont("TkDefaultFont")
    default_font.configure(size=10)

    heading_font = font.nametofont("TkHeadingFont")
    heading_font.configure(size=11, weight="bold")

    style.configure("Header.TLabel", font=("Segoe UI", 18, "bold"))
    style.configure("Description.TLabel", font=("Segoe UI", 10))
    style.configure("CardTitle.TLabel", font=("Segoe UI", 10, "bold"))
    style.configure("Status.TLabel", padding=(PAD, SMALL_PAD))
