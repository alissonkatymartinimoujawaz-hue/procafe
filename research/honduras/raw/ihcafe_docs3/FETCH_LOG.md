# FETCH_LOG — ihcafe_docs3

Fetched 2026-09-25 with curl (browser User-Agent, `-L`, 60 s timeout, up to 2 tries) via `fetch.sh`. The raw per-request log is in `FETCH_LOG.tsv`.

| # | Requested URL | HTTP | Final URL | Size (bytes) | Saved file |
|---|---|---|---|---|---|
| 001 | https://www.laprensa.hn/economia/cafetalero-variedades-cafe-resistente-roya-GVLP1101997 | 200 | same | 184584 | `001_www.laprensa.hn_economia_cafetalero-variedades-cafe-resistente-roya-GVLP1101997.html` (+ `.txt`) |
| 002 | https://www.laprensa.hn/economia/1101997-410/cafetalero-variedades-cafe-resistente-roya (fallback) | 200 | redirected to #001 URL | 184584 | not kept (byte-identical to 001) |
| 003 | https://www.ihcafe.hn/?mdocs-file=5360 | 301 → 000 | https://ihcafe.hn/?mdocs-file=5360 | 0 | none: the redirect target `ihcafe.hn:443` is blocked by the egress proxy (CONNECT 403) |
| 004 | https://ihcafe.hn/?mdocs-file=5360 | 000 | — | 0 | none: `ihcafe.hn:443` is blocked (CONNECT 403) |
| 005 | https://perfectdailygrind.com/es/2020/03/18/explorando-las-variedades-comunes-de-cafe-de-honduras/ | 000 | — | 0 | none: `perfectdailygrind.com:443` is blocked (CONNECT 403) |
| 006 | https://www.ihcafe.hn/?mdocs-posts=informe-estadistico-anual-14-15&mdocs-cat= | 301 → 000 | https://ihcafe.hn/?mdocs-posts=… | 0 | none: redirects to the blocked `ihcafe.hn` |
| 007 | https://www.ihcafe.hn/publicaciones/ | 301 → 000 | https://ihcafe.hn/publicaciones/ | 0 | none: redirects to the blocked `ihcafe.hn`, so no linked Informe Estadístico / Censo PDFs could be listed |

Fallbacks tried, all failed:
- `archive.org/wayback/available` and `web.archive.org` are blocked (CONNECT 403).
- `https://www.ihcafe.hn/?mdocs-file=5360&mdocs-url=false` still returns 301 to the bare `ihcafe.hn` domain.
- `https://www.ihcafe.hn/wp-content/uploads/mdocs/` returns 200 with an empty body (no listing).
- `https://www.ihcafe.hn/wp-json/wp/v2/media?search=alerta` returns 401.

Note: `www.ihcafe.hn` itself is reachable, but WordPress page and query URLs 301-redirect to the bare `ihcafe.hn`, which the network policy denies. Direct `www.ihcafe.hn/wp-content/uploads/...` file URLs, as used in ihcafe_docs2, still work if the exact filename is known.
