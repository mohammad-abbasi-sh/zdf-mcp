"""Offline tests — parse real captured ZDF heute RSS feeds + a real
article page (its embedded ZDF API token scrubbed to REDACTED), no
network. The article fixture keeps its <p> body + JSON-LD NewsArticle
intact."""
import json
import pathlib
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))

from zdf_mcp import domain as dom
from zdf_mcp import server as srv

FIX = pathlib.Path(__file__).resolve().parent / "fixtures"


def _read(name):
    return (FIX / name).read_text(encoding="utf-8")


class TestTopics(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(dom.validate_topic("Politik"), "politik")
        self.assertEqual(dom.validate_topic("  WISSEN "), "wissen")
        self.assertEqual(dom.validate_topic("kultur"), "kultur")

    def test_invalid(self):
        for bad in ["", "sport", "wirtschaft", "panorama", "news"]:
            with self.assertRaises(ValueError, msg=bad):
                dom.validate_topic(bad)

    def test_feed_urls(self):
        self.assertEqual(dom.feed_url(), "https://www.zdfheute.de/rss/zdf/nachrichten")
        self.assertEqual(dom.feed_url("politik"), "https://www.zdfheute.de/rss/zdf/politik")
        self.assertEqual(dom.feed_url("wissen"), "https://www.zdfheute.de/rss/zdf/wissen")

    def test_limit(self):
        self.assertEqual(dom.validate_limit(10), 10)
        with self.assertRaises(ValueError):
            dom.validate_limit(0)
        with self.assertRaises(ValueError):
            dom.validate_limit(51)


class TestFixtures(unittest.TestCase):
    def test_feed_main(self):
        items = dom.parse_feed(_read("feed-main.xml"))
        self.assertEqual(len(items), 173)
        self.assertTrue(all(i["title"] and i["url"] and i["published"] for i in items))
        # The main feed mixes ZDF-family links: zdfheute.de (113),
        # zdf.de programme pages (32), phoenix.de videos (26) + 2 more.
        self.assertTrue(all(i["url"].startswith("https://") for i in items))
        self.assertGreaterEqual(
            sum(1 for i in items if i["url"].startswith("https://www.zdfheute.de/")), 100)
        self.assertTrue(any(i["categories"] for i in items))
        self.assertEqual(items[0]["title"], "Will Aigner wirklich Brücken bauen?")

    def test_feed_politik(self):
        items = dom.parse_feed(_read("feed-politik.xml"))
        self.assertEqual(len(items), 14)
        self.assertTrue(all(i["title"] and i["url"] for i in items))

    def test_feed_wissen(self):
        items = dom.parse_feed(_read("feed-wissen.xml"))
        self.assertEqual(len(items), 20)

    def test_feed_kultur(self):
        items = dom.parse_feed(_read("feed-kultur.xml"))
        self.assertEqual(len(items), 18)

    def test_article(self):
        out = dom.parse_article(_read("article-aigner.html"))
        self.assertEqual(out["headline"], 'Ilse Aigner im "Wahlkampf": Will sie wirklich Brücken bauen?')
        self.assertTrue(out["published"])
        self.assertGreater(len(out["body"]), 2000)
        self.assertIn("überparteilich", out["body"])
        self.assertIn("Bundespräsidentin", out["body"])

    def test_article_url(self):
        self.assertEqual(
            dom.article_url("https://www.zdfheute.de/politik/deutschland/x-100.html"),
            "https://www.zdfheute.de/politik/deutschland/x-100.html")
        self.assertEqual(
            dom.article_url("politik/deutschland/x-100.html"),
            "https://www.zdfheute.de/politik/deutschland/x-100.html")
        with self.assertRaises(ValueError):
            dom.article_url("https://www.tagesschau.de/x.html")
        with self.assertRaises(ValueError):
            dom.article_url("")

    def test_feed_bad_xml(self):
        with self.assertRaises(ValueError):
            dom.parse_feed("<rss><channel><item>broken")


class TestServerOffline(unittest.TestCase):
    """Server tools with fetch_text mocked to the fixtures."""

    def _mock_fetch(self, name):
        def fake(url):
            if url == dom.feed_url():
                return _read("feed-main.xml")
            if url == dom.feed_url("politik"):
                return _read("feed-politik.xml")
            if url == dom.feed_url("wissen"):
                return _read("feed-wissen.xml")
            if url == dom.feed_url("kultur"):
                return _read("feed-kultur.xml")
            if "aigner-bundespraesidentin" in url:
                return _read("article-aigner.html")
            raise AssertionError(f"unexpected URL {url}")
        return fake

    def test_headlines(self):
        with mock.patch("zdf_mcp.server._http.fetch_text", self._mock_fetch(None)):
            out = json.loads(srv.zdf_headlines(limit=5))
        self.assertNotIn("error", out)
        self.assertEqual(out["total_results"], 173)
        self.assertEqual(out["count"], 5)
        self.assertEqual(out["source"], "zdfheute.de")
        self.assertIn("fetched_at", out)

    def test_topic(self):
        with mock.patch("zdf_mcp.server._http.fetch_text", self._mock_fetch(None)):
            out = json.loads(srv.zdf_news_by_topic("politik", limit=3))
        self.assertNotIn("error", out)
        self.assertEqual(out["total_results"], 14)
        self.assertEqual(out["topic"], "politik")

    def test_topic_invalid(self):
        out = json.loads(srv.zdf_news_by_topic("sport"))
        self.assertIn("error", out)
        self.assertIn("sport", out["error"])

    def test_search(self):
        with mock.patch("zdf_mcp.server._http.fetch_text", self._mock_fetch(None)):
            out = json.loads(srv.zdf_search_news("Aigner", limit=5))
        self.assertNotIn("error", out)
        self.assertGreaterEqual(out["total_results"], 1)
        self.assertIn("Aigner", out["items"][0]["title"])

    def test_search_nomatch(self):
        with mock.patch("zdf_mcp.server._http.fetch_text", self._mock_fetch(None)):
            out = json.loads(srv.zdf_search_news("qqqzzzznomatch", limit=5))
        self.assertNotIn("error", out)
        self.assertEqual(out["total_results"], 0)
        self.assertEqual(out["items"], [])

    def test_search_empty_query(self):
        out = json.loads(srv.zdf_search_news("   "))
        self.assertIn("error", out)

    def test_get_article(self):
        with mock.patch("zdf_mcp.server._http.fetch_text", self._mock_fetch(None)):
            out = json.loads(srv.zdf_get_article(
                "https://www.zdfheute.de/politik/deutschland/aigner-bundespraesidentin-linke-afd-100.html"))
        self.assertNotIn("error", out)
        self.assertIn("Aigner", out["headline"])
        self.assertGreater(len(out["body"]), 2000)

    def test_get_article_bad_url(self):
        out = json.loads(srv.zdf_get_article("https://www.tagesschau.de/x.html"))
        self.assertIn("error", out)

    def test_health_mocked(self):
        with mock.patch("zdf_mcp.server._http.health_check",
                        return_value={"status": "ok", "http_status": 200, "url": dom.FEED}):
            out = json.loads(srv.zdf_health())
        self.assertEqual(out["status"], "ok")


if __name__ == "__main__":
    unittest.main()
