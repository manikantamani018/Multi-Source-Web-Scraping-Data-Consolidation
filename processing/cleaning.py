from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse


RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
    "1": 1,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
}


def clean_text(value: Any) -> str | None:
    if value is None:
        return None
    value = re.sub(r"\s+", " ", str(value)).strip()
    return value or None


def normalize_key(value: Any) -> str:
    text = clean_text(value) or ""
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def parse_price(value: Any) -> float | None:
    if value is None:
        return None
    match = re.search(r"-?\d+(?:\.\d+)?", str(value).replace(",", ""))
    return float(match.group()) if match else None


def parse_rating(value: Any) -> int | None:
    if value is None:
        return None
    text = clean_text(value)
    if not text:
        return None
    for key, number in RATING_MAP.items():
        if re.search(rf"\b{re.escape(key)}\b", text, re.IGNORECASE):
            return number
    return None


def clean_url(value: Any) -> str | None:
    text = clean_text(value)
    if not text:
        return None
    parsed = urlparse(text)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None
    return text


def clean_record(record: dict) -> dict:
    cleaned = dict(record)
    for field in ("source", "name_or_title", "category", "author", "tags", "description"):
        cleaned[field] = clean_text(cleaned.get(field))
    cleaned["source_url"] = clean_url(cleaned.get("source_url"))
    cleaned["price"] = parse_price(cleaned.get("price"))
    cleaned["rating"] = parse_rating(cleaned.get("rating"))
    return cleaned
