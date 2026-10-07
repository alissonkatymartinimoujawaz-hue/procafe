#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Build the market data for market.html: world stocks-to-use, ICE certified
stocks-to-use, KC1 / KC2 front spread and Brazil quality spreads.

Inputs  (see market_inputs/README.md):
  market_inputs/annual.csv   one row per coffee season (Oct-Sep)
  market_inputs/daily.csv    one row per trading day
Output:
  data/market.js             window.MARKET = {annual, daily, stats, generated}

  python build_market.py            # build from the CSVs
  python build_market.py --usda     # first fill annual.csv from the USDA PSD coffee CSV

Definitions
  world STU     = world ending stocks / world consumption              (%)
  cert / use    = ICE certified arabica bags / world annual consumption (%)
  front spread  = KC1 - KC2 (US c/lb). > 0 = inverse (backwardation) = nearby scarcity
  exchange share= (cert / use) / (world STU): the part of the world's stocks that
                  sits in ICE warehouses, i.e. what the exchange can actually deliver.
Stdlib only (same as build_data.py).
"""
import os, sys, csv, io, json, zipfile, urllib.request
from datetime import date, datetime
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
INP = os.path.join(HERE, "market_inputs")
ANNUAL = os.path.join(INP, "annual.csv")
DAILY = os.path.join(INP, "daily.csv")
OUT = os.path.join(HERE, "data", "market.js")
USDA_URL = "https://apps.fas.usda.gov/psdonline/downloads/psd_coffee_csv.zip"

DAILY_COLS = ["kc1", "kc2", "certified_bags", "cert_use_pct",
              "fine_cup", "good_cup", "rio_minas", "low_grade", "conilon", "london"]


def num(s):
    s = (s or "").strip().replace(",", "")
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def season_of(d):
    """Coffee year Oct-Sep: 2025-10-01 .. 2026-09-30 -> '2025/26'."""
    y = d.year if d.month >= 10 else d.year - 1
    return f"{y}/{str(y + 1)[-2:]}"


def read_csv(path):
    if not os.path.exists(path):
        return [], []
    with open(path, newline="", encoding="utf-8-sig") as f:
        r = csv.DictReader(f)
        return r.fieldnames or [], list(r)


def write_csv(path, fields, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


# ---------------------------------------------------------------- USDA PSD
def fill_from_usda():
    print("Downloading USDA PSD coffee ...")
    req = urllib.request.Request(USDA_URL, headers={"User-Agent": "Mozilla/5.0"})
    raw = urllib.request.urlopen(req, timeout=120).read()
    z = zipfile.ZipFile(io.BytesIO(raw))
    name = [n for n in z.namelist() if n.lower().endswith(".csv")][0]
    rows = csv.DictReader(io.TextIOWrapper(z.open(name), encoding="utf-8-sig"))
    world = defaultdict(lambda: defaultdict(float))     # year -> attr -> sum
    brazil, vietnam = {}, {}
    for r in rows:
        if "Coffee" not in r.get("Commodity_Description", ""):
            continue
        y, a, v = int(r["Market_Year"]), r["Attribute_Description"].strip(), float(r["Value"] or 0)
        world[y][a] += v
        if a == "Production":
            if r["Country_Name"] == "Brazil":
                brazil[y] = v
            elif r["Country_Name"] == "Vietnam":
                vietnam[y] = v
    fields, rows = read_csv(ANNUAL)
    by = {r["season"]: r for r in rows}
    for y in sorted(world):
        if y < 2005:
            continue
        s = f"{y}/{str(y + 1)[-2:]}"
        r = by.setdefault(s, {k: "" for k in fields} | {"season": s})
        w = world[y]
        r["world_production"] = f"{w.get('Production', 0):.0f}"
        r["world_consumption"] = f"{w.get('Domestic Consumption', 0):.0f}"
        r["world_ending_stocks"] = f"{w.get('Ending Stocks', 0):.0f}"
        if y in brazil:
            r["brazil_production"] = f"{brazil[y]:.0f}"
        if y in vietnam:
            r["vietnam_production"] = f"{vietnam[y]:.0f}"
        if "USDA" not in r.get("note", ""):
            r["note"] = (r.get("note", "") + " USDA PSD").strip()
    write_csv(ANNUAL, fields, sorted(by.values(), key=lambda r: r["season"]))
    print(f"annual.csv updated from USDA ({len(world)} years)")


# ---------------------------------------------------------------- build
def build():
    _, arows = read_csv(ANNUAL)
    _, drows = read_csv(DAILY)

    # daily
    daily = []
    for r in drows:
        try:
            d = datetime.strptime(r["date"].strip()[:10], "%Y-%m-%d").date()
        except (KeyError, ValueError):
            continue
        rec = {"date": d}
        for c in DAILY_COLS:
            rec[c] = num(r.get(c))
        daily.append(rec)
    daily.sort(key=lambda x: x["date"])

    # season averages of KC1 (only if the season is reasonably covered)
    kc_by = defaultdict(list)
    for x in daily:
        if x["kc1"] is not None:
            kc_by[season_of(x["date"])].append(x["kc1"])

    annual = []
    for r in arows:
        s = r["season"].strip()
        stocks, cons = num(r.get("world_ending_stocks")), num(r.get("world_consumption"))
        stu = stocks / cons * 100 if stocks and cons else num(r.get("stu_world_pct"))
        kc1 = num(r.get("kc1_avg"))
        if kc1 is None and len(kc_by.get(s, [])) >= 120:
            kc1 = sum(kc_by[s]) / len(kc_by[s])
        annual.append({
            "season": s, "stu": stu, "kc1_avg": kc1, "df1_avg": num(r.get("df1_avg")),
            "production": num(r.get("world_production")), "consumption": cons, "stocks": stocks,
            "brazil": num(r.get("brazil_production")), "vietnam": num(r.get("vietnam_production")),
            "forecast": "forecast" in (r.get("note") or "").lower(),
        })
    ann = {a["season"]: a for a in annual}

    # daily derived series
    out = defaultdict(list)
    for k in ("date", "kc1", "kc2", "spread", "cert_bags", "cert_use", "stu", "share",
              "fine_cup", "good_cup", "rio_minas", "low_grade", "conilon",
              "fc_gc", "fc_rm", "fc_lg", "gc_rm", "gc_lg", "lg_con"):
        out[k] = []
    for x in daily:
        a = ann.get(season_of(x["date"]), {})
        cons = a.get("consumption")
        cu = x["cert_use_pct"]
        if cu is None and x["certified_bags"] is not None and cons:
            cu = x["certified_bags"] / (cons * 1000) * 100          # cons in 1000 bags
        spread = x["kc1"] - x["kc2"] if x["kc1"] is not None and x["kc2"] is not None else None
        stu = a.get("stu")
        out["date"].append(x["date"].isoformat())
        out["kc1"].append(x["kc1"])
        out["kc2"].append(x["kc2"])
        out["spread"].append(None if spread is None else round(spread, 2))
        out["cert_bags"].append(x["certified_bags"])
        out["cert_use"].append(None if cu is None else round(cu, 4))
        out["stu"].append(stu)
        out["share"].append(None if cu is None or not stu else round(cu / stu * 100, 3))
        ny = x["kc1"]
        for c in ("fine_cup", "good_cup", "rio_minas", "low_grade"):
            out[c].append(None if x[c] is None or ny is None else round(x[c] - ny, 2))   # diff vs NY
        out["conilon"].append(None if x["conilon"] is None or x["london"] is None
                              else round(x["conilon"] - x["london"], 2))
        out["fc_gc"].append(pair(x, "fine_cup", "good_cup"))
        out["fc_rm"].append(pair(x, "fine_cup", "rio_minas"))
        out["fc_lg"].append(pair(x, "fine_cup", "low_grade"))
        out["gc_rm"].append(pair(x, "good_cup", "rio_minas"))
        out["gc_lg"].append(pair(x, "good_cup", "low_grade"))
        out["lg_con"].append(pair(x, "low_grade", "conilon"))

    data = {"generated": date.today().isoformat(), "annual": annual,
            "daily": dict(out), "stats": regimes(out)}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("// Generated by build_market.py - do not edit by hand\n")
        f.write("window.MARKET = " + json.dumps(data, separators=(",", ":")) + ";\n")
    print(f"Wrote {OUT}: {len(annual)} seasons, {len(daily)} daily rows")


def pair(x, a, b):
    return None if x[a] is None or x[b] is None else round(x[a] - x[b], 2)


def regimes(d):
    """Average KC1-KC2 spread by cert/use bucket: the 'curve' between exchange
    stocks and nearby scarcity."""
    edges = [0, 0.2, 0.3, 0.4, 0.6, 0.8, 1.0, 1.2, 9]
    acc = [[] for _ in edges[:-1]]
    for cu, sp in zip(d.get("cert_use", []), d.get("spread", [])):
        if cu is None or sp is None:
            continue
        for i in range(len(edges) - 1):
            if edges[i] <= cu < edges[i + 1]:
                acc[i].append(sp)
                break
    res = []
    for i, v in enumerate(acc):
        if v:
            v = sorted(v)
            res.append({"lo": edges[i], "hi": edges[i + 1], "n": len(v),
                        "mean": round(sum(v) / len(v), 2), "median": v[len(v) // 2],
                        "p90": v[int(len(v) * 0.9)]})
    return {"spread_by_certuse": res}


if __name__ == "__main__":
    if "--usda" in sys.argv:
        try:
            fill_from_usda()
        except Exception as e:                      # keep building from the CSVs
            print("USDA download failed:", e)
    build()
