# Fetch log: station-based grids, Honduras towns

Fetched 2026-09-25 with `research/common/fetch_psl_station_grids.py honduras research/honduras/raw/independent 2005`
from NOAA PSL THREDDS/OPeNDAP (psl.noaa.gov reachable; no 404s, no variable-name changes; the script was not modified).
Nearest 0.5° grid cell to each town (grid_lon in 0–360 °E).

| File | Rows | First | Last | Missing values | Source |
|---|---|---|---|---|---|
| `cpc_precip_daily.csv` | 23808 | 2005-01-01 | 2026-09-23 | 3 (2007-02-26, all towns) | CPC Global Unified Gauge-Based Daily Precipitation (`cpc_global_precip/precip.YYYY.nc`, mm/day) |
| `cpc_tmax_daily.csv` | 23808 | 2005-01-01 | 2026-09-23 | 0 | CPC Global Daily Temperature (`cpc_global_temp/tmax.YYYY.nc`, °C) |
| `cpc_tmin_daily.csv` | 23808 | 2005-01-01 | 2026-09-23 | 0 | CPC Global Daily Temperature (`cpc_global_temp/tmin.YYYY.nc`, °C) |
| `ghcncams_tmean_monthly.csv` | 780 | 2005-01 | 2026-08 | 0 | GHCN_CAMS 2 m temperature (`ghcncams/air.mon.mean.nc`, K converted to °C) |

Daily files: 3 towns × 7936 days (2005-01-01 to 2026-09-23, the last day in the 2026 files on the fetch date), no gaps in the date sequence.
Monthly file: 3 towns × 260 months (2005-01 to 2026-08, the latest month available).
The one empty precipitation day (2007-02-26) is a fill value in the CPC source file, not a fetch failure.

## Grid cells (same cell for all four files)

| Town | grid_lat | grid_lon (°E) |
|---|---|---|
| comayagua | 14.25 | 272.25 |
| ocotepeque | 14.25 | 270.75 |
| copan | 14.75 | 271.25 |

## Failures

335 HTTP requests, 332 returned 200. 3 failed with `ConnectionResetError` (proxy tunnel reset) and succeeded on the script's automatic retry; no year or chunk was skipped. Per-request details are in `fetch_log.jsonl`; `summary.json` is the script's own summary.

## Note

Values are raw grid values, not quality-controlled here. The value ranges include a few outliers, e.g. CPC Tmin below 0 °C; these should be screened before analysis.
