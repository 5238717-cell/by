"""
多 Agent 系统测试脚本
测试各个 Agent 的基本功能
"""
import sys
import os

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agents.message_parser_agent import build_message_parser_agent
from agents.data_analysis_agent import build_data_analysis_agent
from agents.data_storage_agent import build_data_storage_agent


def test_message_parser_agent():
    """测试消息解析 Agent"""
    print("=" * 60)
    print("测试消息解析 Agent")
    print("=" * 60)

    parser = build_message_parser_agent()

    test_message = """
    策略：BTC现货交易
    做多方向，入场金额：1000U
    止盈：20%
    止损：10%
    """

    result = parser.parse(test_message, "测试群")

    if result.get("success"):
        order_info = result["order_info"]
        print("✓ 解析成功")
        print(f"  群名称: {order_info['group_name']}")
        print(f"  订单类型: {order_info['order_type']}")
        print(f"  开仓方向: {order_info['direction']}")
        print(f"  入场金额: {order_info['entry_amount']}")
        print(f"  止盈: {order_info['take_profit']}")
        print(f"  止损: {order_info['stop_loss']}")
        print(f"  策略关键词: {order_info['strategy_keywords']}")
        return True
    else:
        print(f"✗ 解析失败: {result.get('error')}")
        return False


def test_data_storage_agent():
    """测试数据存储 Agent（需要配置）"""
    print("\n" + "=" * 60)
    print("测试数据存储 Agent")
    print("=" * 60)

    # 检查环境变量
    app_token = os.getenv("FEISHU_BITABLE_APP_TOKEN")
    table_id = os.getenv("FEISHU_BITABLE_TABLE_ID")

    if not all([app_token, table_id]):
        print("⚠ 跳过测试: 未配置环境变量 (FEISHU_BITABLE_APP_TOKEN, FEISHU_BITABLE_TABLE_ID)")
        return None

    storage = build_data_storage_agent(app_token, table_id)

    # 测试保存（使用测试数据）
    test_order = {
        "group_name": "测试群",
        "message_content": "测试消息",
        "order_type": "测试",
        "direction": "测试",
        "entry_amount": "100U",
        "take_profit": "10%",
        "stop_loss": "5%",
        "strategy_keywords": ["测试"],
        "parsed_at": "2025-01-01T12:00:00"
    }

    result = storage.save(test_order)

    if result.get("success"):
        print("✓ 保存成功")
        print(f"  记录 ID: {result.get('record_id')}")
        return True
    else:
        print(f"✗ 保存失败: {result.get('error')}")
        return False


def test_data_analysis_agent():
    """测试数据分析 Agent"""
    print("\n" + "=" * 60)
    print("测试数据分析 Agent")
    print("=" * 60)

    # 检查环境变量
    app_token = os.getenv("FEISHU_BITABLE_APP_TOKEN")
    table_id = os.getenv("FEISHU_BITABLE_TABLE_ID")

    if not all([app_token, table_id]):
        print("⚠ 跳过测试: 未配置环境变量 (FEISHU_BITABLE_APP_TOKEN, FEISHU_BITABLE_TABLE_ID)")
        return None

    storage = build_data_storage_agent(app_token, table_id)
    analysis = build_data_analysis_agent(storage)

    # 测试分析
    result = analysis.analyze("daily")

    if result.get("success"):
        analysis_result = result["analysis_result"]
        print("✓ 分析成功")
        print(f"  总订单数: {analysis_result.get('total_orders')}")
        print(f"  分析类型: {analysis_result.get('analysis_type')}")
        return True
    else:
        print(f"✗ 分析失败: {result.get('error')}")
        return False


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("多 Agent 系统测试")
    print("=" * 60)

    results = []

    # 测试消息解析 Agent
    results.append(("消息解析 Agent", test_message_parser_agent()))

    # 测试数据存储 Agent
    results.append(("数据存储 Agent", test_data_storage_agent()))

    # 测试数据分析 Agent
    results.append(("数据分析 Agent", test_data_analysis_agent()))

    # 输出测试结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)

    for name, result in results:
        if result is None:
            status = "跳过"
        elif result:
            status = "通过"
        else:
            status = "失败"
        print(f"{name}: {status}")

    passed = sum(1 for _, r in results if r is True)
    total = len([r for _, r in results if r is not None])

    print(f"\n通过率: {passed}/{total} ({passed/total*100:.1f}%)" if total > 0 else "\n无有效测试")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
