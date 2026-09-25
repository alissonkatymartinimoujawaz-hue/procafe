# What drives Honduran coffee output and yield, and how to forecast 2026/27

Standard-library Python. Run in this order:

1. `analysis.py` loads the data and runs the one-driver-at-a-time tests and the six small regressions. It writes `dataset.json`, `results.json` and `analysis_output.txt`.
2. `robustness.py` runs these checks and writes `robustness.json` and `robustness_output.txt`:
   - biennial cycle vs one-off shocks;
   - yield split into production and bearing area;
   - the fertiliser chain;
   - El Niño years and the driest seasons;
   - coffee-zone temperature from ERA5-Land;
   - Holm correction;
   - forecast back-test 2000/01–2025/26, including the USDA May forecasts.
3. `nowcast.py` holds the IHCAFE monthly export profile, the 2025/26 export checkpoints and the 2026/27 scorecard text. The export checkpoints were read in the press pages saved in `raw/coffee_zones/press/`.
4. `../excel/build_yield_drivers_xlsx.py` builds `Honduras_yield_drivers_forecast.xlsx` and writes `forecast_2026_27.json`. Check the workbook with `../../indonesia/excel/verify_xlsx.py`.
5. `../slides/build_yield_deck.py` builds the 9-slide `Honduras_yield_drivers_forecast.pptx` and the `preview_yield_*.png` files.

Crop year t runs from October t to September t+1. Harvest is November t to March t+1, flowering February–April t, and fertiliser and fruit fill May–October t. The 2026/27 USDA figure is a forecast, so it is kept out of every test.

Limits:
- FAOSTAT nitrogen covers all crops and runs to 2024; FAO imputed the 2022 value.
- The heat window (Sep–Oct) was chosen after trying four windows.
- The 2026 ERA5-Land values are preliminary and stop on 18 September.
- Open-Meteo returned no ERA5-Land rain.
- The Lempira, Intibucá and Olancho points were not obtained (daily quota).
