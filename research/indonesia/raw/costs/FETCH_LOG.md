# Farm-budget / cost-of-production fetch log

Date: 2026-09-24 (UTC). Fetcher: helper session. Checks used curl with a browser User-Agent, one request per host, a 20 s timeout and no retries. Blocked hosts were also tried once with the WebFetch tool.

## Outcome: nothing downloaded

The environment's network egress proxy blocked **every** host named in the brief, plus every fallback mirror or aggregator I tried. So:

- `farm_budgets.csv` holds **only the header row**. The brief allows only numbers read in the documents, not ones from search snippets, and no document could be opened.
- No PDFs or HTML were saved, and no `.txt` extractions were made. Even if downloads had worked, extraction would have failed: `pdftotext` is not installed, `pypdf` and `pdfminer.six` are missing, and `pip install pypdf` gets a 403 from files.pythonhosted.org. pypi.org itself answered 200.
- The BPS step (SEP 2024, SOUT 2014) was skipped because all BPS hosts are still blocked. See `../bps/FETCH_LOG.md`. No new files were added to `raw/bps/`.
- WebSearch works. I used it only to collect candidate URLs, listed in `candidate_sources.csv`. I left out all figures from search snippets on purpose.

## Connectivity check (hosts from the brief)

| Host | curl | WebFetch |
|---|---|---|
| www.bps.go.id | blocked: proxy CONNECT 403 (curl 56) | blocked (earlier run) |
| web-api.bps.go.id | blocked: proxy CONNECT 403 | not tried |
| jurnal.polinela.ac.id | blocked: proxy CONNECT 403 | blocked (EGRESS_BLOCKED) |
| repository.lppm.unila.ac.id | blocked: proxy CONNECT 403 | not tried |
| jurnal.unived.ac.id | blocked: proxy CONNECT 403 | not tried |
| www.researchgate.net | blocked: proxy CONNECT 403 | blocked (EGRESS_BLOCKED) |
| www.ankerresearchinstitute.org | blocked: proxy CONNECT 403 | blocked (EGRESS_BLOCKED) |
| www.fairtrade.net | blocked: proxy CONNECT 403 | not tried |
| www.living-income.com | blocked: proxy CONNECT 403 | not tried |
| www.fao.org | blocked: proxy CONNECT 403 | not tried |
| www.ico.org | blocked: proxy CONNECT 403 | not tried |
| www.idhsustainabletrade.com | blocked: proxy CONNECT 403 | not tried |
| coffeebarometer.org | blocked: proxy CONNECT 403 | not tried |
| www.scopi.or.id | blocked: proxy CONNECT 403 | not tried |
| garuda.kemdikbud.go.id | blocked: proxy CONNECT 403 | not tried |
| e-journal.unair.ac.id | blocked: proxy CONNECT 403 | not tried |
| journal.ipb.ac.id | blocked: proxy CONNECT 403 | not tried |
| jurnal.unej.ac.id | blocked: proxy CONNECT 403 | not tried |
| ojs.unud.ac.id | blocked: proxy CONNECT 403 | not tried |

## Fallback hosts tried (all blocked with proxy CONNECT 403)

repository.uir.ac.id, digilib.uinkhas.ac.id, repository.ipb.ac.id, jurnal.unigal.ac.id, core.ac.uk, api.core.ac.uk, scholar.archive.org, web.archive.org, europepmc.org, doaj.org, api.semanticscholar.org, www.semanticscholar.org, zenodo.org, api.openalex.org, api.crossref.org, www.mdpi.com, raw.githubusercontent.com, apps.fas.usda.gov, ejournal.utp.ac.id, jurnal.um-palembang.ac.id, jurnal.polbangtanmanokwari.ac.id, www.kompas.id, ageconsearch.umn.edu, www.worldbank.org, documents1.worldbank.org, openknowledge.worldbank.org.

Two hosts were not blocked: pypi.org answered 200 and github.com answered 400. Neither has any source documents.

## Documents

| Title | URL | HTTP result | Size | Contents / where the figures are |
|---|---|---|---|---|
| All 20 candidates in `candidate_sources.csv` | see CSV | proxy CONNECT 403 | none | not read |

## Next steps

1. Add the journal hosts (at minimum jurnal.polinela.ac.id, repository.lppm.unila.ac.id, jurnal.unived.ac.id, journal.ipb.ac.id, www.researchgate.net, www.ankerresearchinstitute.org, www.fairtrade.net, *.bps.go.id) to the environment's network allowlist, or switch it to full network access.
2. Add `poppler-utils` (pdftotext) or `pip install pypdf` to the setup script. The PyPI file host is currently blocked.
3. Run this helper again. Or download the PDFs by hand into this folder, and the CSV can be filled in from them.
