# zdf-mcp 📺

mcp-name: io.github.mohammad-abbasi-sh/zdf-mcp

Unofficial **read-only** MCP server for **[zdfheute.de](https://www.zdfheute.de)** — ZDF heute news from zdfheute.de (free, no key, no login): latest headlines, news by topic, keyword search and full article text. No key, no login.

> Built by Mohammad Abbasi as part of the "Germany MCP factory". Not affiliated with zdfheute.de.

## For AI agents

Add to your MCP client config (stdio):

```json
{
  "mcpServers": {
    "zdf": {
      "command": "uvx",
      "args": ["zdf-mcp==0.1.0"]
    }
  }
}
```

Or run locally: `python -m zdf_mcp.server` (needs `mcp<2`, `httpx`).

## Tools

| Tool | Description |
|------|-------------|
| `zdf_headlines` | Latest headlines from the ZDF heute RSS feed — `limit` 1..50 |
| `zdf_news_by_topic` | News by topic — `topic`: politik, sport, wissen, kultur; `limit` 1..50 |
| `zdf_search_news` | Keyword search over the latest headlines — `query`, `limit` 1..50 |
| `zdf_get_article` | Full article text — `article` (zdfheute.de URL or slug) |
| `zdf_health` | Reachability probe (ok / blocked / error) — one polite request |

## Development

```bash
python3 -m venv .venv && .venv/bin/pip install "mcp<2" httpx pytest
.venv/bin/pip install -e .
.venv/bin/python -m pytest tests/ -q
```

## License

MIT

---

Built by [Mohammad Abbasi](https://github.com/mohammad-abbasi-sh) — [Almanibama](https://almanibama.ir) · [mabbasi.ir](https://mabbasi.ir)
