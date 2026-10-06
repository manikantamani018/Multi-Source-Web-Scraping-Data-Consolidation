from __future__ import annotations

import logging
import time
from typing import Optional

import requests


class BaseScraper:
    """Shared HTTP behavior for source-specific scrapers."""

    def __init__(self, timeout: int = 15, retries: int = 2, delay: float = 0.3):
        self.timeout = timeout
        self.retries = retries
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "scraping-assignment/1.0 (educational project)"
        })
        self.logger = logging.getLogger(self.__class__.__name__)

    def fetch(self, url: str) -> Optional[str]:
        for attempt in range(1, self.retries + 2):
            try:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                return response.text
            except requests.RequestException as exc:
                self.logger.warning(
                    "Request failed: url=%s attempt=%s error=%s", url, attempt, exc
                )
                if attempt <= self.retries:
                    time.sleep(self.delay * attempt)
        return None
