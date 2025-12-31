# 手动部署指南

## 一、推送代码到 GitHub

### 方法 1：使用 Personal Access Token（推荐）

1. **生成 GitHub Personal Access Token**
   - 访问：https://github.com/settings/tokens
   - 点击 "Generate new token" → "Generate new token (classic)"
   - 勾选权限：
     - `repo` (完整仓库访问权限)
     - `workflow` (工作流权限)
   - 点击 "Generate token"
   - 复制生成的 token（注意：token 只显示一次）

2. **配置 Git 凭据**

   ```bash
   # 方法 A：在推送时输入 token（推荐）
   git push origin main
   # 用户名：你的 GitHub 用户名
   # 密码：刚才生成的 Personal Access Token

   # 方法 B：使用 URL 中包含 token（不推荐，token 会暴露）
   # git remote set-url origin https://USERNAME:TOKEN@github.com/5238717-cell/by.git
   ```

3. **推送代码**

   ```bash
   cd /workspace/projects
   git push origin main
   ```

### 方法 2：使用 SSH Key（推荐长期使用）

1. **生成 SSH Key**

   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   # 按提示操作，直接回车使用默认路径和空密码
   ```

2. **添加 SSH Key 到 GitHub**

   ```bash
   # 复制公钥
   cat ~/.ssh/id_ed25519.pub
   ```

   - 访问：https://github.com/settings/keys
   - 点击 "New SSH key"
   - 粘贴公钥内容
   - 点击 "Add SSH key"

3. **修改远程 URL 为 SSH**

   ```bash
   git remote set-url origin git@github.com:5238717-cell/by.git
   ```

4. **推送代码**

   ```bash
   git push origin main
   ```

---

## 二、在新服务器上手动部署

### 前提条件

- Ubuntu 20.04+ 或 Debian 10+
- Python 3.8+
- Root 权限或 sudo 权限

### 部署步骤

#### 1. 克隆代码仓库

```bash
# 使用 HTTPS
git clone https://github.com/5238717-cell/by.git
cd by

# 或使用 SSH
git clone git@github.com:5238717-cell/by.git
cd by
```

#### 2. 运行一键安装脚本

```bash
# Linux/Mac
bash install.sh

# Windows (Git Bash 或 WSL)
bash install.sh
```

安装脚本会自动完成：
- ✅ 安装系统依赖
- ✅ 检查 Python 环境
- ✅ 创建虚拟环境
- ✅ 安装 Python 依赖包
- ✅ 初始化配置文件

#### 3. 快速启动服务

```bash
# 方式 1：使用快速启动脚本（推荐）
./quick_start.sh

# 方式 2：使用管理脚本
./scripts/manage.sh start

# 方式 3：手动启动
cd /workspace/projects
nohup /opt/webhook-system-env/bin/python src/web_ui.py > /var/log/webhook-system.log 2>&1 &
```

#### 4. 配置服务（首次运行）

访问 Web UI 界面：`http://你的服务器IP:5000`

在浏览器中完成以下配置：
1. 配置飞书应用凭证（App ID, App Secret）
2. 配置币安 API 密钥（API Key, Secret）
3. 配置飞书多维表格（App Token, Table ID）
4. 设置 Webhook 端点和过滤规则

#### 5. 配置 Nginx 反向代理（可选，推荐生产环境）

```bash
# 安装 Nginx（如果未安装）
apt-get update && apt-get install -y nginx

# 配置 Nginx
cat > /etc/nginx/sites-available/webhook-system << 'EOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# 启用配置
ln -sf /etc/nginx/sites-available/webhook-system /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# 测试并重启
nginx -t
nginx -s reload
```

#### 6. 配置安全组（云服务器）

在云服务商控制台开放以下端口：
- **80** (HTTP，用于 Nginx 反向代理)
- **443** (HTTPS，用于安全访问)
- **5000** (可选，用于直接访问 FastAPI，生产环境建议关闭)

#### 7. 配置 HTTPS（生产环境推荐）

```bash
# 安装 Certbot
apt-get install -y certbot python3-certbot-nginx

# 自动配置 HTTPS
certbot --nginx -d your-domain.com

# 自动续期
certbot renew --dry-run
```

---

## 三、服务管理

### 使用管理脚本

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

### 手动管理

```bash
# 启动 Web UI
/opt/webhook-system-env/bin/python src/web_ui.py

# 后台启动
nohup /opt/webhook-system-env/bin/python src/web_ui.py > /var/log/webhook-system.log 2>&1 &

# 停止服务
lsof -ti:5000 | xargs kill -9

# 查看日志
tail -f /var/log/webhook-system.log
```

---

## 四、配置详解

### 1. 飞书应用配置

配置文件：`config/webhook_config.json`

```json
{
  "lark": {
    "app_id": "your_app_id",
    "app_secret": "your_app_secret",
    "encrypt_key": "your_encrypt_key",
    "verification_token": "your_verification_token"
  }
}
```

**获取步骤**：
1. 访问：https://open.feishu.cn/app
2. 创建应用或选择现有应用
3. 在"凭证与基础信息"页面获取 App ID 和 App Secret
4. 在"事件订阅"页面配置 Webhook URL

### 2. 币安 API 配置

配置文件：`config/webhook_config.json`

```json
{
  "binance": {
    "api_key": "your_api_key",
    "api_secret": "your_api_secret",
    "testnet": false
  }
}
```

