# BPS fetch log

Date: 2026-09-24 (UTC). Fetcher: helper session, curl with a browser User-Agent, one request per host, 20 s timeout, no retries.

## Connectivity check

| Host | Result |
|---|---|
| www.bps.go.id | blocked: proxy CONNECT 403 (curl 56) |
| web-api.bps.go.id | blocked: proxy CONNECT 403 (curl 56) |
| webapi.bps.go.id | blocked: proxy CONNECT 403 (curl 56) |
| searchengine.web.bps.go.id | blocked: proxy CONNECT 403 (curl 56) |
| sumsel.bps.go.id | blocked: proxy CONNECT 403 (curl 56) |
| lampung.bps.go.id | blocked: proxy CONNECT 403 (curl 56) |
| bengkulu.bps.go.id | blocked: proxy CONNECT 403 (curl 56) |
| jatim.bps.go.id | blocked: proxy CONNECT 403 (curl 56) |
| sumut.bps.go.id | blocked: proxy CONNECT 403 (curl 56) |
| aceh.bps.go.id | blocked: proxy CONNECT 403 (curl 56) |

## Outcome

The environment's network policy blocks every BPS host, so nothing was downloaded. That covers A (SEP 2024 national, plantation-subsector and provincial books), B (SOUT 2014 cost-per-hectare tables and publication) and C (Statistik Tanaman Perkebunan Tahunan 2024, Statistik Kopi 2023, Kakao / Kelapa Sawit / Karet, and province-level coffee area and production tables).
No PDFs were fetched, so no text was extracted.

To fetch them, add `*.bps.go.id` (or at least `www.bps.go.id`, `web-api.bps.go.id` and the provincial subdomains) to the environment's network allowlist and run this again, or download the files by hand and put them in this folder.
