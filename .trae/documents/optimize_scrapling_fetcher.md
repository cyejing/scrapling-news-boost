# Scrapling Fetcher 优化计划

## 背景

根据测试用例分析，当前抓取存在以下问题：

| 用例 | 域名 | 问题 | 根因 |
|------|------|------|------|
| 21 | toutiao.com | 只获取到 noscript 内容 | SPA 应用，JS 未执行 |
| 08 | huanqiu.com | 获取到 AdBlock 提示 | 文章在 textarea 中，需 JS 渲染 |

## 实现方案

### 1. 创建站点配置文件

**文件位置**: `scripts/fetcher/site_config.py`

```python
from dataclasses import dataclass
from typing import Optional
import fnmatch
from urllib.parse import urlparse


@dataclass
class SiteConfig:
    """站点抓取配置"""
    domain: str                              # 域名模式，支持通配符如 *.toutiao.com
    wait_for: Optional[str] = None           # 等待元素选择器
    content_selector: Optional[str] = None   # 内容选择器


# 默认配置
DEFAULT_CONFIG = SiteConfig(domain="*")

# 站点配置列表
SITE_CONFIGS = [
    # 今日头条 - SPA 应用，需等待 article 元素
    SiteConfig(
        domain="*.toutiao.com",
        wait_for="article",
    ),
    # 环球网 - 内容在 textarea 中，需要 HTML 解码
    SiteConfig(
        domain="*.huanqiu.com",
        wait_for="textarea.article-content",
        content_selector="textarea.article-content",
    ),
]


def get_site_config(url: str) -> SiteConfig:
    """根据 URL 获取匹配的站点配置，无匹配则返回默认配置"""
    host = urlparse(url).netloc
    for config in SITE_CONFIGS:
        if fnmatch.fnmatch(host, config.domain):
            return config
    return DEFAULT_CONFIG
```

### 2. 修改 ScraplingFetcher 类

**修改文件**: `scripts/fetcher/scrapling_fetcher.py`

主要改动：
1. 导入 `get_site_config`
2. `fetch()` 方法获取站点配置
3. `_fetch_with_stealthy()` 接收配置参数，使用 `wait_for` 和 `content_selector`
4. `_extract_html()` 方法简化处理

```python
def _fetch_with_stealthy(self, url: str, config: SiteConfig) -> FetchResult:
    from scrapling.fetchers import StealthyFetcher

    page = StealthyFetcher.fetch(
        url,
        headless=True,
        network_idle=True,              # 固定为 True
        disable_resources=False,        # 固定为 False
        hide_canvas=True,
        block_webrtc=True,
        google_search=True,
        solve_cloudflare=False,
        real_chrome=True,
        locale='zh-CN',
        timeout=30000,                  # 固定为 30s
        retries=2,
        retry_delay=2,
        adaptive=True,
        wait_for=config.wait_for,       # 使用配置
    )

    html = self._extract_html(page, config)
    return FetchResult(
        html=html,
        title=_extract_title_from_html(html),
        fetch_mode="stealth",
        success=True,
    )

def _extract_html(self, page, config: SiteConfig) -> str:
    """根据配置提取 HTML"""
    if config.content_selector:
        selector = page.css(config.content_selector)
        if selector:
            raw = selector[0].html_content
            # textarea 内容需要 HTML 解码
            if selector[0].tag == 'textarea':
                import html
                return html.unescape(raw)
            return raw
    return page.html_content
```

## 实现步骤

1. **创建** `scripts/fetcher/site_config.py`
2. **修改** `scripts/fetcher/scrapling_fetcher.py`
3. **测试** 用例 21 和 08

## 预期效果

| 用例 | 修改前 | 修改后 |
|------|--------|--------|
| 21 (toutiao.com) | 21 字符 | ~1300 字符 |
| 08 (huanqiu.com) | 101 字符 | ~4000 字符 |
