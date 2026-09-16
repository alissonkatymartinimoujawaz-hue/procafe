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
| `extract_series.py` | reads the workbook, writes the tidy dataset `data/coffee_series.csv` |
| `arma_models.py` | identifies, estimates, checks and forecasts one ARMA/ARIMA model per series |
| `data/coffee_series.csv` | one row per country × series × crop year |
| `output/models_summary.md` | **the report**: model, equation, diagnostics and forecasts per origin |
| `output/models.csv` | one row per series: order, coefficients (φ, θ, c, σ²), AIC/AICc/BIC, tests, backtest |
| `output/forecasts.csv` | point forecasts with 80 % and 95 % intervals |
| `output/fitted.csv` | observed values and one-step-ahead fitted values |
| `output/plots/<country>/<series>.png` | series + fit + forecast, ACF, PACF, residuals |
| `output/plots/<country>/_overview.png` | all series of an origin on one page |

## Run

```bash
pip install -r timeseries/requirements.txt
python timeseries/extract_series.py "Balance Sheet weather MI - Uganda Consolidated.xlsx"
python timeseries/arma_models.py                       # all origins, 5-year horizon
python timeseries/arma_models.py --country Brazil Vietnam --horizon 3
python timeseries/arma_models.py --criterion bic       # AICc (default), AIC or BIC
python timeseries/arma_models.py --last-year 2025      # drop the USDA projections of later crop years
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
