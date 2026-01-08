import os
import shutil
import subprocess
import tkinter as tk
from tkinter import simpledialog, filedialog, messagebox, ttk

from ttkbootstrap import Style

from config_utils import load_config, save_config

config_data = {}


def get_selected_venv(show_warning=True):
    selected_dir = folder_var.get()
    selected_indices = venv_list.curselection()
    if not selected_indices:
        if show_warning:
            messagebox.showinfo("已安裝的包", "請選擇一個虛擬環境")
        return None, None
    selected_venv = venv_list.get(selected_indices[0])
    return selected_dir, selected_venv

def ensure_profile(name):
    profiles = config_data.setdefault("profiles", {})
    if name not in profiles:
        profiles[name] = {"venv_root": "", "activate_workdir": ""}
    return profiles[name]

def get_active_profile():
    profile_name = config_data.get("active_profile", "default")
    return ensure_profile(profile_name)

def get_base_python_command(cfg):
    base_python = cfg.get("base_python", {})
    if base_python.get("mode") == "path":
        return [base_python.get("path", "")]
    return ["py", f"-{base_python.get('py_version', '3.11')}"]

def create_venv(cfg, venv_dir):
    try:
        cmd = get_base_python_command(cfg) + ["-m", "venv", venv_dir]
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        return e.stderr or e.stdout or str(e)
    except Exception as e:
        return str(e)

def get_venv_python(venv_path):
    return os.path.join(venv_path, "Scripts", "python.exe")

def install_package(venv_name, package_name):
    try:
        venv_python = get_venv_python(venv_name)
        result = subprocess.run(
            [venv_python, "-m", "pip", "install", package_name],
            check=True,
            capture_output=True,
            text=True,
        )
        return True if result.returncode == 0 else result.stderr
    except subprocess.CalledProcessError as e:
        return e.stderr or e.stdout or str(e)
    except Exception as e:
        return str(e)

def get_python_version(venv_path):
    try:
        venv_python = get_venv_python(venv_path)
        result = subprocess.run(
            [venv_python, "--version"],
            check=True,
            capture_output=True,
            text=True,
        )
        output = (result.stdout or result.stderr).strip()
        return output if output else "無法獲取版本信息"
    except subprocess.CalledProcessError as e:
        return e.stderr or e.stdout or "無法獲取版本信息"
    except Exception as e:
        return str(e)

