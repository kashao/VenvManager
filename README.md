# VenvManager
Python 3 Venv Manager

這個虛擬環境管理器是一個用 Python 和 tkinter 構建的圖形用戶界面（GUI）應用程式，它可以幫助你輕鬆管理虛擬環境和套件。你可以使用它來創建、刪除虛擬環境，安裝套件，查看已安裝的套件，以及執行其他相關任務。

## 功能

- 選擇虛擬環境資料夾
- 創建新的虛擬環境
- 刪除現有的虛擬環境
- 安裝單個套件
- 從文件中安裝多個套件
- 顯示虛擬環境中的 Python 版本
- 顯示虛擬環境中已安裝的套件
- 執行虛擬環境的 `activate.bat`

## 安裝

首先，確保你已經安裝了 Python。接著，使用以下步驟安裝虛擬環境管理器：

1. 安裝所需的依賴：

   ```bash
   pip install -r requirements.txt
   ```

2. 執行虛擬環境管理器：

   ```bash
   python VenvManger.py
   ```

## 使用

在虛擬環境管理器中，你可以進行以下操作：

- 點擊 "選擇虛擬環境資料夾" 按鈕以選擇虛擬環境的根目錄。
- 使用其他功能按鈕來執行相應的操作。

## 截圖

![Application](https://github.com/kashao/VenvManager/blob/main/Application.png)

### 待研究

我有試著打包起來，但不知道為何創建的功能無法正常使用。