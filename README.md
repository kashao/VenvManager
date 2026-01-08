# VenvManager
Python 3 虛擬環境管理器

這個虛擬環境管理器是一個用 Python 和 tkinter 構建的圖形用戶界面（GUI）應用程式，它可以幫助你輕鬆管理虛擬環境與套件，包括建立/刪除虛擬環境、安裝套件、檢視已安裝套件與執行啟用腳本。

---

# VenvManager (English)
VenvManager is a Python + tkinter GUI app for managing virtual environments and packages. You can create or remove environments, install packages, inspect installed packages, and launch the activation script.

## 功能 (Features)

- 選擇虛擬環境資料夾
- 創建新的虛擬環境
- 刪除現有的虛擬環境
- 安裝單個套件
- 從文件中安裝多個套件
- 顯示虛擬環境中的 Python 版本
- 顯示虛擬環境中已安裝的套件
- 執行虛擬環境的 `activate.bat`
- 設定 Base Python 來源（`py -<version>` 或 `python.exe` 路徑）
- 針對不同 Profile 儲存獨立的虛擬環境根目錄與工作目錄設定

- Select a venv root folder
- Create new virtual environments
- Delete existing environments
- Install packages (single or batch from file)
- Show Python version and installed packages
- Run `activate.bat`
- Configure Base Python source (`py -<version>` or `python.exe` path)
- Save per-profile venv roots and working directory preferences

## 安裝 (Installation)

首先，確保你已經安裝了 Python。接著，使用以下步驟安裝虛擬環境管理器：

1. 安裝所需的依賴：

   ```bash
   pip install -r requirements.txt
   ```

2. 執行虛擬環境管理器：

   ```bash
   python VenvManager.py
   ```

## 使用 (Usage)

在虛擬環境管理器中，你可以進行以下操作：

- 點擊 "選擇虛擬環境資料夾" 按鈕以選擇虛擬環境的根目錄。
- 使用其他功能按鈕來執行相應的操作。

## 截圖 (Screenshot)

![Application](Application.png)
