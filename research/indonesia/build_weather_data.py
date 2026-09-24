#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Build research/indonesia/weather_data.js from the raw files in research/indonesia/raw/:
  nasa_power_daily_<town>.json   NASA POWER daily (PRECTOTCORR, T2M, T2M_MAX)
  oni.ascii.txt                  NOAA CPC ONI
  dmi.had.long.data              NOAA PSL DMI (HadISST)
and the USDA PSD coffee zip (downloaded, or research/indonesia/raw/psd_coffee.csv if present).

Output: window.SUMATRA_WEATHER = {towns, monthly, triggers, oni, dmi, usda_robusta, generated}
monthly[town] = {"YYYY-MM": [rain_mm, t2m, tmax, complete(0/1), days_with_data, rh2m]}
triggers[town] = {"YYYY": "YYYY-MM-DD" | null}: first blossom-trigger rain between June and October,
  i.e. a day with > 10 mm preceded by 11 days averaging < 0.6 mm/day (Alvim 1960; Crisosto et al. 1992).
"""
import csv, io, json, os, sys, urllib.request, zipfile
from datetime import date, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
OUT = os.path.join(HERE, "weather_data.js")
FILL = -999.0
TOWNS = [
    ("pagar_alam", "Pagar Alam", "Sumatra du Sud", -4.0217, 103.2528),
    ("lahat", "Lahat", "Sumatra du Sud", -3.7864, 103.5428),
    ("muaradua", "Muaradua", "Sumatra du Sud (OKU Selatan)", -4.5330, 104.0700),
    ("liwa", "Liwa", "Lampung (Lampung Barat)", -5.0333, 104.0667),
    ("kepahiang", "Kepahiang", "Bengkulu", -3.6500, 102.5800),
]
SEASONS = ["DJF", "JFM", "FMA", "MAM", "AMJ", "MJJ", "JJA", "JAS", "ASO", "SON", "OND", "NDJ"]


def monthly(path):
    p = json.load(open(path))["properties"]["parameter"]
    acc = {}
    rh = p.get("RH2M", {})
    for k, v in p["PRECTOTCORR"].items():
        ym = f"{k[:4]}-{k[4:6]}"
        a = acc.setdefault(ym, {"r": 0.0, "n": 0, "t": [], "x": [], "h": []})
        if v != FILL:
            a["r"] += v; a["n"] += 1
        t, x, h = p["T2M"].get(k, FILL), p["T2M_MAX"].get(k, FILL), rh.get(k, FILL)
        if t != FILL: a["t"].append(t)
        if x != FILL: a["x"].append(x)
        if h != FILL: a["h"].append(h)
    out = {}
    for ym, a in sorted(acc.items()):
        if not a["n"]:
            continue
        y, m = int(ym[:4]), int(ym[5:])
        dim = (date(y + (m == 12), m % 12 + 1, 1) - date(y, m, 1)).days
        out[ym] = [round(a["r"], 1),
                   round(sum(a["t"]) / len(a["t"]), 2) if a["t"] else None,
                   round(sum(a["x"]) / len(a["x"]), 2) if a["x"] else None,
                   1 if a["n"] >= dim - 1 else 0,
                   a["n"],
                   round(sum(a["h"]) / len(a["h"]), 1) if a["h"] else None]
    return out


def triggers(path, first_year=1981):
    """First blossom-trigger day per year (June-October): > 10 mm after 11 days averaging < 0.6 mm."""
    r = json.load(open(path))["properties"]["parameter"]["PRECTOTCORR"]
    last = max(k for k, v in r.items() if v != FILL)
    out = {}
    for y in range(first_year, int(last[:4]) + 1):
        d, found = date(y, 6, 1), None
        while d <= date(y, 10, 31) and d.strftime("%Y%m%d") <= last:
            v = r.get(d.strftime("%Y%m%d"), FILL)
            if v > 10:
                prev = [r.get((d - timedelta(days=i)).strftime("%Y%m%d"), FILL) for i in range(1, 12)]
                if FILL not in prev and sum(prev) / 11 < 0.6:
                    found = d.isoformat()
                    break
            d += timedelta(days=1)
        out[str(y)] = found
    return out


def oni():
    out = {}
    for line in open(os.path.join(RAW, "oni.ascii.txt")):
        s = line.split()
        if len(s) == 4 and s[0] in SEASONS:
            out[f"{s[1]}-{SEASONS.index(s[0]) + 1:02d}"] = float(s[3])
    return out


def dmi():
    out = {}
    path = os.path.join(RAW, "dmi.had.long.data")
    if not os.path.exists(path):
        return out
    for line in open(path):
        s = line.split()
        if len(s) == 13 and s[0].isdigit():
            for m, v in enumerate(s[1:], 1):
                v = float(v)
                if v > -99:
                    out[f"{s[0]}-{m:02d}"] = round(v, 3)
    return out


def usda():
    local = os.path.join(RAW, "psd_coffee.csv")
    if os.path.exists(local):
        rows = csv.DictReader(open(local))
    else:
        data = urllib.request.urlopen("https://apps.fas.usda.gov/psdonline/downloads/psd_coffee_csv.zip", timeout=180).read()
        z = zipfile.ZipFile(io.BytesIO(data))
        rows = csv.DictReader(io.TextIOWrapper(z.open([n for n in z.namelist() if n.endswith(".csv")][0]), encoding="utf-8"))
    return {int(r["Market_Year"]): float(r["Value"]) for r in rows
            if r["Country_Name"] == "Indonesia" and r["Attribute_Description"] == "Robusta Production"}


def main():
    towns, mon, trig = [], {}, {}
    for tid, name, prov, lat, lon in TOWNS:
        f = os.path.join(RAW, f"nasa_power_daily_{tid}.json")
        if os.path.exists(f):
            mon[tid] = monthly(f)
            trig[tid] = triggers(f)
            towns.append({"id": tid, "name": name, "prov": prov, "lat": lat, "lon": lon})
    if not mon:
        sys.exit("no NASA POWER files in " + RAW)
    last = max(max(m) for m in mon.values())
    data = {"generated": date.today().isoformat(), "last_month": last, "towns": towns, "monthly": mon, "triggers": trig,
            "oni": oni(), "dmi": dmi(), "usda_robusta": usda()}
    with open(OUT, "w") as f:
        f.write("// AUTO-GENERATED by build_weather_data.py (NASA POWER, NOAA CPC ONI, NOAA PSL DMI, USDA PSD)\n")
        f.write("window.SUMATRA_WEATHER = " + json.dumps(data, separators=(",", ":")) + ";\n")
    print("wrote", OUT, os.path.getsize(OUT), "bytes; towns:", [t["id"] for t in towns], "last month:", last)


if __name__ == "__main__":
    main()
