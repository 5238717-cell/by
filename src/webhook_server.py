"""
Webhook服务器
用于接收外部系统的交易消息，过滤后交给Agent处理
"""

import os
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
import uvicorn
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import asyncio
from utils.config.config_initializer import run_config_wizard

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 加载配置
def load_config() -> Dict:
    """加载webhook配置文件"""
    workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
    config_path = os.path.join(workspace_path, "config/webhook_config.json")
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load webhook config: {e}")
        return {
            "webhooks": [],
            "server": {"host": "0.0.0.0", "port": 8080},
            "filter_rules": {},
            "message_processing": {}
        }

# 保存配置
def save_config(config: Dict) -> bool:
    """保存webhook配置文件"""
    workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
    config_path = os.path.join(workspace_path, "config/webhook_config.json")
    
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"Failed to save webhook config: {e}")
        return False

# 全局配置
config = load_config()

# 创建FastAPI应用
app = FastAPI(
    title="交易信号Webhook服务",
    description="接收并处理交易消息，过滤非交易信息，提取开仓/平仓信号",
    version="1.0.0"
)

# 消息模型
from pydantic import ConfigDict

class WebhookMessage(BaseModel):
    """Webhook消息模型"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "webhook_id": "webhook_001",
            "timestamp": "2024-01-01T12:00:00",
            "source": "feishu",
            "content": "BTC现货交易，做多，入场价格90000，止盈92000，止损88000",
            "group_name": "交易信号群",
            "user_info": {"user_id": "user_001", "username": "trader"},
            "metadata": {"msg_id": "msg_123"}
        }
    })
    
    webhook_id: str = Field(..., description="Webhook ID")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="消息时间戳")
    source: str = Field(..., description="消息来源（如：feishu、telegram）")
    content: str = Field(..., description="消息内容")
    group_name: str = Field(default="未知群", description="群组/频道名称")
    user_info: Optional[Dict] = Field(default=None, description="发送者信息")
    metadata: Optional[Dict] = Field(default=None, description="额外元数据")

# 消息处理器
class MessageProcessor:
    """消息处理器"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.filter_rules = config.get("filter_rules", {})
        self.processing_config = config.get("message_processing", {})
        
    def is_trading_message(self, content: str) -> tuple[bool, str]:
        """
        判断是否为交易消息
        
        Returns:
            (is_trading, reason): 是否为交易消息及原因
        """
        content_lower = content.lower()
        
        # 检查排除关键词（营销、广告等）
        exclude_keywords = self.filter_rules.get("exclude_keywords", [])
        for keyword in exclude_keywords:
            if keyword.lower() in content_lower:
                logger.info(f"Message filtered by exclude keyword: {keyword}")
                return False, f"包含排除关键词：{keyword}"
        
        # 检查排除模式（趋势分析、免责声明等）
        exclude_patterns = self.filter_rules.get("exclude_patterns", [])
        for pattern in exclude_patterns:
            if pattern.lower() in content_lower:
                logger.info(f"Message filtered by exclude pattern: {pattern}")
                return False, f"匹配排除模式：{pattern}"
        
        # 检查交易关键词
        trading_keywords = self.filter_rules.get("trading_keywords", [])
        keyword_count = sum(1 for kw in trading_keywords if kw.lower() in content_lower)
        
        # 至少包含2个交易关键词才认为是交易消息
        if keyword_count >= 2:
            logger.info(f"Message identified as trading signal (keyword count: {keyword_count})")
            return True, f"包含{keyword_count}个交易关键词"
        
        return False, "交易关键词不足"
    
    def filter_message(self, message: WebhookMessage) -> Dict:
        """
        过滤消息，判断是否需要处理
        
        Returns:
            {
                "should_process": bool,  # 是否需要处理
                "reason": str,  # 原因
                "message_type": str  # 消息类型（trading/analysis/spam）
            }
        """
        if not self.processing_config.get("enable_filter", True):
            # 如果未启用过滤，默认处理所有消息
            return {
                "should_process": True,
                "reason": "过滤功能未启用",
                "message_type": "unknown"
            }
        
        is_trading, reason = self.is_trading_message(message.content)
        
        if is_trading:
            return {
                "should_process": True,
                "reason": reason,
                "message_type": "trading"
            }
        else:
            # 判断是否为分析类消息
            analysis_keywords = ["分析", "趋势", "行情", "观点", "建议"]
            if any(kw in message.content for kw in analysis_keywords):
                return {
                    "should_process": False,
                    "reason": reason,
                    "message_type": "analysis"
                }
            
            return {
                "should_process": False,
                "reason": reason,
                "message_type": "spam"
            }
    
    def log_message(self, message: WebhookMessage, filter_result: Dict):
        """记录消息日志"""
        if not self.processing_config.get("log_all_messages", True):
            return
        
        log_entry = {
            "timestamp": message.timestamp,
            "webhook_id": message.webhook_id,
            "source": message.source,
            "group_name": message.group_name,
            "content": message.content[:200] + "..." if len(message.content) > 200 else message.content,
            "should_process": filter_result["should_process"],
            "message_type": filter_result["message_type"],
            "reason": filter_result["reason"]
        }
        
        logger.info(f"Message logged: {json.dumps(log_entry, ensure_ascii=False)}")

