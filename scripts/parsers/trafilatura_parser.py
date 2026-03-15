from .base import ContentParser, ParseResult
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logger import get_logger

logger = get_logger(__name__)

try:
    import trafilatura
    TRAFILATURA_AVAILABLE = True
except ImportError:
    TRAFILATURA_AVAILABLE = False


class TrafilaturaParser(ContentParser):
    @property
    def name(self) -> str:
        return "trafilatura"

    def parse(self, html: str) -> ParseResult:
        if not html or not html.strip():
            return ParseResult(
                title="",
                content="",
                parser_name=self.name,
                success=False,
                error="Empty HTML content provided"
            )

        if not TRAFILATURA_AVAILABLE:
            return ParseResult(
                title="",
                content="",
                parser_name=self.name,
                success=False,
                error="trafilatura library not installed"
            )

        try:
            content = trafilatura.extract(
                html,
                output_format="markdown",
                include_comments=False,
                include_tables=True,
                no_fallback=False,
                favor_precision=True,
            )

            metadata = trafilatura.extract_metadata(html)

            title = ""
            if metadata:
                title = metadata.title or ""

            if not content:
                return ParseResult(
                    title=title,
                    content="",
                    parser_name=self.name,
                    success=False,
                    error="Trafilatura failed to extract content"
                )

            return ParseResult(
                title=title,
                content=content,
                parser_name=self.name,
                success=True
            )

        except Exception as e:
            logger.warning(f"Trafilatura extraction error: {e}")
            return ParseResult(
                title="",
                content="",
                parser_name=self.name,
                success=False,
                error=f"Trafilatura extraction error: {str(e)}"
            )
