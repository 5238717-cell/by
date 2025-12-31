"""
自动交易工具
结合币安API和持仓跟踪，实现完整的开仓→跟踪→止盈→平仓流程
"""

import logging
from typing import Dict, Optional
from langchain.tools import tool
from cozeloop.decorator import observe

# 导入币安API工具
from tools.binance_trading_tool import _binance_trader

# 导入持仓跟踪工具
from tools.position_tracking_tool import _position_manager

# 导入飞书表格配置
from tools.feishu_bitable_tool import FEISHU_APP_TOKEN, FEISHU_TABLE_ID

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AutoTrader:
    """自动交易器"""
    
    def __init__(self):
        """初始化自动交易器"""
        self.binance_trader = _binance_trader
        self.position_manager = _position_manager
    
    @observe
    def auto_open_position(
        self,
        symbol: str,
        side: str,
        amount: str,
        order_type: str = "MARKET",
        price: str = "",
        leverage: str = "1",
        trade_type: str = "spot",
        take_profit_price: str = "",
        stop_loss_price: str = "",
        enable_tracking: bool = True
    ) -> Dict:
        """
        自动开仓并开始跟踪
        
        Args:
            symbol: 交易对符号
            side: 交易方向
            amount: 交易数量或金额
            order_type: 订单类型
            price: 限价单价格
            leverage: 杠杆倍数
            trade_type: 交易类型 (spot/futures)
            take_profit_price: 止盈价格
            stop_loss_price: 止损价格
            enable_tracking: 是否启用持仓跟踪
        
        Returns:
            交易结果
        """
        result = {
            "order_success": False,
            "tracking_success": False,
            "order_result": None,
            "tracking_result": None
        }
        
        # 步骤1: 在币安下单
        logger.info(f"Placing order on Binance: {symbol} {side} {amount}")
        
        if trade_type.lower() == "futures":
            order_result = self.binance_trader.place_futures_order(
                symbol=symbol,
                side=side,
                order_type=order_type,
                quote_order_qty=float(amount) if float(amount) > 100 else None,
                quantity=float(amount) if float(amount) < 100 else None,
                price=float(price) if price else None,
                leverage=int(leverage),
                position_side=None  # 不指定，使用默认
            )
        else:  # spot
            order_result = self.binance_trader.place_spot_order(
                symbol=symbol,
                side=side,
                order_type=order_type,
                quote_order_qty=float(amount) if float(amount) > 100 else None,
                quantity=float(amount) if float(amount) < 100 else None,
                price=float(price) if price else None
            )
        
        result["order_success"] = order_result.get("success", False)
        result["order_result"] = order_result
        
        if not result["order_success"]:
            return result
        
        # 步骤2: 创建持仓跟踪记录
        if enable_tracking:
            logger.info("Creating position tracking record")
            
            import time
            position_id = f"{symbol}-{side}-{int(time.time())}"
            
            # 获取实际成交价格
            executed_price = order_result.get("price")
            if not executed_price or executed_price == "0":
                # 如果没有成交价格，使用订单中指定的价格或市价估算
                if order_type == "MARKET" and price:
                    executed_price = str(float(price))
                elif order_type == "LIMIT":
                    executed_price = str(float(price))
                else:
                    # 无法获取价格，使用开仓金额和数量估算
                    executed_qty = order_result.get("quantity", "0")
                    executed_value = order_result.get("cummulative_quote_qty", "0")
                    if float(executed_qty) > 0:
                        executed_price = str(float(executed_value) / float(executed_qty))
                    else:
                        executed_price = "0"
            
            # 获取实际成交数量
            executed_qty = order_result.get("quantity", "0")
            if not executed_qty or executed_qty == "0":
                # 使用订单参数中的数量
                if executed_price and executed_price != "0":
                    executed_qty = str(float(amount) if float(amount) < 100 else float(amount) / float(executed_price))
                else:
                    executed_qty = "0"
            
            # 解析止盈止损价格
            tp_price = float(take_profit_price) if take_profit_price else None
            sl_price = float(stop_loss_price) if stop_loss_price else None
            
            tracking_result = self.position_manager.add_position(
                position_id=position_id,
                symbol=symbol.upper(),
                side=side,
                quantity=float(executed_qty),
                entry_price=float(executed_price) if executed_price else 0,
                trade_type=trade_type.lower(),
                leverage=int(leverage),
                take_profit_price=tp_price,
                stop_loss_price=sl_price
            )
            
            result["tracking_success"] = tracking_result.get("success", False)
            result["tracking_result"] = tracking_result
        
        return result
    
    @observe
    def auto_close_position(
        self,
        symbol: str,
        close_price: str = "",
        close_reason: str = "手动平仓",
        use_market_price: bool = True
    ) -> Dict:
        """
        自动平仓并计算收益
        
        Args:
            symbol: 交易对符号
            close_price: 平仓价格（如果不指定且use_market_price=True，则使用市价）
            close_reason: 平仓原因
            use_market_price: 是否使用市价平仓
        
        Returns:
            平仓结果
        """
        result = {
            "order_success": False,
            "tracking_success": False,
            "order_result": None,
            "tracking_result": None,
            "profit_loss": None,
            "profit_loss_percent": None
        }
        
        # 步骤1: 查找持仓
        position = self.position_manager.find_position_by_symbol(symbol, status="open")
        
        if not position:
            result["tracking_result"] = {
                "success": False,
                "error": f"未找到 {symbol} 的未平仓持仓"
            }
            return result
        
        position_id = position["position_id"]
        quantity = str(position["quantity"])
        side = "SELL" if position["side"] in ["BUY", "LONG"] else "BUY"
        
        # 步骤2: 在币安平仓
        actual_close_price = close_price
        
        if use_market_price and not close_price:
            # 使用市价平仓
            logger.info(f"Closing position with market order: {symbol} {side} {quantity}")
            
            if position["trade_type"] == "futures":
                order_result = self.binance_trader.place_futures_order(
                    symbol=symbol,
                    side=side,
                    order_type="MARKET",
                    quantity=float(quantity),
                    leverage=position.get("leverage", 1)
                )
            else:  # spot
                order_result = self.binance_trader.place_spot_order(
                    symbol=symbol,
                    side=side,
                    order_type="MARKET",
                    quantity=float(quantity)
                )
            
            result["order_success"] = order_result.get("success", False)
            result["order_result"] = order_result
            
            if result["order_success"]:
                # 获取实际成交价格
                actual_close_price = order_result.get("price")
                if not actual_close_price or actual_close_price == "0":
                    # 使用成交价值估算
                    executed_qty = order_result.get("quantity", "0")
                    executed_value = order_result.get("cummulative_quote_qty", "0")
                    if float(executed_qty) > 0:
                        actual_close_price = str(float(executed_value) / float(executed_qty))
        else:
            # 使用指定价格平仓（限价单）
            if close_price:
                logger.info(f"Closing position with limit order: {symbol} {side} {quantity} @ {close_price}")
                
                if position["trade_type"] == "futures":
                    order_result = self.binance_trader.place_futures_order(
                        symbol=symbol,
                        side=side,
                        order_type="LIMIT",
                        quantity=float(quantity),
                        price=float(close_price),
                        leverage=position.get("leverage", 1)
                    )
                else:  # spot
                    order_result = self.binance_trader.place_spot_order(
                        symbol=symbol,
                        side=side,
                        order_type="LIMIT",
                        quantity=float(quantity),
                        price=float(close_price)
                    )
                
                result["order_success"] = order_result.get("success", False)
                result["order_result"] = order_result
        
        # 步骤3: 更新持仓记录
        if result["order_success"] and actual_close_price:
            tracking_result = self.position_manager.close_position(
                position_id=position_id,
                close_price=float(actual_close_price),
                close_reason=close_reason
            )
            
            result["tracking_success"] = tracking_result.get("success", False)
            result["tracking_result"] = tracking_result
            
            if result["tracking_success"]:
                result["profit_loss"] = tracking_result["position"].get("actual_profit_loss")
                result["profit_loss_percent"] = tracking_result["position"].get("actual_profit_loss_percent")
        
        return result


