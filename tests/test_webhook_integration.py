#!/usr/bin/env python3
"""
测试 Webhook 服务器的首次运行检测功能
"""

import os
import sys
import tempfile
import json

# 添加 src 目录到 Python 路径
workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
sys.path.insert(0, os.path.join(workspace_path, "src"))

from utils.config.config_initializer import check_first_run, ConfigInitializer


def test_first_run_detection():
    """测试首次运行检测"""
    print("\n" + "=" * 70)
    print("测试 Webhook 服务器首次运行检测功能")
    print("=" * 70)
    
    # 创建临时配置文件
    temp_config = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
    temp_path = temp_config.name
    temp_config.close()
    
    try:
        # 测试 1: 不存在的配置文件
        print("\n测试 1: 配置文件不存在")
        assert check_first_run(temp_path) == True
        print("✅ 正确检测到首次运行")
        
        # 测试 2: 创建有效的配置文件
        print("\n测试 2: 创建有效配置文件")
        initializer = ConfigInitializer(temp_path)
        initializer.config["webhooks"] = [
            {
                "id": "test_webhook",
                "name": "测试 Webhook",
                "url_path": "/test",
                "enabled": True,
                "source": "test"
            }
        ]
        initializer.save_config()
        
        # 再次检查
        assert check_first_run(temp_path) == False
        print("✅ 正确检测到非首次运行")
        
        # 测试 3: 删除配置文件
        print("\n测试 3: 删除配置文件")
        os.remove(temp_path)
        assert check_first_run(temp_path) == True
        print("✅ 正确检测到首次运行（文件已删除）")
        
        print("\n" + "=" * 70)
        print("✅ 所有首次运行检测测试通过！")
        print("=" * 70)
        
    finally:
        # 清理临时文件
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_webhook_server_integration():
    """测试 Webhook 服务器集成"""
    print("\n" + "=" * 70)
    print("测试 Webhook 服务器集成")
    print("=" * 70)
    
    workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
    config_path = os.path.join(workspace_path, "config/webhook_config.json")
    
    # 检查现有配置文件
    if os.path.exists(config_path):
        print(f"\n✅ 配置文件已存在: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print(f"   - Webhook 数量: {len(config.get('webhooks', []))}")
        print(f"   - 服务器地址: {config.get('server', {}).get('host')}:{config.get('server', {}).get('port')}")
        print(f"   - 消息过滤: {'启用' if config.get('message_processing', {}).get('enable_filter') else '禁用'}")
        
        # 检查首次运行检测
        is_first_run = check_first_run(config_path)
        print(f"   - 首次运行: {'是' if is_first_run else '否'}")
        
        if not is_first_run:
            print("\n✅ Webhook 服务器启动时将跳过配置向导")
    else:
        print(f"\n⚠️  配置文件不存在: {config_path}")
        print("   首次运行 Webhook 服务器时将自动启动配置向导")
    
    print("\n" + "=" * 70)


def main():
    """主函数"""
    try:
        test_first_run_detection()
        test_webhook_server_integration()
        
        print("\n" + "=" * 70)
        print("✅ 所有集成测试通过！")
        print("=" * 70)
        print("\n📝 说明:")
        print("  - 首次运行检测功能正常")
        print("  - Webhook 服务器将在配置文件不存在时自动启动配置向导")
        print("  - 您可以随时运行 'python scripts/init_webhook_config.py' 重新配置")
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
