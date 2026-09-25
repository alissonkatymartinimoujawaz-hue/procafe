# -*- coding: utf-8 -*-
"""Static (PNG) versions of the deck's charts for the Word learning guide.

Same data, same colours as the PowerPoint (see pptx_kit.C); one axis per panel.
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt          # noqa: E402
from matplotlib import font_manager      # noqa: E402
import numpy as np                       # noqa: E402

from pptx_kit import C                   # noqa: E402
import analysis as an                    # noqa: E402

FIG = os.path.join(an.BASE, "output", "charts")
os.makedirs(FIG, exist_ok=True)

_fams = {f.name for f in font_manager.fontManager.ttflist}
FONT = "Calibri" if "Calibri" in _fams else ("Carlito" if "Carlito" in _fams else "DejaVu Sans")
plt.rcParams.update({"axes.unicode_minus": True, 
    "font.family": FONT, "font.size": 9, "axes.edgecolor": "#" + C["axis"], "axes.linewidth": 0.8,
    "axes.labelcolor": "#" + C["ink2"], "xtick.color": "#" + C["muted"], "ytick.color": "#" + C["muted"],
    "axes.grid": True, "grid.color": "#" + C["grid"], "grid.linewidth": 0.6, "axes.axisbelow": True,
    "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False, "figure.dpi": 100,
})


def h(c):
    return "#" + C.get(c, c)


def short(y):
    return f"{y % 100:02d}/{(y + 1) % 100:02d}"


def finish(fig, name, title, subtitle=None, source=None):
    """Reserve fixed space (in inches) for title, subtitle and source, then save."""
    H = fig.get_figheight()
    fig.tight_layout(rect=(0, 0.32 / H, 1, 1 - 0.72 / H))
    fig.text(0.01, 1 - 0.06 / H, title, ha="left", va="top", fontsize=12, fontweight="bold", color=h("espresso"))
    if subtitle:
        fig.text(0.01, 1 - 0.34 / H, subtitle, ha="left", va="top", fontsize=8.5, color=h("ink2"))
    if source:
        fig.text(0.01, 0.04 / H, "Source: " + source, ha="left", va="bottom", fontsize=7, color=h("muted"))
    path = os.path.join(FIG, name + ".png")
    fig.savefig(path, dpi=200, facecolor="white")
    plt.close(fig)
    return path


def ygrid_only(ax):
    ax.grid(axis="x", visible=False)


USDA = "USDA FAS PSD (Dec-2025 release) & USDA Coffee: World Markets and Trade (Jul-2026)"
PRICES = "IMF Primary Commodity Prices / ICO Coffee Market Reports"


def make_all(A):
    W, M, ctry, cons, cyp, m = A["W"], A["M"], A["ctry"], A["cons"], A["cyp"], A["m"]
    out = {}
    yrs = list(range(2005, 2026))
    yrs_f = yrs + [2026]
    xl = [short(y) for y in yrs_f]
    x = np.arange(len(xl))

    # 1 world demand + yoy -------------------------------------------------------
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.6, 4.4), gridspec_kw={"height_ratios": [2.2, 1]}, sharex=True)
    v = [W.consumption[y] for y in yrs_f]
    cols = [h("demand")] * (len(v) - 1) + ["#9C93D6"]
    a1.bar(x, v, color=cols, width=0.72)
    for i in (0, len(v) - 1):
        a1.text(x[i], v[i] + 3, f"{v[i]:.1f}" + ("F" if i == len(v) - 1 else ""), ha="center", fontsize=7.5, color=h("ink"))
    a1.set_ylim(0, 200); a1.set_ylabel("million bags"); ygrid_only(a1)
    yy = [W.cons_yoy[y] for y in yrs_f]
    a2.bar(x, [0 if np.isnan(t) else t for t in yy], color=[h("decline") if (not np.isnan(t) and t < 0) else h("demand") for t in yy], width=0.72)
    a2.axhline(0, color=h("axis"), lw=0.8); a2.set_ylabel("y/y %"); ygrid_only(a2)
    a2.set_xticks(x[::2]); a2.set_xticklabels(xl[::2], fontsize=7.5)
    out["world_demand"] = finish(fig, "01_world_demand", "World coffee consumption, 2005/06–2026/27F",
                                 "Million 60-kg bags (top) and year-on-year change, % (bottom); 2026/27 = USDA forecast", USDA)

    # 2 production vs consumption + stock change ------------------------------------
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.6, 4.4), gridspec_kw={"height_ratios": [2, 1]}, sharex=True)
    a1.plot(x, [W.production[y] for y in yrs_f], color=h("supply"), lw=2, label="Production")
    a1.plot(x, v, color=h("demand"), lw=2, label="Consumption")
    a1.set_ylim(100, 200); a1.legend(loc="upper left", ncol=2); a1.set_ylabel("million bags"); ygrid_only(a1)
    sc = [W.stock_change[y] if y <= 2025 else np.nan for y in yrs_f]
    a2.bar(x, [0 if np.isnan(t) else t for t in sc], color=[h("deficit") if (not np.isnan(t) and t < 0) else h("surplus") for t in sc], width=0.72)
    a2.axhline(0, color=h("axis"), lw=0.8); a2.set_ylabel("stock change"); ygrid_only(a2)
    a2.set_xticks(x[::2]); a2.set_xticklabels(xl[::2], fontsize=7.5)
    out["supply_demand"] = finish(fig, "02_supply_vs_demand", "Production vs consumption, and the change in world stocks",
                                  "Million 60-kg bags; red bars = stock draws", USDA)

    # 3 period CAGR -------------------------------------------------------------------
    pc = M["world"]["period_cagr"]
    fig, ax = plt.subplots(figsize=(6.6, 3.2))
    xi = np.arange(len(pc)); w = 0.36
    b1 = ax.bar(xi - w / 2, [p["cons"] for p in pc], w, color=h("demand"), label="Consumption")
    b2 = ax.bar(xi + w / 2, [p["prod"] for p in pc], w, color=h("supply"), label="Production")
    for bars in (b1, b2):
        for b in bars:
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.06, f"{b.get_height():.1f}%", ha="center", fontsize=8)
    ax.set_xticks(xi); ax.set_xticklabels([p["period"] + f"\nstocks {p['stock_change']:+.1f}m" for p in pc], fontsize=8)
    ax.set_ylim(0, 4.5); ax.set_ylabel("% per year"); ax.legend(loc="upper right", ncol=2); ygrid_only(ax)
    out["period_cagr"] = finish(fig, "03_period_cagr", "Growth by 5-year period: demand steady, supply lumpy",
                                "Compound annual growth, %; label under each period = change in world ending stocks", USDA)

    # 4 stocks-to-use & prices ----------------------------------------------------------
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.6, 4.4), sharex=True)
    stu = [W.stocks_to_use[y] for y in yrs_f]
    a1.bar(x, stu, color=[h("deficit") if s_ < 16 else h("steady") for s_ in stu], width=0.72)
    a1.set_ylabel("stocks-to-use %"); a1.set_ylim(0, 40); ygrid_only(a1)
    a2.plot(x[:-1], [cyp.arabica[y] for y in yrs], color=h("arabica"), lw=2, label="Arabica (Other Milds)")
    a2.plot(x[:-1], [cyp.robusta[y] for y in yrs], color=h("robusta"), lw=2, label="Robusta")
    a2.set_ylabel("US c/lb"); a2.legend(loc="upper left"); ygrid_only(a2)
    a2.set_xticks(x[::2]); a2.set_xticklabels(xl[::2], fontsize=7.5)
    out["stocks_prices"] = finish(fig, "04_stocks_prices", "Tight stocks, high prices",
                                  "World ending stocks as % of consumption (top); coffee-year average prices, US c/lb (bottom)", USDA + "; " + PRICES)

    # 5 top consumers ----------------------------------------------------------------
    t = ctry.drop(index=["World", "European Union", "United Kingdom"]).sort_values("c2025", ascending=False).head(15)[::-1]
    fig, ax = plt.subplots(figsize=(6.6, 4.6))
    yi = np.arange(len(t))
    ax.barh(yi + 0.2, t.c2025, 0.4, color=h("demand"), label="2025/26")
    ax.barh(yi - 0.2, t.c2005.fillna(0), 0.4, color="#C9C7C0", label="2005/06")
    for i, (c, r) in enumerate(t.iterrows()):
        ax.text(r.c2025 + 0.4, i + 0.2, f"{r.c2025:.1f} ({r.share2025:.1f}%)", va="center", fontsize=7.5)
    ax.set_yticks(yi); ax.set_yticklabels([c.replace("Korea, South", "South Korea") for c in t.index], fontsize=8)
    ax.set_xlim(0, 60); ax.legend(loc="lower right"); ax.grid(axis="y", visible=False); ax.set_xlabel("million bags")
    out["top_consumers"] = finish(fig, "05_top_consumers", "Who consumes the most: top 15, 2025/26 vs 2005/06",
                                  "Million 60-kg bags; label = 2025/26 volume (share of world)", USDA)

    # 6 growth contributions ------------------------------------------------------------
    contrib = A["contrib"]
    import pandas as pd
    sel = pd.concat([contrib[contrib.delta > 0].head(14), contrib[contrib.delta < -0.2].sort_values("delta")])[::-1]
    gcol = {"Producing countries": "#EDA100", "Emerging importers": "#E87BA4", "Traditional importers": h("demand")}
    fig, ax = plt.subplots(figsize=(6.6, 4.8))
    yi = np.arange(len(sel))
    ax.barh(yi, sel.delta, color=[gcol[g] for g in sel.group], height=0.7)
    for i, dv in enumerate(sel.delta):
        ax.text(dv + (0.1 if dv >= 0 else -0.1), i, f"{dv:+.1f}".replace("-", "\u2212"), va="center", ha="left" if dv >= 0 else "right", fontsize=7.5)
    ax.set_yticks(yi); ax.set_yticklabels(sel.index, fontsize=8); ax.axvline(0, color=h("axis"), lw=0.8)
    ax.grid(axis="y", visible=False); ax.set_xlabel("change in consumption, million bags")
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=v_, label=k) for k, v_ in gcol.items()], loc="lower right", fontsize=8)
    out["contributions"] = finish(fig, "06_growth_contributions", "Where the growth came from, 2005/06 → 2025/26",
                                  "Change in consumption by country, million bags; colour = buyer group", USDA)

    # 7 buyer groups -------------------------------------------------------------------
    G = A["G"]
    fig, ax = plt.subplots(figsize=(6.6, 3.6))
    xg = np.arange(len(yrs)); bottom = np.zeros(len(yrs))
    for g in ["Traditional importers", "Emerging importers", "Producing countries"]:
        vals = np.array([G.loc[y, g] for y in yrs])
        ax.bar(xg, vals, bottom=bottom, color=gcol[g], label=g, width=0.75)
        bottom += vals
    ax.set_xticks(xg[::2]); ax.set_xticklabels([short(y) for y in yrs][::2], fontsize=7.5); ax.legend(loc="upper left", fontsize=8, ncol=3)
    ax.set_ylim(0, 200); ax.set_ylabel("million bags"); ygrid_only(ax)
    out["buyer_groups"] = finish(fig, "07_buyer_groups", "World consumption by buyer group",
                                 "Traditional importers = EU+UK, US, Japan, Canada, Switzerland, Norway, Australia…", USDA)

    # 8 per capita vs income ---------------------------------------------------------------
    INC = A["INC"].copy()
    INC = INC[(INC.cons2024 >= 0.7) & INC.gdppc2024.notna() & INC.kg2024.notna()].drop(index=["World"], errors="ignore")
    fig, ax = plt.subplots(figsize=(6.6, 4.0))
    for c, r in INC.iterrows():
        g = ctry.loc[c, "group"] if c in ctry.index else "Emerging importers"
        ax.scatter(r.gdppc2024, r.kg2024, s=40, color=gcol[g], edgecolor="white", lw=0.8, zorder=3)
        if c in {"China", "India", "Indonesia", "United States", "EU-27 + UK", "Brazil", "Japan", "Vietnam", "Korea, South", "Canada",
                 "Norway", "Switzerland", "Philippines", "Turkey", "Russia", "Ethiopia", "Algeria"}:
            ax.annotate(c.replace("Korea, South", "Korea"), (r.gdppc2024, r.kg2024), xytext=(4, 2), textcoords="offset points", fontsize=7.5)
    ax.set_xscale("log"); ax.set_xlim(500, 150000); ax.set_ylim(0, 10)
    from matplotlib.ticker import FuncFormatter
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f}"))
    ax.set_xlabel("GDP per capita, current US$ (2024, log scale)"); ax.set_ylabel("kg green coffee per person")
    out["per_capita"] = finish(fig, "08_per_capita_income", "Coffee per person vs income",
                               "kg of green coffee per person per year (2024/25) vs GDP per capita", USDA + "; World Bank WDI")

    # 9 formats ------------------------------------------------------------------------------
    FMT = A["FMT"]
    fig, ax = plt.subplots(figsize=(6.6, 3.4))
    rgv = np.array([FMT.rg_world[y] for y in yrs]); sv = np.array([FMT.sol_world[y] for y in yrs])
    ax.bar(xg, rgv, color=h("demand"), label="Roast & ground", width=0.75)
    ax.bar(xg, sv, bottom=rgv, color="#E87BA4", label="Soluble (instant)", width=0.75)
    for i in (0, 10, 20):
        ax.text(xg[i], rgv[i] + sv[i] + 2, f"{sv[i] / (sv[i] + rgv[i]) * 100:.0f}%", ha="center", fontsize=8)
    ax.set_xticks(xg[::2]); ax.set_xticklabels([short(y) for y in yrs][::2], fontsize=7.5); ax.legend(loc="upper left", ncol=2)
    ax.set_ylim(0, 200); ax.set_ylabel("million bags"); ygrid_only(ax)
    out["formats"] = finish(fig, "09_formats", "Roast & ground vs instant (soluble)", "World consumption, million bags; label = soluble share", USDA)

    # 10 prices monthly ---------------------------------------------------------------------------
    mm = m[m.period >= "2010-01"].reset_index(drop=True)
    xm = np.arange(len(mm))
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.6, 4.4), gridspec_kw={"height_ratios": [2.2, 1]}, sharex=True)
    a1.plot(xm, mm.arabica, color=h("arabica"), lw=1.6, label="Arabica (ICO Other Milds)")
    a1.plot(xm, mm.robusta, color=h("robusta"), lw=1.6, label="Robusta (ICO Robustas)")
    a1.legend(loc="upper left"); a1.set_ylabel("US c/lb"); a1.set_ylim(0, 450); ygrid_only(a1)
    a2.plot(xm, mm.ratio, color=h("ink2"), lw=1.3); a2.axhline(2.0, color=h("deficit"), lw=0.9, ls="--")
    a2.set_ylabel("ratio ×"); a2.set_ylim(1, 3); ygrid_only(a2)
    jan = [i for i, p in enumerate(mm.period) if p.endswith("-01")]
    a2.set_xticks(jan[::2]); a2.set_xticklabels([mm.period[i][:4] for i in jan][::2], fontsize=7.5)
    out["prices"] = finish(fig, "10_prices", "Arabica and robusta prices, Jan-2010 → Aug-2026",
                           "Monthly averages, US cents/lb (top); arabica ÷ robusta ratio (bottom, dashed = 2.0×)", PRICES)

    # 11 elasticities -----------------------------------------------------------------------------
    EL = A["EL"].join(ctry[["c2025"]]).sort_values("c2025", ascending=False).head(16).sort_values("e_total")
    fig, ax = plt.subplots(figsize=(6.6, 4.4))
    yi = np.arange(len(EL))
    sig = (EL.e_total + 1.96 * EL.se_total) < 0
    ax.errorbar(EL.e_total, yi, xerr=1.96 * EL.se_total, fmt="none", ecolor="#C9C7C0", elinewidth=2, capsize=0)
    ax.scatter(EL.e_total, yi, color=[h("decline") if s_ else h("ink2") for s_ in sig], zorder=3, s=30)
    ax.axvline(0, color=h("axis"), lw=0.8)
    ax.set_yticks(yi); ax.set_yticklabels([c.replace("Korea, South", "South Korea") for c in EL.index], fontsize=8)
    ax.set_xlim(-2.2, 1.0); ax.grid(axis="y", visible=False); ax.set_xlabel("elasticity of consumption to the green price (±95% range)")
    out["elasticity"] = finish(fig, "11_elasticity", "Short-run price elasticities are close to zero",
                               "Regression of Δln(consumption) on Δln(green price), same year + 1-year lag, 2006/07–2025/26; red = significant",
                               USDA + "; " + PRICES + "; own estimate")

    # 12 brazil -----------------------------------------------------------------------------------
    us_idx, us_yoy, br_idx, br_dec = an.retail_series()
    bra = A["bra"]
    yb = list(range(2020, 2026))
    cats_b = [str(y) for y in yb] + ["2026 YTD"]
    ipca = [br_dec[str(y)] for y in yb] + [br_dec["2026"]]
    vol = [bra.yoy_published.get(y) for y in yb] + [2.29]
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.6, 4.0), sharex=True)
    xb = np.arange(len(cats_b))
    a1.bar(xb, ipca, color=[h("decline") if v_ > 0 else "#B5B3AC" for v_ in ipca], width=0.6)
    for i, v_ in enumerate(ipca):
        a1.text(i, v_ + (2 if v_ > 0 else -6), f"{v_:+.0f}%".replace("-", "\u2212"), ha="center", fontsize=8)
    a1.axhline(0, color=h("axis"), lw=0.8); a1.set_ylabel("retail price %"); a1.set_ylim(-25, 62); ygrid_only(a1)
    a2.bar(xb, vol, color=[h("decline") if v_ < 0 else "#EDA100" for v_ in vol], width=0.6)
    for i, v_ in enumerate(vol):
        a2.text(i, v_ + (0.15 if v_ > 0 else -0.45), f"{v_:+.1f}%".replace("-", "\u2212"), ha="center", fontsize=8)
    a2.axhline(0, color=h("axis"), lw=0.8); a2.set_ylabel("volume y/y %"); a2.set_ylim(-3, 3.2); ygrid_only(a2)
    a2.set_xticks(xb); a2.set_xticklabels(cats_b, fontsize=8)
    out["brazil"] = finish(fig, "12_brazil_threshold", "Brazil: retail price inflation vs consumption",
                           "IPCA ground coffee, % Dec/Dec (top); ABIC consumption, % y/y (bottom); 2026 = year to date",
                           "IBGE IPCA; ABIC Indicadores da Indústria de Café")

    # 13 switching -----------------------------------------------------------------------------------
    ex = A["ex"]; ex = ex[ex.rob_share_12m.notna()].reset_index(drop=True)
    rmap = dict(zip(m.period, m.ratio))
    xe = np.arange(len(ex))
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.6, 4.2), sharex=True)
    a1.plot(xe, ex.rob_share_12m, color=h("robusta"), lw=2); a1.set_ylabel("robusta share %"); ygrid_only(a1)
    a2.plot(xe, [rmap.get(p) for p in ex.export_month], color=h("arabica"), lw=1.6)
    a2.axhline(1.8, color=h("deficit"), lw=0.9, ls="--"); a2.set_ylabel("arabica ÷ robusta"); ygrid_only(a2)
    jan = [i for i, p in enumerate(ex.export_month) if p.endswith("-01")]
    a2.set_xticks(jan); a2.set_xticklabels([ex.export_month[i][:4] for i in jan], fontsize=7.5)
    out["switching"] = finish(fig, "13_switching", "Bean switching: robusta's share of world exports vs the price ratio",
                              "12-month rolling robusta share of exports, % (top, ICO); arabica ÷ robusta ratio (bottom, dashed = 1.8×)", PRICES)

    # 14 production small multiples ---------------------------------------------------------------------
    PR, prod = A["PR"], A["prod"]
    origins = ["Brazil", "Vietnam", "Colombia", "Indonesia", "Ethiopia", "Uganda", "Honduras", "India"]
    fig, axs = plt.subplots(2, 4, figsize=(6.8, 3.8))
    for ax, o in zip(axs.flat, origins):
        vals = [prod.loc[o, y] for y in yrs]
        ax.bar(np.arange(len(yrs)), vals, color=h("supply"), width=0.8)
        if not np.isnan(PR.loc[o, "p2026f"]):
            ax.bar(len(yrs), PR.loc[o, "p2026f"], color="#8FD9BE", width=0.8)
        ax.set_title(o, fontsize=9, loc="left", fontweight="bold")
        ax.set_xticks([0, 10, 20]); ax.set_xticklabels(["05/06", "15/16", "25/26"], fontsize=6.5); ax.tick_params(axis="y", labelsize=6.5)
        ygrid_only(ax)
    out["production"] = finish(fig, "14_production_origins", "Production by origin, 2005/06–2026/27F", "Million bags; light bar = USDA 2026/27 forecast", USDA)

    # 15 producer response map ------------------------------------------------------------------------------
    from build_deck import producer_class
    PRr = PR.drop(index=["World", "EU-27 + UK", "European Union"], errors="ignore"); PRr = PRr[PRr.p2025 >= 0.4]
    pcls = producer_class(PRr)
    ccol = {"Produce regardless": h("demand"), "Cut when low": "#EDA100", "Decline regardless": h("decline"), "Expand when high": h("supply")}
    fig, ax = plt.subplots(figsize=(6.6, 4.4))
    for c, r in PRr.iterrows():
        ax.scatter(r.low_price_resp, r.high_price_resp, s=max(20, r.p2025 * 6), color=ccol[pcls[c]], edgecolor="white", zorder=3)
        ax.annotate(c.replace("Papua New Guinea", "PNG").replace("Cote d'Ivoire", "Côte d'Ivoire"), (r.low_price_resp, r.high_price_resp),
                    xytext=(4, 2), textcoords="offset points", fontsize=7)
    ax.axvline(0, color=h("axis"), lw=0.8); ax.axhline(0, color=h("axis"), lw=0.8)
    ax.set_xlabel("output after the 2018–19 low, % (3-yr avg vs 3-yr avg)"); ax.set_ylabel("output during the 2022–25 boom, %")
    ax.legend(handles=[Patch(color=v_, label=k) for k, v_ in ccol.items()], loc="lower left", fontsize=7.5)
    out["producer_map"] = finish(fig, "15_producer_map", "Producer response map", "Bubble size = 2025/26 production", USDA)

    # 16 retail pass-through US -----------------------------------------------------------------------------
    calp = A["calp"]; blend = 0.6 * calp.arabica + 0.4 * calp.robusta
    yu = list(range(2010, 2025))
    fig, ax = plt.subplots(figsize=(6.6, 3.2))
    ax.plot(yu, [blend[y] / blend[2019] * 100 for y in yu], color=h("arabica"), lw=2, marker="o", ms=3, label="Green coffee (0.6 arabica + 0.4 robusta)")
    ax.plot(yu, [us_idx[y] / us_idx[2019] * 100 for y in yu], color=h("demand"), lw=2, marker="o", ms=3, label="US retail coffee (CPI)")
    ax.set_ylabel("index 2019 = 100"); ax.legend(loc="upper left"); ygrid_only(ax)
    out["passthrough"] = finish(fig, "16_passthrough_us", "US shelf prices move far less than green coffee",
                                "Index 2019 = 100, calendar-year averages", "BLS CPI (coffee); " + PRICES)
    return out


if __name__ == "__main__":
    A = an.build(save=False)
    for k, v in make_all(A).items():
        print(k, v)
