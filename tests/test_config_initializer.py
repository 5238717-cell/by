"""
配置初始化工具测试
"""

import os
import sys
import json
import tempfile
import shutil

# 添加 src 目录到 Python 路径
workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
sys.path.insert(0, os.path.join(workspace_path, "src"))

from utils.config.config_initializer import ConfigInitializer, check_first_run, run_config_wizard


def test_config_initializer():
    """测试配置初始化器"""
    print("\n" + "=" * 60)
    print("测试 1: 配置初始化器基本功能")
    print("=" * 60)
    
    # 创建临时配置文件
    temp_config = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
    temp_path = temp_config.name
    temp_config.close()
    
    try:
        # 测试创建配置初始化器
        initializer = ConfigInitializer(temp_path)
        print("✅ ConfigInitializer 创建成功")
        
        # 测试默认配置
        assert "webhooks" in initializer.config
        assert "server" in initializer.config
        assert "filter_rules" in initializer.config
        assert "message_processing" in initializer.config
        print("✅ 默认配置结构正确")
        
    finally:
        # 清理临时文件
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_check_first_run():
    """测试首次运行检测"""
    print("\n" + "=" * 60)
    print("测试 2: 首次运行检测")
    print("=" * 60)
    
    # 测试不存在的文件
    temp_path = "/tmp/non_existent_config.json"
    assert check_first_run(temp_path) == True
    print("✅ 不存在的文件返回 True（首次运行）")
    
    # 测试空文件
    temp_config = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
    temp_path = temp_config.name
    temp_config.write("")
    temp_config.close()
    
    try:
        assert check_first_run(temp_path) == True
        print("✅ 空文件返回 True（首次运行）")
    finally:
        os.remove(temp_path)
    
    # 测试有效配置文件
    temp_config = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
    temp_path = temp_config.name
    json.dump({
        "webhooks": [],
        "server": {"host": "0.0.0.0", "port": 8080}
    }, temp_config)
    temp_config.close()
    
    try:
        assert check_first_run(temp_path) == False
        print("✅ 有效配置文件返回 False（非首次运行）")
    finally:
        os.remove(temp_path)
    
    # 测试无效配置文件（缺少必要字段）
    temp_config = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
    temp_path = temp_config.name
    json.dump({
        "some_key": "some_value"
    }, temp_config)
    temp_config.close()
    
    try:
        assert check_first_run(temp_path) == True
        print("✅ 无效配置文件返回 True（首次运行）")
    finally:
        os.remove(temp_path)


def test_save_and_load_config():
    """测试保存和加载配置"""
    print("\n" + "=" * 60)
    print("测试 3: 保存和加载配置")
    print("=" * 60)
    
    # 创建临时配置文件
    temp_config = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
    temp_path = temp_config.name
    temp_config.close()
    
    try:
        # 创建初始化器并设置配置
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
        
        # 保存配置
        result = initializer.save_config()
        assert result == True
        print("✅ 配置保存成功")
        
        # 验证文件存在
        assert os.path.exists(temp_path)
        print("✅ 配置文件已创建")
        
        # 验证文件内容
        with open(temp_path, 'r', encoding='utf-8') as f:
            loaded_config = json.load(f)
        
        assert "webhooks" in loaded_config
        assert len(loaded_config["webhooks"]) == 1
        assert loaded_config["webhooks"][0]["id"] == "test_webhook"
        print("✅ 配置内容正确")
        
    finally:
        # 清理临时文件
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_input_methods():
    """测试输入方法 - 仅验证方法存在"""
    print("\n" + "=" * 60)
    print("测试 4: 输入方法（仅验证方法存在）")
    print("=" * 60)
    
    temp_config = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
    temp_path = temp_config.name
    temp_config.close()
    
    try:
        initializer = ConfigInitializer(temp_path)
        
        # 验证输入方法存在
        assert hasattr(initializer, 'input_string')
        print("✅ input_string 方法存在")
        
        assert hasattr(initializer, 'input_boolean')
        print("✅ input_boolean 方法存在")
        
        assert hasattr(initializer, 'input_int')
        print("✅ input_int 方法存在")
        
        assert hasattr(initializer, 'input_list')
        print("✅ input_list 方法存在")
        
        print("\n📝 注意: 输入方法需要交互式输入，自动化测试中跳过实际调用")
        print("   请手动运行配置向导进行交互测试: python src/utils/config/config_initializer.py")
        
    finally:
        # 清理临时文件
        if os.path.exists(temp_path):
            os.remove(temp_path)


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("  配置初始化工具测试套件")
    print("=" * 60)
    
    try:
        test_config_initializer()
        test_check_first_run()
        test_save_and_load_config()
        test_input_methods()
        
        print("\n" + "=" * 60)
        print("✅ 所有测试通过！")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