def get_installed_packages(venv_path):
    try:
        venv_python = get_venv_python(venv_path)
        result = subprocess.run(
            [venv_python, "-m", "pip", "freeze"],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip().split("\n") if result.stdout else []
    except subprocess.CalledProcessError as e:
        return [e.stderr or e.stdout or "無法獲取已安裝的包"]
    except Exception as e:
        return [str(e)]

def select_directory():
    default_open_dir = config_data.get("ui", {}).get("default_open_dir") or None
    folder_selected = filedialog.askdirectory(initialdir=default_open_dir)
    if folder_selected:
        folder_var.set(folder_selected)  # 設置虛擬環境資料夾變數
        active_profile = get_active_profile()
        active_profile["venv_root"] = folder_selected
        config_data.setdefault("ui", {})["default_open_dir"] = folder_selected
        save_config(config_data)
        update_venv_list()

def create_venv_gui():
    selected_dir = folder_var.get()
    if selected_dir:
        venv_name = simpledialog.askstring("創建虛擬環境", "請輸入虛擬環境的名稱:")
        if venv_name:
            result = create_venv(config_data, os.path.join(selected_dir, venv_name))
            if result is True:
                messagebox.showinfo("創建虛擬環境", f"已成功創建虛擬環境 '{venv_name}'")
                # 創建成功後自動更新虛擬環境列表
                update_venv_list()
            else:
                messagebox.showerror("創建虛擬環境", f"創建虛擬環境 '{venv_name}' 時出錯:\n{result}")

def delete_venv_gui():
    selected_dir, selected_venv = get_selected_venv()
    if selected_dir and selected_venv:
        confirm_delete = messagebox.askyesno(
            "刪除虛擬環境",
            f"確定要刪除虛擬環境 '{selected_venv}' 嗎？",
        )
        if confirm_delete:
            try:
                venv_path = os.path.join(selected_dir, selected_venv)
                # 在 Windows 上使用 os.remove 刪除檔案，shutil.rmtree 刪除資料夾
                if os.path.isfile(venv_path):
                    os.remove(venv_path)
                elif os.path.isdir(venv_path):
                    shutil.rmtree(venv_path)
                messagebox.showinfo("刪除虛擬環境", f"已成功刪除虛擬環境 '{selected_venv}'")
                # 刪除成功後自動更新虛擬環境列表
                update_venv_list()
            except Exception as e:
                messagebox.showerror("刪除虛擬環境", f"刪除虛擬環境 '{selected_venv}' 時出錯:\n{str(e)}")

# 創建一個函數來更新虛擬環境列表
def update_venv_list():
    selected_dir = folder_var.get()
    venv_list.delete(0, tk.END)  # 清空虛擬環境列表
    if selected_dir:
        venv_folders = [
            folder
            for folder in os.listdir(selected_dir)
            if os.path.isdir(os.path.join(selected_dir, folder))
        ]
        venv_list.insert(tk.END, *venv_folders)

def install_package_gui():
    selected_dir, selected_venv = get_selected_venv()
    if selected_dir and selected_venv:
        package_name = simpledialog.askstring(
            "安裝包",
            "請輸入要安裝的包的名稱 (可指定版本，例如 package==1.0.0):",
        )
        if package_name:
            result = install_package(os.path.join(selected_dir, selected_venv), package_name)
            if result is True:
                python_version = get_python_version(os.path.join(selected_dir, selected_venv))
                installed_packages = get_installed_packages(os.path.join(selected_dir, selected_venv))
                messagebox.showinfo(
                    "安裝包",
                    (
                        f"已成功在虛擬環境 '{selected_venv}' 中安裝包 '{package_name}'\n"
                        f"Python 版本: {python_version}\n"
                        f"已安裝的包:\n{', '.join(installed_packages)}"
                    ),
                )
            else:
                messagebox.showerror("安裝包", f"安裝包時出錯:\n{result}")

def install_packages_from_file():
    selected_dir, selected_venv = get_selected_venv()
    if selected_dir and selected_venv:
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    package_names = file.read().splitlines()
                total_packages = len(package_names)
                progress["maximum"] = 100  # 設置最大值為 100，代表百分比
                progress["value"] = 0  # 初始值為 0
                for i, package_name in enumerate(package_names, start=1):
                    result = install_package(os.path.join(selected_dir, selected_venv), package_name)
                    if result is True:
                        python_version = get_python_version(os.path.join(selected_dir, selected_venv))
                        installed_packages = get_installed_packages(os.path.join(selected_dir, selected_venv))
                    else:
                        messagebox.showerror("安裝包", f"安裝包 '{package_name}' 時出錯:\n{result}")
                    # 計算完成百分比並設置進度條的值
                    progress["value"] = (i / total_packages) * 100
                    progress.update()  # 更新進度條
                # 安裝完成後顯示訊息並等待用戶關閉窗口
                completion_window = tk.Toplevel(root)
                completion_window.title("安裝完成")
                completion_message = (
                    f"已成功在虛擬環境 '{selected_venv}' 中安裝套件\n"
                    f"Python 版本: {python_version}\n"
                    f"已安裝的套件:\n{', '.join(installed_packages)}"
                )
                tk.Label(completion_window, text=completion_message).pack()
                completion_window.protocol("WM_DELETE_WINDOW", lambda: on_completion_window_close(completion_window))
                completion_window.transient(root)
                completion_window.grab_set()
            except Exception as e:
                messagebox.showerror("安裝包", f"讀取文件時出錯:\n{str(e)}")

def on_completion_window_close(window):
    window.destroy()
    progress.stop()  # 停止進度條動畫


def show_python_version_gui():
    selected_dir, selected_venv = get_selected_venv()
    if selected_dir and selected_venv:
        python_version = get_python_version(os.path.join(selected_dir, selected_venv))
        messagebox.showinfo("Python 版本", f"虛擬環境 '{selected_venv}' 的 Python 版本:\n{python_version}")

def show_installed_packages_gui():
    selected_dir, selected_venv = get_selected_venv()
    if selected_venv:
        installed_packages = get_installed_packages(os.path.join(selected_dir, selected_venv))
        if installed_packages:
            python_version = get_python_version(os.path.join(selected_dir, selected_venv))
            file_name = f'{selected_venv}_requirements_python_{python_version}.txt'
            save_file_path = os.path.join(selected_dir, file_name)
            with open(save_file_path, 'w') as file:
                file.write('\n'.join(installed_packages))
            # 在訊息框中顯示較美觀的格式
            formatted_packages = '\n\n'.join(installed_packages)
            messagebox.showinfo("已安裝的包", f"已成功將已安裝的包保存到 '{file_name}' 文件中:\n\n{formatted_packages}")
        else:
            messagebox.showinfo("已安裝的包", "虛擬環境中未安裝任何包")
            
def run_activate_batch():
    selected_dir, selected_venv = get_selected_venv()
    if selected_dir and selected_venv:
        activate_path = os.path.join(selected_dir, selected_venv, 'Scripts', 'activate.bat')
        if os.path.exists(activate_path):
            try:
                active_profile = get_active_profile()
                workdir_map = active_profile.get("activate_workdirs", {})
                workdir = workdir_map.get(selected_venv) or active_profile.get("activate_workdir", "")
                if workdir:
                    inner = f'cd /d "{workdir}" && call "{activate_path}"'
                else:
                    inner = f'call "{activate_path}"'
                subprocess.Popen(
                    ["cmd.exe", "/K", inner],
                    creationflags=subprocess.CREATE_NEW_CONSOLE,
                )
                messagebox.showinfo("執行 activate.bat", f"已成功在新的命令提示字元窗口中執行 '{activate_path}'")
            except Exception as e:
                messagebox.showerror("執行 activate.bat", f"執行 '{activate_path}' 時出錯:\n{str(e)}")
        else:
            messagebox.showinfo("執行 activate.bat", f"'{activate_path}' 不存在")
            
if __name__ == "__main__":

    config_data = load_config()

    root = tk.Tk()
    root.title("虛擬環境管理器")

    style = Style(theme="flatly")  # 使用 flatly 主題
    root.geometry("500x500")  # 設定視窗大小

    folder_var = tk.StringVar()  # 初始化 folder_var
    profile_var = tk.StringVar(value=config_data.get("active_profile", "default"))
    base_mode_var = tk.StringVar(value=config_data.get("base_python", {}).get("mode", "py"))
    base_version_var = tk.StringVar(value=config_data.get("base_python", {}).get("py_version", "3.11"))
    base_path_var = tk.StringVar(value=config_data.get("base_python", {}).get("path", ""))
    progress = ttk.Progressbar(root, mode="determinate")
    progress.pack(fill="x")
    # 使用 Frame 分隔按鈕和 Listbox
    side_frame = ttk.Frame(root)
    side_frame.pack(side="left", fill="y")

    list_frame = ttk.Frame(root)
    list_frame.pack(side="right", fill="both", expand=True)

    # 按鈕的統一寬度
    button_width = 20

    # 創建按鈕並設置樣式
    profile_label = ttk.Label(side_frame, text="Profile")
    profile_label.pack(pady=(2, 0), padx=5)

    profile_combo = ttk.Combobox(
        side_frame,
        textvariable=profile_var,
        values=list(config_data.get("profiles", {}).keys()),
        state="readonly",
        width=button_width - 2,
    )
    profile_combo.pack(pady=2, padx=5)

    def on_profile_change(event=None):
        selected_profile = profile_var.get()
        ensure_profile(selected_profile)
        config_data["active_profile"] = selected_profile
        folder_var.set(get_active_profile().get("venv_root", ""))
        update_venv_list()
        save_config(config_data)

    profile_combo.bind("<<ComboboxSelected>>", on_profile_change)

    select_folder_button = ttk.Button(side_frame, text="選擇虛擬環境資料夾", command=select_directory, width=button_width, style="TButton")
    select_folder_button.pack(pady=2, padx=5)

    def set_activate_workdir():
        selected_indices = venv_list.curselection()
        if not selected_indices:
            messagebox.showinfo("設定工作目錄", "請先選擇一個虛擬環境")
            return
        selected_venv = venv_list.get(selected_indices[0])
        default_open_dir = config_data.get("ui", {}).get("default_open_dir") or None
        selected_dir = filedialog.askdirectory(initialdir=default_open_dir)
        if selected_dir:
            active_profile = get_active_profile()
            active_profile.setdefault("activate_workdirs", {})[selected_venv] = selected_dir
            config_data.setdefault("ui", {})["default_open_dir"] = selected_dir
            save_config(config_data)
            messagebox.showinfo("設定工作目錄", f"已更新 '{selected_venv}' 的工作目錄為:\n{selected_dir}")

    def clear_activate_workdir():
        selected_indices = venv_list.curselection()
        if not selected_indices:
            messagebox.showinfo("設定工作目錄", "請先選擇一個虛擬環境")
            return
        selected_venv = venv_list.get(selected_indices[0])
        active_profile = get_active_profile()
        workdir_map = active_profile.setdefault("activate_workdirs", {})
        if selected_venv in workdir_map:
            del workdir_map[selected_venv]
            save_config(config_data)
            messagebox.showinfo("設定工作目錄", f"已清除 '{selected_venv}' 的工作目錄設定。")
        else:
            messagebox.showinfo("設定工作目錄", f"'{selected_venv}' 尚未設定工作目錄。")

    activate_workdir_button = ttk.Button(
        side_frame,
        text="設定 activate 工作目錄",
        command=set_activate_workdir,
        width=button_width,
        style="TButton",
    )
    activate_workdir_button.pack(pady=2, padx=5)

    clear_activate_workdir_button = ttk.Button(
        side_frame,
        text="清除 activate 工作目錄",
        command=clear_activate_workdir,
        width=button_width,
        style="TButton",
    )
    clear_activate_workdir_button.pack(pady=2, padx=5)

    base_frame = ttk.LabelFrame(side_frame, text="Base Python", padding=5)
    base_frame.pack(pady=5, padx=5, fill="x")

    base_mode_combo = ttk.Combobox(
        base_frame,
        textvariable=base_mode_var,
        values=["py", "path"],
        state="readonly",
        width=button_width - 6,
    )
    base_mode_combo.pack(pady=2)

    base_version_entry = ttk.Entry(base_frame, textvariable=base_version_var)
    base_version_entry.pack(pady=2, fill="x")

    base_path_entry = ttk.Entry(base_frame, textvariable=base_path_var)
    base_path_entry.pack(pady=2, fill="x")

    def browse_base_python():
        file_path = filedialog.askopenfilename(filetypes=[("Python Executable", "python.exe")])
        if file_path:
            base_path_var.set(file_path)
            update_base_python_config()

    base_path_button = ttk.Button(base_frame, text="選擇 python.exe", command=browse_base_python, width=button_width - 6)
    base_path_button.pack(pady=2)

    def update_base_python_config():
        config_data["base_python"] = {
            "mode": base_mode_var.get(),
            "py_version": base_version_var.get().strip() or "3.11",
            "path": base_path_var.get().strip(),
        }
        save_config(config_data)
        update_base_python_ui_state()

    def update_base_python_ui_state():
        mode = base_mode_var.get()
        if mode == "py":
            base_version_entry.configure(state="normal")
            base_path_entry.configure(state="disabled")
            base_path_button.configure(state="disabled")
        else:
            base_version_entry.configure(state="disabled")
            base_path_entry.configure(state="normal")
            base_path_button.configure(state="normal")

    def test_base_python():
        update_base_python_config()
        cmd = get_base_python_command(config_data)
        cmd.append("--version")
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            output = (result.stdout or result.stderr).strip()
            messagebox.showinfo("Base Python 測試", output if output else "無法取得版本資訊")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Base Python 測試", e.stderr or e.stdout or str(e))
        except Exception as e:
            messagebox.showerror("Base Python 測試", str(e))

    base_test_button = ttk.Button(base_frame, text="Test --version", command=test_base_python, width=button_width - 6)
    base_test_button.pack(pady=2)

    base_mode_combo.bind("<<ComboboxSelected>>", lambda event: update_base_python_config())
    base_version_entry.bind("<FocusOut>", lambda event: update_base_python_config())
    base_path_entry.bind("<FocusOut>", lambda event: update_base_python_config())

    create_button = ttk.Button(side_frame, text="創建虛擬環境", command=create_venv_gui, width=button_width, style="TButton")
    create_button.pack(pady=2, padx=5)

    delete_venv_button = ttk.Button(side_frame, text="刪除虛擬環境", command=delete_venv_gui, width=button_width, style="TButton")
    delete_venv_button.pack(pady=2, padx=5)

    install_button = ttk.Button(side_frame, text="安裝包", command=install_package_gui, width=button_width, style="TButton")
    install_button.pack(pady=2, padx=5)

    install_from_file_button = ttk.Button(side_frame, text="安裝多個套件", command=install_packages_from_file, width=button_width, style="TButton")
    install_from_file_button.pack(pady=2, padx=5)

    show_python_version_button = ttk.Button(side_frame, text="顯示Python版本", command=show_python_version_gui, width=button_width, style="TButton")
    show_python_version_button.pack(pady=2, padx=5)

    show_installed_packages_button = ttk.Button(side_frame, text="顯示已安裝的包", command=show_installed_packages_gui, width=button_width, style="TButton")
    show_installed_packages_button.pack(pady=2, padx=5)

    run_activate_button = ttk.Button(side_frame, text="執行 activate.bat", command=run_activate_batch, width=button_width, style="TButton")
    run_activate_button.pack(pady=2, padx=5)

    quit_button = ttk.Button(side_frame, text="退出", command=root.quit, width=button_width, style="TButton")
    quit_button.pack(pady=2, padx=5)

    # 在 list_frame 中創建 venv_list
    venv_list = tk.Listbox(list_frame)
    venv_list.pack(fill='both', expand=True, padx=5, pady=5)

    folder_var.set(get_active_profile().get("venv_root", ""))
    update_base_python_ui_state()
    update_venv_list()

    root.mainloop()
