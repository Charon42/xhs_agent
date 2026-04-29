import csv
import json
from pathlib import Path
from typing import Any


CSV_FIELDS = [
    "original_title",
    "original_content",
    "original_tags",
    "likes",
    "collects",
    "comments",
    "engagement_score",
    "analysis",
    "rewrite_strategy",
    "new_title",
    "new_content",
    "new_tags",
    "image_prompts",
    "posting_advice",
    "quality_result",
]


def to_cell(value: Any) -> str:
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return "" if value is None else str(value)


def export_results_to_csv(results: list[dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
        writer.writeheader()

        for item in results:
            note = item["original_note"]
            creation = item["creation"]
            row = {
                "original_title": note.get("title"),
                "original_content": note.get("content"),
                "original_tags": note.get("tags"),
                "likes": note.get("likes"),
                "collects": note.get("collects"),
                "comments": note.get("comments"),
                "engagement_score": note.get("engagement_score"),
                "analysis": item.get("analysis"),
                "rewrite_strategy": item.get("rewrite_strategy"),
                "new_title": creation.get("new_title"),
                "new_content": creation.get("new_content"),
                "new_tags": creation.get("new_tags"),
                "image_prompts": creation.get("image_prompts"),
                "posting_advice": creation.get("posting_advice"),
                "quality_result": item.get("quality_check"),
            }
            writer.writerow({key: to_cell(value) for key, value in row.items()})
