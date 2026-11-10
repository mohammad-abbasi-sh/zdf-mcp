"""Domain logic: shape ZDF heute RSS feeds + article pages into
compact dicts (stdlib only).

Data source: the official ZDF heute RSS feeds
(https://www.zdfheute.de/rss/zdf/nachrichten and topic feeds
/rss/zdf/{politik,sport,wissen,kultur}) and zdfheute.de article
pages — free, no key, no login.

Scope note (2026-11-10): the ZDF Mediathek lane is occupied by the
live maintained Kotlin server Nicklas2751/zdfmediathek-mcp
(search_content, broadcast schedules, current broadcasts via the
official Mediathek API), so this server covers ONLY the news lane
that competitor does not touch — zdfheute headlines, topics, search
and article text. There is NO mediathek search tool here, and no
programme tool: /tv-programm and /programm both 404 and the
competitor's broadcast-schedules tool already covers that intent.
"""
from __future__ import annotations

import html as _html
import json
import re
import xml.etree.ElementTree as ET

BASE = "https://www.zdfheute.de"
FEED = f"{BASE}/rss/zdf/nachrichten"

# Topic feeds verified live 2026-11-10. wirtschaft and panorama 404 —
# they are not offered. sport returns the stale sportstudio feed
# (0 items, last pubDate Mar 2025) — also not offered.
TOPICS = {"politik", "wissen", "kultur"}

_LD_RE = re.compile(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', re.S)
_P_RE = re.compile(r'<p[^>]*>(.*?)</p>', re.S)
_TAG_RE = re.compile(r'<[^>]+>')


def validate_topic(topic: str) -> str:
    key = (topic or "").strip().lower()
    if key not in TOPICS:
        raise ValueError(
            f"unsupported topic: {topic!r} "
            f"(use one of: {', '.join(sorted(TOPICS))})"
        )
    return key


def validate_limit(limit: int) -> int:
    if not 1 <= limit <= 50:
        raise ValueError(f"limit out of range: {limit} (expected 1..50)")
    return limit


def feed_url(topic: str | None = None) -> str:
    if topic is None:
        return FEED
    return f"{BASE}/rss/zdf/{validate_topic(topic)}"


def _parse_xml(text: str, what: str) -> ET.Element:
    try:
        return ET.fromstring(text)
    except ET.ParseError as e:
        raise ValueError(f"invalid {what}: {e}") from e


def parse_feed(text: str) -> list[dict]:
    """[{title, url, published, description, categories}] — newest first."""
    root = _parse_xml(text, "RSS feed")
    channel = root.find("channel")
    if channel is None:
        raise ValueError("invalid RSS feed: no <channel>")
    out = []
    for item in channel.findall("item"):
        out.append({
            "title": item.findtext("title") or "",
            "url": item.findtext("link") or "",
            "published": item.findtext("pubDate") or "",
            "description": _html.unescape(
                _TAG_RE.sub("", item.findtext("description") or "")
            ).replace("\u00a0", " ").strip(),
            "categories": [c.text for c in item.findall("category") if c.text],
        })
    return out


def article_url(article: str) -> str:
    """Accept a full zdfheute.de URL or a bare slug/path."""
    a = (article or "").strip()
    if not a:
        raise ValueError("article must not be empty")
    if a.startswith("https://www.zdfheute.de/"):
        return a
    if a.startswith("http://") or a.startswith("https://"):
        raise ValueError("article must be a zdfheute.de link "
                         "(https://www.zdfheute.de/...)")
    return f"{BASE}/{a.lstrip('/')}"


def parse_article(html_text: str) -> dict:
    """Extract headline/date (JSON-LD NewsArticle) + cleaned body <p>s.

    zdfheute.de article pages are server-rendered: the body is plain
    <p> tags (19 in the probe article, 2026-11-10). Short paragraphs
    are image captions — kept, they are part of the article.
    """
    headline, published = "", ""
    for m in _LD_RE.finditer(html_text):
        try:
            ld = json.loads(m.group(1))
        except json.JSONDecodeError:
            continue
        if isinstance(ld, dict) and ld.get("@type") == "NewsArticle":
            headline = ld.get("headline") or ""
            published = ld.get("datePublished") or ""
            break
    paras = []
    for raw in _P_RE.findall(html_text):
        txt = _html.unescape(_TAG_RE.sub("", raw)).replace("\u00a0", " ").strip()
        if txt:
            paras.append(txt)
    body = "\n\n".join(paras)
    return {"headline": headline, "published": published, "body": body}
