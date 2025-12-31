"""
多 Agent 协作工作流
使用 LangGraph 构建多 Agent 协作系统
"""
import logging
from typing import Dict, Any, Literal

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage

from graphs.state import MultiAgentState

logger = logging.getLogger(__name__)


class MultiAgentWorkflow:
    """多 Agent 协作工作流"""

    def __init__(
        self,
        message_listener_agent,
        message_parser_agent,
        data_storage_agent,
        data_analysis_agent
    ):
        """
        初始化多 Agent 工作流

        Args:
            message_listener_agent: 消息监听 Agent
            message_parser_agent: 消息解析 Agent
            data_storage_agent: 数据存储 Agent
            data_analysis_agent: 数据分析 Agent
        """
        self.message_listener_agent = message_listener_agent
        self.message_parser_agent = message_parser_agent
        self.data_storage_agent = data_storage_agent
        self.data_analysis_agent = data_analysis_agent

        self.graph = None
        self._build_graph()

    def node_message_listener(self, state: MultiAgentState) -> MultiAgentState:
        """
        消息监听节点：接收并过滤消息

        Args:
            state: 当前状态

        Returns:
            更新后的状态
        """
        logger.info("=" * 60)
        logger.info("【消息监听 Agent】开始处理")
        logger.info("=" * 60)

        # 从状态中获取事件数据（通过 messages 传递）
        event_data = None
        if state.get("messages"):
            # 从最新的消息中提取事件数据
            latest_msg = state["messages"][-1]
            if isinstance(latest_msg, HumanMessage):
                event_data = latest_msg.content

        if not event_data:
            logger.error("没有事件数据")
            state["error"] = "没有事件数据"
            state["current_stage"] = "completed"
            return state

        # 调用消息监听 Agent
        result = self.message_listener_agent.process_message(event_data)

        if result.get("success"):
            state["raw_message"] = result["message_data"]
            state["is_strategy"] = result["is_strategy"]
            state["skip_parsing"] = not result["is_strategy"]
            state["current_stage"] = "listening"
            logger.info(f"消息监听完成: is_strategy={state['is_strategy']}")
        else:
            state["error"] = result.get("error")
            state["is_strategy"] = False
            state["skip_parsing"] = True
            state["current_stage"] = "completed"
            logger.error(f"消息监听失败: {state['error']}")

        # 添加 AI 消息记录
        state["messages"].append(AIMessage(
            content=f"消息监听: {'成功' if result.get('success') else '失败'} - {result.get('message_data', {}).get('chat_name', '未知群')}"
        ))

        return state

    def node_message_parser(self, state: MultiAgentState) -> MultiAgentState:
        """
        消息解析节点：提取订单信息

        Args:
            state: 当前状态

        Returns:
            更新后的状态
        """
        logger.info("=" * 60)
        logger.info("【消息解析 Agent】开始处理")
        logger.info("=" * 60)

        if state.get("skip_parsing"):
            logger.info("跳过解析（非策略消息）")
            state["skip_storing"] = True
            state["current_stage"] = "completed"
            return state

        raw_message = state.get("raw_message")
        if not raw_message:
            logger.error("没有原始消息数据")
            state["error"] = "没有原始消息数据"
            state["skip_storing"] = True
            state["current_stage"] = "completed"
            return state

        # 调用消息解析 Agent
        result = self.message_parser_agent.parse(
            raw_message["raw_content"],
            raw_message["chat_name"]
        )

        if result.get("success"):
            state["order_info"] = result["order_info"]
            state["current_stage"] = "parsing"
            logger.info("消息解析完成")
        else:
            state["error"] = result.get("error")
            state["skip_storing"] = True
            state["current_stage"] = "completed"
            logger.error(f"消息解析失败: {state['error']}")

        # 添加 AI 消息记录
        state["messages"].append(AIMessage(
            content=f"消息解析: {'成功' if result.get('success') else '失败'}"
        ))

        return state

    def node_data_storage(self, state: MultiAgentState) -> MultiAgentState:
        """
        数据存储节点：写入多维表格

        Args:
            state: 当前状态

        Returns:
            更新后的状态
        """
        logger.info("=" * 60)
        logger.info("【数据存储 Agent】开始处理")
        logger.info("=" * 60)

        if state.get("skip_storing"):
            logger.info("跳过存储")
            state["storage_success"] = False
            state["current_stage"] = "completed"
            return state

        order_info = state.get("order_info")
        if not order_info:
            logger.error("没有订单信息")
            state["error"] = "没有订单信息"
            state["storage_success"] = False
            state["current_stage"] = "completed"
            return state

        # 调用数据存储 Agent
        result = self.data_storage_agent.save(order_info)

        if result.get("success"):
            state["storage_result"] = {
                "record_id": result.get("record_id"),
                "fields": result.get("fields")
            }
            state["storage_success"] = True
            state["current_stage"] = "storing"
            logger.info("数据存储完成")
        else:
            state["error"] = result.get("error")
            state["storage_success"] = False
            state["current_stage"] = "completed"
            logger.error(f"数据存储失败: {state['error']}")

        # 添加 AI 消息记录
        state["messages"].append(AIMessage(
            content=f"数据存储: {'成功' if result.get('success') else '失败'}"
        ))

        return state

    def node_data_analysis(self, state: MultiAgentState) -> MultiAgentState:
        """
        数据分析节点：分析历史数据

        Args:
            state: 当前状态

        Returns:
            更新后的状态
        """
        logger.info("=" * 60)
        logger.info("【数据分析 Agent】开始处理")
        logger.info("=" * 60)

        if not state.get("trigger_analysis"):
            logger.info("不触发数据分析")
            state["current_stage"] = "completed"
            return state

        # 调用数据分析 Agent
        result = self.data_analysis_agent.analyze()

        if result.get("success"):
            state["analysis_result"] = result.get("analysis_result")
            state["current_stage"] = "analyzing"
            logger.info("数据分析完成")
        else:
            state["error"] = result.get("error")
            logger.error(f"数据分析失败: {state['error']}")

        # 添加 AI 消息记录
        state["messages"].append(AIMessage(
            content=f"数据分析: {'成功' if result.get('success') else '失败'}"
        ))

        return state

    def should_parse(self, state: MultiAgentState) -> Literal["parser", "analysis", "end"]:
        """判断是否进入解析节点"""
        if state.get("skip_parsing"):
            return "end"
        return "parser"

    def should_store(self, state: MultiAgentState) -> Literal["storage", "analysis", "end"]:
        """判断是否进入存储节点"""
        if state.get("skip_storing"):
            return "end"
        return "storage"

    def should_analyze(self, state: MultiAgentState) -> Literal["analysis", "end"]:
        """判断是否进入分析节点"""
        if state.get("trigger_analysis"):
            return "analysis"
        return "end"

    def _build_graph(self):
        """构建 LangGraph 工作流"""
        logger.info("构建多 Agent 协作工作流...")

        # 创建状态图
        workflow = StateGraph(MultiAgentState)

        # 添加节点
        workflow.add_node("listener", self.node_message_listener)
        workflow.add_node("parser", self.node_message_parser)
        workflow.add_node("storage", self.node_data_storage)
        workflow.add_node("analysis", self.node_data_analysis)

        # 添加边
        workflow.set_entry_point("listener")

        # 监听 -> 解析 或 结束
        workflow.add_conditional_edges(
            "listener",
            self.should_parse,
            {
                "parser": "parser",
                "end": END
            }
        )

        # 解析 -> 存储
        workflow.add_edge("parser", "storage")

        # 存储 -> 分析 或 结束
        workflow.add_conditional_edges(
            "storage",
            self.should_analyze,
            {
                "analysis": "analysis",
                "end": END
            }
        )

        # 分析 -> 结束
        workflow.add_edge("analysis", END)

        # 编译图
        self.graph = workflow.compile()
        logger.info("✓ 工作流构建完成")

    async def process_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理飞书事件

        Args:
            event_data: 飞书事件数据

        Returns:
            处理结果
        """
        # 初始化状态
        initial_state: MultiAgentState = {
            "messages": [HumanMessage(content=event_data)],
            "raw_message": None,
            "is_strategy": False,
            "order_info": None,
            "storage_result": None,
            "storage_success": False,
            "analysis_result": None,
            "error": None,
            "current_stage": "starting",
            "skip_parsing": False,
            "skip_storing": False,
            "trigger_analysis": False  # 默认不触发分析
        }

        try:
            # 运行工作流
            final_state = self.graph.invoke(initial_state)

            return {
                "success": True,
                "final_state": final_state,
                "storage_success": final_state.get("storage_success", False)
            }

        except Exception as e:
            logger.error(f"处理事件时出错: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    def trigger_analysis(self, analysis_type: str = "daily") -> str:
        """
        手动触发数据分析

        Args:
            analysis_type: 分析类型

        Returns:
            分析报告
        """
        logger.info(f"手动触发数据分析: {analysis_type}")

        report = self.data_analysis_agent.generate_report(analysis_type)

        logger.info("分析报告生成完成")
        return report


def build_multi_agent_workflow(
    message_listener_agent,
    message_parser_agent,
    data_storage_agent,
    data_analysis_agent
):
    """
    构建多 Agent 工作流

    Args:
        message_listener_agent: 消息监听 Agent
        message_parser_agent: 消息解析 Agent
        data_storage_agent: 数据存储 Agent
        data_analysis_agent: 数据分析 Agent

    Returns:
        MultiAgentWorkflow 实例
    """
    return MultiAgentWorkflow(
        message_listener_agent,
        message_parser_agent,
        data_storage_agent,
        data_analysis_agent
    )
