"""MCP server: unofficial read-only access to ZDF heute news via
the official zdfheute.de RSS feeds + article pages. No key, no
login. NOTE: this server covers the NEWS lane only — the ZDF
Mediathek lane is occupied by the live maintained Kotlin server
Nicklas2751/zdfmediathek-mcp, so there is no mediathek search or
programme tool here (verified 2026-11-10)."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone

from mcp.server.fastmcp import FastMCP

from . import domain as _dom
from . import http as _http

INSTRUCTIONS = """\
Unofficial read-only MCP server for ZDF heute news via the official \
zdfheute.de RSS feeds (no key, no login): latest headlines, news by \
topic (politik, wissen, kultur), keyword search over the \
latest headlines and full article text. This server covers the NEWS \
lane only — the ZDF Mediathek is served by the live Kotlin server \
Nicklas2751/zdfmediathek-mcp, so there is no mediathek search or \
programme tool here. Search covers only the latest headlines in the \
RSS feed (~173 items), not the full archive. Built by Mohammad \
Abbasi (mohammad-abbasi-sh) — https://almanibama.ir · \
https://mabbasi.ir — Germany MCP factory.\
"""

_SOURCE = "zdfheute.de"
_DISCLAIMER = "Unofficial read-only data from zdfheute.de RSS feeds and article pages; verify on the site before acting on it."


def _envelope() -> dict:
    return {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "source": _SOURCE,
        "disclaimer": _DISCLAIMER,
    }


def _ok(payload: dict) -> str:
    return json.dumps({**_envelope(), **payload}, ensure_ascii=False)


def _err(e: Exception) -> str:
    return _ok({"error": str(e)})


mcp = FastMCP("zdf-mcp", instructions=INSTRUCTIONS)


@mcp.tool()
def zdf_headlines(limit: int = 10) -> str:
    """Latest ZDF heute headlines. limit: 1..50 (default 10)."""
    try:
        lim = _dom.validate_limit(limit)
        items = _dom.parse_feed(_http.fetch_text(_dom.feed_url()))
    except (_http.ZdfMcpError, ValueError) as e:
        return _err(e)
    return _ok({"total_results": len(items),
                "count": min(lim, len(items)), "items": items[:lim]})


@mcp.tool()
def zdf_news_by_topic(topic: str, limit: int = 10) -> str:
    """ZDF heute news by topic. topic: politik, wissen or kultur.
    limit: 1..50 (default 10)."""
    try:
        top = _dom.validate_topic(topic)
        lim = _dom.validate_limit(limit)
        items = _dom.parse_feed(_http.fetch_text(_dom.feed_url(top)))
    except (_http.ZdfMcpError, ValueError) as e:
        return _err(e)
    return _ok({"topic": top, "total_results": len(items),
                "count": min(lim, len(items)), "items": items[:lim]})


@mcp.tool()
def zdf_search_news(query: str, limit: int = 10) -> str:
    """Keyword search over the LATEST ZDF heute headlines (the RSS
    feed holds roughly the last 173 items — this is not a
    full-archive search). query: keyword or phrase.
    limit: 1..50 (default 10)."""
    try:
        lim = _dom.validate_limit(limit)
        q = (query or "").strip()
        if not q:
            raise ValueError("query must not be empty")
        items = _dom.parse_feed(_http.fetch_text(_dom.feed_url()))
        ql = q.casefold()
        hits = [i for i in items
                if ql in i["title"].casefold()
                or ql in i["description"].casefold()]
    except (_http.ZdfMcpError, ValueError) as e:
        return _err(e)
    return _ok({"query": q,
                "searched": "latest headlines in the ZDF heute RSS feed",
                "total_results": len(hits),
                "count": min(lim, len(hits)), "items": hits[:lim]})


@mcp.tool()
def zdf_get_article(article: str) -> str:
    """Full text of one ZDF heute article. article: a zdfheute.de
    article link (e.g. https://www.zdfheute.de/politik/.../...
    -100.html) or a bare path/slug."""
    try:
        u = _dom.article_url(article)
        out = _dom.parse_article(_http.fetch_text(u))
        if not out["headline"] and not out["body"]:
            raise ValueError("no article content found at that URL "
                             "(it may be a video or topic page)")
    except (_http.ZdfMcpError, ValueError) as e:
        return _err(e)
    return _ok({"url": u, "headline": out["headline"],
                "published": out["published"],
                "body": out["body"][:6000]})


@mcp.tool()
def zdf_health() -> str:
    """Check whether zdfheute.de is reachable right now.

    Returns status ok (HTTP 200), blocked (HTTP 403/429 — bot wall or
    rate limit) or error, plus the HTTP status and the probed URL.
    One polite request; it does not fetch any listings."""
    return _ok(_http.health_check())


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    sys.exit(main())
