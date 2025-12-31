"""
数据分析 Agent
功能：分析历史交易数据，生成报告
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
from collections import Counter

logger = logging.getLogger(__name__)


class DataAnalysisAgent:
    """数据分析 Agent"""

    def __init__(self, storage_agent):
        """
        初始化数据分析 Agent

        Args:
            storage_agent: 数据存储 Agent 实例
        """
        self.storage_agent = storage_agent

    def extract_numeric_value(self, value: str) -> float:
        """从字符串中提取数值"""
        import re

        if not value:
            return 0.0

        # 尝试提取数字
        match = re.search(r'([0-9,.]+)', str(value))
        if match:
            try:
                # 移除逗号
                num_str = match.group(1).replace(',', '')
                return float(num_str)
            except:
                return 0.0
        return 0.0

    def analyze_directions(self, records: List[Dict]) -> Dict[str, Any]:
        """分析开仓方向分布"""
        directions = []
        for record in records:
            fields = record.get("fields", {})
            direction = fields.get("开仓方向")
            if direction:
                directions.append(direction)

        direction_counts = Counter(directions)

        return {
            "total": len(directions),
            "distribution": dict(direction_counts),
            "most_common": direction_counts.most_common(1)[0] if direction_counts else None
        }

    def analyze_strategies(self, records: List[Dict]) -> Dict[str, Any]:
        """分析策略关键词"""
        strategies = []
        for record in records:
            fields = record.get("fields", {})
            keywords = fields.get("策略关键词")
            if keywords:
                # 分割关键词
                if isinstance(keywords, str):
                    strategy_list = [k.strip() for k in keywords.split(',')]
                    strategies.extend(strategy_list)

        strategy_counts = Counter(strategies)

        return {
            "total": len(strategies),
            "distribution": dict(strategy_counts),
            "top_strategies": strategy_counts.most_common(5) if strategy_counts else []
        }

    def analyze_amounts(self, records: List[Dict]) -> Dict[str, Any]:
        """分析入场金额"""
        amounts = []
        for record in records:
            fields = record.get("fields", {})
            amount = fields.get("入场金额")
            if amount:
                numeric_value = self.extract_numeric_value(amount)
                if numeric_value > 0:
                    amounts.append(numeric_value)

        if not amounts:
            return {
                "total": 0,
                "average": 0,
                "max": 0,
                "min": 0
            }

        return {
            "total": len(amounts),
            "average": sum(amounts) / len(amounts),
            "max": max(amounts),
            "min": min(amounts),
            "total_amount": sum(amounts)
        }

    def analyze_time_distribution(self, records: List[Dict]) -> Dict[str, Any]:
        """分析时间分布"""
        time_data = []

        for record in records:
            fields = record.get("fields", {})
            timestamp = fields.get("解析时间") or fields.get("创建时间")

            if timestamp:
                try:
                    # 尝试解析时间
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    time_data.append(dt)
                except:
                    continue

        if not time_data:
            return {
                "by_hour": {},
                "by_day": {},
                "latest": None,
                "oldest": None
            }

        # 按小时分布
        hour_counts = Counter([dt.hour for dt in time_data])

        # 按星期分布
        day_counts = Counter([dt.strftime('%A') for dt in time_data])

        return {
            "by_hour": dict(hour_counts),
            "by_day": dict(day_counts),
            "latest": max(time_data).isoformat() if time_data else None,
            "oldest": min(time_data).isoformat() if time_data else None
        }

    def generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """基于分析生成建议"""
        recommendations = []

        # 基于方向分布
        direction_analysis = analysis.get("direction_analysis", {})
        if direction_analysis.get("most_common"):
            most_common = direction_analysis["most_common"][0]
            recommendations.append(f"最常见的交易方向是: {most_common}")

        # 基于金额分析
        amount_analysis = analysis.get("amount_analysis", {})
        if amount_analysis.get("total", 0) > 0:
            avg_amount = amount_analysis.get("average", 0)
            recommendations.append(f"平均入场金额: {avg_amount:.2f} U")

            max_amount = amount_analysis.get("max", 0)
            min_amount = amount_analysis.get("min", 0)
            recommendations.append(f"入场金额范围: {min_amount:.2f} - {max_amount:.2f} U")

        # 基于策略分析
        strategy_analysis = analysis.get("strategy_analysis", {})
        top_strategies = strategy_analysis.get("top_strategies", [])
        if top_strategies:
            recommendations.append(f"最热门的策略: {top_strategies[0][0]} (出现 {top_strategies[0][1]} 次)")

        return recommendations

    def analyze(self, analysis_type: str = "daily") -> Dict[str, Any]:
        """
        执行数据分析

        Args:
            analysis_type: 分析类型 (daily, weekly, monthly, all)

        Returns:
            分析结果
        """
        try:
            logger.info(f"开始执行 {analysis_type} 数据分析")

            # 获取订单记录
            result = self.storage_agent.get_recent_orders(limit=1000)

            if not result.get("success"):
                return {
                    "success": False,
                    "error": result.get("error")
                }

            records = result.get("records", [])

            if not records:
                return {
                    "success": True,
                    "message": "暂无数据可分析",
                    "analysis_result": None
                }

            logger.info(f"获取到 {len(records)} 条记录")

            # 执行各项分析
            direction_analysis = self.analyze_directions(records)
            strategy_analysis = self.analyze_strategies(records)
            amount_analysis = self.analyze_amounts(records)
            time_analysis = self.analyze_time_distribution(records)

            # 生成建议
            analysis_data = {
                "direction_analysis": direction_analysis,
                "strategy_analysis": strategy_analysis,
                "amount_analysis": amount_analysis,
                "time_analysis": time_analysis
            }

            recommendations = self.generate_recommendations(analysis_data)

            # 构建返回结果
            analysis_result = {
                "analysis_type": analysis_type,
                "total_orders": len(records),
                "direction_analysis": direction_analysis,
                "strategy_analysis": strategy_analysis,
                "amount_analysis": amount_analysis,
                "time_analysis": time_analysis,
                "recommendations": recommendations,
                "generated_at": datetime.now().isoformat()
            }

            logger.info("数据分析完成")
            logger.info(f"总订单数: {analysis_result['total_orders']}")
            logger.info(f"建议: {recommendations}")

            return {
                "success": True,
                "analysis_result": analysis_result
            }

        except Exception as e:
            logger.error(f"数据分析时出错: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    def generate_report(self, analysis_type: str = "daily") -> str:
        """
        生成分析报告文本

        Args:
            analysis_type: 分析类型

        Returns:
            报告文本
        """
        result = self.analyze(analysis_type)

        if not result.get("success"):
            return f"分析失败: {result.get('error')}"

        analysis = result.get("analysis_result")

        if not analysis:
            return "暂无数据可分析"

        # 构建报告文本
        report_lines = [
            "=" * 60,
            f"交易数据分析报告 ({analysis_type.upper()})",
            "=" * 60,
            "",
            f"生成时间: {analysis.get('generated_at')}",
            f"总订单数: {analysis.get('total_orders')}",
            "",
            "--- 方向分析 ---",
        ]

        direction = analysis.get("direction_analysis", {})
        report_lines.append(f"总交易数: {direction.get('total')}")
        if direction.get("most_common"):
            report_lines.append(f"最常见的方向: {direction['most_common'][0]} ({direction['most_common'][1]} 次)")

        report_lines.extend(["", "--- 策略分析 ---"])

        strategy = analysis.get("strategy_analysis", {})
        top_strategies = strategy.get("top_strategies", [])
        if top_strategies:
            report_lines.append("热门策略:")
            for i, (name, count) in enumerate(top_strategies[:5], 1):
                report_lines.append(f"  {i}. {name} ({count} 次)")

        report_lines.extend(["", "--- 金额分析 ---"])

        amount = analysis.get("amount_analysis", {})
        if amount.get("total", 0) > 0:
            report_lines.append(f"平均入场金额: {amount.get('average', 0):.2f} U")
            report_lines.append(f"金额范围: {amount.get('min', 0):.2f} - {amount.get('max', 0):.2f} U")
            report_lines.append(f"总投入金额: {amount.get('total_amount', 0):.2f} U")

        report_lines.extend(["", "--- 建议 ---"])

        recommendations = analysis.get("recommendations", [])
        for rec in recommendations:
            report_lines.append(f"• {rec}")

        report_lines.extend(["", "=" * 60])

        return "\n".join(report_lines)


def build_data_analysis_agent(storage_agent):
    """
    构建数据分析 Agent

    Args:
        storage_agent: 数据存储 Agent 实例

    Returns:
        DataAnalysisAgent 实例
    """
    return DataAnalysisAgent(storage_agent)
