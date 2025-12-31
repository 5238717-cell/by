# 飞书多 Agent 协作系统

一个基于 LangGraph 的多 Agent 协作系统，自动监听飞书群消息、解析交易订单、存储数据并生成分析报告。

## ✨ 特性

- 🤖 **多 Agent 协作**: 4 个专门 Agent 各司其职，通过 LangGraph 工作流协调
- 📊 **智能解析**: 自动提取订单类型、开仓方向、入场金额、止盈、止损等信息
- 💾 **自动存储**: 将解析后的数据自动写入飞书多维表格
- 📈 **数据分析**: 分析历史交易数据，生成统计报告和交易建议
- 🔗 **长连接监听**: 无需公网 IP，使用飞书 SDK 长连接模式接收消息
- 📝 **完整日志**: 详细的运行日志，便于调试和监控

---

## 🏗️ 系统架构

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

---

## 📦 项目结构

```
.
├── src/
│   ├── agents/                          # Agent 实现
│   │   ├── message_listener_agent.py    # 消息监听 Agent
│   │   ├── message_parser_agent.py     # 消息解析 Agent
│   │   ├── data_storage_agent.py       # 数据存储 Agent
│   │   └── data_analysis_agent.py      # 数据分析 Agent
│   ├── graphs/                          # 工作流定义
│   │   ├── state.py                     # 状态定义
│   │   └── multi_agent_graph.py         # 多 Agent 工作流
│   ├── tools/                           # 工具模块
│   │   ├── message_parser.py            # 消息解析工具
│   │   └── bitable_writer.py            # 多维表格写入工具
│   ├── main_multiagent.py               # 多 Agent 系统主程序
│   └── main.py                          # 单 Agent 系统主程序
├── tests/
│   └── test_message_parser.py           # 消息解析测试
├── assets/
│   ├── multi_agent_system.log           # 系统日志
│   └── feishu_listener.log              # 单 Agent 日志
├── config/
│   ├── .env.multiagent                  # 多 Agent 配置模板
│   └── .env.example                     # 单 Agent 配置模板
├── docs/
│   ├── README.md                        # 本文件
│   ├── MULTI_AGENT_GUIDE.md             # 多 Agent 系统指南
│   └── SETUP_GUIDE.md                   # 配置指南
└── requirements.txt                     # 依赖列表
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制配置文件模板
cp config/.env.multiagent config/.env

# 编辑配置文件，填入您的凭证
vim config/.env
```

配置内容：
```bash
# 飞书应用配置
FEISHU_APP_ID=cli_xxxxxxxxxxxxxxxx
FEISHU_APP_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 多维表格配置
FEISHU_BITABLE_APP_TOKEN=bascnxxxxxxxxxxxxxxx
FEISHU_BITABLE_TABLE_ID=tblxxxxxxxxxxxxxxx
```

### 3. 配置 Webhook 服务器（首次运行自动触发）

```bash
# 首次运行 Webhook 服务器时，系统会自动启动配置向导
python src/webhook_server.py

# 或者手动运行配置向导
python scripts/init_webhook_config.py
```

配置向导将引导您完成：
- Webhook 端点配置
- 服务器配置
- 消息过滤规则
- 消息处理配置

详细配置说明请参考：[Webhook 配置指南](docs/WEBHOOK_CONFIG_GUIDE.md)

### 4. 运行系统

```bash
# 运行多 Agent 协作系统
python src/main_multiagent.py

# 或者运行 Webhook 服务器
python src/webhook_server.py
```

---

## 📖 详细文档

- **[多 Agent 系统指南](docs/MULTI_AGENT_GUIDE.md)**: 详细介绍多 Agent 架构、各 Agent 功能和使用方法
- **[配置指南](docs/SETUP_GUIDE.md)**: 完整的飞书应用和多维表格配置说明
- **[Webhook 配置指南](docs/WEBHOOK_CONFIG_GUIDE.md)**: Webhook 服务器的交互式配置向导使用说明

---

## 🤖 各 Agent 功能

### 1. 消息监听 Agent
- 监听飞书群消息
- 获取消息内容和元数据
- 过滤非策略消息

### 2. 消息解析 Agent
- 提取订单类型（开仓、平仓、买入、卖出）
- 识别开仓方向（做多、做空）
- 提取入场金额、止盈、止损
- 解析策略关键词

### 3. 数据存储 Agent
- 将解析后的数据写入飞书多维表格
- 管理字段映射
- 处理写入错误

### 4. 数据分析 Agent
- 统计交易方向分布
- 分析热门策略
- 计算平均入场金额
- 生成分析报告和交易建议

---

## 📝 消息格式示例

系统支持多种消息格式：

### 标准格式
```
策略：BTC现货交易
做多方向，入场金额：1000U
止盈：20%
止损：10%
```

### 详细格式
```
【开仓信号】
品种：BTC/USDT
方向：做空
入场金额：2000U
入场位置：97000
目标位：95000
止损位：98500
```

### 简洁格式
```
买入BTC，入场金额500U，止盈10%，止损5%
```

---

## 📊 数据分析报告

系统可以生成多种类型的分析报告：

### 日报报告示例
```
============================================================
交易数据分析报告 (DAILY)
============================================================

生成时间: 2025-01-01T12:00:00
总订单数: 25

--- 方向分析 ---
总交易数: 25
最常见的方向: 做多 (18 次)

--- 策略分析 ---
热门策略:
  1. BTC 4小时突破 (12 次)
  2. ETH 支撑位反弹 (8 次)
  3. BTC 现货交易 (5 次)

--- 金额分析 ---
平均入场金额: 1250.00 U
金额范围: 500.00 - 3000.00 U
总投入金额: 31250.00 U

--- 建议 ---
• 最常见的交易方向是: 做多
• 平均入场金额: 1250.00 U
• 入场金额范围: 500.00 - 3000.00 U
• 最热门的策略: BTC 4小时突破 (出现 12 次)

============================================================
```

---

## 🔧 自定义配置

### 自定义解析规则

编辑 `src/agents/message_parser_agent.py` 中的 `patterns`：

```python
self.patterns = {
    'order_type': [
        r'开仓', r'平仓', r'买入', r'卖出',
        r'自定义关键词',  # 添加你的关键词
    ],
    # ... 更多字段
}
```

### 自定义分析维度

在 `src/agents/data_analysis_agent.py` 中添加新的分析方法：

```python
def analyze_custom(self, records: List[Dict]) -> Dict[str, Any]:
    """自定义分析维度"""
    # 实现你的分析逻辑
    pass
```

---

## 🧪 测试

运行消息解析测试：

```bash
python tests/test_message_parser.py
```

---

## 📋 要求

- Python 3.8+
- 飞书企业自建应用
- 飞书多维表格

---

## 🔒 安全

- 不要将 `.env` 文件提交到版本控制
- 使用环境变量管理敏感配置
- 只授予应用必要的最小权限

---

## 📄 许可证

MIT

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📞 支持

如有问题，请查看：
1. 日志文件：`assets/multi_agent_system.log`
2. 飞书开放平台日志检索
3. [详细指南](docs/MULTI_AGENT_GUIDE.md)
