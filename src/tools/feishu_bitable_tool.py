"""
飞书多维表格操作工具
用于读取、写入飞书多维表格中的交易数据
"""

import logging
from typing import Dict, List, Optional
from langchain.tools import tool
from cozeloop.decorator import observe
from coze_workload_identity import Client
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FeishuBitable:
    """飞书多维表格客户端封装"""
    
    def __init__(self):
        self.base_url = "https://open.larkoffice.com/open-apis"
        self.timeout = 30
        self.access_token = self._get_access_token()
    
    def _get_access_token(self) -> str:
        """获取飞书多维表格访问令牌"""
        try:
            client = Client()
            access_token = client.get_integration_credential("integration-feishu-base")
            if not access_token:
                raise ValueError("Failed to get Feishu access token")
            return access_token
        except Exception as e:
            logger.error(f"Failed to get Feishu access token: {e}")
            raise
    
    def _headers(self) -> Dict[str, str]:
        """生成请求头"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json; charset=utf-8",
        }
    
    @observe
    def _request(
        self, 
        method: str, 
        path: str, 
        params: Optional[Dict] = None, 
        json: Optional[Dict] = None
    ) -> Dict:
        """发送HTTP请求"""
        try:
            url = f"{self.base_url}{path}"
            resp = requests.request(
                method, 
                url, 
                headers=self._headers(), 
                params=params, 
                json=json, 
                timeout=self.timeout
            )
            resp_data = resp.json()
            
            if resp_data.get("code") != 0:
                error_msg = f"Feishu API error: {resp_data.get('msg')}, code: {resp_data.get('code')}"
                logger.error(error_msg)
                raise Exception(error_msg)
                
            return resp_data
        except requests.exceptions.RequestException as e:
            logger.error(f"Feishu API request error: {e}")
            raise Exception(f"Feishu API request error: {e}")
    
    def list_fields(self, app_token: str, table_id: str) -> List[Dict]:
        """获取表格字段列表"""
        result = self._request(
            "GET", 
            f"/bitable/v1/apps/{app_token}/tables/{table_id}/fields"
        )
        return result.get("data", {}).get("items", [])
    
    def add_records(
        self, 
        app_token: str, 
        table_id: str, 
        records: List[Dict]
    ) -> Dict:
        """批量添加记录"""
        body = {"records": records}
        result = self._request(
            "POST",
            f"/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_create",
            json=body
        )
        return result
    
    def search_records(
        self,
        app_token: str,
        table_id: str,
        filter_conditions: Optional[Dict] = None,
        page_size: int = 100
    ) -> Dict:
        """搜索记录"""
        body = {}
        if filter_conditions:
            body["filter"] = filter_conditions
        
        result = self._request(
            "POST",
            f"/bitable/v1/apps/{app_token}/tables/{table_id}/records/search",
            params={"page_size": page_size},
            json=body
        )
        return result


# 实例化客户端
_feishu_client = FeishuBitable()

# 从用户提供的URL中提取的配置
FEISHU_APP_TOKEN = "XwwsbHItual39JsHxqzcERL9nnp"
FEISHU_TABLE_ID = "tbltsL5mQlzsBTWm"


@tool
def get_table_fields(runtime=None) -> str:
    """
    获取飞书多维表格的字段信息
    
    Returns:
        字段信息的JSON字符串
    """
    try:
        fields = _feishu_client.list_fields(FEISHU_APP_TOKEN, FEISHU_TABLE_ID)
        field_info = []
        for field in fields:
            field_info.append({
                "field_name": field.get("field_name"),
                "field_id": field.get("field_id"),
                "type": field.get("type")
            })
        
        logger.info(f"Got {len(field_info)} fields from table")
        return f"Table fields: {field_info}"
    except Exception as e:
        error_msg = f"Failed to get table fields: {str(e)}"
        logger.error(error_msg)
        return error_msg


@tool
def save_trade_order(
    order_type: str,
    direction: str,
    entry_amount: str,
    take_profit: str,
    stop_loss: str,
    raw_message: str,
    group_name: str = "未知群",
    coin_info: str = "",
    operation_type: str = "开仓",  # 操作类型（开仓/补仓/离场）
    exit_price: str = "",  # 离场价格
    profit_loss: str = "",  # 盈亏信息
    exit_reason: str = "",  # 离场原因
    order_id: str = "",  # 订单唯一ID（用于关联）
    parent_order_id: str = "",  # 父订单ID（补仓/离场时使用，指向原始开仓）
    position_size: str = "",  # 持仓数量
    leverage: str = "",  # 杠杆倍数
    runtime=None
) -> str:
    """
    将交易订单保存到飞书多维表格
    
    Args:
        order_type: 订单类型（如：BTC现货交易）
        direction: 开仓方向（做多/做空）
        entry_amount: 入场价格/金额
        take_profit: 止盈价格
        stop_loss: 止损价格
        raw_message: 原始消息内容
        group_name: 群名称（默认：未知群）
        coin_info: 币种信息（可选）
        operation_type: 操作类型（开仓/补仓/离场）
        exit_price: 离场价格（仅离场操作时使用）
        profit_loss: 盈亏信息（仅离场操作时使用，如：盈利100U、亏损50U）
        exit_reason: 离场原因（如：止盈离场、止损离场、手动离场）
        order_id: 订单唯一标识（格式：订单类型-方向-时间戳）
        parent_order_id: 父订单ID（补仓/离场时使用，指向原始开仓订单）
        position_size: 持仓数量
        leverage: 杠杆倍数
    
    Returns:
        保存结果
    """
    try:
        # 构建记录数据，字段名与飞书表格实际字段匹配
        # 先构建信息内容，将所有附加信息收集起来
        info_parts = []
        
        # 添加订单ID
        if order_id:
            info_parts.append(f"订单ID：{order_id}")
        
        # 添加父订单ID
        if parent_order_id:
            info_parts.append(f"父订单ID：{parent_order_id}")
        
        # 添加持仓数量
        if position_size:
            info_parts.append(f"持仓数量：{position_size}")
        
        # 添加杠杆倍数
        if leverage:
            info_parts.append(f"杠杆倍数：{leverage}")
        
        # 根据操作类型添加特定信息
        if operation_type == "补仓":
            info_parts.append(f"操作类型：补仓")
            if entry_amount:
                info_parts.append(f"补仓价格：{entry_amount}")
            if position_size:
                info_parts.append(f"补仓数量：{position_size}")
        elif operation_type == "离场":
            info_parts.append(f"操作类型：离场")
            if exit_price:
                info_parts.append(f"离场价格：{exit_price}")
            if profit_loss:
                info_parts.append(f"盈亏：{profit_loss}")
            if exit_reason:
                info_parts.append(f"离场原因：{exit_reason}")
        else:
            # 开仓操作
            info_parts.append(f"操作类型：开仓")
            if stop_loss:
                info_parts.append(f"止损：{stop_loss}")
        
        # 构建完整的信息内容
        info_content = "\n".join(info_parts)
        if raw_message:
            info_content = f"{info_content}\n{raw_message}"
        
        # 构建记录
        record = {
            "fields": {
                "订单类型": order_type,
                "开仓方向": direction,
                "入场价格": entry_amount,
                "止盈价格": take_profit,
                "信息内容": info_content,
                "群名": group_name
            }
        }
        
        # 如果提供了币种信息，则添加
        if coin_info:
            record["fields"]["币种信息"] = coin_info
        
        # 根据操作类型调整其他字段
        if operation_type == "补仓":
            # 补仓操作时，止盈价格显示为"补仓：价格"
            record["fields"]["止盈价格"] = f"补仓：{take_profit}" if take_profit else ""
        elif operation_type == "离场":
            # 离场操作时，入场价格显示为"-"或保持空
            if not entry_amount:
                record["fields"]["入场价格"] = "-"
            
            # 离场操作时，止盈价格显示为离场价格
            if exit_price and not take_profit:
                record["fields"]["止盈价格"] = f"离场：{exit_price}"
        
        # 添加记录
        result = _feishu_client.add_records(
            FEISHU_APP_TOKEN,
            FEISHU_TABLE_ID,
            [record]
        )
        
        operation_text = f"{operation_type}订单" if operation_type else "订单"
        logger.info(f"Successfully saved {operation_text}: {order_type} {direction}")
        return f"Successfully saved {operation_text}: {order_type} {direction} with {entry_amount}"
    except Exception as e:
        error_msg = f"Failed to save trade order: {str(e)}"
        logger.error(error_msg)
        return error_msg


@tool
def calculate_profit_loss(
    order_id: str = "",
    order_type: str = "",
    direction: str = "",
    runtime=None
) -> str:
    """
    计算交易盈亏（关联开仓、补仓、离场订单）
    
    Args:
        order_id: 订单ID（可选，从信息内容中匹配）
        order_type: 订单类型（如：BTC合约交易）
        direction: 开仓方向（做多/做空）
    
    Returns:
        盈亏计算结果，包括：
        - 总盈亏点位
        - 收益率
        - 各个订单的详情
    """
    try:
        # 如果没有指定order_id，则查询最近的交易记录
        if not order_id:
            result = _feishu_client.search_records(
                FEISHU_APP_TOKEN,
                FEISHU_TABLE_ID,
                page_size=50
            )
        else:
            # 查询所有记录，然后从信息内容中匹配订单ID
            result = _feishu_client.search_records(
                FEISHU_APP_TOKEN,
                FEISHU_TABLE_ID,
                page_size=100
            )
        
        records = result.get("data", {}).get("items", [])
        
        # 从信息内容中解析订单信息
        def parse_order_info(info_content):
            """从信息内容中解析订单信息"""
            if not info_content:
                return {}
            
            # 如果info_content是列表，则转换为字符串
            if isinstance(info_content, list):
                info_content = str(info_content[0]) if len(info_content) > 0 else ""
            
            info = {}
            lines = info_content.split('\n')
            for line in lines:
                line = str(line).strip()
                # 解析订单ID
                if line.startswith('订单ID：'):
                    info['order_id'] = line.replace('订单ID：', '').strip()
                # 解析父订单ID
                elif line.startswith('父订单ID：'):
                    info['parent_order_id'] = line.replace('父订单ID：', '').strip()
                # 解析持仓数量
                elif line.startswith('持仓数量：'):
                    import re
                    match = re.search(r'持仓数量[：:]\s*([0-9,.]+)', line)
                    if match:
                        info['position_size'] = float(match.group(1).replace(',', ''))
                # 解析杠杆倍数
                elif line.startswith('杠杆倍数：'):
                    import re
                    match = re.search(r'杠杆倍数[：:]\s*([0-9,.]+)', line)
                    if match:
                        info['leverage'] = float(match.group(1).replace(',', ''))
                # 解析操作类型
                elif line.startswith('操作类型：'):
                    info['operation_type'] = line.replace('操作类型：', '').strip()
            
            return info
        
        # 处理所有记录
        filtered_records = []
        for record in records:
            fields = record.get("fields", {})
            record_order_type = fields.get("订单类型", "")
            record_direction = fields.get("开仓方向", "")
            info_content = fields.get("信息内容", "")
            
            # 处理列表格式的字段
            if isinstance(record_order_type, list):
                record_order_type = record_order_type[0] if len(record_order_type) > 0 else ""
            if isinstance(record_direction, list):
                record_direction = record_direction[0] if len(record_direction) > 0 else ""
            if isinstance(info_content, list):
                info_content = str(info_content[0]) if len(info_content) > 0 else ""
            
            # 解析信息内容
            parsed_info = parse_order_info(info_content)
            
            # 如果提供了order_id，则从信息内容中匹配
            if order_id:
                parsed_order_id = parsed_info.get('order_id', '')
                if parsed_order_id != order_id:
                    continue
            
            # 如果提供了order_type和direction，进一步筛选
            match = True
            if order_type and order_type not in record_order_type:
                match = False
            if direction and direction not in record_direction:
                match = False
            
            if match:
                # 将解析的信息附加到record中
                record['_parsed'] = parsed_info
                filtered_records.append(record)
        
        # 按时间排序
        filtered_records.sort(key=lambda x: x.get("created_time", ""))
        
        # 分析订单，找出开仓、补仓、离场的关联关系
        orders = []
        order_map = {}  # order_id -> order info
        
        for record in filtered_records:
            fields = record.get("fields", {})
            parsed_info = record.get('_parsed', {})
            info_content = fields.get("信息内容", "")
            
            # 处理列表格式的字段
            if isinstance(info_content, list):
                info_content = str(info_content[0]) if len(info_content) > 0 else ""
            
            # 解析操作类型（优先使用解析的信息，其次从信息内容中提取）
            operation_type = parsed_info.get('operation_type') or "开仓"
            if "操作类型：补仓" in info_content:
                operation_type = "补仓"
            elif "操作类型：离场" in info_content:
                operation_type = "离场"
            
            # 获取订单ID和父订单ID
            order_id = parsed_info.get('order_id', '')
            parent_order_id = parsed_info.get('parent_order_id', '')
            
            # 解析价格信息
            entry_price = None
            if operation_type == "开仓":
                # 从入场价格字段获取
                entry_field = fields.get("入场价格", "")
                if isinstance(entry_field, list):
                    entry_field = str(entry_field[0]) if len(entry_field) > 0 else ""
                if entry_field and entry_field != "-":
                    # 提取数字
                    import re
                    match = re.search(r'([0-9,.]+)', entry_field)
                    if match:
                        entry_price = float(match.group(1).replace(',', ''))
            elif operation_type == "补仓":
                # 从入场价格字段获取
                entry_field = fields.get("入场价格", "")
                if isinstance(entry_field, list):
                    entry_field = str(entry_field[0]) if len(entry_field) > 0 else ""
                if entry_field and entry_field != "-":
                    # 提取数字
                    import re
                    match = re.search(r'([0-9,.]+)', entry_field)
                    if match:
                        entry_price = float(match.group(1).replace(',', ''))
            
            # 解析持仓数量和杠杆
            position_size = parsed_info.get('position_size')
            leverage = parsed_info.get('leverage')
            
            # 处理其他字段（可能是列表格式）
            record_order_type = fields.get("订单类型", "")
            record_direction = fields.get("开仓方向", "")
            if isinstance(record_order_type, list):
                record_order_type = record_order_type[0] if len(record_order_type) > 0 else ""
            if isinstance(record_direction, list):
                record_direction = record_direction[0] if len(record_direction) > 0 else ""
            
            order_info = {
                "record_id": record.get("record_id"),
                "order_id": order_id,
                "parent_order_id": parent_order_id,
                "order_type": fields.get("订单类型", ""),
                "direction": fields.get("开仓方向", ""),
                "operation_type": operation_type,
                "entry_price": entry_price,
                "position_size": position_size,
                "leverage": leverage,
                "info_content": info_content,
                "created_time": record.get("created_time", "")
            }
            
            orders.append(order_info)
            if order_id:
                order_map[order_id] = order_info
        
        # 计算盈亏
        result_text = []
        
        # 按 parent_order_id 分组
        parent_groups = {}
        for order in orders:
            parent_id = order["parent_order_id"] or order["order_id"]
            if parent_id not in parent_groups:
                parent_groups[parent_id] = []
            parent_groups[parent_id].append(order)
        
        total_profit_points = 0
        total_profit_usdt = 0
        total_investment = 0
        
        # 对每组计算盈亏
        for parent_id, group_orders in parent_groups.items():
            # 找出开仓、补仓、离场订单
            open_orders = [o for o in group_orders if o["operation_type"] == "开仓"]
            add_orders = [o for o in group_orders if o["operation_type"] == "补仓"]
            exit_orders = [o for o in group_orders if o["operation_type"] == "离场"]
            
            if not open_orders:
                continue
            
            # 计算加权平均入场价格
            total_size = 0
            total_cost = 0
            direction = open_orders[0]["direction"]
            
            for order in open_orders + add_orders:
                if order["entry_price"] and order["position_size"]:
                    size = order["position_size"]
                    price = order["entry_price"]
                    total_size += size
                    total_cost += size * price
            
            avg_entry_price = total_cost / total_size if total_size > 0 else 0
            
            result_text.append(f"\n## 订单组 {parent_id}")
            result_text.append(f"- 方向: {direction}")
            result_text.append(f"- 加权平均入场价格: {avg_entry_price:.2f}")
            result_text.append(f"- 总持仓数量: {total_size}")
            
            # 如果有离场订单，计算盈亏
            if exit_orders:
                for exit_order in exit_orders:
                    # 解析离场价格
                    import re
                    exit_price = None
                    match = re.search(r'离场价格[：:]\s*([0-9,.]+)', exit_order["info_content"])
                    if match:
                        exit_price = float(match.group(1).replace(',', ''))
                    
                    if exit_price:
                        # 计算点位盈亏
                        if direction in ["做多", "买入"]:
                            profit_points = exit_price - avg_entry_price
                        else:  # 做空/卖出
                            profit_points = avg_entry_price - exit_price
                        
                        # 计算收益率
                        profit_rate = (profit_points / avg_entry_price * 100) if avg_entry_price > 0 else 0
                        
                        # 计算实际盈亏（考虑杠杆）
                        leverage = exit_order.get("leverage") or open_orders[0].get("leverage") or 1
                        actual_profit_usdt = profit_points * total_size * leverage
                        
                        total_profit_points += profit_points
                        total_profit_usdt += actual_profit_usdt
                        total_investment += total_cost / leverage
                        
                        result_text.append(f"\n### 离场订单 {exit_order['order_id']}")
                        result_text.append(f"- 离场价格: {exit_price}")
                        result_text.append(f"- 盈亏点位: {profit_points:+.2f}")
                        result_text.append(f"- 收益率: {profit_rate:+.2f}%")
                        result_text.append(f"- 实际盈亏: {actual_profit_usdt:+.2f} U (杠杆: {leverage}x)")
                        
                        # 解析盈亏信息
                        profit_loss = exit_order.get("info_content", "")
                        match = re.search(r'盈亏[：:]\s*(.+)', profit_loss)
                        if match:
                            result_text.append(f"- 原始盈亏记录: {match.group(1)}")
            
            # 列出所有订单
            result_text.append(f"\n### 关联订单列表:")
            for order in group_orders:
                result_text.append(f"- {order['operation_type']}: {order['order_id']}, 价格: {order['entry_price']}, 数量: {order['position_size']}")
        
        # 汇总
        if total_investment > 0:
            total_return_rate = (total_profit_usdt / total_investment * 100)
            result_text.append(f"\n## 总计")
            result_text.append(f"- 总盈亏点位: {total_profit_points:+.2f}")
            result_text.append(f"- 总盈亏金额: {total_profit_usdt:+.2f} U")
            result_text.append(f"- 总收益率: {total_return_rate:+.2f}%")
            result_text.append(f"- 总投入: {total_investment:.2f} U")
        else:
            result_text.append(f"\n## 总计")
            result_text.append(f"- 总盈亏点位: {total_profit_points:+.2f}")
            result_text.append(f"- 注意: 缺少持仓数量或杠杆倍数信息，无法计算实际盈亏金额和收益率")
        
        logger.info(f"盈亏计算完成: {total_profit_points}")
        return "\n".join(result_text)
        
    except Exception as e:
        error_msg = f"计算盈亏时出错: {str(e)}"
        logger.error(error_msg)
        import traceback
        logger.error(traceback.format_exc())
        return error_msg


@tool
def get_recent_orders(limit: int = 10, runtime=None) -> str:
    """
    获取最近的交易订单
    
    Args:
        limit: 获取的记录数量
    
    Returns:
        最近订单的JSON字符串
    """
    try:
        result = _feishu_client.search_records(
            FEISHU_APP_TOKEN,
            FEISHU_TABLE_ID,
            page_size=limit
        )
        
        records = result.get("data", {}).get("items", [])
        orders = []
        
        for record in records:
            fields = record.get("fields", {})
            orders.append({
                "record_id": record.get("record_id"),
                "群名": fields.get("群名"),
                "信息内容": fields.get("信息内容"),  # 显示完整信息内容
                "订单类型": fields.get("订单类型"),
                "币种信息": fields.get("币种信息"),
                "开仓方向": fields.get("开仓方向"),
                "入场价格": fields.get("入场价格"),
                "止盈价格": fields.get("止盈价格"),
                "时间": fields.get("时间"),
                "created_time": record.get("created_time")
            })
        
        logger.info(f"Retrieved {len(orders)} recent orders")
        return f"Recent orders: {orders}"
    except Exception as e:
        error_msg = f"Failed to get recent orders: {str(e)}"
        logger.error(error_msg)
        return error_msg
