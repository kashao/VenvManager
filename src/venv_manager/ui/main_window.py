from __future__ import annotations

import subprocess
import sys
import tkinter as tk
import tkinter.ttk as tk_ttk
from collections.abc import Callable
from pathlib import Path
from tkinter import filedialog, messagebox

import ttkbootstrap as ttk

from venv_manager.config import AppConfig, ConfigStore
from venv_manager.paths import get_config_path
from venv_manager.ui.dialogs import (
    NewVenvDialog,
    PackageInputDialog,
    PackageListDialog,
    SettingsDialog,
)
from venv_manager.ui.styles import CARD_PAD, PAD, SMALL_PAD
from venv_manager.venv_service import VenvInfo, VenvService

PanedWindow = getattr(ttk, "PanedWindow", tk_ttk.PanedWindow)


class MainWindow(ttk.Frame):
    def __init__(
        self,
        master: ttk.Window,
        config_store: ConfigStore,
        service: VenvService,
        config: AppConfig,
    ) -> None:
        super().__init__(master, padding=PAD)
        self.master = master
        self.config_store = config_store
        self.service = service
        self.config = config
        self.venvs: list[VenvInfo] = []
        self.selected_venv: VenvInfo | None = None

        self.search_var = tk.StringVar()
        self.status_var = tk.StringVar(value="就緒")
        self.detail_vars = {
            "name": tk.StringVar(value="-"),
            "path": tk.StringVar(value="-"),
            "workdir": tk.StringVar(value="-"),
            "python": tk.StringVar(value="-"),
            "activate": tk.StringVar(value="-"),
        }

        self.pack(fill="both", expand=True)
        self._build_layout()
        self._bind_events()
        self.refresh_venvs()

    def _build_layout(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        self._build_header()
        self._build_top_menu()
        self._build_content()
        self._build_status_bar()

    def _build_header(self) -> None:
        header = ttk.Frame(self)
        header.grid(row=0, column=0, sticky="ew", pady=(0, SMALL_PAD))

        ttk.Label(header, text="VenvManager", style="Header.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text="管理 Windows 本機 Python 虛擬環境、工作資料夾與 pip 套件",
            style="Description.TLabel",
            bootstyle="secondary",
        ).pack(anchor="w", pady=(2, 0))

    def _build_top_menu(self) -> None:
        top_menu = ttk.Frame(self)
        top_menu.grid(row=1, column=0, sticky="ew", pady=(0, PAD))

        self.create_button = ttk.Button(
            top_menu,
            text="新增虛擬環境",
            command=self.create_venv,
            bootstyle="primary",
        )
        self.delete_button = ttk.Button(
            top_menu,
            text="刪除",
            command=self.delete_selected_venv,
            bootstyle="danger-outline",
        )
        self.refresh_button = ttk.Button(
            top_menu,
            text="重新整理",
            command=self.refresh_venvs,
            bootstyle="info-outline",
        )
        self.settings_button = ttk.Button(
            top_menu,
            text="設定",
            command=self.open_settings,
            bootstyle="secondary-outline",
        )

        for button in (
            self.create_button,
            self.delete_button,
            self.refresh_button,
            self.settings_button,
        ):
            button.pack(side="left", padx=(0, SMALL_PAD))

    def _build_content(self) -> None:
        content = PanedWindow(self, orient="horizontal")
        content.grid(row=2, column=0, sticky="nsew")

        sidebar = ttk.Frame(content, padding=(0, 0, PAD, 0), width=160)
        list_panel = ttk.Frame(content, padding=(0, 0, PAD, 0), width=300)
        detail_panel = ttk.Frame(content)
        content.add(sidebar, weight=16)
        content.add(list_panel, weight=32)
        content.add(detail_panel, weight=52)

        sidebar.columnconfigure(0, weight=1)
        list_panel.rowconfigure(0, weight=1)
        list_panel.columnconfigure(0, weight=1)
        detail_panel.rowconfigure(0, weight=1)
        detail_panel.columnconfigure(0, weight=1)

        self._build_sidebar_actions(sidebar)
        self._build_venv_list(list_panel)
        self._build_details_area(detail_panel)
        self.after_idle(lambda: self._set_initial_pane_sizes(content))

    def _build_sidebar_actions(self, parent: ttk.Frame) -> None:
        actions = ttk.Frame(parent)
        actions.grid(row=0, column=0, sticky="new")
        actions.columnconfigure(0, weight=1)

        folder_group = self._create_action_group(actions, 0, "資料夾與啟用")
        self.open_button = self._create_action_button(
            folder_group,
            "開啟資料夾",
            self.open_selected_folder,
            "secondary",
        )
        self.workdir_button = self._create_action_button(
            folder_group,
            "工作資料夾",
            self.set_selected_workdir,
            "secondary-outline",
        )
        self.activate_button = self._create_action_button(
            folder_group,
            "啟用終端機",
            self.call_selected_venv,
            "success",
        )
        self.copy_button = self._create_action_button(
            folder_group,
            "複製指令",
            self.copy_activation_command,
            "success-outline",
        )

        package_group = self._create_action_group(actions, 1, "套件")
        self.install_button = self._create_action_button(
            package_group,
            "安裝套件",
            self.install_package,
            "primary-outline",
        )
        self.install_file_button = self._create_action_button(
            package_group,
            "批次安裝",
            self.install_requirements_file,
            "primary-outline",
        )
        self.show_packages_button = self._create_action_button(
            package_group,
            "套件清單",
            self.show_installed_packages,
            "secondary",
        )

    def _set_initial_pane_sizes(self, content: tk_ttk.PanedWindow) -> None:
        try:
            width = content.winfo_width()
            if width <= 1:
                return
            sidebar_width = min(180, max(150, width // 6))
            list_width = min(360, max(260, width // 3))
            content.sashpos(0, sidebar_width)
            content.sashpos(1, sidebar_width + list_width)
        except tk.TclError:
            return

    def _create_action_group(self, parent: ttk.Frame, row: int, text: str) -> ttk.Labelframe:
        group = ttk.Labelframe(parent, text=text, padding=SMALL_PAD)
        group.grid(row=row, column=0, sticky="ew", pady=(0, PAD))
        group.columnconfigure(0, weight=1)
        return group

    def _create_action_button(
        self,
        parent: ttk.Frame,
        text: str,
        command: Callable[[], None],
        bootstyle: str,
    ) -> ttk.Button:
        button = ttk.Button(parent, text=text, command=command, bootstyle=bootstyle)
        button.pack(fill="x", pady=(0, SMALL_PAD))
        return button

    def _build_venv_list(self, parent: ttk.Frame) -> None:
        parent.rowconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)

        card = ttk.Labelframe(parent, text="虛擬環境列表", padding=CARD_PAD)
        card.grid(row=0, column=0, sticky="nsew")
        card.rowconfigure(1, weight=1)
        card.columnconfigure(0, weight=1)

        search = ttk.Entry(card, textvariable=self.search_var)
        search.grid(row=0, column=0, sticky="ew", pady=(0, SMALL_PAD))

        list_frame = ttk.Frame(card)
        list_frame.grid(row=1, column=0, sticky="nsew")
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(
            list_frame,
            columns=("name",),
            show="headings",
            selectmode="browse",
        )
        self.tree.heading("name", text="虛擬環境")
        self.tree.column("name", anchor="w", stretch=True)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.empty_label = ttk.Label(
            list_frame,
            text="目前沒有任何虛擬環境",
            anchor="center",
            bootstyle="secondary",
        )

    def _build_details_area(self, parent: ttk.Frame) -> None:
        parent.rowconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)

        self.prompt_frame = ttk.Frame(parent, padding=PAD)
        self.prompt_frame.grid(row=0, column=0, sticky="nsew")
        ttk.Label(
            self.prompt_frame,
            text="請從中間列表選取一個虛擬環境",
            anchor="center",
            bootstyle="secondary",
        ).pack(fill="both", expand=True)

        self.details_frame = ttk.Frame(parent)
        self._build_detail_cards(self.details_frame)

    def _build_detail_cards(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(0, weight=1)
        self._create_card(parent, 0, "基本資訊", [("名稱", self.detail_vars["name"])])
        self._create_card(
            parent,
            1,
            "路徑資訊",
            [
                ("venv 位置", self.detail_vars["path"]),
                ("工作資料夾", self.detail_vars["workdir"]),
            ],
        )
        self._create_card(parent, 2, "Python 資訊", [("版本", self.detail_vars["python"])])
        self._create_card(parent, 3, "啟用指令", [("PowerShell", self.detail_vars["activate"])])

    def _create_card(
        self,
        parent: ttk.Frame,
        row: int,
        title: str,
        fields: list[tuple[str, tk.StringVar]],
    ) -> None:
        card = ttk.Labelframe(parent, text=title, padding=CARD_PAD)
        card.grid(row=row, column=0, sticky="ew", pady=(0, SMALL_PAD))
        card.columnconfigure(1, weight=1)

        for index, (label, value) in enumerate(fields):
            ttk.Label(card, text=label, bootstyle="secondary").grid(
                row=index, column=0, sticky="nw", padx=(0, SMALL_PAD), pady=(0, 3)
            )
            ttk.Label(card, textvariable=value, wraplength=620, justify="left").grid(
                row=index, column=1, sticky="ew", pady=(0, 3)
            )

    def _build_status_bar(self) -> None:
        ttk.Separator(self).grid(row=3, column=0, sticky="ew", pady=(PAD, 0))
        ttk.Label(self, textvariable=self.status_var, style="Status.TLabel").grid(
            row=4, column=0, sticky="ew"
        )

    def _bind_events(self) -> None:
        self.search_var.trace_add("write", lambda *_args: self.populate_tree())
        self.tree.bind("<<TreeviewSelect>>", lambda _event: self.on_selection_changed())

    def refresh_venvs(self) -> None:
        try:
            self.venvs = self.service.list_venvs(Path(self.config.venv_root))
        except OSError as exc:
            messagebox.showerror("讀取失敗", str(exc))
            self.venvs = []
        self.populate_tree()
        self.set_status(f"已重新整理，共 {len(self.venvs)} 個虛擬環境")

    def populate_tree(self) -> None:
        query = self.search_var.get().strip().lower()
        self.tree.delete(*self.tree.get_children())

        visible = [venv for venv in self.venvs if query in venv.name.lower()]
        for venv in visible:
            self.tree.insert("", "end", iid=venv.name, values=(venv.name,))

        if visible:
            self.empty_label.grid_remove()
        else:
            self.empty_label.grid(row=0, column=0, sticky="nsew")

        self.selected_venv = None
        self.update_details(None)
        self.update_action_states()

    def on_selection_changed(self) -> None:
        selected = self.tree.selection()
        if not selected:
            self.selected_venv = None
        else:
            name = selected[0]
            self.selected_venv = next((venv for venv in self.venvs if venv.name == name), None)
        self.update_details(self.selected_venv)
        self.update_action_states()

    def update_details(self, venv: VenvInfo | None) -> None:
        if venv is None:
            self.details_frame.grid_remove()
            self.prompt_frame.grid(row=0, column=0, sticky="nsew")
            return

        self.prompt_frame.grid_remove()
        self.details_frame.grid(row=0, column=0, sticky="new")
        self.detail_vars["name"].set(venv.name)
        self.detail_vars["path"].set(str(venv.path))
        self.detail_vars["workdir"].set(str(self.get_workdir_for_venv(venv) or "未設定"))
        self.detail_vars["python"].set(venv.python_version)
        self.detail_vars["activate"].set(self.get_activation_command_for_venv(venv))

    def update_action_states(self) -> None:
        state = "normal" if self.selected_venv else "disabled"
        for button in (
            self.delete_button,
            self.open_button,
            self.activate_button,
            self.workdir_button,
            self.copy_button,
            self.install_button,
            self.install_file_button,
            self.show_packages_button,
        ):
            button.configure(state=state)

    def create_venv(self) -> None:
        dialog = NewVenvDialog(self.master)
        if not dialog.result:
            return

        try:
            self.set_status("正在建立虛擬環境...")
            self.master.update_idletasks()
            self.service.create_venv(
                Path(self.config.venv_root),
                dialog.result,
                self.config.base_python,
            )
        except (OSError, RuntimeError, ValueError, FileExistsError) as exc:
            messagebox.showerror("建立失敗", str(exc))
            self.set_status("建立虛擬環境失敗")
            return

        self.refresh_venvs()
        self.set_status(f"已建立虛擬環境：{dialog.result}")

    def delete_selected_venv(self) -> None:
        if self.selected_venv is None:
            return
        confirm = messagebox.askyesno(
            "刪除虛擬環境",
            f"確定要刪除「{self.selected_venv.name}」嗎？",
        )
        if not confirm:
            return

        name = self.selected_venv.name
        key = self.get_workdir_key(self.selected_venv)
        try:
            self.set_status("正在刪除虛擬環境...")
            self.master.update_idletasks()
            self.service.delete_venv(self.selected_venv.path)
            self.config.venv_workdirs.pop(key, None)
            self.save_config()
        except (OSError, ValueError) as exc:
            messagebox.showerror("刪除失敗", str(exc))
            self.set_status("刪除虛擬環境失敗")
            return

        self.refresh_venvs()
        self.set_status(f"已刪除虛擬環境：{name}")

    def open_selected_folder(self) -> None:
        if self.selected_venv is None:
            return
        path = self.selected_venv.path
        try:
            if sys.platform == "win32":
                subprocess.Popen(["explorer", str(path)])
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(path)])
            else:
                subprocess.Popen(["xdg-open", str(path)])
        except OSError as exc:
            messagebox.showerror("開啟失敗", str(exc))
            return
        self.set_status(f"已開啟資料夾：{path}")

    def call_selected_venv(self) -> None:
        if self.selected_venv is None:
            return
        workdir = self.get_workdir_for_venv(self.selected_venv)
        try:
            self.service.open_activated_shell(self.selected_venv.path, workdir)
        except OSError as exc:
            messagebox.showerror("啟用失敗", str(exc))
            return
        self.set_status(f"已另開啟用終端機：{self.selected_venv.name}")

    def set_selected_workdir(self) -> None:
        if self.selected_venv is None:
            return
        initial_dir = (
            self.config.venv_workdirs.get(self.get_workdir_key(self.selected_venv))
            or self.config.last_open_dir
            or str(Path.home())
        )
        selected = filedialog.askdirectory(parent=self.master, initialdir=initial_dir)
        if not selected:
            return

        self.config.venv_workdirs[self.get_workdir_key(self.selected_venv)] = selected
        self.config.last_open_dir = selected
        if not self.save_config():
            return
        self.update_details(self.selected_venv)
        self.set_status(f"已設定工作資料夾：{selected}")

    def install_package(self) -> None:
        if self.selected_venv is None:
            return
        dialog = PackageInputDialog(self.master)
        if not dialog.result:
            return

        try:
            self.set_status(f"正在安裝套件：{dialog.result}")
            self.master.update_idletasks()
            self.service.install_package(self.selected_venv.path, dialog.result)
        except (OSError, RuntimeError, ValueError) as exc:
            messagebox.showerror("安裝套件失敗", str(exc))
            self.set_status("安裝套件失敗")
            return

        self.update_details(self.selected_venv)
        self.set_status(f"已安裝套件：{dialog.result}")

    def install_requirements_file(self) -> None:
        if self.selected_venv is None:
            return
        file_path = filedialog.askopenfilename(
            parent=self.master,
            title="選擇 requirements 檔案",
            filetypes=[("Requirements files", "*.txt *.pip"), ("All files", "*.*")],
        )
        if not file_path:
            return

        try:
            self.set_status("正在安裝多個套件...")
            self.master.update_idletasks()
            self.service.install_requirements_file(self.selected_venv.path, Path(file_path))
        except (OSError, RuntimeError, ValueError) as exc:
            messagebox.showerror("安裝多個套件失敗", str(exc))
            self.set_status("安裝多個套件失敗")
            return

        self.update_details(self.selected_venv)
        self.set_status("已安裝多個套件")

    def show_installed_packages(self) -> None:
        if self.selected_venv is None:
            return
        try:
            self.set_status("正在讀取已安裝套件...")
            self.master.update_idletasks()
            packages = self.service.get_installed_packages(self.selected_venv.path)
            saved_path = self.save_requirements_snapshot(self.selected_venv, packages)
        except (OSError, RuntimeError, ValueError) as exc:
            messagebox.showerror("讀取套件失敗", str(exc))
            self.set_status("讀取套件失敗")
            return

        PackageListDialog(self.master, self.selected_venv.name, packages, saved_path)
        self.set_status(f"已讀取 {len(packages)} 個套件，並輸出 {saved_path.name}")

    def copy_activation_command(self) -> None:
        if self.selected_venv is None:
            return
        command = self.get_activation_command_for_venv(self.selected_venv)
        self.master.clipboard_clear()
        self.master.clipboard_append(command)
        self.set_status("已複製啟用指令")

    def open_settings(self) -> None:
        self.set_status("正在掃描 Base Python...")
        self.master.update_idletasks()
        dialog = SettingsDialog(self.master, self.config, self.service.discover_base_pythons())
        if dialog.result is None:
            self.set_status("就緒")
            return

        self.config = AppConfig(
            venv_root=dialog.result.venv_root,
            base_python=dialog.result.base_python,
            theme=self.config.theme,
            venv_workdirs=self.config.venv_workdirs,
            last_open_dir=self.config.last_open_dir,
        )
        if not self.save_config():
            return
        self.refresh_venvs()
        self.set_status("已儲存設定")

    def save_requirements_snapshot(self, venv: VenvInfo, packages: list[str]) -> Path:
        filename = f"{venv.name}_requirements_python_{venv.python_version}.txt"
        output_path = Path(self.config.venv_root) / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("\n".join(packages), encoding="utf-8")
        return output_path

    def get_workdir_key(self, venv: VenvInfo) -> str:
        return str(venv.path)

    def get_workdir_for_venv(self, venv: VenvInfo) -> Path | None:
        value = self.config.venv_workdirs.get(self.get_workdir_key(venv))
        if not value:
            return None
        return Path(value)

    def get_activation_command_for_venv(self, venv: VenvInfo) -> str:
        activate = self.service.get_activation_command(venv.path)
        workdir = self.get_workdir_for_venv(venv)
        if not workdir:
            return activate
        quoted_workdir = "'" + str(workdir).replace("'", "''") + "'"
        return f"Set-Location -LiteralPath {quoted_workdir}; {activate}"

    def save_config(self) -> bool:
        try:
            self.config_store.save(self.config)
        except OSError as exc:
            messagebox.showerror("儲存設定失敗", f"{exc}\n\n設定檔位置：{get_config_path()}")
            self.set_status("儲存設定失敗")
            return False
        return True

    def set_status(self, message: str) -> None:
        self.status_var.set(message)
