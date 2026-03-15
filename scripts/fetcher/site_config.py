from dataclasses import dataclass
from typing import Optional
import fnmatch
from urllib.parse import urlparse


@dataclass
class SiteConfig:
    domain: str
    wait_for: Optional[str] = None
    content_selector: Optional[str] = None
    network_idle: bool = False


DEFAULT_CONFIG = SiteConfig(domain="*")

SITE_CONFIGS = [
    SiteConfig(
        domain="finance.sina.com.cn",
        content_selector="#artibody",
    ),
    SiteConfig(
        domain="*.toutiao.com",
        wait_for="article",
        network_idle=True,
    ),
    SiteConfig(
        domain="*.huanqiu.com",
        wait_for="textarea.article-content",
        content_selector="textarea.article-content",
    ),
    SiteConfig(
        domain="*.msn.cn",
        wait_for="article",
        network_idle=True,
    ),
]


def get_site_config(url: str) -> SiteConfig:
    host = urlparse(url).netloc
    for config in SITE_CONFIGS:
        if fnmatch.fnmatch(host, config.domain):
            return config
    return DEFAULT_CONFIG
