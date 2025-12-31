#!/bin/bash

# Webhook服务器启动脚本

echo "========================================="
echo "  交易信号Webhook服务器启动脚本"
echo "========================================="

# 获取工作目录
WORKSPACE_PATH=${COZE_WORKSPACE_PATH:-"/workspace/projects"}
cd "$WORKSPACE_PATH" || exit 1

echo "工作目录: $WORKSPACE_PATH"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3"
    exit 1
fi

echo "Python版本: $(python3 --version)"

# 检查配置文件
CONFIG_FILE="$WORKSPACE_PATH/config/webhook_config.json"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "错误: 未找到配置文件 $CONFIG_FILE"
    exit 1
fi

echo "配置文件: $CONFIG_FILE"

# 启动服务器
echo ""
echo "正在启动Webhook服务器..."
echo ""

# 启动webhook服务器
python3 -m src.webhook_server

echo ""
echo "Webhook服务器已停止"
