# 飞书群消息监听与多维表格写入

一个自动监听飞书群消息、解析交易订单信息并写入多维表格的程序。

## 功能特性

- ✅ **自动监听群消息**：使用飞书 SDK 长连接模式，无需配置 webhook 或公网 IP
- ✅ **智能消息解析**：自动提取订单类型、开仓方向、入场金额、止盈、止损等关键信息
- ✅ **自动写入表格**：将解析后的数据自动写入飞书多维表格
- ✅ **支持策略关键词**：识别策略相关的关键词和引用内容
- ✅ **日志记录**：完整记录所有操作和错误信息

## 项目结构

```
.
├── src/
│   ├── agents/
│   │   └── agent.py              # 主程序（监听服务）
│   ├── tools/
│   │   ├── message_parser.py     # 消息解析模块
│   │   ├── bitable_writer.py     # 多维表格写入模块
│   │   └── feishu_listener.py    # 飞书监听服务
│   └── main.py                    # 入口文件
├── tests/
│   └── test_message_parser.py    # 消息解析测试
├── assets/
│   └── feishu_listener.log       # 运行日志
├── docs/
│   ├── README.md                 # 本文件
│   └── SETUP_GUIDE.md            # 详细配置指南
├── config/
│   └── .env.example              # 环境变量示例
└── requirements.txt              # 依赖列表
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制配置文件模板：
```bash
cp config/.env.example config/.env
```

编辑 `config/.env` 文件，填入您的凭证：

```bash
# 飞书应用配置
FEISHU_APP_ID=cli_xxxxxxxxxxxxxxxx
FEISHU_APP_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 多维表格配置
FEISHU_BITABLE_APP_TOKEN=bascnxxxxxxxxxxxxxxx
FEISHU_BITABLE_TABLE_ID=tblxxxxxxxxxxxxxxx
```

### 3. 运行程序

```bash
python -m src.main
```

## 详细配置指南

完整的配置说明请查看：[SETUP_GUIDE.md](SETUP_GUIDE.md)

## 消息格式示例

程序能够识别包含以下关键词的消息：

### 支持的关键词
- **订单类型**：开仓、平仓、买入、卖出、做多、做空、入场、离场
- **方向**：做多、做空、买入、卖出、long、short
- **金额**：入场金额、投入、仓位
- **止盈**：止盈、目标、盈利、tp
- **止损**：止损、风控、sl
- **策略**：策略、交易计划

### 消息示例
```
策略：BTC 4小时突破
做多方向，入场金额：500U
入场位置：95000
止盈：98000
止损：94000
```

## 测试

运行消息解析测试：
```bash
python tests/test_message_parser.py
```

## 常见问题

### Q: 为什么需要创建企业自建应用？
A: 只有企业自建应用才能配置事件订阅，接收群消息。您提供的 webhook 地址是用于发送消息的自定义机器人，无法接收消息。

### Q: 如何获取多维表格的 App Token 和 Table ID？
A: 请查看 [SETUP_GUIDE.md](SETUP_GUIDE.md) 第三步的详细说明。

### Q: 程序如何持久运行？
A: 推荐使用 `nohup`、`screen` 或 systemd 等方式守护进程。

## 注意事项

1. 必须创建**企业自建应用**，不能使用自定义机器人
2. 应用需要发布版本才能接收消息
3. 必须将应用（机器人）添加到目标群
4. 需要开启相应的事件订阅权限

## 技术栈

- **Python** 3.x
- **lark-oapi** - 飞书 SDK
- **requests** - HTTP 请求
- **正则表达式** - 消息解析

## 许可证

MIT

## 支持

如有问题，请查看：
1. 日志文件：`assets/feishu_listener.log`
2. 飞书开放平台日志检索
3. [SETUP_GUIDE.md](SETUP_GUIDE.md)
