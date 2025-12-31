"""
Web UI 配置管理界面
提供可视化配置管理功能
"""

import os
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException, Form, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 配置文件路径
def get_config_path() -> str:
    """获取配置文件路径"""
    workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
    return os.path.join(workspace_path, "config/webhook_config.json")

# 加载配置
def load_config() -> Dict:
    """加载配置文件"""
    config_path = get_config_path()
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"Config file not found: {config_path}")
        return get_default_config()
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return get_default_config()

# 保存配置
def save_config(config: Dict) -> bool:
    """保存配置文件"""
    config_path = get_config_path()
    try:
        # 确保配置目录存在
        config_dir = os.path.dirname(config_path)
        if config_dir and not os.path.exists(config_dir):
            os.makedirs(config_dir)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        logger.info(f"Config saved to: {config_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to save config: {e}")
        return False

# 获取默认配置
def get_default_config() -> Dict:
    """获取默认配置"""
    return {
        "webhooks": [],
        "server": {
            "host": "0.0.0.0",
            "port": 8080,
            "workers": 1
        },
        "filter_rules": {
            "exclude_keywords": [],
            "trading_keywords": [],
            "exclude_patterns": []
        },
        "message_processing": {
            "enable_filter": True,
            "enable_agent_analysis": True,
            "auto_trade": False,
            "save_to_bitable": True,
            "log_all_messages": True
        }
    }

# 创建 FastAPI 应用
app = FastAPI(
    title="Webhook 配置管理系统",
    description="可视化配置管理界面",
    version="1.0.0"
)

# 获取项目根目录
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 配置静态文件和模板
templates_dir = os.path.join(project_root, "web", "templates")
static_dir = os.path.join(project_root, "web", "static")

# 确保目录存在
os.makedirs(templates_dir, exist_ok=True)
os.makedirs(static_dir, exist_ok=True)

# 挂载静态文件
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# 配置模板引擎
templates = Jinja2Templates(directory=templates_dir)

# ==================== 页面路由 ====================

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """仪表板页面"""
    config = load_config()
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "config": config,
            "page": "dashboard"
        }
    )

@app.get("/webhooks", response_class=HTMLResponse)
async def webhooks_page(request: Request):
    """Webhook 配置页面"""
    config = load_config()
    return templates.TemplateResponse(
        "webhooks.html",
        {
            "request": request,
            "config": config,
            "page": "webhooks"
        }
    )

@app.get("/server", response_class=HTMLResponse)
async def server_page(request: Request):
    """服务器配置页面"""
    config = load_config()
    return templates.TemplateResponse(
        "server.html",
        {
            "request": request,
            "config": config,
            "page": "server"
        }
    )

@app.get("/filters", response_class=HTMLResponse)
async def filters_page(request: Request):
    """过滤规则配置页面"""
    config = load_config()
    return templates.TemplateResponse(
        "filters.html",
        {
            "request": request,
            "config": config,
            "page": "filters"
        }
    )

@app.get("/processing", response_class=HTMLResponse)
async def processing_page(request: Request):
    """消息处理配置页面"""
    config = load_config()
    return templates.TemplateResponse(
        "processing.html",
        {
            "request": request,
            "config": config,
            "page": "processing"
        }
    )

# ==================== API 路由 ====================

@app.get("/api/config")
async def get_config_api():
    """获取完整配置（API）"""
    return load_config()

@app.post("/api/config")
async def save_config_api(config_data: Dict):
    """保存配置（API）"""
    try:
        # 验证配置结构
        if not isinstance(config_data, dict):
            raise HTTPException(status_code=400, detail="Invalid config format")
        
        if "webhooks" not in config_data:
            config_data["webhooks"] = []
        if "server" not in config_data:
            config_data["server"] = {"host": "0.0.0.0", "port": 8080, "workers": 1}
        if "filter_rules" not in config_data:
            config_data["filter_rules"] = {"exclude_keywords": [], "trading_keywords": [], "exclude_patterns": []}
        if "message_processing" not in config_data:
            config_data["message_processing"] = {"enable_filter": True, "enable_agent_analysis": True, "auto_trade": False, "save_to_bitable": True, "log_all_messages": True}
        
        success = save_config(config_data)
        if success:
            return {"success": True, "message": "配置保存成功"}
        else:
            raise HTTPException(status_code=500, detail="配置保存失败")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Webhook 管理 API
@app.post("/api/webhook")
async def add_webhook(webhook_data: Dict):
    """添加 Webhook"""
    try:
        config = load_config()
        
        required_fields = ["id", "name", "url_path", "source"]
        for field in required_fields:
            if field not in webhook_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # 检查 ID 是否重复
        if any(wh.get("id") == webhook_data["id"] for wh in config["webhooks"]):
            raise HTTPException(status_code=409, detail=f"Webhook ID {webhook_data['id']} already exists")
        
        # 设置默认值
        webhook_data.setdefault("enabled", True)
        webhook_data.setdefault("description", "")
        webhook_data.setdefault("verification_token", "")
        
        config["webhooks"].append(webhook_data)
        save_config(config)
        
        return {"success": True, "message": "Webhook 添加成功", "webhook": webhook_data}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/webhook/{webhook_id}")
