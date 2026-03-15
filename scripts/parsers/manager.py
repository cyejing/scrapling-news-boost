from .base import ContentParser, ParseResult
from .trafilatura_parser import TrafilaturaParser
from .scrapling_parser import ScraplingParser
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logger import get_logger

logger = get_logger(__name__)


class ParserManager:
    def __init__(self):
        self._trafilatura = TrafilaturaParser()
        self._scrapling = ScraplingParser()

    def parse(self, html: str, parser: str = "auto") -> ParseResult:
        if parser == "trafilatura":
            return self._trafilatura.parse(html)
        
        if parser == "scrapling":
            return self._scrapling.parse(html)
        
        if parser == "auto":
            result = self._trafilatura.parse(html)
            
            if result.success:
                return result
            
            logger.info(f"[Parse] Trafilatura failed, falling back to Scrapling parser")
            
            fallback_result = self._scrapling.parse(html)
            
            if fallback_result.success:
                return fallback_result
            
            return result
        
        logger.warning(f"Unknown parser: {parser}. Valid options: auto, trafilatura, scrapling")
        return ParseResult(
            title="",
            content="",
            parser_name="unknown",
            success=False,
            error=f"Unknown parser: {parser}. Valid options: auto, trafilatura, scrapling"
        )
