"""
数据存储 Agent
功能：将解析后的订单信息写入飞书多维表格
"""
import logging
from typing import Dict, Any

from functools import wraps
from cozeloop.decorator import observe
from coze_workload_identity import Client

logger = logging.getLogger(__name__)


def get_access_token() -> str:
    """获取多维表格访问令牌"""
    client = Client()
    try:
        access_token = client.get_integration_credential("integration-feishu-base")
        if not access_token:
            raise ValueError("Failed to get access token")
        return access_token
    except Exception as e:
        logger.error(f"Error getting access token: {e}")
        raise


class FeishuBitableClient:
    """飞书多维表格客户端"""

    def __init__(self):
        self.base_url = "https://open.larkoffice.com/open-apis"
        self.timeout = 30
        self.access_token = get_access_token()

    def _headers(self) -> Dict[str, str]:
        """构建请求头"""
        return {
            "Authorization": f"Bearer {self.access_token}" if self.access_token else "",
            "Content-Type": "application/json; charset=utf-8",
        }

    @observe
    def _request(self, method: str, path: str, params: Any = None, json: Any = None) -> Dict:
        """发送HTTP请求"""
        import requests

        try:
            url = f"{self.base_url}{path}"
            resp = requests.request(
                method, url,
                headers=self._headers(),
                params=params,
                json=json,
                timeout=self.timeout
            )
            resp_data = resp.json()

            if resp_data.get("code") != 0:
                raise Exception(f"API error: {resp_data}")

            return resp_data

        except Exception as e:
            logger.error(f"Request error: {e}")
            raise


class DataStorageAgent:
    """数据存储 Agent"""

    def __init__(self, app_token: str, table_id: str):
        """
        初始化数据存储 Agent

        Args:
            app_token: 多维表格 app_token
            table_id: 数据表 table_id
        """
        self.app_token = app_token
        self.table_id = table_id
        self.client = FeishuBitableClient()

        # 字段名称映射
        self.field_mapping = {
            'group_name': '群名称',
            'message_content': '消息内容',
            'order_type': '订单类型',
            'direction': '开仓方向',
            'entry_amount': '入场金额',
            'take_profit': '止盈',
            'stop_loss': '止损',
            'strategy_keywords': '策略关键词',
            'parsed_at': '解析时间'
        }

    def build_fields(self, order_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        将订单信息转换为多维表格字段

        Args:
            order_info: 订单信息

        Returns:
            字段字典
        """
        fields = {
            self.field_mapping['group_name']: order_info.get('group_name'),
            self.field_mapping['message_content']: order_info.get('message_content'),
        }

        # 添加可选字段
        if order_info.get('order_type'):
            fields[self.field_mapping['order_type']] = order_info['order_type']

        if order_info.get('direction'):
            fields[self.field_mapping['direction']] = order_info['direction']

        if order_info.get('entry_amount'):
            fields[self.field_mapping['entry_amount']] = order_info['entry_amount']

        if order_info.get('take_profit'):
            fields[self.field_mapping['take_profit']] = order_info['take_profit']

        if order_info.get('stop_loss'):
            fields[self.field_mapping['stop_loss']] = order_info['stop_loss']

        if order_info.get('strategy_keywords'):
            keywords = order_info['strategy_keywords']
            if isinstance(keywords, list):
                fields[self.field_mapping['strategy_keywords']] = ', '.join(keywords)
            else:
                fields[self.field_mapping['strategy_keywords']] = keywords

        if order_info.get('parsed_at'):
            fields[self.field_mapping['parsed_at']] = order_info['parsed_at']

        return fields

    def save(self, order_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        将订单信息保存到多维表格

        Args:
            order_info: 订单信息

        Returns:
            保存结果
        """
        try:
            logger.info(f"开始保存订单信息: {order_info.get('group_name')}")

            # 构建字段数据
            fields = self.build_fields(order_info)

            # 调用 API 添加记录
            body = {
                "records": [{"fields": fields}]
            }

            result = self.client._request(
                "POST",
                f"/bitable/v1/apps/{self.app_token}/tables/{self.table_id}/records/batch_create",
                json=body
            )

            if result.get("code") == 0:
                logger.info("✅ 成功保存订单信息到多维表格")
                return {
                    "success": True,
                    "record_id": result.get("data", {}).get("records", [{}])[0].get("record_id"),
                    "fields": fields
                }
            else:
                logger.error(f"保存失败: {result}")
                return {
                    "success": False,
                    "error": str(result)
                }

        except Exception as e:
            logger.error(f"保存订单信息时出错: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    def get_recent_orders(self, limit: int = 100) -> Dict[str, Any]:
        """
        获取最近的订单记录

        Args:
            limit: 返回记录数量

        Returns:
            记录列表
        """
        try:
            result = self.client._request(
                "POST",
                f"/bitable/v1/apps/{self.app_token}/tables/{self.table_id}/records/search",
                json={"page_size": limit}
            )

            if result.get("code") == 0:
                records = result.get("data", {}).get("items", [])
                return {
                    "success": True,
                    "records": records,
                    "total": len(records)
                }
            else:
                return {
                    "success": False,
                    "error": str(result)
                }

        except Exception as e:
            logger.error(f"获取订单记录时出错: {e}")
            return {
                "success": False,
                "error": str(e)
            }


def build_data_storage_agent(app_token: str, table_id: str):
    """
    构建数据存储 Agent

    Args:
        app_token: 多维表格 app_token
        table_id: 数据表 table_id

    Returns:
        DataStorageAgent 实例
    """
    return DataStorageAgent(app_token, table_id)