# 全局消息处理器
message_processor = MessageProcessor(config)

# Agent处理器（延迟导入，避免循环依赖）
async def process_with_agent(message: WebhookMessage) -> Dict:
    """
    使用Agent处理交易消息
    
    Args:
        message: webhook消息
    
    Returns:
        Agent处理结果
    """
    try:
        # 延迟导入，避免循环依赖
        from agents.agent import build_agent
        
        # 构建Agent输入
        agent_input = f"""
收到来自 {message.source} 的交易消息：

群名：{message.group_name}
消息内容：
{message.content}

请分析这条消息，识别交易信号（开仓/平仓/补仓/离场），并执行相应操作。
"""
        
        # 构建Agent
        agent = build_agent()
        
        # 调用Agent
        result = await agent.ainvoke({
            "messages": [{"role": "user", "content": agent_input}]
        })
        
        return {
            "success": True,
            "agent_response": result,
            "processed_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error processing message with agent: {e}")
        return {
            "success": False,
            "error": str(e),
            "processed_at": datetime.now().isoformat()
        }

# API路由

@app.get("/")
async def root():
    """根路径"""
    return {
        "service": "Trading Signal Webhook Service",
        "version": "1.0.0",
        "status": "running",
        "webhooks_count": len(config.get("webhooks", []))
    }

@app.get("/webhooks")
async def list_webhooks():
    """列出所有webhook配置"""
    webhooks = config.get("webhooks", [])
    # 只返回基本信息，不包含敏感信息
    return {
        "webhooks": [
            {
                "id": wh.get("id"),
                "name": wh.get("name"),
                "url_path": wh.get("url_path"),
                "enabled": wh.get("enabled"),
                "description": wh.get("description"),
                "source": wh.get("source")
            }
            for wh in webhooks
        ]
    }

@app.post("/webhook/{webhook_id}")
async def receive_webhook(
    webhook_id: str,
    message: WebhookMessage,
    background_tasks: BackgroundTasks
):
    """
    接收webhook消息
    
    Args:
        webhook_id: webhook ID
        message: webhook消息
        background_tasks: 后台任务
    """
    logger.info(f"Received webhook message from {webhook_id}")
    
    # 验证webhook是否启用
    webhooks = config.get("webhooks", [])
    webhook_config = next((wh for wh in webhooks if wh.get("id") == webhook_id), None)
    
    if not webhook_config:
        logger.warning(f"Webhook {webhook_id} not found")
        return JSONResponse(
            status_code=404,
            content={"error": "Webhook not found", "webhook_id": webhook_id}
        )
    
    if not webhook_config.get("enabled", False):
        logger.warning(f"Webhook {webhook_id} is disabled")
        return JSONResponse(
            status_code=403,
            content={"error": "Webhook is disabled", "webhook_id": webhook_id}
        )
    
    # 过滤消息
    filter_result = message_processor.filter_message(message)
    message_processor.log_message(message, filter_result)
    
    if not filter_result["should_process"]:
        logger.info(f"Message filtered: {filter_result['reason']}")
        return {
            "status": "filtered",
            "webhook_id": webhook_id,
            "message_id": message.timestamp,
            "filter_result": filter_result,
            "processed_at": datetime.now().isoformat()
        }
    
    # 如果需要Agent分析，在后台处理
    if config.get("message_processing", {}).get("enable_agent_analysis", True):
        background_tasks.add_task(process_with_agent, message)
        return {
            "status": "processing",
            "webhook_id": webhook_id,
            "message_id": message.timestamp,
            "message_type": filter_result.get("message_type"),
            "processed_at": datetime.now().isoformat(),
            "note": "Message is being processed by agent in background"
        }
    
    # 不使用Agent分析，直接返回
    return {
        "status": "received",
        "webhook_id": webhook_id,
        "message_id": message.timestamp,
        "message_type": filter_result.get("message_type"),
        "processed_at": datetime.now().isoformat()
    }

