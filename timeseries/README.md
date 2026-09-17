# Coffee balance sheet — ARMA time-series models

Python implementation of the autoregressive–moving-average model described on
<https://en.wikipedia.org/wiki/Autoregressive_moving-average_model>, applied to
every origin of the *Balance Sheet* workbook (Brazil, Colombia, Honduras,
Ethiopia, Peru, Indonesia, Vietnam, Uganda) and to every annual series it
contains: **production**, **area**, **yield** and **trees**.

Goal: understand how each series moves (trend, alternation, persistence) and
forecast the next crop years with an honest uncertainty band.

## Files

| file | role |
|---|---|
| `extract_series.py` | reads the workbook, writes the tidy dataset `data/coffee_series.csv` and the Brazil ON/OFF + weather table `data/exog_brazil.csv` |
| `arma_models.py` | identifies, estimates, checks and forecasts one ARMA/ARIMA model per series |
| `armax_models.py` | Brazil only: ARMA + ON/OFF flag + weather as exogenous regressors (ARMAX), weather scenarios |
| `build_region_weather.py` | fetches NASA POWER weather for São Mateus, Cerrado Mineiro and Sul de Minas by crop year (run it where NASA POWER is reachable) |
| `data/coffee_series.csv` | one row per country × series × crop year |
| `output/models_summary.md` | **the report**: model, equation, diagnostics and forecasts per origin |
| `output/models.csv` | one row per series: order, coefficients (φ, θ, c, σ²), AIC/AICc/BIC, tests, backtest |
| `output/forecasts.csv` | point forecasts with 80 % and 95 % intervals |
| `output/fitted.csv` | observed values and one-step-ahead fitted values |
| `output/plots/<country>/<series>.png` | series + fit + forecast, ACF, PACF, residuals |
| `output/plots/<country>/_overview.png` | all series of an origin on one page |
| `output/armax/armax_summary.md` | Brazil ARMAX report: coefficients, candidate table, scenario forecasts |
| `output/armax/models_armax.csv`, `forecasts_armax.csv` | same, machine-readable (one forecast row per scenario × year) |

## Run

```bash
pip install -r timeseries/requirements.txt
python timeseries/extract_series.py "Balance Sheet weather MI - Uganda Consolidated.xlsx"
python timeseries/arma_models.py                       # all origins, 5-year horizon
python timeseries/arma_models.py --country Brazil Vietnam --horizon 3
python timeseries/arma_models.py --criterion bic       # AICc (default), AIC or BIC
python timeseries/arma_models.py --last-year 2025      # drop the USDA projections of later crop years
python timeseries/armax_models.py                      # Brazil: ON/OFF + weather (state weather of the sheet)
python timeseries/build_region_weather.py              # needs internet: NASA POWER for the three regions
python timeseries/armax_models.py --weather regions    # then: regional weather instead of state weather
```

The workbook is not stored in the repository; re-run the first command whenever
the balance sheet changes.

## Method (mapping to the Wikipedia page)

The ARMA(p, q) model of the page is

    X_t = c + ε_t + Σ_{i=1..p} φ_i X_{t−i} + Σ_{j=1..q} θ_j ε_{t−j}

with ε_t white noise. `arma_models.py` follows the page section by section:

1. **Stationarity.** ARMA needs a weakly stationary series. An augmented
   Dickey–Fuller test is run on each series; when a unit root cannot be
   rejected the series is differenced once (∇X_t = X_t − X_{t−1}) and the ARMA
   is fitted to ∇X_t. That is the ARIMA(p, 1, q) generalisation mentioned on
   the page. If the differenced model then shows an MA root on the unit circle
   (the classic sign of over-differencing) the level series is modelled instead,
   with a deterministic linear trend when it improves the criterion.
2. **Identification (Box–Jenkins).** ACF and PACF of the stationary series are
   plotted under each chart, with the ±1.96/√n band: a PACF that cuts off after
   lag p points to AR(p), an ACF that cuts off after lag q to MA(q).
3. **Estimation.** Every candidate with p, q ≤ 3 (p + q ≤ 4) is estimated by
   exact maximum likelihood (statsmodels `ARIMA`, Kalman filter). Candidates
   that do not converge or whose AR/MA roots sit on the unit circle are dropped.
4. **Choice of p and q.** The page recommends the AIC or BIC; the default here
   is the AICc (AIC corrected for small samples: each series has only 15–32
   points). `--criterion aic|bic` switches.
5. **Diagnostics.** Ljung–Box test on the residuals (p > 0.05: no
   autocorrelation left, the ARMA captured the dynamics), in-sample RMSE/MAPE,
   and a **backtest**: the last 3 crop years are hidden, the model is
   re-estimated without them and its forecast is compared with the hidden values
   and with the naive "same as last year" forecast. When the naive MAPE is as
   good as the ARMA MAPE, the series is essentially a random walk and the ARMA
   adds no information beyond the last value.
6. **Forecast.** 5 years ahead with 80 % and 95 % prediction intervals.

The equations in the report use the intercept form of the page. statsmodels
estimates the equivalent "mean + trend + ARMA noise" form; both sets of
coefficients are in `output/models.csv` (`c`, `b` vs `mu`, `beta`).

## Brazil: ON/OFF cycle and weather (ARMAX)

