#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Huila (Colombia) - temperature and rainfall by ENSO phase, coffee years 2008/09 onward.

Reproduces the "Espirito Santo - Sao Mateus | Temperature and rainfall" slide layout
for Huila: one column per ENSO phase (El Nino / La Nina / Neutral), top row = monthly
mean temperature, bottom row = monthly rainfall, one line per coffee year plus the
phase average (bold) and the all-years average (dashed).

Data
  * Weather : NASA POWER daily T2M (degC) and PRECTOTCORR (mm/day), averaged over the
              main Huila coffee municipalities (see POINTS), aggregated to months.
  * ENSO    : NOAA CPC Oceanic Nino Index (ONI v5).

Coffee year = Colombian / FNC coffee year, October -> September.
Phase of a coffee year = mean ONI of OND, NDJ, DJF (the ENSO peak inside that year):
  >= +0.5 El Nino, <= -0.5 La Nina, otherwise Neutral.

Outputs (-> output/huila_enso/)
  huila_enso_panels.png     6-panel slide (same layout as the Sao Mateus example)
  huila_enso_anomaly.png    phase average minus all-years average, per month
  huila_enso_data.xlsx      monthly data per coffee year + phase classification + ONI

Run:
  python huila_enso.py
  python huila_enso.py --oni-file oni.ascii.txt   # use a local copy of the ONI table
