#!/usr/bin/env python3
"""
测试首次运行流程
验证配置向导的自动启动功能
"""

import os
import sys
import json
import tempfile
import shutil

# 添加 src 目录到 Python 路径
workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
sys.path.insert(0, os.path.join(workspace_path, "src"))

from utils.config.config_initializer import check_first_run, ConfigInitializer


def test_first_run_flow():
    """测试完整的首次运行流程"""
    print("\n" + "=" * 70)
    print("  首次运行流程测试")
    print("=" * 70)
    
    # 备份现有配置文件
    config_path = os.path.join(workspace_path, "config/webhook_config.json")
    backup_path = None
    
    if os.path.exists(config_path):
        backup_path = config_path + ".backup"
        shutil.copy(config_path, backup_path)
        print(f"\n📦 已备份现有配置到: {backup_path}")
    
    try:
        # 步骤 1: 验证配置文件不存在时的行为
        print("\n【步骤 1】删除配置文件，模拟首次运行")
        if os.path.exists(config_path):
            os.remove(config_path)
            print(f"✅ 已删除配置文件: {config_path}")
        
        # 验证首次运行检测
        is_first_run = check_first_run(config_path)
        assert is_first_run == True, "首次运行检测失败"
        print("✅ 正确检测到首次运行")
        
        # 步骤 2: 创建一个示例配置
        print("\n【步骤 2】创建示例配置文件")
        initializer = ConfigInitializer(config_path)
        
        # 设置最小可用配置
        initializer.config["webhooks"] = [
            {
                "id": "webhook_001",
                "name": "测试Webhook",
                "url_path": "/test",
                "enabled": True,
                "source": "test",
                "description": "测试配置",
                "verification_token": ""
            }
        ]
        initializer.config["server"] = {"host": "0.0.0.0", "port": 8080, "workers": 1}
        initializer.config["filter_rules"] = {
            "exclude_keywords": ["广告"],
            "trading_keywords": ["开仓", "平仓"],
            "exclude_patterns": ["分析"]
        }
        initializer.config["message_processing"] = {
            "enable_filter": True,
            "enable_agent_analysis": True,
            "auto_trade": False,
            "save_to_bitable": True,
            "log_all_messages": True
        }
        
        # 保存配置
        initializer.save_config()
        print(f"✅ 已创建配置文件: {config_path}")
        
        # 步骤 3: 验证配置文件存在时的行为
        print("\n【步骤 3】验证配置文件存在时的行为")
        is_first_run = check_first_run(config_path)
        assert is_first_run == False, "非首次运行检测失败"
        print("✅ 正确检测到非首次运行（跳过配置向导）")
        
        # 步骤 4: 验证配置文件内容
        print("\n【步骤 4】验证配置文件内容")
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        assert "webhooks" in config
        assert "server" in config
        assert "filter_rules" in config
        assert "message_processing" in config
        assert len(config["webhooks"]) == 1
        assert config["webhooks"][0]["id"] == "webhook_001"
        print("✅ 配置文件结构正确")
        
        # 显示配置摘要
        print("\n" + "=" * 70)
        print("配置文件摘要:")
        print("=" * 70)
        print(f"Webhook 数量: {len(config['webhooks'])}")
        print(f"服务器地址: {config['server']['host']}:{config['server']['port']}")
        print(f"消息过滤: {'启用' if config['message_processing']['enable_filter'] else '禁用'}")
        print(f"Agent 分析: {'启用' if config['message_processing']['enable_agent_analysis'] else '禁用'}")
        
        print("\n" + "=" * 70)
        print("✅ 首次运行流程测试通过！")
        print("=" * 70)
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        return False
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # 恢复备份
        if backup_path and os.path.exists(backup_path):
            shutil.copy(backup_path, config_path)
            os.remove(backup_path)
            print(f"\n📦 已恢复原有配置文件")


def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("  Webhook 首次运行功能验证")
    print("=" * 70)
    print("\n本测试将验证以下功能：")
    print("  1. 配置文件不存在时，正确检测到首次运行")
    print("  2. 首次运行时可以创建配置文件")
    print("  3. 配置文件存在时，正确检测到非首次运行")
    print("  4. 配置文件内容正确")
    print("\n" + "=" * 70)
    
    success = test_first_run_flow()
    
    if success:
        print("\n" + "=" * 70)
        print("🎉 所有测试通过！")
        print("=" * 70)
        print("\n📝 说明:")
        print("  - 首次运行检测功能正常")
        print("  - Webhook 服务器将在首次运行时自动启动配置向导")
        print("  - 配置文件创建后，下次启动将跳过配置向导")
        print("\n💡 使用方法:")
        print("  1. 删除配置文件: rm config/webhook_config.json")
        print("  2. 启动服务器: python src/webhook_server.py")
        print("  3. 按照提示完成配置")
        print("  4. 配置完成后，服务器将自动启动")
        print("\n" + "=" * 70)
        return 0
    else:
        print("\n" + "=" * 70)
        print("❌ 测试失败")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
