from processing.cleaning import clean_record, normalize_key, parse_price, parse_rating
from processing.deduplication import deduplicate
from processing.validation import validate_record


def test_normalize_key_handles_whitespace_and_case():
    assert normalize_key("  Example   BOOK  ") == "example book"


def test_parse_price():
    assert parse_price("£51.77") == 51.77


def test_parse_rating():
    assert parse_rating("star-rating Three") == 3


def test_clean_and_validate_record():
    record = clean_record({
        "source": " Books to Scrape ",
        "source_url": "https://books.toscrape.com/catalogue/example_1/index.html",
        "name_or_title": " Example Book ",
        "price": "£12.50",
        "rating": "Five",
    })
    result = validate_record(record)
    assert result.valid
    assert record["price"] == 12.50
    assert record["rating"] == 5


def test_invalid_record_is_rejected():
    result = validate_record({"source": None, "name_or_title": None, "source_url": None})
    assert not result.valid
    assert "missing_source" in result.errors


def test_deduplication_ignores_case_and_whitespace():
    records = [
        {"source": "Books to Scrape", "name_or_title": "Example Book", "author": None},
        {"source": "Books to Scrape", "name_or_title": " example   book ", "author": None},
    ]
    unique, duplicates = deduplicate(records)
    assert len(unique) == 1
    assert duplicates == 1
