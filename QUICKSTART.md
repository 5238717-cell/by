# 🚀 快速启动指南

## 最快 30 秒启动系统

```bash
# Linux/Mac
./scripts/quick_deploy.sh

# Windows
scripts\quick_deploy.bat
```

访问：**http://localhost:5000**

---

## 不同场景的启动方式

### 🎯 我只想快速体验

```bash
# 使用快速部署脚本
./scripts/quick_deploy.sh
```
→ 自动完成所有配置，直接启动 Web UI

### 🔧 我想完整控制所有选项

```bash
# 使用完整部署脚本
./scripts/deploy.sh
```
→ 提供交互式菜单，可选择启动不同服务

### 📦 我想分步手动部署

参考 [README.md](README.md) 中的"快速开始 - 手动安装"部分

---

## 一键部署功能对照表

| 脚本 | 适用场景 | 功能 | 适合人群 |
|------|---------|------|---------|
| `quick_deploy.sh` | 快速体验 | 自动配置 + 启动 Web UI | 新手、快速测试 |
| `deploy.sh` | 完整部署 | 交互式菜单 + 多服务选择 | 高级用户、生产环境 |
| `start_web_ui.sh` | 仅启动 UI | 启动 Web UI 服务 | 已配置完成 |
| `start_webhook_server.sh` | 仅启动 Webhook | 启动 Webhook 服务 | 仅需 Webhook 功能 |

---

## 常见问题

### ❓ 脚本无法执行？

```bash
# 添加执行权限
chmod +x scripts/*.sh
```

### ❓ 提示找不到 Python？

请先安装 Python 3.8+：
```bash
# Ubuntu/Debian
sudo apt-get install python3.8

# macOS
brew install python@3.8

# Windows
# 下载安装包: https://www.python.org/downloads/
```

### ❓ 依赖安装失败？

使用国内镜像源：
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### ❓ 如何停止服务？

按 `Ctrl+C` 停止当前服务

---

## 下一步

1. 📖 [查看完整部署指南](DEPLOY.md)
2. 📖 [阅读用户手册](docs/README.md)
3. 🎛️ [配置 Webhook](docs/WEBHOOK_CONFIG_GUIDE.md)
4. 🌐 [使用 Web UI](docs/WEB_UI_GUIDE.md)
5. 🤖 [了解多 Agent 系统](docs/MULTI_AGENT_GUIDE.md)
