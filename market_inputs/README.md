# Market inputs (coffee balance sheet & ICE certified stocks)

`build_market.py` (repo root) reads these two files and writes `data/market.js`,
which feeds `market.html`. Only verifiable data goes in here — paste your own
series (Bloomberg/Refinitiv/ICE/USDA/Cecafé exports).

## annual.csv — one row per coffee season (Oct–Sep)
| column | unit | note |
|---|---|---|
| season | `2025/26` | |
| world_production, world_consumption, world_ending_stocks | 1000 bags (60 kg) | USDA PSD. If stocks + consumption are present, STU is computed from them |
| brazil_production, vietnam_production | 1000 bags | the main drivers of world STU |
| stu_world_pct | % | used when stocks/consumption are empty (seeded from your chart) |
| kc1_avg, df1_avg | US c/lb | season average; kc1_avg is computed from daily.csv when empty |

`python build_market.py --usda` tries to download the USDA PSD coffee CSV and
fill production / consumption / stocks / Brazil / Vietnam automatically.

## daily.csv — one row per trading day, ISO dates (`2026-10-06`)
| column | unit | note |
|---|---|---|
| kc1, kc2 | US c/lb | ICE Coffee "C" 1st and 2nd generic (KC1 Comdty, KC2 Comdty) |
| certified_bags | bags | ICE daily certified arabica stocks |
| cert_use_pct | % | optional — if empty it is computed as certified_bags / world_consumption of the season |
| fine_cup, good_cup, rio_minas, low_grade, conilon | US c/lb | Brazil internal physical prices (CEPEA / Cooxupé…), optional |
| london | US c/lb | robusta RC1 converted to c/lb (USD/t ÷ 22.0462), optional |

Empty cells are fine; every chart skips what is missing.
