from __future__ import annotations

from .cleaning import normalize_key


def duplicate_key(record: dict) -> tuple[str, ...]:
    """Build a stable semantic key after normalization.

    Books: source + title. Quotes: source + quote text + author.
    Including source prevents unrelated records from different sites from
    becoming duplicates merely because they share a title/name.
    """
    source = normalize_key(record.get("source"))
    title = normalize_key(record.get("name_or_title"))
    author = normalize_key(record.get("author"))
    return (source, title, author)


def deduplicate(records: list[dict]) -> tuple[list[dict], int]:
    seen: set[tuple[str, ...]] = set()
    unique: list[dict] = []
    duplicates = 0
    for record in records:
        key = duplicate_key(record)
        if key in seen:
            duplicates += 1
            continue
        seen.add(key)
        unique.append(record)
    return unique, duplicates