@app.post("/admin/webhook")
async def add_webhook(webhook_data: Dict):
    """
    添加新的webhook配置
    
    Args:
        webhook_data: webhook配置数据
    """
    required_fields = ["id", "name", "url_path", "source"]
    for field in required_fields:
        if field not in webhook_data:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required field: {field}"
            )
    
    # 检查ID是否重复
    webhooks = config.get("webhooks", [])
    if any(wh.get("id") == webhook_data["id"] for wh in webhooks):
        raise HTTPException(
            status_code=409,
            detail=f"Webhook ID {webhook_data['id']} already exists"
        )
    
    # 设置默认值
    webhook_data.setdefault("enabled", True)
    webhook_data.setdefault("description", "")
    webhook_data.setdefault("verification_token", "")
    
    # 添加到配置
    config["webhooks"].append(webhook_data)
    save_config(config)
    
    logger.info(f"Added new webhook: {webhook_data['id']}")
    
    return {
        "status": "success",
        "webhook": webhook_data
    }

@app.delete("/admin/webhook/{webhook_id}")
async def delete_webhook(webhook_id: str):
    """
    删除webhook配置
    
    Args:
        webhook_id: webhook ID
    """
    webhooks = config.get("webhooks", [])
    original_count = len(webhooks)
    
    # 过滤掉要删除的webhook
    config["webhooks"] = [wh for wh in webhooks if wh.get("id") != webhook_id]
    
    if len(config["webhooks"]) == original_count:
        raise HTTPException(
            status_code=404,
            detail=f"Webhook {webhook_id} not found"
        )
    
    save_config(config)
    
    logger.info(f"Deleted webhook: {webhook_id}")
    
    return {
        "status": "success",
        "webhook_id": webhook_id
    }

@app.post("/admin/webhook/{webhook_id}/toggle")
async def toggle_webhook(webhook_id: str):
    """
    启用/禁用webhook
    
    Args:
        webhook_id: webhook ID
    """
    webhooks = config.get("webhooks", [])
    webhook = next((wh for wh in webhooks if wh.get("id") == webhook_id), None)
    
    if not webhook:
        raise HTTPException(
            status_code=404,
            detail=f"Webhook {webhook_id} not found"
        )
    
    # 切换启用状态
    webhook["enabled"] = not webhook.get("enabled", False)
    save_config(config)
    
    logger.info(f"Toggled webhook {webhook_id} to {webhook['enabled']}")
    
    return {
        "status": "success",
        "webhook_id": webhook_id,
        "enabled": webhook["enabled"]
    }

@app.get("/config")
async def get_config():
    """获取当前配置（不包含敏感信息）"""
    safe_config = {
        "server": config.get("server"),
        "webhooks": [
            {
                "id": wh.get("id"),
                "name": wh.get("name"),
                "url_path": wh.get("url_path"),
                "enabled": wh.get("enabled"),
                "description": wh.get("description"),
                "source": wh.get("source")
            }
            for wh in config.get("webhooks", [])
        ],
        "filter_rules": config.get("filter_rules"),
        "message_processing": config.get("message_processing")
    }
    return safe_config

# 启动服务器
def start_server():
    """启动webhook服务器"""
    server_config = config.get("server", {})
    host = server_config.get("host", "0.0.0.0")
    port = server_config.get("port", 8080)
    
    logger.info(f"Starting webhook server on {host}:{port}")
    logger.info(f"Registered webhooks: {len(config.get('webhooks', []))}")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )

if __name__ == "__main__":
    # 首次运行检查：如果配置文件不存在或无效，运行配置向导
    workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
    config_path = os.path.join(workspace_path, "config/webhook_config.json")
    
    print("\n" + "=" * 60)
    print("  交易信号 Webhook 服务")
    print("=" * 60)
    
    # 运行配置向导（如果需要）
    run_config_wizard(config_path)
    
    # 重新加载配置（如果配置向导创建了新配置）
    global config
    config = load_config()
    
    print("\n" + "=" * 60)
    print("\n🚀 启动 Webhook 服务器...\n")
    
    start_server()
