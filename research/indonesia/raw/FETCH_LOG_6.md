# Fetch log 6: area, BPS costs, wages, fertiliser, FX, farm budgets

Date: 2026-09-24 (UTC). Fetcher: helper session. Each host got one curl request (browser User-Agent, 20 s timeout, no retries). The blocked hosts satudata.pertanian.go.id and jurnal.polinela.ac.id were also tried once with the WebFetch tool.

## Outcome: nothing downloaded, the network policy is still blocking

The brief said network access had just been opened, but the egress proxy still refuses CONNECT with HTTP 403 for every source host. The proxy status endpoint lists these as "gateway answered 403 to CONNECT (policy denial)". WebFetch returned EGRESS_BLOCKED. The proxy rules say not to route around a policy denial, so I did not try mirrors or other workarounds.

So none of these output files were created: `area_by_province.csv`, `bps_cost_per_ha.csv`, `farm_wage.csv`, `fertiliser_het.csv`, `fx_idr_usd.csv`. `costs/farm_budgets.csv` still has only its header row. The brief allows only numbers read from downloaded documents.

PDF/XLSX tools are also unavailable:
- `pip install pypdf pdfplumber openpyxl` fails: pypi.org answers 200, but files.pythonhosted.org returns 403 with `x-deny-reason: host_not_allowed`.
- `apt-get install poppler-utils` fails: the Ubuntu archive returns 403.
- `pdftotext`, `pypdf`, `pdfplumber` and `openpyxl` are not installed.

## Connectivity check

| Host | Result |
|---|---|
| www.bps.go.id | blocked: proxy CONNECT 403 (policy denial) |
| web-api.bps.go.id | blocked: proxy CONNECT 403 (policy denial) |
| webapi.bps.go.id | blocked: proxy CONNECT 403 (policy denial) |
| sumsel.bps.go.id | blocked: proxy CONNECT 403 (policy denial) |
| lampung.bps.go.id | blocked: proxy CONNECT 403 (policy denial) |
| bengkulu.bps.go.id | blocked: proxy CONNECT 403 (policy denial) |
| jatim.bps.go.id | blocked: proxy CONNECT 403 (policy denial) |
| satudata.pertanian.go.id | blocked: proxy CONNECT 403 (policy denial) |
| ditjenbun.pertanian.go.id | reachable through the proxy, but the site's Cloudflare answers 403 'Attention Required' (bot challenge) to curl |
| psp.pertanian.go.id | blocked: proxy CONNECT 403 (policy denial) |
| jurnal.polinela.ac.id | blocked: proxy CONNECT 403 (policy denial) |
| repository.lppm.unila.ac.id | blocked: proxy CONNECT 403 (policy denial) |
| jurnal.unived.ac.id | blocked: proxy CONNECT 403 (policy denial) |
| journal.ipb.ac.id | blocked: proxy CONNECT 403 (policy denial) |
| www.researchgate.net | blocked: proxy CONNECT 403 (policy denial) |
| www.ankerresearchinstitute.org | blocked: proxy CONNECT 403 (policy denial) |
| www.fairtrade.net | blocked: proxy CONNECT 403 (policy denial) |
| www.bi.go.id | blocked: proxy CONNECT 403 (policy denial) |
| pypi.org | 200 OK |
| files.pythonhosted.org | 403, x-deny-reason: host_not_allowed (proxy policy) |

WebFetch results: satudata.pertanian.go.id → EGRESS_BLOCKED, jurnal.polinela.ac.id → EGRESS_BLOCKED.

## To unblock

In the cloud environment's settings (environment menu in the session title bar → Edit → Network access), choose a broader access level or add these to the allowed domains:
`*.bps.go.id` (www, web-api, webapi, sumsel, lampung, bengkulu, jatim), `satudata.pertanian.go.id`, `psp.pertanian.go.id`, `jurnal.polinela.ac.id`, `repository.lppm.unila.ac.id`, `jurnal.unived.ac.id`, `journal.ipb.ac.id`, `www.researchgate.net`, `www.ankerresearchinstitute.org`, `www.fairtrade.net`, `www.bi.go.id`, `files.pythonhosted.org`, and `archive.ubuntu.com` / `security.ubuntu.com` for poppler-utils. See https://code.claude.com/docs/en/claude-code-on-the-web.

ditjenbun.pertanian.go.id is not blocked by the proxy, but its Cloudflare bot check blocks curl, so it will probably need a manual browser download.

Once the hosts are allowed, run this helper again. Candidate farm-budget URLs are already listed in `costs/candidate_sources.csv`.
