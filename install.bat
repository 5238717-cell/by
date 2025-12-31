@echo off
REM ============================================
REM 一键安装脚本 - 从代码仓库自动部署 (Windows)
REM ============================================
REM
REM 使用方法:
REM 1. 打开浏览器访问: https://raw.githubusercontent.com/your-repo/main/install.bat
REM 2. 保存为 install.bat
REM 3. 双击运行
REM
REM ============================================

chcp 65001 >nul
setlocal enabledelayedexpansion

REM 项目配置（需要根据实际情况修改）
set "REPO_URL=https://github.com/your-username/multi-agent-system.git"
set "PROJECT_DIR=multi-agent-system"
set "BRANCH=main"

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

REM 检查命令是否存在
:command_exists
where %~1 >nul 2>&1
goto :eof

REM 安装必要工具
:install_tools
call :print_header "安装必要工具"

call :command_exists git
if %errorlevel% neq 0 (
    call :print_error "未找到 Git，请先安装 Git"
    echo.
    echo 请从以下地址下载并安装 Git:
    echo https://git-scm.com/download/win
    echo.
    pause
    exit /b 1
)

call :print_success "Git 已安装"
goto :eof

REM 检查 Python 环境
:check_python
call :print_header "检查 Python 环境"

call :command_exists python
if %errorlevel% neq 0 (
    call :print_error "未找到 Python，请先安装 Python 3.8+"
    echo.
    echo 请从以下地址下载并安装 Python:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set "python_version=%%i"
call :print_success "Python 版本: %python_version%"
goto :eof

REM 克隆代码仓库
:clone_repo
call :print_header "克隆代码仓库"

REM 检查目录是否已存在
if exist "%PROJECT_DIR%" (
    call :print_warning "项目目录已存在: %PROJECT_DIR%"
    set /p "delete_dir=是否删除并重新克隆? (y/n): "
    if /i "!delete_dir!"=="y" (
        call :print_info "删除旧目录..."
        rmdir /s /q "%PROJECT_DIR%"
    ) else (
        call :print_info "跳过克隆，使用现有目录"
        cd /d "%PROJECT_DIR%"
        goto :eof
    )
)

call :print_info "从代码仓库克隆项目..."
git clone -b %BRANCH% "%REPO_URL%" "%PROJECT_DIR%"

if %errorlevel% equ 0 (
    call :print_success "代码克隆完成"
) else (
    call :print_error "代码克隆失败"
    pause
    exit /b 1
)

cd /d "%PROJECT_DIR%"
goto :eof

REM 安装依赖
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

REM 初始化配置
:init_config
call :print_header "初始化配置"

if not exist "config\webhook_config.json" (
    call :print_info "创建默认配置..."
    python scripts\auto_init_config.py
    call :print_success "配置初始化完成"
) else (
    call :print_success "配置已存在，跳过初始化"
)
goto :eof

REM 显示安装成功信息
:show_success
call :print_header "🎉 安装完成！"

echo.
echo ========================================
echo   项目信息
echo ========================================
echo.
echo   项目目录: %cd%
echo   Python 版本: %python_version%
echo.
echo ========================================
echo   快速启动
echo ========================================
echo.
echo   启动 Web UI (推荐):
echo     [√] scripts\quick_deploy.bat
echo.
echo   或者启动完整部署:
echo     [√] scripts\deploy.bat
echo.
echo ========================================
echo   文档
echo ========================================
echo.
echo   快速启动指南: QUICKSTART.md
echo   完整部署指南: DEPLOY.md
echo   部署文件总结: docs\DEPLOYMENT_SUMMARY.md
echo.
echo ========================================
echo.

REM 询问是否立即启动
set /p "start_ui=是否立即启动 Web UI? (y/n): "
if /i "!start_ui!"=="y" (
    echo.
    call :print_info "启动 Web UI..."
    call scripts\quick_deploy.bat
)
goto :eof

REM 主函数
:main
cls

call :print_header "🚀 飞书多 Agent 协作系统 - 一键安装"

echo 系统信息:
echo   操作系统: Windows
echo.

REM 执行安装步骤
call :install_tools
call :check_python
call :clone_repo
call :install_dependencies
call :init_config

REM 显示成功信息
call :show_success

pause
goto :eof

REM 运行主函数
call :main
