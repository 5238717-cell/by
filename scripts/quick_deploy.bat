@echo off
REM ============================================
REM 快速部署脚本 - 仅启动 Web UI（推荐新手）
REM ============================================

chcp 65001 >nul
setlocal enabledelayedexpansion

echo ==========================================
echo   快速部署 - Web UI 配置管理系统
echo ==========================================
echo.

set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."
cd /d "%PROJECT_ROOT%"

echo [1/4] 检查 Python 环境...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] 未找到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)
python --version
echo [√] Python 环境正常
echo.

echo [2/4] 安装依赖...
pip install -q -r requirements.txt
echo [√] 依赖安装完成
echo.

echo [3/4] 初始化配置...
if not exist "config\webhook_config.json" (
    echo 首次运行，创建默认配置...
    python scripts\auto_init_config.py 2>nul
)
echo [√] 配置初始化完成
echo.

echo [4/4] 启动 Web UI...
echo.
echo ==========================================
echo 🎉 部署完成！
echo ==========================================
echo.
echo 📱 访问地址: http://localhost:5000
echo.
echo 按 Ctrl+C 停止服务器
echo.
echo ==========================================
echo.

REM 启动 Web UI
python src\web_ui.py
