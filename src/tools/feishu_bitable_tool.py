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
    
    Returns:
        保存结果
    """
    try:
        # 构建记录数据，字段名与飞书表格实际字段匹配
        record = {
            "fields": {
                "订单类型": order_type,
                "开仓方向": direction,
                "入场价格": entry_amount,
                "止盈价格": take_profit,
                "信息内容": raw_message,
                "群名": group_name
            }
        }
        
        # 如果提供了币种信息，则添加
        if coin_info:
            record["fields"]["币种信息"] = coin_info
        
        # 将止损信息附加到信息内容中（因为表格中没有止损价格字段）
        if stop_loss:
            record["fields"]["信息内容"] = f"{raw_message}\n止损：{stop_loss}"
        
        # 添加记录
        result = _feishu_client.add_records(
            FEISHU_APP_TOKEN,
            FEISHU_TABLE_ID,
            [record]
        )
        
        logger.info(f"Successfully saved trade order: {order_type} {direction}")
        return f"Successfully saved trade order: {order_type} {direction} with {entry_amount}"
    except Exception as e:
        error_msg = f"Failed to save trade order: {str(e)}"
        logger.error(error_msg)
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
                "信息内容": fields.get("信息内容"),
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
