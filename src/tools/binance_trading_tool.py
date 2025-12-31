"""
币安交易工具
用于在币安交易所执行交易操作
支持现货和期货交易
"""

import os
import logging
from typing import Dict, Optional, Literal
from langchain.tools import tool
from cozeloop.decorator import observe

# 导入币安API库
from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException, BinanceOrderException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BinanceTrader:
    """币安交易客户端封装"""
    
    def __init__(self):
        """初始化币安客户端"""
        # 尝试从环境变量获取配置
        self.api_key = os.getenv("BINANCE_API_KEY")
        self.api_secret = os.getenv("BINANCE_API_SECRET")
        self.testnet = os.getenv("BINANCE_TESTNET", "true").lower() == "true"
        
        # 如果环境变量中没有配置,尝试从配置文件读取
        if not self.api_key or not self.api_secret:
            workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
            config_path = os.path.join(workspace_path, "config/binance_config.json")
            
            if os.path.exists(config_path):
                import json
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        self.api_key = config.get("api_key")
                        self.api_secret = config.get("api_secret")
                        self.testnet = config.get("testnet", True)
                except Exception as e:
                    logger.error(f"Failed to read binance config: {e}")
        
        # 验证配置
        if not self.api_key or not self.api_secret:
            logger.warning("Binance API credentials not configured properly")
        
        # 初始化客户端
        try:
            if self.testnet:
                # 使用测试网
                self.client = Client(
                    self.api_key,
                    self.api_secret,
                    testnet=True
                )
                logger.info("Binance client initialized with testnet")
            else:
                # 使用正式网
                self.client = Client(
                    self.api_key,
                    self.api_secret
                )
                logger.info("Binance client initialized with production")
        except Exception as e:
            logger.error(f"Failed to initialize Binance client: {e}")
            self.client = None
    
    @observe
    def place_spot_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: Optional[float] = None,
        price: Optional[float] = None,
        quote_order_qty: Optional[float] = None
    ) -> Dict:
        """
        下达现货订单
        
        Args:
            symbol: 交易对符号,如 'BTCUSDT'
            side: 订单方向 'BUY' 或 'SELL'
            order_type: 订单类型 'MARKET' 或 'LIMIT'
            quantity: 数量 (限价单必填)
            price: 价格 (仅限价单需要)
            quote_order_qty: 报价数量 (市价单可选,如用USDT金额购买)
        
        Returns:
            订单结果
        """
        if not self.client:
            return {
                "success": False,
                "error": "Binance client not initialized"
            }
        
        try:
            # 参数验证
            if side not in ['BUY', 'SELL']:
                return {
                    "success": False,
                    "error": f"Invalid side: {side}, must be 'BUY' or 'SELL'"
                }
            
            if order_type not in ['MARKET', 'LIMIT']:
                return {
                    "success": False,
                    "error": f"Invalid order_type: {order_type}, must be 'MARKET' or 'LIMIT'"
                }
            
            # 构建订单参数
            order_params = {
                'symbol': symbol.upper(),
                'side': side,
                'type': order_type
            }
            
            # 根据订单类型添加参数
            if order_type == 'LIMIT':
                if not quantity:
                    return {
                        "success": False,
                        "error": "LIMIT order requires 'quantity' parameter"
                    }
                if not price:
                    return {
                        "success": False,
                        "error": "LIMIT order requires 'price' parameter"
                    }
                order_params['quantity'] = quantity
                order_params['price'] = price
                order_params['timeInForce'] = 'GTC'  # Good Till Cancel
            else:  # MARKET
                if quantity:
                    order_params['quantity'] = quantity
                elif quote_order_qty:
                    order_params['quoteOrderQty'] = quote_order_qty
                else:
                    return {
                        "success": False,
                        "error": "MARKET order requires either 'quantity' or 'quote_order_qty' parameter"
                    }
            
            logger.info(f"Placing spot order: {order_params}")
            
            # 下单
            result = self.client.create_order(**order_params)
            
            logger.info(f"Order placed successfully: {result.get('orderId')}")
            
            return {
                "success": True,
                "order_id": result.get('orderId'),
                "symbol": result.get('symbol'),
                "side": result.get('side'),
                "type": result.get('type'),
                "quantity": result.get('executedQty'),
                "price": result.get('price'),
                "cummulative_quote_qty": result.get('cummulativeQuoteQty'),
                "status": result.get('status'),
                "transaction_time": result.get('transactTime')
            }
            
        except BinanceAPIException as e:
            logger.error(f"Binance API error: {e}")
            return {
                "success": False,
                "error": f"Binance API error: {e.message}",
                "code": e.code
            }
        except BinanceOrderException as e:
            logger.error(f"Binance order error: {e}")
            return {
                "success": False,
                "error": f"Binance order error: {e.message}"
            }
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    @observe
    def place_futures_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: Optional[float] = None,
        price: Optional[float] = None,
        quote_order_qty: Optional[float] = None,
        position_side: Optional[str] = None,
        leverage: Optional[int] = None
    ) -> Dict:
        """
        下达期货订单(USDT合约)
        
        Args:
            symbol: 交易对符号,如 'BTCUSDT'
            side: 订单方向 'BUY' 或 'SELL'
            order_type: 订单类型 'MARKET' 或 'LIMIT'
            quantity: 数量 (限价单必填)
            price: 价格 (仅限价单需要)
            quote_order_qty: 报价数量 (市价单可选)
            position_side: 持仓方向 'LONG' 或 'SHORT' (可选,默认为单边持仓模式)
            leverage: 杠杆倍数 (可选,下单前会设置杠杆)
        
        Returns:
            订单结果
        """
        if not self.client:
            return {
                "success": False,
                "error": "Binance client not initialized"
            }
        
        try:
            # 参数验证
            if side not in ['BUY', 'SELL']:
                return {
                    "success": False,
                    "error": f"Invalid side: {side}, must be 'BUY' or 'SELL'"
                }
            
            if order_type not in ['MARKET', 'LIMIT']:
                return {
                    "success": False,
                    "error": f"Invalid order_type: {order_type}, must be 'MARKET' or 'LIMIT'"
                }
            
            # 如果指定了杠杆,先设置杠杆
            if leverage and leverage > 0:
                logger.info(f"Setting leverage to {leverage}x for {symbol}")
                self.client.futures_change_leverage(
                    symbol=symbol.upper(),
                    leverage=leverage
                )
            
            # 构建订单参数
            order_params = {
                'symbol': symbol.upper(),
                'side': side,
                'type': order_type
            }
            
            # 添加持仓方向(如果指定)
            if position_side:
                order_params['positionSide'] = position_side.upper()
            
            # 根据订单类型添加参数
            if order_type == 'LIMIT':
                if not quantity:
                    return {
                        "success": False,
                        "error": "LIMIT order requires 'quantity' parameter"
                    }
                if not price:
                    return {
                        "success": False,
                        "error": "LIMIT order requires 'price' parameter"
                    }
                order_params['quantity'] = quantity
                order_params['price'] = price
                order_params['timeInForce'] = 'GTC'
            else:  # MARKET
                if quantity:
                    order_params['quantity'] = quantity
                elif quote_order_qty:
                    order_params['quoteOrderQty'] = quote_order_qty
                else:
                    return {
                        "success": False,
                        "error": "MARKET order requires either 'quantity' or 'quote_order_qty' parameter"
                    }
            
            logger.info(f"Placing futures order: {order_params}")
            
            # 下单
            result = self.client.futures_create_order(**order_params)
            
            logger.info(f"Futures order placed successfully: {result.get('orderId')}")
            
            return {
                "success": True,
                "order_id": result.get('orderId'),
                "symbol": result.get('symbol'),
                "side": result.get('side'),
                "type": result.get('type'),
                "quantity": result.get('executedQty'),
                "price": result.get('price'),
                "cummulative_quote_qty": result.get('cummulativeQuoteQty'),
                "status": result.get('status'),
                "transaction_time": result.get('transactTime'),
                "position_side": result.get('positionSide')
            }
            
        except BinanceAPIException as e:
            logger.error(f"Binance API error: {e}")
            return {
                "success": False,
                "error": f"Binance API error: {e.message}",
                "code": e.code
            }
        except BinanceOrderException as e:
            logger.error(f"Binance order error: {e}")
            return {
                "success": False,
                "error": f"Binance order error: {e.message}"
            }
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    @observe
    def get_account_balance(self, asset: Optional[str] = None) -> Dict:
        """
        获取账户余额(现货)
        
        Args:
            asset: 资产符号,如 'USDT'(可选)
        
        Returns:
            账户余额信息
        """
        if not self.client:
            return {
                "success": False,
                "error": "Binance client not initialized"
            }
        
        try:
            if asset:
                # 获取特定资产余额
                balance = self.client.get_asset_balance(asset=asset.upper())
                return {
                    "success": True,
                    "asset": balance.get('asset'),
                    "free": balance.get('free'),
                    "locked": balance.get('locked')
                }
            else:
                # 获取所有资产余额
                balances = self.client.get_account()['balances']
                # 只返回有余额的资产
                active_balances = [
                    {
                        "asset": b['asset'],
                        "free": b['free'],
                        "locked": b['locked']
                    }
                    for b in balances
                    if float(b['free']) > 0 or float(b['locked']) > 0
                ]
                return {
                    "success": True,
                    "balances": active_balances
                }
        except Exception as e:
            logger.error(f"Failed to get account balance: {e}")
            return {
                "success": False,
                "error": f"Failed to get account balance: {str(e)}"
            }


