import json
from dataclasses import dataclass, asdict


@dataclass
class OutputResult:
    url: str
    title: str
    content: str
    content_length: int
    fetch_mode: str
    parser_name: str
    fetch_duration: float = 0.0
    parse_duration: float = 0.0
    total_duration: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)


class OutputFormatter:
    def to_json(self, result: OutputResult, indent: int | None = None) -> str:
        data = {
            'ok': True,
            'url': result.url,
            'title': result.title,
            'content_length': result.content_length,
            'fetch_mode': result.fetch_mode,
            'parser': result.parser_name,
            'fetch_duration': round(result.fetch_duration, 2),
            'parse_duration': round(result.parse_duration, 2),
            'total_duration': round(result.total_duration, 2),
            'content': result.content,
        }
        return json.dumps(data, ensure_ascii=False, indent=indent)

    def to_markdown(self, result: OutputResult) -> str:
        lines = [
            f'# {result.title}' if result.title else '# (无标题)',
            '',
            f'> URL: {result.url}',
            f'> 内容长度: {result.content_length} 字符',
            f'> 抓取模式: {result.fetch_mode}',
            f'> 解析器: {result.parser_name}',
            f'> 耗时: 抓取 {result.fetch_duration:.2f}s + 解析 {result.parse_duration:.2f}s = 总计 {result.total_duration:.2f}s',
            '',
            '---',
            '',
            result.content,
        ]
        return '\n'.join(lines)
