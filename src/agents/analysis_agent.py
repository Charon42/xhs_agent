from typing import Any

from src.agents.base_agent import BaseAgent


class AnalysisAgent(BaseAgent):
    agent_name = "analysis_agent"

    def analyze(self, note: dict[str, Any]) -> dict[str, Any]:
        mock_response = {
            "title_hook": "标题用明确人群和具体收益制造点击动机。",
            "user_pain_point": "用户希望用低成本方法解决日常生活或成长中的具体问题。",
            "emotional_value": "提供被理解感、确定感和马上可执行的轻松感。",
            "content_structure": "先描述真实场景，再给出步骤清单，最后补充个人效果反馈。",
            "tag_strategy": "覆盖人群、场景、问题和解决方案标签，利于搜索和推荐匹配。",
            "viral_reason": "痛点具体、门槛低、结果清晰，适合收藏和转发。",
            "reusable_patterns": ["明确人群", "数字化清单", "真实经验背书", "低成本行动建议"],
        }
        return self.run_json(
            system_prompt=(
                "你是小红书内容运营分析 Agent。请分析爆款笔记的标题钩子、用户痛点、"
                "情绪价值、正文结构、标签策略、爆款原因和可复用写法。"
            ),
            user_payload={"note": note},
            mock_response=mock_response,
        )
