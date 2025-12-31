@echo off
REM Web UI 启动脚本 (Windows)

setlocal

echo ========================================
echo   Webhook Web UI 配置管理系统
echo ========================================
echo.

echo 正在启动 Web UI 服务器...
echo.

REM 检查 Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] 未找到 Python，请先安装 Python 3.7+
    pause
    exit /b 1
)

REM 显示 Python 版本
python --version
echo.

REM 检查并安装依赖
echo 检查依赖...
python -c "import fastapi" >nul 2>&1
if %errorlevel% neq 0 (
    echo 未找到 fastapi，正在安装...
    pip install fastapi uvicorn jinja2
)

echo.
echo ========================================
echo 🚀 Web UI 服务器启动成功！
echo ========================================
echo.
echo 访问地址:
echo   http://localhost:5000
echo.
echo API 文档:
echo   http://localhost:5000/api/config
echo.
echo 按 Ctrl+C 停止服务器
echo.
echo ========================================
echo.

REM 切换到项目根目录
cd /d "%~dp0.."

REM 启动服务器
python src\web_ui.py

pause
