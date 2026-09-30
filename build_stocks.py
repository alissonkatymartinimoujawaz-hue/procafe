#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Coffee stock-to-use (SUR) study, 2010/11 -> 2026/27, vs KC1 (ICE NY arabica)
and DF1/RC1 (ICE London robusta).

Output -> data/stocks_to_use.js   (window.STOCKS_TO_USE)

DATA SOURCES
  * Supply & demand: USDA FAS PSD "Coffee, Green" (1000 x 60-kg bags, local
    marketing years). If `psd_coffee.csv` (unzipped from
    https://apps.fas.usda.gov/psdonline/downloads/psd_coffee_csv.zip) sits next
    to this script, the REAL PSD numbers are used and override the embedded
    table. Otherwise the embedded FALLBACK table below is used.
  * Prices: coffee-year averages (Oct Y -> Sep Y+1), KC1 in US c/lb,
    robusta (DF1 / RC1) in US$/t. 2026/27 = spot at 30 Sep 2026.

!!! The embedded FALLBACK table was reconstructed without network access to
!!! PSD Online (egress blocked). It is anchored on published USDA figures
!!! (world 2015/16, 2023/24, 2025/26, 2026/27 stocks; Brazil and Vietnam
!!! 2024/25 -> 2026/27 GAIN balances) but the other years and the small
!!! origins are APPROXIMATE (small-origin stocks can be off by +-50 %).
!!! Exports are derived so every country balance closes:
!!!     exports = beginning stocks + production + imports - consumption - ending
!!! Run with psd_coffee.csv present before trading on the exact levels.

DEFINITIONS
  * World SUR      = world ending stocks / world domestic consumption.
    (Never add exports at world level: every exported bag is consumed in an
    importing country, so cons + exports would double count.)
  * Country SUR    = ending stocks / (domestic consumption + exports)
    = how many months of that origin's total offtake sits in stock.
  * Surplus ratio  = (production - domestic consumption - exports)
                     / (domestic consumption + exports)
    = the year's flow surplus (+) / deficit (-) of an origin vs its offtake.
  * Brazil is split arabica / robusta pro-rata to USDA's production split
    (USDA does not split stocks or exports by type).
"""
import os, csv, json, math

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "data", "stocks_to_use.js")
PSD_CSV = os.path.join(HERE, "psd_coffee.csv")

YEARS = list(range(2010, 2027))          # MY start year: 2010 -> "2010/11"
LABELS = ["%d/%02d" % (y, (y + 1) % 100) for y in YEARS]

# ---------------------------------------------------------------------------
# Prices, coffee-year averages (Oct Y - Sep Y+1). Last one = spot 30-Sep-2026.
# ---------------------------------------------------------------------------
KC1 = [249, 194, 136, 159, 149, 137, 146, 119, 101, 111, 145, 225, 172, 221, 344, 328, 295]
RC1 = [2200, 2100, 1875, 1912, 1848, 1722, 2102, 1740, 1487, 1330, 1612, 2175, 2462, 3775, 4725, 4075, 3865]

# ---------------------------------------------------------------------------
# World (USDA) - production, domestic consumption, ending stocks (1000 bags)
# ---------------------------------------------------------------------------
WORLD = {
    "prod": [142700, 139000, 151400, 150800, 149200, 152400, 158800, 158900, 171400,
             166200, 175900, 167200, 168200, 171600, 174400, 178800, 189700],
    "cons": [136000, 139000, 143000, 146000, 150000, 152000, 156000, 160000, 164000,
             164600, 165000, 167500, 168000, 169500, 171700, 173900, 179700],
    "end":  [30500, 29200, 33600, 36300, 34000, 34800, 32700, 35000, 37300,
             34600, 36800, 31500, 27500, 23900, 21300, 22500, 26300],
}

# ---------------------------------------------------------------------------
# Origins. prod / cons / imp / end per MY; beg = 2009/10 ending stocks.
# arab = arabica share of production (only where the origin grows both).
# ---------------------------------------------------------------------------
C = {}
C["Brazil"] = dict(
    beg=3000,
    prod=[53800, 45700, 55400, 53900, 52600, 52800, 53800, 49700, 65400, 58400,
          69900, 58100, 60700, 66300, 64700, 63500, 71900],
    cons=[19100, 19700, 20100, 20300, 20300, 20500, 21200, 21900, 22200, 22400,
          22400, 22100, 21200, 21700, 21970, 22280, 22390],
    imp=[100] * 17,
    end=[4300, 2400, 6800, 8200, 3700, 1800, 3800, 1400, 4000, 2500,
         4500, 1000, 3500, 2160, 440, 3860, 4400],
    arab=[.72, .71, .70, .67, .65, .64, .71, .72, .67, .68, .71, .61, .60, .67, .62, .56, .60],
)
C["Vietnam"] = dict(
    beg=1500,
    prod=[20000, 26500, 23400, 29800, 27400, 28900, 25500, 29900, 30400, 31300,
          29000, 31600, 29750, 27500, 29000, 31700, 32500],
    cons=[1600, 1700, 1800, 2000, 2200, 2400, 2600, 2800, 2900, 3000,
          3100, 3300, 3500, 3700, 4100, 4700, 4850],
    imp=[800] * 6 + [1300] * 5 + [1700] * 6,
    end=[1300, 2000, 2500, 4500, 4000, 2300, 1200, 2800, 3800, 4800,
         4300, 3800, 3200, 700, 400, 689, 1100],
    arab=[.05] * 17,
)
C["Colombia"] = dict(
    beg=600,
    prod=[8500, 7650, 9900, 12100, 13300, 14000, 14600, 13800, 13900, 14100,
          13400, 12600, 11100, 12900, 13400, 12800, 12800],
    cons=[1400, 1450, 1500, 1550, 1600, 1700, 1750, 1800, 1850, 1900,
          2000, 2050, 2100, 2100, 2150, 2150, 2200],
    imp=[1000] * 5 + [1400] * 6 + [1500] * 6,
    end=[500, 400, 600, 900, 1100, 1200, 1300, 1300, 1400, 1500,
         1700, 1000, 600, 900, 1100, 1000, 1200],
)
C["Honduras"] = dict(
    beg=150,
    prod=[4300, 5900, 4700, 4600, 5300, 5800, 7500, 7600, 7300, 6100,
          6000, 5600, 5700, 5950, 5500, 5700, 5900],
    cons=[330, 340, 350, 350, 360, 370, 370, 380, 380, 390, 390, 400, 400, 410, 410, 420, 420],
    imp=[0] * 17,
    end=[100, 250, 150, 150, 300, 350, 450, 400, 500, 400, 350, 250, 200, 300, 200, 250, 300],
)
C["Ethiopia"] = dict(
    beg=300,
    prod=[6125, 6320, 6233, 6345, 6625, 6510, 6943, 7055, 7300, 7375,
          7550, 8150, 8250, 8350, 8500, 8600, 8700],
    cons=[3300, 3400, 3450, 3500, 3600, 3650, 3700, 3750, 3800, 3900,
          4000, 4100, 4200, 4300, 4400, 4450, 4500],
    imp=[0] * 17,
    end=[250, 300, 250, 300, 350, 300, 350, 300, 350, 300, 250, 300, 350, 300, 250, 300, 300],
)
C["Peru"] = dict(
    beg=200,
    prod=[4100, 5600, 4500, 4300, 2900, 3300, 4200, 4300, 4300, 3800,
          3800, 4200, 3800, 4000, 4100, 4000, 4100],
    cons=[200, 200, 210, 220, 230, 240, 250, 260, 270, 280, 290, 300, 300, 310, 320, 320, 330],
    imp=[0] * 17,
    end=[250, 400, 350, 250, 150, 200, 300, 300, 350, 300, 250, 300, 250, 250, 200, 250, 300],
)
C["Mexico"] = dict(
    beg=700,
    prod=[4000, 4500, 4300, 3900, 3600, 2300, 3100, 3650, 3800, 3700,
          3600, 3900, 3900, 4100, 4000, 3900, 3900],
    cons=[2300, 2350, 2400, 2450, 2500, 2550, 2600, 2700, 2800, 2900,
          3000, 3050, 3100, 3150, 3200, 3200, 3250],
    imp=[900, 900, 1000, 1100, 1300, 1900, 1800, 1600, 1600, 1600,
         1700, 1600, 1600, 1500, 1500, 1600, 1600],
    end=[700, 750, 800, 700, 600, 500, 550, 600, 650, 600, 550, 600, 600, 650, 550, 500, 550],
)
C["Guatemala"] = dict(
    beg=150,
    prod=[3950, 3850, 3750, 3300, 3300, 3400, 3500, 3800, 3650, 3600,
          3650, 3600, 3500, 3550, 3700, 3750, 3700],
    cons=[350, 360, 370, 380, 390, 400, 400, 410, 420, 430, 430, 440, 440, 450, 450, 460, 460],
    imp=[0] * 17,
    end=[150, 200, 150, 100, 150, 150, 200, 200, 250, 200, 200, 150, 150, 200, 150, 150, 200],
)
C["Costa Rica"] = dict(
    beg=100,
    prod=[1550, 1650, 1600, 1450, 1400, 1450, 1500, 1400, 1500, 1450,
          1400, 1400, 1250, 1300, 1200, 1300, 1300],
    cons=[370, 370, 380, 380, 390, 390, 400, 400, 400, 410, 410, 410, 420, 420, 420, 430, 430],
    imp=[200, 200, 250, 250, 300, 300, 300, 300, 300, 350, 350, 350, 400, 400, 400, 400, 400],
    end=[100, 120, 120, 100, 100, 110, 120, 110, 120, 110, 100, 100, 90, 100, 90, 100, 110],
)
C["Nicaragua"] = dict(
    beg=80,
    prod=[1900, 2000, 1900, 1950, 2100, 2100, 2650, 2700, 2700, 2700,
          2900, 2800, 2800, 2900, 3000, 2900, 3000],
    cons=[250, 260, 260, 270, 270, 280, 280, 290, 300, 300, 310, 310, 320, 320, 330, 330, 340],
    imp=[0] * 17,
    end=[80, 100, 90, 90, 110, 100, 130, 120, 140, 120, 110, 100, 90, 110, 90, 100, 110],
)
C["Indonesia"] = dict(
    beg=600,
    prod=[9150, 8300, 10500, 11265, 9350, 12100, 10700, 10800, 10200, 10700,
          11300, 11500, 11850, 9700, 10900, 11300, 11000],
    cons=[3300, 3500, 3700, 3900, 4000, 4150, 4300, 4450, 4600, 4700,
          4750, 4800, 4800, 4800, 4850, 4900, 4950],
    imp=[300, 300, 400, 400, 500, 600, 700, 800, 1000, 1100, 1000, 1100, 1300, 1400, 1300, 1300, 1300],
    end=[700, 500, 900, 1300, 700, 1400, 900, 800, 700, 1000, 1200, 1100, 1300, 400, 500, 800, 700],
    arab=[.15] * 17,
)
C["Uganda"] = dict(
    beg=150,
    prod=[3200, 3100, 3900, 3600, 3800, 3650, 4900, 4800, 4700, 5700,
          6100, 6400, 6400, 6700, 6900, 7700, 7700],
    cons=[150, 160, 170, 180, 190, 200, 210, 220, 230, 240, 250, 260, 270, 280, 290, 300, 300],
    imp=[0] * 17,
    end=[150, 100, 200, 150, 150, 100, 250, 200, 150, 300, 400, 300, 200, 150, 100, 250, 300],
)

ARABICA_BASKET = ["Brazil", "Colombia", "Honduras", "Ethiopia", "Peru", "Mexico",
                  "Guatemala", "Costa Rica", "Nicaragua"]
ROBUSTA_BASKET = ["Brazil", "Vietnam", "Indonesia", "Uganda"]
SURPLUS_ARABICA = ["Brazil", "Colombia", "Honduras", "Mexico", "Peru", "Nicaragua"]
SURPLUS_ROBUSTA = ["Vietnam", "Brazil", "Uganda", "Indonesia"]

PSD_NAMES = {"Costa Rica": "Costa Rica", "Vietnam": "Vietnam"}


def load_psd():
    """Override the fallback with the real USDA PSD CSV when available."""
    if not os.path.exists(PSD_CSV):
        return "fallback (approximate, see header)"
    want = {"Production": "prod", "Domestic Consumption": "cons", "Imports": "imp",
            "Ending Stocks": "end", "Arabica Production": "arabp", "Beginning Stocks": "begs"}
    rows = {}
    with open(PSD_CSV, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            k = want.get(r["Attribute_Description"].strip())
            if not k:
                continue
            y = int(r["Market_Year"])
            rows.setdefault(r["Country_Name"].strip(), {}).setdefault(k, {})[y] = float(r["Value"])
    for name, d in C.items():
        p = rows.get(PSD_NAMES.get(name, name))
        if not p:
            continue
        for k in ("prod", "cons", "imp", "end"):
            if k in p:
                d[k] = [p[k].get(y, d[k][i]) for i, y in enumerate(YEARS)]
        if "begs" in p and YEARS[0] in p["begs"]:
            d["beg"] = p["begs"][YEARS[0]]
        if "arabp" in p and "arab" in d:
            d["arab"] = [p["arabp"].get(y, 0) / max(p["prod"].get(y, 1), 1) for y in YEARS]
    tot = {}
    for name, p in rows.items():
        for k in ("prod", "cons", "end"):
            for y, v in p.get(k, {}).items():
                tot.setdefault(k, {}).setdefault(y, 0)
                tot[k][y] += v
    for k in ("prod", "cons", "end"):
        WORLD[k] = [tot[k].get(y, WORLD[k][i]) for i, y in enumerate(YEARS)]
    return "USDA PSD Online (psd_coffee.csv)"


def balance(name, share=None):
    """Return per-year dict of prod/cons/exp/end/use for an origin (optionally
    scaled to its arabica ('A') or robusta ('R') part)."""
    d = C[name]
    out, beg = [], d["beg"]
    for i in range(len(YEARS)):
        exp = beg + d["prod"][i] + d["imp"][i] - d["cons"][i] - d["end"][i]
        f = 1.0
        if share == "A":
            f = d.get("arab", [1.0] * 17)[i]
        elif share == "R":
            f = 1 - d.get("arab", [0.0] * 17)[i]
        out.append(dict(prod=d["prod"][i] * f, cons=d["cons"][i] * f, exp=exp * f,
                        end=d["end"][i] * f))
        beg = d["end"][i]
    return out


def basket(names, kind):
    tot = [dict(prod=0, cons=0, exp=0, end=0) for _ in YEARS]
    for n in names:
        share = kind if (n in ("Brazil", "Vietnam", "Indonesia") and
                         ((kind == "A" and n == "Brazil") or kind == "R")) else None
        for t, b in zip(tot, balance(n, share)):
            for k in t:
                t[k] += b[k]
    return tot


def sur(rows):
    return [round(100 * r["end"] / (r["cons"] + r["exp"]), 2) for r in rows]


def surplus(rows, beg):
    """Stock build (+) / draw (-) of the year as % of offtake."""
    out, b = [], beg
    for r in rows:
        out.append(round(100 * (r["end"] - b) / (r["cons"] + r["exp"]), 2))
        b = r["end"]
    return out


def basket_beg(names, kind):
    tot = 0.0
    for n in names:
        d = C[n]
        f = 1.0
        if kind == "A" and n == "Brazil":
            f = d["arab"][0]
        elif kind == "R" and "arab" in d:
            f = 1 - d["arab"][0]
        tot += d["beg"] * f
    return tot


# --- small stats helpers (no numpy dependency) ------------------------------
def pearson(a, b):
    n = len(a)
    ma, mb = sum(a) / n, sum(b) / n
    sa = math.sqrt(sum((x - ma) ** 2 for x in a))
    sb = math.sqrt(sum((y - mb) ** 2 for y in b))
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (sa * sb)


def ols(x, y):
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    b = sum((a - mx) * (c - my) for a, c in zip(x, y)) / sum((a - mx) ** 2 for a in x)
    return my - b * mx, b


def main():
    source = load_psd()
    world_sur = [round(100 * e / c, 2) for e, c in zip(WORLD["end"], WORLD["cons"])]

    A = basket(ARABICA_BASKET, "A")
    R = basket(ROBUSTA_BASKET, "R")
    per = {n: balance(n) for n in C}
    per_sur = {n: sur(v) for n, v in per.items()}

    br_a = balance("Brazil", "A")
    br_r = balance("Brazil", "R")
    surplus_a_br = surplus(balance("Brazil"), C["Brazil"]["beg"])
    surplus_a_basket = surplus(basket(SURPLUS_ARABICA, "A"), basket_beg(SURPLUS_ARABICA, "A"))
    surplus_r_vn = surplus(per["Vietnam"], C["Vietnam"]["beg"])
    surplus_r_basket = surplus(basket(SURPLUS_ROBUSTA, "R"), basket_beg(SURPLUS_ROBUSTA, "R"))

    # ---- statistics used in the analysis --------------------------------
    hist = slice(0, len(YEARS) - 1)       # exclude 2026/27 (spot price, forecast S&D)
    lk = [math.log(p) for p in KC1]
    lr = [math.log(p) for p in RC1]
    stats = {}

    def corr_block(tag, series, logp):
        s = series[hist]
        lp = logp[hist]
        d_s = [b - a for a, b in zip(s[:-1], s[1:])]
        d_p = [b - a for a, b in zip(lp[:-1], lp[1:])]
        stats[tag] = dict(
            level=round(pearson(s, lp), 2),
            change=round(pearson(d_s, d_p), 2),
            lead=round(pearson(s[:-1], lp[1:]), 2),   # SUR this year vs price next year
            vs_move=round(pearson(s[1:], d_p), 2),     # level this year vs price change this year
        )

    corr_block("world_vs_kc", world_sur, lk)
    corr_block("world_vs_rc", world_sur, lr)
    corr_block("arabica_basket_vs_kc", sur(A), lk)
    corr_block("robusta_basket_vs_rc", sur(R), lr)
    for n in ("Brazil", "Colombia", "Vietnam", "Honduras", "Ethiopia", "Peru", "Mexico",
              "Guatemala", "Indonesia", "Uganda"):
        corr_block(n + "_vs_kc", per_sur[n], lk)
        corr_block(n + "_vs_rc", per_sur[n], lr)
    corr_block("brazil_prod_vs_kc", [float(v) for v in C["Brazil"]["prod"]], lk)
    corr_block("brazil_surplus_vs_kc", surplus_a_br, lk)
    corr_block("arabica_surplus_vs_kc", surplus_a_basket, lk)
    corr_block("vietnam_surplus_vs_rc", surplus_r_vn, lr)
    corr_block("robusta_surplus_vs_rc", surplus_r_basket, lr)
    corr_block("world_cons_vs_kc", [float(v) for v in WORLD["cons"]], lk)
    corr_block("world_prod_minus_cons_vs_kc",
               [float(p - c) for p, c in zip(WORLD["prod"], WORLD["cons"])], lk)

    br = [float(v) for v in C["Brazil"]["prod"]]
    corr_block("brazil_prod_yoy_vs_kc", [0.0] + [100 * (b / a - 1) for a, b in zip(br[:-1], br[1:])], lk)
    vn = [float(v) for v in C["Vietnam"]["prod"]]
    corr_block("vietnam_prod_yoy_vs_rc", [0.0] + [100 * (b / a - 1) for a, b in zip(vn[:-1], vn[1:])], lr)

    # price regimes by world SUR bucket
    regimes = []
    for lo, hi in ((0, 15), (15, 20), (20, 22), (22, 30)):
        idx = [i for i in range(len(YEARS) - 1) if lo <= world_sur[i] < hi]
        if idx:
            regimes.append(dict(lo=lo, hi=hi, years=[LABELS[i] for i in idx],
                                kc=round(sum(KC1[i] for i in idx) / len(idx)),
                                rc=round(sum(RC1[i] for i in idx) / len(idx))))
    stats["regimes"] = regimes

    # price-vs-SUR fit: log(price) = a + b * SUR   (world SUR)
    a_k, b_k = ols(world_sur[hist], lk[hist])
    a_r, b_r = ols(world_sur[hist], lr[hist])
    fit = dict(kc=dict(a=a_k, b=b_k), rc=dict(a=a_r, b=b_r))
    grid = [12, 14, 16, 18, 20, 22, 24]
    fit["kc_table"] = [(g, round(math.exp(a_k + b_k * g))) for g in grid]
    fit["rc_table"] = [(g, round(math.exp(a_r + b_r * g))) for g in grid]

    data = dict(
        source=source,
        years=LABELS,
        prices=dict(kc1=KC1, rc1=RC1),
        world=dict(sur=world_sur, **WORLD),
        arabica_basket=dict(countries=ARABICA_BASKET, sur=sur(A),
                            end=[round(r["end"]) for r in A],
                            use=[round(r["cons"] + r["exp"]) for r in A]),
        robusta_basket=dict(countries=ROBUSTA_BASKET, sur=sur(R),
                            end=[round(r["end"]) for r in R],
                            use=[round(r["cons"] + r["exp"]) for r in R]),
        countries={n: dict(sur=per_sur[n],
                           prod=C[n]["prod"],
                           end=C[n]["end"],
                           cons=C[n]["cons"],
                           exp=[round(r["exp"]) for r in per[n]])
                   for n in C},
        brazil_split=dict(arabica_sur=sur(br_a), robusta_sur=sur(br_r),
                          arabica_share=C["Brazil"]["arab"]),
        surplus=dict(arabica_brazil=surplus_a_br, arabica_basket=surplus_a_basket,
                     arabica_basket_countries=SURPLUS_ARABICA,
                     robusta_vietnam=surplus_r_vn, robusta_basket=surplus_r_basket,
                     robusta_basket_countries=SURPLUS_ROBUSTA),
        stats=stats,
        fit=fit,
    )
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("// Generated by build_stocks.py - do not edit by hand.\n")
        f.write("window.STOCKS_TO_USE = ")
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write(";\n")
    print("source:", source)
    print("wrote", OUT)
    return data


if __name__ == "__main__":
    d = main()
    print(json.dumps(d["stats"], indent=1))
    print(json.dumps(d["fit"], indent=1))
    for k in ("world", "arabica_basket", "robusta_basket"):
        print(k, d[k]["sur"])
    for n in ("Brazil", "Colombia", "Vietnam", "Indonesia", "Uganda"):
        print(n, d["countries"][n]["sur"], d["countries"][n]["exp"])
    print("surplus", json.dumps(d["surplus"]))
