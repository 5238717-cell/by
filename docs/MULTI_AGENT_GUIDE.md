# 多 Agent 协作系统指南

## 概述

多 Agent 协作系统是由 4 个专门 Agent 组成的智能系统，每个 Agent 负责特定功能，通过 LangGraph 工作流协调完成飞书群消息监听、解析、存储和分析任务。

---

## 系统架构

### Agent 分工

```
┌─────────────────────────────────────────────────────────────┐
│                    多 Agent 协作系统                            │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ 消息监听 Agent │───→│ 消息解析 Agent │───→│ 数据存储 Agent │
│              │    │              │    │              │
│ - 接收消息    │    │ - 提取订单    │    │ - 写入表格    │
│ - 过滤非策略  │    │ - 解析字段    │    │ - 保存记录    │
└──────────────┘    └──────────────┘    └──────────────┘
                                              │
                                              ▼
                                     ┌──────────────┐
                                     │ 数据分析 Agent │
                                     │              │
                                     │ - 统计分析    │
                                     │ - 生成报告    │
                                     │ - 提供建议    │
                                     └──────────────┘
```

### 工作流

```
飞书消息事件
    ↓
[消息监听 Agent] ───→ 非策略消息 → 结束
    │
    ↓ (策略消息)
[消息解析 Agent] ───→ 解析失败 → 结束
    │
    ↓ (解析成功)
[数据存储 Agent] ───→ 存储失败 → 记录错误
    │
    ↓ (存储成功)
[数据分析 Agent] (可选)
    ↓
结束
```

---

## 各 Agent 详细说明

### 1. 消息监听 Agent (MessageListenerAgent)

**职责：**
- 监听飞书群消息
- 获取消息内容和元数据
- 过滤非策略消息

**处理流程：**
1. 接收飞书事件数据
2. 提取消息 ID 和群 ID
3. 获取群名称
4. 获取消息文本内容
5. 判断是否包含策略关键词
6. 过滤非策略消息

**输出：**
- 消息数据（群名称、消息内容、发送者信息等）
- 是否是策略消息的标志

---

### 2. 消息解析 Agent (MessageParserAgent)

**职责：**
- 从消息内容中提取订单相关信息
- 识别关键词和数值

**提取字段：**
- 订单类型：开仓、平仓、买入、卖出等
- 开仓方向：做多、做空
- 入场金额：金额数值和单位
- 止盈：止盈价格/比例
- 止损：止损价格/比例
- 策略关键词：策略描述

**解析规则：**
- 使用正则表达式匹配关键词
- 支持中英文混合
- 容错处理（部分匹配）

---

### 3. 数据存储 Agent (DataStorageAgent)

**职责：**
- 将解析后的订单信息写入飞书多维表格
- 管理字段映射

**处理流程：**
1. 接收订单信息
2. 映射到多维表格字段
3. 调用飞书 API 写入
4. 返回写入结果

**字段映射：**
| 系统字段 | 表格字段 |
|---------|---------|
| group_name | 群名称 |
| message_content | 消息内容 |
| order_type | 订单类型 |
| direction | 开仓方向 |
| entry_amount | 入场金额 |
| take_profit | 止盈 |
| stop_loss | 止损 |
| strategy_keywords | 策略关键词 |
| parsed_at | 解析时间 |

---

### 4. 数据分析 Agent (DataAnalysisAgent)

**职责：**
- 分析历史交易数据
- 生成统计报告
- 提供交易建议

**分析维度：**

1. **方向分析**
   - 做多/做空比例
   - 最常见的交易方向

2. **策略分析**
   - 热门策略排行
   - 策略使用频率

3. **金额分析**
   - 平均入场金额
   - 金额范围统计
   - 总投入金额

4. **时间分析**
   - 交易时段分布
   - 星期分布
   - 最新/最旧记录

**输出：**
- 结构化的分析数据
- 文本格式报告
- 交易建议

---

## 状态管理

### MultiAgentState

```python
{
    # 消息列表（对话历史）
    "messages": List[BaseMessage],

    # 原始消息数据
    "raw_message": Optional[MessageData],

    # 是否是策略消息
    "is_strategy": bool,

    # 解析后的订单信息
    "order_info": Optional[OrderInfo],

    # 存储结果
    "storage_result": Optional[Dict],
    "storage_success": bool,

    # 分析结果
    "analysis_result": Optional[AnalysisResult],

    # 错误信息
    "error": Optional[str],

    # 当前处理阶段
    "current_stage": str,

    # 控制标志
    "skip_parsing": bool,
    "skip_storing": bool,
    "trigger_analysis": bool
}
```

---

## 安装和配置

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制配置文件：
```bash
cp config/.env.multiagent config/.env
```