async def update_webhook(webhook_id: str, webhook_data: Dict):
    """更新 Webhook"""
    try:
        config = load_config()
        
        # 查找并更新 webhook
        webhook = next((wh for wh in config["webhooks"] if wh.get("id") == webhook_id), None)
        if not webhook:
            raise HTTPException(status_code=404, detail=f"Webhook {webhook_id} not found")
        
        # 更新字段
        for key, value in webhook_data.items():
            if key != "id":  # 不允许修改 ID
                webhook[key] = value
        
        save_config(config)
        
        return {"success": True, "message": "Webhook 更新成功", "webhook": webhook}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/webhook/{webhook_id}")
async def delete_webhook(webhook_id: str):
    """删除 Webhook"""
    try:
        config = load_config()
        
        original_count = len(config["webhooks"])
        config["webhooks"] = [wh for wh in config["webhooks"] if wh.get("id") != webhook_id]
        
        if len(config["webhooks"]) == original_count:
            raise HTTPException(status_code=404, detail=f"Webhook {webhook_id} not found")
        
        save_config(config)
        
        return {"success": True, "message": "Webhook 删除成功"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/webhook/{webhook_id}/toggle")
async def toggle_webhook(webhook_id: str):
    """启用/禁用 Webhook"""
    try:
        config = load_config()
        
        webhook = next((wh for wh in config["webhooks"] if wh.get("id") == webhook_id), None)
        if not webhook:
            raise HTTPException(status_code=404, detail=f"Webhook {webhook_id} not found")
        
        # 切换启用状态
        webhook["enabled"] = not webhook.get("enabled", False)
        save_config(config)
        
        return {
            "success": True,
            "message": "Webhook 状态切换成功",
            "webhook_id": webhook_id,
            "enabled": webhook["enabled"]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 服务器配置 API
@app.post("/api/server")
async def update_server(server_data: Dict):
    """更新服务器配置"""
    try:
        config = load_config()
        
        # 更新服务器配置
        if "host" in server_data:
            config["server"]["host"] = server_data["host"]
        if "port" in server_data:
            config["server"]["port"] = int(server_data["port"])
        if "workers" in server_data:
            config["server"]["workers"] = int(server_data["workers"])
        
        save_config(config)
        
        return {"success": True, "message": "服务器配置更新成功", "server": config["server"]}
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid value: {str(e)}")
    except Exception as e:
        logger.error(f"Error updating server config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 过滤规则 API
@app.post("/api/filters")
async def update_filters(filters_data: Dict):
    """更新过滤规则"""
    try:
        config = load_config()
        
        # 更新过滤规则
        if "exclude_keywords" in filters_data:
            config["filter_rules"]["exclude_keywords"] = filters_data["exclude_keywords"]
        if "trading_keywords" in filters_data:
            config["filter_rules"]["trading_keywords"] = filters_data["trading_keywords"]
        if "exclude_patterns" in filters_data:
            config["filter_rules"]["exclude_patterns"] = filters_data["exclude_patterns"]
        
        save_config(config)
        
        return {"success": True, "message": "过滤规则更新成功", "filters": config["filter_rules"]}
    
    except Exception as e:
        logger.error(f"Error updating filters: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 消息处理配置 API
@app.post("/api/processing")
async def update_processing(processing_data: Dict):
    """更新消息处理配置"""
    try:
        config = load_config()
        
        # 更新消息处理配置
        for key in ["enable_filter", "enable_agent_analysis", "auto_trade", "save_to_bitable", "log_all_messages"]:
            if key in processing_data:
                config["message_processing"][key] = bool(processing_data[key])
        
        save_config(config)
        
        return {"success": True, "message": "消息处理配置更新成功", "processing": config["message_processing"]}
    
    except Exception as e:
        logger.error(f"Error updating processing config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 配置导入/导出 API
@app.get("/api/config/export")
async def export_config():
    """导出配置"""
    config = load_config()
    return JSONResponse(content=config)

@app.post("/api/config/import")
async def import_config(config_data: Dict):
    """导入配置"""
    try:
        # 验证配置
        if not isinstance(config_data, dict):
            raise HTTPException(status_code=400, detail="Invalid config format")
        
        # 保存配置
        success = save_config(config_data)
        if success:
            return {"success": True, "message": "配置导入成功"}
        else:
            raise HTTPException(status_code=500, detail="配置导入失败")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error importing config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def start_web_ui(host: str = "0.0.0.0", port: int = 5000):
    """启动 Web UI 服务器"""
    import uvicorn
    import argparse
    
    parser = argparse.ArgumentParser(description='Webhook Web UI 配置管理系统')
    parser.add_argument('--host', default=host, help='监听地址（默认: 0.0.0.0）')
    parser.add_argument('--port', type=int, default=port, help='监听端口（默认: 5000）')
    args = parser.parse_args()
    
    logger.info(f"Starting Web UI server on {args.host}:{args.port}")
    logger.info(f"Dashboard: http://{args.host}:{args.port}")
    logger.info(f"Static files: {static_dir}")
    logger.info(f"Templates: {templates_dir}")
    
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        log_level="info"
    )


if __name__ == "__main__":
    start_web_ui()
