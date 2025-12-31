"""
多 Agent 协作系统主程序
协调 4 个专门 Agent 的工作流
"""
import os
import sys
import logging
import asyncio
from typing import Dict, Any

from lark_oapi.api.lark_oapi import LarkClient
from lark_oapi.sdk.event.connection.base import BaseConnection
from lark_oapi.sdk.event.dispatcher.dispatcher import BaseEventDispatcher

# 导入 Agent
from agents.message_listener_agent import build_message_listener_agent
from agents.message_parser_agent import build_message_parser_agent
from agents.data_storage_agent import build_data_storage_agent
from agents.data_analysis_agent import build_data_analysis_agent

# 导入工作流
from graphs.multi_agent_graph import build_multi_agent_workflow

# 配置日志
def setup_logging(log_level: str = "INFO"):
    """配置日志系统"""
    log_dir = "assets"
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, "multi_agent_system.log")

    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file)
        ]
    )

    return logging.getLogger(__name__)


logger = setup_logging(os.getenv("LOG_LEVEL", "INFO"))


class MultiAgentSystem:
    """多 Agent 协作系统"""

    def __init__(
        self,
        app_id: str,
        app_secret: str,
        bitable_app_token: str,
        bitable_table_id: str
    ):
        """
        初始化多 Agent 系统

        Args:
            app_id: 飞书应用 ID
            app_secret: 飞书应用 Secret
            bitable_app_token: 多维表格 App Token
            bitable_table_id: 数据表 Table ID
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.bitable_app_token = bitable_app_token
        self.bitable_table_id = bitable_table_id

        # 初始化飞书客户端
        self.client = LarkClient.builder().app_id(
            app_id
        ).app_secret(app_secret).build()

        # 初始化各个 Agent
        logger.info("=" * 60)
        logger.info("初始化多 Agent 协作系统")
        logger.info("=" * 60)

        self.message_listener_agent = build_message_listener_agent(self.client)
        logger.info("✓ 消息监听 Agent 已初始化")

        self.message_parser_agent = build_message_parser_agent()
        logger.info("✓ 消息解析 Agent 已初始化")

        self.data_storage_agent = build_data_storage_agent(bitable_app_token, bitable_table_id)
        logger.info("✓ 数据存储 Agent 已初始化")

        self.data_analysis_agent = build_data_analysis_agent(self.data_storage_agent)
        logger.info("✓ 数据分析 Agent 已初始化")

        # 构建工作流
        self.workflow = build_multi_agent_workflow(
            self.message_listener_agent,
            self.message_parser_agent,
            self.data_storage_agent,
            self.data_analysis_agent
        )
        logger.info("✓ 多 Agent 工作流已构建")

        logger.info("=" * 60)
        logger.info("多 Agent 系统初始化完成")
        logger.info("=" * 60)

    async def handle_event(self, event_data: Dict[str, Any]):
        """
        处理飞书事件

        Args:
            event_data: 飞书事件数据
        """
        try:
            logger.info("\n" + "=" * 60)
            logger.info("【系统】收到新事件")
            logger.info("=" * 60)

            # 运行工作流处理事件
            result = await self.workflow.process_event(event_data)

            if result.get("success"):
                logger.info("✓ 事件处理完成")
                if result.get("storage_success"):
                    logger.info("✓ 数据已保存到多维表格")
            else:
                logger.error(f"✗ 事件处理失败: {result.get('error')}")

            logger.info("=" * 60)

        except Exception as e:
            logger.error(f"处理事件时出错: {e}", exc_info=True)

    def generate_analysis_report(self, analysis_type: str = "daily") -> str:
        """
        生成数据分析报告

        Args:
            analysis_type: 分析类型

        Returns:
            分析报告文本
        """
        logger.info(f"生成 {analysis_type} 数据分析报告...")

        report = self.workflow.trigger_analysis(analysis_type)

        logger.info("报告生成完成")
        return report

    def start_event_listener(self):
        """
        启动事件监听服务
        """
        logger.info("=" * 60)
        logger.info("启动飞书事件监听服务...")
        logger.info("=" * 60)

        try:
            # 创建事件分发器
            class EventDispatcher(BaseEventDispatcher):
                def __init__(self, system):
                    self.system = system
                    super().__init__()

                def do_dispatch_event(self, ctx, data):
                    try:
                        # 异步处理事件
                        asyncio.create_task(self.system.handle_event(data))
                    except Exception as e:
                        logger.error(f"事件分发错误: {e}", exc_info=True)

            dispatcher = EventDispatcher(self)

            # 注册接收消息事件
            from lark_oapi.api.im.v1 import P2ImMessageReceiveV1
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
            logger.info("=" * 60)
            logger.info("【多 Agent 协作系统】")
            logger.info("  消息监听 Agent ✓")
            logger.info("  消息解析 Agent ✓")
            logger.info("  数据存储 Agent ✓")
            logger.info("  数据分析 Agent ✓")
            logger.info("=" * 60)
            logger.info("提示: 按 Ctrl+C 停止服务")
            logger.info("")

            # 启动监听
            asyncio.run(connection.start())

        except KeyboardInterrupt:
            logger.info("\n收到停止信号，正在关闭服务...")
        except Exception as e:
            logger.error(f"启动监听服务失败: {e}", exc_info=True)
            raise


def load_config():
    """加载配置"""
    app_id = os.getenv("FEISHU_APP_ID")
    app_secret = os.getenv("FEISHU_APP_SECRET")
    bitable_app_token = os.getenv("FEISHU_BITABLE_APP_TOKEN")
    bitable_table_id = os.getenv("FEISHU_BITABLE_TABLE_ID")

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
        logger.error("配置文件: config/.env.multiagent")
        logger.error("详细配置说明: docs/MULTI_AGENT_GUIDE.md")
        sys.exit(1)

    return {
        "app_id": app_id,
        "app_secret": app_secret,
        "bitable_app_token": bitable_app_token,
        "bitable_table_id": bitable_table_id
    }


def main():
    """主函数"""
    # 加载配置
    config = load_config()

    # 创建多 Agent 系统
    system = MultiAgentSystem(
        app_id=config["app_id"],
        app_secret=config["app_secret"],
        bitable_app_token=config["bitable_app_token"],
        bitable_table_id=config["bitable_table_id"]
    )

    # 启动监听服务
    system.start_event_listener()


if __name__ == "__main__":
    main()
