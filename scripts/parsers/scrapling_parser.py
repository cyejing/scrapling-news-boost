from .base import ContentParser, ParseResult
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logger import get_logger

logger = get_logger(__name__)

try:
    from scrapling.parser import Selector
    SCRAPLING_AVAILABLE = True
except ImportError:
    SCRAPLING_AVAILABLE = False


class ScraplingParser(ContentParser):
    @property
    def name(self) -> str:
        return "scrapling"

    def parse(self, html: str) -> ParseResult:
        if not html or not html.strip():
            return ParseResult(
                title="",
                content="",
                parser_name=self.name,
                success=False,
                error="Empty HTML content provided"
            )

        if not SCRAPLING_AVAILABLE:
            return ParseResult(
                title="",
                content="",
                parser_name=self.name,
                success=False,
                error="scrapling library not installed"
            )

        try:
            page = Selector(html)
            
            title = ""
            title_elem = page.css("title::text")
            if title_elem:
                title = title_elem.get() or ""
            
            content = page.get_all_text()
            
            if not content:
                return ParseResult(
                    title=title.strip(),
                    content="",
                    parser_name=self.name,
                    success=False,
                    error="Scrapling parser failed to extract content"
                )

            return ParseResult(
                title=title.strip(),
                content=content.strip(),
                parser_name=self.name,
                success=True
            )
            
        except Exception as e:
            logger.warning(f"Scrapling parser extraction error: {e}")
            return ParseResult(
                title="",
                content="",
                parser_name=self.name,
                success=False,
                error=f"Scrapling parser extraction error: {str(e)}"
            )
