#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ARMAX models for Brazil: the ARMA of arma_models.py plus the ON/OFF biennial
flag and the weather of the balance sheet as exogenous regressors
("regression with ARMA errors", the ARMAX generalisation of the Wikipedia page):

    X_t = c + b*t + g_on*ON_t + g_rain*RAIN_{t-L} + g_temp*TEMP_{t-L} + u_t
    u_t = sum phi_i u_{t-i} + eps_t + sum theta_j eps_{t-j}

* ON_t   = 1 in an ON crop year, 0 in an OFF year (row 1 of the Brazil sheet;
           the future pattern is known: it alternates).
* RAIN   = production-weighted annual rainfall anomaly of the growing states,
           in 100 mm around the 1998-2025 mean; TEMP = weighted mean
           temperature anomaly in degC.  Lag L = 0 (weather of the crop year)
           or 1 (weather of the previous crop year, through tree condition),
           chosen by AICc.
* Every combination of regressors (none / ON / weather / both), lag and
  ARMA(p, q) order with p, q <= 2 is estimated; AICc picks the model.
* Backtest: last 3 crop years hidden, model re-estimated, forecast with the
  actual ON/OFF and weather of those years; compared with the plain ARMA
  (no regressors) and with the naive forecast.
* Forecast: ON/OFF is known; weather is not, so three scenarios are given:
  normal (anomalies 0), dry-hot (rain -1 sd, temp +1 sd) and wet-cool
  (rain +1 sd, temp -1 sd); the 80 % / 95 % bands are those of the normal
  scenario.  The fit stops at the last crop year with observed weather
  (2025/26), so the first forecast year (2026/27) can be compared with the
  USDA projection kept in the balance sheet.

    python timeseries/armax_models.py [--horizon 6] [--criterion aicc|aic|bic]

