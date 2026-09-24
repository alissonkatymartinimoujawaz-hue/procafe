# Forest / land-use fetch log (2026-09-24)

## 1. Global Forest Watch country statistics (Indonesia) — FAILED
| URL | Attempt | Result |
|---|---|---|
| https://gfw2-data.s3.amazonaws.com/country-pages/country_stats/download/IDN.xlsx | 1 | curl (56) CONNECT tunnel failed, proxy 403 (host blocked by environment network policy) |
| same | 2 (after 5 s) | same, proxy 403 |

WebSearch for a current link found no alternative host. It pointed to globalforestwatch.org / globalnaturewatch.org dashboards and to the `wri/write_country_stats` repo (github.com, also blocked by egress proxy). No other download URL was found, so no other file was tried.

## 3. GFW data API (fallback) — FAILED
| URL | Attempt | Result |
|---|---|---|
| https://data-api.globalforestwatch.org/dataset/gadm__tcl__adm1_change | 1 | proxy 403 (host blocked) |
| same | 2 (after 5 s) | proxy 403 |

So `forest_loss_by_province.csv` and `tree_cover_2000_by_province.csv` were **not produced**. No tree-cover-loss numbers are recorded here. To get them, allow `gfw2-data.s3.amazonaws.com` (or `data-api.globalforestwatch.org`) in the environment's network settings, or download IDN.xlsx manually and add it to this folder.

## 2. FAOSTAT land use (bulk) — OK
- URL: https://bulks-faostat.fao.org/production/Inputs_LandUse_E_All_Data_(Normalized).zip, HTTP 200, 2,971,760 bytes (zip dated 2026-09-16; inner CSV 49,970,463 bytes, latin-1).
- Filter: `Area Code` = 101 (Indonesia); Items = Agricultural land, Cropland, Forest land, Land area, Permanent crops, Primary Forest, Naturally regenerating forest, Planted Forest; all elements (Area in 1000 ha, plus shares, per-capita and carbon stock where FAO provides them); all years.
- Output: `faostat_indonesia_landuse.csv` (original FAOSTAT columns), 927 data rows, years 1961–2025 (forest items from 1990).
- The zip was deleted after extraction and is not committed.
