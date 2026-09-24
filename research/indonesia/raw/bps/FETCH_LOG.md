# BPS fetch log

Date: 2026-09-24 (UTC). Fetcher: helper session. Checks used curl with a browser User-Agent, one request per host, a 20 s timeout and no retries. This log covers two runs on the same day; the second run added satudata.pertanian.go.id and also tried the WebFetch tool.

## Connectivity check

| Host | curl | WebFetch tool |
|---|---|---|
| www.bps.go.id | blocked: proxy CONNECT 403 (curl 56) | blocked (EGRESS_BLOCKED) |
| web-api.bps.go.id | blocked: proxy CONNECT 403 (curl 56) | not tried |
| webapi.bps.go.id | blocked: proxy CONNECT 403 (curl 56) | not tried |
| searchengine.web.bps.go.id | blocked: proxy CONNECT 403 (curl 56) | not tried |
| sumsel.bps.go.id | blocked: proxy CONNECT 403 (curl 56) | not tried |
| lampung.bps.go.id | blocked: proxy CONNECT 403 (curl 56) | not tried |
| bengkulu.bps.go.id | blocked: proxy CONNECT 403 (curl 56) | not tried |
| jatim.bps.go.id | blocked: proxy CONNECT 403 (curl 56) | not tried |
| sumut.bps.go.id | blocked: proxy CONNECT 403 (curl 56) | not tried |
| aceh.bps.go.id | blocked: proxy CONNECT 403 (curl 56) | not tried |
| satudata.pertanian.go.id | blocked: proxy CONNECT 403 (curl 56) | blocked (EGRESS_BLOCKED), tried on Buku_Outlook_Kopi_2023_lengkap.pdf |

## Outcome

The environment's network policy blocks every BPS host and the Ministry of Agriculture data portal, so nothing was downloaded:

- A: SEP 2024 national, plantation-subsector and provincial books
- B: SOUT 2014 cost-per-hectare tables and the SOUT 2014 publication
- C: Statistik Tanaman Perkebunan Tahunan 2024, Statistik Kopi 2023, and Statistik Kakao, Kelapa Sawit and Karet
- D: the Outlook Kopi, Kakao, Kelapa Sawit and Karet books

No PDFs were fetched, so no text was extracted. `pdftotext` is not installed, and `pip install pypdf` also failed (403 from files.pythonhosted.org). Text extraction would therefore also need a PDF tool installed in the environment's setup script.

No table titles on biaya, ongkos, pendapatan or nilai produksi per hektar could be listed, because no file was read.

To fetch them, add `*.bps.go.id` and `satudata.pertanian.go.id` to the environment's network allowlist and run this again, or download the files by hand and put them in this folder.
