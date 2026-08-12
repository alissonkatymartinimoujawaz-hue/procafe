#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Generate real weather-graph data for the coffee-region website from NASA POWER.

For each city (lat/lon) it fetches daily T2M (mean air temp, degC) and
PRECTOTCORR (corrected precipitation, mm/day) from 1981 to the latest available
day, then computes, PER YEAR (plus a 1981..last-full-year baseline):
  * temp     : monthly mean temperature
  * precip   : monthly rainfall totals            (accumulated derived in page)
  * water    : DAILY Thornthwaite-Mather soil-water extract (mm), real fluctuations
  * decadal  : 10-day net balance P - PET (mm)     -> "SALDO LÍQUIDO" bar chart

Output -> weather_site/data/sul_de_minas_graphs.js  (window.SUL_DE_MINAS_GRAPHS)

Run with the gentuk venv python:
  C:\\Users\\aliss\\gentuk-data-mcp\\.venv\\Scripts\\python.exe weather_site\\build_data.py

NASA-based, verifiable. Baseline = NASA 1981..last full year (NOT the report's
1974-2025 station baseline) -> close but not identical to the source report.
Leap day (Feb 29) is ignored so every year aligns to 365 days.
"""
import os, sys, json, math, time, urllib.request
from datetime import date, timedelta
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "data", "sul_de_minas_graphs.js")

CITIES = [
    ("varginha",       "Varginha",       -21.5667, -45.4061),
    ("carmo_de_minas", "Carmo de Minas", -22.1753, -45.1508),
    ("boa_esperanca",  "Boa Esperança",  -21.0664, -45.5769),
    ("guape",          "Guapé",          -20.7344, -46.0853),
]

START = "19810101"
YEARS_SHOWN = [2024, 2025, 2026]     # years generated as selectable/overlay lines
CAD = 130.0                          # available soil-water capacity (mm) = wet-season plateau height
FILL = -999.0
DIM = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]   # Feb=28 (leap day ignored)


def end_date():
    return (date.today() - timedelta(days=4)).strftime("%Y%m%d")  # NASA latency


def fetch(lat, lon, start, end, tries=4):
    url = ("https://power.larc.nasa.gov/api/temporal/daily/point"
           "?parameters=T2M,PRECTOTCORR&community=AG"
           f"&latitude={lat}&longitude={lon}&start={start}&end={end}&format=JSON")
    last = None
    for k in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=120) as r:
                data = json.load(r)
            p = data["properties"]["parameter"]
            return p["T2M"], p["PRECTOTCORR"]
        except Exception as e:               # noqa
            last = e
            time.sleep(3 * (k + 1))
    raise RuntimeError(f"NASA POWER fetch failed for {lat},{lon}: {last!r}")


def daylight_hours(lat_deg, doy):
    lat = math.radians(lat_deg)
    decl = 0.409 * math.sin(2 * math.pi / 365.0 * doy - 1.39)
    x = max(-1.0, min(1.0, -math.tan(lat) * math.tan(decl)))
    return 24.0 / math.pi * math.acos(x)


def mid_doy(m):
    return sum(DIM[:m - 1]) + DIM[m - 1] // 2 + 1


def pet_fn(tmean_clim, lat):
    """Return a monthly Thornthwaite PET function pet(tmean, month) -> mm/month."""
    I = sum((t / 5.0) ** 1.514 for t in tmean_clim if t and t > 0)
    a = 6.75e-7 * I ** 3 - 7.71e-5 * I ** 2 + 1.792e-2 * I + 0.49239

    def pet(t, m):
        if t is None or t <= 0 or I <= 0:
            unadj = 0.0
        elif t <= 26.5:
            unadj = 16.0 * (10.0 * t / I) ** a
        else:
            unadj = -415.85 + 32.24 * t - 0.43 * t * t
        N = daylight_hours(lat, mid_doy(m))
        return max(0.0, unadj * (N / 12.0) * (DIM[m - 1] / 30.0))
    return pet


def daily_pet_array(monthly_tmean, tmean_clim, lat):
    pet = pet_fn(tmean_clim, lat)
    arr = []
    for m in range(1, 13):
        arr += [pet(monthly_tmean[m - 1], m) / DIM[m - 1]] * DIM[m - 1]
    return arr


def water_bucket(daily_p, pet_arr):
    """Daily soil-water reservoir ('disponibilidade de água no solo', mm).
       Starts full at CAD, each day adds P - PET, drains any excess above CAD,
       and falls below zero (deficit) without a floor. Reproduces the report shape:
       a wet-season plateau near +CAD and a dry-season drawdown into negative mm."""
    S = CAD
    out = []
    for i, P in enumerate(daily_p):
        if P is None:
            out.append(round(S, 1))
            continue
        S += P - pet_arr[i]
        if S > CAD:
            S = CAD
        out.append(round(S, 1))
    return out


def decadal_net(daily_p, pet_arr):
    """10-day (decade) net P - PET, 3 decades/month -> 36 values (None if no data)."""
    out = []
    idx = 0
    for m in range(1, 13):
        dim = DIM[m - 1]
        seg_p = daily_p[idx:idx + dim]
        seg_pet = pet_arr[idx:idx + dim]
        for a, b in [(0, 10), (10, 20), (20, dim)]:
            sp = seg_p[a:b]
            vals = [v for v in sp if v is not None]
            if not sp or not vals:
                out.append(None)
            else:
                out.append(round(sum(vals) - sum(seg_pet[a:a + len(vals)]), 1))
        idx += dim
    return out


def year_sequence(daily, yr):
    seq_t, seq_p = [], []
    for m in range(1, 13):
        for dd in range(1, DIM[m - 1] + 1):        # Feb=28 -> Feb 29 skipped
            t, p = daily.get(f"{yr:04d}{m:02d}{dd:02d}", (None, None))
            seq_t.append(t); seq_p.append(p)
    while seq_p and seq_p[-1] is None:             # trim partial current year
        seq_p.pop(); seq_t.pop()
    return seq_t, seq_p


def build_city(lat, lon, end):
    t2m, prec = fetch(lat, lon, START, end)
    by_ym_t = defaultdict(list)
    by_ym_p = defaultdict(float)
    seen_p = set()
    daily = {}
    for k in sorted(t2m.keys()):
        t = None if t2m[k] == FILL else t2m[k]
        p = None if prec[k] == FILL else prec[k]
        y, m = int(k[:4]), int(k[4:6])
        if t is not None:
            by_ym_t[(y, m)].append(t)
        if p is not None:
            by_ym_p[(y, m)] += p
            seen_p.add((y, m))
        daily[k] = (t, p)

    last_full = date.today().year - 1
    base_years = list(range(1981, last_full + 1))

    temp_base, prec_base = [], []
    for m in range(1, 13):
        ts = [v for y in base_years for v in by_ym_t.get((y, m), [])]
        temp_base.append(round(sum(ts) / len(ts), 1) if ts else None)
        pv = [by_ym_p[(y, m)] for y in base_years if (y, m) in seen_p]
        prec_base.append(round(sum(pv) / len(pv), 1) if pv else None)

    temp = {"baseline": temp_base}
    precip = {"baseline": prec_base}
    for yr in YEARS_SHOWN:
        tm = [round(sum(by_ym_t[(yr, m)]) / len(by_ym_t[(yr, m)]), 1)
              if by_ym_t.get((yr, m)) else None for m in range(1, 13)]
        pm = [round(by_ym_p[(yr, m)], 1) if (yr, m) in seen_p else None
              for m in range(1, 13)]
        while tm and tm[-1] is None:
            tm.pop()
        while pm and pm[-1] is None:
            pm.pop()
        temp[str(yr)] = tm
        precip[str(yr)] = pm

    # daily climatology by day-of-year (skip Feb 29)
    doy_t = defaultdict(list); doy_p = defaultdict(list)
    for k, (t, p) in daily.items():
        y, m, dd = int(k[:4]), int(k[4:6]), int(k[6:8])
        if (m == 2 and dd == 29) or y not in base_years:
            continue
        doy = sum(DIM[:m - 1]) + dd
        if t is not None:
            doy_t[doy].append(t)
        if p is not None:
            doy_p[doy].append(p)
    clim_p = [round(sum(doy_p[d]) / len(doy_p[d]), 2) if doy_p.get(d) else None
              for d in range(1, 366)]

    pet_base = daily_pet_array(temp_base, temp_base, lat)
    water = {"baseline": water_bucket(clim_p, pet_base)}
    decadal = {"baseline": decadal_net(clim_p, pet_base)}
    for yr in YEARS_SHOWN:
        _, seq_p = year_sequence(daily, yr)
        if not seq_p:
            continue
        mt = temp[str(yr)] + temp_base[len(temp[str(yr)]):]     # fill missing months
        pet_arr = daily_pet_array(mt, temp_base, lat)
        water[str(yr)] = water_bucket(seq_p, pet_arr[:len(seq_p)])
        decadal[str(yr)] = decadal_net(seq_p, pet_arr)

    return {"temp": temp, "precip": precip, "water": water, "decadal": decadal}


def main():
    end = end_date()
    print("NASA POWER window:", START, "->", end, flush=True)
    cities = {}
    for cid, name, lat, lon in CITIES:
        print(f"  fetching {name} ({lat},{lon}) ...", flush=True)
        cities[cid] = build_city(lat, lon, end)
        time.sleep(1.0)
    payload = {
        "source": "NASA POWER (T2M, PRECTOTCORR)",
        "method": f"Daily soil-water bucket (capacity {int(CAD)} mm), P−PET with Thornthwaite PET",
        "baseline_label": f"1981–{date.today().year - 1}",
        "generated": date.today().strftime("%Y-%m-%d"),
        "years_shown": YEARS_SHOWN,
        "cities": cities,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("// AUTO-GENERATED by build_data.py — NASA POWER. Do not edit by hand.\n")
        f.write("window.SUL_DE_MINAS_GRAPHS = ")
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")
    print("wrote", OUT, flush=True)


if __name__ == "__main__":
    main()
