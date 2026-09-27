#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Which source is closest to reality? Compare CHIRPS v3, NASA POWER and Open-Meteo
with INMET automatic-station observations (the "truth"), at the station points.

Inputs : validation/stations/*.json   (tools/extract_inmet.py)
         validation/grids/nasa.json, om_stations.json, om_best_match.json
                                        (tools/fetch_reference.py, GitHub Actions)
         validation/grids/chirps.json  (CHIRPS monthly at the stations)
Output : validation/metrics.json + a printed summary
"""
import json, math, os
from collections import defaultdict
from datetime import date, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V = os.path.join(ROOT, "validation")
STATIONS = ["A515", "A531", "A529", "A524", "A523", "A556", "A616"]
MG = ["A515", "A531", "A529", "A524", "A523", "A556"]          # Minas Gerais coffee areas


def load(name):
    p = os.path.join(V, "grids", name + ".json")
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None


def daily(start, values):
    d0 = date.fromisoformat(start)
    return {(d0 + timedelta(i)).isoformat(): v for i, v in enumerate(values) if v is not None}


def monthly(days, how, first="2007-01", last="2026-08"):
    """{YYYY-MM: sum|mean} only for months where every day is present."""
    by = defaultdict(list)
    for d, v in days.items():
        by[d[:7]].append(v)
    out = {}
    for m, vals in by.items():
        y, mo = map(int, m.split("-"))
        n = ((date(y + mo // 12, mo % 12 + 1, 1)) - date(y, mo, 1)).days
        if first <= m <= last and len(vals) == n:
            out[m] = sum(vals) if how == "sum" else sum(vals) / n
    return out


def stats(pairs, rel=False):
    n = len(pairs)
    if n < 12:
        return None
    s = [a for a, _ in pairs]
    o = [b for _, b in pairs]
    ms, mo = sum(s) / n, sum(o) / n
    ss = math.sqrt(sum((x - ms) ** 2 for x in s) / n)
    so = math.sqrt(sum((x - mo) ** 2 for x in o) / n)
    r = sum((x - ms) * (y - mo) for x, y in pairs) / (n * ss * so) if ss and so else float("nan")
    out = {"n": n, "bias": round(ms - mo, 3), "mae": round(sum(abs(x - y) for x, y in pairs) / n, 3),
           "rmse": round(math.sqrt(sum((x - y) ** 2 for x, y in pairs) / n), 3), "r": round(r, 3)}
    if rel:
        out["bias_pct"] = round(100 * (ms - mo) / mo, 1) if mo else None
        out["mae_pct"] = round(100 * out["mae"] / mo, 1) if mo else None
        alpha, beta = ss / so, ms / mo
        out["kge"] = round(1 - math.sqrt((r - 1) ** 2 + (alpha - 1) ** 2 + (beta - 1) ** 2), 3)
    return out


def report_rows():
    """{(town, YYYY-MM): (temp_cur, prec_cur)} from the monthly report tables of the site."""
    import re
    out = {}
    for name in ("sul_de_minas.js", "cerrado.js"):
        src = open(os.path.join(ROOT, "data", name), encoding="utf-8").read()
        for m in re.finditer(r'"(\d{4}-\d{2})":\s*\{(.*?)\n\s*\}', src, re.S):
            for r in re.finditer(r'city:\s*"(\w+)".*?temp_cur:\s*([\d.]+).*?prec_cur:\s*([\d.]+)', m.group(2)):
                out[(r.group(1), m.group(1))] = (float(r.group(2)), float(r.group(3)))
    return out


def against_reports(ch, nasa, om):
    """Second check: the station values printed in the site's monthly reports."""
    rep = report_rows()
    town_month = {}
    if nasa:
        p = nasa["towns"]
        for t, s in p["series"].items():
            town_month[("NASA POWER", t, "rain")] = monthly(daily(p["start"], s["PRECTOTCORR"]), "sum", "2006-07")
            town_month[("NASA POWER", t, "tmean")] = monthly(daily(p["start"], s["T2M"]), "mean", "2006-07")
    if om:
        for t, s in om["series"].items():
            town_month[("Open-Meteo ERA5-Land", t, "rain")] = monthly(daily(om["start"], s["precipitation_sum"]), "sum", "2006-07")
            town_month[("Open-Meteo ERA5-Land", t, "tmean")] = monthly(daily(om["start"], s["temperature_2m_mean"]), "mean", "2006-07")
    pairs = defaultdict(list)
    for (t, m), (temp, rain) in rep.items():
        if ch and ch["series"].get(t, {}).get(m) is not None:
            pairs[("CHIRPS v3", "rain")].append((ch["series"][t][m], rain))
        for src in ("NASA POWER", "Open-Meteo ERA5-Land"):
            for var, obs_v in (("rain", rain), ("tmean", temp)):
                v = town_month.get((src, t, var), {}).get(m)
                if v is not None:
                    pairs[(src, var)].append((v, obs_v))
    return {f"{src}|{var}": stats(p, var == "rain") for (src, var), p in pairs.items()}


def main():
    obs = {c: json.load(open(os.path.join(V, "stations", c + ".json"), encoding="utf-8")) for c in STATIONS}
    nasa, om, bm, ch = load("nasa"), load("om_stations"), load("om_best_match"), load("chirps")

    # source -> station -> variable -> daily dict  (CHIRPS: monthly dict)
    src = defaultdict(lambda: defaultdict(dict))
    if nasa:
        p = nasa["stations"]
        for c in STATIONS:
            s = p["series"][c]
            for var, key in (("rain", "PRECTOTCORR"), ("tmean", "T2M"), ("tmin", "T2M_MIN"),
                             ("tmax", "T2M_MAX"), ("rh", "RH2M")):
                src["NASA POWER"][c][var] = daily(p["start"], s[key])
    for label, g in (("Open-Meteo ERA5-Land", om), ("Open-Meteo best_match", bm)):
        if not g:
            continue
        for c in STATIONS:
            s = g["series"][c]
            for var, key in (("rain", "precipitation_sum"), ("tmean", "temperature_2m_mean"),
                             ("tmin", "temperature_2m_min"), ("tmax", "temperature_2m_max"),
                             ("rh", "relative_humidity_2m")):
                src[label][c][var] = daily(g["start"], s[key])

    truth = {c: {var: daily(obs[c]["start"], obs[c]["series"][var])
                 for var in ("rain", "tmean", "tmin", "tmax", "rh")} for c in STATIONS}

    results = {"period": "2007-01..2026-08 (best_match: 2017-01..2026-08)", "by_var": {}}
    for var in ("rain", "tmean", "tmin", "tmax", "rh"):
        how = "sum" if var == "rain" else "mean"
        res = {}
        labels = list(src) + (["CHIRPS v3"] if (ch and var == "rain") else [])
        for label in labels:
            per_station, all_m, all_d, all_y = {}, [], [], []
            for c in STATIONS:
                t_days = truth[c][var]
                t_mon = monthly(t_days, how)
                if label == "CHIRPS v3":
                    s_mon = {m: v for m, v in ch["series"][c].items() if v is not None}
                    s_days = {}
                else:
                    s_days = src[label][c].get(var, {})
                    s_mon = monthly(s_days, how)
                pm = [(s_mon[m], t_mon[m]) for m in sorted(t_mon) if m in s_mon]
                pd = [(s_days[d], t_days[d]) for d in t_days if d in s_days]
                # calendar years with 12 complete months
                years = defaultdict(list)
                for m in t_mon:
                    if m in s_mon:
                        years[m[:4]].append(m)
                py = [(sum(s_mon[m] for m in ms) if how == "sum" else sum(s_mon[m] for m in ms) / 12,
                       sum(t_mon[m] for m in ms) if how == "sum" else sum(t_mon[m] for m in ms) / 12)
                      for y, ms in years.items() if len(ms) == 12]
                per_station[c] = {"monthly": stats(pm, var == "rain"),
                                  "yearly": stats(py, var == "rain") if len(py) >= 3 else None,
                                  "daily": stats(pd, var == "rain") if pd else None}
                if c in MG:
                    all_m += pm
                    all_d += pd
                    all_y += py
            res[label] = {"stations": per_station,
                          "mg_monthly": stats(all_m, var == "rain"),
                          "mg_yearly": stats(all_y, var == "rain") if len(all_y) >= 12 else None,
                          "mg_daily": stats(all_d, var == "rain") if all_d else None}
        results["by_var"][var] = res

    results["reports"] = against_reports(ch, nasa, load("om_towns"))
    with open(os.path.join(V, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=1)

    names = {"rain": "Rainfall (monthly totals)", "tmean": "Mean temperature", "tmin": "Min temperature",
             "tmax": "Max temperature", "rh": "Relative humidity"}
    for var, res in results["by_var"].items():
        print(f"\n== {names[var]} — 6 MG stations pooled ==")
        for label, r in sorted(res.items(), key=lambda kv: (kv[1]["mg_monthly"] or {}).get("mae", 1e9)):
            m, y, d = r["mg_monthly"], r["mg_yearly"], r["mg_daily"]
            line = f"  {label:24s} monthly: n={m['n']:4d} bias={m['bias']:+7.2f} MAE={m['mae']:6.2f} r={m['r']:.3f}"
            if var == "rain":
                line += f" bias%={m['bias_pct']:+5.1f} MAE%={m['mae_pct']:4.1f} KGE={m['kge']:.3f}"
            if y:
                line += f" | yearly MAE={y['mae']:.1f}" + (f" ({y['mae_pct']:.1f}%) r={y['r']:.2f}" if var == "rain" else f" r={y['r']:.2f}")
            if d:
                line += f" | daily MAE={d['mae']:.2f} r={d['r']:.3f}"
            print(line)


if __name__ == "__main__":
    main()
