#!/bin/bash
# ============================================
# Webhook 系统管理脚本
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

# 检查服务状态
check_status() {
    print_header "服务状态"

    # 检查 Web UI
    if lsof -i:5000 > /dev/null 2>&1; then
        print_success "Web UI 服务: 运行中 (端口 5000)"
        lsof -i:5000 | grep LISTEN
    else
        print_error "Web UI 服务: 未运行"
    fi

    # 检查 Nginx
    if pgrep nginx > /dev/null; then
        print_success "Nginx 服务: 运行中"
        curl -s -o /dev/null -w "  HTTP 响应: %{http_code}\n" http://127.0.0.1:80
    else
        print_error "Nginx 服务: 未运行"
    fi
}

# 启动服务
start_service() {
    print_header "启动服务"

    # 启动 Web UI
    if lsof -i:5000 > /dev/null 2>&1; then
        print_warning "Web UI 服务已在运行"
    else
        print_info "启动 Web UI 服务..."
        nohup /opt/webhook-system-env/bin/python src/web_ui.py > /var/log/webhook-system.log 2>&1 &
        sleep 2
        if lsof -i:5000 > /dev/null 2>&1; then
            print_success "Web UI 服务启动成功"
        else
            print_error "Web UI 服务启动失败，查看日志："
            tail -20 /var/log/webhook-system.log
            return 1
        fi
    fi

    # 启动 Nginx
    if pgrep nginx > /dev/null; then
        print_warning "Nginx 服务已在运行"
    else
        print_info "启动 Nginx 服务..."
        nginx
        if pgrep nginx > /dev/null; then
            print_success "Nginx 服务启动成功"
        else
            print_error "Nginx 服务启动失败"
            return 1
        fi
    fi

    print_success "所有服务启动完成！"
    echo ""
    echo "访问地址："
    echo -e "  ${GREEN}http://localhost:80${NC}"
    echo -e "  ${GREEN}http://你的服务器IP:80${NC}"
}

# 停止服务
stop_service() {
    print_header "停止服务"

    # 停止 Web UI
    print_info "停止 Web UI 服务..."
    lsof -ti:5000 | xargs -r kill -9 2>/dev/null || true
    print_success "Web UI 服务已停止"

    # 停止 Nginx
    print_info "停止 Nginx 服务..."
    pkill nginx 2>/dev/null || true
    print_success "Nginx 服务已停止"

    print_success "所有服务已停止"
}

# 重启服务
restart_service() {
    print_header "重启服务"
    stop_service
    sleep 1
    start_service
}

# 查看日志
view_logs() {
    print_header "查看日志"
    print_info "Web UI 日志 (/var/log/webhook-system.log):"
    echo ""
    tail -50 /var/log/webhook-system.log
}

# 显示菜单
show_menu() {
    print_header "Webhook 系统管理"

    echo "1) 查看服务状态"
    echo "2) 启动服务"
    echo "3) 停止服务"
    echo "4) 重启服务"
    echo "5) 查看日志"
    echo "6) 退出"
    echo ""
}

# 主函数
main() {
    if [ $# -eq 0 ]; then
        # 无参数时显示菜单
        while true; do
            show_menu
            read -p "请输入选项 (1-6): " choice
            case $choice in
                1) check_status ;;
                2) start_service ;;
                3) stop_service ;;
                4) restart_service ;;
                5) view_logs ;;
                6) echo "退出"; exit 0 ;;
                *) print_error "无效选项，请重新输入" ;;
            esac
            echo ""
            read -p "按 Enter 继续..."
        done
    else
        # 有参数时直接执行命令
        case $1 in
            status) check_status ;;
            start) start_service ;;
            stop) stop_service ;;
            restart) restart_service ;;
            logs) view_logs ;;
            *) echo "用法: $0 {status|start|stop|restart|logs}" ;;
        esac
    fi
}

main "$@"