# 实例化自动交易器
_auto_trader = AutoTrader()


@tool
def auto_open_and_track(
    symbol: str,
    side: str,
    amount: str,
    order_type: str = "MARKET",
    price: str = "",
    leverage: str = "1",
    trade_type: str = "spot",
    take_profit_price: str = "",
    stop_loss_price: str = "",
    record_id: str = "",  # 飞书表格记录ID，用于更新订单状态
    runtime=None
) -> str:
    """
    自动开仓并开始跟踪（结合币安API下单+持仓跟踪）
    
    Args:
        symbol: 交易对符号 (如: BTCUSDT, ETHUSDT)
        side: 交易方向 (BUY/做多/买入 或 SELL/做空/卖出)
        amount: 交易数量或金额 (如: 0.001或100)
        order_type: 订单类型 (MARKET-市价单 或 LIMIT-限价单, 默认MARKET)
        price: 限价单价格 (仅限价单需要, 如: 90000)
        leverage: 杠杆倍数 (如: 1, 5, 10, 默认1)
        trade_type: 交易类型 (spot-现货 或 futures-期货, 默认spot)
        take_profit_price: 止盈价格 (可选, 如: 92000)
        stop_loss_price: 止损价格 (可选, 如: 88000)
        record_id: 飞书表格记录ID (可选, 用于更新订单状态为"已下单")
    
    Returns:
        交易和跟踪结果
    """
    try:
        # 映射方向
        side_map = {
            '做多': 'BUY',
            '买入': 'BUY',
            'buy': 'BUY',
            'long': 'BUY',
            '做空': 'SELL',
            '卖出': 'SELL',
            'sell': 'SELL',
            'short': 'SELL'
        }
        side_upper = side_map.get(side.lower(), side.upper())
        
        # 执行自动开仓
        result = _auto_trader.auto_open_position(
            symbol=symbol,
            side=side_upper,
            amount=amount,
            order_type=order_type.upper(),
            price=price,
            leverage=leverage,
            trade_type=trade_type.lower(),
            take_profit_price=take_profit_price,
            stop_loss_price=stop_loss_price,
            enable_tracking=True
        )
        
        # 如果提供了record_id且交易成功，更新飞书表格状态
        update_status_result = ""
        if record_id and result["order_success"]:
            try:
                # 导入 update_order_status 工具
                from tools.feishu_bitable_tool import update_order_status
                
                # 获取实际成交价格和数量
                order_result = result.get("order_result", {})
                executed_price = order_result.get("price", "")
                executed_qty = order_result.get("quantity", "")
                
                # 生成订单ID
                import time
                order_id = f"{symbol}-{side_upper}-{int(time.time())}"
                
                # 使用 update_order_status 工具更新状态
                # 这个工具会自动检测是否有"状态"字段
                status_update = update_order_status(
                    record_id=record_id,
                    status="已下单",
                    order_id=order_id,
                    entry_price=executed_price,
                    position_size=executed_qty
                )
                
                if "Successfully" in status_update:
                    update_status_result = f"\n✅ **飞书表格状态已更新**: 状态改为'已下单'"
                else:
                    update_status_result = f"\n⚠️ **飞书表格状态更新失败**: {status_update}"
            except Exception as e:
                update_status_result = f"\n⚠️ **飞书表格状态更新失败**: {str(e)}"
        
        # 构建返回信息
        output_parts = []
        
        # 订单结果
        order_result = result.get("order_result", {})
        if result["order_success"]:
            output_parts.append(f"✅ **币安下单成功**")
            output_parts.append(f"订单ID: {order_result.get('order_id')}")
            output_parts.append(f"交易对: {order_result.get('symbol')}")
            output_parts.append(f"方向: {order_result.get('side')}")
            output_parts.append(f"类型: {order_result.get('type')}")
            output_parts.append(f"数量: {order_result.get('quantity')}")
            output_parts.append(f"成交价格: {order_result.get('price', '市价')}")
            output_parts.append(f"成交额: {order_result.get('cummulative_quote_qty')}")
            output_parts.append(f"状态: {order_result.get('status')}")
        else:
            output_parts.append(f"❌ **币安下单失败**: {order_result.get('error')}")
        
        output_parts.append("\n")
        
        # 持仓跟踪结果
        tracking_result = result.get("tracking_result", {})
        if result["tracking_success"]:
            position = tracking_result["position"]
            output_parts.append(f"✅ **持仓跟踪已创建**")
            output_parts.append(f"持仓ID: {position['position_id']}")
            output_parts.append(f"开仓价格: {position['entry_price']}")
            output_parts.append(f"开仓价值: {position['entry_value']:.2f} USDT")
            output_parts.append(f"止盈价格: {position['take_profit_price'] if position['take_profit_price'] else '未设置'}")
            output_parts.append(f"止损价格: {position['stop_loss_price'] if position['stop_loss_price'] else '未设置'}")
            output_parts.append(f"\n💡 **提示**: 当价格达到目标时,发送止盈指令即可自动平仓并计算收益。")
        else:
            output_parts.append(f"❌ **持仓跟踪创建失败**: {tracking_result.get('error')}")
        
        # 添加飞书表格更新结果
        if update_status_result:
            output_parts.append(update_status_result)
        
        return "\n".join(output_parts)
    
    except Exception as e:
        logger.error(f"Error in auto_open_and_track: {e}")
        return f"自动开仓时出错: {str(e)}"


