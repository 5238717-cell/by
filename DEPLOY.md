# 🚀 一键部署指南

本指南提供完整的一键部署方案，支持 Linux/Mac 和 Windows 系统。

## 快速开始

### Linux/Mac 系统

```bash
# 1. 赋予执行权限
chmod +x scripts/deploy.sh

# 2. 运行一键部署脚本
./scripts/deploy.sh
```

### Windows 系统

```cmd
# 运行一键部署脚本
scripts\deploy.bat
```

---

## 部署流程

部署脚本会自动执行以下步骤：

### 1. 环境检查
- ✅ 检查 Python 3.8+ 是否已安装
- ✅ 检查 Python 版本是否满足要求
- ✅ 显示系统信息

### 2. 依赖安装
- ✅ 自动安装 `requirements.txt` 中的所有依赖
- ✅ 包括：langchain, langgraph, fastapi, lark-oapi 等

### 3. 目录创建
- ✅ 创建 `assets` 目录（资源文件）
- ✅ 创建 `logs` 目录（日志文件）
- ✅ 创建 `config` 目录（配置文件）
- ✅ 创建 `data` 目录（数据文件）

### 4. 配置检查
- ✅ 检查 `config/agent_llm_config.json` 是否存在
- ✅ 检查 `config/webhook_config.json` 是否存在
- ✅ 如果缺少配置文件，提示运行配置向导

### 5. 服务选择
部署完成后，您可以选择启动以下服务：

| 选项 | 服务 | 说明 |
|------|------|------|
| 1 | Webhook 服务器 | 接收外部消息并转发给 Agent |
| 2 | Web UI 配置管理系统 | 可视化配置界面（推荐） |
| 3 | 多 Agent 协作系统 | 完整的多 Agent 系统 |
| 4 | 系统状态 | 查看配置和依赖状态 |
| 5 | 运行测试 | 执行单元测试 |
| 6 | 查看日志 | 查看系统运行日志 |
| 7 | 停止服务 | 停止所有运行中的服务 |
| 8 | 退出 | 退出部署系统 |

---

## 详细功能说明

### 📊 系统状态检查

检查内容包括：
- **配置文件状态**: 检查所有必需的配置文件是否存在
- **依赖包状态**: 检查关键 Python 包是否已安装
- **服务运行状态**: 检查哪些服务正在运行

### 🔧 配置向导

如果配置文件缺失，部署脚本会提示您运行配置向导：

```bash
python scripts/auto_init_config.py
```

配置向导会引导您完成：
1. 模型配置（LLM 选择、参数设置）
2. 飞书应用配置（App ID、App Secret）
3. 多维表格配置（App Token、Table ID）
4. Webhook 端点配置
5. 消息过滤规则配置
6. 交易参数配置

详细说明请参考：
- [配置指南](docs/SETUP_GUIDE.md)
- [Webhook 配置指南](docs/WEBHOOK_CONFIG_GUIDE.md)

### 📝 日志查看

部署脚本支持查看系统日志：

```bash
# 在部署菜单中选择选项 6
# 系统会列出所有可用的日志文件：
#   - logs/webhook_server.log
#   - logs/web_ui.log
#   - logs/multi_agent_system.log
#   - logs/feishu_listener.log
```

### ⏹️ 停止服务

在部署菜单中选择选项 7，可以一键停止所有运行中的服务：
- Webhook 服务器
- Web UI 服务
- 多 Agent 系统

---

## 单独启动服务

如果您已经完成部署，想单独启动某个服务：

### 启动 Webhook 服务器

```bash
# Linux/Mac
./scripts/start_webhook_server.sh

# Windows
scripts\start_webhook_server.bat

# 或直接运行
python src/webhook_server.py
```

### 启动 Web UI 配置管理系统

```bash
# Linux/Mac
./scripts/start_web_ui.sh

# Windows
scripts\start_web_ui.bat

# 或直接运行
python src/web_ui.py
```

访问地址：http://localhost:5000

### 启动多 Agent 协作系统

```bash
# 直接运行
python src/main_multiagent.py
```

---

## 常见问题

### Q1: Python 版本过低怎么办？

部署脚本会检测 Python 版本，如果低于 3.8 会报错并退出。请先升级 Python：

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3.8

# macOS (使用 Homebrew)
brew install python@3.8
```

### Q2: 依赖安装失败怎么办？

请检查网络连接，或使用国内镜像源：

```bash
# 使用清华镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q3: 配置文件如何手动创建？

参考以下文档手动创建配置文件：
- [配置指南](docs/SETUP_GUIDE.md)
- [Webhook 配置指南](docs/WEBHOOK_CONFIG_GUIDE.md)

### Q4: 如何在不同端口启动 Web UI？

```bash
# 修改端口后启动
WEBUI_PORT=8080 ./scripts/start_web_ui.sh

# Windows
set WEBUI_PORT=8080
scripts\start_web_ui.bat
```

### Q5: 如何后台运行服务？

```bash
# 使用 nohup 后台运行
nohup python src/webhook_server.py > logs/webhook_server.log 2>&1 &

# 查看进程
ps aux | grep webhook_server

# 停止服务
kill <PID>
```

---

## Docker 部署（可选）

如果您想使用 Docker 部署，请参考：

```bash
# 构建镜像
docker build -t multi-agent-system .

# 运行容器
docker run -d \
  -p 5000:5000 \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/logs:/app/logs \
  --name multi-agent \
  multi-agent-system
```

> ⚠️ 注意：Docker 部署需要额外的 Dockerfile 和 docker-compose.yml 文件

---

## 生产环境部署建议

### 1. 使用进程管理器

```bash
# 使用 Supervisor
sudo apt-get install supervisor

# 创建配置文件 /etc/supervisor/conf.d/multi-agent.conf
[program:webhook-server]
command=/path/to/python src/webhook_server.py
directory=/path/to/project
autostart=true
autorestart=true
stderr_logfile=/var/log/multi-agent/webhook.err.log
stdout_logfile=/var/log/multi-agent/webhook.out.log
```

### 2. 使用 Nginx 反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. 配置 SSL/HTTPS

```bash
# 使用 Certbot 获取免费 SSL 证书
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 4. 定期备份

```bash
# 备份配置和日志
tar -czf backup_$(date +%Y%m%d).tar.gz config/ logs/

# 定时备份（每天凌晨 2 点）
0 2 * * * /path/to/backup_script.sh
```

---

## 下一步

部署完成后，您可以：

1. 📖 阅读 [多 Agent 系统指南](docs/MULTI_AGENT_GUIDE.md)
2. 🎛️ 访问 Web UI 配置管理系统 (http://localhost:5000)
3. 📊 查看 [Web UI 使用指南](docs/WEB_UI_GUIDE.md)
4. 🤖 了解 [自动交易功能](docs/auto_trading_guide.md)
5. 💰 配置 [币安 API](docs/binance_api_guide.md)

---

## 获取帮助

如果遇到问题，请：

1. 查看日志文件：`logs/` 目录
2. 运行系统状态检查：部署菜单选项 4
3. 查阅详细文档：`docs/` 目录
4. 提交 Issue 并附上错误日志

---

## 更新部署

当项目更新后，重新部署：

```bash
# 拉取最新代码
git pull

# 运行部署脚本（会自动更新依赖）
./scripts/deploy.sh
```
