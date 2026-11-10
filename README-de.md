# zdf-mcp 📺

mcp-name: io.github.mohammad-abbasi-sh/zdf-mcp

Inoffizieller **nur lesender** MCP-Server für **[zdfheute.de](https://www.zdfheute.de)** — ZDF-heute-Nachrichten von zdfheute.de (kostenlos, kein Schlüssel, kein Login): aktuelle Schlagzeilen, Nachrichten nach Thema, Stichwortsuche und Volltext. Kein Schlüssel, keine Anmeldung.

> Gebaut von Mohammad Abbasi als Teil der "Germany MCP factory". Nicht mit zdfheute.de verbunden.

## Für KI-Agenten

Zur MCP-Client-Konfiguration hinzufügen (stdio):

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

Oder lokal starten: `python -m zdf_mcp.server` (benötigt `mcp<2`, `httpx`).

## Tools

| Tool | Beschreibung |
|------|-------------|
| `zdf_headlines` | Aktuelle ZDF-heute-Schlagzeilen |
| `zdf_news_by_topic` | ZDF-heute-Nachrichten nach Thema |
| `zdf_search_news` | ZDF-heute-Schlagzeilen nach Stichwort suchen |
| `zdf_get_article` | Volltext eines ZDF-heute-Artikels |
| `zdf_health` | Erreichbarkeitsprüfung (ok / blocked / error) — eine höfliche Anfrage |

## Entwicklung

```bash
python3 -m venv .venv && .venv/bin/pip install "mcp<2" httpx pytest
.venv/bin/pip install -e .
.venv/bin/python -m pytest tests/ -q
```

## Lizenz

MIT

---

Built by [Mohammad Abbasi](https://github.com/mohammad-abbasi-sh) — [Almanibama](https://almanibama.ir) · [mabbasi.ir](https://mabbasi.ir)
