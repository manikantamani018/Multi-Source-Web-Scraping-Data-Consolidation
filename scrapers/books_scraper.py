from __future__ import annotations

from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .base import BaseScraper


class BooksScraper(BaseScraper):
    BASE_URL = "https://books.toscrape.com/"
    START_URL = BASE_URL + "catalogue/page-1.html"
    SOURCE = "Books to Scrape"

    def scrape(self) -> tuple[list[dict], dict]:
        records: list[dict] = []
        pages = 0
        failed_pages = 0
        consecutive_failures = 0
        url = self.START_URL

        while url:
            pages += 1
            html = self.fetch(url)
            if html is None:
                failed_pages += 1
                consecutive_failures += 1
                if consecutive_failures >= 3:
                    self.logger.error("Stopping after %s consecutive page failures", consecutive_failures)
                    break
                url = self._next_url_from_failed_page(url)
                if url is None:
                    break
                continue

            consecutive_failures = 0

            soup = BeautifulSoup(html, "html.parser")
            scraped_at = datetime.now(timezone.utc).isoformat()
            for card in soup.select("article.product_pod"):
                records.append(self._parse_book(card, url, scraped_at))

            next_link = soup.select_one("li.next a")
            url = urljoin(url, next_link["href"]) if next_link and next_link.get("href") else None

        return records, {"pages_attempted": pages, "failed_pages": failed_pages}

    def _parse_book(self, card, page_url: str, scraped_at: str) -> dict:
        title_node = card.select_one("h3 a")
        price_node = card.select_one(".price_color")
        availability_node = card.select_one(".availability")
        rating_node = card.select_one("p.star-rating")
        category = None
        book_url = urljoin(page_url, title_node["href"]) if title_node and title_node.get("href") else None

        return {
            "source": self.SOURCE,
            "source_url": book_url or page_url,
            "name_or_title": title_node.get("title", "").strip() if title_node else None,
            "category": category,
            "price": price_node.get_text(" ", strip=True) if price_node else None,
            "rating": " ".join(rating_node.get("class", [])[1:]) if rating_node else None,
            "author": None,
            "tags": None,
            "description": availability_node.get_text(" ", strip=True) if availability_node else None,
            "scraped_at": scraped_at,
        }

    @staticmethod
    def _next_url_from_failed_page(url: str) -> str | None:
        # If a page fails, continue to the next numeric catalogue page.
        if "page-" not in url:
            return None
        prefix, rest = url.rsplit("page-", 1)
        number = rest.split(".", 1)[0]
        if not number.isdigit():
            return None
        next_number = int(number) + 1
        if next_number > 50:
            return None
        return f"{prefix}page-{next_number}.html"
