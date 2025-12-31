"""
持仓状态管理工具
用于跟踪当前的持仓信息，支持开仓、平仓、止盈操作
"""

import os
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
from langchain.tools import tool
from cozeloop.decorator import observe

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PositionManager:
    """持仓状态管理器"""
    
    def __init__(self):
        """初始化持仓管理器"""
        self.workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
        self.positions_file = os.path.join(self.workspace_path, "assets/positions.json")
        self._ensure_file_exists()
        self.positions = self._load_positions()
    
    def _ensure_file_exists(self):
        """确保持仓文件存在"""
        if not os.path.exists(os.path.dirname(self.positions_file)):
            os.makedirs(os.path.dirname(self.positions_file), exist_ok=True)
        
        if not os.path.exists(self.positions_file):
            self._save_positions({})
    
    def _load_positions(self) -> Dict:
        """加载持仓数据"""
        try:
            with open(self.positions_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load positions: {e}")
            return {}
    
    def _save_positions(self, positions: Dict):
        """保存持仓数据"""
        try:
            with open(self.positions_file, 'w', encoding='utf-8') as f:
                json.dump(positions, f, ensure_ascii=False, indent=2)
            self.positions = positions
        except Exception as e:
            logger.error(f"Failed to save positions: {e}")
    
    @observe
    def add_position(
        self,
        position_id: str,
        symbol: str,
        side: str,
        quantity: float,
        entry_price: float,
        trade_type: str = "spot",
        leverage: int = 1,
        take_profit_price: Optional[float] = None,
        stop_loss_price: Optional[float] = None
    ) -> Dict:
        """
        添加新持仓
        
        Args:
            position_id: 持仓唯一ID
            symbol: 交易对符号
            side: 持仓方向 (BUY/SELL 或 LONG/SHORT)
            quantity: 持仓数量
            entry_price: 开仓价格
            trade_type: 交易类型 (spot/futures)
            leverage: 杠杆倍数
            take_profit_price: 止盈价格
            stop_loss_price: 止损价格
        
        Returns:
            持仓信息
        """
        try:
            position = {
                "position_id": position_id,
                "symbol": symbol,
                "side": side,
                "quantity": quantity,
                "entry_price": entry_price,
                "entry_value": entry_price * quantity,
                "trade_type": trade_type,
                "leverage": leverage,
                "take_profit_price": take_profit_price,
                "stop_loss_price": stop_loss_price,
                "status": "open",  # open, closed
                "open_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "close_time": None,
                "close_price": None,
                "close_value": None,
                "profit_loss": None,
                "profit_loss_percent": None
            }
            
            self.positions[position_id] = position
            self._save_positions(self.positions)
            
            logger.info(f"Position added: {position_id}")
            return {
                "success": True,
                "position": position
            }
        except Exception as e:
            logger.error(f"Failed to add position: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @observe
    def close_position(
        self,
        position_id: str,
        close_price: float,
        close_reason: str = ""
    ) -> Dict:
        """
        关闭持仓
        
        Args:
            position_id: 持仓ID
            close_price: 平仓价格
            close_reason: 平仓原因
        
        Returns:
            平仓结果
        """
        try:
            if position_id not in self.positions:
                return {
                    "success": False,
                    "error": f"Position {position_id} not found"
                }
            
            position = self.positions[position_id]
            
            if position["status"] == "closed":
                return {
                    "success": False,
                    "error": f"Position {position_id} already closed"
                }
            
            # 计算盈亏
            entry_price = position["entry_price"]
            quantity = position["quantity"]
            entry_value = position["entry_value"]
            
            close_value = close_price * quantity
            
            # 根据方向计算盈亏
            if position["side"] in ["BUY", "LONG"]:
                profit_loss = close_value - entry_value
            else:  # SELL, SHORT
                profit_loss = entry_value - close_value
            
            profit_loss_percent = (profit_loss / entry_value) * 100
            
            # 考虑杠杆倍数
            actual_profit_loss = profit_loss * position["leverage"]
            actual_profit_loss_percent = profit_loss_percent * position["leverage"]
            
            # 更新持仓状态
            position["status"] = "closed"
            position["close_price"] = close_price
            position["close_value"] = close_value
            position["close_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            position["close_reason"] = close_reason
            position["profit_loss"] = profit_loss
            position["profit_loss_percent"] = profit_loss_percent
            position["actual_profit_loss"] = actual_profit_loss
            position["actual_profit_loss_percent"] = actual_profit_loss_percent
            
            self.positions[position_id] = position
            self._save_positions(self.positions)
            
            logger.info(f"Position closed: {position_id}, Profit: {actual_profit_loss}")
            
            return {
                "success": True,
                "position": position
            }
        except Exception as e:
            logger.error(f"Failed to close position: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @observe
    def get_position(self, position_id: str) -> Optional[Dict]:
        """
        获取指定持仓信息
        
        Args:
            position_id: 持仓ID
        
        Returns:
            持仓信息
        """
        return self.positions.get(position_id)
    
    @observe
    def get_open_positions(self) -> List[Dict]:
        """
        获取所有未平仓的持仓
        
        Returns:
            未平仓持仓列表
        """
        return [pos for pos in self.positions.values() if pos["status"] == "open"]
    
    @observe
    def get_all_positions(self) -> List[Dict]:
        """
        获取所有持仓
        
        Returns:
            所有持仓列表
        """
        return list(self.positions.values())
    
    @observe
    def update_position(
        self,
        position_id: str,
        **kwargs
    ) -> Dict:
        """
        更新持仓信息
        
        Args:
            position_id: 持仓ID
            **kwargs: 要更新的字段
        
        Returns:
            更新结果
        """
        try:
            if position_id not in self.positions:
                return {
                    "success": False,
                    "error": f"Position {position_id} not found"
                }
            
            position = self.positions[position_id]
            
            for key, value in kwargs.items():
                if key in position:
                    position[key] = value
            
            self.positions[position_id] = position
            self._save_positions(self.positions)
            
            return {
                "success": True,
                "position": position
            }
        except Exception as e:
            logger.error(f"Failed to update position: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @observe
    def find_position_by_symbol(self, symbol: str, status: str = "open") -> Optional[Dict]:
        """
        根据交易对查找持仓
        
        Args:
            symbol: 交易对符号
            status: 持仓状态 (open/closed)
        
        Returns:
            持仓信息
        """
        for pos in self.positions.values():
            if pos["symbol"].upper() == symbol.upper() and pos["status"] == status:
                return pos
        return None


# 实例化持仓管理器
_position_manager = PositionManager()


@tool
def open_tracking_position(
    symbol: str,
    side: str,
    quantity: str,
    entry_price: str,
    trade_type: str = "spot",
    leverage: str = "1",
    take_profit_price: str = "",
    stop_loss_price: str = "",
    runtime=None
) -> str:
    """
    开仓并开始跟踪持仓
    
    Args:
        symbol: 交易对符号 (如: BTCUSDT, ETHUSDT)
        side: 持仓方向 (BUY/做多/买入 或 SELL/做空/卖出)
        quantity: 持仓数量 (如: 0.001)
        entry_price: 开仓价格 (如: 90000)
        trade_type: 交易类型 (spot-现货 或 futures-期货, 默认spot)
        leverage: 杠杆倍数 (如: 1, 5, 10, 默认1)
        take_profit_price: 止盈价格 (可选, 如: 92000)
        stop_loss_price: 止损价格 (可选, 如: 88000)
    
    Returns:
        持仓信息
    """
    try:
        # 生成持仓ID
        import time
        position_id = f"{symbol}-{side}-{int(time.time())}"
        
        # 解析参数
        side_map = {
            '做多': 'BUY',
            '买入': 'BUY',
            'buy': 'BUY',
            'long': 'LONG',
            '做空': 'SELL',
            '卖出': 'SELL',
            'sell': 'SELL',
            'short': 'SHORT'
        }
        side_upper = side_map.get(side.lower(), side.upper())
        
        # 解析止盈止损价格
        tp_price = float(take_profit_price) if take_profit_price else None
        sl_price = float(stop_loss_price) if stop_loss_price else None
        
        # 添加持仓
        result = _position_manager.add_position(
            position_id=position_id,
            symbol=symbol.upper(),
            side=side_upper,
            quantity=float(quantity),
            entry_price=float(entry_price),
            trade_type=trade_type.lower(),
            leverage=int(leverage),
            take_profit_price=tp_price,
            stop_loss_price=sl_price
        )
        
        if result.get('success'):
            position = result['position']
            return (f"✅ 持仓已创建并开始跟踪!\n\n"
                    f"📊 **持仓信息**\n"
                    f"- 持仓ID: {position['position_id']}\n"
                    f"- 交易对: {position['symbol']}\n"
                    f"- 方向: {position['side']}\n"
                    f"- 数量: {position['quantity']}\n"
                    f"- 开仓价格: {position['entry_price']}\n"
                    f"- 开仓价值: {position['entry_value']:.2f} USDT\n"
                    f"- 交易类型: {'现货' if position['trade_type'] == 'spot' else '期货'}\n"
                    f"- 杠杆: {position['leverage']}x\n"
                    f"- 止盈价格: {position['take_profit_price'] if position['take_profit_price'] else '未设置'}\n"
                    f"- 止损价格: {position['stop_loss_price'] if position['stop_loss_price'] else '未设置'}\n"
                    f"- 开仓时间: {position['open_time']}\n\n"
                    f"💡 **提示**: 当价格达到止盈/止损价格时,您可以发送止盈/止损指令,系统将自动平仓并计算收益。")
        else:
            return f"❌ 创建持仓失败: {result.get('error')}"
    
    except Exception as e:
        logger.error(f"Error in open_tracking_position: {e}")
        return f"创建持仓时出错: {str(e)}"


@tool
def close_tracking_position(
    symbol: str,
    close_price: str,
    close_reason: str = "手动平仓",
    runtime=None
) -> str:
    """
    平仓并计算收益
    
    Args:
        symbol: 交易对符号 (如: BTCUSDT)
        close_price: 平仓价格 (如: 92000)
        close_reason: 平仓原因 (如: 止盈平仓、止损平仓、手动平仓)
    
    Returns:
        平仓结果和收益信息
    """
    try:
        # 查找未平仓的持仓
        position = _position_manager.find_position_by_symbol(symbol, status="open")
        
        if not position:
            return f"❌ 未找到 {symbol} 的未平仓持仓。\n\n💡 提示: 请使用 get_open_positions 查看所有未平仓持仓。"
        
        position_id = position['position_id']
        
        # 平仓
        result = _position_manager.close_position(
            position_id=position_id,
            close_price=float(close_price),
            close_reason=close_reason
        )
        
        if result.get('success'):
            position = result['position']
            
            # 格式化盈亏信息
            profit_loss = position.get('actual_profit_loss', 0)
            profit_loss_percent = position.get('actual_profit_loss_percent', 0)
            
            profit_emoji = "🟢" if profit_loss > 0 else "🔴" if profit_loss < 0 else "⚪"
            profit_status = "盈利" if profit_loss > 0 else "亏损" if profit_loss < 0 else "保本"
            
            return (f"✅ 持仓已平仓!\n\n"
                    f"📊 **持仓详情**\n"
                    f"- 持仓ID: {position['position_id']}\n"
                    f"- 交易对: {position['symbol']}\n"
                    f"- 方向: {position['side']}\n"
                    f"- 数量: {position['quantity']}\n"
                    f"- 开仓价格: {position['entry_price']}\n"
                    f"- 平仓价格: {position['close_price']}\n"
                    f"- 开仓价值: {position['entry_value']:.2f} USDT\n"
                    f"- 平仓价值: {position['close_value']:.2f} USDT\n"
                    f"- 开仓时间: {position['open_time']}\n"
                    f"- 平仓时间: {position['close_time']}\n"
                    f"- 平仓原因: {position['close_reason']}\n"
                    f"- 交易类型: {'现货' if position['trade_type'] == 'spot' else '期货'}\n"
                    f"- 杠杆: {position['leverage']}x\n\n"
                    f"{profit_emoji} **收益分析**\n"
                    f"- 收益状态: {profit_status}\n"
                    f"- 收益金额: {profit_loss:+.2f} USDT\n"
                    f"- 收益率: {profit_loss_percent:+.2f}%\n"
                    f"- 原始收益率: {position.get('profit_loss_percent', 0):+.2f}% (未计算杠杆)")
        else:
            return f"❌ 平仓失败: {result.get('error')}"
    
    except Exception as e:
        logger.error(f"Error in close_tracking_position: {e}")
        return f"平仓时出错: {str(e)}"


@tool
def get_open_positions(runtime=None) -> str:
    """
    获取所有未平仓的持仓
    
    Returns:
        未平仓持仓列表
    """
    try:
        positions = _position_manager.get_open_positions()
        
        if not positions:
            return "📋 当前没有未平仓的持仓。"
        
        result = [f"📋 未平仓持仓列表 ({len(positions)} 个持仓)\n"]
        
        for i, pos in enumerate(positions, 1):
            entry_value = pos.get('entry_value', 0)
            current_value = entry_value  # 假设当前价值等于开仓价值,实际应查询实时价格
            
            result.append(f"\n**持仓 {i}**")
            result.append(f"- 持仓ID: {pos['position_id']}")
            result.append(f"- 交易对: {pos['symbol']}")
            result.append(f"- 方向: {pos['side']}")
            result.append(f"- 数量: {pos['quantity']}")
            result.append(f"- 开仓价格: {pos['entry_price']}")
            result.append(f"- 开仓价值: {entry_value:.2f} USDT")
            result.append(f"- 交易类型: {'现货' if pos['trade_type'] == 'spot' else '期货'}")
            result.append(f"- 杠杆: {pos['leverage']}x")
            
            if pos.get('take_profit_price'):
                result.append(f"- 止盈价格: {pos['take_profit_price']}")
            
            if pos.get('stop_loss_price'):
                result.append(f"- 止损价格: {pos['stop_loss_price']}")
            
            result.append(f"- 开仓时间: {pos['open_time']}")
        
        return "\n".join(result)
    
    except Exception as e:
        logger.error(f"Error in get_open_positions: {e}")
        return f"查询持仓时出错: {str(e)}"


@tool
def get_position_history(limit: str = "10", runtime=None) -> str:
    """
    获取历史持仓记录
    
    Args:
        limit: 返回记录数量 (默认10)
    
    Returns:
        历史持仓列表
    """
    try:
        positions = _position_manager.get_all_positions()
        
        # 过滤已平仓的持仓
        closed_positions = [pos for pos in positions if pos['status'] == 'closed']
        
        # 按平仓时间倒序排列
        closed_positions.sort(key=lambda x: x.get('close_time', ''), reverse=True)
        
        # 限制返回数量
        limit_int = int(limit)
        closed_positions = closed_positions[:limit_int]
        
        if not closed_positions:
            return "📋 暂无历史持仓记录。"
        
        result = [f"📋 历史持仓记录 (最近 {len(closed_positions)} 条)\n"]
        
        for i, pos in enumerate(closed_positions, 1):
            profit_loss = pos.get('actual_profit_loss', 0)
            profit_loss_percent = pos.get('actual_profit_loss_percent', 0)
            profit_emoji = "🟢" if profit_loss > 0 else "🔴" if profit_loss < 0 else "⚪"
            
            result.append(f"\n**持仓 {i}** {profit_emoji}")
            result.append(f"- 持仓ID: {pos['position_id']}")
            result.append(f"- 交易对: {pos['symbol']}")
            result.append(f"- 方向: {pos['side']}")
            result.append(f"- 开仓价格: {pos['entry_price']}")
            result.append(f"- 平仓价格: {pos['close_price']}")
            result.append(f"- 收益: {profit_loss:+.2f} USDT ({profit_loss_percent:+.2f}%)")
            result.append(f"- 平仓原因: {pos['close_reason']}")
            result.append(f"- 平仓时间: {pos['close_time']}")
        
        # 计算总收益
        total_profit = sum(pos.get('actual_profit_loss', 0) for pos in closed_positions)
        total_emoji = "🟢" if total_profit > 0 else "🔴" if total_profit < 0 else "⚪"
        result.append(f"\n**总收益** {total_emoji}: {total_profit:+.2f} USDT")
        
        return "\n".join(result)
    
    except Exception as e:
        logger.error(f"Error in get_position_history: {e}")
        return f"查询历史持仓时出错: {str(e)}"
