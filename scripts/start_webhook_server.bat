@echo off
REM Webhook服务器启动脚本 (Windows)

echo =========================================
echo   交易信号Webhook服务器启动脚本
echo =========================================

REM 获取工作目录
set "WORKSPACE_PATH=%COZE_WORKSPACE_PATH%"
if "%WORKSPACE_PATH%"=="" set "WORKSPACE_PATH=C:\workspace\projects"
cd /d "%WORKSPACE_PATH%" || exit /b 1

echo 工作目录: %WORKSPACE_PATH%

REM 检查Python环境
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Python
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo Python版本: %PYTHON_VERSION%

REM 检查配置文件
set CONFIG_FILE=%WORKSPACE_PATH%\config\webhook_config.json
if not exist "%CONFIG_FILE%" (
    echo 错误: 未找到配置文件 %CONFIG_FILE%
    exit /b 1
)

echo 配置文件: %CONFIG_FILE%

REM 启动服务器
echo.
echo 正在启动Webhook服务器...
echo.

REM 启动webhook服务器
python -m src.webhook_server

echo.
echo Webhook服务器已停止

pause
