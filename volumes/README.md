# Volumes — coffee depot / storage tracker (Minas Gerais & Espírito Santo)

Daily tracking of what enters and leaves the depots, plus the official monthly
export series for the two states. Page: `volumes.html`.

## Why a manual daily log

No public source publishes the daily in/out movements of coffee warehouses in
MG or ES. What exists publicly:

| Source | What | Cadence | Use here |
| --- | --- | --- | --- |
| Conab — Levantamento de Estoques Privados | private stocks by state and type (arabica/conilon) | once a year, reference 31 March | enter it as a `stock_bags` line for the state total |
| Comex Stat (MDIC) | exports by NCM 0901, by state and municipality of origin | monthly, ~1st of the next month | fetched automatically with `--exports` (outflow) |
| Cecafé monthly report | exports by port (Santos, Vitória, Rio) and by type | monthly, ~10th | manual reference |
| CCCV Vitória | ES exports + daily quotes | monthly / daily | manual reference for ES |
| Cooxupé harvest bulletin | harvest progress and volumes received (Sul de Minas) | weekly during harvest | enter as `inflow_bags` for a "Cooxupé" site |
| B3 certified stocks | bags certified in B3 accredited warehouses (mostly MG/SP) | daily, tiny share of real stocks | enter as a "B3 certified" site if wanted |
| SAFRAS & Mercado, Escritório Carvalhaes | commercialization pace, Santos stocks | weekly, paid | enter manually if you subscribe |

So the daily granularity comes from **your own numbers** (your depot, your
broker, cooperative bulletins). The page then aggregates by day, week and month.

## Files

```
volumes/
  daily_log.csv        <- YOU edit this every day
  build_volumes.py     <- turns the log (+ Comex Stat) into data/volumes.js
  cache/               <- downloaded Comex Stat CSVs (ignored by git)
  README.md
data/volumes.js        <- generated, loaded by volumes.html
volumes.html           <- the page (day / week / month, per site, per state, total)
assets/volumes-chart.js<- time-series chart renderer
```

## Daily routine

1. Open `volumes/daily_log.csv` and add one line per site:

   ```
   date,state,site,inflow_bags,outflow_bags,stock_bags,source,note
   2026-09-05,MG,Armazém Varginha,850,400,,broker,harvest trucks
   2026-09-05,ES,Armazém Vitória,600,1500,,CCCV,vessel loading
   ```

   * `state`: `MG` or `ES`.
   * `site`: any label, but keep it identical from one day to the next
     (it is the key that links the days together).
   * `inflow_bags` / `outflow_bags`: bags of 60 kg. Leave empty for 0.
   * `stock_bags`: optional. When you have a measured stock (physical count,
     Conab figure, cooperative statement), put it here: it resets the running
     balance. Otherwise stock = previous stock + inflow − outflow.
   * Several lines for the same site and day are allowed: flows are summed,
     the last `stock_bags` wins.
   * Delete the `source=example` lines when you start.

2. Rebuild the data file:

   ```
   python volumes/build_volumes.py
   ```

   Once a month, add the official exports of MG and ES (Comex Stat, ~100–200 MB
   per year downloaded once and cached):

   ```
   python volumes/build_volumes.py --exports
   python volumes/build_volumes.py --exports --years 2023 2024 2025 2026
   ```

3. Open `volumes.html` (or push: the site picks up `data/volumes.js`).

## What the page shows

* **Scope**: total, one state, or one site.
* **Granularity**: day, ISO week, month. Flows are summed over the period,
  stock is the value at the end of the period.
* **Range**: last 30 / 90 / 365 days or everything.
* KPI tiles: current stock, inflow and outflow over the last 7 days, net.
* Chart 1: stock (dots mark days with a measured `stock_bags`).
* Chart 2: inflow vs outflow bars.
* Table: latest raw entries.
* **Official exports (Comex Stat)**: monthly green-coffee exports from MG and
  ES in bags, and the top exporting municipalities, when `--exports` was run.

## Notes on Comex Stat

* Bulk files: `EXP_<year>.csv` (NCM level, UF of origin) and
  `EXP_<year>_MUN.csv` (SH4 level, municipality of origin), semicolon separated,
  latin-1. Documented at https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/estatisticas/base-de-dados-bruta
* "green" = NCM 0901.11 + 0901.12 (not roasted), "roasted" = 0901.21 + 0901.22,
  "total" = all of 0901. Bags = net kg / 60.
* The UF of origin in Comex Stat is the state of the *exporter's* fiscal
  origin, which is close to, but not exactly, where the coffee was stored.
