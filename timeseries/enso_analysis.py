#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
What El Nino / La Nina did, historically, to each origin's yield, production
and (Brazil) weather, measured in the balance sheet itself.

For every country x series: anomaly = deviation of the observed value from a
linear trend fitted on the whole series, in % of the trend value (for Brazil
production/yield the ON/OFF flag is added to the trend regression so the
biennial cycle does not pollute the comparison).  Anomalies are then averaged
by the ENSO phase of the crop year (see enso.py).

Outputs (timeseries/output/enso/):
    enso_effects.csv     mean anomaly by phase, n years, years list
    enso_years.csv       crop year x series anomaly with its ENSO phase
    brazil_weather_by_phase.csv   state rainfall / temperature by phase
"""
import os
import numpy as np
import pandas as pd
from enso import enso_for_crop_year, intensity_class, ONI_SEASONS

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data", "coffee_series.csv")
EXOG = os.path.join(HERE, "data", "exog_brazil.csv")
OUT = os.path.join(HERE, "output", "enso")

SERIES = ["Production Total", "Production Arabica", "Production Robusta", "Yield", "Yield (production / bearing area)",
          "Yield (per harvested ha)", "Output per planted ha", "Area bearing", "Area total"]
EXCLUDE = {("Vietnam", "Production Arabica")}     # 17 -> 1 200 bags: % anomalies meaningless
# ENSO seasons left out of the averages on request (Brazil: the weak 2014/15 El Nino)
EXCLUDE_SEASONS = {"Brazil": {2014}}


def anomalies(y, onoff=None):
    """% deviation of each crop year from the mean of its neighbours
    (two years before and two after, at least three of them).  A local
    reference, so a series that accelerated (Uganda, Vietnam) or that has an
    ON/OFF cycle (the window holds two ON and two OFF neighbours) is not
    biased the way a global linear trend would be.  For Brazil the ON/OFF
    level difference is removed first (regression on the flag + trend)."""
    v = y.values.astype(float)
    if onoff is not None:
        t = np.arange(len(v), dtype=float)
        X = np.c_[np.ones(len(v)), t, onoff]
        beta, *_ = np.linalg.lstsq(X, v, rcond=None)
        v = v - beta[2] * (onoff - onoff.mean())       # ON years brought down, OFF years up
    out = np.full(len(v), np.nan)
    for i in range(len(v)):
        nb = [v[j] for j in (i - 2, i - 1, i + 1, i + 2) if 0 <= j < len(v)]
        if len(nb) >= 3:
            out[i] = (v[i] / np.mean(nb) - 1) * 100
    return pd.Series(out, index=y.index)


def main():
    os.makedirs(OUT, exist_ok=True)
    d = pd.read_csv(DATA)
    ex = pd.read_csv(EXOG).set_index("year")
    rows, years = [], []
    for (country, series), g in d.groupby(["country", "series"], sort=False):
        if series not in SERIES or (country, series) in EXCLUDE:
            continue
        y = g.set_index("year")["value"].sort_index()
        y = y[y.index <= 2025]                       # 2026/27 = projections
        if len(y) < 12:
            continue
        onoff = ex.loc[y.index, "onoff"].values if country == "Brazil" and ("Production" in series or "Yield" in series) else None
        a = anomalies(y, onoff)
        ph = pd.DataFrame({"anomaly_pct": a}).dropna()
        ph["season"], ph["oni"], ph["phase"], ph["strength"] = zip(*[enso_for_crop_year(country, yr) for yr in ph.index])
        ph = ph[~ph["season"].isin(EXCLUDE_SEASONS.get(country, set()))]
        ph["country"], ph["series"], ph["value"] = country, series, y.loc[ph.index].values
        ph["yoy_pct"] = (y.pct_change() * 100).loc[ph.index].values
        years.append(ph.reset_index().rename(columns={"index": "year"}))
        for phase, gg in ph.groupby("phase"):
            rows.append(dict(country=country, series=series, phase=phase, n=len(gg),
                             mean_anomaly_pct=gg["anomaly_pct"].mean(), median_anomaly_pct=gg["anomaly_pct"].median(),
                             mean_yoy_pct=gg["yoy_pct"].mean(),
                             share_below_trend=(gg["anomaly_pct"] < 0).mean() * 100,
                             years=" ".join(f"{yr}/{str(yr+1)[2:]}" for yr in gg.index)))
        # intensity classes
        ph["classe"] = [intensity_class(o, p_, se) for o, p_, se in zip(ph.oni, ph.phase, ph.season)]
        for cls, gg in ph.groupby("classe"):
            if cls == "neutre":
                continue
            rows.append(dict(country=country, series=series, phase=cls, n=len(gg),
                             mean_anomaly_pct=gg["anomaly_pct"].mean(), median_anomaly_pct=gg["anomaly_pct"].median(),
                             mean_yoy_pct=gg["yoy_pct"].mean(), share_below_trend=(gg["anomaly_pct"] < 0).mean() * 100,
                             years=" ".join(f"{yr}/{str(yr+1)[2:]}" for yr in gg.index)))
        # strong events only
        for phase in ("El Nino", "La Nina"):
            gg = ph[(ph.phase == phase) & (ph.oni.abs() >= 1.0)]
            if len(gg):
                rows.append(dict(country=country, series=series, phase=phase + " (|ONI| >= 1)", n=len(gg),
                                 mean_anomaly_pct=gg["anomaly_pct"].mean(), median_anomaly_pct=gg["anomaly_pct"].median(),
                                 mean_yoy_pct=gg["yoy_pct"].mean(), share_below_trend=(gg["anomaly_pct"] < 0).mean() * 100,
                                 years=" ".join(f"{yr}/{str(yr+1)[2:]}" for yr in gg.index)))
    from enso import ONI_SOURCE
    print("ENSO source:", ONI_SOURCE)
    eff = pd.DataFrame(rows)
    eff.to_csv(os.path.join(OUT, "enso_effects.csv"), index=False, float_format="%.2f")
    pd.concat(years).to_csv(os.path.join(OUT, "enso_years.csv"), index=False, float_format="%.3f")

    # Brazil weather by phase (state rainfall and temperature, crop years 1998/99 - 2025/26)
    w = ex.loc[ex.index <= 2025].copy()
    w["season"], w["oni"], w["phase"], _ = zip(*[enso_for_crop_year("Brazil", yr) for yr in w.index])
    w = w[~w["season"].isin(EXCLUDE_SEASONS.get("Brazil", set()))]
    cols = [c for c in w.columns if c.startswith(("rain_", "temp_"))]
    mean_all = w[cols].mean()
    w["classe"] = [intensity_class(o, p_, se) for o, p_, se in zip(w.oni, w.phase, w.season)]
    out = []
    for key in ("phase", "classe"):
      for phase, gg in w.groupby(key):
        if key == "classe" and phase == "neutre":
            continue
        rec = {"phase": phase, "n": len(gg), "years": " ".join(f"{yr}/{str(yr+1)[2:]}" for yr in gg.index)}
        for c in cols:
            rec[c] = gg[c].mean()
            rec[c + "_dev"] = gg[c].mean() - mean_all[c]
        out.append(rec)
    pd.DataFrame(out).to_csv(os.path.join(OUT, "brazil_weather_by_phase.csv"), index=False, float_format="%.2f")

    # Brazil: every El Nino / La Nina episode -> crop year N+1, by species, with the state weather of that crop year
    yrs = pd.concat(years)
    def col(series, field):
        g = yrs[(yrs.country == "Brazil") & (yrs.series == series)].set_index("year")
        return g[field] if len(g) else pd.Series(dtype=float)
    ep = []
    for season, (oni, phase, strength) in sorted(ONI_SEASONS.items()):
        cy = season + 1
        if phase == "neutral" or cy not in col("Production Total", "value").index or season in EXCLUDE_SEASONS.get("Brazil", set()):
            continue
        rec = dict(episode=f"{season}/{str(season+1)[2:]}", oni=oni, phase=phase, classe=intensity_class(oni, phase, season),
                   campagne=f"{cy}/{str(cy+1)[2:]}", year=cy, onoff="ON" if ex.loc[cy, "onoff"] == 1 else "OFF")
        for series, tag in [("Production Arabica", "arabica"), ("Production Robusta", "robusta"), ("Production Total", "total"),
                            ("Yield (production / bearing area)", "yield")]:
            rec[tag] = col(series, "value").get(cy); rec[tag + "_yoy"] = col(series, "yoy_pct").get(cy); rec[tag + "_anom"] = col(series, "anomaly_pct").get(cy)
        for c in ("rain_mg", "temp_mg", "rain_es", "temp_es", "rain_sp", "rain_pr"):
            rec[c] = ex.loc[cy, c] if cy in ex.index else np.nan
            rec[c + "_dev"] = rec[c] - mean_all[c]
        ep.append(rec)
    pd.DataFrame(ep).to_csv(os.path.join(OUT, "brazil_enso_episodes.csv"), index=False, float_format="%.2f")

    pd.set_option("display.width", 250)
    show = eff[eff.series.isin(["Production Total", "Production Arabica", "Yield", "Yield (production / bearing area)", "Output per planted ha"])]
    print(show[["country", "series", "phase", "n", "mean_anomaly_pct", "median_anomaly_pct", "share_below_trend"]].to_string(index=False))
    print()
    print(pd.DataFrame(out)[["phase", "n", "rain_mg_dev", "temp_mg_dev", "rain_es_dev", "temp_es_dev", "rain_sp_dev", "rain_pr_dev", "years"]].to_string(index=False))


if __name__ == "__main__":
    main()
