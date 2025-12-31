# 🔧 配置代码仓库地址

在使用一键部署脚本前，需要先将脚本中的代码仓库地址替换为您实际的仓库地址。

---

## 📍 需要修改的文件

### 1. install.sh

打开 `install.sh`，找到第 16 行左右：

```bash
# 项目配置（需要根据实际情况修改）
REPO_URL="https://github.com/your-username/multi-agent-system.git"
PROJECT_DIR="multi-agent-system"
BRANCH="main"
```

**修改示例：**

```bash
# 项目配置（已修改）
REPO_URL="https://github.com/johnsmith/feishu-multi-agent.git"
PROJECT_DIR="feishu-multi-agent"
BRANCH="main"
```

### 2. install.bat

打开 `install.bat`，找到第 12 行左右：

```batch
REM 项目配置（需要根据实际情况修改）
set "REPO_URL=https://github.com/your-username/multi-agent-system.git"
set "PROJECT_DIR=multi-agent-system"
set "BRANCH=main"
```

**修改示例：**

```batch
REM 项目配置（已修改）
set "REPO_URL=https://github.com/johnsmith/feishu-multi-agent.git"
set "PROJECT_DIR=feishu-multi-agent"
set "BRANCH=main"
```

### 3. index.html

打开 `index.html`，找到所有包含 `your-repo` 的代码块：

```html
<code>curl -fsSL https://raw.githubusercontent.com/your-repo/main/install.sh | bash</code>
```

**修改示例：**

```html
<code>curl -fsSL https://raw.githubusercontent.com/johnsmith/feishu-multi-agent/main/install.sh | bash</code>
```

### 4. docs/ONLINE_INSTALL.md

打开 `docs/ONLINE_INSTALL.md`，找到所有安装命令：

```bash
curl -fsSL https://raw.githubusercontent.com/your-repo/main/install.sh | bash
```

**修改示例：**

```bash
curl -fsSL https://raw.githubusercontent.com/johnsmith/feishu-multi-agent/main/install.sh | bash
```

---

## 🎯 配置示例

### GitHub 仓库

```bash
# 标准格式
REPO_URL="https://github.com/username/repository-name.git"

# 示例
REPO_URL="https://github.com/johnsmith/trading-bot.git"
```

### GitLab 仓库

```bash
# 标准格式
REPO_URL="https://gitlab.com/username/repository-name.git"

# 示例
REPO_URL="https://gitlab.com/jane/trading-system.git"
```

### Gitee 仓库

```bash
# 标准格式
REPO_URL="https://gitee.com/username/repository-name.git"

# 示例
REPO_URL="https://gitee.com/zhangsan/trading-bot.git"
```

### 私有仓库

```bash
# 带 token 的格式
REPO_URL="https://username:token@github.com/username/repository-name.git"

# 或使用 SSH（需要配置 SSH 密钥）
REPO_URL="git@github.com:username/repository-name.git"
```

---

## 📋 配置检查清单

配置完成后，请检查以下项目：

- [ ] `install.sh` 中的 `REPO_URL` 已修改
- [ ] `install.sh` 中的 `PROJECT_DIR` 根据需要修改（可选）
- [ ] `install.sh` 中的 `BRANCH` 根据需要修改（可选）
- [ ] `install.bat` 中的 `REPO_URL` 已修改
- [ ] `install.bat` 中的 `PROJECT_DIR` 根据需要修改（可选）
- [ ] `install.bat` 中的 `BRANCH` 根据需要修改（可选）
- [ ] `index.html` 中的所有 `your-repo` 已替换
- [ ] `docs/ONLINE_INSTALL.md` 中的所有示例已更新
- [ ] README.md 中的示例已更新（如有需要）

---

## ✅ 配置验证

配置完成后，可以测试安装脚本：

### 测试克隆

```bash
# 测试仓库地址是否可访问
git clone https://github.com/johnsmith/feishu-multi-agent.git test-clone

# 如果成功，删除测试目录
rm -rf test-clone
```

### 测试安装脚本

```bash
# 本地测试安装脚本（不实际安装）
bash -n install.sh
```

---

## 🚀 配置完成后

配置完成后，您可以：

1. **提交到代码仓库**

```bash
git add install.sh install.bat index.html docs/ONLINE_INSTALL.md
git commit -m "chore: 配置代码仓库地址"
git push
```

2. **测试在线安装**

```bash
# 从其他机器测试
curl -fsSL https://raw.githubusercontent.com/johnsmith/feishu-multi-agent/main/install.sh | bash
```

3. **发布部署说明**

将 `index.html` 部署到 GitHub Pages 或您的网站，用户可以直接访问进行一键安装。

---

## 📝 常见配置场景

### 场景 1: 使用 main 分支

```bash
REPO_URL="https://github.com/johnsmith/trading-bot.git"
BRANCH="main"
```

### 场景 2: 使用 develop 分支

```bash
REPO_URL="https://github.com/johnsmith/trading-bot.git"
BRANCH="develop"
```

### 场景 3: 使用特定版本标签

```bash
REPO_URL="https://github.com/johnsmith/trading-bot.git"
BRANCH="v1.0.0"
```

### 场景 4: 自定义安装目录

```bash
REPO_URL="https://github.com/johnsmith/trading-bot.git"
PROJECT_DIR="my-trading-system"
```

---

## 🔍 故障排除

### Q1: 克隆失败

**检查：**
- 仓库地址是否正确
- 仓库是否为公开（或已配置访问权限）
- 网络连接是否正常

### Q2: 分支不存在

**检查：**
- 分支名称是否拼写正确
- 该分支是否存在于远程仓库

### Q3: 权限问题

**解决方案：**
```bash
# 使用 sudo 运行（Linux/macOS）
sudo bash install.sh
```

---

## 📞 获取帮助

如果配置过程中遇到问题，请：

1. 查看 [在线部署文档](docs/ONLINE_INSTALL.md)
2. 检查代码仓库的访问权限
3. 提交 Issue 并附上错误信息

---

## 🎉 配置完成

配置完成后，用户可以通过以下方式一键部署：

```bash
# Linux/Mac
curl -fsSL https://raw.githubusercontent.com/johnsmith/feishu-multi-agent/main/install.sh | bash

# Windows
# 下载并运行 install.bat
```

祝部署顺利！🚀
