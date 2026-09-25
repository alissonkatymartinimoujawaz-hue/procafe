# -*- coding: utf-8 -*-
"""
Coffee demand research pack: data consolidation + analytics.

Everything the deck and the Word guide show is computed here from the source
files in data/source_files (official bulk files or verified mirrors of them) and
the search-verified rows in data/raw.  Clean tables are written to data/clean
and every headline number to output/metrics.json, so no figure is typed by hand.

Run:  python research/coffee-demand/scripts/analysis.py
"""
import csv
import json
import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.normpath(os.path.join(HERE, ".."))
SRC = os.path.join(BASE, "data", "source_files")
RAW = os.path.join(BASE, "data", "raw")
CLEAN = os.path.join(BASE, "data", "clean")
OUT = os.path.join(BASE, "output")

FIRST, LAST = 2005, 2025          # USDA marketing years 2005/06 .. 2025/26 (Dec-2025 PSD vintage)


def my(y):
    """Marketing-year label: 2005 -> '2005/06'."""
    return f"{y}/{str(y + 1)[2:]}"


def cagr(a, b, n):
    return (b / a) ** (1.0 / n) - 1.0 if (a and b and a > 0 and n) else np.nan


# ============================================================================ USDA PSD
def load_psd():
    p = pd.read_csv(os.path.join(SRC, "usda_psd_coffee_dec2025vintage_via_foodberg.csv.gz"), low_memory=False)
    return p[p.is_aggregate == 0].copy()


def psd_table(p, attribute):
    """country x market_year, million 60-kg bags."""
    t = p[p.attribute == attribute].pivot_table(index="country", columns="market_year",
                                                values="value", aggfunc="sum") / 1000.0
    t.loc["World"] = t.sum(axis=0, min_count=1)
    # EU+UK like-for-like: USDA's EU series includes the UK up to 2015/16 and excludes it after
    if "European Union" in t.index:
        uk = t.loc["United Kingdom"] if "United Kingdom" in t.index else 0
        t.loc["EU-27 + UK"] = t.loc["European Union"].add(uk.fillna(0) if hasattr(uk, "fillna") else 0)
    return t


# USDA July-2026 report ("June 2026" edition, released 22 Jul 2026) — search-verified values
USDA_JUL26 = {
    "world": {"production": 189.667, "arabica": 105.867, "robusta": 83.8, "consumption": 179.7,
              "ending_stocks": 26.3},
    "consumption": {"European Union": 42.5, "United States": 26.95, "China": 6.75},
    "consumption_yoy": {"European Union": 2.2, "United States": 5.7, "China": 5.1, "Japan": 3.7, "World": 3.6},
    "production": {"Brazil": 71.9, "Vietnam": 32.5, "Honduras": 6.0},
    "production_arabica": {"Brazil": 47.5},
    "production_robusta": {"Brazil": 24.4},
    "revisions_2025": {"bean_exports": 119.5, "bean_imports": 118.6, "EU imports": 46.5, "US imports": 23.1},
}

# Groups for the "who buys" view
TRADITIONAL = ["EU-27 + UK", "United States", "Japan", "Canada", "Switzerland", "Norway", "Australia",
               "New Zealand", "Israel", "Iceland"]


def buyer_group(country, producers):
    if country in TRADITIONAL or country in ("European Union", "United Kingdom"):
        return "Traditional importers"
    if country in producers and country not in ("China",):
        return "Producing countries"
    return "Emerging importers"


