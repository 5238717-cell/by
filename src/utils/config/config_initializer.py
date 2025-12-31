"""
配置初始化工具
支持交互式输入配置，生成 webhook 配置文件
"""

import os
import json
from typing import Dict, List, Optional
from datetime import datetime


class ConfigInitializer:
    """配置初始化器"""
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = {
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
    
    def print_header(self, title: str):
        """打印标题"""
        print("\n" + "=" * 60)
        print(f"  {title}")
        print("=" * 60)
    
    def print_section(self, section: str):
        """打印章节"""
        print(f"\n【{section}】")
        print("-" * 60)
    
    def input_boolean(self, prompt: str, default: bool = True) -> bool:
        """输入布尔值"""
        default_str = "Y/n" if default else "y/N"
        while True:
            user_input = input(f"{prompt} [{default_str}]: ").strip().lower()
            if not user_input:
                return default
            if user_input in ['y', 'yes', '是', '1']:
                return True
            elif user_input in ['n', 'no', '否', '0']:
                return False
            print("请输入 Y 或 N")
    
    def input_string(self, prompt: str, default: str = "", required: bool = False) -> str:
        """输入字符串"""
        while True:
            default_display = f"[{default}]" if default else ""
            user_input = input(f"{prompt} {default_display}: ").strip()
            if not user_input:
                user_input = default
            if required and not user_input:
                print("此项为必填项，请重新输入")
                continue
            return user_input
    
    def input_int(self, prompt: str, default: int, min_val: int = None, max_val: int = None) -> int:
        """输入整数"""
        while True:
            default_display = f"[{default}]"
            user_input = input(f"{prompt} {default_display}: ").strip()
            if not user_input:
                return default
            
            try:
                value = int(user_input)
                if min_val is not None and value < min_val:
                    print(f"最小值为 {min_val}")
                    continue
                if max_val is not None and value > max_val:
                    print(f"最大值为 {max_val}")
                    continue
                return value
            except ValueError:
                print("请输入有效的整数")
    
    def input_list(self, prompt: str, default_items: List[str] = None) -> List[str]:
        """输入列表（逗号分隔）"""
        default_str = ", ".join(default_items) if default_items else ""
        default_display = f"[{default_str}]" if default_str else ""
        user_input = input(f"{prompt} {default_display}: ").strip()
        
        if not user_input:
            return default_items or []
        
        # 分割并清理空格
        items = [item.strip() for item in user_input.split(",")]
        # 过滤空字符串
        return [item for item in items if item]
    
    def configure_webhook(self) -> Dict:
        """配置单个 webhook"""
        self.print_section("配置 Webhook 端点")
        
        webhook = {
            "id": self.input_string("Webhook ID (如: webhook_001)", "webhook_001", required=True),
            "name": self.input_string("Webhook 名称", "飞书交易信号Webhook", required=True),
            "url_path": self.input_string("URL 路径 (如: /webhook/trading)", "/webhook/trading", required=True),
            "enabled": self.input_boolean("是否启用", True),
            "description": self.input_string("描述", "接收飞书群交易信号消息"),
            "source": self.input_string("消息来源 (如: feishu/telegram)", "feishu"),
            "verification_token": self.input_string("验证令牌 (可选)", "")
        }
        
        return webhook
    
    def configure_webhooks(self) -> List[Dict]:
        """配置多个 webhook"""
        self.print_section("Webhook 配置")
        
        webhooks = []
        while True:
            webhook = self.configure_webhook()
            webhooks.append(webhook)
            
            if not self.input_boolean("\n是否继续添加 Webhook", False):
                break
        
        return webhooks
    
    def configure_server(self) -> Dict:
        """配置服务器"""
        self.print_section("服务器配置")
        
        server = {
            "host": self.input_string("监听地址", "0.0.0.0"),
            "port": self.input_int("监听端口", 8080, min_val=1, max_val=65535),
            "workers": self.input_int("工作进程数", 1, min_val=1, max_val=10)
        }
        
        return server
    
    def configure_filter_rules(self) -> Dict:
        """配置过滤规则"""
        self.print_section("消息过滤规则")
        
        print("\n📋 过除关键词：包含这些关键词的消息将被过滤（营销、广告等）")
        exclude_keywords = self.input_list("排除关键词（逗号分隔）", [
            "广告", "营销", "推广", "免费", "扫码", "加群",
            "关注", "点赞", "转发", "分享", "福利", "优惠券",
            "折扣", "限时优惠", "领取", "报名", "注册", "开户"
        ])
        
        print("\n📋 交易关键词：包含至少2个这些关键词的消息将被识别为交易消息")
        trading_keywords = self.input_list("交易关键词（逗号分隔）", [
            "开仓", "平仓", "做多", "做空", "买入", "卖出",
            "long", "short", "buy", "sell", "入场", "离场",
            "止盈", "止损", "补仓", "加仓", "下单", "成交"
        ])
        
        print("\n📋 排除模式：匹配这些模式的消息将被过滤（分析、免责声明等）")
        exclude_patterns = self.input_list("排除模式（逗号分隔）", [
            "趋势分析", "市场分析", "技术分析", "基本面分析",
            "投资建议", "风险提示", "免责声明", "仅供参考"
        ])
        
        return {
            "exclude_keywords": exclude_keywords,
            "trading_keywords": trading_keywords,
            "exclude_patterns": exclude_patterns
        }
    
    def configure_message_processing(self) -> Dict:
        """配置消息处理"""
        self.print_section("消息处理配置")
        
        processing = {
            "enable_filter": self.input_boolean("启用消息过滤", True),
            "enable_agent_analysis": self.input_boolean("启用 Agent 分析", True),
            "auto_trade": self.input_boolean("自动交易 (⚠️  慎用)", False),
            "save_to_bitable": self.input_boolean("保存到飞书多维表格", True),
            "log_all_messages": self.input_boolean("记录所有消息日志", True)
        }
        
        return processing
    
    def show_config_summary(self):
        """显示配置摘要"""
        self.print_section("配置摘要")
        
        print("\n📌 Webhook 端点:")
        for wh in self.config["webhooks"]:
            status = "✅" if wh["enabled"] else "❌"
            print(f"  {status} {wh['name']} ({wh['id']})")
            print(f"     路径: {wh['url_path']}")
            print(f"     来源: {wh['source']}")
        
        print(f"\n📌 服务器:")
        print(f"  地址: {self.config['server']['host']}:{self.config['server']['port']}")
        print(f"  工作进程: {self.config['server']['workers']}")
        
        print(f"\n📌 过滤规则:")
        print(f"  排除关键词: {len(self.config['filter_rules']['exclude_keywords'])} 个")
        print(f"  交易关键词: {len(self.config['filter_rules']['trading_keywords'])} 个")
        print(f"  排除模式: {len(self.config['filter_rules']['exclude_patterns'])} 个")
        
        print(f"\n📌 消息处理:")
        print(f"  消息过滤: {'✅' if self.config['message_processing']['enable_filter'] else '❌'}")
        print(f"  Agent 分析: {'✅' if self.config['message_processing']['enable_agent_analysis'] else '❌'}")
        print(f"  自动交易: {'✅' if self.config['message_processing']['auto_trade'] else '❌'}")
        print(f"  保存到表格: {'✅' if self.config['message_processing']['save_to_bitable'] else '❌'}")
        print(f"  记录日志: {'✅' if self.config['message_processing']['log_all_messages'] else '❌'}")
    
    def save_config(self) -> bool:
        """保存配置"""
        try:
            # 确保配置目录存在
            config_dir = os.path.dirname(self.config_path)
            if config_dir and not os.path.exists(config_dir):
                os.makedirs(config_dir)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            
            print(f"\n✅ 配置已保存到: {self.config_path}")
            return True
        except Exception as e:
            print(f"\n❌ 保存配置失败: {e}")
            return False
    
    def run(self):
        """运行配置向导"""
        self.print_header("Webhook 配置向导")
        print("\n欢迎使用 Webhook 配置向导！")
        print("本向导将帮助您配置交易信号接收系统。")
        print("\n📌 您可以按 Enter 使用默认值（括号中显示）\n")
        
        # 配置各个部分
        self.config["webhooks"] = self.configure_webhooks()
        self.config["server"] = self.configure_server()
        self.config["filter_rules"] = self.configure_filter_rules()
        self.config["message_processing"] = self.configure_message_processing()
        
        # 显示摘要
        self.show_config_summary()
        
        # 确认保存
        if self.input_boolean("\n是否保存配置", True):
            if self.save_config():
                self.print_header("配置完成")
                print("\n配置已完成！您现在可以启动 Webhook 服务器了。")
                print("\n启动命令:")
                print("  python src/webhook_server.py")
                print("\n或者使用后台模式:")
                print("  nohup python src/webhook_server.py > logs/webhook.log 2>&1 &")
            else:
                print("\n配置保存失败，请重试。")
        else:
            print("\n配置已取消。")


def check_first_run(config_path: str) -> bool:
    """检查是否为首次运行"""
    # 检查配置文件是否存在
    if not os.path.exists(config_path):
        return True
    
    # 检查配置文件是否为空或格式错误
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if not content.strip():
                return True
            
            data = json.loads(content)
            # 检查是否包含必要的配置项
            if "webhooks" not in data or "server" not in data:
                return True
    except:
        return True
    
    return False


def run_config_wizard(config_path: str = None):
    """运行配置向导"""
    if config_path is None:
        workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
        config_path = os.path.join(workspace_path, "config/webhook_config.json")
    
    print(f"\n🔍 检查配置文件: {config_path}")
    
    if check_first_run(config_path):
        print("✨ 检测到首次运行或配置文件无效，启动配置向导...\n")
        initializer = ConfigInitializer(config_path)
        initializer.run()
        return True
    else:
        print("✅ 配置文件已存在，跳过配置向导。")
        print(f"   如需重新配置，请删除配置文件后重启: {config_path}")
        return False


if __name__ == "__main__":
    # 直接运行配置向导
    run_config_wizard()