# 实例化币安交易客户端
_binance_trader = BinanceTrader()


@tool
def binance_spot_open_position(
    symbol: str,
    direction: str,
    amount: str,
    order_type: str = "MARKET",
    price: str = "",
    runtime=None
) -> str:
    """
    在币安现货市场开仓
    
    Args:
        symbol: 交易对符号,如 'BTCUSDT'、'ETHUSDT'
        direction: 交易方向, 'BUY'(做多/买入) 或 'SELL'(做空/卖出)
        amount: 交易数量或金额,如 '0.001'(BTC数量) 或 '100'(USDT金额)
        order_type: 订单类型, 'MARKET'(市价单) 或 'LIMIT'(限价单,默认MARKET)
        price: 限价单价格(仅限价单需要,如 '90000')
    
    Returns:
        订单执行结果
    """
    try:
        # 解析amount参数
        try:
            # 判断是数量还是金额
            if float(amount) < 100:  # 假设小于100的为数量(如BTC 0.001)
                quantity = float(amount)
                quote_order_qty = None
            else:  # 大于等于100的为金额(如USDT 100)
                quantity = None
                quote_order_qty = float(amount)
        except ValueError:
            return f"错误: 金额参数无效 - {amount}"
        
        # 映射方向
        side_map = {
            '做多': 'BUY',
            '买入': 'BUY',
            'buy': 'BUY',
            '做多方向': 'BUY',
            '做空': 'SELL',
            '卖出': 'SELL',
            'sell': 'SELL',
            '做空方向': 'SELL'
        }
        side = side_map.get(direction.lower(), direction.upper())
        
        # 映射订单类型
        order_type = order_type.upper()
        
        # 解析价格(限价单)
        price_float = None
        if order_type == 'LIMIT' and price:
            try:
                price_float = float(price)
            except ValueError:
                return f"错误: 价格参数无效 - {price}"
        
        # 执行订单
        result = _binance_trader.place_spot_order(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price_float,
            quote_order_qty=quote_order_qty
        )
        
        if result.get('success'):
            return (f"✅ 现货订单执行成功!\n"
                    f"订单ID: {result.get('order_id')}\n"
                    f"交易对: {result.get('symbol')}\n"
                    f"方向: {result.get('side')}\n"
                    f"类型: {result.get('type')}\n"
                    f"数量: {result.get('quantity')}\n"
                    f"价格: {result.get('price')}\n"
                    f"成交额: {result.get('cummulative_quote_qty')}\n"
                    f"状态: {result.get('status')}")
        else:
            return f"❌ 订单执行失败: {result.get('error')}"
            
    except Exception as e:
        logger.error(f"Error in binance_spot_open_position: {e}")
        return f"执行现货订单时出错: {str(e)}"


