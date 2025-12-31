# 📦 部署文件总结

本文档总结了一键部署相关的所有文件及其用途。

---

## 📁 新增文件列表

### 脚本文件（scripts/）

| 文件名 | 用途 | 适用系统 |
|--------|------|---------|
| `deploy.sh` | 完整部署脚本，提供交互式菜单 | Linux/Mac |
| `deploy.bat` | 完整部署脚本，提供交互式菜单 | Windows |
| `quick_deploy.sh` | 快速部署脚本，自动配置并启动 Web UI | Linux/Mac |
| `quick_deploy.bat` | 快速部署脚本，自动配置并启动 Web UI | Windows |

### 文档文件（根目录）

| 文件名 | 用途 |
|--------|------|
| `DEPLOY.md` | 完整的部署指南 |
| `QUICKSTART.md` | 30 秒快速启动指南 |

---

## 🚀 快速使用

### 方式一：快速部署（推荐新手）

**Linux/Mac:**
```bash
./scripts/quick_deploy.sh
```

**Windows:**
```cmd
scripts\quick_deploy.bat
```

**特点：**
- ✅ 自动检查环境
- ✅ 自动安装依赖
- ✅ 自动初始化配置
- ✅ 直接启动 Web UI
- ✅ 无需手动操作

**适合场景：** 首次使用、快速体验、新手用户

---

### 方式二：完整部署（推荐高级用户）

**Linux/Mac:**
```bash
./scripts/deploy.sh
```

**Windows:**
```cmd
scripts\deploy.bat
```

**特点：**
- ✅ 提供交互式菜单
- ✅ 环境健康检查
- ✅ 系统状态查看
- ✅ 多服务选择
- ✅ 日志管理
- ✅ 服务控制

**菜单选项：**
1. 启动 Webhook 服务器
2. 启动 Web UI 配置管理系统
3. 启动多 Agent 协作系统
4. 查看系统状态
5. 运行测试
6. 查看日志
7. 停止所有服务
8. 退出

**适合场景：** 高级用户、生产环境、需要精细控制

---

## 📋 部署脚本功能详解

### 环境检查
- Python 版本检查（要求 3.8+）
- 关键依赖检查
- 配置文件检查

### 依赖安装
- 自动安装 `requirements.txt` 中的所有包
- 支持国内镜像源
- 显示安装进度

### 目录创建
- `assets/` - 资源文件目录
- `logs/` - 日志文件目录
- `config/` - 配置文件目录
- `data/` - 数据文件目录

### 配置初始化
- 检查配置文件是否存在
- 自动运行配置向导
- 生成默认配置

### 服务管理
- 启动/停止服务
- 查看运行状态
- 查看日志
- 运行测试

---

## 🎯 使用场景对照表

| 用户类型 | 推荐脚本 | 原因 |
|---------|---------|------|
| 新手用户 | `quick_deploy.sh/bat` | 自动化程度高，无需手动配置 |
| 快速测试 | `quick_deploy.sh/bat` | 一键启动，快速验证 |
| 生产部署 | `deploy.sh/bat` | 提供完整控制和监控 |
| 高级用户 | `deploy.sh/bat` | 支持所有高级功能 |
| 开发调试 | `deploy.sh/bat` | 便于查看状态和日志 |

---

## 🔧 故障排除

### 1. 脚本无法执行

**问题：** `Permission denied`

**解决：**
```bash
chmod +x scripts/*.sh
```

### 2. Python 未找到

**问题：** `command not found: python`

**解决：**
```bash
# Ubuntu/Debian
sudo apt-get install python3.8

# macOS
brew install python@3.8

# Windows
# 下载安装: https://www.python.org/downloads/
```

### 3. 依赖安装失败

**问题：** `pip install` 失败

**解决：**
```bash
# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 4. 配置文件缺失

**问题：** 提示缺少配置文件

**解决：**
```bash
# 脚本会自动检测并提示运行配置向导
python scripts/auto_init_config.py
```

---

## 📖 文档导航

### 新手路径
1. [QUICKSTART.md](../QUICKSTART.md) - 30 秒快速启动
2. 运行 `quick_deploy.sh` 启动系统
3. 访问 http://localhost:5000

### 高级用户路径
1. [DEPLOY.md](../DEPLOY.md) - 完整部署指南
2. 运行 `deploy.sh` 选择服务
3. 根据需要配置系统

### 深度定制路径
1. [SETUP_GUIDE.md](SETUP_GUIDE.md) - 配置指南
2. [WEBHOOK_CONFIG_GUIDE.md](WEBHOOK_CONFIG_GUIDE.md) - Webhook 配置
3. [WEB_UI_GUIDE.md](WEB_UI_GUIDE.md) - Web UI 使用
4. [MULTI_AGENT_GUIDE.md](MULTI_AGENT_GUIDE.md) - 多 Agent 系统

---

## 🎓 最佳实践

### 开发环境
1. 使用 `quick_deploy.sh` 快速启动
2. 通过 Web UI 管理配置
3. 查看日志进行调试

### 测试环境
1. 使用 `deploy.sh` 完整部署
2. 使用"运行测试"功能验证
3. 使用"系统状态"检查环境

### 生产环境
1. 使用 `deploy.sh` 完整部署
2. 配置 Supervisor 或 Systemd
3. 配置 Nginx 反向代理
4. 启用 SSL/HTTPS
5. 配置日志轮转
6. 设置定期备份

详细生产部署请参考 [DEPLOY.md](../DEPLOY.md) 的"生产环境部署建议"部分。

---

## 🔄 更新和维护

### 更新系统

```bash
# 拉取最新代码
git pull

# 重新运行部署脚本
./scripts/deploy.sh
```

### 备份配置

```bash
# 备份配置文件
tar -czf backup_$(date +%Y%m%d).tar.gz config/ logs/

# 恢复配置
tar -xzf backup_YYYYMMDD.tar.gz
```

---

## 📞 获取帮助

如果遇到问题：

1. 查看日志文件：`logs/` 目录
2. 运行系统状态检查：`deploy.sh` → 选项 4
3. 查阅相关文档：`docs/` 目录
4. 提交 Issue 并附上错误日志

---

## 📝 变更记录

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| 1.0.0 | 2025-01-XX | 初始版本，支持一键部署 |
| 1.0.1 | 2025-01-XX | 添加快速部署脚本 |
| 1.0.2 | 2025-01-XX | 添加 Windows 支持 |
| 1.0.3 | 2025-01-XX | 优化交互体验 |

---

## 🎉 总结

通过一键部署系统，您可以：

- ✅ 在 30 秒内启动系统（快速部署）
- ✅ 通过交互式菜单管理所有服务（完整部署）
- ✅ 跨平台支持（Linux/Mac/Windows）
- ✅ 自动化环境检查和依赖安装
- ✅ 可视化配置管理（Web UI）
- ✅ 完整的文档支持

开始使用：[快速启动指南](../QUICKSTART.md)
