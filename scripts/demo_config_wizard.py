#!/usr/bin/env python3
"""
配置向导演示脚本
展示配置向导的使用流程（非交互式演示）
"""

import os
import sys
import json
import tempfile

# 添加 src 目录到 Python 路径
workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
sys.path.insert(0, os.path.join(workspace_path, "src"))

from utils.config.config_initializer import ConfigInitializer


def demo_config_wizard():
    """演示配置向导流程"""
    print("\n" + "=" * 70)
    print("  Webhook 配置向导演示")
    print("=" * 70)
    print("\n这是一个配置向导的使用演示，展示完整的配置流程。")
    print("在实际使用中，您会看到交互式输入界面，可以按 Enter 使用默认值。\n")
    
    # 创建临时配置文件
    temp_config = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
    temp_path = temp_config.name
    temp_config.close()
    
    try:
        # 创建配置初始化器
        initializer = ConfigInitializer(temp_path)
        
        # 演示 Webhook 配置
        print("=" * 70)
        print("【步骤 1】配置 Webhook 端点")
        print("=" * 70)
        print("\n在交互式界面中，您会看到以下问题：")
        print("  📌 Webhook ID [webhook_001]: ")
        print("  📌 Webhook 名称 [飞书交易信号Webhook]: ")
        print("  📌 URL 路径 [/webhook/trading]: ")
        print("  📌 是否启用 [Y/n]: ")
        print("  📌 描述 [接收飞书群交易信号消息]: ")
        print("  📌 消息来源 [feishu]: ")
        print("  📌 验证令码 []: ")
        
        # 设置示例值
        initializer.config["webhooks"] = [
            {
                "id": "webhook_001",
                "name": "飞书交易信号Webhook",
                "url_path": "/webhook/trading",
                "enabled": True,
                "description": "接收飞书群交易信号消息",
                "source": "feishu",
                "verification_token": ""
            }
        ]
        print("\n✅ 已配置 1 个 Webhook 端点")
        
        # 演示服务器配置
        print("\n" + "=" * 70)
        print("【步骤 2】配置服务器")
        print("=" * 70)
        print("\n在交互式界面中，您会看到以下问题：")
        print("  📌 监听地址 [0.0.0.0]: ")
        print("  📌 监听端口 [8080]: ")
        print("  📌 工作进程数 [1]: ")
        
        initializer.config["server"] = {
            "host": "0.0.0.0",
            "port": 8080,
            "workers": 1
        }
        print("\n✅ 已配置服务器参数")
        
        # 演示过滤规则配置
        print("\n" + "=" * 70)
        print("【步骤 3】配置消息过滤规则")
        print("=" * 70)
        print("\n在交互式界面中，您会看到以下问题：")
        print("  📋 排除关键词（营销、广告等）[广告, 营销, 推广, ...]: ")
        print("  📋 交易关键词（开仓、平仓等）[开仓, 平仓, 做多, ...]: ")
        print("  📋 排除模式（分析、免责声明等）[趋势分析, 投资建议, ...]: ")
        
        initializer.config["filter_rules"] = {
            "exclude_keywords": ["广告", "营销", "推广", "免费"],
            "trading_keywords": ["开仓", "平仓", "做多", "做空", "买入", "卖出"],
            "exclude_patterns": ["趋势分析", "市场分析", "投资建议"]
        }
        print("\n✅ 已配置过滤规则")
        
        # 演示消息处理配置
        print("\n" + "=" * 70)
        print("【步骤 4】配置消息处理")
        print("=" * 70)
        print("\n在交互式界面中，您会看到以下问题：")
        print("  📌 启用消息过滤 [Y/n]: ")
        print("  📌 启用 Agent 分析 [Y/n]: ")
        print("  📌 自动交易 (⚠️  慎用) [y/N]: ")
        print("  📌 保存到飞书多维表格 [Y/n]: ")
        print("  📌 记录所有消息日志 [Y/n]: ")
        
        initializer.config["message_processing"] = {
            "enable_filter": True,
            "enable_agent_analysis": True,
            "auto_trade": False,
            "save_to_bitable": True,
            "log_all_messages": True
        }
        print("\n✅ 已配置消息处理选项")
        
        # 显示配置摘要
        print("\n" + "=" * 70)
        print("【步骤 5】配置摘要")
        print("=" * 70)
        
        print("\n📌 Webhook 端点:")
        for wh in initializer.config["webhooks"]:
            status = "✅" if wh["enabled"] else "❌"
            print(f"  {status} {wh['name']} ({wh['id']})")
            print(f"     路径: {wh['url_path']}")
            print(f"     来源: {wh['source']}")
        
        print(f"\n📌 服务器:")
        print(f"  地址: {initializer.config['server']['host']}:{initializer.config['server']['port']}")
        print(f"  工作进程: {initializer.config['server']['workers']}")
        
        print(f"\n📌 过滤规则:")
        print(f"  排除关键词: {len(initializer.config['filter_rules']['exclude_keywords'])} 个")
        print(f"  交易关键词: {len(initializer.config['filter_rules']['trading_keywords'])} 个")
        print(f"  排除模式: {len(initializer.config['filter_rules']['exclude_patterns'])} 个")
        
        print(f"\n📌 消息处理:")
        print(f"  消息过滤: {'✅' if initializer.config['message_processing']['enable_filter'] else '❌'}")
        print(f"  Agent 分析: {'✅' if initializer.config['message_processing']['enable_agent_analysis'] else '❌'}")
        print(f"  自动交易: {'✅' if initializer.config['message_processing']['auto_trade'] else '❌'}")
        print(f"  保存到表格: {'✅' if initializer.config['message_processing']['save_to_bitable'] else '❌'}")
        print(f"  记录日志: {'✅' if initializer.config['message_processing']['log_all_messages'] else '❌'}")
        
        # 保存配置
        print("\n" + "=" * 70)
        print("【步骤 6】保存配置")
        print("=" * 70)
        
        initializer.save_config()
        print("\n✅ 配置已保存")
        
        # 显示配置文件内容
        print("\n" + "=" * 70)
        print("生成的配置文件内容:")
        print("=" * 70)
        
        with open(temp_path, 'r', encoding='utf-8') as f:
            config_json = json.load(f)
        
        print(json.dumps(config_json, ensure_ascii=False, indent=2))
        
        print("\n" + "=" * 70)
        print("📝 使用说明")
        print("=" * 70)
        print("""
在实际使用中，您可以通过以下方式启动配置向导：

1. 首次运行 Webhook 服务器时自动触发：
   $ python src/webhook_server.py

2. 手动运行配置向导：
   $ python scripts/init_webhook_config.py

3. 直接运行配置向导模块：
   $ python src/utils/config/config_initializer.py

配置文件将保存到: config/webhook_config.json

如需重新配置，请删除配置文件后重新运行：
   $ rm config/webhook_config.json
   $ python src/webhook_server.py
        """)
        
    finally:
        # 清理临时文件
        if os.path.exists(temp_path):
            os.remove(temp_path)


def main():
    """主函数"""
    demo_config_wizard()
    
    print("\n" + "=" * 70)
    print("✅ 演示完成")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
