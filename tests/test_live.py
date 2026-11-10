"""Live tests — hit the real zdfheute.de RSS feeds + one article. Cautious: few requests.

Run:  pytest tests/test_live.py -v
Skip: pytest -m "not live"  (or set ZDF_SKIP_LIVE=1)
"""
import json
import os
import pathlib
import sys
import unittest

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))

from zdf_mcp import server as srv

pytestmark = pytest.mark.live
SKIP = os.environ.get("ZDF_SKIP_LIVE") == "1"


@pytest.mark.skipif(SKIP, reason="ZDF_SKIP_LIVE=1")
class TestLive(unittest.TestCase):
    def test_headlines_live(self):
        out = json.loads(srv.zdf_headlines(limit=3))
        self.assertNotIn("error", out)
        self.assertGreaterEqual(out["total_results"], 50)
        print(f"\nLIVE headlines: {out['total_results']} — {out['items'][0]['title'][:60]}")

    def test_topic_live(self):
        out = json.loads(srv.zdf_news_by_topic("politik", limit=3))
        self.assertNotIn("error", out)
        self.assertGreaterEqual(out["total_results"], 1)
        print(f"\nLIVE politik: {out['total_results']} — {out['items'][0]['title'][:60]}")

    def test_search_live(self):
        out = json.loads(srv.zdf_search_news("Ukraine", limit=3))
        self.assertNotIn("error", out)
        print(f"\nLIVE search 'Ukraine': {out['total_results']} hits")

    def test_get_article_live(self):
        out = json.loads(srv.zdf_get_article(
            "https://www.zdfheute.de/politik/deutschland/aigner-bundespraesidentin-linke-afd-100.html"))
        self.assertNotIn("error", out)
        self.assertTrue(out["headline"])
        self.assertGreater(len(out["body"]), 500)
        print(f"\nLIVE article: {out['headline'][:70]} — body {len(out['body'])} chars")

    def test_health_live(self):
        out = json.loads(srv.zdf_health())
        self.assertEqual(out["status"], "ok")
        self.assertEqual(out["http_status"], 200)
