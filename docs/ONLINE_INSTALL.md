# 🌐 在线一键部署

本文档介绍如何从代码仓库一键部署飞书多 Agent 协作系统。

---

## 🚀 30 秒快速安装

### Linux / macOS

```bash
# 使用 curl
curl -fsSL https://raw.githubusercontent.com/your-repo/main/install.sh | bash

# 或使用 wget
wget -qO- https://raw.githubusercontent.com/your-repo/main/install.sh | bash
```

### Windows

1. 访问：https://raw.githubusercontent.com/your-repo/main/install.bat
2. 右键 → 另存为 → `install.bat`
3. 双击运行

---

## 📦 安装脚本会做什么

### 自动化流程

1. **环境检查**
   - ✅ 检查 Git 是否安装
   - ✅ 检查 Python 3.8+ 是否安装
   - ✅ 显示系统信息

2. **代码克隆**
   - ✅ 从代码仓库克隆最新代码
   - ✅ 自动处理目录冲突

3. **依赖安装**
   - ✅ 自动安装 requirements.txt 中的所有依赖
   - ✅ 支持网络重试和错误处理

4. **配置初始化**
   - ✅ 自动运行配置向导
   - ✅ 生成默认配置文件

5. **可选启动**
   - ✅ 询问是否立即启动 Web UI
   - ✅ 显示后续使用说明

---

## 🔧 系统要求

### 最低要求

| 组件 | 版本要求 |
|------|---------|
| Python | 3.8 或更高 |
| Git | 任意版本 |
| 操作系统 | Linux / macOS / Windows |
| 内存 | 最低 2GB |
| 磁盘空间 | 最低 1GB |

### 推荐配置

| 组件 | 推荐版本 |
|------|---------|
| Python | 3.10+ |
| Git | 2.0+ |
| 内存 | 4GB+ |
| 磁盘空间 | 5GB+ |

---

## 📋 手动安装步骤

如果自动安装失败，可以按以下步骤手动安装：

### 1. 克隆代码仓库

```bash
git clone https://github.com/your-repo/multi-agent-system.git
cd multi-agent-system
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 初始化配置

```bash
python scripts/auto_init_config.py
```

### 4. 启动系统

```bash
# 快速启动（推荐）
./scripts/quick_deploy.sh

# 或完整部署
./scripts/deploy.sh
```

---

## 🎯 安装选项

### 修改代码仓库地址

如果您想从其他代码仓库安装，可以修改安装脚本：

```bash
# 编辑 install.sh
vim install.sh

# 修改以下变量
REPO_URL="https://github.com/your-username/multi-agent-system.git"
BRANCH="main"

# 保存后运行
bash install.sh
```

### 指定安装目录

```bash
# 克隆到指定目录
git clone https://github.com/your-repo/multi-agent-system.git my-custom-dir
cd my-custom-dir
./scripts/quick_deploy.sh
```

### 使用特定分支

```bash
# 克隆特定分支
git clone -b develop https://github.com/your-repo/multi-agent-system.git
cd multi-agent-system
./scripts/quick_deploy.sh
```

---

## 🔍 常见问题

### Q1: curl/wget 命令无法找到

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install curl wget
```

**Linux (CentOS/RHEL):**
```bash
sudo yum install curl wget
```

**macOS:**
```bash
brew install curl wget
```

### Q2: Git 未安装

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install git
```

**Linux (CentOS/RHEL):**
```bash
sudo yum install git
```

**macOS:**
```bash
brew install git
```

**Windows:**
- 下载安装包：https://git-scm.com/download/win

### Q3: Python 版本过低

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install python3.8
```

**Linux (CentOS/RHEL):**
```bash
sudo yum install python38
```

**macOS:**
```bash
brew install python@3.8
```

**Windows:**
- 下载安装包：https://www.python.org/downloads/

### Q4: 权限不足

**Linux/macOS:**
```bash
# 使用 sudo 运行
sudo bash -c "$(curl -fsSL https://raw.githubusercontent.com/your-repo/main/install.sh)"
```

### Q5: 网络连接失败

使用国内镜像源：
```bash
# 修改 pip 源
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 然后重新安装
./scripts/quick_deploy.sh
```

### Q6: 克隆代码失败

检查网络连接和仓库地址是否正确：
```bash
# 手动测试连接
ping github.com

# 手动克隆
git clone https://github.com/your-repo/multi-agent-system.git
```

---

## 🔄 更新系统

### 方法一：重新运行安装脚本

```bash
# 删除旧目录
rm -rf multi-agent-system

# 重新运行安装
curl -fsSL https://raw.githubusercontent.com/your-repo/main/install.sh | bash
```

### 方法二：手动更新

```bash
# 进入项目目录
cd multi-agent-system

# 拉取最新代码
git pull

# 更新依赖
pip install -r requirements.txt

# 重新启动
./scripts/quick_deploy.sh
```

---

## 🌟 高级功能

### 使用 Docker 部署

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

### 生产环境部署

详细的部署建议请参考：
- [生产环境部署指南](../DEPLOY.md#生产环境部署建议)

### 自定义配置

如果您想自定义配置，请参考：
- [配置指南](../SETUP_GUIDE.md)
- [Webhook 配置指南](WEBHOOK_CONFIG_GUIDE.md)
- [Web UI 使用指南](WEB_UI_GUIDE.md)

---

## 📚 相关文档

- [快速启动指南](../QUICKSTART.md)
- [完整部署指南](../DEPLOY.md)
- [部署文件总结](DEPLOYMENT_SUMMARY.md)
- [多 Agent 系统指南](MULTI_AGENT_GUIDE.md)

---

## 🆘 获取帮助

如果遇到问题，请：

1. 查看日志文件：`logs/` 目录
2. 查阅相关文档：`docs/` 目录
3. 提交 Issue 并附上错误日志
4. 访问项目 Wiki

---

## 📝 下一步

安装完成后，您可以：

1. 📖 阅读 [快速启动指南](../QUICKSTART.md)
2. 🎛️ 访问 Web UI (http://localhost:5000)
3. 📊 查看 [部署文件总结](DEPLOYMENT_SUMMARY.md)
4. 🤖 了解 [多 Agent 系统](MULTI_AGENT_GUIDE.md)

---

## ⚠️ 注意事项

1. **首次安装**：首次运行会自动下载依赖，可能需要几分钟
2. **网络要求**：需要能够访问 GitHub 和 PyPI
3. **权限要求**：需要写权限来安装 Python 包和创建目录
4. **安全建议**：生产环境请使用虚拟环境

---

## 🎉 开始使用

现在就开始使用吧！

```bash
# 一行命令，30 秒启动
curl -fsSL https://raw.githubusercontent.com/your-repo/main/install.sh | bash
```

然后访问：**http://localhost:5000**

祝您使用愉快！🚀
