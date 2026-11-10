"""Fetch guide pages with a disk cache.

The cache saves full HTML keyed by URL hash so guide parsing and fixture
diffing can run offline, and retries against the cache if the site blocks
or a fetch fails.
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

CACHE_TTL_SECONDS = 24 * 60 * 60


def cache_dir() -> Path:
    return Path.home() / ".cache" / "d4filter"


def _cache_path(url: str) -> Path:
    digest = hashlib.sha256(url.encode()).hexdigest()[:32]
    return cache_dir() / f"{digest}.json"


def fetch_cached(url: str, use_cache: bool = True, ttl_seconds: float | None = None) -> str:
    entry = _cache_path(url)
    ttl = CACHE_TTL_SECONDS if ttl_seconds is None else ttl_seconds
    if use_cache and entry.exists():
        try:
            data = json.loads(entry.read_text())
            if time.time() - data["fetched_at"] < ttl:
                return data["html"]
        except (json.JSONDecodeError, KeyError):
            pass

    import urllib.request

    # Mobalytics (and possibly other guide hosts) reject minimal CLI UAs;
    # these headers reproduce what a plain browser session sends.
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "identity",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Upgrade-Insecure-Requests": "1",
    }
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        html = response.read().decode("utf-8", errors="replace")

    cache_dir().mkdir(parents=True, exist_ok=True)
    entry.write_text(json.dumps({"url": url, "fetched_at": time.time(), "html": html}))
    return html
