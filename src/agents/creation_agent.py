from typing import Any

from src.agents.base_agent import BaseAgent


class CreationAgent(BaseAgent):
    agent_name = "creation_agent"

    def create_content(
        self,
        note: dict[str, Any],
        analysis: dict[str, Any],
        rewrite_strategy: dict[str, Any],
    ) -> dict[str, Any]:
        first_tag = note.get("tags", ["生活"])[0]
        mock_response = {
            "new_title": f"打工人也能照做的{first_tag}小方法，亲测更省心",
            "new_content": (
                "以前我总觉得改变状态需要很复杂的计划，后来发现真正能坚持下来的，"
                "反而是那些马上能做的小动作。\n\n"
                "我的做法是：\n"
                "1. 先找到最影响状态的一个场景，不要一次改太多；\n"
                "2. 把方法拆成 10 分钟内能完成的动作；\n"
                "3. 连续记录 3 天，看它是不是真的适合自己；\n"
                "4. 有效果再固定下来，没效果就换一个更轻的方法。\n\n"
                "这套思路最适合忙的时候用，不追求完美，但能让生活慢慢回到可控状态。"
            ),
            "new_tags": ["打工人", first_tag, "生活效率", "自我提升", "经验分享"],
            "image_prompts": [
                "干净明亮的手机备忘录风格清单图，展示 4 个可执行步骤",
                "年轻职场人在通勤或办公间隙整理生活计划，真实自然的小红书风格照片",
            ],
            "posting_advice": "建议在工作日早上 7:30-9:00 或晚上 20:00-22:00 发布，标题突出人群和即时收益。",
        }
        return self.run_json(
            system_prompt="你是小红书内容创作 Agent。请生成新的标题、正文、标签、图片提示词和发布建议。",
            user_payload={
                "original_note": note,
                "analysis": analysis,
                "rewrite_strategy": rewrite_strategy,
            },
            mock_response=mock_response,
        )
