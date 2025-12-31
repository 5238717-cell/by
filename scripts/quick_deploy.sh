#!/bin/bash
# ============================================
# 快速部署脚本 - 仅启动 Web UI（推荐新手）
# ============================================

echo "=========================================="
echo "  快速部署 - Web UI 配置管理系统"
echo "=========================================="
echo ""

# 获取项目根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "${PROJECT_ROOT}"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}[1/4]${NC} 检查 Python 环境..."
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}未找到 Python 3，正在尝试安装...${NC}"
    exit 1
fi
python3 --version
echo -e "${GREEN}✓ Python 环境正常${NC}"
echo ""

echo -e "${BLUE}[2/4]${NC} 安装依赖..."
pip install -q -r requirements.txt
echo -e "${GREEN}✓ 依赖安装完成${NC}"
echo ""

echo -e "${BLUE}[3/4]${NC} 初始化配置..."
if [ ! -f "config/webhook_config.json" ]; then
    echo "首次运行，创建默认配置..."
    python3 scripts/auto_init_config.py 2>/dev/null || echo "配置已存在"
fi
echo -e "${GREEN}✓ 配置初始化完成${NC}"
echo ""

echo -e "${BLUE}[4/4]${NC} 启动 Web UI..."
echo ""
echo -e "${GREEN}==========================================${NC}"
echo -e "${GREEN}🎉 部署完成！${NC}"
echo -e "${GREEN}==========================================${NC}"
echo ""
echo "📱 访问地址: ${BLUE}http://localhost:5000${NC}"
echo ""
echo "按 Ctrl+C 停止服务器"
echo ""
echo "=========================================="
echo ""

# 启动 Web UI
python3 src/web_ui.py
