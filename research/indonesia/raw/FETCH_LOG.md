# Fetch log: raw data for the Indonesia robusta analysis

Fetched on 2026-09-24 (UTC) from the cloud session's egress proxy.

## Connectivity check (one request per host, 20 s timeout, no retries)

| Host | Result |
|---|---|
| power.larc.nasa.gov | 200 OK |
| www.cpc.ncep.noaa.gov | 200 OK |
| psl.noaa.gov | 200 OK |
| fenixservices.fao.org | **BLOCKED**: proxy CONNECT returned 403. Skipped. |
| thedocs.worldbank.org | 301, reachable |
| www.bom.gov.au | 403 without a browser User-Agent; 200 with one. The site blocks bots; the proxy does not block it. |
| www.worldbank.org (extra check) | **BLOCKED**: proxy CONNECT returned 403 |

## Files

| File | URL | HTTP | Size (bytes) | Coverage / notes |
|---|---|---|---|---|
| nasa_power_daily_pagar_alam.json | https://power.larc.nasa.gov/api/temporal/daily/point?parameters=PRECTOTCORR,T2M,T2M_MAX,T2M_MIN,RH2M&community=AG&latitude=-4.0217&longitude=103.2528&start=19810101&end=20260919&format=JSON | 200 | 1,398,159 | 1981-01-01 → 2026-09-19, 16,698 days, one request |
| nasa_power_daily_lahat.json | same, lat -3.7864, lon 103.5428 | 200 | 1,397,868 | 1981-01-01 → 2026-09-19 |
| nasa_power_daily_muaradua.json | same, lat -4.5330, lon 104.0700 | 200 | 1,396,912 | 1981-01-01 → 2026-09-19 |
| nasa_power_daily_liwa.json | same, lat -5.0333, lon 104.0667 | 200 | 1,396,636 | 1981-01-01 → 2026-09-19 |
| nasa_power_daily_kepahiang.json | same, lat -3.6500, lon 102.5800 | 200 | 1,398,018 | 1981-01-01 → 2026-09-19 |
| oni.ascii.txt | https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt | 200 | 23,000 | DJF 1950 → JJA 2026 (last ONI +1.80) |
| cpc_ensodisc.html | https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso_advisory/ensodisc.shtml | 200 | 13,506 | Current discussion; the alert status is "El Niño Advisory" |
| dmi.had.long.data | https://psl.noaa.gov/gcos_wgsp/Timeseries/Data/dmi.had.long.data | 200 | 19,861 | Jan 1870 → May 2026 (Jun–Dec 2026 = -9999); file created 25 Jul 2026 |
| bom_climate_driver_update.html | https://www.bom.gov.au/climate/enso/ | 200 (with a browser UA) | 191,984 | Page is titled "Southern hemisphere monitoring". The page may load its current values with JavaScript, so the saved HTML may not contain them. |
| worldbank_cmo_monthly.xlsx | https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Historical-Data-Monthly.xlsx | 200 | 586,735 | Pink Sheet "Updated on September 02, 2026"; latest month 2026M08. The landing page www.worldbank.org is blocked, so the link came from a web search. |

## Not fetched

- **FAOSTAT (faostat_indonesia_crops.csv)**: fenixservices.fao.org is blocked by the egress proxy (CONNECT 403), so no request was made. To get it, allow the host or download the file by hand from https://www.fao.org/faostat/en/#data/QCL (area 101 Indonesia; items 656, 254, 836, 661, 689, 56; elements 5312, 5510; 1990→latest).
