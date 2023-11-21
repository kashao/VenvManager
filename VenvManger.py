import os
import shutil
import subprocess
import tkinter as tk
from tkinter import simpledialog, filedialog, messagebox, ttk
from ttkbootstrap import Style

def create_venv(venv_name):
    try:
        # 使用 subprocess 創建虛擬環境
        subprocess.run(['python', '-m', 'venv', venv_name], shell=True)
        return True
    except Exception as e:
        return str(e)

def install_package(venv_name, package_name):
    try:
        # 使用虛擬環境的 activate 腳本啟動虛擬環境
        activate_script = os.path.join(venv_name, 'Scripts', 'activate')
        cmd = f'call {activate_script} && pip install {package_name}'
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.returncode == 0:
            return True
        else:
            return result.stderr
    except Exception as e:
        return str(e)

def get_python_version(venv_path):
    try:
        activate_script = os.path.join(venv_path, 'Scripts', 'activate')
        cmd = f'call {activate_script} && python --version'
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return "無法獲取版本信息"
    except Exception as e:
        return str(e)

def get_installed_packages(venv_path):
    try:
        activate_script = os.path.join(venv_path, 'Scripts', 'activate')
        cmd = f'call {activate_script} && pip freeze'
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            return result.stdout.strip().split('\n')
        else:
            return ["無法獲取已安裝的包"]
    except Exception as e:
        return str(e)

def select_directory():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        folder_var.set(folder_selected)  # 設置虛擬環境資料夾變數
        venv_list.delete(0, tk.END)  # 清空列表框
        for entry in os.listdir(folder_selected):
            if os.path.isdir(os.path.join(folder_selected, entry)):
                venv_list.insert(tk.END, entry)

def create_venv_gui():
    selected_dir = folder_var.get()
    if selected_dir:
        venv_name = simpledialog.askstring("創建虛擬環境", "請輸入虛擬環境的名稱:")
        if venv_name:
            result = create_venv(os.path.join(selected_dir, venv_name))
            if result is True:
                messagebox.showinfo("創建虛擬環境", f"已成功創建虛擬環境 '{venv_name}'")
                # 創建成功後自動更新虛擬環境列表
                update_venv_list()
            else:
                messagebox.showerror("創建虛擬環境", f"創建虛擬環境 '{venv_name}' 時出錯:\n{result}")

def delete_venv_gui():
    selected_dir = folder_var.get()
    selected_indices = venv_list.curselection()  # 獲得選擇的索引列表
    if not selected_indices:
        messagebox.showinfo("已安裝的包", "請選擇一個虛擬環境")
        return  # 如果未選擇虛擬環境，就不執行後面的程式碼
    selected_venv = venv_list.get(venv_list.curselection())
    if selected_dir and selected_venv:
        confirm_delete = messagebox.askyesno("刪除虛擬環境", f"確定要刪除虛擬環境 '{selected_venv}' 嗎？")
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
    if selected_dir:
        venv_list.delete(0, tk.END)  # 清空虛擬環境列表
        venv_folders = [folder for folder in os.listdir(selected_dir) if os.path.isdir(os.path.join(selected_dir, folder))]
        venv_list.insert(tk.END, *venv_folders)

def install_package_gui():
    selected_dir = folder_var.get()
    selected_indices = venv_list.curselection()  # 獲得選擇的索引列表
    if not selected_indices:
        messagebox.showinfo("已安裝的包", "請選擇一個虛擬環境")
        return  # 如果未選擇虛擬環境，就不執行後面的程式碼
    selected_venv = venv_list.get(venv_list.curselection())
    if selected_dir and selected_venv:
        package_name = simpledialog.askstring("安裝包", "請輸入要安裝的包的名稱 (可指定版本，例如 package==1.0.0):")
        if package_name:
            result = install_package(os.path.join(selected_dir, selected_venv), package_name)
            if result is True:
                python_version = get_python_version(os.path.join(selected_dir, selected_venv))
                installed_packages = get_installed_packages(os.path.join(selected_dir, selected_venv))
                messagebox.showinfo("安裝包", f"已成功在虛擬環境 '{selected_venv}' 中安裝包 '{package_name}'\nPython 版本: {python_version}\n已安裝的包:\n{', '.join(installed_packages)}")
            else:
                messagebox.showerror("安裝包", f"安裝包時出錯:\n{result}")

def install_packages_from_file():
    selected_dir = folder_var.get()
    selected_indices = venv_list.curselection()  # 獲得選擇的索引列表
    if not selected_indices:
        messagebox.showinfo("已安裝的包", "請選擇一個虛擬環境")
        return  # 如果未選擇虛擬環境，就不執行後面的程式碼
    selected_venv = venv_list.get(venv_list.curselection())
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
                completion_message = f"已成功在虛擬環境 '{selected_venv}' 中安裝套件\nPython 版本: {python_version}\n已安裝的套件:\n{', '.join(installed_packages)}"
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
    selected_dir = folder_var.get()
    selected_indices = venv_list.curselection()  # 獲得選擇的索引列表
    if not selected_indices:
        messagebox.showinfo("已安裝的包", "請選擇一個虛擬環境")
        return  # 如果未選擇虛擬環境，就不執行後面的程式碼
    selected_venv = venv_list.get(venv_list.curselection())
    if selected_dir and selected_venv:
        python_version = get_python_version(os.path.join(selected_dir, selected_venv))
        messagebox.showinfo("Python 版本", f"虛擬環境 '{selected_venv}' 的 Python 版本:\n{python_version}")

def show_installed_packages_gui():
    selected_dir = folder_var.get()
    selected_indices = venv_list.curselection()  # 獲得選擇的索引列表
    if not selected_indices:
        messagebox.showinfo("已安裝的包", "請選擇一個虛擬環境")
        return  # 如果未選擇虛擬環境，就不執行後面的程式碼

    selected_venv = venv_list.get(selected_indices[0])  # 獲得第一個選擇的虛擬環境
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
    selected_dir = folder_var.get()
    selected_indices = venv_list.curselection()  # 獲得選擇的索引列表
    if not selected_indices:
        messagebox.showinfo("已安裝的包", "請選擇一個虛擬環境")
        return  # 如果未選擇虛擬環境，就不執行後面的程式碼
    selected_venv = venv_list.get(venv_list.curselection())

    if selected_dir and selected_venv:
        activate_path = os.path.join(selected_dir, selected_venv, 'Scripts', 'activate.bat')
        if os.path.exists(activate_path):
            try:
                subprocess.Popen(['start', 'cmd', '/k', activate_path], shell=True)
                messagebox.showinfo("執行 activate.bat", f"已成功在新的命令提示字元窗口中執行 '{activate_path}'")
            except Exception as e:
                messagebox.showerror("執行 activate.bat", f"執行 '{activate_path}' 時出錯:\n{str(e)}")
        else:
            messagebox.showinfo("執行 activate.bat", f"'{activate_path}' 不存在")
            
if __name__ == "__main__":

    root = tk.Tk()
    root.title("虛擬環境管理器")

    style = Style(theme="flatly")  # 使用 flatly 主題
    root.geometry("500x500")  # 設定視窗大小

    folder_var = tk.StringVar()  # 初始化 folder_var
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
    select_folder_button = ttk.Button(side_frame, text="選擇虛擬環境資料夾", command=select_directory, width=button_width, style="TButton")
    select_folder_button.pack(pady=2, padx=5)

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

    root.mainloop()
