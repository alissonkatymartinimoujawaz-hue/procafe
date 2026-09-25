# Excel exports

`Sumatra_weather_by_ENSO_season.xlsx`: monthly mean temperature and rainfall by July–June season, grouped El Niño / La Niña / Neutral, for the South Sumatra 3-town mean (Pagar Alam, Lahat, Muaradua) and for each of the 5 robusta towns. Same 20 seasons as the São Mateus chart (2005/06–2024/25), plus 2025/26 and 2026/27 (to August 2026) outside the averages.

- Weather: NASA POWER daily (`../raw/nasa_power_daily_*.json`), 1 Jul 2005 → 19 Sep 2026, in the `Daily` sheet. `Monthly` sums or averages it with SUMIFS / AVERAGEIFS formulas.
- ENSO: NOAA CPC ONI (`../raw/oni.ascii.txt`, last period JJA 2026). An episode needs at least 5 consecutive overlapping periods with the rounded ONI at ≥ +0.5 or ≤ −0.5. Each season takes the episode status of its Nov–Jan (NDJ) period. The formulas are in `ENSO_monthly` and `ENSO_seasons`.
- Checks: the `Checks` sheet. `verify_xlsx.py` re-reads the file, recomputes every formula and compares it with the value stored in the file.

Rebuild with `python3 build_weather_xlsx.py`, then run `python3 verify_xlsx.py Sumatra_weather_by_ENSO_season.xlsx`. Both use the standard library only (`xlsxw.py` writes the file).
