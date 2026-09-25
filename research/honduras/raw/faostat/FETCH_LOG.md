# FAOSTAT fetch log — Honduras (Area Code 95)

- Fetched: 2026-09-25 with `python3 research/common/fetch_faostat_country.py 95 research/honduras/raw/faostat honduras`
- Source: FAOSTAT bulk downloads, normalized CSVs, `https://bulks-faostat.fao.org/production/`
- Only rows with `Area Code == 95` are kept. The zips were deleted after filtering.
- The script ran twice because `price_indices` failed on the first run. Both runs gave the same results. `fetch_log.jsonl` holds the machine log for both runs, so each entry appears twice.

| File | Source zip (URL = base + name) | HTTP | Zip size (bytes) | Rows kept | Years |
|---|---|---|---|---|---|
| `honduras_qcl.csv` | `Production_Crops_Livestock_E_All_Data_(Normalized).zip` | 200 | 33,921,825 | 17,837 | 1961–2024 |
| `honduras_prices.csv` | `Prices_E_All_Data_(Normalized).zip` | 200 | 11,683,910 | 5,412 | 1991–2025 |
| `honduras_landuse.csv` | `Inputs_LandUse_E_All_Data_(Normalized).zip` | 200 | 2,971,760 | 1,676 | 1961–2025 |
| `honduras_fert_nutrient.csv` | `Inputs_FertilizersNutrient_E_All_Data_(Normalized).zip` | 200 | 2,030,532 | 1,101 | 1961–2024 |
| `honduras_fert_product.csv` | `Inputs_FertilizersProduct_E_All_Data_(Normalized).zip` | 200 | 2,786,645 | 1,309 | 2002–2024 |
| `honduras_exchange.csv` | `Exchange_rate_E_All_Data_(Normalized).zip` | 200 | 1,274,157 | 671 | 1970–2026 |
| `honduras_employment.csv` | `Employment_Indicators_Agriculture_E_All_Data_(Normalized).zip` | 200 | 2,369,575 | 1,831 | 1985–2025 |
| *(none)* | `Prices_Indices_E_All_Data_(Normalized).zip` | **403 Forbidden** (twice) | — | 0 | — |

## Failure

- `Prices_Indices_E_All_Data_(Normalized).zip` returned HTTP 403 on both runs. A `curl -I` also returned 403, as did the alternative name `Price_Indices_...`. The bucket most likely has no file under this name, since FAO's storage returns 403 for missing keys. It was left as is. The coffee producer price index (2014–2016 = 100) is still available in `honduras_prices.csv`.

## Series checks

**`honduras_qcl.csv` — Item "Coffee, green"**
- Area harvested (ha): 64 years, 1961–2024
- Production (t): 64 years, 1961–2024
- Yield (kg/ha): 64 years, 1961–2024

**`honduras_prices.csv` — Item "Coffee, green"**
- Producer Price (LCU/tonne): 21 annual values plus 9 monthly rows, 1991–2024
- Producer Price (USD/tonne): 21 annual values, 1991–2024
- Producer Price (SLC/tonne): 21 values, 1991–2024
- Producer Price Index (2014–2016 = 100): 35 values, 1991–2025
- **Gap:** there are no LCU or USD producer prices for **2009–2021**. The annual series covers 1991–2008 and 2022–2024.

**`honduras_landuse.csv` — Element "Area", unit 1000 ha**
- Forest land: 1990–2025 (36 years)
- Permanent crops: 1961–2024 (64)
- Cropland: 1961–2024 (64)
- Permanent meadows and pastures: 1961–2024 (64)
- Temporary meadows and pastures: 2001–2024 (24)

**`honduras_fert_nutrient.csv` — Element "Agricultural Use", unit t**
- Nutrient nitrogen N (total): 1961–2024 (64)
- Nutrient phosphate P2O5 (total): 1961–2024 (64)
- Nutrient potash K2O (total): 1961–2024 (64)

**Other files**
- `honduras_fert_product.csv`: fertiliser products by type, such as urea, DAP and AN. It holds import and export quantities and values plus agricultural use, 2002–2024.
- `honduras_exchange.csv`: Lempira (HNL) per USD, as annual and monthly values, 1970–2026.
- `honduras_employment.csv`: employment in agriculture and agrifood systems, including ILO modelled estimates, share of total employment and agriculture value added per worker (constant 2015 USD), 1985–2025.
