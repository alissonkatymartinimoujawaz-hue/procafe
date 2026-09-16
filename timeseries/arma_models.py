#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ARMA / ARIMA time-series models of the coffee balance-sheet series
(production, area, yield, trees) for every origin, following the method of
https://en.wikipedia.org/wiki/Autoregressive_moving-average_model :

    X_t = c + eps_t + sum_{i=1..p} phi_i X_{t-i} + sum_{j=1..q} theta_j eps_{t-j}

1. Stationarity.  ARMA requires a (weakly) stationary series.  An augmented
   Dickey-Fuller test decides whether the series is differenced once first
   (X_t -> X_t - X_{t-1}); this is the ARIMA(p, 1, q) generalisation of the
   Wikipedia page.  Series that look trend-stationary may instead carry a
   deterministic linear trend (c + b*t) in the level equation.
2. Identification (Box-Jenkins).  ACF and PACF of the stationary series are
   plotted: the PACF cutting off after lag p suggests AR(p), the ACF cutting
   off after lag q suggests MA(q).
3. Order selection.  Every ARMA(p, q) with p, q <= 3 is fitted by exact maximum
   likelihood (statsmodels ARIMA, Kalman filter) and the candidate with the
   lowest information criterion is kept (AICc by default: the small-sample
   corrected AIC, ~25 observations per series; AIC or BIC on request).
4. Diagnostics.  Ljung-Box test on the residuals (no remaining autocorrelation
   => the ARMA captured the dynamics), in-sample RMSE / MAPE and an
   out-of-sample backtest: the last `--backtest` years are hidden, the model
   re-estimated, and its forecast compared with the hidden values and with a
   naive "same as last year" forecast.
5. Forecast.  `--horizon` years ahead with 80 % and 95 % prediction intervals.

    python timeseries/arma_models.py                # all origins, all series
    python timeseries/arma_models.py --country Brazil --horizon 5
    python timeseries/arma_models.py --criterion bic --last-year 2025

Outputs (timeseries/output/):
    models.csv          one row per series: order, coefficients, criteria, tests
                        (phi_i, theta_j, sigma2; c / b = intercept and trend of the
                        Wikipedia equation; mu / beta = statsmodels' mean and trend of
                        the level series, X_t = mu + beta*t + ARMA noise)
    forecasts.csv       point forecasts and intervals per series and year
    fitted.csv          observed values and in-sample one-step-ahead fits
    models_summary.md   readable report (equations, tables, forecasts)
    plots/<country>/<series>.png   series + fit + forecast, ACF, PACF, residuals
    plots/<country>/_overview.png  all series of the origin on one figure
