from dataclasses import dataclass
from typing import Optional
import fnmatch
import json
import os
from urllib.parse import urlparse


@dataclass
class SiteConfig:
    domain: str
    wait_for: Optional[str] = None
    content_selector: Optional[str] = None
    network_idle: bool = False
    solve_cloudflare: bool = False
    original_url: Optional[str] = None
    comment: Optional[str] = None


DEFAULT_CONFIG = SiteConfig(domain="*")


def _load_configs() -> list[SiteConfig]:
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "site_config.json")
    if not os.path.exists(config_path):
        return []
    
    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    return [
        SiteConfig(
            domain=item.get("domain", "*"),
            wait_for=item.get("wait_for"),
            content_selector=item.get("content_selector"),
            network_idle=item.get("network_idle", False),
            solve_cloudflare=item.get("solve_cloudflare", False),
            original_url=item.get("original_url"),
            comment=item.get("comment"),
        )
        for item in data
    ]


SITE_CONFIGS = _load_configs()


def get_site_config(url: str) -> SiteConfig:
    host = urlparse(url).netloc
    for config in SITE_CONFIGS:
        if fnmatch.fnmatch(host, config.domain):
            return config
    return DEFAULT_CONFIG