`armax_models.py` is the ARMAX generalisation of the page: the same ARMA noise,
plus regressors whose future values are known or can be set as scenarios.

    X_t = c + b·t + g_on·ON_t + g_rain·RAIN_{t−L} + g_temp·TEMP_{t−L} + u_t,   u_t ~ ARMA(p, q)

* **ON/OFF**: the flag written in the header of the Brazil sheet (ON = high
  year of the biennial cycle). The future pattern is known (it alternates), so
  the forecast keeps the full ON/OFF amplitude instead of damping it as a plain
  ARMA does. The effect is large and significant: about +7.4 million bags of
  arabica in an ON year, p < 0.001, and the AICc drops from 503 to 494.
* **Weather**: the balance sheet only has annual state averages (rainfall and
  temperature for Minas Gerais, Espírito Santo, São Paulo, Paraná, others).
  Minas Gerais stands in for Cerrado Mineiro + Sul de Minas (arabica) and
  Espírito Santo for São Mateus (robusta). At this resolution the weather adds
  nothing the criterion keeps: rainfall has the right sign (about +450 to
  +500 bags per +100 mm) but p ≈ 0.15 to 0.6, temperature nothing. What drives
  a coffee crop is seasonal (rain at flowering in Sep–Nov, the Oct–Apr wet
  season, winter frost, Aug–Sep drought) and regional, hence the next point.
* **Regional weather**: `build_region_weather.py` fetches NASA POWER daily data
  for São Mateus, Cerrado Mineiro and Sul de Minas (three or four points each)
  and aggregates them by crop year into the seasonal indicators above. NASA
  POWER is not reachable from the environment where this was written, so the
  script is tested on synthetic data only; run it from your own machine (like
  `build_data.py`) and then `armax_models.py --weather regions`.
* **Scenarios**: ON/OFF is known; weather is not. Forecasts are given for
  normal weather (anomaly 0), dry-hot (rain −1 sd, temp +1 sd) and wet-cool
  (+1 sd, −1 sd). With the state weather not selected, the three scenarios
  coincide; they separate once a weather regressor is kept.
* The ARMAX fit stops at 2025/26 (last crop year with observed weather), so its
  first forecast year 2026/27 can be compared with the USDA projection stored
  in the sheet (arabica: model 49.9 vs USDA 47.5 million bags).

## Data corrections applied

* **Brazil production rows 27–28** ("Production Arabica / Robusta (1000 60KG
  bags)") are shifted one crop year late for 2001/02–2008/09: their
  "2003/2004 (OFF)" column holds the 2002/03 record crop (53.6 million bags in
  USDA terms) and so on until 2009/10, where both blocks realign. The
  "Total Production" block (rows 54–56, million bags) matches the USDA
  marketing-year series throughout and is the one used here (×1000). Brazil
  yield is recomputed from it as production / bearing area.

## What the data allowed, and what to watch

* **Ethiopia and Peru are skipped.** In the workbook those two sheets are an
  exact copy of the Honduras block (same area, production and yield numbers).
  Modelling them would only repeat the Honduras results under another name.
  Fill the sheets with Ethiopian and Peruvian data and re-run: they are already
  configured with the same row layout.
* **Brazil's biennial cycle** shows up directly in the models: arabica
  production gives ARIMA(1,1,0) with φ₁ ≈ −0.61, i.e. a change in one year is
  followed by a change of the opposite sign the next year (ON/OFF years).
* **Vietnam** has the most informative dynamics: production, bearing area and
  yield all carry a significant drift and the ARMA backtest beats the naive
  forecast by a wide margin.
* **Colombia (USDA)** area and tree series are step functions that USDA keeps
  constant for years; the forecasts are flat and the intervals are tight only
  because the source is, not because the physical stock is.
* **Uganda** bearing area, non-bearing area and yield per harvested hectare
  exist only from 2019/20 (8 points): not modelled. Total area and output per
  planted hectare are.
* **Trees** are only available for Brazil, Colombia, Honduras and Indonesia;
  the Vietnam and Uganda sheets carry none.
* The last crop-year columns of each sheet (2025/26, 2026/27) are USDA
  estimates or projections, not final numbers. Use `--last-year` to exclude them
  if you want models fitted on realised harvests only.
* Interior gaps (e.g. Vietnam area 2012–2014) are linearly interpolated; the
  count is in `models.csv` (`n_interpolated`).
* With 20–30 annual points, ARMA forecasts are wide and the 80 % interval is the
  realistic planning range. The point forecast should be read together with the
  backtest columns of the report.

## ENSO analysis and per-origin Word reports

* `enso.py` classifies every crop year by the El Niño / La Niña episode that
  drives it (NOAA CPC episode list; drop the official ONI or RONI table in
  `data/oni.csv`, columns `year, DJF … NDJ`, and it is used instead).
  Brazil, Peru, Indonesia and Vietnam are driven by the episode peaking the
  winter before their harvest; Colombia, Honduras, Ethiopia and Uganda by the
  episode developing during their growing year.
* `enso_analysis.py` measures, in the balance sheet, the mean deviation of
  yield and production from the neighbouring crop years by ENSO phase (Brazil
  ON/OFF removed first), and the Brazil state weather by phase →
  `output/enso/`.
* `report_docx.py` (+ `report_figures.py`) writes one Word report per origin in
  `output/reports/`: causal chain, crop calendar, balance-sheet facts, yield
  drivers, measured ENSO effects, forecast and the implication of the current
  El Niño. Ethiopia and Peru reports carry the structure and climatology only
  (their sheets are copies of Honduras).
