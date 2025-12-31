"""
消息解析 Agent
功能：从消息内容中提取订单相关信息
"""
import re
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class MessageParserAgent:
    """消息解析 Agent"""

    def __init__(self):
        # 定义提取规则
        self.patterns = {
            # 订单类型
            'order_type': [
                r'开仓', r'平仓', r'买入', r'卖出', r'做多', r'做空',
                r'long', r'short', r'buy', r'sell',
                r'入场', r'离场', r'建仓', r'撤仓'
            ],
            # 方向
            'direction': [
                r'做多|看多|买入|long|buy',
                r'做空|看空|卖出|short|sell'
            ],
            # 金额
            'amount': [
                r'入场[金额]*[:：\s]*([0-9,.]+)\s*(U|USDT|USD)?',
                r'投入[金额]*[:：\s]*([0-9,.]+)\s*(U|USDT|USD)?',
                r'仓位[:：\s]*([0-9,.]+)\s*(U|USDT|USD)?',
                r'金额[:：\s]*([0-9,.]+)\s*(U|USDT|USD)?'
            ],
            # 止盈
            'take_profit': [
                r'止盈[:：\s]*([0-9,.]+)\s*(%|U|USDT|USD)?',
                r'目标[:：\s]*([0-9,.]+)\s*(%|U|USDT|USD)?',
                r'盈利[:：\s]*([0-9,.]+)\s*(%|U|USDT|USD)?',
                r'tp[:：\s]*([0-9,.]+)\s*(%|U|USDT|USD)?',
                r'目标位[:：\s]*([0-9,.]+)\s*(%|U|USDT|USD)?'
            ],
            # 止损
            'stop_loss': [
                r'止损[:：\s]*([0-9,.]+)\s*(%|U|USDT|USD)?',
                r'风控[:：\s]*([0-9,.]+)\s*(%|U|USDT|USD)?',
                r'sl[:：\s]*([0-9,.]+)\s*(%|U|USDT|USD)?',
                r'止损位[:：\s]*([0-9,.]+)\s*(%|U|USDT|USD)?'
            ],
            # 策略关键词
            'strategy': [
                r'策略[:：\s]*(.+?)(?:\n|$)',
                r'strategy[:：\s]*(.+?)(?:\n|$)',
                r'交易计划[:：\s]*(.+?)(?:\n|$)'
            ]
        }

    def extract_order_type(self, text: str) -> Optional[str]:
        """提取订单类型"""
        for pattern in self.patterns['order_type']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        return None

    def extract_direction(self, text: str) -> Optional[str]:
        """提取开仓方向"""
        if re.search(r'做多|看多|long', text, re.IGNORECASE):
            return '做多'
        elif re.search(r'做空|看空|short', text, re.IGNORECASE):
            return '做空'
        elif re.search(r'买入|buy', text, re.IGNORECASE):
            return '买入'
        elif re.search(r'卖出|sell', text, re.IGNORECASE):
            return '卖出'
        return None

    def extract_entry_amount(self, text: str) -> Optional[str]:
        """提取入场金额"""
        for pattern in self.patterns['amount']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # 返回完整的匹配字符串
                full_match = match.group(0)
                return full_match
        return None

    def extract_take_profit(self, text: str) -> Optional[str]:
        """提取止盈"""
        for pattern in self.patterns['take_profit']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        return None

    def extract_stop_loss(self, text: str) -> Optional[str]:
        """提取止损"""
        for pattern in self.patterns['stop_loss']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        return None

    def extract_strategy_keywords(self, text: str) -> List[str]:
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

    def parse(self, message_content: str, group_name: str) -> Dict[str, Any]:
        """
        解析消息内容，提取订单信息

        Args:
            message_content: 消息内容
            group_name: 群名称

        Returns:
            解析结果
        """
        try:
            logger.info(f"开始解析消息: {message_content[:100]}...")

            # 提取各字段
            order_type = self.extract_order_type(message_content)
            direction = self.extract_direction(message_content)
            entry_amount = self.extract_entry_amount(message_content)
            take_profit = self.extract_take_profit(message_content)
            stop_loss = self.extract_stop_loss(message_content)
            strategy_keywords = self.extract_strategy_keywords(message_content)

            # 构建订单信息
            order_info = {
                "group_name": group_name,
                "message_content": message_content,
                "order_type": order_type,
                "direction": direction,
                "entry_amount": entry_amount,
                "take_profit": take_profit,
                "stop_loss": stop_loss,
                "strategy_keywords": strategy_keywords,
                "parsed_at": datetime.now().isoformat()
            }

            logger.info("解析结果:")
            logger.info(f"  群名称: {order_info['group_name']}")
            logger.info(f"  订单类型: {order_info['order_type']}")
            logger.info(f"  开仓方向: {order_info['direction']}")
            logger.info(f"  入场金额: {order_info['entry_amount']}")
            logger.info(f"  止盈: {order_info['take_profit']}")
            logger.info(f"  止损: {order_info['stop_loss']}")
            logger.info(f"  策略关键词: {order_info['strategy_keywords']}")

            return {
                "success": True,
                "order_info": order_info
            }

        except Exception as e:
            logger.error(f"解析消息时出错: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }


def build_message_parser_agent():
    """
    构建消息解析 Agent

    Returns:
        MessageParserAgent 实例
    """
    return MessageParserAgent()
