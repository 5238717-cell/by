"""
消息解析模块
用于解析飞书群消息，提取订单相关信息
"""
import re
from typing import Dict, Optional, List
from dataclasses import dataclass


@dataclass
class OrderInfo:
    """订单信息数据类"""
    group_name: str  # 群名称
    message_content: str  # 消息内容
    order_type: Optional[str] = None  # 订单类型（如：买入、卖出、开仓、平仓等）
    direction: Optional[str] = None  # 开仓方向（如：做多、做空、long、short）
    entry_amount: Optional[str] = None  # 入场金额
    take_profit: Optional[str] = None  # 止盈
    stop_loss: Optional[str] = None  # 止损
    strategy_keywords: Optional[List[str]] = None  # 策略关键词


class MessageParser:
    """消息解析器"""

    def __init__(self):
        # 定义常见的关键词模式
        self.patterns = {
            # 订单类型关键词
            'order_type': [
                r'开仓', r'平仓', r'买入', r'卖出', r'做多', r'做空',
                r'long', r'short', r'buy', r'sell',
                r'入场', r'离场', r'建仓', r'撤仓'
            ],
            # 方向关键词
            'direction': [
                r'做多|看多|买入|long|buy',
                r'做空|看空|卖出|short|sell'
            ],
            # 金额相关的模式
            'amount': [
                r'入场[金额]*[:：\s]*([0-9,.]+)\s*(U|USDT|USD)?',
                r'投入[金额]*[:：\s]*([0-9,.]+)\s*(U|USDT|USD)?',
                r'仓位[:：\s]*([0-9,.]+)\s*(U|USDT|USD)?',
                r'金额[:：\s]*([0-9,.]+)\s*(U|USDT|USD)?'
            ],
            # 止盈模式
            'take_profit': [
                r'止盈[:：\s]*([0-9,.]+)\s*(%|U|USDT|USD)?',
                r'目标[:：\s]*([0-9,.]+)\s*(%|U|USDT|USD)?',
                r'盈利[:：\s]*([0-9,.]+)\s*(%|U|USDT|USD)?',
                r'tp[:：\s]*([0-9,.]+)\s*(%|U|USDT|USD)?'
            ],
            # 止损模式
            'stop_loss': [
                r'止损[:：\s]*([0-9,.]+)\s*(%|U|USDT|USD)?',
                r'风控[:：\s]*([0-9,.]+)\s*(%|U|USDT|USD)?',
                r'sl[:：\s]*([0-9,.]+)\s*(%|U|USDT|USD)?'
            ],
            # 策略关键词
            'strategy': [
                r'策略[:：\s]*(.+?)(?:\n|$)',
                r'strategy[:：\s]*(.+?)(?:\n|$)',
                r'交易计划[:：\s]*(.+?)(?:\n|$)'
            ]
        }

    def parse_message(self, message_content: str, group_name: str) -> OrderInfo:
        """
        解析消息内容

        Args:
            message_content: 消息内容
            group_name: 群名称

        Returns:
            OrderInfo: 解析后的订单信息
        """
        order_info = OrderInfo(
            group_name=group_name,
            message_content=message_content
        )

        # 提取订单类型
        order_info.order_type = self._extract_order_type(message_content)

        # 提取开仓方向
        order_info.direction = self._extract_direction(message_content)

        # 提取入场金额
        order_info.entry_amount = self._extract_entry_amount(message_content)

        # 提取止盈
        order_info.take_profit = self._extract_take_profit(message_content)

        # 提取止损
        order_info.stop_loss = self._extract_stop_loss(message_content)

        # 提取策略关键词
        order_info.strategy_keywords = self._extract_strategy_keywords(message_content)

        return order_info

    def _extract_order_type(self, text: str) -> Optional[str]:
        """提取订单类型"""
        for pattern in self.patterns['order_type']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        return None

    def _extract_direction(self, text: str) -> Optional[str]:
        """提取开仓方向"""
        # 做多/看多
        if re.search(r'做多|看多|long', text, re.IGNORECASE):
            return '做多'
        # 做空/看空
        elif re.search(r'做空|看空|short', text, re.IGNORECASE):
            return '做空'
        # 买入
        elif re.search(r'买入|buy', text, re.IGNORECASE):
            return '买入'
        # 卖出
        elif re.search(r'卖出|sell', text, re.IGNORECASE):
            return '卖出'
        return None

    def _extract_entry_amount(self, text: str) -> Optional[str]:
        """提取入场金额"""
        for pattern in self.patterns['amount']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # 返回完整匹配字符串，包含单位
                return match.group(0)
        return None

    def _extract_take_profit(self, text: str) -> Optional[str]:
        """提取止盈"""
        for pattern in self.patterns['take_profit']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        return None

    def _extract_stop_loss(self, text: str) -> Optional[str]:
        """提取止损"""
        for pattern in self.patterns['stop_loss']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        return None

    def _extract_strategy_keywords(self, text: str) -> List[str]:
        """提取策略关键词"""
        keywords = []

        # 查找策略相关关键词
        for pattern in self.patterns['strategy']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                keywords.append(match.group(1).strip())

        # 查找关键词标记
        keyword_matches = re.findall(r'关键词[:：\s]*([^\n]+)', text)
        keywords.extend(keyword_matches)

        return keywords if keywords else None

    def is_strategy_message(self, text: str) -> bool:
        """判断是否是策略消息"""
        # 检查是否包含"策略"关键词
        if re.search(r'策略|strategy|交易计划', text, re.IGNORECASE):
            return True

        # 检查是否包含交易相关信息
        trading_keywords = ['开仓', '平仓', '入场', '止盈', '止损', '仓位', '买入', '卖出']
        for keyword in trading_keywords:
            if keyword in text:
                return True

        return False


# 示例使用
if __name__ == "__main__":
    parser = MessageParser()

    # 测试用例
    test_message = """
    策略：BTC现货交易
    做多方向，入场金额：1000U
    止盈：20%
    止损：10%
    """

    result = parser.parse_message(test_message, "交易信号群")
    print("解析结果：")
    print(f"群名称: {result.group_name}")
    print(f"订单类型: {result.order_type}")
    print(f"开仓方向: {result.direction}")
    print(f"入场金额: {result.entry_amount}")
    print(f"止盈: {result.take_profit}")
    print(f"止损: {result.stop_loss}")
    print(f"策略关键词: {result.strategy_keywords}")
    print(f"是否策略消息: {parser.is_strategy_message(test_message)}")
