# Honduras coffee: varieties, finance, costs, farm-gate prices (raw sources)

**Status (2026-09-25): no documents could be downloaded.** This session's network is as blocked as the requesting session's:
- curl got a proxy 403 on CONNECT for all 28 requested hosts, plus jsdelivr, raw.githubusercontent and web.archive.org (see `FETCH_LOG.md`).
- The server-side WebFetch tool returned `EGRESS_BLOCKED` for WCR, IHCAFE, World Bank API and Sweet Maria's.
- pip, apt and npm are also blocked (403), so no PDF or XLSX extraction tools could be installed.
- Only **WebSearch** worked. It returns titles, URLs and a search-engine summary, which counts as a snippet under the golden rule.

## Files
| file | content |
|---|---|
| `varieties.csv`, `variety_adoption.csv`, `yields.csv`, `finance.csv`, `credit_bch.csv`, `costs.csv`, `farmgate.csv` | **Header only.** No number could be read in a downloaded document, so none are recorded as verified. |
| `snippets_unverified.csv` | 37 numbers or facts from WebSearch summaries, each marked UNVERIFIED, with the query used and the candidate source URLs. |
| `sources_to_fetch.csv` | Direct URLs (IHCAFE mdocs, decree PDFs on FAOLEX/TSC/IHCAFE, Avelino 2015 full text, BCH FX XLSX, INE export bulletin, USDA GAIN, AECID cost guide) to download when a host is allowed. |
| `FETCH_LOG.md` | Connectivity results and tooling notes. |

## Most important leads (ALL UNVERIFIED, from search summaries only)
| topic | claim | candidate source |
|---|---|---|
| Lempira | IHCAFE says resistance lost (monitored since 2007, susceptible by 2015, officially 2017) | IHCAFE Boletín SAT No 8, Oct 2017 (`ihcafe.hn/?mdocs-file=5360`); PROMECAFE WikiCafe 2019 |
| Lempira adoption | 56.08% of sampled farms; 67.74% of farms with susceptible varieties (2017) | same bulletin |
| Varieties | Lempira: Catimor (Timor 832/1 x Caturra), released 1997/98. Parainema: Sarchimor, released 2004. 2024 releases: Ihcatú 75, Anacafé 14 SHN, Obatá SHN | WCR pages; El Heraldo Feb 2024 |
| 2012-13 rust | ~100,000 mz affected (25%); ~1.5 M qq lost (~US$250 M); 200,000 of 400,000 mz resistant | El Heraldo 2013 |
| Decreto 93-2018 | up to L1,900 M, L200/qq on 2016/17 production (the US$25/qq and US$1.50/qq in the brief were **not** confirmed) | IHCAFE PDF of decree |
| Fideicomiso | Decreto 152-2003, reformed by 56-2007. The snippet says **US$4/qq** retention, which conflicts with the brief's US$9/qq | FAOLEX hon94834.pdf |
| 2018-19 relief | Decreto 47-2018, up to 20 yrs at 2%; BANHPROVI coffee fund L300 M; >55,000 growers | El Heraldo; MiAmbiente |
| Bono Cafetalero | 2020-21: L250 M (~US$10.1 M), 83,273 producers, 216,223 qq fertiliser. 2025: L350 M, 119,803 producers, 300,000 qq | La Prensa; TNH |
| Yield | ~18 qq oro/mz national; 2022-23 production 7,159,804 qq oro | El Heraldo / La Prensa |
| Cost | ~US$130/qq (2023); break-even ~US$135/qq (2019) | La Prensa |
| Export price | 2023-24 average US$198.83 per 46 kg | EFE/swissinfo citing IHCAFE |

## Not found even as snippets
- L370 M fertiliser line.
- The 2017 loan.
- PEPP, PAPP and FIRSA details.
- The BCH coffee credit series.
- ICO grower-price series.
- Annual average FX series.
- IHCAFE 95.
- Variety-level yields.

## Next step
The environment's network access must allow the hosts above (at least ihcafe.hn, faolex.fao.org, tsc.gob.hn, varieties.worldcoffeeresearch.org, api.worldbank.org, bch.hn, ico.org). Then fetch `sources_to_fetch.csv` and verify each snippet.
