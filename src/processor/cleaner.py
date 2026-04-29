import re
from typing import Any


REQUIRED_FIELDS = ["title", "content", "tags", "likes", "collects", "comments", "url", "author", "published_at"]


def clean_text(value: Any) -> str:
    text = "" if value is None else str(value)
    return re.sub(r"\s+", " ", text).strip()


def clean_tags(tags: Any) -> list[str]:
    if isinstance(tags, str):
        raw_tags = re.split(r"[#,，,\s]+", tags)
    elif isinstance(tags, list):
        raw_tags = tags
    else:
        raw_tags = []

    result: list[str] = []
    for tag in raw_tags:
        cleaned = clean_text(tag).lstrip("#")
        if cleaned and cleaned not in result:
            result.append(cleaned)
    return result


def parse_count(value: Any) -> int:
    if value is None:
        return 0
    if isinstance(value, (int, float)):
        return int(value)

    text = clean_text(value).lower().replace(",", "")
    if not text:
        return 0

    multiplier = 1
    if text.endswith("w") or text.endswith("万"):
        multiplier = 10000
        text = text[:-1]
    elif text.endswith("k"):
        multiplier = 1000
        text = text[:-1]

    try:
        return int(float(text) * multiplier)
    except ValueError:
        digits = re.sub(r"[^\d]", "", text)
        return int(digits) if digits else 0


def calculate_engagement_score(likes: int, collects: int, comments: int) -> float:
    return round(likes * 1.0 + collects * 1.4 + comments * 2.0, 2)


def clean_note(note: dict[str, Any]) -> dict[str, Any] | None:
    normalized = {
        "title": clean_text(note.get("title")),
        "content": clean_text(note.get("content")),
        "tags": clean_tags(note.get("tags")),
        "likes": parse_count(note.get("likes")),
        "collects": parse_count(note.get("collects")),
        "comments": parse_count(note.get("comments")),
        "url": clean_text(note.get("url")),
        "author": clean_text(note.get("author")),
        "published_at": clean_text(note.get("published_at")),
    }
    if not normalized["title"] or not normalized["content"]:
        return None

    normalized["engagement_score"] = calculate_engagement_score(
        normalized["likes"], normalized["collects"], normalized["comments"]
    )
    return normalized


def clean_notes(notes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cleaned = []
    for note in notes:
        result = clean_note(note)
        if result:
            cleaned.append(result)
    return cleaned
