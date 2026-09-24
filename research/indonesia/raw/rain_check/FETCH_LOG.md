# FETCH_LOG — independent monthly rainfall check (rain_check)

Fetched 2026-09-24 from a cloud container, Python standard library only (`fetch_gpcc.py` in this folder can repeat it:
`python3 fetch_gpcc.py log.jsonl` run from this directory).
Target: monthly rainfall from 1981 at 5 towns, from a source independent of NASA POWER.

## 1. CHIRPS v2.0 via the IRI Data Library: FAILED (blocked by network policy)

| # | URL | Result |
|---|-----|--------|
| 1 | `https://iridl.ldeo.columbia.edu/SOURCES/.UCSB/.CHIRPS/.v2p0/.monthly/.global/.precipitation/X/103.2528/VALUE/Y/-4.0217/VALUE/T/(Jan%201981)/(Dec%202026)/RANGE/data.csv` | `CONNECT tunnel failed, response 403`: the environment's egress proxy refused the connection |
| 2 | (5 s later) `.../X/103.2528/VALUE/Y/-4.0217/VALUE/data.csv` | same 403 from the egress proxy |
| – | `https://data.chc.ucsb.edu/products/CHIRPS-2.0/` (CHIRPS origin, checked once) | same 403 from the egress proxy |

The server never received these requests; the proxy blocks these hosts. No CHIRPS or CHIRP-prelim data were obtained.

## 2. GPCC via NOAA PSL THREDDS/OPeNDAP: OK

Host `psl.noaa.gov`. Steps: read `.dds`/`.das` (and the `gpcc/`, `monitor/`, `combined/`, `first_guess/` catalogs),
then `.ascii?lat,lon,time` to get the coordinate arrays, then `precip[t0:t1][lat box][lon box]`. The box is the smallest one
holding the nearest grid cell of every town. Units: mm per month (`precip` units "mm", monthly totals).
Missing value -9.96921E36 is dropped: those months are absent from the CSV.

Notes on failures along the way:
- One request for all 468 months at a single 0.25° cell (`full_v2020 ...ascii?precip[1080:1547][376][413]`) failed twice
  (urllib error, then curl `502 Proxy Error` after 60 s: the PSL front end timed out while reading many time steps).
  Fix: split time into chunks of 60 months (~17 s each). Every chunked request then returned HTTP 200 on the first try.
- A bare `curl` URL containing `[...]` needs `-g`.

### Products and coverage

| File | PSL dataset | Grid | Months in file | Notes |
|------|-------------|------|----------------|-------|
| `gpcc_full_v2020_monthly.csv` | `Datasets/gpcc/full_v2020/precip.mon.total.0.25x0.25.v2020.nc` | 0.25° | 1981-01 to 2019-12 (468/468 per town) | GPCC Full Data v2020, the reference quality-controlled gauge analysis; the file ends in 2019 |
| `gpcc_monitor_v2020_monthly.csv` | `Datasets/gpcc/monitor/precip.monitor.mon.total.1x1.v2020.nc` | 1° | 1982-01 to 2021-04 (472 valid; 2021-05 to 2025-12 are fill values in the PSL file, 56 months) | GPCC Monitoring Product; the time axis runs to 2025-12 but the data stop at 2021-04 |
| `gpcc_first_guess_monthly.csv` | `Datasets/gpcc/first_guess/precip.first.mon.total.1x1.nc` | 1° | 2012-01 to 2026-08 (176/176) | GPCC First Guess: near-real-time, SYNOP-only, least quality control. It is the only GPCC source for 2021-05 onward (including 2022) |

The other PSL entries are not used: `combined/` splices full and monitor data, and `full_v2018`/`full_v7` are older versions.

### Grid cell per town (nearest cell centre)

| Town | Lat, Lon | 0.25° cell (full_v2020) [ilat, ilon] | 1° cell (monitor, first guess) [ilat, ilon] |
|------|----------|-----------------------------|-------------------------------|
| pagar_alam | -4.0217, 103.2528 | -4.125, 103.375 [376, 413] | -4.5, 103.5 [94, 103] |
| lahat | -3.7864, 103.5428 | -3.875, 103.625 [375, 414] | -3.5, 103.5 [93, 103] |
| muaradua | -4.533, 104.07 | -4.625, 104.125 [378, 416] | -4.5, 104.5 [94, 104] |
| liwa | -5.0333, 104.0667 | -5.125, 104.125 [380, 416] | -5.5, 104.5 [95, 104] |
| kepahiang | -3.65, 102.58 | -3.625, 102.625 [374, 410] | -3.5, 102.5 [93, 102] |

Caveats: a 1° cell is about 110 km across and averages over mountains and lowland. Liwa's 1° cell is centred at -5.5, 104.5,
south-east of the town, and Pagar Alam's is centred at -4.5, 103.5. Both towns lie almost halfway between two cell centres.
Prefer the 0.25° full_v2020 series wherever it covers the period.

### Agreement between products (monthly values, same town)

| Pair | Overlap | Correlation r (range across towns) |
|------|---------|--------------------|
| full_v2020 vs monitor | 1982-01 to 2019-12 (456 months) | 0.74 to 0.84 |
| full_v2020 vs first guess | 2012-01 to 2019-12 (96 months) | 0.91 to 0.94 |
| monitor vs first guess | 2012-01 to 2021-04 (112 months) | 0.98 to 0.99 |

