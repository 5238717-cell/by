#!/usr/bin/env python3
"""
自动化配置初始化脚本
使用默认值自动生成配置文件，无需交互式输入

使用方法:
    python scripts/auto_init_config.py
"""

import os
import sys

# 添加 src 目录到 Python 路径
workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
sys.path.insert(0, os.path.join(workspace_path, "src"))

from utils.config.config_initializer import ConfigInitializer


def auto_init_config():
    """使用默认值自动初始化配置"""
    print("\n" + "=" * 70)
    print("  Webhook 配置自动化初始化")
    print("=" * 70)
    print("\n本脚本将使用默认值自动生成配置文件，无需交互式输入。\n")
    
    # 配置文件路径
    config_path = os.path.join(workspace_path, "config/webhook_config.json")
    
    # 检查配置文件是否已存在
    if os.path.exists(config_path):
        print(f"⚠️  配置文件已存在: {config_path}")
        response = input("是否覆盖现有配置？(y/N): ").strip().lower()
        if response != 'y':
            print("操作已取消。")
            return False
    
    # 创建配置初始化器
    initializer = ConfigInitializer(config_path)
    
    # 设置 Webhook 配置
    print("📌 配置 Webhook 端点...")
    initializer.config["webhooks"] = [
        {
            "id": "webhook_001",
            "name": "飞书交易信号Webhook",
            "url_path": "/webhook/trading-signal-001",
            "enabled": True,
            "description": "接收飞书群交易信号消息",
            "source": "feishu",
            "verification_token": ""
        }
    ]
    print("  ✅ 已配置 1 个 Webhook 端点")
    
    # 设置服务器配置
    print("\n📌 配置服务器...")
    initializer.config["server"] = {
        "host": "0.0.0.0",
        "port": 8080,
        "workers": 1
    }
    print("  ✅ 地址: 0.0.0.0:8080")
    
    # 设置过滤规则
    print("\n📌 配置消息过滤规则...")
    initializer.config["filter_rules"] = {
        "exclude_keywords": [
            "广告", "营销", "推广", "免费", "扫码", "加群",
            "关注", "点赞", "转发", "分享", "福利", "优惠券",
            "折扣", "限时优惠", "领取", "报名", "注册", "开户",
            "开户链接", "入金", "出金", "邀请码", "邀请链接",
            "返佣", "佣金", "代理", "合作", "客服", "咨询",
            "联系", "电话", "微信", "QQ", "电报", "Telegram", "Discord"
        ],
        "trading_keywords": [
            "开仓", "平仓", "做多", "做空", "买入", "卖出",
            "long", "short", "buy", "sell", "入场", "离场",
            "止盈", "止损", "补仓", "加仓", "下单", "成交",
            "价格", "数量"
        ],
        "exclude_patterns": [
            "趋势分析", "市场分析", "技术分析", "基本面分析",
            "行情分析", "投资建议", "风险提示", "免责声明",
            "仅供参考", "不构成投资建议", "市场有风险", "投资需谨慎"
        ]
    }
    print("  ✅ 排除关键词: 30 个")
    print("  ✅ 交易关键词: 16 个")
    print("  ✅ 排除模式: 10 个")
    
    # 设置消息处理配置
    print("\n📌 配置消息处理...")
    initializer.config["message_processing"] = {
        "enable_filter": True,
        "enable_agent_analysis": True,
        "auto_trade": False,
        "save_to_bitable": True,
        "log_all_messages": True
    }
    print("  ✅ 消息过滤: 启用")
    print("  ✅ Agent 分析: 启用")
    print("  ✅ 自动交易: 禁用")
    print("  ✅ 保存到表格: 启用")
    print("  ✅ 记录日志: 启用")
    
    # 保存配置
    print("\n💾 保存配置文件...")
    if initializer.save_config():
        print(f"\n✅ 配置已保存到: {config_path}")
        
        # 显示配置摘要
        print("\n" + "=" * 70)
        print("配置摘要:")
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
        
        print("\n" + "=" * 70)
        print("🚀 现在您可以启动 Webhook 服务器了：")
        print("=" * 70)
        print("\n启动命令:")
        print("  python src/webhook_server.py")
        print("\n后台启动:")
        print("  nohup python src/webhook_server.py > logs/webhook.log 2>&1 &")
        print("\n" + "=" * 70)
        
        return True
    else:
        print("\n❌ 配置保存失败")
        return False


def main():
    """主函数"""
    try:
        success = auto_init_config()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\n⚠️  操作已取消（用户中断）")
        return 1
    except Exception as e:
        print(f"\n\n❌ 出错: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
