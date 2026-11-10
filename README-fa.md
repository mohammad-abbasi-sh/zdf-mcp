# zdf-mcp 📺

mcp-name: io.github.mohammad-abbasi-sh/zdf-mcp

سرور MCP غیررسمی و **فقط‌خواندنی** برای **[zdfheute.de](https://www.zdfheute.de)** — اخبار ZDF heute از zdfheute.de (رایگان، بدون کلید): تازه‌ترین تیترها، اخبار بر اساس موضوع، جست‌وجوی کلیدواژه و متن کامل مقاله. بدون کلید، بدون ورود.

> ساختهٔ محمد عباسی، بخشی از «کارخانهٔ MCP آلمان». وابسته به zdfheute.de نیست.

## برای ایجنت‌های هوش مصنوعی

به پیکربندی MCP کلاینت اضافه کنید (stdio):

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

یا به‌صورت محلی اجرا کنید: `python -m zdf_mcp.server` (نیازمند `mcp<2` و `httpx`).

## ابزارها

| ابزار | توضیح |
|------|-------|
| `zdf_headlines` | تازه‌ترین تیترهای ZDF heute |
| `zdf_news_by_topic` | اخبار ZDF heute بر اساس موضوع |
| `zdf_search_news` | جست‌وجوی تیترهای ZDF heute با کلیدواژه |
| `zdf_get_article` | متن کامل مقالهٔ ZDF heute |
| `zdf_health` | بررسی دسترس‌پذیری (ok / blocked / error) — یک درخواست مؤدبانه |

## توسعه

```bash
python3 -m venv .venv && .venv/bin/pip install "mcp<2" httpx pytest
.venv/bin/pip install -e .
.venv/bin/python -m pytest tests/ -q
```

## لایسنس

MIT

---

Built by [Mohammad Abbasi](https://github.com/mohammad-abbasi-sh) — [Almanibama](https://almanibama.ir) · [mabbasi.ir](https://mabbasi.ir)