## 3. CPC Global Unified Gauge-Based (0.5° daily): not fetched

The brief says to use CPC only if sources 1 and 2 both fail. GPCC worked, so CPC was skipped.
CPC would be the natural gauge-based cross-check for 2020 onward, where only the GPCC first guess is available.

## Request log (every HTTP request made by fetch_gpcc.py in the final run)

| URL | Status | Bytes | Seconds |
|-----|--------|-------|---------|
| `…/gpcc/full_v2020/precip.mon.total.0.25x0.25.v2020.nc.ascii?lat,lon,time` | 200 | 32730 | 0.7 |
| `…/gpcc/full_v2020/precip.mon.total.0.25x0.25.v2020.nc.ascii?precip[1080:1139][374:380][410:416]` | 200 | 27407 | 17.0 |
| `…/gpcc/full_v2020/precip.mon.total.0.25x0.25.v2020.nc.ascii?precip[1140:1199][374:380][410:416]` | 200 | 27576 | 17.0 |
| `…/gpcc/full_v2020/precip.mon.total.0.25x0.25.v2020.nc.ascii?precip[1200:1259][374:380][410:416]` | 200 | 27041 | 17.7 |
| `…/gpcc/full_v2020/precip.mon.total.0.25x0.25.v2020.nc.ascii?precip[1260:1319][374:380][410:416]` | 200 | 27277 | 17.1 |
| `…/gpcc/full_v2020/precip.mon.total.0.25x0.25.v2020.nc.ascii?precip[1320:1379][374:380][410:416]` | 200 | 27386 | 17.1 |
| `…/gpcc/full_v2020/precip.mon.total.0.25x0.25.v2020.nc.ascii?precip[1380:1439][374:380][410:416]` | 200 | 27260 | 17.0 |
| `…/gpcc/full_v2020/precip.mon.total.0.25x0.25.v2020.nc.ascii?precip[1440:1499][374:380][410:416]` | 200 | 27037 | 17.3 |
| `…/gpcc/full_v2020/precip.mon.total.0.25x0.25.v2020.nc.ascii?precip[1500:1547][374:380][410:416]` | 200 | 21599 | 19.3 |
| `…/gpcc/monitor/precip.monitor.mon.total.1x1.v2020.nc.ascii?lat,lon,time` | 200 | 8545 | 5.5 |
| `…/gpcc/monitor/precip.monitor.mon.total.1x1.v2020.nc.ascii?precip[0:119][93:95][102:104]` | 200 | 12784 | 0.8 |
| `…/gpcc/monitor/precip.monitor.mon.total.1x1.v2020.nc.ascii?precip[120:239][93:95][102:104]` | 200 | 12673 | 1.4 |
| `…/gpcc/monitor/precip.monitor.mon.total.1x1.v2020.nc.ascii?precip[240:359][93:95][102:104]` | 200 | 12715 | 0.9 |
| `…/gpcc/monitor/precip.monitor.mon.total.1x1.v2020.nc.ascii?precip[360:479][93:95][102:104]` | 200 | 13005 | 1.0 |
| `…/gpcc/monitor/precip.monitor.mon.total.1x1.v2020.nc.ascii?precip[480:527][93:95][102:104]` | 200 | 7160 | 0.7 |
| `…/gpcc/first_guess/precip.first.mon.total.1x1.nc.ascii?lat,lon,time` | 200 | 5373 | 1.2 |
| `…/gpcc/first_guess/precip.first.mon.total.1x1.nc.ascii?precip[0:119][93:95][102:104]` | 200 | 12936 | 0.8 |
| `…/gpcc/first_guess/precip.first.mon.total.1x1.nc.ascii?precip[120:175][93:95][102:104]` | 200 | 6102 | 0.9 |

(`…/gpcc/` = `https://psl.noaa.gov/thredds/dodsC/Datasets/gpcc/`. Manual `curl` checks of `.dds`, `.das` and `catalog.xml` all returned 200.)
## June–October totals (mm), computed from the CSVs

| Town | Source | 2010 | 2011 | 2015 | 2022 |
|------|--------|-----:|-----:|-----:|-----:|
| pagar_alam | full_v2020 0.25° | 1314 | 617 | 201 | – |
| pagar_alam | monitor 1° | 1253 | 473 | 218 | – |
| pagar_alam | first guess 1° | – | – | 246 | 1443 |
| lahat | full_v2020 0.25° | 1316 | 645 | 203 | – |
| lahat | monitor 1° | 1414 | 589 | 280 | – |
| lahat | first guess 1° | – | – | 302 | 1547 |
| muaradua | full_v2020 0.25° | 1008 | 390 | 262 | – |
| muaradua | monitor 1° | 1115 | 403 | 244 | – |
| muaradua | first guess 1° | – | – | 248 | 853 |
| liwa | full_v2020 0.25° | 1083 | 402 | 262 | – |
| liwa | monitor 1° | 1034 | 336 | 229 | – |
| liwa | first guess 1° | – | – | 257 | 720 |
| kepahiang | full_v2020 0.25° | 1441 | 820 | 238 | – |
| kepahiang | monitor 1° | 1452 | 614 | 318 | – |
| kepahiang | first guess 1° | – | – | 359 | 1935 |
