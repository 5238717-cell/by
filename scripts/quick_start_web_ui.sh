#!/bin/bash
# Web UI 快速启动脚本

echo "=========================================="
echo "  Web UI 快速启动脚本"
echo "=========================================="
echo ""

# 检查配置文件
if [ ! -f "config/webhook_config.json" ]; then
    echo "⚠️  配置文件不存在，正在初始化默认配置..."
    python scripts/auto_init_config.py
    echo ""
fi

echo "🚀 正在启动 Web UI 服务器..."
echo ""
echo "访问地址:"
echo "  http://localhost:5000"
echo ""
echo "按 Ctrl+C 停止服务器"
echo ""
echo "=========================================="
echo ""

# 启动 Web UI
python src/web_ui.py
