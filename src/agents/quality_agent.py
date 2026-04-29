from typing import Any


class QualityAgent:
    def check(self, creation: dict[str, Any]) -> dict[str, Any]:
        title = str(creation.get("new_title", "")).strip()
        content = str(creation.get("new_content", "")).strip()
        tags = creation.get("new_tags", [])
        suggestions: list[str] = []

        if not title:
            suggestions.append("缺少新标题。")
        if len(title) < 8:
            suggestions.append("标题过短，建议补充目标人群或具体收益。")
        if len(title) > 32:
            suggestions.append("标题偏长，建议压缩到 32 字以内。")
        if len(content) < 80:
            suggestions.append("正文过短，建议补充场景、步骤和个人体验。")
        if not any(word in content for word in ["我", "亲测", "发现", "建议", "适合"]):
            suggestions.append("正文缺少小红书常见的个人经验语气。")
        if not isinstance(tags, list) or not 3 <= len(tags) <= 8:
            suggestions.append("标签数量建议控制在 3-8 个。")
        if not creation.get("image_prompts"):
            suggestions.append("缺少图片提示词。")
        if not creation.get("posting_advice"):
            suggestions.append("缺少发布建议。")

        return {
            "passed": len(suggestions) == 0,
            "suggestions": suggestions,
            "checks": {
                "title_length": len(title),
                "content_length": len(content),
                "tag_count": len(tags) if isinstance(tags, list) else 0,
            },
        }
