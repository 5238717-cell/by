#!/usr/bin/env python3
"""
Webhook功能测试脚本
"""

import requests
import json
from datetime import datetime

# Webhook服务器配置
BASE_URL = "http://localhost:8080"

def test_root():
    """测试根路径"""
    print("\n=== 测试根路径 ===")
    response = requests.get(f"{BASE_URL}/")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    return response.status_code == 200

def test_list_webhooks():
    """测试列出webhook配置"""
    print("\n=== 测试列出webhook配置 ===")
    response = requests.get(f"{BASE_URL}/webhooks")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    return response.status_code == 200

def test_get_config():
    """测试获取配置"""
    print("\n=== 测试获取配置 ===")
    response = requests.get(f"{BASE_URL}/config")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    return response.status_code == 200

def test_send_trading_message():
    """测试发送交易消息"""
    print("\n=== 测试发送交易消息 ===")
    
    message = {
        "webhook_id": "webhook_001",
        "timestamp": datetime.now().isoformat(),
        "source": "feishu",
        "content": "BTC现货交易，做多，入场价格90000，止盈92000，止损88000",
        "group_name": "交易信号群",
        "user_info": {"user_id": "user_001", "username": "trader"},
        "metadata": {"msg_id": "msg_123"}
    }
    
    print(f"发送消息: {json.dumps(message, ensure_ascii=False, indent=2)}")
    
    response = requests.post(
        f"{BASE_URL}/webhook/webhook_001",
        json=message
    )
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    return response.status_code == 200

def test_send_spam_message():
    """测试发送垃圾消息（应被过滤）"""
    print("\n=== 测试发送垃圾消息（营销信息）===")
    
    message = {
        "webhook_id": "webhook_001",
        "timestamp": datetime.now().isoformat(),
        "source": "feishu",
        "content": "限时优惠！扫码添加客服微信，领取免费课程和优惠券！",
        "group_name": "交易信号群",
        "user_info": {"user_id": "user_002", "username": "spammer"}
    }
    
    print(f"发送消息: {json.dumps(message, ensure_ascii=False, indent=2)}")
    
    response = requests.post(
        f"{BASE_URL}/webhook/webhook_001",
        json=message
    )
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    # 检查是否被过滤
    if response.status_code == 200:
        result = response.json()
        return result.get("status") == "filtered"
    
    return False

def test_send_analysis_message():
    """测试发送分析消息（应被过滤）"""
    print("\n=== 测试发送分析消息（趋势判断）===")
    
    message = {
        "webhook_id": "webhook_001",
        "timestamp": datetime.now().isoformat(),
        "source": "feishu",
        "content": "BTC/USDT 趋势分析：当前处于上升趋势，建议等待回调后再入场。仅供参考，不构成投资建议。",
        "group_name": "交易分析群",
        "user_info": {"user_id": "user_003", "username": "analyst"}
    }
    
    print(f"发送消息: {json.dumps(message, ensure_ascii=False, indent=2)}")
    
    response = requests.post(
        f"{BASE_URL}/webhook/webhook_001",
        json=message
    )
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    # 检查是否被过滤
    if response.status_code == 200:
        result = response.json()
        return result.get("status") == "filtered" and result.get("filter_result", {}).get("message_type") == "analysis"
    
    return False

def test_send_exit_message():
    """测试发送平仓消息"""
    print("\n=== 测试发送平仓消息 ===")
    
    message = {
        "webhook_id": "webhook_001",
        "timestamp": datetime.now().isoformat(),
        "source": "feishu",
        "content": "BTC已平仓，离场价格92000，止盈离场",
        "group_name": "交易信号群",
        "user_info": {"user_id": "user_001", "username": "trader"}
    }
    
    print(f"发送消息: {json.dumps(message, ensure_ascii=False, indent=2)}")
    
    response = requests.post(
        f"{BASE_URL}/webhook/webhook_001",
        json=message
    )
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    return response.status_code == 200

def test_add_webhook():
    """测试添加webhook"""
    print("\n=== 测试添加webhook ===")
    
    new_webhook = {
        "id": "webhook_003",
        "name": "Telegram交易信号",
        "url_path": "/webhook/trading-signal-003",
        "enabled": True,
        "description": "接收Telegram交易信号消息",
        "source": "telegram",
        "verification_token": ""
    }
    
    print(f"添加webhook: {json.dumps(new_webhook, ensure_ascii=False, indent=2)}")
    
    response = requests.post(
        f"{BASE_URL}/admin/webhook",
        json=new_webhook
    )
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    return response.status_code == 200

def test_toggle_webhook():
    """测试切换webhook状态"""
    print("\n=== 测试切换webhook状态 ===")
    
    response = requests.post(f"{BASE_URL}/admin/webhook/webhook_001/toggle")
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    # 切换回来
    requests.post(f"{BASE_URL}/admin/webhook/webhook_001/toggle")
    
    return response.status_code == 200

def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("Webhook功能测试")
    print("=" * 60)
    
    # 检查服务器是否运行
    try:
        response = requests.get(BASE_URL, timeout=2)
        if response.status_code != 200:
            print("\n❌ 错误: Webhook服务器未运行或无法访问")
            return False
    except requests.exceptions.RequestException:
        print("\n❌ 错误: 无法连接到Webhook服务器")
        print("   请先启动服务器: python -m src.webhook_server")
        return False
    
    # 运行测试
    tests = [
        ("根路径", test_root),
        ("列出webhook配置", test_list_webhooks),
        ("获取配置", test_get_config),
        ("发送交易消息", test_send_trading_message),
        ("发送垃圾消息", test_send_spam_message),
        ("发送分析消息", test_send_analysis_message),
        ("发送平仓消息", test_send_exit_message),
        ("添加webhook", test_add_webhook),
        ("切换webhook状态", test_toggle_webhook),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            status = "✅ 通过" if result else "❌ 失败"
            print(f"\n{status}: {test_name}")
        except Exception as e:
            results.append((test_name, False))
            print(f"\n❌ 失败: {test_name}")
            print(f"   错误: {e}")
    
    # 打印总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"通过: {passed}/{total}")
    print(f"失败: {total - passed}/{total}")
    
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")
    
    print("\n" + "=" * 60)
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
