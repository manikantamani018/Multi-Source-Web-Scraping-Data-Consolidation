from __future__ import annotations

from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .base import BaseScraper


class QuotesScraper(BaseScraper):
    BASE_URL = "https://quotes.toscrape.com/"
    START_URL = BASE_URL
    SOURCE = "Quotes to Scrape"

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
                    self.logger.error(
                        "Stopping after %s consecutive page failures",
                        consecutive_failures,
                    )
                    break

                url = self._next_url_from_failed_page(url)
                continue

            consecutive_failures = 0

            soup = BeautifulSoup(html, "html.parser")
            scraped_at = datetime.now(timezone.utc).isoformat()

            for block in soup.select("div.quote"):
                record = self._parse_quote(
                    block,
                    url,
                    scraped_at,
                )
                records.append(record)

            next_link = soup.select_one("li.next a")

            if next_link:
                href = next_link.get("href")

                if isinstance(href, str):
                    url = urljoin(url, href)
                else:
                    url = None
            else:
                url = None

        return records, {
            "pages_attempted": pages,
            "failed_pages": failed_pages,
        }

    def _parse_quote(
        self,
        block,
        page_url: str,
        scraped_at: str,
    ) -> dict:

        text_node = block.select_one("span.text")
        author_node = block.select_one("small.author")
        tag_nodes = block.select("a.tag")

        quote_text = (
            text_node.get_text(" ", strip=True)
            if text_node
            else None
        )

        author = (
            author_node.get_text(" ", strip=True)
            if author_node
            else None
        )

        tags = None

        if tag_nodes:
            tags = ", ".join(
                tag.get_text(" ", strip=True)
                for tag in tag_nodes
            )

        return {
            "source": self.SOURCE,
            "source_url": page_url,
            "name_or_title": quote_text,
            "category": None,
            "price": None,
            "rating": None,
            "author": author,
            "tags": tags,
            "description": None,
            "scraped_at": scraped_at,
        }

    @staticmethod
    def _next_url_from_failed_page(url: str) -> str | None:

        base_url = QuotesScraper.BASE_URL.rstrip("/")
        current_url = url.rstrip("/")

        if current_url == base_url:
            return urljoin(
                QuotesScraper.BASE_URL,
                "page/2/",
            )

        parts = current_url.split("/")

        if parts and parts[-1].isdigit():
            next_page = int(parts[-1]) + 1

            if next_page <= 10:
                return urljoin(
                    QuotesScraper.BASE_URL,
                    f"page/{next_page}/",
                )

        return None