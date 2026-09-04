# Irrigation / Water Availability Index — Central Highlands (Tây Nguyên)

One page, `regions/central_highlands.html`, answering three questions for the Vietnamese
robusta belt, daily and monthly:

| Question | What the page shows | Variable |
|---|---|---|
| How much rain, and is it normal? | daily total, 30- and 90-day accumulation, gap to the 1991–2020 normal in mm / % / percentile, monthly SPI-like score | `PRECTOTCORR` |
| Is the soil actually soaked? | surface (0–5 cm), root zone (~1 m) and whole-profile wetness against the normal range for the same time of year | `GWETTOP` `GWETROOT` `GWETPROF` |
| How full is the reservoir? | a modelled slow groundwater store, as a percentile of its own 1991–2020 record, plus observed wells if you supply them | modelled from `PRECTOTCORR` + `GWETPROF` |

A fourth block covers the demand side: reference evapotranspiration ET₀ (Hargreaves),
crop demand ETc = 0.9 × ET₀, actual uptake ETa = Ks × ETc with the FAO-56 stress
coefficient, and the gap between them — the transpiration the trees could not take up.

The three water-supply terms are combined into **WAI**, a 0–100 index: `0.35 × rainfall + 0.35 × root-zone
soil + 0.30 × groundwater store`, each term a percentile of 1991–2020 for that time of
year. Below 20 = severe deficit, above 80 = surplus; 50 is exactly normal.

Ten points cover the five provinces (Đắk Lắk ×3, Đắk Nông ×2, Gia Lai ×2, Kon Tum ×1,
Lâm Đồng ×2), each selectable, plus a weighted regional line.

## Looking at a past year (2008, 2016, …)

The record starts in **1991**, so any past season is already there once the snapshot is
built. Set **Window → “One calendar year…”** and pick the year:

* the charts show that year alone against the 1991–2020 normal, daily or monthly;
* the index cards read as of 31 December of that year, not today;
* the station board switches to annual figures — rainfall and its anomaly, mean and
  lowest WAI, number of stress days, crop demand ETc, and transpiration lost to stress.

That is the answer to "how dry was 2008 for Vietnamese coffee, and where": pick 2008,
read the station board, then switch to daily to see when in the year it happened.

## Data

`build_water_index.py` downloads **NASA POWER** daily point series (free, no key,
MERRA-2 / GEOS land surface) from 1991 to today and writes one file per station:

```
python build_water_index.py              # all 10 stations -> data/water/
python build_water_index.py pleiku       # just one, manifest is kept in step
```

The script only downloads. Every index — anomalies, percentiles, the reservoir model,
the composite — is computed in `assets/wai.js`, so the stored snapshot and a live
browser fetch can never disagree.

## Updating

* **Automatic, daily.** `.github/workflows/water-index.yml` runs at 02:20 UTC
  (~09:20 Vietnam), regenerates `data/water/` and commits it if anything changed.
  Enable Actions on the repository; no secret is needed.
* **On demand, from the page.** “Update now” re-pulls the last 120 days straight from
  `power.larc.nasa.gov` in the browser and splices them onto the snapshot. Nothing is
  written back — it is a live view for whoever clicked.
* **No snapshot at all?** The page falls back to fetching the full history live, so it
  works before the first workflow run (slower: ten requests).

NASA POWER publishes 2–4 days behind real time; the page always states the last day it
actually has.

## Groundwater — read this before quoting a number

Vietnam has no open API for well levels, so the store on this page is **modelled, not
measured**: rain above 5 mm/day that falls on an already-wet profile (gate on
`GWETPROF` 0.55 → 0.90) feeds a linear store draining with a 150-day recession — the way
the basalt aquifers of the plateau actually refill. It tracks the *direction and relative
level* of storage, not a water table in metres.

To overlay real data — NAWAPI monitoring bulletins, a provincial DONRE series, or your
own farm wells — fill in `data/central_highlands_wells.js` (monthly, as a percentile of
each well's own record; the file documents the conversion from metres). The observed
series is then drawn on top of the modelled one in both views.

## Irrigation signal

Robusta here is irrigated through the Nov–Apr dry season to trigger and hold flowering.
The page accumulates `Σ max(0, 0.9 × ET₀ − rain)` from 15 November (ET₀ by Hargreaves
from POWER temperatures) and converts it to rounds of 44 mm ≈ 400 L/tree at 1,100
trees/ha. The badge turns to *round due* when root-zone wetness falls below 0.40, and to
*irrigate now* below 0.30. These thresholds are agronomic rules of thumb — tune
`W_RAIN`, `KC`, `ROUND_MM`, `TRIG_GR` and the reservoir constants at the top of
`assets/wai.js` to your own agronomy.

## Swapping in Copernicus ERA5-Land

The index does not care where the series come from: it needs daily rain, three soil
wetness levels and min/mean/max temperature. Only `build_water_index.py` would change
(ERA5-Land via the CDS API needs an account and a key, which is why POWER — already used
by the Brazil pages — is the default here). Keep the output shape:
`window.CH_WATER["<id>"] = { start, end, n, vars: { p, gt, gr, gp, t, tx, tn } }`.

## Files

```
build_water_index.py               download NASA POWER -> data/water/
data/water/manifest.js             station list + generation date
data/water/<station>.js            raw daily series, 1991 -> today
data/central_highlands_wells.js    optional observed groundwater overlay
assets/wai.js                      all the maths (baseline, anomalies, model, index)
assets/wai-charts.js               SVG charts with hover readout
regions/central_highlands.html     the page
.github/workflows/water-index.yml  daily refresh
```
