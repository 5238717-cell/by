"""
消息监听 Agent
功能：监听飞书群消息，获取消息内容和元数据，过滤非策略消息
"""
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class MessageListenerAgent:
    """消息监听 Agent"""

    def __init__(self, client):
        """
        初始化消息监听 Agent

        Args:
            client: 飞书客户端
        """
        self.client = client
        self.chat_name_cache: Dict[str, str] = {}

    def get_chat_name(self, chat_id: str) -> str:
        """获取群名称"""
        if chat_id in self.chat_name_cache:
            return self.chat_name_cache[chat_id]

        try:
            from lark_oapi.api.im.v1 import GetChatRequest

            request = GetChatRequest.builder().chat_id(chat_id).build()
            response = self.client.im.v1.chat.get(request)

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
            from lark_oapi.api.im.v1 import GetMessageRequest

            request = GetMessageRequest.builder().message_id(message_id).build()
            response = self.client.im.v1.message.get(request)

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

    def extract_sender_info(self, event_data: Dict[str, Any]) -> tuple:
        """提取发送者信息"""
        try:
            sender = event_data.get("event", {}).get("sender", {})
            sender_id = sender.get("sender_id", {}).get("open_id", "")
            sender_type = sender.get("sender_type", "")
            sender_name = sender.get("sender_name", "") or sender_type

            return sender_id, sender_name
        except Exception as e:
            logger.error(f"Error extracting sender info: {e}")
            return "", ""

    def is_strategy_message(self, content: str) -> bool:
        """判断是否是策略消息"""
        if not content:
            return False

        # 检查是否包含"策略"关键词
        strategy_keywords = ['策略', 'strategy', '交易计划', '开仓', '平仓', '入场', '止盈', '止损', '仓位']
        for keyword in strategy_keywords:
            if keyword.lower() in content.lower():
                return True

        return False

    def process_message(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理消息事件，提取消息数据和元数据

        Args:
            event_data: 飞书事件数据

        Returns:
            处理结果，包含消息数据和过滤标志
        """
        try:
            event = event_data.get("event", {})
            message = event.get("message", {})

            if not message:
                return {
                    "success": False,
                    "error": "No message data"
                }

            chat_id = message.get("chat_id")
            message_id = message.get("message_id")
            message_type = message.get("msg_type", "text")
            create_time = message.get("create_time")

            if not chat_id or not message_id:
                return {
                    "success": False,
                    "error": "Missing chat_id or message_id"
                }

            logger.info(f"收到消息 - 群ID: {chat_id}, 消息ID: {message_id}")

            # 获取群名称
            chat_name = self.get_chat_name(chat_id)

            # 获取消息内容
            message_content = self.get_message_content(message_id)

            if not message_content:
                logger.warning("消息内容为空")
                return {
                    "success": False,
                    "error": "Empty message content",
                    "is_strategy": False
                }

            # 提取发送者信息
            sender_id, sender_name = self.extract_sender_info(event_data)

            # 判断是否是策略消息
            is_strategy = self.is_strategy_message(message_content)

            logger.info(f"消息内容: {message_content[:200]}...")
            logger.info(f"是否策略消息: {is_strategy}")

            # 构建消息数据
            message_data = {
                "chat_id": chat_id,
                "chat_name": chat_name,
                "message_id": message_id,
                "sender_id": sender_id,
                "sender_name": sender_name,
                "message_type": message_type,
                "raw_content": message_content,
                "timestamp": datetime.fromtimestamp(create_time / 1000).isoformat() if create_time else datetime.now().isoformat()
            }

            return {
                "success": True,
                "message_data": message_data,
                "is_strategy": is_strategy
            }

        except Exception as e:
            logger.error(f"处理消息时出错: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "is_strategy": False
            }


def build_message_listener_agent(client):
    """
    构建消息监听 Agent

    Args:
        client: 飞书客户端

    Returns:
        MessageListenerAgent 实例
    """
    return MessageListenerAgent(client)
