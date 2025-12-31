"""
飞书群消息监听与多维表格写入主程序
功能：监听飞书群消息，解析订单信息，写入多维表格
"""
import os
import sys
import logging
import json
import asyncio
from typing import Dict, Optional

from lark_oapi.api.im.v1 import GetMessageRequest
from lark_oapi.sdk.event.connection.base import BaseConnection
from lark_oapi.sdk.auth.access_token.internal import InternalAppAccessTokenManager

from tools.message_parser import MessageParser, OrderInfo
from tools.bitable_writer import BitableWriter

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('assets/feishu_listener.log')
    ]
)
logger = logging.getLogger(__name__)


class FeishuOrderAgent:
    """飞书订单监听与处理Agent"""

    def __init__(
        self,
        app_id: str,
        app_secret: str,
        bitable_app_token: str,
        bitable_table_id: str
    ):
        """
        初始化 Agent

        Args:
            app_id: 飞书应用的 App ID
            app_secret: 飞书应用的 App Secret
            bitable_app_token: 多维表格的 app_token
            bitable_table_id: 多维表格的 table_id
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.bitable_app_token = bitable_app_token
        self.bitable_table_id = bitable_table_id

        # 初始化组件
        self.parser = MessageParser()
        self.bitable_writer = BitableWriter(bitable_app_token, bitable_table_id)

        # 缓存
        self.chat_name_cache: Dict[str, str] = {}
        self.client_cache: Optional[Dict] = None

        logger.info("FeishuOrderAgent initialized")
        logger.info(f"App ID: {app_id}")
        logger.info(f"Bitable App Token: {bitable_app_token}")
        logger.info(f"Bitable Table ID: {bitable_table_id}")

    def get_client(self):
        """获取飞书客户端"""
        from lark_oapi.api import lark_oapi as LarkClient

        if self.client_cache is None:
            self.client_cache = LarkClient.builder().app_id(
                self.app_id
            ).app_secret(self.app_secret).build()

        return self.client_cache

    def get_chat_name(self, chat_id: str) -> str:
        """获取群名称"""
        if chat_id in self.chat_name_cache:
            return self.chat_name_cache[chat_id]

        try:
            from lark_oapi.api.im.v1 import GetChatRequest

            client = self.get_client()
            request = GetChatRequest.builder().chat_id(chat_id).build()
            response = client.im.v1.chat.get(request)

            if response.code == 0 and response.data:
                chat_name = response.data.name or "未知群"
                self.chat_name_cache[chat_id] = chat_name
                return chat_name
            else:
                logger.error(f"Failed to get chat info: {response.code}")
                return "未知群"

        except Exception as e:
            logger.error(f"Error getting chat name: {e}")
            return "未知群"

    def get_message_content(self, message_id: str) -> Optional[str]:
        """获取消息文本内容"""
        try:
            client = self.get_client()
            request = GetMessageRequest.builder().message_id(message_id).build()
            response = client.im.v1.message.get(request)

            if response.code == 0 and response.data:
                content_json = response.data.content
                if not content_json:
                    return None

                content = json.loads(content_json)
                msg_type = response.data.msg_type

                if msg_type == "text":
                    return content.get("text", "")
                elif msg_type == "post":
                    post_content = content.get("post", {})
                    if post_content:
                        zh_cn = post_content.get("zh_cn", [])
                        if zh_cn and len(zh_cn) > 0:
                            paragraphs = []
                            for item in zh_cn:
                                if isinstance(item, list):
                                    text_list = [
                                        elem.get("text", "")
                                        for elem in item
                                        if isinstance(elem, dict) and "text" in elem
                                    ]
                                    paragraphs.extend(text_list)
                            return "\n".join(paragraphs)
                return None

            else:
                logger.error(f"Failed to get message content: {response.code}")
                return None

        except Exception as e:
            logger.error(f"Error getting message content: {e}")
            return None

    def handle_message_event(self, ctx, event_data: Dict):
        """处理消息事件"""
        try:
            event = event_data.get("event", {})
            message = event.get("message", {})

            if not message:
                return

            chat_id = message.get("chat_id")
            message_id = message.get("message_id")

            if not chat_id or not message_id:
                return

            logger.info(f"收到消息 - 群ID: {chat_id}, 消息ID: {message_id}")

            # 获取群名称
            chat_name = self.get_chat_name(chat_id)

            # 获取消息内容
            message_content = self.get_message_content(message_id)

            if not message_content:
                logger.warning("消息内容为空，跳过")
                return

            logger.info(f"消息内容: {message_content[:200]}...")

            # 判断是否是策略消息
            if not self.parser.is_strategy_message(message_content):
                logger.info("非策略消息，跳过处理")
                return

            # 解析消息
            order_info = self.parser.parse_message(message_content, chat_name)

            logger.info(f"解析结果:")
            logger.info(f"  群名称: {order_info.group_name}")
            logger.info(f"  订单类型: {order_info.order_type}")
            logger.info(f"  开仓方向: {order_info.direction}")
            logger.info(f"  入场金额: {order_info.entry_amount}")
            logger.info(f"  止盈: {order_info.take_profit}")
            logger.info(f"  止损: {order_info.stop_loss}")
            logger.info(f"  策略关键词: {order_info.strategy_keywords}")

            # 写入多维表格
            success = self.bitable_writer.write_order_info(order_info)

            if success:
                logger.info(f"✅ 成功写入多维表格 - 群: {chat_name}")
            else:
                logger.error(f"❌ 写入多维表格失败 - 群: {chat_name}")

        except Exception as e:
            logger.error(f"处理消息事件时出错: {e}", exc_info=True)

    def start(self):
        """启动监听服务"""
        logger.info("=" * 60)
        logger.info("启动飞书群消息监听服务...")
        logger.info("=" * 60)

        try:
            from lark_oapi.sdk.event.dispatcher.dispatcher import (
                BaseEventDispatcher,
            )
            from lark_oapi.api.im.v1 import P2ImMessageReceiveV1

            # 创建自定义事件分发器
            class EventDispatcher(BaseEventDispatcher):
                def __init__(self, agent):
                    self.agent = agent
                    super().__init__()

                def do_dispatch_event(self, ctx, data):
                    try:
                        # 调用 Agent 的消息处理方法
                        self.agent.handle_message_event(ctx, data)
                    except Exception as e:
                        logger.error(f"事件分发错误: {e}", exc_info=True)

            # 创建事件分发器实例
            dispatcher = EventDispatcher(self)

            # 注册接收消息事件
            dispatcher.register_p2_im_message_receive_v1(
                P2ImMessageReceiveV1(handler=lambda event: dispatcher.do_dispatch_event(
                    None,
                    event.to_dict() if hasattr(event, 'to_dict') else event
                ))
            )

            # 创建长连接
            connection = BaseConnection(
                app_id=self.app_id,
                app_secret=self.app_secret,
                event_handler=dispatcher,
            )

            logger.info("✓ 长连接已建立，开始监听群消息...")
            logger.info("提示: 按 Ctrl+C 停止服务")
            logger.info("=" * 60)

            # 启动监听
            asyncio.run(connection.start())

        except KeyboardInterrupt:
            logger.info("\n收到停止信号，正在关闭服务...")
        except Exception as e:
            logger.error(f"启动监听服务失败: {e}", exc_info=True)
            raise


def main():
    """主函数"""
    # 从环境变量读取配置
    app_id = os.getenv("FEISHU_APP_ID")
    app_secret = os.getenv("FEISHU_APP_SECRET")
    bitable_app_token = os.getenv("FEISHU_BITABLE_APP_TOKEN")
    bitable_table_id = os.getenv("FEISHU_BITABLE_TABLE_ID")

    # 检查必需的配置
    if not all([app_id, app_secret, bitable_app_token, bitable_table_id]):
        logger.error("=" * 60)
        logger.error("缺少必需的环境变量配置！")
        logger.error("=" * 60)
        logger.error("请设置以下环境变量:")
        logger.error("  - FEISHU_APP_ID: 飞书应用的 App ID")
        logger.error("  - FEISHU_APP_SECRET: 飞书应用的 App Secret")
        logger.error("  - FEISHU_BITABLE_APP_TOKEN: 多维表格的 App Token")
        logger.error("  - FEISHU_BITABLE_TABLE_ID: 多维表格的 Table ID")
        logger.error("=" * 60)
        logger.error("详细配置说明请查看 docs/SETUP_GUIDE.md")
        sys.exit(1)

    # 创建并启动 Agent
    agent = FeishuOrderAgent(
        app_id=app_id,
        app_secret=app_secret,
        bitable_app_token=bitable_app_token,
        bitable_table_id=bitable_table_id
    )

    # 启动监听服务
    agent.start()


if __name__ == "__main__":
    main()
