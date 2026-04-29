import json
from typing import Any

from openai import OpenAI

from config import Settings
from src.utils.logger import get_logger


logger = get_logger(__name__)


class BaseAgent:
    agent_name = "base_agent"

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = None
        if not settings.mock_llm:
            self.client = OpenAI(
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url,
                timeout=20,
                max_retries=0,
            )

    def run_json(self, system_prompt: str, user_payload: dict[str, Any], mock_response: dict[str, Any]) -> dict[str, Any]:
        if self.settings.mock_llm:
            return mock_response

        try:
            response = self.client.chat.completions.create(
                model=self.settings.openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": "请只返回合法 JSON，不要 Markdown。\n\n" + json.dumps(user_payload, ensure_ascii=False),
                    },
                ],
                temperature=0.7,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content or "{}"
            return json.loads(content)
        except Exception as exc:
            logger.warning("%s LLM call failed, fallback to mock response: %s", self.agent_name, exc)
            return mock_response
