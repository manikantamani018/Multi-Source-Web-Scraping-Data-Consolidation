# Multi-Source Web Scraping & Data Consolidation

## 1. Overview

This project implements the Python take-home assignment using two public practice sites:

- Books to Scrape: https://books.toscrape.com/
- Quotes to Scrape: https://quotes.toscrape.com/

The pipeline performs:

1. Source scraping
2. Automatic pagination
3. Data cleaning and standardization
4. Record validation
5. Duplicate detection/removal
6. Consolidation into one CSV
7. JSON summary generation
8. Logging and failure handling

Only publicly accessible pages are requested. The project does not bypass authentication, CAPTCHA, access controls, or security mechanisms.

## 2. Python Version

Python 3.10+ is recommended.

## 3. Project Structure

```text
scraping_assignment/
├── scrapers/
│   ├── __init__.py
│   ├── base.py
│   ├── books_scraper.py
│   └── quotes_scraper.py
├── processing/
│   ├── __init__.py
│   ├── cleaning.py
│   ├── validation.py
│   └── deduplication.py
├── output/
│   ├── final_dataset.csv
│   └── summary_report.json
├── logs/
│   └── scraper.log
├── tests/
│   ├── __init__.py
│   └── test_processing.py
├── main.py
├── requirements.txt
├── README.md
└── AI_USAGE.md
```

## 4. Installation

Create a virtual environment:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## 5. Run the Scraper

From the project root:

```bash
python main.py
```

The pipeline creates/updates:

- `output/final_dataset.csv`
- `output/summary_report.json`
- `logs/scraper.log`

## 6. Scraping Approach

### Books to Scrape

`BooksScraper` starts at the first catalogue page and follows the site's `li.next a` pagination link until there is no next page. Each product card is parsed independently. Missing selectors return `None` instead of crashing the complete run.

### Quotes to Scrape

`QuotesScraper` starts at the home page and follows the site's next-page link until pagination ends. Each quote block is parsed for quote text, author, tags, and source page URL.

Source-specific selectors are isolated inside their scraper modules.

## 7. Data Model

The standardized CSV schema is:

| Field | Purpose |
|---|---|
| source | Name of the source website |
| source_url | Original page/product URL captured by the scraper |
| name_or_title | Book title or quote text |
| category | Source category when available |
| price | Numeric price when available |
| rating | Integer 1-5 when available |
| author | Author when available |
| tags | Comma-separated tags when available |
| description | Availability/description text when available |
| scraped_at | UTC timestamp for collection |

Fields that do not apply to a source remain empty/`None`; no data is invented.

## 8. Cleaning and Standardization

The cleaning layer is separate from scraping and:

- trims and collapses whitespace;
- normalizes empty strings to `None`;
- converts prices such as `£51.77` to `51.77`;
- converts Books to Scrape rating words into integers 1-5;
- validates HTTP/HTTPS URLs;
- provides normalized text keys for duplicate detection.

## 9. Validation

A record is rejected when:

- source is missing;
- name/title is missing;
- source URL is missing or invalid;
- price exists but is not numeric;
- rating exists but is outside 1-5.

Rejection reasons are included in `summary_report.json`.

## 10. Duplicate Detection

Duplicate detection is performed after cleaning and validation.

The fingerprint is based on normalized:

- source;
- title/quote text;
- author.

Whitespace, capitalization, and punctuation differences are normalized before comparison. Including the source prevents unrelated records from separate websites from being considered duplicates merely because their text happens to match.

Duplicates are removed from the final dataset and the count is reported.

## 11. Error Handling and Logging

HTTP requests use:

- timeout handling;
- HTTP status checking;
- limited retries;
- increasing delay between retry attempts;
- logging for failed requests.

A failed individual page does not automatically stop the complete pipeline. The scraper attempts to continue pagination when the page number can be determined.

Missing HTML elements are handled safely and become null values.

## 12. Output

`final_dataset.csv` contains the consolidated, cleaned, validated, deduplicated records.

`summary_report.json` contains:

- records collected per source;
- pages attempted;
- failed pages;
- records after cleaning/validation;
- rejected records;
- duplicate records removed;
- final record count;
- rejection reasons;
- execution time;
- output locations.

## 13. Tests

Run:

```bash
pytest -q
```

The tests cover normalization, numeric conversion, rating conversion, validation, and duplicate detection.

## 14. Assumptions

- The supplied practice websites expose static HTML suitable for Requests + BeautifulSoup.
- The pagination links remain available in the HTML.
- A missing source-specific field is represented as null rather than guessed.
- Books are identified using source + normalized title; quotes are identified using source + normalized quote text + author.
- The assignment does not require storing the full page HTML or images.

## 15. Known Limitations

- The Books listing page does not expose every detail field directly, so fields such as category are left empty rather than requiring an additional request per book.
- The scraper is intentionally polite and sequential; it is not optimized for high-volume production crawling.
- The summary records failures encountered during a run but does not persist checkpoints between executions.

## 16. AI Usage

See `AI_USAGE.md` for the required AI-assisted development disclosure.