"""
import argparse
import os
import re
import sys
import warnings

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller, acf, pacf
from statsmodels.stats.diagnostic import acorr_ljungbox

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data", "coffee_series.csv")
OUT = os.path.join(HERE, "output")

MIN_OBS = 10          # below this an ARMA fit is meaningless
MAX_P = MAX_Q = 3     # order grid
MAX_PQ = 4            # parsimony: p + q <= 4
ADF_ALPHA = 0.05
ROOT_TOL = 1.02       # AR/MA root modulus below this = parameter on the unit-circle boundary

# palette (dataviz reference palette, light mode)
C_SERIES, C_FIT, C_FCST, C_TEXT, C_MUTED, C_GRID = "#2a78d6", "#52514e", "#eb6834", "#0b0b0b", "#52514e", "#e6e5e1"
plt.rcParams.update({
    "font.size": 9, "axes.edgecolor": C_GRID, "axes.labelcolor": C_MUTED, "xtick.color": C_MUTED,
    "ytick.color": C_MUTED, "axes.grid": True, "grid.color": C_GRID, "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False, "figure.facecolor": "#fcfcfb",
    "axes.facecolor": "#fcfcfb", "legend.frameon": False, "axes.titlecolor": C_TEXT,
})


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


# --------------------------------------------------------------------------- data
def load_series(path, country=None, last_year=None):
    df = pd.read_csv(path)
    if country:
        wanted = {c.lower() for c in country}
        df = df[df["country"].str.lower().isin(wanted)]
    if last_year:
        df = df[df["year"] <= last_year]
    # every origin stops at its last production year: later cells are stray formulas
    last_prod = df[df["variable"] == "production"].groupby("country")["year"].max()
    df = df[df["year"] <= df["country"].map(last_prod).fillna(df["year"])]
    out = []
    for (country, series), g in df.groupby(["country", "series"], sort=False):
        g = g.sort_values("year")
        years = np.arange(g["year"].min(), g["year"].max() + 1)
        y = pd.Series(g["value"].values, index=g["year"].values, dtype=float).reindex(years)
        n_gap = int(y.isna().sum())
        if n_gap:
            y = y.interpolate()                    # linear fill of interior gaps
        out.append(dict(country=country, series=series, variable=g["variable"].iloc[0],
                        unit=g["unit"].iloc[0], source=g["source"].iloc[0], y=y, n_gap=n_gap))
    return out


# --------------------------------------------------------------------------- modelling
def adf_p(x):
    x = np.asarray(x, float)
    if len(x) < 8 or np.std(x) == 0:
        return np.nan
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            return float(adfuller(x, regression="c", autolag="AIC")[1])
    except Exception:
        return np.nan


def fit_arima(y, order, trend):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        res = ARIMA(y.values, order=order, trend=trend).fit(method_kwargs={"maxiter": 500})
    return res


def criterion(res, name):
    return {"aic": res.aic, "bic": res.bic, "aicc": res.aicc}[name]


def boundary(res):
    """True when an AR or MA root sits (numerically) on the unit circle."""
    roots = np.r_[res.arroots, res.maroots]
    return len(roots) > 0 and np.min(np.abs(roots)) < ROOT_TOL


def select_model(y, d, crit):
    """Grid over (p, q) and over the deterministic part; return the best fit.

    Candidates with an AR or MA root on the unit circle are discarded: an MA
    root at -1 after differencing means the series was over-differenced, an
    AR root at 1 without differencing means it should have been differenced.
    """
    trends = ["c", "ct"] if d == 0 else ["n", "t"]     # 't' with d=1 is a drift
    best, table = None, []
    for trend in trends:
        for p in range(MAX_P + 1):
            for q in range(MAX_Q + 1):
                if p + q > MAX_PQ:
                    continue
                k = p + q + len(trend.replace("n", "")) + 1
                if len(y) - d <= k + 3:                 # not enough data for the parameters
                    continue
                try:
                    res = fit_arima(y, (p, d, q), trend)
                except Exception:
                    continue
                if not res.mle_retvals.get("converged", True):
                    continue
                if not np.isfinite(criterion(res, crit)):
                    continue
                row = dict(p=p, d=d, q=q, trend=trend, aic=res.aic, aicc=res.aicc, bic=res.bic,
                           boundary=boundary(res))
                table.append(row)
                if row["boundary"]:
                    continue
                if best is None or criterion(res, crit) < criterion(best[0], crit):
                    best = (res, row)
    return best, pd.DataFrame(table)


def coef_dict(res):
    names = list(res.model.param_names)
    out = {}
    for n, v in zip(names, res.params):
        if n.startswith("ar.L"):
            out["phi" + n[4:]] = v
        elif n.startswith("ma.L"):
            out["theta" + n[4:]] = v
        elif n == "const":
            out["mu"] = v            # statsmodels: X_t = mu + beta*t + u_t, u_t ~ ARMA
        elif n in ("x1", "drift"):
            out["beta"] = v
        elif n == "sigma2":
            out["sigma2"] = v
    return out


def wiki_intercept(row, coefs):
    """Convert statsmodels' 'regression with ARMA errors' parametrisation
    (X_t = mu + beta*t + u_t, u_t = sum phi_i u_{t-i} + eps_t + sum theta_j eps_{t-j})
    into the intercept form of the Wikipedia page
    (X_t = c + b*t + sum phi_i X_{t-i} + eps_t + ...).  Adds c / b to coefs."""
    phis = [coefs.get(f"phi{i}", 0.0) for i in range(1, row["p"] + 1)]
    s1, s2 = 1.0 - sum(phis), sum(i * f for i, f in enumerate(phis, 1))
    mu, beta = coefs.get("mu"), coefs.get("beta")
    if row["d"] == 0:
        if mu is not None:
            coefs["c"] = mu * s1 + (beta or 0.0) * s2
        if beta is not None:
            coefs["b"] = beta * s1
    else:                                            # drift: constant of the differenced equation
        if beta is not None:
            coefs["c"] = beta * s1
    return coefs


def equation(row, coefs):
    """Wikipedia-style equation of the chosen model (t = 1 for the first observed year)."""
    x = "X_t" if row["d"] == 0 else "∇X_t"
    terms = []                                       # (sign, text)
    if "c" in coefs:
        terms.append((np.sign(coefs["c"]), f"{abs(coefs['c']):.4g}"))
    if "b" in coefs:                                 # linear trend (d=0)
        terms.append((np.sign(coefs["b"]), f"{abs(coefs['b']):.4g}·t"))
    for i in range(1, row["p"] + 1):
        v = coefs[f"phi{i}"]
        terms.append((np.sign(v), f"{abs(v):.3f}·{x.replace('_t', f'_{{t-{i}}}')}"))
    terms.append((1, "ε_t"))
    for j in range(1, row["q"] + 1):
        v = coefs[f"theta{j}"]
        terms.append((np.sign(v), f"{abs(v):.3f}·ε_{{t-{j}}}"))
    rhs = ""
    for k, (sg, txt) in enumerate(terms):
        if k == 0:
            rhs += ("−" if sg < 0 else "") + txt
        else:
            rhs += (" − " if sg < 0 else " + ") + txt
    eq = f"{x} = {rhs}"
    if row["d"] == 1:
        eq += "   with ∇X_t = X_t − X_{t-1}"
    return eq


def backtest(y, row, h):
    """Hide the last h points, refit the chosen order, compare with the truth."""
    if len(y) - h < MIN_OBS:
        return np.nan, np.nan
    train, test = y.iloc[:-h], y.iloc[-h:]
    try:
        res = fit_arima(train, (row["p"], row["d"], row["q"]), row["trend"])
        fc = res.get_forecast(h).predicted_mean
    except Exception:
        return np.nan, np.nan
    mape = float(np.mean(np.abs((test.values - fc) / test.values))) * 100
    naive = float(np.mean(np.abs((test.values - train.iloc[-1]) / test.values))) * 100
    return mape, naive


def model_one(item, crit, horizon, bt_h):
    y = item["y"]
    n = len(y)
    info = dict(country=item["country"], series=item["series"], variable=item["variable"],
                unit=item["unit"], source=item["source"], n_obs=n, first_year=int(y.index[0]),
                last_year=int(y.index[-1]), n_interpolated=item["n_gap"])
    if n < MIN_OBS:
        info["status"] = f"too short ({n} obs < {MIN_OBS}): not modelled"
        return info, None
    if np.std(y.values) / max(abs(np.mean(y.values)), 1e-9) < 1e-3:
        info["status"] = "constant series: no dynamics to model, forecast = last value"
        return info, None

    p_level = adf_p(y.values)
    p_diff = adf_p(np.diff(y.values))
    d = 0 if (np.isfinite(p_level) and p_level < ADF_ALPHA) else 1
    info.update(adf_p_level=p_level, adf_p_diff=p_diff)

    best, grid = select_model(y, d, crit)
    d_reason = f"ADF p = {p_level:.3f} on levels"
    if d == 1 and len(grid) and grid.sort_values(crit).iloc[0]["boundary"] and \
            grid.sort_values(crit).iloc[0]["q"] > 0:
        # the preferred differenced model has an MA root on the unit circle:
        # classic sign of over-differencing -> model the level series instead
        best0, grid0 = select_model(y, 0, crit)
        if best0 is not None:
            d, best, grid = 0, best0, grid0
            d_reason += "; d=1 gave an MA unit root (over-differencing) -> level model kept"
    info["d_reason"] = d_reason
    if best is None:
        info["status"] = "no ARMA candidate converged"
        return info, None
    res, row = best
    coefs = wiki_intercept(row, coef_dict(res))
    lb_lag = max(1, min(10, n // 4))
    lb = acorr_ljungbox(res.resid[d:], lags=[lb_lag], return_df=True)
    fc = res.get_forecast(horizon)
    ci80, ci95 = fc.conf_int(alpha=0.20), fc.conf_int(alpha=0.05)
    years = np.arange(y.index[-1] + 1, y.index[-1] + 1 + horizon)
    fitted = pd.Series(res.fittedvalues, index=y.index)
    if d:
        fitted.iloc[0] = np.nan
    resid = (y - fitted)
    bt_mape, naive_mape = backtest(y, row, bt_h)

    info.update(status="ok", p=row["p"], d=d, q=row["q"], trend=row["trend"],
                model=f"ARIMA({row['p']},{d},{row['q']})" if d else f"ARMA({row['p']},{row['q']})",
                aic=res.aic, aicc=res.aicc, bic=res.bic, loglik=res.llf,
                ljungbox_lag=lb_lag, ljungbox_p=float(lb["lb_pvalue"].iloc[0]),
                rmse_insample=float(np.sqrt(np.nanmean(resid.values ** 2))),
                mape_insample=float(np.nanmean(np.abs(resid.values / y.values))) * 100,
                backtest_h=bt_h, backtest_mape_arma=bt_mape, backtest_mape_naive=naive_mape,
                equation=equation(row, coefs), **{k: v for k, v in coefs.items()})
    detail = dict(res=res, row=row, coefs=coefs, fitted=fitted, resid=resid, grid=grid,
                  forecast=pd.DataFrame({"year": years, "forecast": fc.predicted_mean,
                                         "lo80": ci80[:, 0], "hi80": ci80[:, 1],
                                         "lo95": ci95[:, 0], "hi95": ci95[:, 1]}),
                  d=d)
    return info, detail


# --------------------------------------------------------------------------- plots
def plot_series(item, info, detail, path):
    y = item["y"]
    fig = plt.figure(figsize=(11, 7.2))
    gs = fig.add_gridspec(2, 3, height_ratios=[1.6, 1], hspace=0.45, wspace=0.35)
    ax = fig.add_subplot(gs[0, :])
    ax.plot(y.index, y.values, color=C_SERIES, lw=2, marker="o", ms=4, label="observed")
    if detail:
        f = detail["forecast"]
        ax.plot(detail["fitted"].index, detail["fitted"].values, color=C_FIT, lw=1.4, ls="--",
                label="one-step-ahead fit")
        xs = np.r_[y.index[-1], f["year"].values]
        ax.fill_between(xs, np.r_[y.values[-1], f["lo95"]], np.r_[y.values[-1], f["hi95"]],
                        color=C_FCST, alpha=0.12, lw=0, label="95 % interval")
        ax.fill_between(xs, np.r_[y.values[-1], f["lo80"]], np.r_[y.values[-1], f["hi80"]],
                        color=C_FCST, alpha=0.22, lw=0, label="80 % interval")
        ax.plot(xs, np.r_[y.values[-1], f["forecast"].values], color=C_FCST, lw=2, marker="o",
                ms=4, label=f"{info['model']} forecast")
        for yr, v in zip(f["year"], f["forecast"]):
            ax.annotate(f"{v:,.0f}" if abs(v) >= 100 else f"{v:.2f}", (yr, v), textcoords="offset points",
                        xytext=(0, 7), ha="center", fontsize=7.5, color=C_TEXT)
        ax.set_title(f"{item['country']} — {item['series']} ({item['unit']})   {info['model']}"
                     f"{', trend' if info['trend'] == 'ct' else (', drift' if info['trend'] == 't' else '')}",
                     loc="left", fontsize=11, fontweight="bold")
        ax.text(0.0, -0.16, info["equation"], transform=ax.transAxes, fontsize=8, color=C_MUTED)
    else:
        ax.set_title(f"{item['country']} — {item['series']} ({item['unit']})   {info['status']}",
                     loc="left", fontsize=11, fontweight="bold")
    ax.legend(loc="upper left", fontsize=8, ncol=3)
    ax.set_xlabel("crop year (first calendar year)")

    x = y.values if not detail else (np.diff(y.values) if detail["d"] else y.values)
    nl = max(1, min(10, len(x) // 2 - 1))
    for k, (name, fn) in enumerate([("ACF", acf), ("PACF", pacf)]):
        axk = fig.add_subplot(gs[1, k])
        try:
            vals = fn(x, nlags=nl, **({"method": "ywm"} if name == "PACF" else {}))
        except Exception:
            vals = np.full(nl + 1, np.nan)
        lags = np.arange(len(vals))
        axk.vlines(lags[1:], 0, vals[1:], color=C_SERIES, lw=2)
        axk.scatter(lags[1:], vals[1:], color=C_SERIES, s=14, zorder=3)
        band = 1.96 / np.sqrt(len(x))
        axk.axhspan(-band, band, color=C_FIT, alpha=0.10, lw=0)
        axk.axhline(0, color=C_MUTED, lw=0.8)
        axk.set_ylim(-1.05, 1.05)
        axk.set_title(f"{name} of {'∇X' if (detail and detail['d']) else 'X'} (identification)", loc="left", fontsize=9)
        axk.set_xlabel("lag (years)")
    ax3 = fig.add_subplot(gs[1, 2])
    if detail:
        r = detail["resid"].dropna()
        ax3.bar(r.index, r.values, color=C_FIT, width=0.7)
        ax3.axhline(0, color=C_MUTED, lw=0.8)
        ax3.set_title(f"residuals ε_t   Ljung-Box p = {info['ljungbox_p']:.2f}", loc="left", fontsize=9)
    else:
        ax3.axis("off")
    fig.savefig(path, dpi=130, bbox_inches="tight")
    plt.close(fig)


def plot_overview(country, entries, path):
    entries = [e for e in entries]
    n = len(entries)
    ncol = 3
    nrow = int(np.ceil(n / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(13, 3.1 * nrow), squeeze=False)
    for ax, (item, info, detail) in zip(axes.flat, entries):
        y = item["y"]
        ax.plot(y.index, y.values, color=C_SERIES, lw=1.8, marker="o", ms=3)
        if detail:
            f = detail["forecast"]
            xs = np.r_[y.index[-1], f["year"].values]
            ax.fill_between(xs, np.r_[y.values[-1], f["lo80"]], np.r_[y.values[-1], f["hi80"]],
                            color=C_FCST, alpha=0.2, lw=0)
            ax.plot(xs, np.r_[y.values[-1], f["forecast"].values], color=C_FCST, lw=1.8, marker="o", ms=3)
            ax.set_title(f"{item['series']} ({item['unit']}) — {info['model']}", loc="left", fontsize=9)
        else:
            ax.set_title(f"{item['series']} ({item['unit']}) — not modelled", loc="left", fontsize=9)
    for ax in list(axes.flat)[n:]:
        ax.axis("off")
    fig.suptitle(f"{country}: observed (blue) and ARMA forecasts with 80 % interval (orange)",
                 x=0.01, ha="left", fontsize=12, fontweight="bold")
    fig.tight_layout()
    fig.savefig(path, dpi=120, bbox_inches="tight")
    plt.close(fig)


# --------------------------------------------------------------------------- report
def write_report(rows, forecasts, crit, horizon, path):
    L = ["# ARMA models of the coffee balance sheet", "",
         f"Order selected by **{crit.upper()}** over p, q ≤ {MAX_P} (p + q ≤ {MAX_PQ}); "
         f"d = 1 when the ADF test does not reject a unit root at {ADF_ALPHA:.0%}; forecast horizon {horizon} years.",
         "Equation notation follows the Wikipedia page: X_t is the series, ε_t white noise, φ the AR and θ the MA coefficients; "
         "in a linear trend b·t, t = 1 for the first observed year of the series.",
         "Backtest MAPE = mean absolute percentage error over the last hidden years (model re-estimated without them); "
         "'naive' = forecasting last observed value.", ""]
    for country, g in rows.groupby("country", sort=False):
        L += [f"## {country}", "", "| series | unit | years | n | model | equation | AICc | Ljung-Box p | backtest MAPE (ARMA / naive) |",
              "|---|---|---|---|---|---|---|---|---|"]
        for _, r in g.iterrows():
            if r["status"] != "ok":
                L.append(f"| {r['series']} | {r['unit']} | {r['first_year']}–{r['last_year']} | {r['n_obs']} | – | {r['status']} | | | |")
                continue
            trend = " + trend" if r["trend"] == "ct" else (" + drift" if r["trend"] == "t" else "")
            bt = (f"{r['backtest_mape_arma']:.1f} % / {r['backtest_mape_naive']:.1f} %"
                  if np.isfinite(r["backtest_mape_arma"]) else "n/a")
            L.append(f"| {r['series']} | {r['unit']} | {r['first_year']}–{r['last_year']} | {r['n_obs']} | {r['model']}{trend} | "
                     f"`{r['equation']}` | {r['aicc']:.1f} | {r['ljungbox_p']:.2f} | {bt} |")
        fg = forecasts[forecasts["country"] == country]
        if len(fg):
            years = sorted(fg["year"].unique())
            L += ["", "Forecasts (point estimate, 80 % interval):", "",
                  "| series | " + " | ".join(f"{y}/{y + 1}" for y in years) + " |",
                  "|---|" + "---|" * len(years)]
            for series, sg in fg.groupby("series", sort=False):
                sg = sg.set_index("year")
                cells = []
                for y in years:
                    if y in sg.index:
                        v, lo, hi = sg.loc[y, ["forecast", "lo80", "hi80"]]
                        fmt = (lambda z: f"{z:,.0f}") if abs(v) >= 100 else (lambda z: f"{z:.2f}")
                        cells.append(f"**{fmt(v)}** [{fmt(lo)}; {fmt(hi)}]")
                    else:
                        cells.append("")
                L.append(f"| {series} | " + " | ".join(cells) + " |")
        L.append("")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(L))


# --------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", default=DATA)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--country", nargs="*", help="only these origins (default: all)")
    ap.add_argument("--horizon", type=int, default=5, help="forecast years (default 5)")
    ap.add_argument("--backtest", type=int, default=3, help="years hidden for the backtest (default 3)")
    ap.add_argument("--criterion", choices=["aicc", "aic", "bic"], default="aicc")
    ap.add_argument("--last-year", type=int, help="ignore observations after this crop year")
    args = ap.parse_args()

    items = load_series(args.data, args.country, args.last_year)
    if not items:
        sys.exit("no series found")
    os.makedirs(os.path.join(args.out, "plots"), exist_ok=True)
    rows, fcs, fits, by_country = [], [], [], {}
    for item in items:
        info, detail = model_one(item, args.criterion, args.horizon, args.backtest)
        rows.append(info)
        by_country.setdefault(item["country"], []).append((item, info, detail))
        d = os.path.join(args.out, "plots", slug(item["country"]))
        os.makedirs(d, exist_ok=True)
        plot_series(item, info, detail, os.path.join(d, slug(item["series"]) + ".png"))
        tag = info["model"] if detail else "-"
        print(f"{item['country']:22s} {item['series']:36s} n={info['n_obs']:3d}  {tag:14s} {info['status']}")
        if detail:
            f = detail["forecast"].copy()
            f.insert(0, "series", item["series"]); f.insert(0, "country", item["country"])
            f["unit"] = item["unit"]; f["model"] = info["model"]
            fcs.append(f)
            fits.append(pd.DataFrame({"country": item["country"], "series": item["series"], "year": item["y"].index,
                                      "observed": item["y"].values, "fitted": detail["fitted"].values}))
    for country, entries in by_country.items():
        plot_overview(country, entries, os.path.join(args.out, "plots", slug(country), "_overview.png"))

    rows = pd.DataFrame(rows)
    forecasts = pd.concat(fcs, ignore_index=True) if fcs else pd.DataFrame(columns=["country", "series", "year"])
    rows.to_csv(os.path.join(args.out, "models.csv"), index=False, float_format="%.6g")
    forecasts.to_csv(os.path.join(args.out, "forecasts.csv"), index=False, float_format="%.6g")
    if fits:
        pd.concat(fits, ignore_index=True).to_csv(os.path.join(args.out, "fitted.csv"), index=False, float_format="%.6g")
    write_report(rows, forecasts, args.criterion, args.horizon, os.path.join(args.out, "models_summary.md"))
    print(f"\nwritten: {args.out}/models.csv, forecasts.csv, fitted.csv, models_summary.md, plots/")


if __name__ == "__main__":
    main()
