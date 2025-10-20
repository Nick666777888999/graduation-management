@echo off
chcp 65001
title 畢業資料管理系統

echo.
echo ========================================
echo        畢業資料管理系統啟動器
echo ========================================
echo.

:: 檢查 Python 是否安裝
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未檢測到 Python，請先安裝 Python
    echo 下載地址: https://www.python.org/downloads/
    pause
    exit
)

:: 初始化數據文件
echo 📁 初始化數據文件...
python init_data.py

:: 檢查依賴
if not exist "requirements.txt" (
    echo ❌ 缺少 requirements.txt
    pause
    exit
)

echo ✅ 檢查 Python... 已安裝
echo 📦 安裝依賴...
pip install -r requirements.txt

echo 🚀 啟動系統...
python start_system.py

pause