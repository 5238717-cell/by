#!/usr/bin/env python3
"""
Webhook 配置初始化脚本
独立运行的配置向导，方便用户快速配置系统

使用方法:
    python scripts/init_webhook_config.py
"""

import os
import sys

# 添加 src 目录到 Python 路径
workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
sys.path.insert(0, os.path.join(workspace_path, "src"))

from utils.config.config_initializer import run_config_wizard


def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("  交易信号 Webhook 配置向导")
    print("=" * 70)
    print("\n本向导将帮助您配置 Webhook 服务器，包括：")
    print("  • Webhook 端点配置（ID、名称、URL路径等）")
    print("  • 服务器配置（监听地址、端口、工作进程数）")
    print("  • 消息过滤规则（排除关键词、交易关键词等）")
    print("  • 消息处理配置（过滤开关、Agent分析、自动交易等）")
    print("\n💡 提示:")
    print("  • 可以按 Enter 使用默认值（括号中显示）")
    print("  • 配置文件将保存到: config/webhook_config.json")
    print("  • 如需重新配置，请删除配置文件后重新运行本脚本")
    print("\n" + "-" * 70)
    
    # 运行配置向导
    try:
        run_config_wizard()
    except KeyboardInterrupt:
        print("\n\n⚠️  配置已取消（用户中断）")
        return 1
    except Exception as e:
        print(f"\n\n❌ 配置过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
