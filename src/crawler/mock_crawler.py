import json
from pathlib import Path

from config import DATA_DIR


class MockCrawler:
    """Load local sample notes so the full pipeline can run without login."""

    def __init__(self, data_path: Path | None = None) -> None:
        self.data_path = data_path or DATA_DIR / "mock_notes.json"

    def fetch_notes(self, limit: int = 5) -> list[dict]:
        if not self.data_path.exists():
            raise FileNotFoundError(f"Mock data file not found: {self.data_path}")

        notes = json.loads(self.data_path.read_text(encoding="utf-8"))
        return notes[:limit]
