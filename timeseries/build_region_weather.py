#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fetch NASA POWER daily weather for the three Brazilian coffee regions asked for
in the forecast (Sao Mateus / ES for robusta, Cerrado Mineiro and Sul de Minas
for arabica) and aggregate it by CROP YEAR for armax_models.py --weather regions.

Run it from a machine with internet access (same API as build_data.py):

    python timeseries/build_region_weather.py            # 1997 -> today
    python timeseries/armax_models.py --weather regions

Output -> timeseries/data/weather_regions.csv, one row per region x crop year:
    year            first calendar year of the USDA marketing year (July-June);
                    the harvest of crop year Y/Y+1 takes place May-Sep of Y
    rain_sep_nov_mm rainfall Sep-Nov of Y-1  (flowering / fruit set)
    rain_oct_apr_mm rainfall Oct Y-1 - Apr Y (fruit development, the wet season)
    rain_total_mm   rainfall Jul Y-1 - Jun Y
    temp_oct_apr_c  mean temperature Oct Y-1 - Apr Y
    temp_jun_aug_c  mean temperature Jun-Aug of Y-1 (winter before flowering:
                    frost / heat stress window)
    tmin_jun_aug_c  lowest daily minimum Jun-Aug of Y-1 (frost indicator)
    dry_days_aug_sep  days with < 1 mm in Aug-Sep of Y-1 (pre-flowering drought)
Each region is the mean of its listed points.
"""
import csv
import json
import os
import sys
import time
import urllib.request
from collections import defaultdict
from datetime import date, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "data", "weather_regions.csv")

REGIONS = {
    "sao_mateus":      [("Sao Mateus", -18.716, -39.859), ("Nova Venecia", -18.716, -40.400),
                        ("Jaguare", -18.906, -40.075)],
    "cerrado_mineiro": [("Patrocinio", -18.944, -46.993), ("Araguari", -18.647, -48.187),
                        ("Monte Carmelo", -18.724, -47.499)],
    "sul_de_minas":    [("Varginha", -21.567, -45.406), ("Carmo de Minas", -22.175, -45.151),
                        ("Boa Esperanca", -21.066, -45.577), ("Guape", -20.734, -46.085)],
}
START_YEAR = 1997          # first crop year needs Jul 1997


def fetch(lat, lon, start, end, tries=4):
    url = ("https://power.larc.nasa.gov/api/temporal/daily/point"
           "?parameters=T2M,T2M_MIN,PRECTOTCORR&community=AG"
           f"&latitude={lat}&longitude={lon}&start={start}&end={end}&format=JSON")
    last = None
    for k in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=180) as r:
                p = json.load(r)["properties"]["parameter"]
            return p["T2M"], p["T2M_MIN"], p["PRECTOTCORR"]
        except Exception as e:                                   # noqa
            last = e
            time.sleep(5 * (k + 1))
    raise RuntimeError(f"NASA POWER failed for {lat},{lon}: {last}")


def crop_year_stats(t2m, tmin, pr):
    """Aggregate daily dicts {YYYYMMDD: value} by crop year (see module docstring)."""
    buckets = defaultdict(lambda: defaultdict(list))
    for k, p in pr.items():
        y, m = int(k[:4]), int(k[4:6])
        t, tn = t2m.get(k, -999.0), tmin.get(k, -999.0)
        if p is None or p < -900 or t < -900:
            continue
        # Jul-Dec of calendar year y belong to crop year y+1 ; Jan-Jun to crop year y
        cy = y + 1 if m >= 7 else y
        b = buckets[cy]
        b["rain_total"].append(p)
        if m in (9, 10, 11):
            b["rain_sep_nov"].append(p)
        if m >= 10 or m <= 4:
            b["rain_oct_apr"].append(p); b["temp_oct_apr"].append(t)
        if m in (6, 7, 8):
            b["temp_jun_aug"].append(t)
            if tn > -900:
                b["tmin_jun_aug"].append(tn)
        if m in (8, 9):
            b["dry_aug_sep"].append(1 if p < 1.0 else 0)
    rows = {}
    for cy, b in buckets.items():
        if len(b["rain_total"]) < 360:          # incomplete crop year
            continue
        rows[cy] = dict(rain_sep_nov_mm=sum(b["rain_sep_nov"]), rain_oct_apr_mm=sum(b["rain_oct_apr"]),
                        rain_total_mm=sum(b["rain_total"]),
                        temp_oct_apr_c=sum(b["temp_oct_apr"]) / len(b["temp_oct_apr"]),
                        temp_jun_aug_c=sum(b["temp_jun_aug"]) / len(b["temp_jun_aug"]),
                        tmin_jun_aug_c=min(b["tmin_jun_aug"]) if b["tmin_jun_aug"] else None,
                        dry_days_aug_sep=sum(b["dry_aug_sep"]))
    return rows


def main():
    start = f"{START_YEAR}0701"
    end = (date.today() - timedelta(days=4)).strftime("%Y%m%d")
    fields = ["region", "year", "crop_year", "rain_sep_nov_mm", "rain_oct_apr_mm", "rain_total_mm",
              "temp_oct_apr_c", "temp_jun_aug_c", "tmin_jun_aug_c", "dry_days_aug_sep"]
    out = []
    for region, points in REGIONS.items():
        per_point = []
        for name, lat, lon in points:
            print(f"{region:16s} {name:15s} {lat:8.3f} {lon:8.3f} ...", end=" ", flush=True)
            t2m, tmin, pr = fetch(lat, lon, start, end)
            stats = crop_year_stats(t2m, tmin, pr)
            per_point.append(stats)
            print(f"{len(stats)} crop years")
        years = sorted(set.intersection(*(set(s) for s in per_point)))
        for cy in years:
            rec = {"region": region, "year": cy, "crop_year": f"{cy}/{cy + 1}"}
            for f in fields[3:]:
                vals = [s[cy][f] for s in per_point if s[cy][f] is not None]
                rec[f] = round(sum(vals) / len(vals), 2) if vals else None
            out.append(rec)
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(out)
    print(f"\n{len(out)} rows -> {OUT}")


if __name__ == "__main__":
    main()