Outputs (timeseries/output/armax/): models_armax.csv, forecasts_armax.csv,
armax_summary.md, plots/*.png.
"""
import argparse
import os
import sys
import warnings
from itertools import product

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.stats.diagnostic import acorr_ljungbox

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from arma_models import DATA, slug, boundary, C_SERIES, C_FIT, C_FCST, C_TEXT, C_MUTED  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
EXOG = os.path.join(HERE, "data", "exog_brazil.csv")
OUT = os.path.join(HERE, "output", "armax")
C_DRY, C_WET = "#e34948", "#1baf7a"

# (series, weather column group).  Sheet weather is by state: Minas Gerais is
# the proxy for Cerrado Mineiro + Sul de Minas (arabica), Espirito Santo for
# Sao Mateus (robusta).  With --weather regions the NASA POWER file built by
# build_region_weather.py replaces them (see REGIONS below).
TARGETS = [
    ("Production Arabica", "mg"),
    ("Production Robusta", "es"),
    ("Production Total", "total"),
    ("Yield (production / bearing area)", "total"),
]
REGIONS = {"mg": ["cerrado_mineiro", "sul_de_minas"], "es": ["sao_mateus"],
           "total": ["cerrado_mineiro", "sul_de_minas", "sao_mateus"]}
WEATHER_REGIONS = os.path.join(HERE, "data", "weather_regions.csv")
REG_SETS = [(), ("onoff",), ("rain", "temp"), ("onoff", "rain", "temp"), ("onoff", "rain"), ("onoff", "temp")]
MAX_P = MAX_Q = 2


def fit(y, X, order, trend):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return ARIMA(y, exog=X if X is not None and X.shape[1] else None, order=order, trend=trend
                     ).fit(method_kwargs={"maxiter": 500})


def crit(res, name):
    return {"aic": res.aic, "bic": res.bic, "aicc": res.aicc}[name]


def regional_weather(path):
    """NASA POWER crop-year weather by region -> columns rain_<grp>, temp_<grp>
    (rain = Oct-Apr rainfall of the crop, temp = Oct-Apr mean temperature)."""
    w = pd.read_csv(path)
    out = pd.DataFrame(index=sorted(w["year"].unique()))
    for grp, regs in REGIONS.items():
        sub = w[w["region"].isin(regs)].groupby("year")[["rain_oct_apr_mm", "temp_oct_apr_c"]].mean()
        out[f"rain_{grp}"], out[f"temp_{grp}"] = sub["rain_oct_apr_mm"], sub["temp_oct_apr_c"]
    return out


def build_exog(ex, grp, lag):
    """Regressor table indexed by year: onoff, rain (100 mm anomaly), temp (degC anomaly)."""
    df = pd.DataFrame(index=ex.index)
    df["onoff"] = ex["onoff"].astype(float)
    rain, temp = ex[f"rain_{grp}"], ex[f"temp_{grp}"]
    base = ex.index <= 2025
    r = (rain - rain[base].mean()) / 100.0
    t = temp - temp[base].mean()
    df["rain"], df["temp"] = r.shift(lag), t.shift(lag)
    return df, dict(rain_mean=float(rain[base].mean()), rain_sd=float(rain[base].std()),
                    temp_mean=float(temp[base].mean()), temp_sd=float(temp[base].std()))


def select(y, exog_by_lag, cr):
    best, table = None, []
    for regs, lag in product(REG_SETS, (0, 1)):
        if not any(r in ("rain", "temp") for r in regs) and lag == 1:
            continue                                     # lag only matters with weather
        X = exog_by_lag[lag][list(regs)] if regs else None
        ok = y.index if X is None else X.dropna().index.intersection(y.index)
        yy = y.loc[ok]
        XX = None if X is None else X.loc[ok]
        for p, q, trend in product(range(MAX_P + 1), range(MAX_Q + 1), ("c", "ct")):
            k = p + q + len(regs) + len(trend) + 1
            if len(yy) <= k + 4:
                continue
            try:
                res = fit(yy.values, None if XX is None else XX.values, (p, 0, q), trend)
            except Exception:
                continue
            if not res.mle_retvals.get("converged", True) or boundary(res) or not np.isfinite(crit(res, cr)):
                continue
            row = dict(regressors="+".join(regs) or "none", lag=lag, p=p, q=q, trend=trend,
                       aic=res.aic, aicc=res.aicc, bic=res.bic, n=len(yy))
            table.append(row)
            if best is None or crit(res, cr) < crit(best[0], cr):
                best = (res, row, yy, XX)
    return best, pd.DataFrame(table).sort_values(cr)


def param_table(res, regs, trend):
    names = list(res.model.param_names)
    out = []
    for n, v, se, pv in zip(names, res.params, res.bse, res.pvalues):
        label = {"const": "c (intercept)", "x1": "b (trend / year)", "sigma2": "sigma2"}.get(n, n)
        # statsmodels names exog columns by position when passed as ndarray
        if n.startswith("x") and n[1:].isdigit():
            i = int(n[1:]) - 1
            k = len(trend.replace("n", "")) - 1     # 'c' -> const only ; 'ct' -> const + x1 trend
            if trend == "ct" and i == 0:
                label = "b (trend / year)"
            else:
                j = i - (1 if trend == "ct" else 0)
                label = {"onoff": "g_on (ON year, level)", "rain": "g_rain (per +100 mm)",
                         "temp": "g_temp (per +1 degC)"}[regs[j]]
        out.append(dict(param=label, value=float(v), se=float(se), p=float(pv)))
    return out


def backtest(y, X, row, h=3):
    train, test = y.iloc[:-h], y.iloc[-h:]
    Xtr = None if X is None else X.loc[train.index]
    Xte = None if X is None else X.loc[test.index]
    res = fit(train.values, None if Xtr is None else Xtr.values, (row["p"], 0, row["q"]), row["trend"])
    fc = res.get_forecast(h, exog=None if Xte is None else Xte.values).predicted_mean
    return float(np.mean(np.abs((test.values - fc) / test.values))) * 100, \
        float(np.mean(np.abs((test.values - train.iloc[-1]) / test.values))) * 100


def scenarios(sd, regs, lag, last_year, horizon, ex):
    """Future regressor paths: ON/OFF alternates from the last observed year."""
    years = np.arange(last_year + 1, last_year + 1 + horizon)
    on_last = int(ex.loc[last_year, "onoff"])
    on = np.array([(on_last + k) % 2 for k in range(1, horizon + 1)], float)
    paths = {}
    for name, (dr, dt) in {"normal": (0, 0), "dry-hot": (-1, 1), "wet-cool": (1, -1)}.items():
        df = pd.DataFrame(index=years)
        df["onoff"] = on
        df["rain"], df["temp"] = dr * sd["rain_sd"] / 100.0, dt * sd["temp_sd"]
        if lag == 1:     # first future year uses the observed weather of the last year
            r0 = (ex.loc[last_year, "rain"] - sd["rain_mean"]) / 100.0
            t0 = ex.loc[last_year, "temp"] - sd["temp_mean"]
            df.loc[years[0], ["rain", "temp"]] = [r0, t0]
        paths[name] = df[list(regs)] if regs else None
    return years, paths


def plot(series, unit, y, fitted, years, fcs, usda, info, path):
    fig, ax = plt.subplots(figsize=(11, 5.2))
    ax.plot(y.index, y.values, color=C_SERIES, lw=2, marker="o", ms=4, label="observed")
    ax.plot(fitted.index, fitted.values, color=C_FIT, lw=1.3, ls="--", label="ARMAX fit (ON/OFF + weather)")
    x0, y0 = y.index[-1], y.values[-1]
    for name, col in (("normal", C_FCST), ("dry-hot", C_DRY), ("wet-cool", C_WET)):
        f = fcs[name]
        ax.plot(np.r_[x0, years], np.r_[y0, f["forecast"]], color=col, lw=2, marker="o", ms=4,
                label=f"forecast, {name} weather")
        if name == "normal":
            ax.fill_between(np.r_[x0, years], np.r_[y0, f["lo80"]], np.r_[y0, f["hi80"]], color=col, alpha=0.18, lw=0,
                            label="80 % interval (normal)")
    if usda is not None:
        ax.scatter([years[0]], [usda], marker="D", s=40, color=C_TEXT, zorder=5, label="USDA projection in the balance sheet")
    ax.set_title(f"Brazil — {series} ({unit})   {info}", loc="left", fontsize=11, fontweight="bold")
    ax.set_xlabel("crop year (first calendar year); ON years alternate from the last observed one")
    ax.legend(loc="upper left", fontsize=8, ncol=2)
    fig.savefig(path, dpi=130, bbox_inches="tight")
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", default=DATA)
    ap.add_argument("--exog", default=EXOG)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--horizon", type=int, default=6)
    ap.add_argument("--criterion", choices=["aicc", "aic", "bic"], default="aicc")
    ap.add_argument("--weather", choices=["sheet", "regions"], default="sheet",
                    help="sheet = state weather of the balance sheet; regions = NASA POWER file "
                         "data/weather_regions.csv (Sao Mateus, Cerrado Mineiro, Sul de Minas)")
    args = ap.parse_args()
    os.makedirs(os.path.join(args.out, "plots"), exist_ok=True)

    data = pd.read_csv(args.data)
    ex = pd.read_csv(args.exog).set_index("year")
    if args.weather == "regions":
        if not os.path.exists(WEATHER_REGIONS):
            sys.exit(f"{WEATHER_REGIONS} not found: run build_region_weather.py first (needs NASA POWER access)")
        reg = regional_weather(WEATHER_REGIONS)
        ex = ex[["crop_year", "onoff"]].join(reg, how="outer")
        ex["onoff"] = ex["onoff"].ffill()          # keep alternating if the weather file goes further
    weather_years = ex.dropna(subset=["rain_total"]).index
    rows, fcs_out, L = [], [], []
    src = ("balance-sheet state weather (Minas Gerais for arabica, Espirito Santo for robusta)" if args.weather == "sheet"
           else "NASA POWER regional weather (Cerrado Mineiro + Sul de Minas for arabica, Sao Mateus for robusta)")
    L += ["# Brazil ARMAX: ON/OFF cycle and weather", "", f"Weather source: {src}.", "",
          "Regression with ARMA errors: X_t = c + b·t + g_on·ON_t + g_rain·RAIN_{t−L} + g_temp·TEMP_{t−L} + u_t, "
          "u_t ~ ARMA(p, q). RAIN and TEMP are production-weighted state anomalies (100 mm, °C) around the 1998–2025 mean; "
          f"the fit uses the crop years with observed weather ({weather_years.min()}/{weather_years.min()+1} – "
          f"{weather_years.max()}/{weather_years.max()+1}). Selection by {args.criterion.upper()} over regressor sets, weather lag (0/1) and p, q ≤ {MAX_P}.", ""]
    for series, grp in TARGETS:
        g = data[(data.country == "Brazil") & (data.series == series)].set_index("year")["value"].sort_index()
        unit = data[(data.country == "Brazil") & (data.series == series)]["unit"].iloc[0]
        usda_next = g.get(weather_years.max() + 1)
        y = g.loc[g.index.isin(weather_years)]
        exog_by_lag, sd = {}, None
        for lag in (0, 1):
            exog_by_lag[lag], sd = build_exog(ex, grp, lag)
        (res, row, yy, XX), table = select(y, exog_by_lag, args.criterion)
        regs = tuple(row["regressors"].split("+")) if row["regressors"] != "none" else ()
        params = param_table(res, regs, row["trend"])
        lb = acorr_ljungbox(res.resid, lags=[min(8, len(yy) // 4)], return_df=True)["lb_pvalue"].iloc[0]
        fitted = pd.Series(res.fittedvalues, index=yy.index)
        # backtests: ARMAX vs plain ARMA (best plain candidate of the same grid) vs naive
        bt_x, bt_naive = backtest(yy, XX, row)
        plain = table[table.regressors == "none"].iloc[0]
        bt_plain, _ = backtest(y, None, plain)
        # forecasts
        ex_full = ex.copy()
        ex_full["rain"], ex_full["temp"] = ex[f"rain_{grp}"], ex[f"temp_{grp}"]
        years, paths = scenarios(sd, regs, row["lag"], int(yy.index[-1]), args.horizon, ex_full)
        fcs = {}
        for name, Xf in paths.items():
            f = res.get_forecast(args.horizon, exog=None if Xf is None else Xf.values)
            ci80, ci95 = f.conf_int(alpha=0.2), f.conf_int(alpha=0.05)
            fcs[name] = pd.DataFrame({"year": years, "forecast": f.predicted_mean, "lo80": ci80[:, 0], "hi80": ci80[:, 1],
                                      "lo95": ci95[:, 0], "hi95": ci95[:, 1], "onoff": paths["normal"]["onoff"].values
                                      if paths["normal"] is not None and "onoff" in paths["normal"] else np.nan})
            fcs[name].insert(0, "scenario", name); fcs[name].insert(0, "series", series); fcs[name].insert(0, "country", "Brazil")
            fcs_out.append(fcs[name])
        model = f"ARMAX({row['p']},{row['q']})" if regs else f"ARMA({row['p']},{row['q']})"
        info = f"{model} + {row['regressors']} (weather lag {row['lag']}){' + trend' if row['trend']=='ct' else ''}"
        plot(series, unit, y, fitted, years, fcs, usda_next, info, os.path.join(args.out, "plots", slug(series) + ".png"))
        rec = dict(series=series, unit=unit, n=len(yy), first_year=int(yy.index[0]), last_year=int(yy.index[-1]),
                   regressors=row["regressors"], weather_lag=row["lag"], p=row["p"], q=row["q"], trend=row["trend"],
                   aicc=res.aicc, aic=res.aic, bic=res.bic, ljungbox_p=float(lb), backtest_mape_armax=bt_x,
                   backtest_mape_arma=bt_plain, backtest_mape_naive=bt_naive,
                   rain_mean_mm=sd["rain_mean"], rain_sd_mm=sd["rain_sd"], temp_mean_c=sd["temp_mean"], temp_sd_c=sd["temp_sd"],
                   usda_projection_next_year=usda_next)
        for p_ in params:
            key = p_["param"].split(" ")[0]
            rec[key], rec[key + "_se"], rec[key + "_p"] = p_["value"], p_["se"], p_["p"]
        rows.append(rec)
        print(f"{series:36s} {info:55s} backtest ARMAX {bt_x:5.1f}%  ARMA {bt_plain:5.1f}%  naive {bt_naive:5.1f}%")

        # ---- report
        L += [f"## {series} ({unit})", "",
              f"**{info}**, fitted on {len(yy)} crop years ({int(yy.index[0])}/{int(yy.index[0])+1} – {int(yy.index[-1])}/{int(yy.index[-1])+1}). "
              f"AICc {res.aicc:.1f} (plain ARMA of the same grid: {plain['aicc']:.1f}). Ljung-Box p = {lb:.2f}.", "",
              "| parameter | value | std. error | p-value |", "|---|---|---|---|"]
        for p_ in params:
            L.append(f"| {p_['param']} | {p_['value']:.4g} | {p_['se']:.3g} | {p_['p']:.3f} |")
        L += ["", f"Backtest {int(yy.index[-3])}–{int(yy.index[-1])} (MAPE): ARMAX {bt_x:.1f} % · plain ARMA {bt_plain:.1f} % · naive {bt_naive:.1f} %.",
              "", "Top 8 candidates by AICc:", "", "| regressors | lag | p | q | trend | AICc |", "|---|---|---|---|---|---|"]
        for _, t in table.head(8).iterrows():
            L.append(f"| {t.regressors} | {t.lag} | {t.p} | {t.q} | {t.trend} | {t.aicc:.1f} |")
        L += ["", f"Forecasts (ON/OFF known, weather scenarios; sd rain = {sd['rain_sd']:.0f} mm, sd temp = {sd['temp_sd']:.2f} °C):", "",
              "| crop year | ON/OFF | normal [80 %] | dry-hot | wet-cool |", "|---|---|---|---|---|"]
        for i, yr in enumerate(years):
            n_, d_, w_ = fcs["normal"].iloc[i], fcs["dry-hot"].iloc[i], fcs["wet-cool"].iloc[i]
            fmt = (lambda z: f"{z:,.0f}") if abs(n_.forecast) >= 100 else (lambda z: f"{z:.2f}")
            on = "ON" if n_.onoff == 1 else ("OFF" if n_.onoff == 0 else "")
            extra = f" (USDA in sheet: {fmt(usda_next)})" if i == 0 and usda_next is not None else ""
            L.append(f"| {yr}/{yr+1} | {on} | **{fmt(n_.forecast)}** [{fmt(n_.lo80)}; {fmt(n_.hi80)}]{extra} | {fmt(d_.forecast)} | {fmt(w_.forecast)} |")
        L.append("")

    pd.DataFrame(rows).to_csv(os.path.join(args.out, "models_armax.csv"), index=False, float_format="%.6g")
    pd.concat(fcs_out, ignore_index=True).to_csv(os.path.join(args.out, "forecasts_armax.csv"), index=False, float_format="%.6g")
    with open(os.path.join(args.out, "armax_summary.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    print(f"\nwritten: {args.out}/models_armax.csv, forecasts_armax.csv, armax_summary.md, plots/")


if __name__ == "__main__":
    main()
