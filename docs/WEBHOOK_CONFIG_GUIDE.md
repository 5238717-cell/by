# Webhook 配置指南

## 概述

本系统提供交互式配置向导，帮助您快速完成 Webhook 服务器的配置。在首次运行时会自动检测并启动配置向导。

## 配置向导功能

配置向导将引导您完成以下配置：

### 1. Webhook 端点配置
- **Webhook ID**: 唯一标识符（如: webhook_001）
- **Webhook 名称**: 描述性名称（如: 飞书交易信号Webhook）
- **URL 路径**: 接收消息的路径（如: /webhook/trading）
- **是否启用**: 启用或禁用该端点
- **消息来源**: 消息来源类型（如: feishu、telegram）
- **验证令牌**: 可选的安全令牌

### 2. 服务器配置
- **监听地址**: 服务器绑定的地址（默认: 0.0.0.0）
- **监听端口**: 服务器端口号（默认: 8080）
- **工作进程数**: 并发处理的工作进程数量（默认: 1）

### 3. 消息过滤规则
- **排除关键词**: 包含这些关键词的消息将被过滤（营销、广告等）
  - 默认包括: 广告、营销、推广、免费、扫码、加群等
  
- **交易关键词**: 包含至少2个这些关键词的消息将被识别为交易消息
  - 默认包括: 开仓、平仓、做多、做空、买入、卖出、long、short等
  
- **排除模式**: 匹配这些模式的消息将被过滤（分析、免责声明等）
  - 默认包括: 趋势分析、市场分析、投资建议、风险提示等

### 4. 消息处理配置
- **启用消息过滤**: 是否过滤非交易消息（默认: True）
- **启用 Agent 分析**: 是否使用 Agent 分析交易消息（默认: True）
- **自动交易**: 是否自动执行交易（⚠️ 慎用，默认: False）
- **保存到飞书多维表格**: 是否将交易记录保存到表格（默认: True）
- **记录所有消息日志**: 是否记录所有接收到的消息日志（默认: True）

## 使用方法

### 方法 1: 首次运行自动触发

当您第一次启动 Webhook 服务器时，系统会自动检测配置文件并启动配置向导：

```bash
python src/webhook_server.py
```

### 方法 2: 手动运行配置向导

您可以随时手动运行配置向导来重新配置系统：

```bash
# 使用配置初始化脚本（推荐）
python scripts/init_webhook_config.py

# 或者直接运行配置向导模块
python src/utils/config/config_initializer.py
```

### 方法 3: 删除配置后重新配置

如果您想重新配置整个系统，可以删除现有配置文件：

```bash
rm config/webhook_config.json
python src/webhook_server.py
```

## 配置文件位置

配置文件保存在项目的 `config/webhook_config.json` 路径下。

## 配置示例

以下是典型的配置示例：

```json
{
  "webhooks": [
    {
      "id": "webhook_001",
      "name": "飞书交易信号Webhook",
      "url_path": "/webhook/trading-signal-001",
      "enabled": true,
      "description": "接收飞书群交易信号消息",
      "source": "feishu",
      "verification_token": ""
    }
  ],
  "server": {
    "host": "0.0.0.0",
    "port": 8080,
    "workers": 1
  },
  "filter_rules": {
    "exclude_keywords": [
      "广告", "营销", "推广", "免费", "扫码"
    ],
    "trading_keywords": [
      "开仓", "平仓", "做多", "做空", "买入", "卖出"
    ],
    "exclude_patterns": [
      "趋势分析", "市场分析", "投资建议"
    ]
  },
  "message_processing": {
    "enable_filter": true,
    "enable_agent_analysis": true,
    "auto_trade": false,
    "save_to_bitable": true,
    "log_all_messages": true
  }
}
```

## 启动 Webhook 服务器

配置完成后，您可以启动 Webhook 服务器：

```bash
# 前台运行
python src/webhook_server.py

# 后台运行（Linux/Mac）
nohup python src/webhook_server.py > logs/webhook.log 2>&1 &

# 后台运行（Windows）
start /B python src/webhook_server.py
```

## 访问 Webhook 服务

服务器启动后，您可以通过以下端点访问：

- **根路径**: `http://localhost:8080/` - 服务状态
- **Webhook列表**: `http://localhost:8080/webhooks` - 查看所有 Webhook 配置
- **接收消息**: `http://localhost:8080/webhook/{webhook_id}` - 接收交易消息（POST）
- **当前配置**: `http://localhost:8080/config` - 查看当前配置（脱敏）

## 管理端点

系统提供以下管理端点（通过 API 调用）：

- `POST /admin/webhook` - 添加新的 Webhook 配置
- `DELETE /admin/webhook/{webhook_id}` - 删除 Webhook 配置
- `POST /admin/webhook/{webhook_id}/toggle` - 启用/禁用 Webhook

## 测试配置

运行配置初始化工具的测试套件：

```bash
python tests/test_config_initializer.py
```

## 常见问题

### Q: 如何修改已有的配置？
A: 您可以手动编辑 `config/webhook_config.json` 文件，或者删除文件后重新运行配置向导。

### Q: 配置向导支持交互式输入吗？
A: 是的，配置向导完全支持交互式输入，您可以按 Enter 使用默认值。

### Q: 如何添加多个 Webhook 端点？
A: 在配置向导中，配置完一个 Webhook 后，系统会询问是否继续添加新的 Webhook。

### Q: 配置文件的安全性如何？
A: 配置文件包含服务器配置和过滤规则，但不包含敏感的 API 密钥。建议将配置文件纳入版本控制（如果包含敏感信息请加密）。

### Q: 如何验证配置是否正确？
A: 启动 Webhook 服务器后，访问 `http://localhost:8080/config` 端点查看当前配置。

## 技术支持

如有问题，请查看项目文档或联系技术支持团队。
