# 服务器配置文档

## 系统环境

### 已安装组件
- Python 3.12.3
- 虚拟环境：/opt/webhook-system-env
- Nginx 1.24.0
- FastAPI 0.121.2
- Uvicorn 0.38.0

### 项目路径
- 项目目录：/workspace/projects
- 配置目录：/workspace/projects/config
- 日志目录：/var/log/

## 服务配置

### Web UI 服务
- **端口**：5000
- **监听地址**：0.0.0.0（所有网卡）
- **启动命令**：
  ```bash
  nohup /opt/webhook-system-env/bin/python /workspace/projects/src/web_ui.py > /var/log/webhook-system.log 2>&1 &
  ```

### Nginx 反向代理
- **监听端口**：80
- **配置文件**：/etc/nginx/sites-available/webhook-system
- **代理目标**：http://127.0.0.1:5000
- **重启命令**：
  ```bash
  nginx -s reload  # 重新加载配置
  nginx -s stop    # 停止服务
  nginx            # 启动服务
  ```

## 服务管理

### 使用管理脚本
```bash
# 查看服务状态
./scripts/manage.sh status

# 启动所有服务
./scripts/manage.sh start

# 停止所有服务
./scripts/manage.sh stop

# 重启所有服务
./scripts/manage.sh restart

# 查看日志
./scripts/manage.sh logs
```

### 手动管理

#### 启动 Web UI
```bash
cd /workspace/projects
/opt/webhook-system-env/bin/python src/web_ui.py
```

#### 后台运行 Web UI
```bash
nohup /opt/webhook-system-env/bin/python /workspace/projects/src/web_ui.py > /var/log/webhook-system.log 2>&1 &
```

#### 停止 Web UI
```bash
lsof -ti:5000 | xargs kill -9
```

#### 启动 Nginx
```bash
nginx
```

#### 停止 Nginx
```bash
pkill nginx
```

#### 重新加载 Nginx 配置
```bash
nginx -s reload
```

## 访问地址

### 本地访问
- 直接访问：http://localhost:5000
- 通过 Nginx：http://localhost:80

### 外部访问
```
http://43.128.70.173:80
```

**重要提示**：
- 需要在腾讯云控制台配置安全组，开放 80 端口
- 安全组配置路径：控制台 → 云服务器 → 安全组 → 入站规则 → 添加规则
- 规则配置：TCP:80，来源：0.0.0.0/0（或指定 IP）

## 日志文件

### Web UI 日志
- **位置**：/var/log/webhook-system.log
- **错误日志**：/var/log/webhook-system-error.log
- **查看最新日志**：
  ```bash
  tail -f /var/log/webhook-system.log
  ```

### Nginx 日志
- **访问日志**：/var/log/nginx/access.log
- **错误日志**：/var/log/nginx/error.log
- **查看最新日志**：
  ```bash
  tail -f /var/log/nginx/access.log
  tail -f /var/log/nginx/error.log
  ```

## 系统配置文件

### Webhook 配置
```bash
cat /workspace/projects/config/webhook_config.json
```

### LLM 配置
```bash
cat /workspace/projects/config/agent_llm_config.json
```

### Nginx 配置
```bash
cat /etc/nginx/sites-available/webhook-system
```

## 故障排查

### 端口被占用
```bash
# 查看端口占用
lsof -i:5000
lsof -i:80

# 强制停止占用进程
lsof -ti:5000 | xargs kill -9
```

### 服务无法启动
```bash
# 查看日志
tail -100 /var/log/webhook-system.log

# 检查配置文件
python3 src/web_ui.py --help
```

### Nginx 配置错误
```bash
# 测试配置
nginx -t

# 查看错误日志
tail -100 /var/log/nginx/error.log
```

## 性能优化

### 调整 Nginx worker 进程数
编辑 `/etc/nginx/nginx.conf`：
```nginx
worker_processes auto;
worker_connections 1024;
```

### 启用 Gzip 压缩
在 `/etc/nginx/sites-available/webhook-system` 中添加：
```nginx
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css application/json application/javascript;
```

## 安全建议

1. **配置防火墙**：使用 UFW 或 iptables 限制访问
2. **使用 HTTPS**：配置 SSL/TLS 证书（Let's Encrypt）
3. **添加认证**：配置 Nginx 基础认证或 JWT 认证
4. **限制访问来源**：在腾讯云安全组中指定允许访问的 IP

## 监控和告警

### 检查服务健康状态
```bash
# 检查 Web UI
curl http://localhost:5000

# 检查 Nginx
curl http://localhost:80

# 查看进程
ps aux | grep "python.*web_ui.py"
ps aux | grep nginx
```

### 自动化监控脚本
```bash
# 创建监控脚本
cat > /workspace/scripts/monitor.sh << 'EOF'
#!/bin/bash
# 检查 Web UI
if ! lsof -i:5000 > /dev/null 2>&1; then
    echo "Web UI 服务未运行，正在启动..."
    ./scripts/manage.sh start
fi

# 检查 Nginx
if ! pgrep nginx > /dev/null; then
    echo "Nginx 服务未运行，正在启动..."
    nginx
fi
EOF

chmod +x /workspace/scripts/monitor.sh

# 添加到 crontab（每分钟检查一次）
crontab -e
# 添加：* * * * * /workspace/scripts/monitor.sh
```
