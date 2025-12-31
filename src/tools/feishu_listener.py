"""
飞书消息监听服务
使用飞书 SDK 的长连接模式监听群消息
"""
import json
import logging
import os
from typing import Optional, Dict, Any
from lark_oapi.api.im.v1 import GetChatRequest, GetMessageRequest
from lark_oapi.api.bitable.v1 import GetAppTableRequest

from tools.message_parser import MessageParser, OrderInfo
from tools.bitable_writer import BitableWriter

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FeishuMessageListener:
    """飞书消息监听器"""

    def __init__(
        self,
        app_id: str,
        app_secret: str,
        bitable_app_token: str,
        bitable_table_id: str
    ):
        """
        初始化消息监听器

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

        # 初始化消息解析器
        self.parser = MessageParser()

        # 初始化多维表格写入器
        self.bitable_writer = BitableWriter(bitable_app_token, bitable_table_id)

        # 缓存群名称
        self.chat_name_cache: Dict[str, str] = {}

        logger.info("FeishuMessageListener initialized")

    def get_chat_name(self, client, chat_id: str) -> str:
        """
        获取群名称

        Args:
            client: 飞书客户端
            chat_id: 群聊ID

        Returns:
            群名称
        """
        # 先从缓存查找
        if chat_id in self.chat_name_cache:
            return self.chat_name_cache[chat_id]

        try:
            request = GetChatRequest.builder().chat_id(chat_id).build()
            response = client.im.v1.chat.get(request)

            if response.code == 0 and response.data:
                chat_name = response.data.name or "未知群"
                self.chat_name_cache[chat_id] = chat_name
                return chat_name
            else:
                logger.error(f"Failed to get chat info: {response.code} - {response.msg}")
                return "未知群"

        except Exception as e:
            logger.error(f"Error getting chat name: {e}")
            return "未知群"

    def get_message_content(self, client, message_id: str) -> Optional[str]:
        """
        获取消息内容

        Args:
            client: 飞书客户端
            message_id: 消息ID

        Returns:
            消息文本内容
        """
        try:
            request = GetMessageRequest.builder().message_id(message_id).build()
            response = client.im.v1.message.get(request)

            if response.code == 0 and response.data:
                content_json = response.data.content
                if not content_json:
                    return None

                # 解析消息内容
                content = json.loads(content_json)

                # 根据消息类型提取文本
                msg_type = response.data.msg_type

                if msg_type == "text":
                    # 文本消息
                    return content.get("text", "")

                elif msg_type == "post":
                    # 富文本消息
                    post_content = content.get("post", {})
                    if post_content:
                        # post 内容可能包含多个段落
                        zh_cn = post_content.get("zh_cn", [])
                        if zh_cn and len(zh_cn) > 0:
                            # 提取所有段落文本
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
                logger.error(f"Failed to get message content: {response.code} - {response.msg}")
                return None

        except Exception as e:
            logger.error(f"Error getting message content: {e}")
            return None

    def handle_message_event(self, client, event_data: Dict[str, Any]) -> None:
        """
        处理消息事件

        Args:
            client: 飞书客户端
            event_data: 事件数据
        """
        try:
            # 解析事件数据
            event = event_data.get("event", {})
            message = event.get("message", {})

            if not message:
                logger.warning("No message data in event")
                return

            chat_id = message.get("chat_id")
            message_id = message.get("message_id")

            if not chat_id or not message_id:
                logger.warning("Missing chat_id or message_id")
                return

            logger.info(f"Received message: chat_id={chat_id}, message_id={message_id}")

            # 获取群名称
            chat_name = self.get_chat_name(client, chat_id)

            # 获取消息内容
            message_content = self.get_message_content(client, message_id)

            if not message_content:
                logger.warning("No message content")
                return

            logger.info(f"Message content: {message_content[:100]}...")

            # 判断是否是策略消息
            if not self.parser.is_strategy_message(message_content):
                logger.info("Not a strategy message, skipping")
                return

            # 解析消息内容
            order_info = self.parser.parse_message(message_content, chat_name)

            logger.info(f"Parsed order info: {order_info}")

            # 写入多维表格
            success = self.bitable_writer.write_order_info(order_info)

            if success:
                logger.info(f"Successfully wrote order info for group: {chat_name}")
            else:
                logger.error(f"Failed to write order info for group: {chat_name}")

        except Exception as e:
            logger.error(f"Error handling message event: {e}", exc_info=True)

    def start_event_listener(self, event_handler_func):
        """
        启动事件监听器（使用长连接模式）

        Args:
            event_handler_func: 事件处理函数
        """
        import asyncio
        from lark_oapi.sdk.auth.access_token.internal import (
            InternalAppAccessTokenManager,
        )
        from lark_oapi.sdk.event.dispatcher.dispatcher import (
            BaseEventDispatcher,
        )
        from lark_oapi.api.im.v1 import (
            P2ImMessageReceiveV1,
        )

        class SimpleEventDispatcher(BaseEventDispatcher):
            """简单的事件分发器"""

            def __init__(self, handler_func):
                self.handler_func = handler_func
                super().__init__()

            def do_dispatch_event(self, ctx, data):
                """分发事件"""
                try:
                    # 调用事件处理函数
                    self.handler_func(ctx, data)
                    logger.info("Event dispatched successfully")
                except Exception as e:
                    logger.error(f"Error dispatching event: {e}", exc_info=True)

        async def listen():
            """启动监听"""
            try:
                # 创建应用访问令牌管理器
                access_token_manager = InternalAppAccessTokenManager(
                    app_id=self.app_id,
                    app_secret=self.app_secret,
                )

                # 创建事件分发器
                dispatcher = SimpleEventDispatcher(event_handler_func)

                # 使用长连接模式接收事件
                logger.info("Starting event listener with long connection mode...")

                # 注册接收消息事件处理器
                dispatcher.register_p2_im_message_receive_v1(
                    P2ImMessageReceiveV1(handler=self.handle_message_event_wrapper)
                )

                # 启动长连接
                from lark_oapi.sdk.event.connection.base import BaseConnection

                # 使用上下文
                context = {
                    "client": None,  # 客户端会在连接时自动设置
                    "listener": self
                }

                # 创建并启动连接
                connection = BaseConnection(
                    app_id=self.app_id,
                    app_secret=self.app_secret,
                    event_handler=dispatcher,
                )

                # 开始监听
                await connection.start()

            except Exception as e:
                logger.error(f"Error starting event listener: {e}", exc_info=True)

        # 运行异步监听
        asyncio.run(listen())

    def handle_message_event_wrapper(self, event):
        """
        消息事件包装器（适配飞书 SDK）

        Args:
            event: 飞书事件对象
        """
        try:
            # 转换事件为字典
            event_dict = event.to_dict() if hasattr(event, 'to_dict') else event

            # 处理消息事件
            self.handle_message_event(None, event_dict)

        except Exception as e:
            logger.error(f"Error in message event wrapper: {e}", exc_info=True)
