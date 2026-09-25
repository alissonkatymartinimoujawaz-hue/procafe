# Fetch log: Honduras raw data (fetched 2026-09-25)

Scripts: `fetch_nasa.py` (from this folder) and `rain_check/fetch_gpcc.py log.jsonl` (from `rain_check/`). Both ran once, and every request succeeded on the first try. No host was blocked. The per-request logs are in `FETCH_LOG_nasa.jsonl` and `rain_check/log.jsonl`.

## NASA POWER daily (PRECTOTCORR, T2M, T2M_MAX, T2M_MIN, RH2M; community AG)

URL pattern: `https://power.larc.nasa.gov/api/temporal/daily/point?parameters=PRECTOTCORR,T2M,T2M_MAX,T2M_MIN,RH2M&community=AG&latitude={lat}&longitude={lon}&start=19810101&end=20260925&format=JSON`

| File | HTTP | Size (bytes on disk / response) | First | Last | Days | Grid cell (lon, lat, elev m) |
|---|---|---|---|---|---|---|
| nasa_power_daily_comayagua.json | 200 | 1,561,576 / 1,394,768 | 19810101 | 20260922 | 16,701 | -87.633, 14.45, 1015.27 |
| nasa_power_daily_ocotepeque.json | 200 | 1,561,749 / 1,394,941 | 19810101 | 20260922 | 16,701 | -89.183, 14.433, 902.67 |
| nasa_power_daily_copan.json | 200 | 1,561,865 / 1,395,057 | 19810101 | 20260922 | 16,701 | -88.783, 14.767, 790.93 |

The request asked for data up to 20260925. The script dropped the trailing all-fill (-999) days, so the data ends at 20260922. None of the 5 parameters has a -999 value left in any file.

## GPCC monthly (PSL THREDDS OPeNDAP ASCII)

URL pattern: `https://psl.noaa.gov/thredds/dodsC/Datasets/gpcc/{path}.ascii?precip[t0:t1][i0:i1][j0:j1]`. The coordinates were fetched first with `?lat,lon,time`.

| File (in rain_check/) | Dataset path | HTTP | Size (bytes) | Rows | First | Last valid | Grid cells (lat, lon °E): Comayagua / Ocotepeque / Copán |
|---|---|---|---|---|---|---|---|
| gpcc_full_v2020_monthly.csv | full_v2020/precip.mon.total.0.25x0.25.v2020.nc | 200 (9 requests) | 114,382 | 1,404 (468 per town) | 1981-01 | 2019-12 | 14.375, 272.375 / 14.375, 270.875 / 14.875, 271.125 |
| gpcc_monitor_v2020_monthly.csv | monitor/precip.monitor.mon.total.1x1.v2020.nc | 200 (6 requests) | 106,870 | 1,416 (472 per town) | 1982-01 | 2021-04 | 14.5, 272.5 / 14.5, 270.5 / 14.5, 271.5 |
| gpcc_first_guess_monthly.csv | first_guess/precip.first.mon.total.1x1.nc | 200 (3 requests) | 37,247 | 528 (176 per town) | 2012-01 | 2026-08 | 14.5, 272.5 / 14.5, 270.5 / 14.5, 271.5 |

Notes:
- The monitoring product's time axis on PSL runs from 1982-01 to 2025-12. For all 3 towns, the 56 months from 2021-05 to 2025-12 are missing values, so those months have no CSV rows. The monitoring series really ends at 2021-04.
- On the 1° grids, Comayagua, Ocotepeque and Copán all fall in the 14.5°N row. Ocotepeque and Copán are in neighbouring columns.
- The CSV rows are the nearest grid cell to each town. No interpolation was applied.

## Added 2026-09-25: continuous monthly rainfall 1981 to 2026

| File (in rain_check/) | Source | HTTP | Size (bytes) | Rows | First | Last |
|---|---|---|---|---|---|---|
| gpcc_combined_v2020_monthly.csv | combined/precip.comb.v2020to2019-v2020monitorafter.total.nc (PSL, 1°): Full v2020 to 2019, then Monitoring v2020 | 200 (15 requests) | 157,993 | 1,620 (540 per town, 0 missing) | 1981-01 | 2025-12 |
| gpcc_1981_2026_monthly.csv | The combined file above, plus First Guess for 2026-01 to 2026-08 (built locally, no new download) | – | 159,673 | 1,644 (548 per town) | 1981-01 | 2026-08 |

- The combined file was fetched with `python3 fetch_gpcc.py log.jsonl gpcc_combined_v2020` after adding it to `DSETS` in `fetch_gpcc.py`. Its grid cells are the same as the other 1° files.
- The combined file has values after 2021-04, unlike the standalone monitoring file on PSL, which leaves those months empty.
- The combined file and First Guess agree closely over 2021-2025 (60 months per town). The correlation is 0.996 for Comayagua, 0.976 for Ocotepeque and 0.997 for Copán, and the mean monthly rain differs by 0.1, 0.5 and 2.8 mm.
- The 2026 months are First Guess, which GPCC calls a preliminary product built from fewer stations. For example, Ocotepeque 2026-08 = 3.5 mm looks too low and should be checked against a later release.
