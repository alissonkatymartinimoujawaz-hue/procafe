# Fetch log: Indonesian crop area, production, yield and farm-budget sources

Fetched on 2026-09-24 (UTC) through the cloud session's egress proxy.

## Connectivity check (one request per host, 20 s timeout, no retries)

| Host | Result |
|---|---|
| ourworldindata.org | **BLOCKED**: proxy CONNECT returned 403 |
| bulks-faostat.fao.org | Reachable. The root returns an S3 403 (listing denied); the bulk zip files return 200 |
| fenixservices.fao.org | **BLOCKED**: proxy CONNECT returned 403 |
| www.fao.org | **BLOCKED**: proxy CONNECT returned 403 |
| satudata.pertanian.go.id | **BLOCKED**: proxy CONNECT returned 403 |
| ditjenbun.pertanian.go.id | The proxy lets it through, but the site's Cloudflare challenge returns 403 ("Attention Required!"), even with a browser User-Agent |
| www.bps.go.id | **BLOCKED**: proxy CONNECT returned 403 |
| webapi.bps.go.id | **BLOCKED**: proxy CONNECT returned 403 |
| github.com | Reachable (400 on a bare GET of the root) |
| raw.githubusercontent.com | **BLOCKED**: proxy CONNECT returned 403 |

Extra single checks (all failed): epublikasi.pertanian.go.id (http gives 403, https CONNECT gives 403), pertanian.go.id, psp.pertanian.go.id, kikp-pertanian.id, pisagro.org and wwf.id (CONNECT 403 for each).

## Files

| File | Source URL | HTTP | Size (bytes) | Contents |
|---|---|---|---|---|
| faostat_indonesia_crops.csv | https://bulks-faostat.fao.org/production/Production_Crops_Livestock_E_Asia.zip (FAOSTAT QCL, file dated 2025-12-23; zip 4,708,076 B) | 200 | 30,884 | Filtered to Indonesia (area code 101). Long format: item_code, item, element_code, element, unit, year, value, flag. Covers 1990→2024. Items: 656 Coffee, green; 661 Cocoa beans; 254 Oil palm fruit; 836 Natural rubber; each with 5312 Area harvested (ha), 5510 Production (t) and 5412 Yield (kg/ha). Also 257 Palm oil and 258 Oil of palm kernel (production only). Area harvested in 2000 → 2024: cocoa 749,917 → 1,386,749 ha; coffee 1,260,687 → 1,269,354 ha; rubber 2,400,000 (E) → 3,149,277 ha; oil palm fruit 2,014,000 (X) → 14,320,000 (X) ha. FAO flags: A official, E estimated, X from an international organisation. FAO has no arabica/robusta split. |
| faostat_indonesia_producer_prices.csv | https://bulks-faostat.fao.org/production/Prices_E_Asia.zip (FAOSTAT PP; zip 2,569,132 B) | 200 | 88,539 | Filtered to Indonesia, same items. Columns: item_code, item, element_code, element, months, unit, year, value, flag. Covers 1991→2025. Elements: Producer Price in LCU/t (annual and monthly rows), SLC/t and USD/t, plus the Producer Price Index (2014-2016 = 100). |

The raw multi-country zip files were not committed; they were used only in the scratchpad.

## Not fetched (the host is blocked; the URLs below came from web search and were **not** downloaded)

- **Our World in Data grapher CSVs**: ourworldindata.org is blocked. The FAOSTAT bulk files above hold the same underlying data.
- **Ministry of Agriculture Outlook books** (satudata.pertanian.go.id is blocked):
  - Outlook Kopi 2023: https://satudata.pertanian.go.id/assets/docs/publikasi/Buku_Outlook_Kopi_2023_lengkap.pdf
  - Outlook Kakao 2025: https://satudata.pertanian.go.id/assets/docs/publikasi/OUTLOOK_KAKAO_2025_sign_rev.pdf
  - Outlook Kakao 2023: https://satudata.pertanian.go.id/assets/docs/publikasi/FINALOUTLOOK_KAKAO_2023.pdf
  - Outlook Kakao 2022: https://satudata.pertanian.go.id/assets/docs/publikasi/OUTLOOK_KAKAO_2022.pdf
  - Outlook Kelapa Sawit and Outlook Karet: no URL found; they are probably under the same /assets/docs/publikasi/ path.
- **Ditjenbun Statistik Perkebunan (Unggulan Nasional)**: behind a Cloudflare challenge.
  - 2023-2025 Jilid I: https://ditjenbun.pertanian.go.id/?publikasi=buku-statistik-perkebunan-2023-2025-jilid-i
  - 2021-2023: https://ditjenbun.pertanian.go.id/?publikasi=buku-statistik-perkebunan-2021-2023
  - Index page: https://ditjenbun.pertanian.go.id/pojok-media/publikasi/
  - These books give area by smallholder/state/private estate and are the only source here that splits coffee into arabica and robusta.
- **BPS publications** (www.bps.go.id is blocked): Statistik Kopi Indonesia 2023 (published 2024-11-29, catalog 5504006, 9.63 MB), https://www.bps.go.id/en/publication/2024/11/29/d748d9bf594118fe112fc51e/statistik-kopi-indonesia-2023.html. The Kakao, Kelapa Sawit and Karet editions and the "Struktur Ongkos Usaha Tani" / "Survei Ongkos Usaha Tanaman Perkebunan" publications were not searched for, because the host is blocked.
- **Farm budgets / production cost per hectare**: no reachable source was found. All candidate sources (BPS, Ministry of Agriculture) are on blocked hosts.

To get the missing files, add satudata.pertanian.go.id, www.bps.go.id and ourworldindata.org to the environment's network allowlist, or download the PDFs by hand and put them in this folder. The Ditjenbun site needs a real browser because of the Cloudflare challenge.
