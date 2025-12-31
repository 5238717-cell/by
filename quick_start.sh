#!/bin/bash
# ============================================
# 快速启动脚本 - Webhook 配置管理系统
# ============================================

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  Webhook 系统快速启动${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# 检查服务状态
if lsof -i:5000 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Web UI 服务已运行 (端口 5000)${NC}"
else
    echo -e "${BLUE}→ 启动 Web UI 服务...${NC}"
    nohup /opt/webhook-system-env/bin/python /workspace/projects/src/web_ui.py > /var/log/webhook-system.log 2>&1 &
    sleep 2
    if lsof -i:5000 > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Web UI 服务启动成功${NC}"
    else
        echo -e "${YELLOW}✗ Web UI 服务启动失败，查看日志: tail /var/log/webhook-system.log${NC}"
        exit 1
    fi
fi

if pgrep nginx > /dev/null; then
    echo -e "${GREEN}✓ Nginx 服务已运行${NC}"
else
    echo -e "${BLUE}→ 启动 Nginx 服务...${NC}"
    nginx
    if pgrep nginx > /dev/null; then
        echo -e "${GREEN}✓ Nginx 服务启动成功${NC}"
    else
        echo -e "${YELLOW}✗ Nginx 服务启动失败${NC}"
        exit 1
    fi
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  🎉 系统启动完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}访问地址：${NC}"
echo -e "  ${CYAN}http://localhost:80${NC}"
echo -e "  ${CYAN}http://43.128.70.173:80${NC}"
echo ""
echo -e "${YELLOW}注意：${NC}"
echo -e "  1. 请确保腾讯云安全组已开放 80 端口"
echo -e "  2. 使用 ./scripts/manage.sh 管理服务"
echo -e "  3. 查看日志: tail -f /var/log/webhook-system.log"
echo ""