# ============================================================================ prices
def load_prices():
    """Monthly Other Milds (arabica) & Robustas, US cents/lb.
    1990-01..2025-09: IMF PCPS source file (ICO New York cash prices).
    2025-10..2026-08: ICO Coffee Market Report tables (mirror), cross-checked vs search-verified ICO values."""
    imf = pd.read_csv(os.path.join(CLEAN, "prices_monthly_imf.csv"))
    imf = imf.rename(columns={"arabica_other_milds_usc_lb": "arabica", "robusta_usc_lb": "robusta"})
    imf["source"] = "IMF PCPS (PCOFFOTM, PCOFFROB)"
    ico = pd.read_csv(os.path.join(SRC, "ico_cmr_mirror", "prices.csv"))
    ico = ico.rename(columns={"price_month": "period", "other_milds": "arabica", "robustas": "robusta"})
    add = ico[ico.period > imf.period.max()][["period", "arabica", "robusta"]].copy()
    add["source"] = "ICO Coffee Market Report (Aug-2026 vintage)"
    m = pd.concat([imf, add], ignore_index=True).sort_values("period").reset_index(drop=True)
    # ICO composite (I-CIP): from the ICO tables; drop months whose group prices disagree with IMF (parse errors)
    chk = ico.merge(imf[["period", "arabica", "robusta"]], on="period", how="left", suffixes=("", "_imf"))
    bad = (chk.arabica - chk.arabica_imf).abs().gt(1.5) | (chk.robusta - chk.robusta_imf).abs().gt(1.5)
    chk.loc[bad, "i_cip"] = np.nan
    m = m.merge(chk[["period", "i_cip", "colombian_milds", "brazilian_naturals"]], on="period", how="left")
    m["ratio"] = m.arabica / m.robusta
    m["spread"] = m.arabica - m.robusta
    m["blend"] = 0.6 * m.arabica + 0.4 * m.robusta     # simple consumption-weighted green price
    m["date"] = pd.PeriodIndex(m.period, freq="M")
    m["year"] = m.date.dt.year
    m["cy"] = np.where(m.date.dt.month >= 10, m.year, m.year - 1)   # coffee year Oct-Sep, labelled by start year
    return m


def coffee_year_prices(m):
    g = m.groupby("cy").agg(arabica=("arabica", "mean"), robusta=("robusta", "mean"), icip=("i_cip", "mean"),
                            blend=("blend", "mean"), months=("arabica", "size"))
    g["ratio"] = g.arabica / g.robusta
    g["spread"] = g.arabica - g.robusta
    g["blend_yoy"] = g.blend.pct_change() * 100
    return g


def calendar_prices(m):
    g = m.groupby("year").agg(arabica=("arabica", "mean"), robusta=("robusta", "mean"), icip=("i_cip", "mean"),
                              months=("arabica", "size"))
    g["ratio"] = g.arabica / g.robusta
    return g


# ============================================================================ ICO exports by type
def load_ico_exports():
    ex = pd.read_csv(os.path.join(SRC, "ico_cmr_mirror", "exports.csv"))
    # two months where the parsed 'arabicas' column is inconsistent with its components (PDF parse errors)
    fix = (ex.arabicas - (ex.colombian_milds + ex.other_milds + ex.brazilian_naturals)).abs() > 5
    ex.loc[fix, "arabicas"] = ex.colombian_milds + ex.other_milds + ex.brazilian_naturals
    ex["date"] = pd.PeriodIndex(ex.export_month, freq="M")
    ex["cy"] = np.where(ex.date.dt.month >= 10, ex.date.dt.year, ex.date.dt.year - 1)
    ex["rob_share"] = ex.robustas / ex.total * 100
    ex = ex.sort_values("date").reset_index(drop=True)
    ex["rob_share_12m"] = ex.robustas.rolling(12).sum() / ex.total.rolling(12).sum() * 100
    cy = ex.groupby("cy").agg(months=("total", "size"), total=("total", "sum"), arabicas=("arabicas", "sum"),
                              robustas=("robustas", "sum"), brazilian_naturals=("brazilian_naturals", "sum"),
                              colombian_milds=("colombian_milds", "sum"), other_milds=("other_milds", "sum"))
    cy["rob_share"] = cy.robustas / cy.total * 100
    return ex, cy


# ============================================================================ raw (search-verified) rows
def raw_rows(fname):
    return list(csv.DictReader(open(os.path.join(RAW, fname), encoding="utf-8")))


def pick(rows, dataset, entity=None, period=None, conf=("high", "medium")):
    out = []
    for r in rows:
        if r["dataset"] != dataset or not r["value"]:
            continue
        if entity and r["entity"] != entity:
            continue
        if period and r["period"] != period:
            continue
        if r["confidence"] not in conf:
            continue
        out.append(r)
    return out


def brazil_abic():
    d = raw_rows("D_producer_consumption.csv")
    s = {}
    for r in pick(d, "consumption_abic", "Brazil", conf=("high", "medium", "low")):
        try:
            s[int(r["period"])] = float(r["value"])
        except ValueError:
            pass
    df = pd.DataFrame({"consumption": pd.Series(s)}).sort_index()
    df["yoy"] = df.consumption.pct_change() * 100
    # ABIC-published growth rates where available (they prevail over our computed ones across the 2016 gap)
    pub = {int(r["period"]): float(r["value"]) for r in pick(d, "consumption_abic_yoy_pct", "Brazil", conf=("high", "medium"))}
    df["yoy_published"] = pd.Series(pub)
    return df


