"""
测试飞书 API 更新记录
"""

from tools.feishu_bitable_tool import _feishu_client
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_update_record(record_id: str):
    """测试更新记录"""
    try:
        # 先获取当前记录
        logger.info(f"Getting current record: {record_id}")
        result = _feishu_client._request(
            "GET",
            f"/bitable/v1/apps/{_feishu_client.FEISHU_APP_TOKEN}/tables/{_feishu_client.FEISHU_TABLE_ID}/records/{record_id}"
        )
        
        current_fields = result.get("data", {}).get("fields", {})
        logger.info(f"Current fields: {current_fields}")
        
        # 获取信息内容
        current_info = current_fields.get("信息内容", "")
        if isinstance(current_info, list):
            current_info = current_info[0] if len(current_info) > 0 else ""
        
        logger.info(f"Current info content: {current_info}")
        
        # 构建新的信息内容
        import re
        current_info = re.sub(r'^【[^\n]+】\n', '', current_info)
        new_info = f"【已下单】\n{current_info}"
        
        logger.info(f"New info content: {new_info}")
        
        # 尝试更新记录（只更新信息内容字段）
        logger.info("Updating record...")
        update_result = _feishu_client._request(
            "PATCH",
            f"/bitable/v1/apps/{_feishu_client.FEISHU_APP_TOKEN}/tables/{_feishu_client.FEISHU_TABLE_ID}/records/{record_id}",
            json={"fields": {"信息内容": new_info}}
        )
        
        logger.info(f"Update result: {update_result}")
        return "Success"
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"Error: {e}"

if __name__ == "__main__":
    # 测试更新记录
    result = test_update_record("recv6WCt3IrUr7")
    print(result)
