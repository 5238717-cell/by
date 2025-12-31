"""
多 Agent 协作系统的状态定义
定义在各个 Agent 之间传递的数据结构
"""
from typing import Annotated, Optional, List, Dict, Any
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage


class MessageData(TypedDict):
    """消息数据结构"""
    chat_id: str
    chat_name: str
    message_id: str
    sender_id: Optional[str]
    sender_name: Optional[str]
    message_type: str  # text, post, etc.
    raw_content: str
    timestamp: str


class OrderInfo(TypedDict):
    """订单信息数据结构"""
    group_name: str
    message_content: str
    order_type: Optional[str]
    direction: Optional[str]
    entry_amount: Optional[str]
    take_profit: Optional[str]
    stop_loss: Optional[str]
    strategy_keywords: Optional[List[str]]
    parsed_at: str


class AnalysisResult(TypedDict):
    """分析结果数据结构"""
    analysis_type: str  # daily, weekly, monthly
    total_orders: int
    success_rate: Optional[float]
    average_profit: Optional[float]
    top_strategy: Optional[str]
    recommendations: List[str]
    generated_at: str


class MultiAgentState(TypedDict):
    """多 Agent 协作系统的状态"""
    # 消息列表（用于对话历史）
    messages: Annotated[List[BaseMessage], add_messages]

    # 原始消息数据（监听 Agent 填充）
    raw_message: Optional[MessageData]

    # 是否是策略消息（监听 Agent 过滤后标记）
    is_strategy: bool

    # 解析后的订单信息（解析 Agent 填充）
    order_info: Optional[OrderInfo]

    # 存储结果（存储 Agent 填充）
    storage_result: Optional[Dict[str, Any]]
    storage_success: bool

    # 分析结果（分析 Agent 填充）
    analysis_result: Optional[AnalysisResult]

    # 错误信息
    error: Optional[str]

    # 当前处理阶段
    current_stage: str  # listening, parsing, storing, analyzing, completed

    # 控制标志
    skip_parsing: bool  # 如果不是策略消息，跳过解析
    skip_storing: bool  # 如果解析失败，跳过存储
    trigger_analysis: bool  # 是否触发数据分析