@tool
def auto_close_and_calc_profit(
    symbol: str,
    close_price: str = "",
    close_reason: str = "手动平仓",
    use_market_price: bool = True,
    runtime=None
) -> str:
    """
    自动平仓并计算收益（结合币安API平仓+持仓记录更新）
    
    Args:
        symbol: 交易对符号 (如: BTCUSDT)
        close_price: 平仓价格 (如果不指定,则使用市价平仓)
        close_reason: 平仓原因 (如: 止盈平仓、止损平仓、手动平仓)
        use_market_price: 是否使用市价平仓 (默认True)
    
    Returns:
        平仓结果和收益分析
    """
    try:
        # 执行自动平仓
        result = _auto_trader.auto_close_position(
            symbol=symbol,
            close_price=close_price,
            close_reason=close_reason,
            use_market_price=use_market_price
        )
        
        # 构建返回信息
        output_parts = []
        
        # 检查持仓状态
        tracking_result = result.get("tracking_result", {})
        if not result.get("tracking_success") and "error" in tracking_result:
            return f"❌ {tracking_result.get('error')}\n\n💡 提示: 使用 get_open_positions 查看所有未平仓持仓。"
        
        # 订单结果
        order_result = result.get("order_result", {})
        if result["order_success"]:
            output_parts.append(f"✅ **币安平仓成功**")
            output_parts.append(f"订单ID: {order_result.get('order_id')}")
            output_parts.append(f"交易对: {order_result.get('symbol')}")
            output_parts.append(f"方向: {order_result.get('side')}")
            output_parts.append(f"数量: {order_result.get('quantity')}")
            output_parts.append(f"成交价格: {order_result.get('price', '市价')}")
            output_parts.append(f"成交额: {order_result.get('cummulative_quote_qty')}")
            output_parts.append(f"状态: {order_result.get('status')}")
        else:
            if "error" in order_result:
                output_parts.append(f"⚠️ **币安平仓订单失败**: {order_result.get('error')}")
        
        output_parts.append("\n")
        
        # 持仓更新和收益计算结果
        if result["tracking_success"]:
            position = tracking_result["position"]
            
            profit_loss = position.get('actual_profit_loss', 0)
            profit_loss_percent = position.get('actual_profit_loss_percent', 0)
            
            profit_emoji = "🟢" if profit_loss > 0 else "🔴" if profit_loss < 0 else "⚪"
            profit_status = "盈利" if profit_loss > 0 else "亏损" if profit_loss < 0 else "保本"
            
            output_parts.append(f"✅ **持仓已平仓并记录**")
            output_parts.append(f"\n📊 **交易详情**")
            output_parts.append(f"- 持仓ID: {position['position_id']}")
            output_parts.append(f"- 开仓价格: {position['entry_price']}")
            output_parts.append(f"- 平仓价格: {position['close_price']}")
            output_parts.append(f"- 开仓价值: {position['entry_value']:.2f} USDT")
            output_parts.append(f"- 平仓价值: {position['close_value']:.2f} USDT")
            output_parts.append(f"- 平仓原因: {position['close_reason']}")
            output_parts.append(f"- 开仓时间: {position['open_time']}")
            output_parts.append(f"- 平仓时间: {position['close_time']}")
            output_parts.append(f"- 杠杆: {position['leverage']}x")
            output_parts.append(f"\n{profit_emoji} **收益分析**")
            output_parts.append(f"- 收益状态: {profit_status}")
            output_parts.append(f"- 收益金额: {profit_loss:+.2f} USDT")
            output_parts.append(f"- 收益率: {profit_loss_percent:+.2f}%")
            output_parts.append(f"- 原始收益率: {position.get('profit_loss_percent', 0):+.2f}% (未计算杠杆)")
        else:
            output_parts.append(f"❌ **持仓更新失败**: {tracking_result.get('error')}")
        
        return "\n".join(output_parts)
    
    except Exception as e:
        logger.error(f"Error in auto_close_and_calc_profit: {e}")
        return f"自动平仓时出错: {str(e)}"
