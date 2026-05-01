from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog

import ttkbootstrap as ttk

from venv_manager.config import AppConfig
from venv_manager.ui.styles import PAD, SMALL_PAD
from venv_manager.venv_service import PythonInstallation


class NewVenvDialog(ttk.Toplevel):
    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master)
        self.title("新增虛擬環境")
        self.resizable(False, False)
        self.result: str | None = None
        self.name_var = tk.StringVar()

        container = ttk.Frame(self, padding=PAD)
        container.pack(fill="both", expand=True)

        ttk.Label(container, text="虛擬環境名稱").grid(row=0, column=0, sticky="w")
        entry = ttk.Entry(container, textvariable=self.name_var, width=34)
        entry.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(SMALL_PAD, PAD))

        ttk.Button(container, text="取消", command=self._cancel, bootstyle="secondary-outline").grid(
            row=2, column=0, sticky="e", padx=(0, SMALL_PAD)
        )
        ttk.Button(container, text="建立", command=self._submit, bootstyle="primary").grid(
            row=2, column=1, sticky="e"
        )

        self.bind("<Return>", lambda _event: self._submit())
        self.bind("<Escape>", lambda _event: self._cancel())
        self.transient(master)
        self.grab_set()
        entry.focus_set()
        self._center(master)
        self.wait_window()

    def _submit(self) -> None:
        name = self.name_var.get().strip()
        if name:
            self.result = name
            self.destroy()

    def _cancel(self) -> None:
        self.result = None
        self.destroy()

    def _center(self, master: tk.Misc) -> None:
        self.update_idletasks()
        x = master.winfo_rootx() + (master.winfo_width() - self.winfo_width()) // 2
        y = master.winfo_rooty() + (master.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{max(x, 0)}+{max(y, 0)}")


class PackageInputDialog(ttk.Toplevel):
    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master)
        self.title("安裝套件")
        self.resizable(False, False)
        self.result: str | None = None
        self.package_var = tk.StringVar()

        container = ttk.Frame(self, padding=PAD)
        container.pack(fill="both", expand=True)

        ttk.Label(container, text="套件名稱").grid(row=0, column=0, sticky="w")
        entry = ttk.Entry(container, textvariable=self.package_var, width=42)
        entry.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(SMALL_PAD, PAD))
        ttk.Label(
            container,
            text="可輸入 requests、rich==13.7.0 等 pip install 支援的格式。",
            bootstyle="secondary",
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(0, PAD))

        ttk.Button(container, text="取消", command=self._cancel, bootstyle="secondary-outline").grid(
            row=3, column=0, sticky="e", padx=(0, SMALL_PAD)
        )
        ttk.Button(container, text="安裝", command=self._submit, bootstyle="primary").grid(
            row=3, column=1, sticky="e"
        )

        self.bind("<Return>", lambda _event: self._submit())
        self.bind("<Escape>", lambda _event: self._cancel())
        self.transient(master)
        self.grab_set()
        entry.focus_set()
        self._center(master)
        self.wait_window()

    def _submit(self) -> None:
        package = self.package_var.get().strip()
        if package:
            self.result = package
            self.destroy()

    def _cancel(self) -> None:
        self.result = None
        self.destroy()

    def _center(self, master: tk.Misc) -> None:
        self.update_idletasks()
        x = master.winfo_rootx() + (master.winfo_width() - self.winfo_width()) // 2
        y = master.winfo_rooty() + (master.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{max(x, 0)}+{max(y, 0)}")


class PackageListDialog(ttk.Toplevel):
    def __init__(
        self,
        master: tk.Misc,
        venv_name: str,
        packages: list[str],
        saved_path: Path,
    ) -> None:
        super().__init__(master)
        self.title(f"已安裝套件 - {venv_name}")
        self.geometry("620x420")
        self.minsize(520, 320)

        container = ttk.Frame(self, padding=PAD)
        container.pack(fill="both", expand=True)
        container.rowconfigure(2, weight=1)
        container.columnconfigure(0, weight=1)

        count_text = f"{venv_name} 目前有 {len(packages)} 個套件"
        ttk.Label(container, text=count_text, style="CardTitle.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, SMALL_PAD)
        )
        ttk.Label(
            container,
            text=f"已輸出：{saved_path}",
            bootstyle="secondary",
            wraplength=560,
            justify="left",
        ).grid(row=1, column=0, sticky="ew", pady=(0, SMALL_PAD))

        text_frame = ttk.Frame(container)
        text_frame.grid(row=2, column=0, sticky="nsew")
        text_frame.rowconfigure(0, weight=1)
        text_frame.columnconfigure(0, weight=1)

        text = tk.Text(text_frame, wrap="none", height=18)
        text.insert("1.0", "\n".join(packages) if packages else "尚未安裝任何套件。")
        text.configure(state="disabled")
        yscroll = ttk.Scrollbar(text_frame, orient="vertical", command=text.yview)
        text.configure(yscrollcommand=yscroll.set)
        text.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")

        ttk.Button(container, text="關閉", command=self.destroy, bootstyle="secondary").grid(
            row=3, column=0, sticky="e", pady=(PAD, 0)
        )

        self.transient(master)
        self.grab_set()
        self._center(master)

    def _center(self, master: tk.Misc) -> None:
        self.update_idletasks()
        x = master.winfo_rootx() + (master.winfo_width() - self.winfo_width()) // 2
        y = master.winfo_rooty() + (master.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{max(x, 0)}+{max(y, 0)}")


class SettingsDialog(ttk.Toplevel):
    def __init__(
        self,
        master: tk.Misc,
        config: AppConfig,
        python_installations: list[PythonInstallation],
    ) -> None:
        super().__init__(master)
        self.title("設定")
        self.resizable(False, False)
        self.result: AppConfig | None = None
        self.venv_root_var = tk.StringVar(value=config.venv_root)
        self.base_python_var = tk.StringVar(value=config.base_python)
        self.installations = python_installations
        self.installation_by_label = {item.label: item for item in python_installations}

        container = ttk.Frame(self, padding=PAD)
        container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=1)

        ttk.Label(container, text="venv 存放資料夾").grid(row=0, column=0, sticky="w")
        root_row = ttk.Frame(container)
        root_row.grid(row=1, column=0, sticky="ew", pady=(SMALL_PAD, PAD))
        root_row.columnconfigure(0, weight=1)
        ttk.Entry(root_row, textvariable=self.venv_root_var, width=64).grid(
            row=0, column=0, sticky="ew", padx=(0, SMALL_PAD)
        )
        ttk.Button(root_row, text="瀏覽", command=self._browse_root, bootstyle="secondary").grid(
            row=0, column=1
        )

        ttk.Label(container, text="Base Python").grid(row=2, column=0, sticky="w")
        python_row = ttk.Frame(container)
        python_row.grid(row=3, column=0, sticky="ew", pady=(SMALL_PAD, SMALL_PAD))
        python_row.columnconfigure(0, weight=1)

        values = [item.label for item in python_installations]
        current_label = self._label_for_command(config.base_python)
        if current_label and current_label not in values:
            values.insert(0, current_label)

        state = "readonly" if values else "normal"
        self.base_combo = ttk.Combobox(
            python_row,
            textvariable=self.base_python_var,
            values=values,
            state=state,
            width=62,
        )
        self.base_combo.grid(row=0, column=0, sticky="ew", padx=(0, SMALL_PAD))
        ttk.Button(
            python_row,
            text="python.exe",
            command=self._browse_python,
            bootstyle="secondary",
        ).grid(row=0, column=1)

        if current_label:
            self.base_python_var.set(current_label)

        hint = "下拉選單會掃描 Python Launcher 與 PATH；也可以指定完整 python.exe。"
        ttk.Label(container, text=hint, bootstyle="secondary").grid(
            row=4, column=0, sticky="w", pady=(0, PAD)
        )

        actions = ttk.Frame(container)
        actions.grid(row=5, column=0, sticky="e")
        ttk.Button(actions, text="取消", command=self._cancel, bootstyle="secondary-outline").pack(
            side="left", padx=(0, SMALL_PAD)
        )
        ttk.Button(actions, text="儲存", command=self._submit, bootstyle="primary").pack(side="left")

        self.bind("<Escape>", lambda _event: self._cancel())
        self.transient(master)
        self.grab_set()
        self._center(master)
        self.wait_window()

    def _label_for_command(self, command: str) -> str:
        for item in self.installations:
            if item.command == command:
                return item.label
        return command

    def _browse_root(self) -> None:
        selected = filedialog.askdirectory(parent=self, initialdir=self.venv_root_var.get() or None)
        if selected:
            self.venv_root_var.set(selected)

    def _browse_python(self) -> None:
        selected = filedialog.askopenfilename(
            parent=self,
            title="選擇 python.exe",
            filetypes=[("Python executable", "python.exe"), ("Executable", "*.exe")],
        )
        if selected:
            self.base_python_var.set(str(Path(selected)))

    def _submit(self) -> None:
        base_python = self.base_python_var.get().strip()
        install = self.installation_by_label.get(base_python)
        if install:
            base_python = install.command

        self.result = AppConfig(
            venv_root=self.venv_root_var.get().strip(),
            base_python=base_python,
        )
        self.destroy()

    def _cancel(self) -> None:
        self.result = None
        self.destroy()

    def _center(self, master: tk.Misc) -> None:
        self.update_idletasks()
        x = master.winfo_rootx() + (master.winfo_width() - self.winfo_width()) // 2
        y = master.winfo_rooty() + (master.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{max(x, 0)}+{max(y, 0)}")
