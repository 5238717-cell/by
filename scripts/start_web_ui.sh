#!/bin/bash
# Web UI 启动脚本 (Linux/Mac)

# 获取项目根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 添加 src 目录到 Python 路径
export PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH}"

# 配置
HOST="${WEBUI_HOST:-0.0.0.0}"
PORT="${WEBUI_PORT:-5000}"

# 颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Webhook Web UI 配置管理系统${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

echo -e "${GREEN}正在启动 Web UI 服务器...${NC}"
echo ""

# 检查 Python 版本
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "Python 版本: ${YELLOW}${python_version}${NC}"
echo ""

# 检查依赖
echo "检查依赖..."
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo -e "${YELLOW}未找到 fastapi，正在安装...${NC}"
    pip install fastapi uvicorn jinja2
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "🚀 Web UI 服务器启动成功！"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "访问地址:"
echo -e "  ${BLUE}http://localhost:${PORT}${NC}"
echo ""
echo "API 文档:"
echo -e "  ${BLUE}http://localhost:${PORT}/api/config${NC}"
echo ""
echo -e "按 ${YELLOW}Ctrl+C${NC} 停止服务器"
echo ""
echo -e "${GREEN}========================================${NC}"
echo ""

# 启动服务器
cd "${PROJECT_ROOT}"
python3 src/web_ui.py --host "${HOST}" --port "${PORT}"
