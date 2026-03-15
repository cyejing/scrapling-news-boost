import re
import urllib.request
from dataclasses import dataclass
from urllib.parse import urlparse
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logger import get_logger

logger = get_logger(__name__)


@dataclass
class FetchResult:
    html: str
    final_url: str
    title: str
    fetch_mode: str
    success: bool = True
    error: str = ""


def _extract_title_from_html(html: str) -> str:
    match = re.search(r"<title[^>]*>([^<]+)</title>", html, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return ""


class ScraplingFetcher:
    def __init__(self):
        self._stealthy_fetcher = None
        self._fetcher = None

    def _fetch_with_stealthy(self, url: str) -> FetchResult:
        from scrapling.fetchers import StealthyFetcher

        page = StealthyFetcher.fetch(
            url,
            headless=True,
            network_idle=False,
            disable_resources=True,
            hide_canvas=True,
            block_webrtc=True,
            google_search=True,
            solve_cloudflare=False,
            real_chrome=True,
            locale='zh-CN',
            timeout=15000,
            retries=2,
            retry_delay=2,
            adaptive=True,
        )
        html = page.html_content
        return FetchResult(
            html=html,
            final_url=page.url,
            title=_extract_title_from_html(html),
            fetch_mode="stealth",
            success=True,
        )

    def _fetch_with_fetcher(self, url: str) -> FetchResult:
        from scrapling.fetchers import Fetcher

        fetcher = Fetcher()
        page = fetcher.get(
            url,
            stealthy_headers=True,
            adaptive=True,
            timeout=15,
        )
        html = page.html_content
        return FetchResult(
            html=html,
            final_url=page.url,
            title=_extract_title_from_html(html),
            fetch_mode="fetcher",
            success=True,
        )

    def _fetch_with_urllib(self, url: str) -> FetchResult:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            },
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            html = r.read().decode("utf-8", errors="replace")
        return FetchResult(
            html=html,
            final_url=url,
            title=_extract_title_from_html(html),
            fetch_mode="urllib",
            success=True,
        )

    def fetch(self, url: str) -> FetchResult:
        parts = urlparse(url)
        if parts.scheme not in ("http", "https"):
            return FetchResult(
                html="",
                final_url=url,
                title="",
                fetch_mode="",
                success=False,
                error="url must start with http:// or https://",
            )

        try:
            return self._fetch_with_stealthy(url)
        except ImportError as e:
            logger.warning(f"scrapling not installed, falling back to urllib. {e}")
        except Exception as e:
            logger.warning(f"StealthyFetcher failed ({e}), trying Fetcher")

        try:
            return self._fetch_with_fetcher(url)
        except ImportError:
            pass
        except Exception as e:
            logger.warning(f"Fetcher failed ({e}), falling back to urllib")

        try:
            return self._fetch_with_urllib(url)
        except Exception as e:
            logger.error(f"All fetch methods failed: {e}")
            return FetchResult(
                html="",
                final_url=url,
                title="",
                fetch_mode="",
                success=False,
                error=f"all fetch methods failed: {e}",
            )