def ipca_coffee():
    f = raw_rows("F_marginal_buyers.csv")
    rows = pick(f, "retail_price_change_pct", "Brazil IPCA café moído", conf=("high", "medium", "low"))
    return [(r["period"], float(r["value"]), r["unit"], r["confidence"], r["source_url"]) for r in rows]


def starbucks():
    e = raw_rows("E_drivers.csv")
    tot = {}
    for r in pick(e, "stores_starbucks_total", "Starbucks", conf=("high", "medium")):
        per = r["period"]
        if per.startswith("FY") and len(per) == 6:
            tot[int(per[2:])] = float(r["value"])
    china = {int(r["period"][2:6]): float(r["value"]) for r in pick(e, "stores_starbucks_china", "Starbucks China", conf=("high",))
             if r["period"].startswith("FY") and len(r["period"]) == 6}
    us = {int(r["period"][2:6]): float(r["value"]) for r in pick(e, "stores_starbucks_us", "Starbucks US", conf=("high",))
          if r["period"].startswith("FY") and len(r["period"]) == 6}
    return pd.Series(tot).sort_index(), pd.Series(china).sort_index(), pd.Series(us).sort_index()


# ============================================================================ World Bank
WB_NAME = {"Korea, South": "Korea, Rep.", "Russia": "Russian Federation", "Iran": "Iran, Islamic Rep.",
           "Egypt": "Egypt, Arab Rep.", "Vietnam": "Viet Nam", "Turkey": "Turkiye", "European Union": "European Union",
           "Venezuela": "Venezuela, RB", "Yemen": "Yemen, Rep.", "Syria": "Syrian Arab Republic",
           "Congo (Kinshasa)": "Congo, Dem. Rep.", "Congo (Brazzaville)": "Congo, Rep.", "Laos": "Lao PDR",
           "Cote d'Ivoire": "Cote d'Ivoire", "Burma": "Myanmar", "Kyrgyzstan": "Kyrgyz Republic",
           "Slovakia": "Slovak Republic", "Hong Kong": "Hong Kong SAR, China", "Macedonia": "North Macedonia",
           "Bahamas, The": "Bahamas, The", "Gambia, The": "Gambia, The", "World": "World"}


def load_population():
    pop = pd.read_csv(os.path.join(SRC, "wb_population.csv"))    # World Bank SP.POP.TOTL (datahub core 'population' package)
    return pop.pivot_table(index="Country Name", columns="Year", values="Value")


def load_gdppc():
    path = os.path.join(SRC, "wb_API_NY.GDP.PCAP.CD.csv")
    g = pd.read_csv(path, skiprows=4)
    g = g.set_index("Country Name")
    cols = [c for c in g.columns if c.isdigit()]
    g = g[cols]
    g.columns = [int(c) for c in cols]
    return g


