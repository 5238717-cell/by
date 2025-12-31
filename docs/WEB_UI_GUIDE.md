# Web UI 配置管理系统

## 🎯 功能概述

Webhook 配置管理系统提供了可视化的 Web 界面，让您可以通过浏览器轻松配置和管理整个系统。

## ✨ 主要功能

### 1. **仪表板**
- 系统配置概览
- 实时统计信息
- 快速操作入口

### 2. **Webhook 管理**
- 添加/编辑/删除 Webhook 端点
- 启用/禁用 Webhook
- 实时预览配置

### 3. **服务器配置**
- 监听地址和端口
- 工作进程数
- 配置预览

### 4. **过滤规则**
- 排除关键词管理
- 交易关键词管理
- 排除模式管理
- 可视化标签编辑

### 5. **消息处理**
- 启用/禁用消息过滤
- 启用/禁用 Agent 分析
- 自动交易开关（慎用）
- 保存到飞书多维表格
- 记录日志开关

## 🚀 快速开始

### 方法 1：使用启动脚本（推荐）

#### Linux/Mac
```bash
cd /workspace/projects
chmod +x scripts/start_web_ui.sh
./scripts/start_web_ui.sh
```

#### Windows
```cmd
cd /workspace/projects
scripts\start_web_ui.bat
```

### 方法 2：直接运行 Python 脚本

```bash
cd /workspace/projects
python src/web_ui.py
```

### 方法 3：指定端口运行

```bash
# Linux/Mac
WEBUI_PORT=8080 ./scripts/start_web_ui.sh

# Windows
set WEBUI_PORT=8080
scripts\start_web_ui.bat
```

## 🌐 访问 Web UI

服务器启动后，在浏览器中打开：

```
http://localhost:5000
```

## 📋 功能说明

### 仪表板
- 显示系统配置概览
- Webhook 数量统计
- 服务器配置信息
- 过滤规则统计
- 快速操作按钮

### Webhook 配置
- **添加 Webhook**：点击右上角"添加 Webhook"按钮
- **编辑 Webhook**：点击操作列的编辑按钮
- **启用/禁用**：点击操作列的切换按钮
- **删除 Webhook**：点击操作列的删除按钮

### 服务器配置
- 配置监听地址（默认：0.0.0.0）
- 配置监听端口（默认：8080）
- 配置工作进程数（默认：1）
- 实时配置预览

### 过滤规则
- **排除关键词**：添加/删除营销、广告等排除关键词
- **交易关键词**：添加/删除交易相关关键词
- **排除模式**：添加/删除分析、免责声明等排除模式
- 支持回车键快速添加
- 可视化标签展示

### 消息处理
- 使用开关控制各项功能
- 自动交易功能有安全警告
- 实时配置预览

## 🔧 API 端点

Web UI 提供了完整的 REST API：

### 获取配置
```http
GET /api/config
```

### 保存配置
```http
POST /api/config
Content-Type: application/json

{
  "webhooks": [...],
  "server": {...},
  "filter_rules": {...},
  "message_processing": {...}
}
```

### Webhook 管理
```http
# 添加 Webhook
POST /api/webhook

# 更新 Webhook
PUT /api/webhook/{webhook_id}

# 删除 Webhook
DELETE /api/webhook/{webhook_id}

# 切换 Webhook 状态
POST /api/webhook/{webhook_id}/toggle
```

### 服务器配置
```http
POST /api/server
Content-Type: application/json

{
  "host": "0.0.0.0",
  "port": 8080,
  "workers": 1
}
```

### 过滤规则
```http
POST /api/filters
Content-Type: application/json

{
  "exclude_keywords": ["广告", "营销"],
  "trading_keywords": ["开仓", "平仓"],
  "exclude_patterns": ["趋势分析"]
}
```

### 消息处理
```http
POST /api/processing
Content-Type: application/json

{
  "enable_filter": true,
  "enable_agent_analysis": true,
  "auto_trade": false,
  "save_to_bitable": true,
  "log_all_messages": true
}
```

### 配置导入/导出
```http
# 导出配置
GET /api/config/export

# 导入配置
POST /api/config/import
Content-Type: application/json
```

## 💡 使用技巧

1. **实时保存**：所有配置修改后点击"保存"按钮立即生效
2. **配置预览**：每个页面底部都有配置预览，方便确认
3. **快速添加**：在过滤规则页面，输入关键词后按回车快速添加
4. **安全提示**：启用自动交易前会显示警告提示
5. **API 调用**：可以通过 API 端点直接操作配置

## 🔒 安全建议

1. 修改默认端口，避免暴露在公网
2. 使用反向代理（如 Nginx）添加认证
3. 不要在公网环境启用自动交易
4. 定期备份配置文件
5. 使用 HTTPS 访问（生产环境）

## 🐛 故障排查

### 问题 1：无法访问 Web UI
- 检查防火墙设置
- 确认端口未被占用
- 检查服务器是否正常运行

### 问题 2：配置保存失败
- 检查文件权限
- 确认配置文件格式正确
- 查看服务器日志

### 问题 3：页面显示异常
- 清除浏览器缓存
- 检查网络连接
- 确认静态文件正确加载

## 📚 相关文档

- [README.md](../README.md) - 项目主文档
- [WEBHOOK_CONFIG_GUIDE.md](WEBHOOK_CONFIG_GUIDE.md) - Webhook 配置指南
- [QUICK_CONFIG_GUIDE.md](QUICK_CONFIG_GUIDE.md) - 快速配置指南

## 🎉 开始使用

现在启动 Web UI 服务器，开始配置您的系统吧！

```bash
cd /workspace/projects
./scripts/start_web_ui.sh
```

然后在浏览器中打开：http://localhost:5000
