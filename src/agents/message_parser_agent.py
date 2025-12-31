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
            # 操作类型（新增）
            'operation_type': [
                r'平仓|离场|出局|了结|close|exit',  # 离场
                r'开仓|入场|建仓|买入|卖出|做多|做空|long|short|buy|sell'  # 开仓
            ],
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
            # 离场价格（新增）
            'exit_price': [
                r'离场价格[:：\s]*([0-9,.]+)\s*(U|USDT|USD)?',
                r'平仓价格[:：\s]*([0-9,.]+)\s*(U|USDT|USD)?',
                r'出局价格[:：\s]*([0-9,.]+)\s*(U|USDT|USD)?',
                r'close[:：\s]*([0-9,.]+)\s*(U|USDT|USD)?'
            ],
            # 盈亏信息（新增）
            'profit_loss': [
                r'盈利[:：\s]*([+-]?[0-9,.]+)\s*(U|USDT|USD|%)?',
                r'亏损[:：\s]*([+-]?[0-9,.]+)\s*(U|USDT|USD|%)?',
                r'盈亏[:：\s]*([+-]?[0-9,.]+)\s*(U|USDT|USD|%)?',
                r'获利[:：\s]*([+-]?[0-9,.]+)\s*(U|USDT|USD|%)?',
                r'profit[:：\s]*([+-]?[0-9,.]+)\s*(U|USDT|USD|%)?',
                r'pnl[:：\s]*([+-]?[0-9,.]+)\s*(U|USDT|USD|%)?'
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
            # 离场原因（新增）
            'exit_reason': [
                r'止盈离场',
                r'止损离场',
                r'手动离场',
                r'技术离场',
                r'风控离场'
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

    def extract_operation_type(self, text: str) -> str:
        """提取操作类型：开仓、补仓 或 离场"""
        # 先检查是否是补仓
        add_keywords = ['补仓', '加仓', 'add', 'add position', '加注']
        for keyword in add_keywords:
            if keyword in text:
                return '补仓'
        
        # 再检查是否是离场
        exit_keywords = ['平仓', '离场', '出局', '了结', 'close', 'exit']
        for keyword in exit_keywords:
            if keyword in text:
                return '离场'
        
        # 如果不是补仓也不是离场，则默认为开仓
        return '开仓'

    def extract_exit_price(self, text: str) -> Optional[str]:
        """提取离场价格"""
        for pattern in self.patterns['exit_price']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        return None

    def extract_profit_loss(self, text: str) -> Optional[str]:
        """提取盈亏信息"""
        for pattern in self.patterns['profit_loss']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        return None

    def extract_exit_reason(self, text: str) -> Optional[str]:
        """提取离场原因"""
        for pattern in self.patterns['exit_reason']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        # 如果消息中包含止盈相关关键词，则为止盈离场
        if re.search(r'止盈|目标达成', text, re.IGNORECASE):
            return '止盈离场'
        
        # 如果消息中包含止损相关关键词，则为止损离场
        if re.search(r'止损|风控', text, re.IGNORECASE):
            return '止损离场'
        
        # 默认为手动离场
        return None

    def parse(self, message_content: str, group_name: str, parent_order_id: str = None) -> Dict[str, Any]:
        """
        解析消息内容，提取订单信息

        Args:
            message_content: 消息内容
            group_name: 群名称
            parent_order_id: 父订单ID（补仓/离场时使用）

        Returns:
            解析结果
        """
        try:
            logger.info(f"开始解析消息: {message_content[:100]}...")

            # 提取操作类型（开仓/补仓/离场）
            operation_type = self.extract_operation_type(message_content)
            
            # 提取订单类型和方向
            order_type = self.extract_order_type(message_content)
            direction = self.extract_direction(message_content)
            
            # 根据操作类型提取不同的字段
            if operation_type == '离场':
                # 离场操作特有字段
                exit_price = self.extract_exit_price(message_content)
                profit_loss = self.extract_profit_loss(message_content)
                exit_reason = self.extract_exit_reason(message_content)
                
                # 离场时不需要入场金额、止盈、止损
                entry_amount = None
                take_profit = None
                stop_loss = None
                
                # 解析持仓数量和杠杆（从消息中提取）
                position_size = self._extract_position_size(message_content)
                leverage = self._extract_leverage(message_content)
                
            elif operation_type == '补仓':
                # 补仓操作特有字段
                entry_amount = self.extract_entry_amount(message_content)
                take_profit = self.extract_take_profit(message_content)
                stop_loss = None  # 补仓通常不单独设置止损
                
                # 补仓时不需要离场相关字段
                exit_price = None
                profit_loss = None
                exit_reason = None
                
                # 解析持仓数量和杠杆
                position_size = self._extract_position_size(message_content)
                leverage = self._extract_leverage(message_content)
                
            else:
                # 开仓操作字段
                entry_amount = self.extract_entry_amount(message_content)
                take_profit = self.extract_take_profit(message_content)
                stop_loss = self.extract_stop_loss(message_content)
                
                # 开仓时不需要离场相关字段
                exit_price = None
                profit_loss = None
                exit_reason = None
                
                # 解析持仓数量和杠杆
                position_size = self._extract_position_size(message_content)
                leverage = self._extract_leverage(message_content)
            
            # 生成订单ID
            import time
            timestamp = int(time.time())
            order_id = f"{order_type or 'TRADE'}-{direction or 'UNKNOWN'}-{timestamp}"
            
            # 如果是补仓或离场，必须提供父订单ID
            if operation_type in ['补仓', '离场'] and not parent_order_id:
                logger.warning(f"操作类型为{operation_type}，但未提供父订单ID")
            
            # 提取策略关键词
            strategy_keywords = self.extract_strategy_keywords(message_content)

            # 构建订单信息
            order_info = {
                "group_name": group_name,
                "message_content": message_content,
                "operation_type": operation_type,  # 开仓/补仓/离场
                "order_type": order_type,
                "direction": direction,
                "entry_amount": entry_amount,
                "take_profit": take_profit,
                "stop_loss": stop_loss,
                "exit_price": exit_price,
                "profit_loss": profit_loss,
                "exit_reason": exit_reason,
                "order_id": order_id,  # 订单唯一ID
                "parent_order_id": parent_order_id or "",  # 父订单ID
                "position_size": position_size,  # 持仓数量
                "leverage": leverage,  # 杠杆倍数
                "strategy_keywords": strategy_keywords,
                "parsed_at": datetime.now().isoformat()
            }

            logger.info("解析结果:")
            logger.info(f"  群名称: {order_info['group_name']}")
            logger.info(f"  操作类型: {order_info['operation_type']}")
            logger.info(f"  订单ID: {order_info['order_id']}")
            logger.info(f"  父订单ID: {order_info['parent_order_id']}")
            logger.info(f"  订单类型: {order_info['order_type']}")
            logger.info(f"  开仓方向: {order_info['direction']}")
            logger.info(f"  入场金额: {order_info['entry_amount']}")
            logger.info(f"  止盈: {order_info['take_profit']}")
            logger.info(f"  止损: {order_info['stop_loss']}")
            logger.info(f"  离场价格: {order_info['exit_price']}")
            logger.info(f"  盈亏信息: {order_info['profit_loss']}")
            logger.info(f"  离场原因: {order_info['exit_reason']}")
            logger.info(f"  持仓数量: {order_info['position_size']}")
            logger.info(f"  杠杆倍数: {order_info['leverage']}")
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
    
    def _extract_position_size(self, text: str) -> Optional[str]:
        """提取持仓数量"""
        patterns = [
            r'持仓[数量]*[:：\s]*([0-9,.]+)',
            r'数量[:：\s]*([0-9,.]+)',
            r'仓位[:：\s]*([0-9,.]+)',
            r'size[:：\s]*([0-9,.]+)',
            r'张数[:：\s]*([0-9,.]+)',
            r'([0-9,.]+)\s*(张|手|个|u)'
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    def _extract_leverage(self, text: str) -> Optional[str]:
        """提取杠杆倍数"""
        patterns = [
            r'杠杆[:：\s]*([0-9,.]+)[倍]*',
            r'leverage[:：\s]*([0-9,.]+)[x]*',
            r'([0-9,.]+)[x倍]*\s*杠杆',
            r'([0-9,.]+)[x] lever'
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None


def build_message_parser_agent():
    """
    构建消息解析 Agent

    Returns:
        MessageParserAgent 实例
    """
    return MessageParserAgent()