"""
import os, sys, json, time, argparse, urllib.request
from datetime import date, timedelta
from collections import defaultdict

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "output", "huila_enso")

# Main coffee municipalities of Huila (lat, lon)
POINTS = [
    ("Pitalito", 1.8537, -76.0507),
    ("Garzón",   2.1959, -75.6278),
    ("La Plata", 2.3903, -75.8908),
    ("Acevedo",  1.8052, -75.8892),
    ("Gigante",  2.3868, -75.5462),
]

FIRST_YEAR = 2008                      # first coffee year = Oct 2008 -> Sep 2009
MONTHS = [10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9]
MONTH_LABELS = ["Oct", "Nov", "Dec", "Jan", "Feb", "Mar",
                "Apr", "May", "Jun", "Jul", "Aug", "Sep"]
ONI_URL = "https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt"
THRESHOLD = 0.5

PHASES = ["El Niño", "La Niña", "Neutral"]
PHASE_COLOR = {"El Niño": "#eb6834", "La Niña": "#2a78d6", "Neutral": "#52514e"}
AVG_COLOR = "#0b0b0b"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"


# ---------------------------------------------------------------- data fetch
def fetch_json(url, tries=4):
    last = None
    for k in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=120) as r:
                return r.read().decode("utf-8")
        except Exception as e:          # network hiccup -> back off and retry
            last = e
            time.sleep(3 * (k + 1))
    raise RuntimeError(f"fetch failed: {url}: {last!r}")


def fetch_point(lat, lon, start, end):
    url = ("https://power.larc.nasa.gov/api/temporal/daily/point"
           "?parameters=T2M,PRECTOTCORR&community=AG"
           f"&latitude={lat}&longitude={lon}&start={start}&end={end}&format=JSON")
    p = json.loads(fetch_json(url))["properties"]["parameter"]
    return p["T2M"], p["PRECTOTCORR"]


def monthly_weather():
    """Region-average monthly mean temp (degC) and rainfall total (mm), keyed (year, month)."""
    start = f"{FIRST_YEAR}1001"
    end = (date.today() - timedelta(days=5)).strftime("%Y%m%d")   # NASA latency
    temp = defaultdict(list)     # (y, m) -> daily values from all points
    rain = defaultdict(lambda: defaultdict(float))   # point -> (y, m) -> mm
    days = defaultdict(lambda: defaultdict(int))
    for name, lat, lon in POINTS:
        print(f"  NASA POWER: {name} ({lat}, {lon})")
        t2m, pr = fetch_point(lat, lon, start, end)
        for d, v in t2m.items():
            if v > -900:
                temp[(int(d[:4]), int(d[4:6]))].append(v)
        for d, v in pr.items():
            if v > -900:
                ym = (int(d[:4]), int(d[4:6]))
                rain[name][ym] += v
                days[name][ym] += 1
    rows = []
    for ym in sorted(temp):
        y, m = ym
        full = pd.Period(f"{y}-{m:02d}").days_in_month
        # rainfall total: average of the points' monthly totals, only for complete months
        totals = [rain[n][ym] for n, _, _ in POINTS if days[n][ym] == full]
        rows.append({
            "year": y, "month": m,
            "temp_c": round(sum(temp[ym]) / len(temp[ym]), 2),
            "rain_mm": round(sum(totals) / len(totals), 1) if totals else None,
        })
    return pd.DataFrame(rows)


def load_oni(path=None):
    """ONI table -> dict {(season 'DJF', year): anomaly}."""
    text = open(path, encoding="utf-8").read() if path else fetch_json(ONI_URL)
    oni = {}
    for line in text.splitlines():
        parts = line.split()
        if len(parts) == 4 and parts[1].isdigit():
            oni[(parts[0], int(parts[1]))] = float(parts[3])
    return oni


def classify(oni, cy):
    """Coffee year cy = Oct cy -> Sep cy+1. Uses OND(cy), NDJ(cy+1), DJF(cy+1)."""
    vals = [oni.get(("OND", cy)), oni.get(("NDJ", cy + 1)), oni.get(("DJF", cy + 1))]
    vals = [v for v in vals if v is not None]
    if not vals:
        return None, None
    peak = sum(vals) / len(vals)
    phase = "El Niño" if peak >= THRESHOLD else "La Niña" if peak <= -THRESHOLD else "Neutral"
    return phase, round(peak, 2)


# ---------------------------------------------------------------- shaping
def by_coffee_year(wx):
    """Wide tables: rows = coffee year label, columns = Oct..Sep."""
    wx = wx.copy()
    wx["cy"] = (wx.year - (wx.month < 10)).astype(int)
    wx = wx[wx.cy >= FIRST_YEAR]
    wx["label"] = wx.cy.map(lambda c: f"{c}/{str(c + 1)[-2:]}")
    out = {}
    for col in ("temp_c", "rain_mm"):
        t = wx.pivot(index="label", columns="month", values=col)
        out[col] = t.reindex(columns=MONTHS)
    cys = wx.drop_duplicates("label").set_index("label").cy
    return out, cys


# ---------------------------------------------------------------- charts
def style_axes(ax, title, unit):
    ax.set_title(title, loc="left", fontsize=10, color=INK, pad=6)
    ax.text(1.0, 1.02, unit, transform=ax.transAxes, ha="right", va="bottom",
            fontsize=8, color=INK2)
    ax.set_xticks(range(12))
    ax.set_xticklabels(MONTH_LABELS, fontsize=7, color=INK2)
    ax.tick_params(axis="y", labelsize=7, colors=INK2, length=0)
    ax.tick_params(axis="x", length=0)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)


def panels(tables, phase_of, out_png):
    fig, axes = plt.subplots(2, 3, figsize=(13.33, 7.0), sharey="row")
    fig.patch.set_facecolor("white")
    x = range(12)
    all_mean = {k: t.mean() for k, t in tables.items()}
    ylims = {"temp_c": None, "rain_mm": None}
    for j, phase in enumerate(PHASES):
        years = [y for y in tables["temp_c"].index if phase_of.get(y) == phase]
        c = PHASE_COLOR[phase]
        for i, (key, title, unit) in enumerate([("temp_c", "Mean temperature", "°C"),
                                                ("rain_mm", "Monthly rainfall", "mm")]):
            ax = axes[i, j]
            t = tables[key].loc[years]
            for y in years:
                ax.plot(x, t.loc[y].values, color=c, alpha=0.28, linewidth=1.0)
            if years:
                ax.plot(x, t.mean().values, color=c, linewidth=2.4, label=f"{phase} average")
            ax.plot(x, all_mean[key].values, color=AVG_COLOR, linewidth=1.4,
                    linestyle=(0, (4, 3)), label="All-years average")
            head = f"{phase} ({len(years)} seasons)" if i == 0 else ""
            if head:
                ax.text(0, 1.16, head, transform=ax.transAxes, fontsize=12,
                        fontweight="bold", color=INK)
            style_axes(ax, title, unit)
            if i == 1:
                ax.text(0, -0.2, "Seasons: " + ", ".join(years), transform=ax.transAxes,
                        fontsize=6.5, color=INK2, va="top", wrap=True)
                ax.legend(loc="upper right", fontsize=7, frameon=False)
    fig.suptitle("Huila — Temperature and rainfall by ENSO phase (coffee year Oct–Sep)",
                 x=0.01, ha="left", fontsize=15, fontweight="bold", color=INK)
    fig.text(0.01, 0.005,
             "Source: NASA POWER (T2M, PRECTOTCORR), mean of Pitalito, Garzón, La Plata, Acevedo, "
             "Gigante · ENSO phase from NOAA CPC ONI (mean OND–NDJ–DJF, ±0.5 °C)",
             fontsize=7, color=INK2)
    fig.tight_layout(rect=(0, 0.03, 1, 0.965), h_pad=3.2)
    fig.savefig(out_png, dpi=200)
    plt.close(fig)


def anomaly_chart(tables, phase_of, out_png):
    fig, axes = plt.subplots(1, 2, figsize=(13.33, 4.6))
    fig.patch.set_facecolor("white")
    x = list(range(12))
    w = 0.26
    specs = [("temp_c", "Temperature anomaly vs all-years average", "°C", False),
             ("rain_mm", "Rainfall anomaly vs all-years average", "%", True)]
    for ax, (key, title, unit, pct) in zip(axes, specs):
        base = tables[key].mean()
        for k, phase in enumerate(PHASES):
            years = [y for y in tables[key].index if phase_of.get(y) == phase]
            if not years:
                continue
            m = tables[key].loc[years].mean()
            d = (m / base - 1) * 100 if pct else m - base
            ax.bar([v + (k - 1) * w for v in x], d.values, width=w - 0.03,
                   color=PHASE_COLOR[phase], label=phase)
        ax.axhline(0, color=INK2, linewidth=0.8)
        style_axes(ax, title, unit)
        ax.legend(loc="upper right", fontsize=8, frameon=False, ncol=3)
    fig.suptitle("Huila — How each ENSO phase departs from normal, month by month",
                 x=0.01, ha="left", fontsize=15, fontweight="bold", color=INK)
    fig.text(0.01, 0.01, "Source: NASA POWER, NOAA CPC ONI · coffee years from 2008/09",
             fontsize=7, color=INK2)
    fig.tight_layout(rect=(0, 0.04, 1, 0.92))
    fig.savefig(out_png, dpi=200)
    plt.close(fig)


# ---------------------------------------------------------------- main
def build(wx, oni):
    os.makedirs(OUT_DIR, exist_ok=True)
    tables, cys = by_coffee_year(wx)
    phase_of, cls_rows = {}, []
    for label, cy in cys.items():
        phase, peak = classify(oni, cy)
        phase_of[label] = phase
        cls_rows.append({"coffee_year": label, "oni_peak_OND_NDJ_DJF": peak, "phase": phase,
                         "complete": bool(tables["temp_c"].loc[label].notna().all())})
    cls = pd.DataFrame(cls_rows)
    print(cls.to_string(index=False))

    panels(tables, phase_of, os.path.join(OUT_DIR, "huila_enso_panels.png"))
    anomaly_chart(tables, phase_of, os.path.join(OUT_DIR, "huila_enso_anomaly.png"))

    with pd.ExcelWriter(os.path.join(OUT_DIR, "huila_enso_data.xlsx")) as xw:
        cls.to_excel(xw, sheet_name="Classification", index=False)
        for key, name in (("temp_c", "Temperature_C"), ("rain_mm", "Rainfall_mm")):
            t = tables[key].copy()
            t.columns = MONTH_LABELS
            t.insert(0, "phase", [phase_of[y] for y in t.index])
            t.to_excel(xw, sheet_name=name)
            s = tables[key].groupby([phase_of[y] for y in tables[key].index]).mean()
            s.columns = MONTH_LABELS
            s.loc["All years"] = tables[key].mean().values
            s.round(2).to_excel(xw, sheet_name=name + "_avg")
        pd.DataFrame([{"season": s, "year": y, "oni": v} for (s, y), v in sorted(
            oni.items(), key=lambda kv: kv[0][1]) if y >= FIRST_YEAR]).to_excel(
            xw, sheet_name="ONI", index=False)
    print(f"Written to {OUT_DIR}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--oni-file", help="local copy of CPC oni.ascii.txt")
    a = ap.parse_args()
    print("Loading ONI ...")
    oni = load_oni(a.oni_file)
    print("Loading NASA POWER daily data ...")
    wx = monthly_weather()
    build(wx, oni)


if __name__ == "__main__":
    main()
