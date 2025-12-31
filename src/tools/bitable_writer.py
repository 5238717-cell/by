"""
多维表格操作模块
用于将解析后的订单信息写入飞书多维表格
"""
import os
import logging
from typing import Dict, Optional
from functools import wraps
from cozeloop.decorator import observe
from coze_workload_identity import Client

from tools.message_parser import OrderInfo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_access_token() -> str:
    """
    获取飞书多维表格的访问令牌
    """
    client = Client()
    try:
        access_token = client.get_integration_credential("integration-feishu-base")
        if not access_token:
            raise ValueError("Failed to get access token for integration-feishu-base")
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
    def _request(self, method: str, path: str, params: Optional[Dict] = None, json: Optional[Dict] = None) -> Dict:
        """
        发送HTTP请求

        Args:
            method: HTTP方法
            path: 请求路径
            params: 查询参数
            json: 请求体

        Returns:
            响应数据

        Raises:
            Exception: 请求失败时抛出异常
        """
        import requests

        try:
            url = f"{self.base_url}{path}"
            logger.info(f"Request: {method} {url}")
            resp = requests.request(
                method, url,
                headers=self._headers(),
                params=params,
                json=json,
                timeout=self.timeout
            )
            resp_data = resp.json()
            logger.info(f"Response: {resp_data}")

            if resp_data.get("code") != 0:
                raise Exception(f"FeishuBitable API error: {resp_data}")

            return resp_data
        except requests.exceptions.RequestException as e:
            logger.error(f"FeishuBitable API request error: {e}")
            raise Exception(f"FeishuBitable API request error: {e}")

    def add_record(
        self,
        app_token: str,
        table_id: str,
        fields: Dict
    ) -> Dict:
        """
        添加一条记录到多维表格

        Args:
            app_token: 多维表格的app_token
            table_id: 数据表的table_id
            fields: 要插入的字段数据

        Returns:
            响应数据
        """
        try:
            body = {
                "records": [
                    {
                        "fields": fields
                    }
                ]
            }

            result = self._request(
                "POST",
                f"/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_create",
                json=body
            )

            logger.info(f"Record added successfully: {result}")
            return result

        except Exception as e:
            logger.error(f"Error adding record: {e}")
            raise

    def get_table_fields(self, app_token: str, table_id: str) -> list:
        """
        获取数据表的字段列表

        Args:
            app_token: 多维表格的app_token
            table_id: 数据表的table_id

        Returns:
            字段列表
        """
        try:
            result = self._request(
                "GET",
                f"/bitable/v1/apps/{app_token}/tables/{table_id}/fields"
            )
            return result.get("data", {}).get("items", [])
        except Exception as e:
            logger.error(f"Error getting table fields: {e}")
            raise


class BitableWriter:
    """多维表格写入器"""

    def __init__(self, app_token: str, table_id: str):
        """
        初始化多维表格写入器

        Args:
            app_token: 多维表格的app_token
            table_id: 数据表的table_id
        """
        self.app_token = app_token
        self.table_id = table_id
        self.client = FeishuBitableClient()

        # 字段名称映射（根据实际表格字段调整）
        self.field_mapping = {
            'group_name': '群名称',
            'message_content': '消息内容',
            'order_type': '订单类型',
            'direction': '开仓方向',
            'entry_amount': '入场金额',
            'take_profit': '止盈',
            'stop_loss': '止损',
            'strategy_keywords': '策略关键词'
        }

    def write_order_info(self, order_info: OrderInfo) -> bool:
        """
        将订单信息写入多维表格

        Args:
            order_info: 订单信息对象

        Returns:
            是否写入成功
        """
        try:
            # 构建字段数据
            fields = {
                self.field_mapping['group_name']: order_info.group_name,
                self.field_mapping['message_content']: order_info.message_content,
            }

            # 只添加非None的字段
            if order_info.order_type:
                fields[self.field_mapping['order_type']] = order_info.order_type

            if order_info.direction:
                fields[self.field_mapping['direction']] = order_info.direction

            if order_info.entry_amount:
                fields[self.field_mapping['entry_amount']] = order_info.entry_amount

            if order_info.take_profit:
                fields[self.field_mapping['take_profit']] = order_info.take_profit

            if order_info.stop_loss:
                fields[self.field_mapping['stop_loss']] = order_info.stop_loss

            if order_info.strategy_keywords:
                # 如果是列表，转换为字符串
                if isinstance(order_info.strategy_keywords, list):
                    fields[self.field_mapping['strategy_keywords']] = ', '.join(order_info.strategy_keywords)
                else:
                    fields[self.field_mapping['strategy_keywords']] = order_info.strategy_keywords

            # 调用API添加记录
            result = self.client.add_record(self.app_token, self.table_id, fields)

            if result.get("code") == 0:
                logger.info(f"Successfully wrote order info to bitable: {order_info.group_name}")
                return True
            else:
                logger.error(f"Failed to write order info: {result}")
                return False

        except Exception as e:
            logger.error(f"Error writing order info to bitable: {e}")
            return False

    def create_table_if_not_exists(self, table_name: str) -> bool:
        """
        如果表格不存在，则创建表格（可选功能）

        Args:
            table_name: 表格名称

        Returns:
            是否创建成功
        """
        try:
            # 检查表格是否已存在
            tables_result = self.client._request(
                "GET",
                f"/bitable/v1/apps/{self.app_token}/tables"
            )

            existing_tables = tables_result.get("data", {}).get("items", [])
            for table in existing_tables:
                if table.get("name") == table_name:
                    logger.info(f"Table '{table_name}' already exists")
                    self.table_id = table.get("table_id")
                    return True

            # 创建新表格
            fields = [
                {"field_name": "群名称", "type": 1},
                {"field_name": "消息内容", "type": 1},
                {"field_name": "订单类型", "type": 1},
                {"field_name": "开仓方向", "type": 1},
                {"field_name": "入场金额", "type": 1},
                {"field_name": "止盈", "type": 1},
                {"field_name": "止损", "type": 1},
                {"field_name": "策略关键词", "type": 1},
            ]

            result = self.client._request(
                "POST",
                f"/bitable/v1/apps/{self.app_token}/tables",
                json={
                    "table_name": table_name,
                    "fields": fields
                }
            )

            if result.get("code") == 0:
                self.table_id = result.get("data", {}).get("table_id")
                logger.info(f"Successfully created table: {table_name}")
                return True
            else:
                logger.error(f"Failed to create table: {result}")
                return False

        except Exception as e:
            logger.error(f"Error creating table: {e}")
            return False


# 示例使用
if __name__ == "__main__":
    # 需要用户提供实际的 app_token 和 table_id
    APP_TOKEN = "your_app_token"
    TABLE_ID = "your_table_id"

    writer = BitableWriter(APP_TOKEN, TABLE_ID)

    # 创建测试订单信息
    test_order = OrderInfo(
        group_name="交易信号群",
        message_content="策略：BTC现货交易\n做多方向，入场金额：1000U\n止盈：20%\n止损：10%",
        order_type="开仓",
        direction="做多",
        entry_amount="入场金额：1000U",
        take_profit="止盈：20%",
        stop_loss="止损：10%",
        strategy_keywords=["BTC现货交易"]
    )

    # 写入表格
    success = writer.write_order_info(test_order)
    print(f"Write result: {success}")
