from typing import Any

from src.agents.base_agent import BaseAgent


class RewriteAgent(BaseAgent):
    agent_name = "rewrite_agent"

    def create_strategy(self, note: dict[str, Any], analysis: dict[str, Any]) -> dict[str, Any]:
        mock_response = {
            "target_audience": "希望提升效率和生活质量的年轻职场人。",
            "content_angle": "从原笔记的经验清单切入，改成更适合日常复用的行动方案。",
            "title_directions": ["明确人群 + 结果", "避坑提醒 + 清单", "真实场景 + 快速改善"],
            "body_structure": ["共鸣场景", "3-5 个具体方法", "执行注意事项", "个人化总结"],
            "differentiation": "加入更细的执行时机和适用边界，避免简单搬运原内容。",
        }
        return self.run_json(
            system_prompt="你是内容改写策略 Agent。请基于爆款分析生成对标改写思路，避免复刻原文。",
            user_payload={"original_note": note, "analysis": analysis},
            mock_response=mock_response,
        )
