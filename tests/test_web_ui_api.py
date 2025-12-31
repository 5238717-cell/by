#!/usr/bin/env python3
"""
测试 Web UI API 功能
"""

import sys
import os
import json
import requests

# 添加 src 目录到 Python 路径
workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
sys.path.insert(0, os.path.join(workspace_path, "src"))

from web_ui import load_config, save_config, get_default_config


def test_config_operations():
    """测试配置操作"""
    print("\n" + "=" * 70)
    print("测试配置操作")
    print("=" * 70)
    
    # 测试加载配置
    print("\n1. 测试加载配置...")
    config = load_config()
    assert isinstance(config, dict)
    assert "webhooks" in config
    assert "server" in config
    assert "filter_rules" in config
    assert "message_processing" in config
    print("   ✅ 配置加载成功")
    print(f"   - Webhook 数量: {len(config['webhooks'])}")
    print(f"   - 服务器地址: {config['server']['host']}:{config['server']['port']}")
    
    # 测试默认配置
    print("\n2. 测试默认配置...")
    default_config = get_default_config()
    assert isinstance(default_config, dict)
    assert "webhooks" in default_config
    print("   ✅ 默认配置加载成功")
    
    # 测试配置结构验证
    print("\n3. 测试配置结构验证...")
    required_keys = ["webhooks", "server", "filter_rules", "message_processing"]
    for key in required_keys:
        assert key in config, f"缺少配置项: {key}"
    print("   ✅ 配置结构验证通过")
    
    return True


def test_webhook_operations():
    """测试 Webhook 操作"""
    print("\n" + "=" * 70)
    print("测试 Webhook 操作")
    print("=" * 70)
    
    config = load_config()
    original_count = len(config["webhooks"])
    
    # 测试添加 Webhook
    print("\n1. 测试添加 Webhook...")
    new_webhook = {
        "id": "test_webhook_001",
        "name": "测试 Webhook",
        "url_path": "/test/webhook",
        "enabled": True,
        "source": "test",
        "description": "测试 Webhook",
        "verification_token": ""
    }
    
    # 检查 ID 是否已存在
    existing_ids = [wh.get("id") for wh in config["webhooks"]]
    if new_webhook["id"] in existing_ids:
        print(f"   ⚠️  Webhook ID 已存在，跳过添加测试")
    else:
        config["webhooks"].append(new_webhook)
        success = save_config(config)
        assert success == True
        assert len(config["webhooks"]) == original_count + 1
        print("   ✅ Webhook 添加成功")
    
    # 重新加载配置
    config = load_config()
    
    # 测试更新 Webhook
    print("\n2. 测试更新 Webhook...")
    webhook = next((wh for wh in config["webhooks"] if wh.get("id") == new_webhook["id"]), None)
    if webhook:
        webhook["name"] = "更新后的 Webhook"
        success = save_config(config)
        assert success == True
        print("   ✅ Webhook 更新成功")
    else:
        print("   ⚠️  Webhook 不存在，跳过更新测试")
    
    # 测试删除 Webhook
    print("\n3. 测试删除 Webhook...")
    webhook = next((wh for wh in config["webhooks"] if wh.get("id") == new_webhook["id"]), None)
    if webhook:
        config["webhooks"].remove(webhook)
        success = save_config(config)
        assert success == True
        assert len(config["webhooks"]) == original_count
        print("   ✅ Webhook 删除成功")
    else:
        print("   ⚠️  Webhook 不存在，跳过删除测试")
    
    return True


