# Asia Coffee differentials fetch log

Date: 2026-09-24 (UTC). Fetcher: helper session.

## Hosts

Everything was blocked; only the WebSearch tool worked.

| Host | curl (browser UA, 20 s, 1 try) | WebFetch tool |
|---|---|---|
| www.brecorder.com | blocked (proxy CONNECT 403, curl 56) | blocked (EGRESS_BLOCKED) |
| www.ft.lk | blocked | blocked |
| www.deccanherald.com | blocked | blocked |
| www.tradingview.com | blocked | blocked |
| www.malaymail.com | blocked | blocked |
| www.nasdaq.com | blocked | blocked |
| theedgemalaysia.com | blocked | blocked |
| www.zawya.com | blocked | blocked |
| www.reuters.com, www.business-standard.com, www.thestar.com.my, www.investing.com | blocked | not tried |
| news.yahoo.com | not tried | blocked |

## Result

- Quotes recorded: **0**. `asia_coffee_differentials.csv` contains only the header. No article page could be opened, and the brief says to record only values read on a page.
- Coverage gap: January 2023 to September 2026 is entirely missing.
- `candidate_articles.csv` lists 37 syndicated Asia Coffee articles, with their titles and URLs taken from WebSearch results. Once the hosts are reachable, fetch these first. `year_from_url` is filled only where the URL encodes the year (TradingView/Reuters). Business Recorder IDs run from about 40253785 to 40440002; higher IDs are more recent.
- The WebSearch answer summaries did quote figures, but these are model-written summaries that mixed up dates across articles (for example, a 2018 quote shown as recent). They were **not** recorded.

## To complete

Add at least `www.brecorder.com` and `www.tradingview.com` to the environment's network allowlist, then fetch the URLs in `candidate_articles.csv`. Business Recorder carries almost every weekly Reuters "Asia coffee" report.
