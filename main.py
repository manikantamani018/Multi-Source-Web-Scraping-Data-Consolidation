from __future__ import annotations

import csv
import json
import logging
import sys
import time
from collections import Counter
from pathlib import Path

from scrapers.books_scraper import BooksScraper
from scrapers.quotes_scraper import QuotesScraper
from processing.cleaning import clean_record
from processing.deduplication import deduplicate
from processing.validation import validate_record


ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "output"
LOG_DIR = ROOT / "logs"
CSV_PATH = OUTPUT_DIR / "final_dataset.csv"
SUMMARY_PATH = OUTPUT_DIR / "summary_report.json"
LOG_PATH = LOG_DIR / "scraper.log"

FIELDS = [
    "source", "source_url", "name_or_title", "category", "price", "rating",
    "author", "tags", "description", "scraped_at"
]


def configure_logging() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    LOG_DIR.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[logging.FileHandler(LOG_PATH, encoding="utf-8"), logging.StreamHandler(sys.stdout)],
        force=True,
    )


def write_csv(records: list[dict]) -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    with CSV_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows({field: record.get(field) for field in FIELDS} for record in records)


def write_summary(summary: dict) -> None:
    with SUMMARY_PATH.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, ensure_ascii=False)


def run() -> dict:
    configure_logging()
    logger = logging.getLogger("pipeline")
    start = time.perf_counter()

    scrapers = [BooksScraper(), QuotesScraper()]
    raw_records: list[dict] = []
    per_source = {}

    for scraper in scrapers:
        logger.info("Starting source: %s", scraper.SOURCE)
        records, metrics = scraper.scrape()
        raw_records.extend(records)
        per_source[scraper.SOURCE] = {
            "records_collected": len(records),
            **metrics,
        }
        logger.info("Finished source: %s records=%s", scraper.SOURCE, len(records))

    cleaned_records = [clean_record(record) for record in raw_records]
    valid_records: list[dict] = []
    rejected = []
    for record in cleaned_records:
        result = validate_record(record)
        if result.valid:
            valid_records.append(record)
        else:
            rejected.append({"record": record, "errors": result.errors})

    unique_records, duplicate_count = deduplicate(valid_records)

    counts_after_cleaning = Counter(record["source"] for record in valid_records)
    counts_final = Counter(record["source"] for record in unique_records)
    for source in per_source:
        per_source[source]["records_after_cleaning_validation"] = counts_after_cleaning[source]
        per_source[source]["final_records"] = counts_final[source]

    duration = round(time.perf_counter() - start, 3)
    summary = {
        "execution": {
            "duration_seconds": duration,
            "completed": True,
        },
        "sources": per_source,
        "totals": {
            "records_collected": len(raw_records),
            "records_after_cleaning_and_validation": len(valid_records),
            "records_rejected": len(rejected),
            "duplicate_records_removed": duplicate_count,
            "final_record_count": len(unique_records),
        },
        "rejection_reasons": dict(Counter(error for item in rejected for error in item["errors"])),
        "outputs": {
            "dataset": str(CSV_PATH.relative_to(ROOT)),
            "summary": str(SUMMARY_PATH.relative_to(ROOT)),
            "log": str(LOG_PATH.relative_to(ROOT)),
        },
    }

    write_csv(unique_records)
    write_summary(summary)
    logger.info("Pipeline complete: final_records=%s duration=%ss", len(unique_records), duration)
    return summary


if __name__ == "__main__":
    run()
