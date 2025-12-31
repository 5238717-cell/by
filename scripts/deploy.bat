@echo off
REM ============================================
REM 一键部署脚本 - Windows
REM ============================================

chcp 65001 >nul
setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."
cd /d "%PROJECT_ROOT%"

REM 打印头部
:print_header
echo.
echo ========================================
echo   %~1
echo ========================================
echo.
goto :eof

REM 打印成功消息
:print_success
echo [√] %~1
goto :eof

REM 打印错误消息
:print_error
echo [×] %~1
goto :eof

REM 打印警告消息
:print_warning
echo [!] %~1
goto :eof

REM 打印信息消息
:print_info
echo [i] %~1
goto :eof

REM 检查Python环境
:check_python
call :print_header "检查 Python 环境"

where python >nul 2>&1
if %errorlevel% neq 0 (
    call :print_error "未找到 Python，请先安装 Python 3.8+"
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set "python_version=%%i"
call :print_success "Python 版本: %python_version%"

call :print_success "Python 环境检查通过"
goto :eof

REM 检查并安装依赖
:install_dependencies
call :print_header "安装 Python 依赖"

if exist "requirements.txt" (
    call :print_info "正在安装依赖包..."
    pip install -r requirements.txt
    if %errorlevel% equ 0 (
        call :print_success "依赖安装完成"
    ) else (
        call :print_warning "依赖安装过程中出现警告或错误"
    )
) else (
    call :print_warning "未找到 requirements.txt 文件"
)
goto :eof

REM 检查配置文件
:check_config
call :print_header "检查配置文件"

set "config_needed=0"

REM 检查 agent 配置
if not exist "config\agent_llm_config.json" (
    call :print_warning "缺少 agent_llm_config.json"
    set "config_needed=1"
) else (
    call :print_success "找到 agent_llm_config.json"
)

REM 检查 webhook 配置
if not exist "config\webhook_config.json" (
    call :print_warning "缺少 webhook_config.json"
    set "config_needed=1"
) else (
    call :print_success "找到 webhook_config.json"
)

REM 如果需要配置，询问是否运行配置向导
if !config_needed! equ 1 (
    echo.
    set /p "run_config=是否运行配置向导? (y/n): "
    if /i "!run_config!"=="y" (
        call :print_info "启动配置向导..."
        python scripts\auto_init_config.py
        call :print_success "配置完成"
    ) else (
        call :print_warning "跳过配置向导，您需要手动创建配置文件"
    )
) else (
    call :print_success "配置文件检查完成"
)
goto :eof

REM 创建必要的目录
:create_directories
call :print_header "创建必要目录"

set "directories=assets logs config data"

for %%d in (%directories%) do (
    if not exist "%%d" (
        mkdir "%%d"
        call :print_success "创建目录: %%d"
    ) else (
        call :print_success "目录已存在: %%d"
    )
)
goto :eof

REM 显示菜单
:show_menu
call :print_header "请选择要启动的服务"

echo 1) 启动 Webhook 服务器
echo 2) 启动 Web UI 配置管理系统
echo 3) 启动多 Agent 协作系统
echo 4) 查看系统状态
echo 5) 运行测试
echo 6) 查看日志
echo 7) 停止所有服务
echo 8) 退出
echo.
set /p "choice=请输入选项 (1-8): "

if "%choice%"=="1" goto :start_webhook
if "%choice%"=="2" goto :start_webui
if "%choice%"=="3" goto :start_multiagent
if "%choice%"=="4" goto :check_status
if "%choice%"=="5" goto :run_tests
if "%choice%"=="6" goto :view_logs
if "%choice%"=="7" goto :stop_services
if "%choice%"=="8" goto :exit_script

call :print_error "无效选项，请重新选择"
echo.
goto :show_menu

:start_webhook
echo.
call :print_info "启动 Webhook 服务器..."
python src\webhook_server.py
goto :show_menu

:start_webui
echo.
call :print_info "启动 Web UI 配置管理系统..."
call scripts\start_web_ui.bat
goto :show_menu

:start_multiagent
echo.
call :print_info "启动多 Agent 协作系统..."
python src\main_multiagent.py
goto :show_menu

:check_status
echo.
call :print_info "系统状态检查..."

echo 配置文件状态:
if exist "config\agent_llm_config.json" (
    call :print_success "agent_llm_config.json"
) else (
    call :print_error "agent_llm_config.json (缺失)"
)

if exist "config\webhook_config.json" (
    call :print_success "webhook_config.json"
) else (
    call :print_error "webhook_config.json (缺失)"
)

echo.
echo 关键依赖状态:
python -c "import langchain" >nul 2>&1
if %errorlevel% equ 0 (
    call :print_success "langchain"
) else (
    call :print_error "langchain (未安装)"
)

python -c "import langgraph" >nul 2>&1
if %errorlevel% equ 0 (
    call :print_success "langgraph"
) else (
    call :print_error "langgraph (未安装)"
)

python -c "import fastapi" >nul 2>&1
if %errorlevel% equ 0 (
    call :print_success "fastapi"
) else (
    call :print_error "fastapi (未安装)"
)

python -c "import lark_oapi" >nul 2>&1
if %errorlevel% equ 0 (
    call :print_success "lark_oapi"
) else (
    call :print_error "lark_oapi (未安装)"
)

goto :show_menu

:run_tests
echo.
call :print_info "运行测试..."
python -m pytest tests\
call :print_success "测试完成"
pause
goto :show_menu

:view_logs
echo.
call :print_info "查看日志..."
if exist "logs" (
    echo 可用的日志文件:
    echo.
    dir /b logs\*.log 2>nul
    if %errorlevel% neq 0 (
        call :print_warning "未找到日志文件"
    )
) else (
    call :print_warning "日志目录不存在"
)
echo.
pause
goto :show_menu

:stop_services
echo.
call :print_info "停止所有服务..."
taskkill /f /im python.exe >nul 2>&1
call :print_success "已停止所有 Python 进程"
goto :show_menu

:exit_script
echo.
call :print_success "退出部署系统"
pause
exit /b 0

REM 主函数
:main
cls

call :print_header "🚀 飞书多 Agent 协作系统 - 一键部署"

echo 系统信息:
echo   项目目录: %PROJECT_ROOT%
echo   操作系统: Windows
for /f "tokens=2" %%i in ('python --version 2^>^&1') do echo   Python 版本: %%i
echo.

REM 执行部署步骤
call :check_python
call :install_dependencies
call :create_directories
call :check_config

call :print_header "🎉 部署准备完成！"

echo.
echo 接下来您可以选择启动的服务：
echo.

REM 显示菜单
call :show_menu

goto :eof

REM 运行主函数
call :main
