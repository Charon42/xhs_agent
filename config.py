from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parent
DATA_DIR = ROOT_DIR / "data"
DEFAULT_OUTPUT_DIR = ROOT_DIR / "outputs"
AUTH_DIR = ROOT_DIR / "auth"
DEFAULT_STORAGE_STATE = AUTH_DIR / "xhs_storage_state.json"


@dataclass(frozen=True)
class Settings:
    openai_api_key: str
    openai_base_url: str
    openai_model: str
    mock_llm: bool


def load_settings(force_mock_llm: bool = False) -> Settings:
    load_dotenv(ROOT_DIR / ".env")
    api_key = os.getenv("OPENAI_API_KEY", "").strip() or os.getenv("DOUBAO_API_KEY", "").strip()
    base_url = (
        os.getenv("OPENAI_BASE_URL", "").strip()
        or os.getenv("DOUBAO_BASE_URL", "").strip()
        or "https://api.openai.com/v1"
    )
    model = (
        os.getenv("OPENAI_MODEL", "").strip()
        or os.getenv("DOUBAO_MODEL", "").strip()
        or "gpt-4o-mini"
    )
    return Settings(
        openai_api_key=api_key,
        openai_base_url=base_url,
        openai_model=model,
        mock_llm=force_mock_llm or not bool(api_key),
    )