@tool
def binance_futures_open_position(
    symbol: str,
    direction: str,
    amount: str,
    order_type: str = "MARKET",
    price: str = "",
    leverage: str = "1",
    position_side: str = "",
    runtime=None
) -> str:
    """
    在币安期货市场开仓(USDT合约)
    
    Args:
        symbol: 交易对符号,如 'BTCUSDT'、'ETHUSDT'
        direction: 交易方向, 'BUY'(做多/买入) 或 'SELL'(做空/卖出)
        amount: 交易数量或金额,如 '0.001'(BTC数量) 或 '100'(USDT金额)
        order_type: 订单类型, 'MARKET'(市价单) 或 'LIMIT'(限价单,默认MARKET)
        price: 限价单价格(仅限价单需要,如 '90000')
        leverage: 杠杆倍数,如 '1', '5', '10', '20' (默认1倍)
        position_side: 持仓方向, 'LONG'(多头) 或 'SHORT'(空头), 可选
    
    Returns:
        订单执行结果
    """
    try:
        # 解析amount参数
        try:
            # 判断是数量还是金额
            if float(amount) < 100:  # 假设小于100的为数量(如BTC 0.001)
                quantity = float(amount)
                quote_order_qty = None
            else:  # 大于等于100的为金额(如USDT 100)
                quantity = None
                quote_order_qty = float(amount)
        except ValueError:
            return f"错误: 金额参数无效 - {amount}"
        
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
        side = side_map.get(direction.lower(), direction.upper())
        
        # 映射订单类型
        order_type = order_type.upper()
        
        # 解析价格(限价单)
        price_float = None
        if order_type == 'LIMIT' and price:
            try:
                price_float = float(price)
            except ValueError:
                return f"错误: 价格参数无效 - {price}"
        
        # 解析杠杆倍数
        try:
            leverage_int = int(leverage)
        except ValueError:
            return f"错误: 杠杆倍数参数无效 - {leverage}"
        
        # 映射持仓方向
        position_side_upper = None
        if position_side:
            position_side_upper = position_side.upper()
        
        # 执行订单
        result = _binance_trader.place_futures_order(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price_float,
            quote_order_qty=quote_order_qty,
            leverage=leverage_int,
            position_side=position_side_upper
        )
        
        if result.get('success'):
            return (f"✅ 期货订单执行成功!\n"
                    f"订单ID: {result.get('order_id')}\n"
                    f"交易对: {result.get('symbol')}\n"
                    f"方向: {result.get('side')}\n"
                    f"类型: {result.get('type')}\n"
                    f"数量: {result.get('quantity')}\n"
                    f"价格: {result.get('price')}\n"
                    f"成交额: {result.get('cummulative_quote_qty')}\n"
                    f"状态: {result.get('status')}\n"
                    f"持仓方向: {result.get('position_side')}")
        else:
            return f"❌ 订单执行失败: {result.get('error')}"
            
    except Exception as e:
        logger.error(f"Error in binance_futures_open_position: {f"Error in binance_futures_open_position: {e}"}")
        return f"执行期货订单时出错: {str(e)}"


@tool
def binance_get_balance(asset: str = "", runtime=None) -> str:
    """
    查询币安账户余额
    
    Args:
        asset: 资产符号,如 'USDT', 'BTC'(可选,不填则查询所有资产)
    
    Returns:
        账户余额信息
    """
    try:
        result = _binance_trader.get_account_balance(asset=asset if asset else None)
        
        if result.get('success'):
            if 'balances' in result:
                # 返回所有资产
                balance_info = []
                for b in result['balances']:
                    balance_info.append(
                        f"{b['asset']}: 可用 {b['free']}, 冻结 {b['locked']}"
                    )
                return "📊 账户余额:\n" + "\n".join(balance_info)
            else:
                # 返回单个资产
                return (f"📊 {result['asset']} 余额:\n"
                        f"可用: {result['free']}\n"
                        f"冻结: {result['locked']}")
        else:
            return f"❌ 查询余额失败: {result.get('error')}"
            
    except Exception as e:
        logger.error(f"Error in binance_get_balance: {e}")
        return f"查询余额时出错: {str(e)}"