def test_server_config():
    """测试服务器配置"""
    print("\n" + "=" * 70)
    print("测试服务器配置")
    print("=" * 70)
    
    config = load_config()
    
    print("\n1. 测试服务器配置读取...")
    assert "host" in config["server"]
    assert "port" in config["server"]
    assert "workers" in config["server"]
    print(f"   ✅ 服务器配置读取成功")
    print(f"   - 地址: {config['server']['host']}:{config['server']['port']}")
    print(f"   - 工作进程: {config['server']['workers']}")
    
    print("\n2. 测试服务器配置更新...")
    original_port = config["server"]["port"]
    config["server"]["port"] = 8081
    success = save_config(config)
    assert success == True
    print("   ✅ 服务器配置更新成功")
    
    # 恢复原始端口
    config["server"]["port"] = original_port
    save_config(config)
    
    return True


def test_filter_rules():
    """测试过滤规则"""
    print("\n" + "=" * 70)
    print("测试过滤规则")
    print("=" * 70)
    
    config = load_config()
    
    print("\n1. 测试过滤规则读取...")
    assert "exclude_keywords" in config["filter_rules"]
    assert "trading_keywords" in config["filter_rules"]
    assert "exclude_patterns" in config["filter_rules"]
    print(f"   ✅ 过滤规则读取成功")
    print(f"   - 排除关键词: {len(config['filter_rules']['exclude_keywords'])} 个")
    print(f"   - 交易关键词: {len(config['filter_rules']['trading_keywords'])} 个")
    print(f"   - 排除模式: {len(config['filter_rules']['exclude_patterns'])} 个")
    
    print("\n2. 测试过滤规则更新...")
    config["filter_rules"]["exclude_keywords"].append("测试关键词")
    success = save_config(config)
    assert success == True
    print("   ✅ 过滤规则更新成功")
    
    # 移除测试关键词
    config = load_config()
    if "测试关键词" in config["filter_rules"]["exclude_keywords"]:
        config["filter_rules"]["exclude_keywords"].remove("测试关键词")
        save_config(config)
    
    return True


def test_processing_config():
    """测试消息处理配置"""
    print("\n" + "=" * 70)
    print("测试消息处理配置")
    print("=" * 70)
    
    config = load_config()
    
    print("\n1. 测试消息处理配置读取...")
    processing = config["message_processing"]
    assert "enable_filter" in processing
    assert "enable_agent_analysis" in processing
    assert "auto_trade" in processing
    assert "save_to_bitable" in processing
    assert "log_all_messages" in processing
    print(f"   ✅ 消息处理配置读取成功")
    print(f"   - 消息过滤: {'启用' if processing['enable_filter'] else '禁用'}")
    print(f"   - Agent 分析: {'启用' if processing['enable_agent_analysis'] else '禁用'}")
    print(f"   - 自动交易: {'启用' if processing['auto_trade'] else '禁用'}")
    
    print("\n2. 测试消息处理配置更新...")
    original_value = processing["enable_filter"]
    processing["enable_filter"] = not original_value
    success = save_config(config)
    assert success == True
    print("   ✅ 消息处理配置更新成功")
    
    # 恢复原始值
    config = load_config()
    config["message_processing"]["enable_filter"] = original_value
    save_config(config)
    
    return True


def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("  Web UI 配置管理系统 - API 功能测试")
    print("=" * 70)
    
    try:
        # 运行所有测试
        test_config_operations()
        test_webhook_operations()
        test_server_config()
        test_filter_rules()
        test_processing_config()
        
        print("\n" + "=" * 70)
        print("✅ 所有测试通过！")
        print("=" * 70)
        print("\n📝 测试总结:")
        print("  - 配置加载和保存功能正常")
        print("  - Webhook 操作（增删改查）正常")
        print("  - 服务器配置读写正常")
        print("  - 过滤规则管理正常")
        print("  - 消息处理配置正常")
        print("\n🚀 Web UI 配置管理系统已就绪！")
        print("\n启动 Web UI 服务器:")
        print("  Linux/Mac: ./scripts/start_web_ui.sh")
        print("  Windows:  scripts\\start_web_ui.bat")
        print("  或者:    python src/web_ui.py")
        print("\n访问地址:")
        print("  http://localhost:5000")
        print("\n" + "=" * 70)
        
        return 0
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
