# FETCH_LOG — varieties_finance (2026-09-25)

## Environment
- pip install pypdf openpyxl: FAILED (files.pythonhosted.org 403 via proxy). apt-get poppler-utils: FAILED (403). npm pdfjs-dist: FAILED (registry 403).
- Available locally: python3 (requests only), node22, libreoffice, unzip. No PDF text extractor installed; libreoffice could convert XLSX->CSV.
- WebFetch (server-side fetch tool): EGRESS_BLOCKED for varieties.worldcoffeeresearch.org, api.worldbank.org, www.ihcafe.hn, library.sweetmarias.com.
- WebSearch: WORKS (returns titles, URLs and a summary; no documents). All numbers obtained are therefore snippets -> snippets_unverified.csv.

## 0. Connectivity check (curl, browser UA, 1 request, 20 s, no retries) — 2026-09-25 ~13:58 UTC

| host | HTTP | curl exit | proxy detail |
|---|---|---|---|
| www.ihcafe.hn | 000 | 56 | gateway 403 to CONNECT (policy denial) |
| ihcafe.hn | 000 | 56 | gateway 403 to CONNECT (policy denial) |
| varieties.worldcoffeeresearch.org | 000 | 56 | gateway 403 to CONNECT (policy denial) |
| worldcoffeeresearch.org | 000 | 56 | gateway 403 to CONNECT (policy denial) |
| www.ico.org | 000 | 56 | gateway 403 to CONNECT (policy denial) |
| icocoffee.org | 000 | 56 | gateway 403 to CONNECT (policy denial) |
| www.bch.hn | 000 | 56 | gateway 403 to CONNECT (policy denial) |
| www.tsc.gob.hn | 000 | 56 | gateway 403 to CONNECT (policy denial) |
| www.congresonacional.hn | 000 | 56 | gateway 403 to CONNECT (policy denial) |
| www.sag.gob.hn | 000 | 56 | gateway 403 to CONNECT (policy denial) |
| www.banadesa.hn | 000 | 56 | gateway 403 to CONNECT (policy denial) |
| api.worldbank.org | 000 | 56 | gateway 403 to CONNECT (policy denial) |
| www.promecafe.net | 000 | 56 | gateway 403 to CONNECT (policy denial) |
| www.researchgate.net | 000 | 56 | gateway 403 to CONNECT (policy denial) |
| www.scielo.org | 000 | 56 | gateway 403 to CONNECT (policy denial) |
| www.redalyc.org | 000 | 56 | gateway 403 to CONNECT (policy denial) |
| bdigital.zamorano.edu | 000 | 56 | gateway 403 to CONNECT (policy denial) |
| www.laprensa.hn | 000 | 56 | gateway 403 to CONNECT (policy denial) |
| www.elheraldo.hn | 000 | 56 | gateway 403 to CONNECT (policy denial) |
| www.latribuna.hn | 000 | 56 | gateway 403 to CONNECT (policy denial) |
| proceso.hn | 000 | 56 | gateway 403 to CONNECT (policy denial) |
| repositorio.cepal.org | 000 | 56 | gateway 403 to CONNECT (policy denial) |
| openknowledge.fao.org | 000 | 56 | gateway 403 to CONNECT (policy denial) |
| publications.iadb.org | 000 | 56 | gateway 403 to CONNECT (policy denial) |
| documents.worldbank.org | 000 | 56 | gateway 403 to CONNECT (policy denial) |
| www.technoserve.org | 000 | 56 | gateway 403 to CONNECT (policy denial) |
| www.cafeimports.com | 000 | 56 | gateway 403 to CONNECT (policy denial) |
| www.sweetmarias.com | 000 | 56 | gateway 403 to CONNECT (policy denial) |
| cdn.jsdelivr.net | 000 | 56 | gateway 403 to CONNECT (policy denial) |
| raw.githubusercontent.com | 000 | 56 | gateway 403 to CONNECT (policy denial) |
| web.archive.org | 000 | 56 | gateway 403 to CONNECT (policy denial) |

Only github.com answered (HTTP 400 to bare GET). No file could be downloaded from any listed host.
