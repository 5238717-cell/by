#!/bin/bash
# ============================================
# 一键部署脚本 - Linux/Mac
# ============================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 项目根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "${PROJECT_ROOT}"

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

# 检查Python环境
check_python() {
    print_header "检查 Python 环境"
    
    if ! command -v python3 &> /dev/null; then
        print_error "未找到 Python 3，请先安装 Python 3.8+"
        exit 1
    fi
    
    python_version=$(python3 --version 2>&1 | awk '{print $2}')
    print_success "Python 版本: $python_version"
    
    # 检查Python版本是否满足要求
    major_version=$(echo $python_version | cut -d. -f1)
    minor_version=$(echo $python_version | cut -d. -f2)
    
    if [ "$major_version" -lt 3 ] || [ "$major_version" -eq 3 ] && [ "$minor_version" -lt 8 ]; then
        print_error "Python 版本过低，需要 Python 3.8 或更高版本"
        exit 1
    fi
    
    print_success "Python 环境检查通过"
}

# 检查并安装依赖
install_dependencies() {
    print_header "安装 Python 依赖"
    
    if [ -f "requirements.txt" ]; then
        print_info "正在安装依赖包..."
        pip install -r requirements.txt
        print_success "依赖安装完成"
    else
        print_warning "未找到 requirements.txt 文件"
    fi
}

# 检查配置文件
check_config() {
    print_header "检查配置文件"
    
    config_needed=false
    
    # 检查 agent 配置
    if [ ! -f "config/agent_llm_config.json" ]; then
        print_warning "缺少 agent_llm_config.json"
        config_needed=true
    else
        print_success "找到 agent_llm_config.json"
    fi
    
    # 检查 webhook 配置
    if [ ! -f "config/webhook_config.json" ]; then
        print_warning "缺少 webhook_config.json"
        config_needed=true
    else
        print_success "找到 webhook_config.json"
    fi
    
    # 如果需要配置，询问是否运行配置向导
    if [ "$config_needed" = true ]; then
        echo ""
        echo -e "${YELLOW}是否运行配置向导? (y/n): ${NC}\c"
        read run_config
        if [ "$run_config" = "y" ] || [ "$run_config" = "Y" ]; then
            print_info "启动配置向导..."
            python3 scripts/auto_init_config.py
            print_success "配置完成"
        else
            print_warning "跳过配置向导，您需要手动创建配置文件"
        fi
    else
        print_success "配置文件检查完成"
    fi
}

# 创建必要的目录
create_directories() {
    print_header "创建必要目录"
    
    directories=(
        "assets"
        "logs"
        "config"
        "data"
    )
    
    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_success "创建目录: $dir"
        else
            print_success "目录已存在: $dir"
        fi
    done
}

# 显示菜单
show_menu() {
    print_header "请选择要启动的服务"
    
    echo "1) 启动 Webhook 服务器"
    echo "2) 启动 Web UI 配置管理系统"
    echo "3) 启动多 Agent 协作系统"
    echo "4) 查看系统状态"
    echo "5) 运行测试"
    echo "6) 查看日志"
    echo "7) 停止所有服务"
    echo "8) 退出"
    echo ""
    read -p "请输入选项 (1-8): " choice
    
    case $choice in
        1)
            echo ""
            print_info "启动 Webhook 服务器..."
            python3 src/webhook_server.py
            ;;
        2)
            echo ""
            print_info "启动 Web UI 配置管理系统..."
            ./scripts/start_web_ui.sh
            ;;
        3)
            echo ""
            print_info "启动多 Agent 协作系统..."
            python3 src/main_multiagent.py
            ;;
        4)
            echo ""
            print_info "系统状态检查..."
            check_system_status
            show_menu
            ;;
        5)
            echo ""
            print_info "运行测试..."
            python3 -m pytest tests/
            print_success "测试完成"
            show_menu
            ;;
        6)
            echo ""
            print_info "查看日志..."
            show_logs
            show_menu
            ;;
        7)
            echo ""
            print_info "停止所有服务..."
            stop_all_services
            show_menu
            ;;
        8)
            echo ""
            print_success "退出部署系统"
            exit 0
            ;;
        *)
            print_error "无效选项，请重新选择"
            echo ""
            show_menu
            ;;
    esac
}

# 检查系统状态
check_system_status() {
    print_header "系统状态"
    
    # 检查配置文件
    echo "配置文件状态:"
    [ -f "config/agent_llm_config.json" ] && print_success "agent_llm_config.json" || print_error "agent_llm_config.json (缺失)"
    [ -f "config/webhook_config.json" ] && print_success "webhook_config.json" || print_error "webhook_config.json (缺失)"
    
    # 检查Python依赖
    echo ""
    echo "关键依赖状态:"
    python3 -c "import langchain" 2>/dev/null && print_success "langchain" || print_error "langchain (未安装)"
    python3 -c "import langgraph" 2>/dev/null && print_success "langgraph" || print_error "langgraph (未安装)"
    python3 -c "import fastapi" 2>/dev/null && print_success "fastapi" || print_error "fastapi (未安装)"
    python3 -c "import lark_oapi" 2>/dev/null && print_success "lark_oapi" || print_error "lark_oapi (未安装)"
    
    # 检查运行中的服务
    echo ""
    echo "运行中的服务:"
    if pgrep -f "webhook_server.py" > /dev/null; then
        print_success "Webhook 服务器 (运行中)"
    else
        print_warning "Webhook 服务器 (未运行)"
    fi
    
    if pgrep -f "web_ui.py" > /dev/null; then
        print_success "Web UI (运行中)"
    else
        print_warning "Web UI (未运行)"
    fi
}

# 显示日志
show_logs() {
    print_header "系统日志"
    
    if [ -d "logs" ]; then
        log_files=$(find logs -name "*.log" -type f 2>/dev/null)
        if [ -z "$log_files" ]; then
            print_warning "未找到日志文件"
            return
        fi
        
        echo "可用的日志文件:"
        echo ""
        select logfile in $log_files "返回"; do
            if [ "$logfile" = "返回" ]; then
                return
            fi
            
            echo ""
            echo "=== $logfile (最近50行) ==="
            tail -n 50 "$logfile"
            echo ""
            break
        done
    else
        print_warning "日志目录不存在"
    fi
}

# 停止所有服务
stop_all_services() {
    # 停止 webhook 服务器
    if pgrep -f "webhook_server.py" > /dev/null; then
        pkill -f "webhook_server.py"
        print_success "已停止 Webhook 服务器"
    fi
    
    # 停止 Web UI
    if pgrep -f "web_ui.py" > /dev/null; then
        pkill -f "web_ui.py"
        print_success "已停止 Web UI"
    fi
    
    # 停止多 Agent 系统
    if pgrep -f "main_multiagent.py" > /dev/null; then
        pkill -f "main_multiagent.py"
        print_success "已停止多 Agent 系统"
    fi
}

# 主函数
main() {
    clear
    
    print_header "🚀 飞书多 Agent 协作系统 - 一键部署"
    
    echo "系统信息:"
    echo "  项目目录: $PROJECT_ROOT"
    echo "  操作系统: $(uname -s)"
    echo "  Python 版本: $(python3 --version)"
    echo ""
    
    # 执行部署步骤
    check_python
    install_dependencies
    create_directories
    check_config
    
    print_header "🎉 部署准备完成！"
    
    echo ""
    echo "接下来您可以选择启动的服务："
    echo ""
    
    # 显示菜单
    show_menu
}

# 捕获 Ctrl+C
trap 'echo ""; print_warning "部署已中断"; exit 1' INT

# 运行主函数
main