编辑 `config/.env`：
```bash
# 飞书应用配置
FEISHU_APP_ID=cli_xxxxxxxxxxxxxxxx
FEISHU_APP_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 多维表格配置
FEISHU_BITABLE_APP_TOKEN=bascnxxxxxxxxxxxxxxx
FEISHU_BITABLE_TABLE_ID=tblxxxxxxxxxxxxxxx

# 系统配置
DEBUG=true
LOG_LEVEL=INFO
AUTO_ANALYZE=false
ANALYSIS_INTERVAL=24
```

### 3. 创建多维表格

创建包含以下字段的表格：

| 字段名称 | 字段类型 | 说明 |
|---------|---------|------|
| 群名称 | 文本 | 消息来源群 |
| 消息内容 | 文本 | 原始消息内容 |
| 订单类型 | 文本 | 开仓/平仓/买入/卖出等 |
| 开仓方向 | 文本 | 做多/做空 |
| 入场金额 | 文本 | 入场金额（含单位） |
| 止盈 | 文本 | 止盈价格/比例 |
| 止损 | 文本 | 止损价格/比例 |
| 策略关键词 | 文本 | 策略相关关键词 |
| 解析时间 | 日期 | 解析时间戳 |

### 4. 运行系统

```bash
python src/main_multiagent.py
```

---

## 使用示例

### 自动处理流程

系统启动后会自动监听飞书群消息：

1. 收到群消息 → 消息监听 Agent 处理
2. 策略消息 → 消息解析 Agent 提取信息
3. 解析成功 → 数据存储 Agent 写入表格
4. （可选）触发数据分析 Agent 生成报告

### 手动触发分析

在程序运行时，可以手动触发数据分析：

```python
from src.main_multiagent import MultiAgentSystem
from src.agents.data_storage_agent import build_data_storage_agent

# 创建存储 Agent
storage_agent = build_data_storage_agent(
    app_token="your_app_token",
    table_id="your_table_id"
)

# 创建分析 Agent
analysis_agent = build_data_analysis_agent(storage_agent)

# 生成日报
report = analysis_agent.generate_report("daily")
print(report)

# 生成周报
report = analysis_agent.generate_report("weekly")
print(report)
```

---

## 日志说明

系统会生成详细的运行日志：

- **日志文件**: `assets/multi_agent_system.log`
- **日志级别**: DEBUG, INFO, WARNING, ERROR

日志内容包括：
- 每个 Agent 的处理过程
- 状态转换
- 错误信息
- 性能指标

---

## 工作流可视化

```
[Start] → [Listener] → (is_strategy?) → [Parser] → [Storage] → (analyze?) → [Analysis] → [End]
                            ↓ No
                          [End]
```

---

## 扩展开发

### 添加新 Agent

1. 在 `src/agents/` 下创建新的 Agent 类
2. 实现 Agent 的处理逻辑
3. 在 `src/graphs/multi_agent_graph.py` 中添加节点
4. 在工作流中连接新节点

### 自定义解析规则

修改 `src/agents/message_parser_agent.py` 中的 `patterns`：

```python
self.patterns = {
    'custom_field': [
        r'自定义模式1',
        r'自定义模式2'
    ],
    # ... 其他字段
}
```

### 自定义分析维度

在 `src/agents/data_analysis_agent.py` 中添加新的分析方法：

```python
def analyze_custom_dimension(self, records: List[Dict]) -> Dict[str, Any]:
    """自定义分析维度"""
    # 实现分析逻辑
    pass
```

---

## 故障排查

### 问题 1: Agent 无法连接到飞书

**症状**: 日志显示连接失败

**解决方案**:
1. 检查 App ID 和 App Secret 是否正确
2. 确认应用已发布版本
3. 检查网络连接

### 问题 2: 消息解析不准确

**症状**: 提取的信息不完整或错误

**解决方案**:
1. 查看日志中的原始消息内容
2. 调整 `message_parser_agent.py` 中的正则表达式
3. 添加更多的模式匹配

### 问题 3: 数据写入失败

**症状**: 存储显示失败

**解决方案**:
1. 检查多维表格的 App Token 和 Table ID
2. 确认表格字段名称与配置匹配
3. 检查权限设置

---

## 性能优化

### 异步处理

系统使用异步处理提高并发能力：

```python
async def handle_event(self, event_data: Dict[str, Any]):
    result = await self.workflow.process_event(event_data)
```

### 缓存机制

群名称等元数据会被缓存：

```python
self.chat_name_cache: Dict[str, str] = {}
```

---

## 安全建议

1. **保护敏感信息**: 不要将 `.env` 文件提交到版本控制
2. **使用环境变量**: 在生产环境中使用环境变量管理配置
3. **权限控制**: 只授予应用必要的最小权限
4. **日志脱敏**: 避免在日志中记录敏感信息

---

## 相关文档

- [飞书开放平台文档](https://open.feishu.cn/document)
- [LangGraph 文档](https://python.langchain.com/docs/langgraph)
- [项目 README](../README.md)

---

## 许可证

MIT
