#!/usr/bin/env python3
"""
Web content fetcher with Trafilatura parser and Scrapling parser fallback.

Usage:
  uv run scrapling_fetch.py <url> [max_chars] [--json] [--parser PARSER]

Examples:
  uv run scrapling_fetch.py "https://example.com"
  uv run scrapling_fetch.py "https://example.com" 15000
  uv run scrapling_fetch.py "https://example.com" 10000 --json
  uv run scrapling_fetch.py "https://example.com" 10000 --parser scrapling
"""

import argparse
import sys
import time
from pathlib import Path

from fetcher import ScraplingFetcher
from parsers import ParserManager
from format import OutputFormatter, OutputResult
from logger import get_logger

logger = get_logger(__name__)


def main():
    arg_parser = argparse.ArgumentParser(
        description="Fetch and parse web content with Trafilatura and Scrapling parser fallback"
    )
    arg_parser.add_argument("url", help="URL to fetch")
    arg_parser.add_argument(
        "max_chars",
        nargs="?",
        type=int,
        default=10000,
        help="Max characters (default: 10000)",
    )
    arg_parser.add_argument("--json", action="store_true", help="Output as JSON")
    arg_parser.add_argument(
        "--parser",
        choices=["auto", "trafilatura", "scrapling"],
        default="auto",
        help="Parser to use: auto (default, Trafilatura with Scrapling fallback), trafilatura, scrapling",
    )
    arg_parser.add_argument(
        "--output",
        help="Output file path for JSON result (only works with --json)",
    )

    args = arg_parser.parse_args()

    fetcher = ScraplingFetcher()
    
    fetch_start = time.time()
    fetch_result = fetcher.fetch(args.url)
    fetch_duration = time.time() - fetch_start

    if not fetch_result.success:
        logger.error(f"[Fetch] {fetch_result.error} (took {fetch_duration:.2f}s)")
        sys.exit(1)

    logger.info(f"[Fetch] success with mode={fetch_result.fetch_mode}, html_length={len(fetch_result.html)}, took={fetch_duration:.2f}s")

    parser_manager = ParserManager()
    
    parse_start = time.time()
    parse_result = parser_manager.parse(fetch_result.html, args.parser)
    parse_duration = time.time() - parse_start

    if not parse_result.success:
        logger.error(f"[Parse] {parse_result.error} (took {parse_duration:.2f}s)")
        sys.exit(1)

    logger.info(f"[Parse] success with parser={parse_result.parser_name}, content_length={len(parse_result.content)}, took={parse_duration:.2f}s")

    content = parse_result.content[: args.max_chars]

    total_duration = fetch_duration + parse_duration

    result = OutputResult(
        url=args.url,
        title=parse_result.title or fetch_result.title,
        content=content,
        content_length=len(content),
        fetch_mode=fetch_result.fetch_mode,
        parser_name=parse_result.parser_name,
        fetch_duration=fetch_duration,
        parse_duration=parse_duration,
        total_duration=total_duration,
    )

    formatter = OutputFormatter()
    if args.json:
        json_output = formatter.to_json(result)
        if args.output:
            Path(args.output).write_text(json_output, encoding="utf-8")
        else:
            print(json_output)
    else:
        print(formatter.to_markdown(result))


if __name__ == "__main__":
    main()
