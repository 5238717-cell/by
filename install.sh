#!/bin/bash
# ============================================
# 一键安装脚本 - 从代码仓库自动部署
# ============================================
#
# 使用方法:
# curl -fsSL https://raw.githubusercontent.com/your-repo/main/install.sh | bash
# 或
# wget -qO- https://raw.githubusercontent.com/your-repo/main/install.sh | bash
#
# ============================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 项目配置
REPO_URL="https://github.com/5238717-cell/by.git"
PROJECT_DIR="by"
BRANCH="main"

# 打印带颜色的消息
print_header() {
    echo ""
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}========================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 安装必要工具
install_tools() {
    print_header "安装必要工具"

    if ! command_exists git; then
        print_info "安装 Git..."
        if command_exists apt-get; then
            apt-get update && apt-get install -y git
        elif command_exists yum; then
            yum install -y git
        elif command_exists brew; then
            brew install git
        else
            print_error "无法自动安装 Git，请手动安装后重试"
            exit 1
        fi
        print_success "Git 安装完成"
    else
        print_success "Git 已安装"
    fi
}

# 检查 Python 环境
check_python() {
    print_header "检查 Python 环境"

    if ! command_exists python3; then
        print_error "未找到 Python 3，请先安装 Python 3.8+"
        echo ""
        echo "Ubuntu/Debian: sudo apt-get install python3.8"
        echo "CentOS/RHEL: sudo yum install python38"
        echo "macOS: brew install python@3.8"
        exit 1
    fi

    python_version=$(python3 --version 2>&1 | awk '{print $2}')
    print_success "Python 版本: $python_version"

    # 检查版本
    major_version=$(echo $python_version | cut -d. -f1)
    minor_version=$(echo $python_version | cut -d. -f2)

    if [ "$major_version" -lt 3 ] || ([ "$major_version" -eq 3 ] && [ "$minor_version" -lt 8 ]); then
        print_error "Python 版本过低，需要 Python 3.8 或更高版本"
        exit 1
    fi

    print_success "Python 环境检查通过"
}

# 克隆代码仓库
clone_repo() {
    print_header "克隆代码仓库"

    # 检查目录是否已存在
    if [ -d "$PROJECT_DIR" ]; then
        print_warning "项目目录已存在: $PROJECT_DIR"
        read -p "$(echo -e ${YELLOW}是否删除并重新克隆? (y/n): ${NC})" -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_info "删除旧目录..."
            rm -rf "$PROJECT_DIR"
        else
            print_info "跳过克隆，使用现有目录"
            cd "$PROJECT_DIR"
            return 0
        fi
    fi

    print_info "从代码仓库克隆项目..."
    git clone -b "$BRANCH" "$REPO_URL" "$PROJECT_DIR"

    if [ $? -eq 0 ]; then
        print_success "代码克隆完成"
    else
        print_error "代码克隆失败"
        exit 1
    fi

    cd "$PROJECT_DIR"
}

# 安装依赖
install_dependencies() {
    print_header "安装 Python 依赖"

    if [ -f "requirements.txt" ]; then
        print_info "正在安装依赖包..."
        pip3 install -r requirements.txt

        if [ $? -eq 0 ]; then
            print_success "依赖安装完成"
        else
            print_warning "依赖安装过程中出现警告或错误，但继续执行..."
        fi
    else
        print_warning "未找到 requirements.txt 文件"
    fi
}

# 初始化配置
init_config() {
    print_header "初始化配置"

    if [ ! -f "config/webhook_config.json" ]; then
        print_info "创建默认配置..."
        python3 scripts/auto_init_config.py
        print_success "配置初始化完成"
    else
        print_success "配置已存在，跳过初始化"
    fi
}

# 显示安装成功信息
show_success() {
    print_header "🎉 安装完成！"

    echo ""
    echo "=========================================="
    echo "  项目信息"
    echo "=========================================="
    echo ""
    echo "  项目目录: $(pwd)"
    echo "  Python 版本: $(python3 --version)"
    echo ""
    echo "=========================================="
    echo "  快速启动"
    echo "=========================================="
    echo ""
    echo "  启动 Web UI (推荐):"
    echo -e "    ${GREEN}./scripts/quick_deploy.sh${NC}"
    echo ""
    echo "  或者启动完整部署:"
    echo -e "    ${GREEN}./scripts/deploy.sh${NC}"
    echo ""
    echo "=========================================="
    echo "  文档"
    echo "=========================================="
    echo ""
    echo "  快速启动指南: ${CYAN}QUICKSTART.md${NC}"
    echo "  完整部署指南: ${CYAN}DEPLOY.md${NC}"
    echo "  部署文件总结: ${CYAN}docs/DEPLOYMENT_SUMMARY.md${NC}"
    echo ""
    echo "=========================================="
    echo ""
}

# 主函数
main() {
    clear

    print_header "🚀 飞书多 Agent 协作系统 - 一键安装"

    echo "系统信息:"
    echo "  操作系统: $(uname -s)"
    echo "  架构: $(uname -m)"
    echo ""

    # 执行安装步骤
    install_tools
    check_python
    clone_repo
    install_dependencies
    init_config

    # 显示成功信息
    show_success

    # 询问是否立即启动
    echo ""
    read -p "$(echo -e ${YELLOW}是否立即启动 Web UI? (y/n): ${NC})" -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        print_info "启动 Web UI..."
        ./scripts/quick_deploy.sh
    fi
}

# 捕获 Ctrl+C
trap 'echo ""; print_warning "安装已中断"; exit 1' INT

# 运行主函数
main