# ============================================================================ main build
def build(save=True):
    os.makedirs(CLEAN, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    M = {}   # metrics for text

    psd = load_psd()
    cons = psd_table(psd, "Domestic Consumption")
    prod = psd_table(psd, "Production")
    arab = psd_table(psd, "Arabica Production")
    robu = psd_table(psd, "Robusta Production")
    rg = psd_table(psd, "Rst,Ground Dom. Consum")
    sol = psd_table(psd, "Soluble Dom. Cons.")
    stocks = psd_table(psd, "Ending Stocks")
    bexp = psd_table(psd, "Bean Exports")
    bimp = psd_table(psd, "Bean Imports")
    rgexp = psd_table(psd, "Roast & Ground Exports")
    solexp = psd_table(psd, "Soluble Exports")
    yrs = list(range(FIRST, LAST + 1))
    producers = set(prod.index[(prod[yrs].fillna(0) > 0).any(axis=1)]) - {"World"}

    # ---------------------------------------------------------------- world balance
    W = pd.DataFrame({
        "production": prod.loc["World", yrs], "arabica": arab.loc["World", yrs], "robusta": robu.loc["World", yrs],
        "consumption": cons.loc["World", yrs], "ending_stocks": stocks.loc["World", yrs],
        "bean_exports": bexp.loc["World", yrs], "rg_consumption": rg.loc["World", yrs],
        "soluble_consumption": sol.loc["World", yrs]})
    W.loc[2026] = {"production": USDA_JUL26["world"]["production"], "arabica": USDA_JUL26["world"]["arabica"],
                   "robusta": USDA_JUL26["world"]["robusta"], "consumption": USDA_JUL26["world"]["consumption"],
                   "ending_stocks": USDA_JUL26["world"]["ending_stocks"]}
    W["label"] = [my(y) for y in W.index]
    W["cons_yoy"] = W.consumption.pct_change() * 100
    W["prod_yoy"] = W.production.pct_change() * 100
    W["surplus"] = W.production - W.consumption
    W["stock_change"] = W.ending_stocks.diff()
    W["stocks_to_use"] = W.ending_stocks / W.consumption * 100
    W["robusta_share"] = W.robusta / W.production * 100
    W["soluble_share"] = W.soluble_consumption / W.consumption * 100
    W["vintage"] = ["USDA PSD Dec-2025"] * len(yrs) + ["USDA Jul-2026 forecast"]
    M["world"] = {
        "cons_2005": W.consumption[2005], "cons_2025": W.consumption[2025], "cons_2026f": W.consumption[2026],
        "prod_2005": W.production[2005], "prod_2025": W.production[2025], "prod_2026f": W.production[2026],
        "cons_cagr_05_25": cagr(W.consumption[2005], W.consumption[2025], 20) * 100,
        "prod_cagr_05_25": cagr(W.production[2005], W.production[2025], 20) * 100,
        "cons_abs_gain_05_25": W.consumption[2025] - W.consumption[2005],
        "cons_avg_annual_gain": (W.consumption[2025] - W.consumption[2005]) / 20,
        "cons_down_years": [my(y) for y in range(2006, 2026) if W.cons_yoy[y] < 0],
        "prod_down_years": [my(y) for y in range(2006, 2026) if W.prod_yoy[y] < 0],
        "cons_yoy_sd": W.cons_yoy.loc[2006:2025].std(), "prod_yoy_sd": W.prod_yoy.loc[2006:2025].std(),
        "cons_yoy_max": W.cons_yoy.loc[2006:2025].max(), "cons_yoy_min": W.cons_yoy.loc[2006:2025].min(),
        "prod_yoy_max": W.prod_yoy.loc[2006:2025].max(), "prod_yoy_min": W.prod_yoy.loc[2006:2025].min(),
        "stocks_peak": W.ending_stocks.loc[2005:2025].max(), "stocks_peak_year": my(int(W.ending_stocks.loc[2005:2025].idxmax())),
        "stocks_2025": W.ending_stocks[2025], "stu_peak": W.stocks_to_use.loc[2005:2025].max(),
        "stu_2025": W.stocks_to_use[2025], "stocks_2026f": W.ending_stocks[2026],
        "robusta_share_2005": W.robusta_share[2005], "robusta_share_2025": W.robusta_share[2025],
        "robusta_2005": W.robusta[2005], "robusta_2025": W.robusta[2025],
        "arabica_2005": W.arabica[2005], "arabica_2025": W.arabica[2025],
        "soluble_share_2005": W.soluble_share[2005], "soluble_share_2025": W.soluble_share[2025],
    }
    periods = [(2005, 2010), (2010, 2015), (2015, 2020), (2020, 2025)]
    M["world"]["period_cagr"] = [{"period": f"{my(a)}–{my(b)}",
                                  "cons": cagr(W.consumption[a], W.consumption[b], b - a) * 100,
                                  "prod": cagr(W.production[a], W.production[b], b - a) * 100,
                                  "stock_change": W.ending_stocks[b] - W.ending_stocks[a]} for a, b in periods]
    # cumulative stock draw in the deficit run
    M["world"]["stock_draw_20_25"] = W.ending_stocks[2025] - W.ending_stocks[2020]

    # ---------------------------------------------------------------- country consumption
    C = cons.copy()
    top_now = C.drop(index=["World", "European Union", "United Kingdom"], errors="ignore")[LAST].sort_values(ascending=False)
    ctry = pd.DataFrame({
        "c2005": C[2005], "c2010": C[2010], "c2015": C[2015], "c2020": C[2020], "c2024": C[2024], "c2025": C[2025]})
    ctry["share2025"] = ctry.c2025 / C.loc["World", LAST] * 100
    ctry["cagr_05_25"] = [cagr(a, b, 20) * 100 for a, b in zip(ctry.c2005, ctry.c2025)]
    ctry["cagr_05_15"] = [cagr(a, b, 10) * 100 for a, b in zip(ctry.c2005, ctry.c2015)]
    ctry["cagr_15_20"] = [cagr(a, b, 5) * 100 for a, b in zip(ctry.c2015, ctry.c2020)]
    ctry["cagr_20_25"] = [cagr(a, b, 5) * 100 for a, b in zip(ctry.c2020, ctry.c2025)]
    ctry["yoy_2025"] = (ctry.c2025 / ctry.c2024 - 1) * 100
    ctry["delta_05_25"] = ctry.c2025 - ctry.c2005
    # smoothed (3-yr average) growth during the price spike vs the low-price years before it
    avg = lambda y0, y1: C[list(range(y0, y1 + 1))].mean(axis=1)
    ctry["avg_17_19"] = avg(2017, 2019)
    ctry["avg_23_25"] = avg(2023, 2025)
    ctry["chg_spike_3yavg"] = (ctry.avg_23_25 / ctry.avg_17_19 - 1) * 100
    ctry["min_yoy_21_25"] = (C[list(range(2021, 2026))].values / C[list(range(2020, 2025))].values - 1).min(axis=1) * 100
    ctry["down_years_21_25"] = ((C[list(range(2021, 2026))].values / C[list(range(2020, 2025))].values - 1) < 0).sum(axis=1)
    ctry["group"] = [buyer_group(c, producers) for c in ctry.index]

    # ---------------------------------------------------------------- growth contributions 2005/06 -> 2025/26
    contrib_base = ctry.drop(index=["World", "European Union", "United Kingdom"], errors="ignore").copy()
    contrib_base["delta"] = contrib_base.c2025.fillna(0) - contrib_base.c2005.fillna(0)
    contrib = contrib_base.sort_values("delta", ascending=False)
    M["contrib_total"] = contrib.delta.sum()
    M["contrib_by_group"] = contrib.groupby("group").delta.sum().to_dict()
    grp_level = {}
    for yr in yrs:
        s = C[yr].drop(index=["World", "European Union", "United Kingdom"], errors="ignore")
        grp_level[yr] = s.groupby([buyer_group(c, producers) for c in s.index]).sum()
    G = pd.DataFrame(grp_level).T
    G["label"] = [my(y) for y in G.index]

    # ---------------------------------------------------------------- per capita
    pop = load_population()
    pc = {}
    for c in ctry.index:
        wb = WB_NAME.get(c, c)
        if c in ("EU-27 + UK", "European Union", "United Kingdom"):
            continue            # EU/UK handled together below (USDA EU series changes perimeter in 2016)
        if wb in pop.index:
            p05 = pop.loc[wb, 2005] if 2005 in pop.columns else np.nan
            p24 = pop.loc[wb, 2024] if 2024 in pop.columns else np.nan
            pc[c] = {"pop2005": p05, "pop2024": p24,
                     "kg2005": C.loc[c, 2005] * 1e6 * 60 / p05 if p05 and not np.isnan(C.loc[c, 2005]) else np.nan,
                     "kg2024": C.loc[c, 2024] * 1e6 * 60 / p24 if p24 and not np.isnan(C.loc[c, 2024]) else np.nan}
    # EU+UK per capita from the EU-27 aggregate + UK populations
    if "European Union" in pop.index and "United Kingdom" in pop.index:
        p24 = pop.loc["European Union", 2024] + pop.loc["United Kingdom", 2024]
        p05 = pop.loc["European Union", 2005] + pop.loc["United Kingdom", 2005]
        pc["EU-27 + UK"] = {"pop2024": p24, "kg2024": ctry.loc["EU-27 + UK", "c2024"] * 1e6 * 60 / p24,
                            "pop2005": p05, "kg2005": ctry.loc["EU-27 + UK", "c2005"] * 1e6 * 60 / p05}
    PC = pd.DataFrame(pc).T
    wp05, wp24 = pop.loc["World", 2005], pop.loc["World", 2024]
    M["pop"] = {"world_2005": wp05, "world_2024": wp24,
                "kg_world_2005": W.consumption[2005] * 1e6 * 60 / wp05, "kg_world_2024": W.consumption[2024] * 1e6 * 60 / wp24}
    # decomposition of world growth 2005/06 -> 2024/25: population vs per-capita
    g_tot = W.consumption[2024] / W.consumption[2005]
    g_pop = wp24 / wp05
    g_pc = g_tot / g_pop
    M["decomp"] = {"total_pct": (g_tot - 1) * 100, "pop_pct": (g_pop - 1) * 100, "pc_pct": (g_pc - 1) * 100,
                   "pop_share_of_growth": np.log(g_pop) / np.log(g_tot) * 100,
                   "pc_share_of_growth": np.log(g_pc) / np.log(g_tot) * 100}

    # ---------------------------------------------------------------- income
    try:
        gdp = load_gdppc()
    except Exception:  # noqa: BLE001
        gdp = None
    INC = None
    if gdp is not None:
        rows = []

        def latest(wb, upto):
            ser = gdp.loc[wb, [y for y in gdp.columns if y <= upto]].dropna()
            return (ser.iloc[-1], int(ser.index[-1])) if len(ser) else (np.nan, None)
        for c in PC.index:
            wb = "European Union" if c == "EU-27 + UK" else WB_NAME.get(c, c)
            if wb in gdp.index:
                g24, y24 = latest(wb, 2024)
                rows.append({"country": c, "gdppc2005": gdp.loc[wb, 2005], "gdppc2024": g24, "gdp_year": y24,
                             "kg2005": PC.loc[c, "kg2005"], "kg2024": PC.loc[c, "kg2024"],
                             "cons2005": C.loc[c, 2005] if c in C.index else np.nan, "cons2024": C.loc[c, 2024]})
        INC = pd.DataFrame(rows).set_index("country")

    # ---------------------------------------------------------------- prices
    m = load_prices()
    cyp = coffee_year_prices(m)
    calp = calendar_prices(m)
    M["prices"] = {
        "last_month": m.period.max(),
        "arabica_peak": m.arabica.max(), "arabica_peak_month": m.loc[m.arabica.idxmax(), "period"],
        "robusta_peak": m.robusta.max(), "robusta_peak_month": m.loc[m.robusta.idxmax(), "period"],
        "arabica_low_2015_20": m[(m.year >= 2015) & (m.year <= 2020)].arabica.min(),
        "arabica_low_2015_20_month": m.loc[m[(m.year >= 2015) & (m.year <= 2020)].arabica.idxmin(), "period"],
        "robusta_low_2015_20": m[(m.year >= 2015) & (m.year <= 2020)].robusta.min(),
        "robusta_low_2015_20_month": m.loc[m[(m.year >= 2015) & (m.year <= 2020)].robusta.idxmin(), "period"],
        "arabica_last": m.arabica.iloc[-1], "robusta_last": m.robusta.iloc[-1],
        "ratio_last": m.ratio.iloc[-1], "spread_last": m.spread.iloc[-1],
        "icip_peak": m.i_cip.max(), "icip_peak_month": m.loc[m.i_cip.idxmax(), "period"], "icip_last": m.i_cip.dropna().iloc[-1],
        "ratio_min_2010": m[m.year >= 2010].ratio.min(), "ratio_min_2010_month": m.loc[m[m.year >= 2010].ratio.idxmin(), "period"],
        "ratio_max_2010": m[m.year >= 2010].ratio.max(), "ratio_max_2010_month": m.loc[m[m.year >= 2010].ratio.idxmax(), "period"],
        "cy": {int(k): {"arabica": v.arabica, "robusta": v.robusta, "blend": v.blend, "ratio": v.ratio,
                        "months": int(v.months)} for k, v in cyp.loc[2005:].iterrows()},
    }
    pre = cyp.loc[2015:2019, "blend"].mean()
    spike = cyp.loc[2021:2025, "blend"].mean()
    M["prices"]["blend_avg_15_19"] = pre
    M["prices"]["blend_avg_21_25"] = spike
    M["prices"]["blend_change_pct"] = (spike / pre - 1) * 100
    M["prices"]["blend_17_19"] = cyp.loc[2017:2019, "blend"].mean()
    M["prices"]["blend_23_25"] = cyp.loc[2023:2025, "blend"].mean()
    M["prices"]["blend_change_3yavg_pct"] = (M["prices"]["blend_23_25"] / M["prices"]["blend_17_19"] - 1) * 100

    # ---------------------------------------------------------------- elasticity (short-run, pooled per country)
    lp = np.log(cyp.blend)
    EL = []
    for c in ctry.index:
        if c in ("World", "European Union", "United Kingdom"):
            continue
        s = C.loc[c, list(range(2006, LAST + 1))]
        if s.isna().any() or (C.loc[c, 2025] or 0) < 0.8:
            continue
        dl = np.log(C.loc[c, list(range(2006, LAST + 1))].values) - np.log(C.loc[c, list(range(2005, LAST))].values)
        dp = (lp.loc[2006:LAST].values - lp.loc[2005:LAST - 1].values)
        dp_lag = (lp.loc[2005:LAST - 1].values - lp.loc[2004:LAST - 2].values)
        X = np.column_stack([np.ones_like(dp), dp, dp_lag])
        beta, *_ = np.linalg.lstsq(X, dl, rcond=None)
        resid = dl - X @ beta
        n, k = X.shape
        s2 = resid @ resid / (n - k)
        cov = s2 * np.linalg.inv(X.T @ X)
        se = np.sqrt(np.diag(cov))
        EL.append({"country": c, "trend_pct": beta[0] * 100, "e_same_year": beta[1], "e_lag1": beta[2],
                   "e_total": beta[1] + beta[2], "se_total": np.sqrt(cov[1, 1] + cov[2, 2] + 2 * cov[1, 2]),
                   "n": n})
    EL = pd.DataFrame(EL).set_index("country")

    # ---------------------------------------------------------------- ICO exports by type (switching)
    ex, excy = load_ico_exports()
    excy = excy.join(cyp[["ratio", "spread", "arabica", "robusta"]], how="left")
    M["switch"] = {int(k): {"rob_share": v.rob_share, "ratio": v.ratio, "months": int(v.months),
                            "total_mbags": v.total / 1000} for k, v in excy.iterrows() if v.months >= 8}

    # ---------------------------------------------------------------- producers
    P = prod.copy()
    PR = pd.DataFrame({"p2005": P[2005], "p2010": P[2010], "p2015": P[2015], "p2020": P[2020], "p2024": P[2024],
                       "p2025": P[2025]})
    PR["avg_16_18"] = P[[2016, 2017, 2018]].mean(axis=1)
    PR["avg_19_21"] = P[[2019, 2020, 2021]].mean(axis=1)        # output after the 2018-19 price low
    PR["avg_22_25"] = P[[2022, 2023, 2024, 2025]].mean(axis=1)  # output during/after the price spike
    PR["low_price_resp"] = (PR.avg_19_21 / PR.avg_16_18 - 1) * 100
    PR["high_price_resp"] = (PR.avg_22_25 / PR.avg_19_21 - 1) * 100
    PR["cagr_05_25"] = [cagr(a, b, 20) * 100 for a, b in zip(P[[2004, 2005, 2006]].mean(axis=1), P[[2023, 2024, 2025]].mean(axis=1))]
    PR["share2025"] = PR.p2025 / P.loc["World", 2025] * 100
    PR["robusta_share2025"] = robu[2025] / P[2025] * 100
    PR["p2026f"] = pd.Series({k: v for k, v in USDA_JUL26["production"].items()})

    # ---------------------------------------------------------------- R&G / soluble / trade formats
    FMT = pd.DataFrame({
        "rg_world": rg.loc["World", yrs], "sol_world": sol.loc["World", yrs],
        "swiss_rg_exports": rgexp.loc["Switzerland", yrs] if "Switzerland" in rgexp.index else np.nan,
        "world_rg_exports": rgexp.loc["World", yrs], "world_sol_exports": solexp.loc["World", yrs]})

    # ---------------------------------------------------------------- ICO world (coffee years) from A
    a_rows = raw_rows("A_world_balance.csv")
    ico_cons = {r["period"]: float(r["value"]) for r in a_rows if r["dataset"] == "world_consumption_ico"
                and r["value"] and "10 Sep 2026" in (r["notes"] + r["source_title"]) or False}
    ico_region = {}
    for r in a_rows:
        if r["dataset"] == "consumption_region_ico" and r["value"] and r["confidence"] == "high":
            ico_region.setdefault(r["entity"], {})[r["period"]] = float(r["value"])

    # ---------------------------------------------------------------- Brazil
    bra = brazil_abic()
    sb_tot, sb_china, sb_us = starbucks()

    if save:
        W.to_csv(os.path.join(CLEAN, "world_balance_usda.csv"))
        cons.to_csv(os.path.join(CLEAN, "consumption_by_country_usda.csv"))
        prod.to_csv(os.path.join(CLEAN, "production_by_country_usda.csv"))
        arab.to_csv(os.path.join(CLEAN, "production_arabica_by_country_usda.csv"))
        robu.to_csv(os.path.join(CLEAN, "production_robusta_by_country_usda.csv"))
        ctry.to_csv(os.path.join(CLEAN, "consumption_country_metrics.csv"))
        contrib.to_csv(os.path.join(CLEAN, "consumption_growth_contributions.csv"))
        G.to_csv(os.path.join(CLEAN, "consumption_by_buyer_group.csv"))
        PC.to_csv(os.path.join(CLEAN, "per_capita_kg.csv"))
        if INC is not None:
            INC.to_csv(os.path.join(CLEAN, "income_vs_consumption.csv"))
        m.drop(columns=["date"]).to_csv(os.path.join(CLEAN, "prices_monthly.csv"), index=False)
        cyp.to_csv(os.path.join(CLEAN, "prices_coffee_year.csv"))
        calp.to_csv(os.path.join(CLEAN, "prices_calendar_year.csv"))
        EL.to_csv(os.path.join(CLEAN, "elasticity_estimates.csv"))
        ex.drop(columns=["date"]).to_csv(os.path.join(CLEAN, "ico_exports_monthly.csv"), index=False)
        excy.to_csv(os.path.join(CLEAN, "ico_exports_coffee_year.csv"))
        PR.to_csv(os.path.join(CLEAN, "producer_metrics.csv"))
        FMT.to_csv(os.path.join(CLEAN, "formats_rg_soluble.csv"))
        bra.to_csv(os.path.join(CLEAN, "brazil_abic_consumption.csv"))
        with open(os.path.join(OUT, "metrics.json"), "w") as f:
            json.dump(M, f, indent=1, default=lambda o: float(o) if isinstance(o, (np.floating, np.integer)) else str(o))

    return dict(W=W, cons=cons, prod=prod, arab=arab, robu=robu, rg=rg, sol=sol, stocks=stocks, ctry=ctry,
                contrib=contrib, G=G, PC=PC, INC=INC, m=m, cyp=cyp, calp=calp, EL=EL, ex=ex, excy=excy, PR=PR,
                FMT=FMT, bra=bra, sb_tot=sb_tot, sb_china=sb_china, sb_us=sb_us, ico_region=ico_region,
                producers=producers, M=M, rgexp=rgexp, solexp=solexp, bimp=bimp, bexp=bexp)


if __name__ == "__main__":
    A = build()
    M = A["M"]
    print(json.dumps({k: v for k, v in M["world"].items() if not isinstance(v, list)}, indent=1, default=str)[:3000])


# ============================================================================ retail prices (consumer side)
def retail_series():
    """US CPI 'coffee' (BLS, index 1982-84=100) and Brazil IPCA 'café moído' (IBGE) rows collected in B_prices.csv.
    Both are official statistics read from public copies of the official releases (confidence: medium)."""
    b = raw_rows("B_prices.csv")
    us_idx = {int(r["period"]): float(r["value"]) for r in b
              if r["dataset"] == "retail_cpi_us_coffee_index" and r["value"] and len(r["period"]) == 4}
    us_yoy = {r["period"]: float(r["value"]) for r in b
              if r["dataset"] in ("retail_cpi_us_coffee", "retail_cpi_us_coffee_yoy") and r["value"]}
    br_idx = {r["period"]: float(r["value"]) for r in b
              if r["dataset"] == "retail_ipca_brazil_cafe_moido_index" and r["value"]}
    br_dec = {r["period"]: float(r["value"]) for r in b
              if r["dataset"] == "retail_ipca_brazil_cafe_moido" and r["value"]}
    return (pd.Series(us_idx).sort_index(), us_yoy, pd.Series(br_idx).sort_index(), br_dec)
