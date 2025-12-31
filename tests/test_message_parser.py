"""
消息解析模块测试脚本
测试消息解析功能，验证能否正确提取订单信息
"""
import sys
import os

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tools.message_parser import MessageParser, OrderInfo


def test_message_parser():
    """测试消息解析功能"""

    print("=" * 60)
    print("消息解析模块测试")
    print("=" * 60)

    parser = MessageParser()

    # 测试用例列表
    test_cases = [
        {
            "name": "标准策略消息",
            "message": """策略：BTC现货交易
做多方向，入场金额：1000U
止盈：20%
止损：10%""",
            "expected": {
                "order_type": "入场",
                "direction": "做多",
                "entry_amount": "入场金额：1000U",
                "take_profit": "止盈：20%",
                "stop_loss": "止损：10%"
            }
        },
        {
            "name": "英文关键词消息",
            "message": """Strategy: ETH 4h breakout
Long position, Entry: 5000U
TP: 10%
SL: 5%""",
            "expected": {
                "order_type": None,  # 英文可能不匹配
                "direction": None,
                "entry_amount": None,
                "take_profit": "TP: 10%",
                "stop_loss": "SL: 5%"
            }
        },
        {
            "name": "开仓信号消息",
            "message": """【开仓信号】
品种：BTC/USDT
方向：做空
入场金额：2000U
入场位置：97000
目标位：95000
止损位：98500""",
            "expected": {
                "order_type": "开仓",
                "direction": "做空",
                "entry_amount": "入场金额：2000U",
                "take_profit": "目标位：95000",
                "stop_loss": "止损位：98500"
            }
        },
        {
            "name": "简单交易消息",
            "message": """买入BTC，入场金额500U，止盈10%，止损5%""",
            "expected": {
                "order_type": "买入",
                "direction": "买入",
                "entry_amount": "入场金额500U",
                "take_profit": "止盈10%",
                "stop_loss": "止损5%"
            }
        },
        {
            "name": "普通聊天消息（非策略）",
            "message": """今天天气不错，大家一起出去玩吧！""",
            "expected": {
                "is_strategy": False
            }
        }
    ]

    # 运行测试
    success_count = 0
    total_count = len(test_cases)

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {test_case['name']}")
        print("-" * 60)

        message = test_case["message"]
        expected = test_case["expected"]

        # 判断是否策略消息
        is_strategy = parser.is_strategy_message(message)

        if "is_strategy" in expected:
            # 测试策略判断
            if is_strategy == expected["is_strategy"]:
                print(f"✓ 策略判断正确: {is_strategy}")
                success_count += 1
            else:
                print(f"✗ 策略判断错误: 期望 {expected['is_strategy']}, 实际 {is_strategy}")
        else:
            # 解析消息
            result = parser.parse_message(message, "测试群")

            print(f"原始消息: {message[:100]}...")
            print(f"解析结果:")
            print(f"  订单类型: {result.order_type}")
            print(f"  开仓方向: {result.direction}")
            print(f"  入场金额: {result.entry_amount}")
            print(f"  止盈: {result.take_profit}")
            print(f"  止损: {result.stop_loss}")
            print(f"  策略关键词: {result.strategy_keywords}")

            # 验证解析结果（宽松匹配）
            test_passed = True

            for key, expected_value in expected.items():
                actual_value = getattr(result, key)
                if expected_value and actual_value:
                    if expected_value in actual_value:
                        print(f"  ✓ {key}: 匹配")
                    else:
                        print(f"  ⚠ {key}: 部分匹配 (期望: {expected_value}, 实际: {actual_value})")
                        test_passed = False
                elif not expected_value and not actual_value:
                    print(f"  ✓ {key}: 都为空")
                else:
                    print(f"  ⚠ {key}: 不匹配 (期望: {expected_value}, 实际: {actual_value})")
                    test_passed = False

            if test_passed:
                print("✓ 测试通过")
                success_count += 1
            else:
                print("⚠ 测试部分通过")

    # 输出测试结果
    print("\n" + "=" * 60)
    print(f"测试结果: {success_count}/{total_count} 通过")
    print("=" * 60)

    return success_count == total_count


if __name__ == "__main__":
    try:
        success = test_message_parser()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n测试执行出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
