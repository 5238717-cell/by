"""
飞书交易订单分析 Agent
基于 LangChain 和 LangGraph 构建的多 Agent 协作系统
"""
import os
import json
from typing import Annotated
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage
from coze_coding_utils.runtime_ctx.context import default_headers
from storage.memory.memory_saver import get_memory_saver

# 导入工具
from tools.feishu_bitable_tool import (
    get_table_fields,
    save_trade_order,
    get_recent_orders
)

LLM_CONFIG = "config/agent_llm_config.json"

# 默认保留最近 20 轮对话 (40 条消息)
MAX_MESSAGES = 40


def _windowed_messages(old, new):
    """滑动窗口: 只保留最近 MAX_MESSAGES 条消息"""
    return add_messages(old, new)[-MAX_MESSAGES:]  # type: ignore


class AgentState(MessagesState):
    messages: Annotated[list[AnyMessage], _windowed_messages]


def build_agent(ctx=None):
    """
    构建交易订单分析 Agent

    Returns:
        Agent 实例
    """
    workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
    config_path = os.path.join(workspace_path, LLM_CONFIG)

    with open(config_path, 'r', encoding='utf-8') as f:
        cfg = json.load(f)

    api_key = os.getenv("COZE_WORKLOAD_IDENTITY_API_KEY")
    base_url = os.getenv("COZE_INTEGRATION_MODEL_BASE_URL")

    llm = ChatOpenAI(
        model=cfg['config'].get("model"),
        api_key=api_key,
        base_url=base_url,
        temperature=cfg['config'].get('temperature', 0.7),
        streaming=True,
        timeout=cfg['config'].get('timeout', 600),
        extra_body={
            "thinking": {
                "type": cfg['config'].get('thinking', 'disabled')
            }
        },
        default_headers=default_headers(ctx) if ctx else {}
    )

    # 系统提示词
    system_prompt = """# 角色定义
你是交易订单分析专家，专注于飞书群消息中的交易订单提取与分析。

# 任务目标
你的任务是分析提供的消息内容，识别交易订单信息，并将其存储到飞书多维表格中。

# 能力
- 识别和提取交易订单的关键信息：订单类型、开仓方向、入场价格、止盈价格、止损价格等
- 将解析后的数据保存到飞书多维表格
- 查询和分析历史交易数据
- 生成交易统计报告和优化建议

# 工具使用说明

## save_trade_order 工具
用于保存交易订单到飞书多维表格。参数说明：
- order_type: 订单类型（如：BTC现货交易、BTC合约交易等）
- direction: 开仓方向（做多、做空、买入、卖出）
- entry_amount: 入场价格或金额（如：1000U、50000）
- take_profit: 止盈价格或比例（如：20%、105000）
- stop_loss: 止损价格或比例（如：10%、95000）
- raw_message: 原始消息内容（完整复制）
- group_name: 群名称（可选，默认"未知群"）
- coin_info: 币种信息（可选，如：BTC/USDT）

## get_recent_orders 工具
用于查询最近的交易订单记录。参数：
- limit: 返回的记录数量（默认10条）

## get_table_fields 工具
用于获取表格字段结构，无需参数。

# 输出格式
请以 Markdown 格式返回清晰的分析结果，包括：
1. 提取的订单信息（如果有的话）
2. 保存结果（成功或失败的详细信息）
3. 相关建议或分析

# 注意事项
- 如果消息中不包含交易订单信息，请明确告知用户
- 确保所有提取的数据准确无误
- 遇到无法解析的内容时，保持诚实并提供可能的替代方案
- 工具参数与表格字段已自动映射，无需担心中文字段问题
- 止损价格会自动附加到信息内容中保存
"""

    return create_agent(
        model=llm,
        system_prompt=system_prompt,
        tools=[get_table_fields, save_trade_order, get_recent_orders],
        checkpointer=get_memory_saver(),
        state_schema=AgentState,
    )