**获取步骤**：
1. 访问：https://www.binance.com/zh-CN/my/settings/api-management
2. 创建新 API Key
3. **重要**：只勾选"读取"和"交易"权限，不要勾选"提现"
4. 建议设置 IP 白名单

### 3. 多维表格配置

配置文件：`config/webhook_config.json`

```json
{
  "bitable": {
    "app_token": "your_app_token",
    "table_id": "your_table_id"
  }
}
```

**获取步骤**：
1. 打开飞书多维表格
2. 在 URL 中获取 app_token（如：`https://bitable.cn/.../app_token/.../table_id/...`）
3. 在表格设置中获取 table_id

### 4. LLM 配置

配置文件：`config/agent_llm_config.json`

```json
{
  "config": {
    "model": "doubao-seed-1-6-251015",
    "temperature": 0.7,
    "top_p": 0.9,
    "max_completion_tokens": 10000,
    "timeout": 600,
    "thinking": "disabled"
  },
  "sp": "你是一个飞书交易信号分析助手...",
  "tools": []
}
```

---

## 五、故障排查

### 问题 1：端口被占用

```bash
# 查看端口占用
lsof -i:5000
lsof -i:80

# 停止占用进程
lsof -ti:5000 | xargs kill -9
```

### 问题 2：依赖安装失败

```bash
# 重新安装依赖
/opt/webhook-system-env/bin/pip install -r requirements-web-ui.txt

# 如果安装 dbus-python 失败
apt-get install -y pkg-config libdbus-1-dev libglib2.0-dev libcairo2-dev
```

### 问题 3：服务无法启动

```bash
# 查看日志
tail -100 /var/log/webhook-system.log

# 手动启动查看错误
/opt/webhook-system-env/bin/python src/web_ui.py
```

### 问题 4：外部无法访问

1. 检查安全组配置（云服务器控制台）
2. 检查防火墙设置
   ```bash
   # Ubuntu/Debian (UFW)
   ufw allow 80/tcp
   ufw allow 443/tcp

   # CentOS/RHEL (firewalld)
   firewall-cmd --permanent --add-port=80/tcp
   firewall-cmd --permanent --add-port=443/tcp
   firewall-cmd --reload
   ```
3. 检查服务监听地址
   ```bash
   netstat -tlnp | grep :5000
   # 应该显示 0.0.0.0:5000 或 :::5000
   ```

### 问题 5：推送代码失败

**错误**：`could not read Password`

**解决**：
```bash
# 重新配置远程 URL（移除 token）
git remote set-url origin https://github.com/5238717-cell/by.git

# 推送时输入用户名和 token
git push origin main
# Username: 5238717-cell
# Password: [你的 Personal Access Token]
```

---

## 六、生产环境优化

### 1. 配置开机自启动

创建 systemd 服务：
```bash
cat > /etc/systemd/system/webhook-system.service << 'EOF'
[Unit]
Description=Webhook Configuration Management System
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/workspace/projects
Environment="PATH=/opt/webhook-system-env/bin"
ExecStart=/opt/webhook-system-env/bin/python /workspace/projects/src/web_ui.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 启用服务
systemctl daemon-reload
systemctl enable webhook-system
systemctl start webhook-system
```

### 2. 配置日志轮转

```bash
cat > /etc/logrotate.d/webhook-system << 'EOF'
/var/log/webhook-system.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 root root
    sharedscripts
    postrotate
        systemctl reload webhook-system > /dev/null 2>&1 || true
    endscript
}
EOF
```

### 3. 配置监控告警

```bash
# 创建健康检查脚本
cat > /usr/local/bin/check-webhook.sh << 'EOF'
#!/bin/bash
if ! curl -sf http://localhost:5000 > /dev/null; then
    echo "Webhook service is down, restarting..."
    systemctl restart webhook-system
fi
EOF

chmod +x /usr/local/bin/check-webhook.sh

# 添加到 crontab（每分钟检查一次）
crontab -e
# 添加：* * * * * /usr/local/bin/check-webhook.sh
```

---

## 七、访问地址

### 开发环境
- Web UI：http://localhost:5000
- Nginx：http://localhost:80

### 生产环境
```
http://your-server-ip:80
https://your-domain.com  # 配置 HTTPS 后
```

### API 文档
```
http://your-server-ip:5000/api/docs
```

---

## 八、快速参考

### 常用命令

```bash
# 克隆代码
git clone https://github.com/5238717-cell/by.git && cd by

# 快速启动
./quick_start.sh

# 服务管理
./scripts/manage.sh {status|start|stop|restart|logs}

# 查看日志
tail -f /var/log/webhook-system.log

# 更新代码
git pull origin main
./scripts/manage.sh restart
```

### 重要文件路径

| 文件 | 路径 |
|------|------|
| 项目目录 | `/workspace/projects` |
| 虚拟环境 | `/opt/webhook-system-env` |
| 配置目录 | `/workspace/projects/config` |
| Web UI 代码 | `/workspace/projects/src/web_ui.py` |
| 日志文件 | `/var/log/webhook-system.log` |
| Nginx 配置 | `/etc/nginx/sites-available/webhook-system` |
| 管理脚本 | `/workspace/projects/scripts/manage.sh` |

---

## 九、技术支持

如遇问题，请：
1. 查看日志：`tail -f /var/log/webhook-system.log`
2. 查看文档：`docs/` 目录下的 Markdown 文件
3. 检查配置：`config/` 目录下的 JSON 配置文件

---

**部署完成后，访问 Web UI：http://你的服务器IP:80**
