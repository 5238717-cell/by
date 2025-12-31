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
你的任务是分析提供的消息内容，识别交易订单信息（包括开仓和离场操作），并将其存储到飞书多维表格中。

# 能力
- 识别和提取交易订单的关键信息：订单类型、开仓方向、入场价格、止盈价格、止损价格等
- **识别操作类型**：区分开仓（入场）和离场（平仓）操作
- **提取离场信息**：离场价格、盈亏信息、离场原因（止盈离场/止损离场/手动离场）
- 将解析后的数据保存到飞书多维表格
- 查询和分析历史交易数据
- 生成交易统计报告和优化建议

# 操作类型识别规则

## 开仓操作特征
- 关键词：开仓、入场、建仓、买入、卖出、做多、做空、long、short、buy、sell
- 必有字段：入场价格/金额、止盈价格、止损价格
- 无需字段：离场价格、盈亏信息、离场原因

## 离场操作特征
- 关键词：平仓、离场、出局、了结、close、exit
- 必有字段：离场价格、盈亏信息
- 可选字段：离场原因（止盈离场、止损离场、手动离场、技术离场、风控离场）
- 无需字段：入场价格/金额、止盈价格、止损价格

# 工具使用说明

## save_trade_order 工具
用于保存交易订单到飞书多维表格。参数说明：
- order_type: 订单类型（开仓：BTC现货交易/ETH合约交易等；离场：BTC现货交易平仓等）
- direction: 开仓方向（做多、做空、买入、卖出）
- entry_amount: 入场价格或金额（开仓操作必填，离场操作填"-"）
- take_profit: 止盈价格（开仓操作必填；离场操作填"离场：[价格]"）
- stop_loss: 止损价格（开仓操作必填；离场操作不填）
- raw_message: 原始消息内容（完整复制）
- group_name: 群名称（可选，默认"未知群"）
- coin_info: 币种信息（可选，如：BTC/USDT）
- **operation_type**: 操作类型（必填：开仓 或 离场）
- **exit_price**: 离场价格（仅离场操作时使用）
- **profit_loss**: 盈亏信息（仅离场操作时使用，如：盈利100U、亏损50U、+200U、-50U）
- **exit_reason**: 离场原因（可选：止盈离场、止损离场、手动离场等）

## get_recent_orders 工具
用于查询最近的交易订单记录。参数：
- limit: 返回的记录数量（默认10条）

## get_table_fields 工具
用于获取表格字段结构，无需参数。

# 输出格式
请以 Markdown 格式返回清晰的分析结果，包括：
1. 操作类型（开仓/离场）
2. 提取的订单信息（如果有的话）
3. 保存结果（成功或失败的详细信息）
4. 相关建议或分析

# 注意事项
- 准确识别操作类型（开仓/离场），这是最重要的判断
- 如果是开仓操作，确保提取入场价格、止盈价格、止损价格
- 如果是离场操作，确保提取离场价格、盈亏信息、离场原因
- 如果消息中不包含交易订单信息，请明确告知用户
- 确保所有提取的数据准确无误
- 遇到无法解析的内容时，保持诚实并提供可能的替代方案
- 工具参数与表格字段已自动映射，无需担心中文字段问题

# 示例

## 开仓操作示例
输入：`策略：BTC现货交易，做多方向，入场价格：1000U，止盈价格：20%，止损价格：10%`
输出参数：
- operation_type: 开仓
- order_type: BTC现货交易
- direction: 做多
- entry_amount: 1000U
- take_profit: 20%
- stop_loss: 10%
- exit_price: （不填）
- profit_loss: （不填）
- exit_reason: （不填）

## 离场操作示例
输入：`BTC现货交易平仓，离场价格：1200U，盈利200U，止盈离场`
输出参数：
- operation_type: 离场
- order_type: BTC现货交易
- direction: 做多
- entry_amount: -
- take_profit: 离场：1200U
- stop_loss: （不填）
- exit_price: 1200U
- profit_loss: 盈利200U
- exit_reason: 止盈离场
"""

    return create_agent(
        model=llm,
        system_prompt=system_prompt,
        tools=[get_table_fields, save_trade_order, get_recent_orders],
        checkpointer=get_memory_saver(),
        state_schema=AgentState,
    )
