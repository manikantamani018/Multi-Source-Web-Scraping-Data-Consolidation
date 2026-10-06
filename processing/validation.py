from __future__ import annotations

from dataclasses import dataclass

from .cleaning import normalize_key


@dataclass
class ValidationResult:
    valid: bool
    errors: list[str]


def validate_record(record: dict) -> ValidationResult:
    errors: list[str] = []

    if not normalize_key(record.get("source")):
        errors.append("missing_source")
    if not normalize_key(record.get("name_or_title")):
        errors.append("missing_name_or_title")
    if not record.get("source_url"):
        errors.append("invalid_source_url")

    price = record.get("price")
    if price is not None and not isinstance(price, (int, float)):
        errors.append("price_not_numeric")

    rating = record.get("rating")
    if rating is not None and rating not in {1, 2, 3, 4, 5}:
        errors.append("rating_out_of_range")

    return ValidationResult(valid=not errors, errors=errors)
