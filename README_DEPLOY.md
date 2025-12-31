# 📦 代码推送和部署指南

## 快速开始

### 步骤 1：推送代码到 GitHub

运行推送脚本：
```bash
./push_to_github.sh
```

按照提示选择认证方式并完成推送。

### 步骤 2：在新服务器上部署

```bash
# 1. 克隆代码
git clone https://github.com/5238717-cell/by.git
cd by

# 2. 运行一键安装
bash install.sh

# 3. 启动服务
./quick_start.sh
```

### 步骤 3：访问 Web UI

```
http://你的服务器IP:80
```

---

## 详细说明

### 推送代码

#### 方式 1：使用推送脚本（推荐）

```bash
./push_to_github.sh
```

脚本会自动：
- 检查 Git 状态
- 添加和提交更改
- 拉取最新代码
- 推送到 GitHub

#### 方式 2：手动推送

```bash
# 添加更改
git add -A

# 提交更改
git commit -m "你的提交信息"

# 拉取最新代码
git pull origin main

# 推送代码
git push origin main
```

### 认证方式

#### 方法 A：Personal Access Token

1. 生成 Token：https://github.com/settings/tokens
2. 选择权限：`repo` (完整仓库访问权限)
3. 推送时输入：
   - Username: 你的 GitHub 用户名
   - Password: 刚刚生成的 Token

#### 方法 B：SSH Key（推荐长期使用）

1. 生成 SSH Key：
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   ```

2. 添加到 GitHub：
   - 访问：https://github.com/settings/keys
   - 点击 "New SSH key"
   - 粘贴公钥内容 (`cat ~/.ssh/id_ed25519.pub`)

3. 修改远程 URL：
   ```bash
   git remote set-url origin git@github.com:5238717-cell/by.git
   ```

4. 推送代码：
   ```bash
   git push origin main
   ```

---

## 手动部署

### 前提条件

- Ubuntu 20.04+ 或 Debian 10+
- Python 3.8+
- Root 权限

### 部署步骤

```bash
# 1. 克隆代码仓库
git clone https://github.com/5238717-cell/by.git
cd by

# 2. 运行一键安装脚本
bash install.sh

# 3. 启动服务
./quick_start.sh

# 4. 访问 Web UI
# 在浏览器中打开：http://你的服务器IP:80
```

### 一键安装脚本会自动完成

- ✅ 检查系统环境
- ✅ 安装系统依赖
- ✅ 创建 Python 虚拟环境
- ✅ 安装 Python 依赖包
- ✅ 初始化配置文件

### 服务管理

```bash
# 查看服务状态
./scripts/manage.sh status

# 启动服务
./scripts/manage.sh start

# 停止服务
./scripts/manage.sh stop

# 重启服务
./scripts/manage.sh restart

# 查看日志
./scripts/manage.sh logs
```

---

## 配置说明

### 1. 首次访问

访问 `http://你的服务器IP:80` 后，需要配置：

- **飞书应用凭证**
  - App ID
  - App Secret

- **币安 API 密钥**（如需自动交易）
  - API Key
  - API Secret

- **多维表格配置**
  - App Token
  - Table ID

### 2. 配置文件位置

- Webhook 配置：`config/webhook_config.json`
- LLM 配置：`config/agent_llm_config.json`
- Nginx 配置：`/etc/nginx/sites-available/webhook-system`

### 3. 修改配置后重启

```bash
# 修改配置文件后重启服务
./scripts/manage.sh restart
```

---

## 常见问题

### Q: 推送时提示认证失败？

**A**: 检查以下几点：
1. Personal Access Token 是否已过期
2. Token 权限是否包含 `repo`
3. 用户名和 Token 是否输入正确

### Q: 安装失败怎么办？

**A**: 查看安装日志：
```bash
# 重新运行安装脚本，查看详细输出
bash install.sh

# 或手动安装依赖
apt-get update
apt-get install -y python3-pip python3-venv nginx git
```

### Q: 服务启动后无法访问？

**A**: 检查以下几点：
1. 查看服务状态：`./scripts/manage.sh status`
2. 查看日志：`tail -f /var/log/webhook-system.log`
3. 检查安全组配置（云服务器控制台）
4. 检查防火墙：
   ```bash
   # Ubuntu/Debian
   sudo ufw allow 80/tcp
   # CentOS/RHEL
   sudo firewall-cmd --permanent --add-port=80/tcp
   sudo firewall-cmd --reload
   ```

### Q: 如何更新代码？

**A**:
```bash
# 拉取最新代码
git pull origin main

# 重启服务
./scripts/manage.sh restart
```

---

## 相关文档

- [完整部署手册](MANUAL_DEPLOY.md)
- [服务器配置文档](docs/SERVER_CONFIG.md)
- [Web UI 使用指南](docs/WEB_UI_GUIDE.md)
- [快速启动指南](QUICKSTART.md)

---

## 技术支持

如遇问题：
1. 查看日志：`tail -f /var/log/webhook-system.log`
2. 检查配置文件
3. 查看相关文档

---

**项目地址**：https://github.com/5238717-cell/by
