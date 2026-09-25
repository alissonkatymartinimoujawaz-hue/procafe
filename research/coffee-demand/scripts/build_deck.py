# -*- coding: utf-8 -*-
"""Build the PowerPoint research deck (native, editable charts) from analysis.py outputs.

Run:  python research/coffee-demand/scripts/build_deck.py
Out:  research/coffee-demand/output/Coffee_Demand_Research_2026.pptx
"""
import os
import sys

import numpy as np
import pandas as pd
from lxml import etree
from pptx.oxml.ns import qn
from pptx.enum.shapes import MSO_SHAPE

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analysis as an                      # noqa: E402
from pptx_kit import (C, Deck, add_text, add_rect, add_line, category_chart, scatter_chart,  # noqa: E402
                      side_panel, stat_block, legend_chip, table, set_plot_layout)

OUT = os.path.join(an.BASE, "output", "Coffee_Demand_Research_2026.pptx")
L, CT = 0.55, 2.05          # left margin, content top
CW = 12.23                  # content width
FC = "9C93D6"               # forecast tint of the demand colour
SUPPLY_FC = "8FD9BE"


def f1(x):
    return f"{x:,.1f}"


def sg(x, d=1):
    """Signed number with a real minus sign and no '-0'."""
    v = round(float(x), d)
    if v == 0:
        return f"{0:.{d}f}"
    return (f"+{v:.{d}f}" if v > 0 else f"\u2212{abs(v):.{d}f}")


def pct(x, d=1, sign=True):
    if not sign:
        v = round(float(x), d)
        return (f"\u2212{abs(v):.{d}f}%" if v < 0 else f"{v:.{d}f}%")
    return sg(x, d) + "%"


def short(y):
    return f"{y % 100:02d}/{(y + 1) % 100:02d}"


def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


def src(*parts):
    return " · ".join(parts)


LABEL_POS_HEADROOM = {"Mexico": "left", "Vietnam": "above", "Philippines": "above", "Algeria": "below", "Canada": "left",
                      "Turkey": "below", "Russia": "above", "Korea, South": "left", "Saudi Arabia": "right", "Indonesia": "below"}
LABEL_POS_INCOME = {"EU-27 + UK": "left", "Algeria": "below", "Korea, South": "left", "Saudi Arabia": "right", "Mexico": "left",
                    "Brazil": "above", "Russia": "right", "Colombia": "right", "United States": "below", "Egypt": "right"}
USDA = "USDA FAS PSD (Dec-2025 release; bulk file via public mirror, validated) and USDA Coffee: World Markets and Trade, Jul-2026"
ICO = "ICO Coffee Market Reports (monthly tables)"
IMF = "IMF Primary Commodity Prices (ICO New York cash quotes, US c/lb)"


def log_x_axis(chart):
    """Switch the X value axis of an XY chart to log10 scale."""
    ax = chart.category_axis._element
    scaling = ax.find(qn("c:scaling"))
    lb = etree.Element(qn("c:logBase")); lb.set("val", "10")
    scaling.insert(0, lb)


def build():
    A = an.build(save=True)
    M, W, cons, prod, ctry, PR = A["M"], A["W"], A["cons"], A["prod"], A["ctry"], A["PR"]
    cyp, m, EL, excy = A["cyp"], A["m"], A["EL"], A["excy"]
    d = Deck()
    mw = M["world"]
    yrs = list(range(2005, 2026))
    yrs_f = yrs + [2026]

    # ------------------------------------------------------------------ 1 title
    s = d.title_slide("Coffee market research · demand side",
                      "Who drinks the coffee, who flinches at the price, who keeps producing",
                      "World coffee demand 2005–2026: growth vs supply, who consumes and why, the marginal buyer "
                      "(elastic vs inelastic, bean switching) and the marginal producer",
                      "September 2026 · volumes: USDA PSD & ICO · prices: IMF/ICO to Aug-2026 · national data: ABIC (Brazil), IBGE, BLS")
    notes(s, "Research pack built only from official statistics (USDA, ICO, IMF, World Bank, ABIC, IBGE, BLS). "
             "Every number is computed from the files in research/coffee-demand/data; see the last two slides for provenance.")

    # ------------------------------------------------------------------ 2 executive summary
    cls = classify(ctry)
    s = d.content_slide("Executive summary", "Demand is a slow, steady engine; supply and a few price-sensitive buyers set the price",
                        None, src(USDA, ICO, IMF, "ABIC", "World Bank"))
    boxes = [
        ("Demand grows steadily", f"World use {f1(mw['cons_2005'])}m → {f1(mw['cons_2025'])}m bags (2005/06→2025/26): "
         f"+{f1(mw['cons_avg_annual_gain'])}m bags or {mw['cons_cagr_05_25']:.1f}% a year; down in only {len(mw['cons_down_years'])} of 20 years. "
         f"2026/27F: record {f1(mw['cons_2026f'])}m."),
        ("Supply sets the cycle", f"Output swings twice as much (σ of y/y {mw['prod_yoy_sd']:.1f}% vs {mw['cons_yoy_sd']:.1f}%). "
         f"In 2020/21→2025/26 supply grew {M['world']['period_cagr'][3]['prod']:.1f}%/yr vs demand {M['world']['period_cagr'][3]['cons']:.1f}%/yr: "
         f"stocks −{abs(mw['stock_draw_20_25']):.1f}m to {f1(mw['stocks_2025'])}m, stocks-to-use {mw['stu_2025']:.0f}% → price spike."),
        ("Who drinks it", f"Europe (EU-27+UK {f1(ctry.loc['EU-27 + UK','c2025'])}m) and the US ({f1(ctry.loc['United States','c2025'])}m) are biggest "
         f"but flat. {M['contrib_by_group']['Producing countries'] / M['contrib_total'] * 100:.0f}% of the growth since 2005 came from producing "
         f"countries, {M['contrib_by_group']['Emerging importers'] / M['contrib_total'] * 100:.0f}% from new importers (China ×{ctry.loc['China','c2025']/ctry.loc['China','c2005']:.0f})."),
        ("Why it grows", f"~{M['decomp']['pop_share_of_growth']:.0f}% of growth is more people, ~{M['decomp']['pc_share_of_growth']:.0f}% more coffee per head — "
         f"driven by income and cities in Asia/MENA, café chains (Starbucks stores ×{A['sb_tot'].iloc[-1]/A['sb_tot'].iloc[0]:.0f} since FY05) and instant "
         f"(soluble {mw['soluble_share_2005']:.0f}% → {mw['soluble_share_2025']:.0f}% of use)."),
        ("Marginal buyers", f"Green prices +{M['prices']['blend_change_3yavg_pct']:.0f}% (3-yr avg). Inelastic: EU {pct(ctry.loc['EU-27 + UK','chg_spike_3yavg'],0)}, "
         f"US {pct(ctry.loc['United States','chg_spike_3yavg'],0)}. Still growing: China {pct(ctry.loc['China','chg_spike_3yavg'],0)}. "
         f"Cut back: Japan {pct(ctry.loc['Japan','chg_spike_3yavg'],0)}, Algeria {pct(ctry.loc['Algeria','chg_spike_3yavg'],0)}, "
         f"Brazil (ABIC −2.3% in 2025 after retail +80% y/y)."),
        ("Switching & producers", f"Roasters add robusta when arabica trades ≥1.8× robusta (export share {excy.loc[2022,'rob_share']:.0f}% in 22/23, "
         f"~{excy.loc[2025,'rob_share']:.0f}% in 25/26 YTD). Brazil, Vietnam, Ethiopia, Uganda produce through lows; Central America cut after "
         f"the 2018–19 low and never recovered; high prices now deliver a record {f1(mw['prod_2026f'])}m crop (2026/27F)."),
    ]
    bw, bh, gx, gy = 3.93, 2.3, 0.22, 0.22
    for i, (hd, body) in enumerate(boxes):
        col, row = i % 3, i // 3
        x, y = L + col * (bw + gx), 1.75 + row * (bh + gy)
        add_rect(s, x, y, bw, bh, C["panel"])
        add_text(s, x + 0.18, y + 0.14, 0.5, 0.5, f"{i + 1}", size=26, bold=True, color=C["crema"])
        add_text(s, x + 0.62, y + 0.2, bw - 0.8, 0.4, hd, size=15, bold=True, color=C["espresso"])
        add_text(s, x + 0.18, y + 0.72, bw - 0.36, bh - 0.8, body, size=11.5, color=C["ink"], line_spacing=1.05)
    notes(s, "Six answers to the brief. Each box is expanded in the section of the same name.")

    # ------------------------------------------------------------------ 3 how to read
    s = d.content_slide("How to read this deck", "Sources, definitions and the three numbers you need to know",
                        None, "See appendix for URLs and data vintages")
    rows = [
        ["Volumes (supply & demand)", "USDA FAS PSD (Production, Supply & Distribution), all countries, 2005/06–2025/26; "
         "USDA Jul-2026 report for 2026/27 forecasts", "Million 60-kg bags of green-bean equivalent; marketing years (e.g. 2024/25)"],
        ["Consumption definition", "USDA 'domestic consumption' = use/disappearance (imports − re-exports ± stock change in importing "
         "countries). ICO uses coffee years (Oct–Sep) and 'apparent consumption'", "Year-to-year moves in importers include inventory swings: "
         "read trends on 3-year averages"],
        ["Prices", "IMF PCPS / ICO indicator prices: 'Arabica' = ICO Other Milds, 'Robusta' = ICO Robustas, New York cash, "
         "monthly to Aug-2026", "US cents per lb; coffee-year averages Oct–Sep; 'green price' = 60% arabica + 40% robusta"],
        ["Bean mix / switching", "ICO monthly exports by group (Colombian Milds, Other Milds, Brazilian Naturals, Robustas), "
         "Sep-2015–Jul-2026", "Robusta share of world exports, all forms"],
        ["National data", "ABIC (Brazil roasters' association) consumption; IBGE IPCA ground-coffee price index; "
         "BLS US CPI coffee; World Bank population & GDP per capita; company reports (Starbucks)", "Brazil period = Nov–Oct"],
    ]
    table(s, L, 1.8, CW, 3.6, ["Topic", "Source", "Unit / note"], rows, col_widths=[2.3, 6.3, 3.63],
          font_size=11, bold_cols=(0,))
    for i, (v, lab) in enumerate([("1 bag = 60 kg", "green coffee"), ("1m bags ≈ 60,000 t", "≈ 0.6% of world use"),
                                  ("100 US c/lb ≈ $2.20/kg", "≈ $2,205 per tonne")]):
        stat_block(s, L + i * 4.1, 5.75, 3.9, v, lab, size=22)
    notes(s, "Why USDA for the long history: it is the only official source with a consistent country-by-country balance "
             "for every year since 2005. ICO numbers are shown where they add information (coffee-year balance, regions, exports by type).")

    # ================================================================== SECTION 1
    d.section_slide(1, "The global picture", "How fast does world demand grow, year by year — and is it growing faster than supply?")

    # ------------------------------------------------------------------ 4 world demand
    cats = [short(y) for y in yrs_f]
    vals = [W.consumption[y] for y in yrs_f]
    s = d.content_slide("01 · Global demand",
                        f"World demand grew in {20 - len(mw['cons_down_years'])} of the last 20 years: +{f1(mw['cons_abs_gain_05_25'])}m bags "
                        f"since 2005/06, about +{f1(mw['cons_avg_annual_gain'])}m (+{mw['cons_cagr_05_25']:.1f}%) a year",
                        "World coffee consumption, million 60-kg bags (top) and year-on-year change, % (bottom); 2026/27 = USDA forecast",
                        src(USDA))
    last = len(cats) - 1
    fr = category_chart(s, "col", L, CT, 8.5, 3.05, cats,
                        [dict(name="Consumption", values=vals, color=C["demand"], point_colors={last: FC},
                              labels={0: f1(vals[0]), last - 1: f1(vals[last - 1]), last: f1(vals[last]) + "F"},
                              label_pos="out")],
                        vmin=0, vmax=200, major=50, gap=35, cat_label_skip=2, plot=(0.07, 0.08, 0.91, 0.8))
    yoy = [W.cons_yoy[y] if not np.isnan(W.cons_yoy[y]) else None for y in yrs_f]
    pc_ = {i: (C["decline"] if (v is not None and v < 0) else C["demand"]) for i, v in enumerate(yoy)}
    pc_[last] = FC
    lab = {i: f"{sg(v, 1)}" for i, v in enumerate(yoy) if v is not None and (v < 0 or v > 4.5)}
    category_chart(s, "col", L, CT + 3.05, 8.5, 1.85, cats,
                   [dict(name="y/y %", values=yoy, color=C["demand"], point_colors=pc_, labels=lab, label_size=8,
                         label_bold=False, label_color=C["ink2"])],
                   vmin=-5, vmax=12, major=5, gap=35, num_fmt='0"%"', cat_label_skip=2, tick_low=True,
                   plot=(0.07, 0.05, 0.91, 0.72))
    x0 = 9.25
    stat_block(s, x0, CT, 3.5, f"+{mw['cons_cagr_05_25']:.1f}% / yr", f"CAGR 2005/06→2025/26 ({f1(mw['cons_2005'])}m → {f1(mw['cons_2025'])}m bags)")
    stat_block(s, x0, CT + 1.15, 3.5, f"+{f1(mw['cons_avg_annual_gain'])}m bags", "average extra demand every year ≈ one Honduras crop")
    stat_block(s, x0, CT + 2.3, 3.5, f"{len(mw['cons_down_years'])} down years", ", ".join(mw['cons_down_years']) +
               " — mostly stock swings in importers or COVID (2019/20–2020/21)")
    stat_block(s, x0, CT + 3.55, 3.5, f"{f1(mw['cons_2026f'])}m", f"2026/27 USDA forecast, record (+{W.cons_yoy[2026]:.1f}% vs Dec-25 estimate)")
    notes(s, "USDA world consumption is the sum of 90+ country balances. The +10.6% in 2009/10 and the dips in 2010/11 and 2023/24 are largely "
             "inventory movements in importing countries (USDA measures disappearance), so read the trend, not single years.")

    # ------------------------------------------------------------------ 5 supply vs demand
    pcg = M["world"]["period_cagr"]
    s = d.content_slide("01 · Demand vs supply",
                        f"Supply grew faster over 20 years ({mw['prod_cagr_05_25']:.1f}% vs {mw['cons_cagr_05_25']:.1f}% a year), but stalled in "
                        f"2020–25 while demand kept rising — stocks were cut almost in half",
                        "World production vs consumption, million bags (top); change in world ending stocks, million bags (bottom)",
                        src(USDA))
    pv = [W.production[y] for y in yrs_f]
    category_chart(s, "line", L, CT, 8.5, 2.95, cats,
                   [dict(name="Production", values=pv, color=C["supply"], labels={last: f1(pv[last]) + "F"}, label_pos="above"),
                    dict(name="Consumption", values=vals, color=C["demand"], labels={last: f1(vals[last]) + "F"}, label_pos="below")],
                   vmin=100, vmax=200, major=25, cat_label_skip=2, plot=(0.07, 0.14, 0.91, 0.74), markers=False)
    sc = [W.stock_change[y] if y <= 2025 and not np.isnan(W.stock_change[y]) else None for y in yrs_f]
    pcs = {i: (C["deficit"] if (v is not None and v < 0) else C["surplus"]) for i, v in enumerate(sc)}
    lab = {i: f"{sg(v, 1)}" for i, v in enumerate(sc) if v is not None and abs(v) >= 5}
    category_chart(s, "col", L, CT + 2.95, 8.5, 1.95, cats,
                   [dict(name="Stock change", values=sc, color=C["surplus"], point_colors=pcs, labels=lab, label_size=8,
                         label_bold=False)],
                   vmin=-12, vmax=12, major=6, gap=35, cat_label_skip=2, tick_low=True, plot=(0.07, 0.04, 0.91, 0.74))
    side_panel(s, 9.25, CT, 3.53, 4.8, "Is demand outgrowing supply?", [
        [{"text": "20 years: no. ", "bold": True}, {"text": f"Production +{mw['prod_cagr_05_25']:.1f}%/yr vs consumption +{mw['cons_cagr_05_25']:.1f}%/yr (2005/06 was a small Brazil crop)."}],
        [{"text": "2020/21→2025/26: yes. ", "bold": True}, {"text": f"Demand +{pcg[3]['cons']:.1f}%/yr, supply +{pcg[3]['prod']:.1f}%/yr; five straight stock draws, "
                                                                     f"{f1(W.ending_stocks[2020])}m → {f1(mw['stocks_2025'])}m bags."}],
        [{"text": "2026/27F: supply back. ", "bold": True}, {"text": f"Output +{W.prod_yoy[2026]:.1f}% to a record {f1(mw['prod_2026f'])}m; USDA sees stocks rebuilding "
                                                                     f"+1.9m to {f1(mw['stocks_2026f'])}m (first rise in six years)."}],
        "ICO agrees: four deficit years 2021/22–2024/25, then a 3.0m surplus in 2025/26.",
    ], size=11)
    notes(s, "USDA's July-2026 report did not state its revised 2025/26 stocks; the +1.9m stock build is USDA's own figure versus that revised base, "
             "so the bottom chart stops at 2025/26 (Dec-2025 vintage).")

    # ------------------------------------------------------------------ 6 growth scoreboard
    s = d.content_slide("01 · Growth scoreboard",
                        "Demand grows 1–2.5% a year in every 5-year block; supply lurches between +0.3% and +3.7%",
                        "Compound annual growth by period, %: world consumption vs world production (USDA); labels under the chart = change in ending stocks",
                        src(USDA))
    pc_names = [p["period"] for p in pcg]
    category_chart(s, "col", L, CT, 8.5, 4.2, pc_names,
                   [dict(name="Consumption", values=[p["cons"] for p in pcg], color=C["demand"]),
                    dict(name="Production", values=[p["prod"] for p in pcg], color=C["supply"])],
                   vmin=0, vmax=4.5, major=1, num_fmt='0.0"%"', labels=True, label_fmt='0.0"%"', label_pos="out",
                   gap=80, overlap=-10, plot=(0.07, 0.12, 0.91, 0.76))
    for i, p in enumerate(pcg):
        xc = L + 8.5 * (0.07 + 0.91 * (i + 0.5) / 4)
        add_text(s, xc - 1.0, CT + 4.3, 2.0, 0.45, f"stocks {sg(p['stock_change'], 1)}m", size=11, bold=True,
                 color=C["deficit"] if p["stock_change"] < 0 else C["ink2"], align="c")
    side_panel(s, 9.25, CT, 3.53, 4.8, "Reading it like a trader", [
        "Demand growth is narrow-band: 1.1–2.5%/yr. It is the anchor, not the driver, of the price cycle.",
        "Supply growth is lumpy — Brazil's biennial cycle, frosts (2021), droughts (2023–24) and slow tree renewal.",
        f"Only in 2020–25 did demand beat supply: the {abs(pcg[3]['stock_change']):.1f}m stock draw is what produced record prices.",
        "Rule of thumb: world demand needs ~+2.5m bags of new supply each year just to stand still.",
    ], size=11)

    # ------------------------------------------------------------------ 7 stocks-to-use vs prices
    s = d.content_slide("01 · Stocks & price",
                        f"Stocks-to-use fell from {mw['stu_peak']:.0f}% to {mw['stu_2025']:.0f}% — and green prices doubled: tight stocks, not demand booms, "
                        "drive price spikes",
                        "World ending stocks as % of consumption (top, USDA); average price by coffee year Oct–Sep, US c/lb (bottom, IMF/ICO)",
                        src(USDA, IMF, ICO))
    stu = [W.stocks_to_use[y] for y in yrs_f]
    pcol = {i: C["deficit"] for i, v in enumerate(stu) if v < 16}
    pcol[last] = "C9C7C0"
    category_chart(s, "col", L, CT, 8.5, 2.35, cats,
                   [dict(name="Stocks-to-use", values=stu, color=C["steady"], point_colors=pcol,
                         labels={int(np.argmax(stu[:-1])): f"{max(stu[:-1]):.0f}%", last - 1: f"{stu[last-1]:.0f}%", last: f"{stu[last]:.0f}%F"},
                         label_pos="out")],
                   vmin=0, vmax=40, major=10, num_fmt='0"%"', gap=35, cat_label_skip=2, plot=(0.07, 0.1, 0.91, 0.76))
    ar = [cyp.arabica.get(y) for y in yrs] + [None]
    ro = [cyp.robusta.get(y) for y in yrs] + [None]
    category_chart(s, "line", L, CT + 2.4, 8.5, 2.5, cats,
                   [dict(name="Arabica (Other Milds)", values=ar, color=C["arabica"], labels={yrs.index(2024): f"{ar[yrs.index(2024)]:.0f}"}, label_pos="above"),
                    dict(name="Robusta", values=ro, color=C["robusta"], labels={yrs.index(2024): f"{ro[yrs.index(2024)]:.0f}"}, label_pos="below")],
                   vmin=0, vmax=400, major=100, cat_label_skip=2, plot=(0.07, 0.14, 0.91, 0.72))
    side_panel(s, 9.25, CT, 3.53, 4.8, "So what", [
        f"Stocks peaked at {f1(mw['stocks_peak'])}m bags in {mw['stocks_peak_year']} (≈{mw['stu_peak']:.0f}% of a year's use).",
        f"By 2025/26 they were {f1(mw['stocks_2025'])}m — {mw['stu_2025']:.0f}% of use, the lowest since at least 2005.",
        f"Arabica averaged {cyp.arabica[2024]:.0f} c/lb in 2024/25 vs {cyp.arabica[2018]:.0f} in 2018/19; robusta {cyp.robusta[2024]:.0f} vs {cyp.robusta[2018]:.0f}.",
        "Below ~16% stocks-to-use (red bars) the market has no buffer against a weather shock.",
        "USDA's 2026/27 rebuild (14.6%F) is the first step back — watch whether it holds.",
    ], size=11)

    # ------------------------------------------------------------------ 8 who consumes most
    order = ctry.drop(index=["World", "European Union", "United Kingdom"]).sort_values("c2025", ascending=False).head(15)
    names = list(order.index)[::-1]
    s = d.content_slide("01 · Who consumes",
                        f"Europe and the US still drink {order.loc[['EU-27 + UK','United States'],'share2025'].sum():.0f}% of the world's coffee — "
                        "but the next ten are mostly producing and emerging countries",
                        "Coffee consumption by country, million bags, 2025/26 (USDA forecast, Dec-2025) vs 2005/06; label = 2025/26 volume and share of world",
                        src(USDA, "EU-27 + UK combined because USDA's EU series excludes the UK from 2016/17"))
    v25 = [order.loc[n, "c2025"] for n in names]
    v05 = [order.loc[n, "c2005"] if not np.isnan(order.loc[n, "c2005"]) else 0 for n in names]
    labs = {i: f"{v25[i]:.1f}  ({order.loc[n,'share2025']:.1f}%)" for i, n in enumerate(names)}
    category_chart(s, "bar", L, CT - 0.05, 8.5, 4.85, names,
                   [dict(name="2005/06", values=v05, color="C9C7C0"),
                    dict(name="2025/26", values=v25, color=C["demand"], labels=labs, label_pos="out", label_size=9,
                         label_bold=False)],
                   vmin=0, vmax=60, major=10, gap=40, overlap=0, plot=(0.2, 0.06, 0.72, 0.86), cat_font=10)
    side_panel(s, 9.25, CT, 3.53, 4.8, "Who, and how", [
        [{"text": "Largest bloc: ", "bold": True}, {"text": f"EU-27+UK {f1(ctry.loc['EU-27 + UK','c2025'])}m (Germany, France, Italy lead — ICO)."}],
        [{"text": "Largest country: ", "bold": True}, {"text": f"US {f1(ctry.loc['United States','c2025'])}m, then Brazil {f1(ctry.loc['Brazil','c2025'])}m — a producer that drinks ~a third of its crop."}],
        [{"text": "Fastest risers: ", "bold": True}, {"text": f"China {f1(ctry.loc['China','c2005'])}→{f1(ctry.loc['China','c2025'])}m, Vietnam, Philippines, Turkey, Korea."}],
        "How they drink differs: Europe/US/Brazil >90% roast & ground (home + cafés); instant is 91% in the Philippines and ~⅓ in China, Indonesia, Vietnam (USDA).",
        f"Top 15 = {order.share2025.sum():.0f}% of world use.",
    ], size=11)
    notes(s, "USDA reports the EU as one balance. Within Europe the ICO's 2019 data rank Germany (8.7m), France (6.2m), Italy (5.5m), Spain (3.3m), UK (3.8m).")

    # ------------------------------------------------------------------ 9 where growth came from
    contrib = A["contrib"]
    top_pos = contrib[contrib.delta > 0].head(14)
    neg = contrib[contrib.delta < -0.2].sort_values("delta")
    sel = pd.concat([top_pos, neg])
    names = list(sel.index)[::-1]
    gcol = {"Producing countries": "EDA100", "Emerging importers": "E87BA4", "Traditional importers": C["demand"]}
    s = d.content_slide("01 · Where growth came from",
                        f"{(M['contrib_by_group']['Producing countries'] + M['contrib_by_group']['Emerging importers']) / M['contrib_total'] * 100:.0f}% "
                        f"of the extra {f1(M['contrib_total'])}m bags since 2005/06 came from producing countries and new importers",
                        "Change in consumption 2005/06 → 2025/26, million bags, largest contributors and decliners; colour = buyer group",
                        src(USDA))
    dv = [sel.loc[n, "delta"] for n in names]
    pcol = {i: gcol[sel.loc[n, "group"]] for i, n in enumerate(names)}
    labs = {i: f"{sg(v, 1)}" for i, v in enumerate(dv)}
    category_chart(s, "bar", L, CT - 0.05, 8.5, 4.85, names,
                   [dict(name="Δ 2005/06→2025/26", values=dv, color=C["demand"], point_colors=pcol, labels=labs,
                         label_pos="out", label_size=9, label_bold=False)],
                   vmin=-2, vmax=8, major=2, gap=35, plot=(0.22, 0.03, 0.72, 0.9), tick_low=True, cat_font=10)
    gy = CT
    for g in ["Producing countries", "Emerging importers", "Traditional importers"]:
        v = M["contrib_by_group"][g]
        add_rect(s, 9.3, gy + 0.08, 0.2, 0.2, gcol[g])
        add_text(s, 9.62, gy - 0.02, 3.2, 0.35, g, size=12, bold=True, color=C["ink"])
        add_text(s, 9.62, gy + 0.3, 3.2, 0.5, f"+{f1(v)}m bags · {v / M['contrib_total'] * 100:.0f}% of growth", size=13, color=C["ink2"])
        gy += 0.95
    add_text(s, 9.3, gy + 0.1, 3.45, 1.9,
             [{"runs": [{"text": "Producing countries ", "bold": True}, {"text": "= countries that also grow coffee (Brazil, Vietnam, Philippines, Indonesia, Ethiopia, Mexico…). "}], "space_after": 4},
              {"runs": [{"text": "Emerging importers ", "bold": True}, {"text": "= China, Korea, Russia, Turkey, Middle East & North Africa…"}]}],
             size=10.5, color=C["ink2"])

    # ------------------------------------------------------------------ 10 buyer groups over time
    G = A["G"]
    s = d.content_slide("01 · Buyer groups",
                        f"Traditional importers fell from {G.loc[2005,'Traditional importers']/G.loc[2005,['Emerging importers','Producing countries','Traditional importers']].sum()*100:.0f}% "
                        f"to {G.loc[2025,'Traditional importers']/G.loc[2025,['Emerging importers','Producing countries','Traditional importers']].sum()*100:.0f}% "
                        "of world demand in 20 years — the centre of gravity is moving to origin countries and Asia",
                        "World consumption by buyer group, million bags (USDA); labels = share of world",
                        src(USDA))
    ser = []
    for g in ["Traditional importers", "Emerging importers", "Producing countries"]:
        vals_g = [G.loc[y, g] for y in yrs]
        tot = [G.loc[y, ["Emerging importers", "Producing countries", "Traditional importers"]].sum() for y in yrs]
        labs = {0: f"{vals_g[0] / tot[0] * 100:.0f}%", len(yrs) - 1: f"{vals_g[-1] / tot[-1] * 100:.0f}%"}
        ser.append(dict(name=g, values=vals_g, color=gcol[g], labels=labs, label_color=C["white"] if g == "Traditional importers" else C["ink"]))
    category_chart(s, "col_stacked", L, CT, 8.5, 4.8, [short(y) for y in yrs], ser, vmin=0, vmax=180, major=30,
                   gap=30, cat_label_skip=2, label_pos="ctr", plot=(0.07, 0.12, 0.91, 0.76))
    side_panel(s, 9.25, CT, 3.53, 4.8, "So what", [
        f"Traditional importers (EU+UK, US, Japan, Canada, Switzerland, Norway, Australia) grew only {an.cagr(G.loc[2005,'Traditional importers'], G.loc[2025,'Traditional importers'], 20)*100:.1f}%/yr.",
        f"Producing countries grew {an.cagr(G.loc[2005,'Producing countries'], G.loc[2025,'Producing countries'], 20)*100:.1f}%/yr — they now drink "
        f"{G.loc[2025,'Producing countries']:.0f}m bags, ~{G.loc[2025,'Producing countries']/W.production[2025]*100:.0f}% of world output, before exporting.",
        f"Emerging importers grew {an.cagr(G.loc[2005,'Emerging importers'], G.loc[2025,'Emerging importers'], 20)*100:.1f}%/yr (China, Korea, Turkey, Gulf, North Africa).",
        "Implication: the export surplus of Brazil, Vietnam, Indonesia, Ethiopia shrinks as their own populations drink more.",
    ], size=11)

    # ------------------------------------------------------------------ 11 per capita vs income
    INC = A["INC"].copy()
    INC = INC[(INC.cons2024 >= 0.7) & INC.gdppc2024.notna() & INC.kg2024.notna()]
    INC = INC.drop(index=[i for i in INC.index if i == "World"], errors="ignore")
    grp_of = {c: ctry.loc[c, "group"] if c in ctry.index else "Emerging importers" for c in INC.index}
    series = []
    lab_set = {"China", "India", "Indonesia", "United States", "EU-27 + UK", "Brazil", "Japan", "Vietnam", "Korea, South",
               "Canada", "Norway", "Switzerland", "Philippines", "Turkey", "Saudi Arabia", "Russia", "Mexico", "Ethiopia", "Algeria"}
    for g in ["Traditional importers", "Emerging importers", "Producing countries"]:
        sub = INC[[grp_of[c] == g for c in INC.index]]
        pts = [(float(sub.loc[c, "gdppc2024"]), float(sub.loc[c, "kg2024"])) for c in sub.index]
        labels = {i: c.replace("Korea, South", "Korea").replace("United States", "US").replace("Saudi Arabia", "Saudi")
                  for i, c in enumerate(sub.index) if c in lab_set}
        lpm = {i: LABEL_POS_HEADROOM.get(c, "right") for i, c in enumerate(sub.index)}
        series.append(dict(name=g, points=pts, color=gcol[g], labels=labels, label_size=9, label_pos_map=lpm))
    s = d.content_slide("01 · Headroom",
                        f"Coffee per person rises with income — China ({INC.loc['China','kg2024']:.2f} kg) and India ({INC.loc['India','kg2024']:.2f} kg) "
                        f"sit far below Europe ({INC.loc['EU-27 + UK','kg2024']:.1f} kg): that is the growth runway",
                        "Consumption per person, kg of green coffee per year (2024/25), vs GDP per capita, current US$ (2024, log scale); countries using ≥0.7m bags",
                        src(USDA, "World Bank WDI (population, GDP per capita)"))
    fr = scatter_chart(s, L, CT, 8.5, 4.8, series, xmin=500, xmax=150000, ymin=0, ymax=10, ymajor=2, x_fmt='#,##0',
                       y_fmt='0', plot=(0.07, 0.1, 0.9, 0.78), marker_size=9)
    log_x_axis(fr.chart)
    add_text(s, L + 0.1, CT + 4.45, 5, 0.3, "GDP per capita, US$ (log scale) →", size=9, color=C["muted"])
    side_panel(s, 9.25, CT, 3.53, 4.8, "Headroom maths", [
        f"If China reached Korea's {INC.loc['Korea, South','kg2024']:.1f} kg, it would need ~{INC.loc['Korea, South','kg2024'] * 1.41e9 / 60 / 1e6:.0f}m bags — "
        f"{INC.loc['Korea, South','kg2024'] * 1.41e9 / 60 / 1e6 / ctry.loc['China','c2024']:.0f}× today.",
        f"Indonesia ({INC.loc['Indonesia','kg2024']:.1f} kg), Vietnam ({INC.loc['Vietnam','kg2024']:.1f} kg), Turkey ({INC.loc['Turkey','kg2024']:.1f} kg) are mid-way.",
        "Saturation sits around 4–9 kg: Nordics, Switzerland, Canada, Brazil, Europe, the US.",
        "Japan is the exception: rich, but per-capita use is falling (ageing, RTD/tea competition).",
    ], size=11)
    notes(s, "kg per person = USDA consumption × 60 kg / World Bank population (2024). Green-bean equivalent, including instant.")

    # ------------------------------------------------------------------ 12 decomposition
    dec = M["decomp"]
    base, final = W.consumption[2005], W.consumption[2024]
    popeff = base * dec["pop_pct"] / 100
    pceff = final - base - popeff
    s = d.content_slide("01 · Why it grows",
                        f"About two thirds of demand growth is simply more people; one third is more coffee per person",
                        "Decomposition of world consumption growth 2005/06 → 2024/25, million bags (USDA volumes, World Bank population)",
                        src(USDA, "World Bank population (SP.POP.TOTL)"))
    cats_w = ["2005/06", "+ more people", "+ more per person", "2024/25"]
    invisible = [0, base, base + popeff, 0]
    shown = [base, popeff, pceff, final]
    fr = category_chart(s, "col_stacked", L, CT, 8.5, 4.8, cats_w,
                        [dict(name="base", values=invisible, color=C["white"]),
                         dict(name="value", values=shown, color=C["demand"], point_colors={1: "7A6FCF", 2: FC},
                              labels={0: f1(base), 1: f"+{f1(popeff)}", 2: f"+{f1(pceff)}", 3: f1(final)},
                              label_color=C["white"])],
                        vmin=0, vmax=190, major=30, gap=45, legend=False, label_pos="ctr", plot=(0.07, 0.06, 0.91, 0.84))
    ser0 = fr.chart.plots[0].series[0]
    ser0.format.fill.background()
    ser0.format.line.fill.background()
    side_panel(s, 9.25, CT, 3.53, 4.8, "The two engines", [
        [{"text": f"Population +{dec['pop_pct']:.1f}%: ", "bold": True},
         {"text": f"{M['pop']['world_2005']/1e9:.2f}bn → {M['pop']['world_2024']/1e9:.2f}bn people (~{dec['pop_share_of_growth']:.0f}% of growth, log basis)."}],
        [{"text": f"Per person +{dec['pc_pct']:.1f}%: ", "bold": True},
         {"text": f"{M['pop']['kg_world_2005']:.2f} → {M['pop']['kg_world_2024']:.2f} kg a year (~{dec['pc_share_of_growth']:.0f}% of growth)."}],
        "Per-capita gains come from Asia, the Middle East and producing countries; in Europe, the US and Japan per-capita use is flat or falling.",
        "So demand growth is structurally ~1.2% from demography + ~0.5% from habits and income.",
    ], size=11)

    # ================================================================== SECTION 2
    d.section_slide(2, "Demand segments & drivers",
                    "Which kind of demand grew — homes, cafés, instant, roasters — and what drove it year by year?")

    # ------------------------------------------------------------------ 13 formats
    FMT = A["FMT"]
    s = d.content_slide("02 · Formats",
                        f"Instant coffee is the fastest-growing format: soluble rose from {mw['soluble_share_2005']:.0f}% to "
                        f"{mw['soluble_share_2025']:.0f}% of world consumption",
                        "World consumption by format, million bags: roast & ground vs soluble (instant), USDA; labels = soluble share",
                        src(USDA))
    rgv = [FMT.rg_world[y] for y in yrs]
    solv = [FMT.sol_world[y] for y in yrs]
    labs = {i: f"{solv[i] / (solv[i] + rgv[i]) * 100:.0f}%" for i in (0, 5, 10, 15, 20)}
    category_chart(s, "col_stacked", L, CT, 8.5, 4.8, [short(y) for y in yrs],
                   [dict(name="Roast & ground", values=rgv, color=C["demand"]),
                    dict(name="Soluble (instant)", values=solv, color="E87BA4", labels=labs, label_pos="ctr", label_size=9)],
                   vmin=0, vmax=180, major=30, gap=30, cat_label_skip=2, plot=(0.07, 0.12, 0.91, 0.76))
    sol_g = an.cagr(FMT.sol_world[2005], FMT.sol_world[2025], 20) * 100
    rg_g = an.cagr(FMT.rg_world[2005], FMT.rg_world[2025], 20) * 100
    side_panel(s, 9.25, CT, 3.53, 4.8, "Segments", [
        [{"text": "Soluble: ", "bold": True}, {"text": f"{f1(FMT.sol_world[2005])}m → {f1(FMT.sol_world[2025])}m bags, +{sol_g:.1f}%/yr — "
                                                       "dominant in the Philippines (91%), Thailand, India, Mexico; ~⅓ of use in China, Indonesia, Vietnam; mostly robusta."}],
        [{"text": "Roast & ground: ", "bold": True}, {"text": f"+{rg_g:.1f}%/yr — home brewing, capsules and cafés in mature markets."}],
        "Capsules/pods show up as roasted-coffee trade: world roast & ground exports "
        f"{f1(FMT.world_rg_exports[2005])}m → {f1(FMT.world_rg_exports[2025])}m bags; Switzerland (Nespresso's base) alone {f1(FMT.swiss_rg_exports[2025])}m.",
        "Channel split is not in official data: in Brazil, retail (at-home) is 73–78% of volume, cafés/out-of-home the rest (ABIC, 2025).",
    ], size=10.5)

    # ------------------------------------------------------------------ 14 coffee shops
    sb, sbc, sbu = A["sb_tot"], A["sb_china"], A["sb_us"]
    s = d.content_slide("02 · Coffee shops",
                        f"Coffee-shop chains quadrupled their footprint — Starbucks alone went from {sb.iloc[0]:,.0f} to {sb.iloc[-1]:,.0f} stores, "
                        "and the growth has moved to China",
                        "Starbucks stores worldwide at fiscal year-end (left; FY07, FY09, FY11–13 not captured); Starbucks China vs US stores, FY2020–FY2025 (right; FY22 not captured)",
                        src("Starbucks Form 10-K / annual reports (fiscal years to late Sep/early Oct)", "Luckin Coffee Form 20-F (FY2024), as quoted"))
    pts = [(float(k), float(v)) for k, v in sb.items()]
    scatter_chart(s, L, CT, 5.9, 4.8, [dict(name="Starbucks stores", points=pts, color=C["demand"],
                                            labels={0: f"{sb.iloc[0]/1000:.1f}k", len(pts) - 1: f"{sb.iloc[-1]/1000:.1f}k"})],
                  xmin=2004, xmax=2026, ymin=0, ymax=45000, xmajor=2, ymajor=10000, x_fmt='0', y_fmt='#,##0',
                  plot=(0.12, 0.08, 0.84, 0.8), lines=False, legend=False)
    # connect the dots with a line series drawn as a second scatter (lines)
    rng = list(range(int(sbc.index.min()), int(sbc.index.max()) + 1))
    yrs_sb = [f"FY{y % 100:02d}" for y in rng]
    category_chart(s, "col", 6.65, CT, 4.1, 4.8, yrs_sb,
                   [dict(name="US", values=[sbu.get(y) for y in rng], color="C9C7C0"),
                    dict(name="China", values=[sbc.get(y) for y in rng], color=C["demand"],
                         labels={0: f"{sbc.iloc[0]:,.0f}", len(rng) - 1: f"{sbc.iloc[-1]:,.0f}"}, label_pos="out", label_size=9)],
                   vmin=0, vmax=20000, major=5000, gap=50, overlap=-5, plot=(0.14, 0.12, 0.84, 0.76), num_fmt='#,##0')
    add_text(s, 10.95, CT, 1.85, 4.8, [
        {"runs": [{"text": f"×{sb.iloc[-1] / sb.iloc[0]:.1f}", "bold": True, "size": 24, "color": C["espresso"]}]},
        {"runs": [{"text": "Starbucks stores FY05→FY25", "size": 10, "color": C["ink2"]}], "space_after": 10},
        {"runs": [{"text": f"+{(sbc.iloc[-1] / sbc.iloc[0] - 1) * 100:.0f}%", "bold": True, "size": 24, "color": C["espresso"]}]},
        {"runs": [{"text": f"Starbucks China FY20→FY25 vs US +{(sbu.iloc[-1] / sbu.iloc[0] - 1) * 100:.0f}%", "size": 10, "color": C["ink2"]}], "space_after": 10},
        {"runs": [{"text": "22,340", "bold": True, "size": 24, "color": C["espresso"]}]},
        {"runs": [{"text": "Luckin stores end-2024 (20-F) — ~2.9× Starbucks China", "size": 10, "color": C["ink2"]}]},
    ], size=10)
    notes(s, "Starbucks store counts from 10-K filings (FY2007, FY2009, FY2011–13 not captured, so the left chart shows points, not a line). "
             "Luckin's 22,340 stores is its FY2024 20-F figure as quoted in a secondary source (not re-checked against the filing).")

    # ------------------------------------------------------------------ 15 income vs demand growth
    INC2 = A["INC"].copy()
    INC2 = INC2[(INC2.cons2005 >= 0.15) & (INC2.cons2024 >= 0.7) & INC2.gdppc2024.notna()].drop(index=["World"], errors="ignore")
    INC2["gdp_g"] = [an.cagr(a, b, (int(y) if not np.isnan(y) else 2024) - 2005) * 100 for a, b, y in zip(INC2.gdppc2005, INC2.gdppc2024, INC2.gdp_year)]
    INC2["cons_g"] = [an.cagr(a, b, 19) * 100 for a, b in zip(INC2.cons2005, INC2.cons2024)]
    INC2 = INC2[INC2.cons_g < 25]
    series = []
    lab_set2 = {"China", "Vietnam", "Turkey", "Philippines", "Indonesia", "Korea, South", "Saudi Arabia", "India", "EU-27 + UK",
                "United States", "Japan", "Brazil", "Ethiopia", "Russia", "Egypt", "Algeria", "Mexico", "Colombia"}
    for g in ["Traditional importers", "Emerging importers", "Producing countries"]:
        sub = INC2[[ctry.loc[c, "group"] == g if c in ctry.index else g == "Emerging importers" for c in INC2.index]]
        pts = [(float(sub.loc[c, "gdp_g"]), float(sub.loc[c, "cons_g"])) for c in sub.index]
        labels = {i: c.replace("Korea, South", "Korea").replace("United States", "US").replace("Saudi Arabia", "Saudi")
                  for i, c in enumerate(sub.index) if c in lab_set2}
        lpm = {i: LABEL_POS_INCOME.get(c, "right") for i, c in enumerate(sub.index)}
        series.append(dict(name=g, points=pts, color=gcol[g], labels=labels, label_size=9, label_pos_map=lpm))
    ch = INC2.loc["China"] if "China" in INC2.index else None
    s = d.content_slide("02 · Income & cities",
                        "Where incomes multiplied, coffee demand multiplied faster — the income effect is strongest in Asia and the Middle East",
                        "Growth 2005→2024, % per year: GDP per capita in current US$ (x, World Bank) vs coffee consumption (y, USDA); countries with ≥0.7m bags in 2024/25",
                        src(USDA, "World Bank WDI NY.GDP.PCAP.CD"))
    scatter_chart(s, L, CT, 8.5, 4.8, series, xmin=-2, xmax=14, ymin=-4, ymax=22, xmajor=2, ymajor=4, x_fmt='0"%"',
                  y_fmt='0"%"', plot=(0.08, 0.1, 0.88, 0.78))
    side_panel(s, 9.25, CT, 3.53, 4.8, "Drivers, with numbers", [
        [{"text": "Income: ", "bold": True}, {"text": f"China GDP/head ×{A['INC'].loc['China','gdppc2024']/A['INC'].loc['China','gdppc2005']:.1f} (2005→24), Vietnam ×"
                                                      f"{A['INC'].loc['Vietnam','gdppc2024']/A['INC'].loc['Vietnam','gdppc2005']:.1f}, Indonesia ×{A['INC'].loc['Indonesia','gdppc2024']/A['INC'].loc['Indonesia','gdppc2005']:.1f}."}],
        [{"text": "Cities: ", "bold": True}, {"text": "China's urban share rose from 42.5% to 65.5% (World Bank) — cafés and office demand follow."}],
        [{"text": "Habit: ", "bold": True}, {"text": f"demand grows faster than income where coffee is new: China {INC2.loc['China','cons_g']:.0f}%/yr, "
                                                      f"Turkey {INC2.loc['Turkey','cons_g']:.0f}%, Vietnam {INC2.loc['Vietnam','cons_g']:.0f}% a year (2005→24)."}],
        [{"text": "Mature: ", "bold": True}, {"text": "EU, US, Japan sit near zero — income no longer adds volume, only value (premium, cafés)."}],
    ], size=10.5)
    notes(s, "Growth rates are compound annual rates 2005→2024. China's 2005/06 base is tiny (0.2m bags), so its rate is extreme; Egypt, Turkey and Vietnam also start from low bases.")

    # ------------------------------------------------------------------ 16 segment map
    tot25 = G.loc[2025, ["Emerging importers", "Producing countries", "Traditional importers"]].sum()
    s = d.content_slide("02 · Segment map",
                        "Demand map: three buyer groups with very different growth and price sensitivity",
                        "Size and growth by segment (USDA volumes); price response measured over the 2021–25 spike (see section 03)",
                        src(USDA, "ABIC", "Starbucks 10-K"))
    rows = [
        ["Traditional importers\nEU+UK, US, Japan, Canada, CH, NO, AU", f"{f1(G.loc[2025,'Traditional importers'])}m ({G.loc[2025,'Traditional importers']/tot25*100:.0f}%)",
         f"{sg(an.cagr(G.loc[2005,'Traditional importers'], G.loc[2025,'Traditional importers'], 20)*100, 1)}%/yr",
         "Home R&G, capsules, cafés; premiumisation adds value not volume", "Inelastic (Japan the exception)"],
        ["Emerging importers\nChina, Korea, Russia, Turkey, Gulf, N. Africa", f"{f1(G.loc[2025,'Emerging importers'])}m ({G.loc[2025,'Emerging importers']/tot25*100:.0f}%)",
         f"{sg(an.cagr(G.loc[2005,'Emerging importers'], G.loc[2025,'Emerging importers'], 20)*100, 1)}%/yr",
         "Café chains (Luckin, Starbucks), instant, RTD; young urban buyers", "Grow through price spikes; robusta-heavy N. Africa cuts"],
        ["Producing countries\nBrazil, Philippines, Indonesia, Vietnam, Ethiopia, Mexico…", f"{f1(G.loc[2025,'Producing countries'])}m ({G.loc[2025,'Producing countries']/tot25*100:.0f}%)",
         f"{sg(an.cagr(G.loc[2005,'Producing countries'], G.loc[2025,'Producing countries'], 20)*100, 1)}%/yr",
         "Home brewing & instant; local robusta/conilon blends; retail 73–78% in Brazil", "Mixed: Brazil cuts at +80% retail; Asia keeps growing"],
        ["Format: soluble (instant)", f"{f1(FMT.sol_world[2025])}m ({mw['soluble_share_2025']:.0f}%)", f"+{sol_g:.1f}%/yr",
         "Cheapest cup; robusta-based", "Buyers switch into it when prices rise"],
        ["Format: roast & ground (incl. capsules, cafés)", f"{f1(FMT.rg_world[2025])}m ({100 - mw['soluble_share_2025']:.0f}%)", f"+{rg_g:.1f}%/yr",
         "Blend decisions sit with roasters", "Roasters switch arabica↔robusta inside blends"],
    ]
    table(s, L, CT, CW, 4.6, ["Segment", "2025/26 volume", "CAGR 05→25", "How they drink / who buys", "Price behaviour"], rows,
          col_widths=[3.3, 1.8, 1.45, 3.35, 2.33], font_size=10.5, bold_cols=(0,))

    # ================================================================== SECTION 3
    d.section_slide(3, "Marginal buyers", "When green prices more than doubled (2021–2025), who kept buying, who did not react, "
                                           "who cut back — at what price — and who switched beans?")

    # ------------------------------------------------------------------ 17 price chart
    mm = m[m.period >= "2010-01"].reset_index(drop=True)
    pcats = [p[:4] for p in mm.period]
    idx = {p: i for i, p in enumerate(mm.period)}
    pk_a = mm.arabica.idxmax(); pk_r = mm.robusta.idxmax()
    lo_a = mm[(mm.period >= "2015-01") & (mm.period <= "2020-12")].arabica.idxmin()
    lo_r = mm[(mm.period >= "2015-01") & (mm.period <= "2020-12")].robusta.idxmin()
    s = d.content_slide("03 · The price shock",
                        f"Green coffee tripled from the 2019–20 lows to records in 2025; in Aug-2026 arabica still costs "
                        f"{M['prices']['ratio_last']:.1f}× robusta",
                        "Monthly average prices, US cents/lb: ICO Other Milds (arabica) and ICO Robustas (top); arabica ÷ robusta ratio (bottom). Jan-2010 → Aug-2026",
                        src(IMF, ICO))
    category_chart(s, "line", L, CT, 8.5, 3.2, pcats,
                   [dict(name="Arabica (Other Milds)", values=list(mm.arabica), color=C["arabica"], width=1.75,
                         labels={pk_a: f"{mm.arabica[pk_a]:.0f} ({mm.period[pk_a]})", lo_a: f"{mm.arabica[lo_a]:.0f} ({mm.period[lo_a]})",
                                 len(mm) - 1: f"{mm.arabica.iloc[-1]:.0f}"}, label_pos="above", label_size=8),
                    dict(name="Robusta", values=list(mm.robusta), color=C["robusta"], width=1.75,
                         labels={pk_r: f"{mm.robusta[pk_r]:.0f} ({mm.period[pk_r]})", lo_r: f"{mm.robusta[lo_r]:.0f} ({mm.period[lo_r]})",
                                 len(mm) - 1: f"{mm.robusta.iloc[-1]:.0f}"}, label_pos="below", label_size=8)],
                   vmin=0, vmax=450, major=100, cat_label_skip=12, plot=(0.07, 0.12, 0.91, 0.76))
    category_chart(s, "line", L, CT + 3.2, 8.5, 1.65, pcats,
                   [dict(name="Arabica ÷ robusta", values=list(mm.ratio), color=C["ink2"], width=1.5),
                    dict(name="2.0×", values=[2.0] * len(mm), color=C["deficit"], width=1, dash="DASH")],
                   vmin=1, vmax=3, major=0.5, cat_label_skip=12, num_fmt='0.0"×"', plot=(0.07, 0.12, 0.91, 0.66), legend=False)
    add_text(s, L + 0.65, CT + 3.2, 6, 0.25, [{"runs": [{"text": "Arabica ÷ robusta ratio", "bold": True, "color": C["ink2"]},
                                                        {"text": "   (dashed red line = 2.0×)", "color": C["muted"]}]}], size=9)
    side_panel(s, 9.25, CT, 3.53, 4.8, "Price regimes", [
        f"2017–20: glut. Arabica bottomed at {mm.arabica[lo_a]:.0f} c/lb ({mm.period[lo_a]}), robusta {mm.robusta[lo_r]:.0f} ({mm.period[lo_r]}).",
        "2021–22: Brazil frost + drought → arabica spike; ratio > 2.4×.",
        "2023–24: robusta shortfalls (Vietnam, Indonesia) → robusta record, ratio collapses to 1.15× (Sep-2024).",
        f"2025: both at records (robusta {mm.robusta[pk_r]:.0f}, arabica {mm.arabica[pk_a]:.0f}). 2026: easing on record crop outlook, ratio back to {M['prices']['ratio_last']:.1f}×.",
    ], size=10.5)
    notes(s, "Arabica = ICO 'Other Milds' indicator (Central American/Peruvian washed arabica, NY ex-dock), robusta = ICO 'Robustas'. "
             "IMF series to Sep-2025, ICO Coffee Market Report tables for Oct-2025 to Aug-2026.")

    # ------------------------------------------------------------------ 18 framework
    s = d.content_slide("03 · Three kinds of buyer",
                        "Three kinds of buyer: those who keep growing, those who don't react, and those who cut back",
                        f"Classification of the 30 largest consuming countries by the change in consumption (3-yr average 2023/24–2025/26 vs 2017/18–2019/20) "
                        f"while the green price rose {M['prices']['blend_change_3yavg_pct']:.0f}%",
                        src(USDA, IMF, ICO))
    cols = [("KEEP GROWING", "Demand up >+10% through the spike", C["green"], "↑", cls["grow"]),
            ("INELASTIC", "Between −5% and +10%: price barely matters", C["steady"], "→", cls["steady"]),
            ("CUT BACK", "Down >5%, or a clear break when prices peaked", C["decline"], "↓", cls["cut"])]
    cw3 = 3.95
    for i, (hd, rule, col, arrow, members) in enumerate(cols):
        x = L + i * (cw3 + 0.19)
        add_rect(s, x, CT, cw3, 0.7, col)
        add_text(s, x + 0.15, CT + 0.05, cw3 - 0.3, 0.6, [{"runs": [{"text": f"{arrow}  {hd}", "bold": True, "size": 17, "color": C["white"]}]}],
                 anchor="m")
        share = sum(ctry.loc[c, "c2025"] for c, _ in members if c in ctry.index) / W.consumption[2025] * 100
        add_text(s, x + 0.15, CT + 0.78, cw3 - 0.3, 0.55, f"{rule} · {share:.0f}% of world use", size=10.5, color=C["ink2"])
        rws = [[c.replace("Korea, South", "South Korea"), f"{sg(v, 0)}%", f"{ctry.loc[c,'c2025']:.1f}"] for c, v in members[:11]]
        table(s, x, CT + 1.3, cw3, 0.3 * (len(rws) + 1), ["Country", "Δ 3-yr avg", "m bags"], rws,
              col_widths=[2.05, 1.0, 0.9], font_size=10, header_fill=col, align=["l", "r", "r"], row_height=0.3)
        if hd == "CUT BACK":
            add_text(s, x, CT + 1.3 + 0.3 * (len(rws) + 1) + 0.15, cw3, 1.3, [
                {"runs": [{"text": "Brazil ", "bold": True}, {"text": "is classed as cutting because ABIC measured −2.3% in 2025 (per capita −3.9%) "
                                                                     "when retail prices rose ~80% y/y; USDA's 3-yr average shows −3%."}], "space_after": 4},
                {"runs": [{"text": "US (−3%) ", "bold": True}, {"text": "stays inelastic: its dip was destocking and reversed (+11% in 2024/25)."}]}],
                size=9.5, color=C["ink2"])
    notes(s, "Rule: Keep growing = 3-yr average consumption up more than 10%; Inelastic = between −5% and +10% with no structural break; "
             "Cut back = down more than 5% or a break in trend at the price peak (Brazil: ABIC −2.3% in 2025). Japan's decline started before the spike (structural + price).")

    # ------------------------------------------------------------------ 19-21 3x3 cards
    groups = [
        ("Keep growing", ["China", "Vietnam", "Turkey"], C["green"],
         "Keep growing whatever the price: China, Vietnam and Turkey added 50–90% through the spike",
         "Growth markets are building the habit (cafés, instant, young urban buyers); a doubling of green prices slowed China only in 2025/26."),
        ("Inelastic", ["EU-27 + UK", "United States", "Canada"], C["steady"],
         "Inelastic: Europe, the US and Canada barely moved while green prices more than doubled",
         "Year-to-year swings are inventory moves (destocking in 2022/23–2023/24, restocking in 2024/25), not drinkers quitting."),
        ("Cut back", ["Japan", "Brazil", "Algeria"], C["decline"],
         "Cut back: Japan, Algeria and Brazil are the marginal buyers — they lose volume when prices spike",
         "Japan was already declining (ageing, tea/RTD); Algeria is a robusta market hit by the 2023–25 robusta surge; Brazil cut only at +80% retail inflation."),
    ]
    cy_years = list(range(2015, 2026))
    for gname, countries, gcolr, title, takeaway in groups:
        s = d.content_slide(f"03 · {gname}", title,
                            "Each card: arabica & robusta coffee-year average price, US c/lb (top) · consumption, million bags, with y/y % (bottom). 2015/16 → 2025/26",
                            src(USDA, IMF, ICO, "red bars = y/y decline; elasticity = own estimate, see slide 'Elasticity'"))
        for k, c in enumerate(countries):
            price_card(s, L + k * 4.13, CT - 0.1, 3.97, 4.72, c, ctry, cons, cyp, cy_years, EL, gcolr, first=(k == 0))
        add_rect(s, L, 6.68, CW, 0.3, "FFFFFF")
        add_text(s, L, 6.66, CW, 0.3, [{"runs": [{"text": "Takeaway: ", "bold": True, "color": gcolr},
                                                 {"text": takeaway, "color": C["ink"]}]}], size=11)

    # ------------------------------------------------------------------ 22 elasticity
    el = EL.join(ctry[["c2025"]]).sort_values("c2025", ascending=False).head(16)
    el = el.sort_values("e_total")
    names = [n.replace("Korea, South", "South Korea") for n in el.index]
    sig = [(v + 1.96 * se < 0) for v, se in zip(el.e_total, el.se_total)]
    pcol = {i: (C["decline"] if sig[i] else "B5B3AC") for i in range(len(names))}
    labs = {i: f"{sg(v, 2)} (±{1.96 * se:.2f})" for i, (v, se) in enumerate(zip(el.e_total, el.se_total))}
    s = d.content_slide("03 · Elasticity",
                        "Measured short-run price elasticities are close to zero: a 10% rise in green prices moves volumes by ~0–1%",
                        "Estimated elasticity of consumption to the green price (same year + 1-year lag), 2006/07–2025/26; label = estimate (±95% range); red = significantly below zero",
                        src(USDA, IMF, "own regression: Δln(consumption) on Δln(0.6·arabica+0.4·robusta), t and t−1"))
    category_chart(s, "bar", L, CT - 0.05, 8.5, 4.85, names,
                   [dict(name="Elasticity", values=list(el.e_total), color="B5B3AC", point_colors=pcol, labels=labs,
                         label_pos="out", label_size=9, label_bold=False)],
                   vmin=-1.2, vmax=0.6, major=0.2, gap=40, num_fmt='0.0', plot=(0.2, 0.03, 0.74, 0.9), tick_low=True, cat_font=10)
    side_panel(s, 9.25, CT, 3.53, 4.8, "How to read it", [
        "Elasticity −0.1 = volumes fall 1% when the green price rises 10%.",
        "Big consumers (EU, US, Brazil) sit at ~0: green coffee is a small part of the cup price and habits are sticky.",
        ("Significantly negative: " + ", ".join(f"{n} ({sg(v, 2)})" for n, v, g in zip(names, el.e_total, sig) if g) +
         ". China's estimate is large but too noisy to be conclusive."),
        "Retail prices move less than green (next slide), so elasticities vs shelf prices are ~2–3× larger.",
    ], size=10.5)

    # ------------------------------------------------------------------ 23 retail pass-through
    us_idx, us_yoy, br_idx, br_dec = an.retail_series()
    calp = A["calp"]
    blend_cal = 0.6 * calp.arabica + 0.4 * calp.robusta
    yrs_us = [y for y in range(2010, 2025)]
    us_i = [us_idx.get(y) / us_idx.get(2019) * 100 for y in yrs_us]
    gr_i = [blend_cal.get(y) / blend_cal.get(2019) * 100 for y in yrs_us]
    s = d.content_slide("03 · Why consumers barely react",
                        f"Consumers see only part of the shock: US shelf prices rose {us_i[-1] - 100:.0f}% (2019→2024) while green coffee rose "
                        f"{gr_i[-1] - 100:.0f}%",
                        "Index 2019 = 100: US CPI 'coffee' (BLS) vs green price (0.6·arabica + 0.4·robusta, IMF/ICO), calendar years (left); "
                        "Brazil IPCA ground coffee index, Dec-2020 = 100 (right)",
                        src("BLS CPI (series: coffee, 1982-84=100)", "IBGE IPCA 'café moído'", IMF, "both retail series read from public copies of the official releases"))
    category_chart(s, "line", L, CT, 6.0, 4.8, [str(y) for y in yrs_us],
                   [dict(name="Green coffee", values=gr_i, color=C["arabica"], labels={len(yrs_us) - 1: f"{gr_i[-1]:.0f}"}, label_pos="above"),
                    dict(name="US retail (CPI coffee)", values=us_i, color=C["demand"], labels={len(yrs_us) - 1: f"{us_i[-1]:.0f}"}, label_pos="below")],
                   vmin=0, vmax=300, major=50, cat_label_skip=2, plot=(0.09, 0.12, 0.88, 0.76), markers=True)
    bi = br_idx[br_idx.index >= "2019-12"]
    bx = [int(k[:4]) + (int(k[5:7]) - 1) / 12 for k in bi.index]
    ipk = int(np.argmax(bi.values))
    scatter_chart(s, 6.75, CT, 3.4, 4.8, [dict(name="Brazil ground coffee (IPCA)", points=list(zip(bx, [float(v) for v in bi.values])),
                                               color=C["decline"], labels={ipk: f"{bi.max():.0f} ({bi.index[ipk]})", len(bi) - 1: f"{bi.iloc[-1]:.0f}"},
                                               label_pos_map={ipk: "above", len(bi) - 1: "below"})],
                  xmin=2019.5, xmax=2027, ymin=0, ymax=350, xmajor=1, ymajor=50, x_fmt='0', y_fmt='0',
                  plot=(0.14, 0.12, 0.82, 0.76), lines=True, legend=False)
    add_text(s, 6.8, CT - 0.02, 3.3, 0.3, "Brazil ground coffee, IPCA (Dec-2020 = 100)", size=9, color=C["ink2"])
    side_panel(s, 10.35, CT, 2.43, 4.8, "Pass-through", [
        f"US retail +{us_yoy.get('2025-06', float('nan')):.0f}% y/y in Jun-25, +{us_yoy.get('2026-01', float('nan')):.0f}% Jan-26, +{us_yoy.get('2026-07', float('nan')):.0f}% Jul-26: the shock arrives ~1 year late.",
        f"Brazil passes it faster: +{br_dec['2021']:.0f}% (2021), +{br_dec['2024']:.0f}% (2024), +{br_dec['2025']:.0f}% (2025), then {br_dec['2026']:.0f}% in 2026 YTD.",
        "The larger and faster the retail hit, the more volume is lost.",
    ], size=10)

    # ------------------------------------------------------------------ 24 Brazil threshold
    bra = A["bra"]
    yb = list(range(2020, 2026))
    cats_b = [str(y) for y in yb] + ["2026 YTD"]
    ipca = [br_dec[str(y)] for y in yb] + [br_dec["2026"]]
    vol = [bra.yoy_published.get(y) for y in yb] + [2.29]
    s = d.content_slide("03 · Brazil: where demand cracks",
                        "Brazil shows the threshold: volumes absorbed +40% retail inflation, fell only when it hit ~+80% y/y — and bounced back as prices fell",
                        "Retail ground-coffee inflation, % Dec/Dec (top, IBGE IPCA; 2026 = Dec-25→Aug-26) · domestic consumption, % y/y (bottom, ABIC; 2026 = Jan–Aug retail)",
                        src("ABIC Indicadores da Indústria de Café", "IBGE IPCA 'café moído'", "ABIC consumption years run Nov–Oct"))
    category_chart(s, "col", L, CT, 6.3, 2.45, cats_b,
                   [dict(name="Retail price inflation", values=ipca, color=C["decline"],
                         point_colors={i: ("B5B3AC" if v < 0 else C["decline"]) for i, v in enumerate(ipca)},
                         labels={i: pct(v, 0) for i, v in enumerate(ipca)}, label_pos="out", label_size=9)],
                   vmin=-20, vmax=60, major=20, num_fmt='0"%"', gap=45, tick_low=True, plot=(0.1, 0.08, 0.87, 0.76), legend=False)
    add_text(s, L + 0.6, CT - 0.05, 4, 0.25, "Retail price, % (IPCA ground coffee)", size=9, bold=True, color=C["ink2"])
    category_chart(s, "col", L, CT + 2.5, 6.3, 2.35, cats_b,
                   [dict(name="Consumption y/y", values=vol, color="EDA100",
                         point_colors={i: (C["decline"] if v < 0 else "EDA100") for i, v in enumerate(vol)},
                         labels={i: pct(v, 1) for i, v in enumerate(vol)}, label_pos="out", label_size=9)],
                   vmin=-3, vmax=3, major=1, num_fmt='0"%"', gap=45, tick_low=True, plot=(0.1, 0.08, 0.87, 0.76), legend=False)
    add_text(s, L + 0.6, CT + 2.47, 4, 0.25, "Volume, % y/y (ABIC)", size=9, bold=True, color=C["ink2"])
    rows = [["2021", pct(br_dec['2021'], 0), "+1.7%", "Absorbed"],
            ["2022", pct(br_dec['2022'], 0), "−1.0%", "First dip (inflation, lost income)"],
            ["2024", pct(br_dec['2024'], 0), "+1.1%", "Absorbed"],
            ["H1-2025", "+78% to +82% (12-month)", "−2.3% (2025)", "Break: per capita −3.9%"],
            ["2026 YTD", pct(br_dec['2026'], 0) + " (Dec→Aug)", "+2.3% (Jan–Aug)", "Recovery (+4.7% May–Aug)"]]
    table(s, 7.05, CT, 5.73, 2.6, ["Year", "Retail price (IPCA)", "Volume (ABIC)", "Reading"], rows,
          col_widths=[0.95, 1.6, 1.3, 1.88], font_size=10, bold_cols=(0,))
    side_panel(s, 7.05, CT + 2.8, 5.73, 2.0, "Threshold", [
        "Two years of +35–40% retail inflation were absorbed; volume only broke when 12-month inflation reached ~+80% (Mar–May 2025).",
        "Elasticity vs retail ≈ −0.03 to −0.05; demand returned within 2–3 quarters once prices fell (−17% y/y by Jul-2026).",
    ], size=10.5)

    # ------------------------------------------------------------------ 25 episodes table
    s = d.content_slide("03 · At what price increase?",
                        "Demand cracks with a lag: the lasting declines came the year after a +44–48% jump in green prices; most other dips were inventory swings",
                        "Decline episodes 2015/16–2025/26 in the 30 largest markets: consumption y/y vs green-price change (coffee-year average, same and previous year)",
                        src(USDA, IMF, ICO))
    ep = episodes(cons, cyp, ctry)
    rws = [[e["country"], e["year"], f"{sg(e['cons_yoy'], 1)}%", f"{sg(e['p_same'], 0)}%", f"{sg(e['p_prev'], 0)}%", f"{e['level']:.0f}", e["read"]]
           for e in ep[:13]]
    table(s, L, CT - 0.05, CW, 0.33 * (len(rws) + 1), ["Market", "Year", "Consumption y/y", "Green price, same yr", "Green price, prior yr",
                                                        "Green price level (c/lb)", "Reading"], rws,
          col_widths=[1.7, 1.0, 1.45, 1.55, 1.55, 1.65, 3.33], font_size=10, align=["l", "c", "r", "r", "r", "r", "l"], row_height=0.33)
    notes(s, "Green price = 60% ICO Other Milds + 40% ICO Robustas, coffee-year (Oct–Sep) average. 'Reading' separates price-driven drops from inventory swings "
             "(importers' USDA consumption includes stock changes) and structural declines (Japan).")

    # ------------------------------------------------------------------ 26 switching
    exm = A["ex"].copy()
    exm = exm[exm.rob_share_12m.notna()].reset_index(drop=True)
    rmap = dict(zip(m.period, m.ratio))
    exm["ratio"] = [rmap.get(p) for p in exm.export_month]
    xcat = [p[:4] for p in exm.export_month]
    s = d.content_slide("03 · Bean switching",
                        "Bean switching is real but second-order: robusta gains export share when arabica trades ≥1.8× robusta — "
                        "supply decides the big moves",
                        "Robusta share of world coffee exports, 12-month rolling, % (top, ICO) · arabica ÷ robusta price ratio, monthly (bottom, IMF/ICO); Aug-2016 → Jul-2026",
                        src(ICO, IMF, "own calculation"))
    shv = list(exm.rob_share_12m)
    first_jan = next(i for i, p in enumerate(exm.export_month) if p.endswith("-01"))
    category_chart(s, "line", L, CT, 8.5, 2.55, xcat,
                   [dict(name="Robusta share (12m)", values=shv, color=C["robusta"], width=2,
                         labels={int(np.argmin(shv[:60])): f"{min(shv[:60]):.1f}%", len(shv) - 1: f"{shv[-1]:.1f}%"}, label_pos="below")],
                   vmin=32, vmax=46, major=2, num_fmt='0"%"', cat_label_skip=12, plot=(0.07, 0.1, 0.91, 0.74), legend=False)
    add_text(s, L + 0.65, CT - 0.05, 6, 0.25, "Robusta share of world exports, 12-month rolling", size=9, bold=True, color=C["ink2"])
    category_chart(s, "line", L, CT + 2.6, 8.5, 2.25, xcat,
                   [dict(name="Arabica ÷ robusta", values=list(exm.ratio), color=C["arabica"], width=1.75),
                    dict(name="1.8×", values=[1.8] * len(exm), color=C["deficit"], width=1, dash="DASH")],
                   vmin=1, vmax=3, major=0.5, num_fmt='0.0"×"', cat_label_skip=12, plot=(0.07, 0.1, 0.91, 0.74), legend=False)
    add_text(s, L + 0.65, CT + 2.55, 6, 0.25, [{"runs": [{"text": "Arabica ÷ robusta price ratio", "bold": True, "color": C["ink2"]},
                                                         {"text": "   (dashed = 1.8×)", "color": C["muted"]}]}], size=9)
    bk = switch_buckets(A["ex"], m)
    rows = [[b["bucket"], sg(b["mean"], 1) + " pp", str(b["n"])] for b in bk]
    add_text(s, 9.25, CT - 0.05, 3.53, 0.5, "Ratio at month t → change in robusta export share over the next 12 months", size=10.5,
             bold=True, color=C["espresso"])
    table(s, 9.25, CT + 0.55, 3.53, 0.3 * (len(rows) + 1), ["Arabica ÷ robusta", "Robusta share Δ", "months"], rows,
          col_widths=[1.35, 1.38, 0.8], font_size=10, align=["l", "r", "r"], row_height=0.3)
    add_text(s, 9.25, CT + 0.65 + 0.3 * (len(rows) + 1), 3.53, 2.4, [
        {"runs": [{"text": "2022/23: ", "bold": True}, {"text": "ICO cites 'substitution towards the Robustas' after the 2021–22 arabica spike (ratio 2.5×)."}], "space_after": 4},
        {"runs": [{"text": "2023–24: ", "bold": True}, {"text": "robusta demand + Asian shortfalls close the gap to 1.15× (Sep-2024) — switching reverses."}], "space_after": 4},
        {"runs": [{"text": "2025/26: ", "bold": True}, {"text": f"ratio ~1.9–2.0× and a record conilon crop push the share to {shv[-1]:.0f}%."}], "space_after": 4},
        {"runs": [{"text": "Who: ", "bold": True}, {"text": "blend roasters, soluble makers and Brazil's own industry — not the individual drinker."}]},
    ], size=10, color=C["ink"])
    notes(s, "Correlation between the 12-month change in the robusta export share and the 12-month change in the price ratio (3–6 months earlier) is about +0.35: "
             "positive but modest, because export shares also move with Brazil's arabica on/off-year cycle and robusta crops in Vietnam/Brazil.")

    # ------------------------------------------------------------------ 27 structural shift
    rsh = [W.robusta_share[y] for y in yrs_f]
    ssh = [W.soluble_share[y] if y <= 2025 else None for y in yrs_f]
    s = d.content_slide("03 · Structural switch",
                        f"Structurally the world is moving to robusta and instant: robusta {mw['robusta_share_2005']:.0f}% → {mw['robusta_share_2025']:.0f}% "
                        f"of output, soluble {mw['soluble_share_2005']:.0f}% → {mw['soluble_share_2025']:.0f}% of use",
                        "Robusta share of world production, % (USDA) and soluble share of world consumption, % (USDA); 2026/27 = forecast",
                        src(USDA))
    category_chart(s, "line", L, CT, 8.5, 4.8, cats,
                   [dict(name="Robusta share of production", values=rsh, color=C["robusta"], markers=True,
                         labels={0: f"{rsh[0]:.0f}%", last - 1: f"{rsh[last-1]:.0f}%", last: f"{rsh[last]:.0f}%F"}, label_pos="above"),
                    dict(name="Soluble share of consumption", values=ssh, color="E87BA4", markers=True,
                         labels={0: f"{ssh[0]:.0f}%", last - 1: f"{ssh[last-1]:.0f}%"}, label_pos="below")],
                   vmin=0, vmax=60, major=10, num_fmt='0"%"', cat_label_skip=2, plot=(0.07, 0.12, 0.91, 0.76), markers=True)
    side_panel(s, 9.25, CT, 3.53, 4.8, "Why it matters", [
        f"Robusta output {f1(mw['robusta_2005'])}m → {f1(mw['robusta_2025'])}m bags (+{an.cagr(mw['robusta_2005'], mw['robusta_2025'], 20)*100:.1f}%/yr) vs arabica "
        f"{f1(mw['arabica_2005'])}m → {f1(mw['arabica_2025'])}m (+{an.cagr(mw['arabica_2005'], mw['arabica_2025'], 20)*100:.1f}%/yr).",
        "Cheaper beans + instant + espresso blends = the way price-sensitive demand keeps growing.",
        "Robusta's supply base (Vietnam, Brazil conilon, Uganda, Indonesia) is where demand growth lands.",
        "The switch is not one-way: in 2023–24 robusta got too expensive and the share dipped.",
    ], size=10.5)

    # ------------------------------------------------------------------ 28 buyer summary
    s = d.content_slide("03 · Marginal buyer summary",
                        "The marginal buyer is small, price-exposed and robusta-heavy — not the European or American drinker",
                        "Summary of evidence, 2021–2026", src(USDA, ICO, "ABIC", "IBGE", "BLS"))
    rows = [
        ["Keep growing", "China, Vietnam, Turkey, Saudi Arabia, Korea, Mexico, Indonesia, Ethiopia", "+13% to +90%", "Price slows, doesn't stop, growth (China −4% in 25/26)", "Demand floor: +1m bags/yr"],
        ["Inelastic", "EU-27+UK, US, Canada, Switzerland, Norway, Philippines, India", "−3% to +10%", "Inventory swings; retail pass-through small and late", "Anchor: ~52% of use"],
        ["Cut back", "Japan, Algeria, Russia, Serbia, Brazil (2025)", "−3% to −15%", "Brazil broke at +80% retail; Japan structural + price", "Swing: −0.5 to −1m bags"],
        ["Switchers", "Blend roasters, instant makers, Brazil's industry", "robusta share ±1–6 pp", "Add robusta at ratio ≥1.8×, back when <1.5×", "Moves the arbitrage"],
    ]
    table(s, L, CT, CW, 3.2, ["Type", "Who", "3-yr change", "Mechanism", "Market role"], rows,
          col_widths=[1.5, 4.0, 1.5, 3.3, 1.93], font_size=11, bold_cols=(0,),
          cell_colors={(0, 0): C["green"], (1, 0): C["ink2"], (2, 0): C["decline"], (3, 0): C["robusta"]})
    add_text(s, L, CT + 3.45, CW, 1.3, [
        {"runs": [{"text": "Answer to the brief: ", "bold": True}, {"text": "when prices rise, the volume that disappears is small (≈1–2m bags of 174m) and comes from "
                                                                              "Japan, North Africa, Eastern Europe/Russia and, at extreme retail inflation, Brazil. "
                                                                              "The bigger adjustment is the bean mix: roasters move toward robusta when arabica costs ≥1.8× robusta."}]}],
        size=13, color=C["ink"])

    # ================================================================== SECTION 4
    d.section_slide(4, "Marginal producers", "At the lowest prices, who keeps producing no matter what, who cuts, "
                                             "and who never comes back — even at high prices?")

    # ------------------------------------------------------------------ 29 small multiples
    origins = ["Brazil", "Vietnam", "Colombia", "Indonesia", "Ethiopia", "Uganda", "Honduras", "India"]
    s = d.content_slide("04 · Supply by origin",
                        "Four origins drive supply growth (Brazil, Vietnam, Ethiopia, Uganda); Colombia, Indonesia and Honduras have gone sideways",
                        "Production by origin, million bags, 2005/06 → 2025/26 (USDA), 2026/27 = USDA July-2026 forecast where published",
                        src(USDA))
    for k, o in enumerate(origins):
        col, row = k % 4, k // 4
        x, y = L + col * 3.08, CT + row * 2.45
        vals_o = [prod.loc[o, yy] for yy in yrs] + [PR.loc[o, "p2026f"] if not np.isnan(PR.loc[o, "p2026f"]) else None]
        mx = max(v for v in vals_o if v is not None)
        vmax = float(np.ceil(mx * 1.25 / 5) * 5) if mx > 10 else float(np.ceil(mx * 1.3))
        cl = PR.loc[o, "cagr_05_25"]
        add_text(s, x, y, 2.95, 0.3, [{"runs": [{"text": o + "  ", "bold": True, "size": 12},
                                                {"text": f"{sg(cl, 1)}%/yr · {PR.loc[o,'share2025']:.0f}% of world", "size": 9.5, "color": C["ink2"]}]}])
        category_chart(s, "col", x, y + 0.28, 2.95, 2.05, cats,
                       [dict(name=o, values=vals_o, color=C["supply"], point_colors={last: SUPPLY_FC},
                             labels={0: f"{vals_o[0]:.1f}"} | ({last: f"{vals_o[last]:.1f}F"} if vals_o[last] else {last - 1: f"{vals_o[last-1]:.1f}"}),
                             label_pos="out", label_size=8, label_bold=False)],
                       vmin=0, vmax=vmax, gap=30, cat_label_skip=5, plot=(0.1, 0.12, 0.86, 0.72), val_font=8, cat_font=8,
                       legend=False)

    # ------------------------------------------------------------------ 30 response map
    PRr = PR.drop(index=["World", "EU-27 + UK", "European Union"], errors="ignore")
    PRr = PRr[PRr.p2025 >= 0.4]
    pcls = producer_class(PRr)
    ccol = {"Produce regardless": C["demand"], "Cut when low": "EDA100", "Decline regardless": C["decline"], "Expand when high": C["supply"]}
    series = []
    for k in ["Produce regardless", "Expand when high", "Cut when low", "Decline regardless"]:
        sub = [c for c in PRr.index if pcls[c] == k]
        pts = [(float(PRr.loc[c, "low_price_resp"]), float(PRr.loc[c, "high_price_resp"])) for c in sub]
        series.append(dict(name=k, points=pts, color=ccol[k], labels={i: c.replace("Papua New Guinea", "PNG").replace("Cote d'Ivoire", "Côte d'Ivoire")
                                                                      for i, c in enumerate(sub)}, label_size=8.5))
    s = d.content_slide("04 · Producer response map",
                        "Producer response map: output after the 2018–19 price low vs output during the 2022–25 price boom",
                        "Change in production, %: average 2019/20–2021/22 vs 2016/17–2018/19 (x, low-price response) and average 2022/23–2025/26 vs 2019/20–2021/22 "
                        "(y, high-price response); origins ≥0.4m bags",
                        src(USDA, IMF))
    fr = scatter_chart(s, L, CT, 8.5, 4.8, series, xmin=-30, xmax=30, ymin=-30, ymax=30, xmajor=10, ymajor=10,
                       x_fmt='0"%"', y_fmt='0"%"', plot=(0.08, 0.1, 0.88, 0.8))
    add_line(s, fr.xy_x(0), fr.top, fr.xy_x(0), fr.top + fr.height, C["axis"], 1)
    def lst(kind, key=None, n=6):
        cs = [c for c in PRr.sort_values("p2025", ascending=False).index if pcls[c] == kind][:n]
        nm = lambda c: c.replace("Papua New Guinea", "PNG").replace("Cote d'Ivoire", "Côte d'Ivoire")
        return ", ".join(f"{nm(c)} {sg(PRr.loc[c, key], 0)}%" if key else nm(c) for c in cs)
    side_panel(s, 9.25, CT, 3.53, 4.8, "Four types", [
        [{"text": "Produce regardless: ", "bold": True, "color": C["demand"]}, {"text": lst("Produce regardless") + " — no cut after the low."}],
        [{"text": "Cut when low: ", "bold": True, "color": "B07800"}, {"text": lst("Cut when low", "low_price_resp") + " (after the low)."}],
        [{"text": "Decline regardless: ", "bold": True, "color": C["decline"]}, {"text": lst("Decline regardless", "high_price_resp") + " (during the boom)."}],
        [{"text": "Expand when high: ", "bold": True, "color": "12805A"}, {"text": lst("Expand when high", "high_price_resp") + " — come back when prices pay."}],
    ], size=10)

    # ------------------------------------------------------------------ 31 producer types table
    s = d.content_slide("04 · Price thresholds",
                        f"Who produces no matter what — and who cuts when arabica stays near {cyp.loc[2017:2019, 'arabica'].mean():.0f} c/lb for two years",
                        "Producer types, evidence and the price levels at which behaviour changed (USDA production; ICO/IMF prices)",
                        src(USDA, IMF, ICO))
    lowp = cyp.loc[2017:2019, "arabica"].mean()
    prevp = cyp.loc[2014:2016, "arabica"].mean()
    rows = [
        ["Produce no matter what", "Brazil, Vietnam, Ethiopia, Uganda, India",
         f"Kept growing through arabica ~{lowp:.0f} c/lb and robusta ~{cyp.loc[2017:2019,'robusta'].mean():.0f} c/lb (2017/18–2019/20)",
         "Scale & mechanisation (Brazil), high yields (Vietnam), low cash costs/smallholder (Ethiopia, Uganda)"],
        ["Cut when prices are low", "Honduras, Peru, El Salvador, Colombia (PNG too, then re-expanded)",
         f"Output fell 7–26% after arabica averaged {lowp:.0f} c/lb (−{(1 - lowp / prevp) * 100:.0f}% vs 2014–16) for 2+ years",
         "High labour cost per bag, rust, fertiliser cuts, farm abandonment & migration"],
        ["Decline even at high prices", "Côte d'Ivoire, Costa Rica, Cameroon, Guatemala, Nicaragua, Malaysia",
         f"Still falling in 2022–25 with arabica > 200 c/lb", "Land competes with cocoa, rubber, durian, housing; ageing trees and farmers"],
        ["Expand when prices are high", "Brazil (conilon), Vietnam, Uganda, Ethiopia, PNG, Thailand",
         "Respond with a 2–4 year lag: record 2025/26 conilon, record 189.7m world crop 2026/27F", "Fertiliser & replanting pay again; new robusta area"],
    ]
    table(s, L, CT, CW, 4.2, ["Type", "Who", "Price trigger (evidence)", "Why"], rows, col_widths=[2.2, 3.1, 3.6, 3.33],
          font_size=10.5, bold_cols=(0,), cell_colors={(0, 0): C["demand"], (1, 0): "B07800", (2, 0): C["decline"], (3, 0): "12805A"})
    add_text(s, L, CT + 4.35, CW, 0.5, "Supply elasticity is low in the short run (trees take 3–4 years) and asymmetric: low prices cut output at the "
                                       "high-cost margin within 1–2 years; high prices add output mainly where land and capital are cheap (Brazil, Vietnam, East Africa).",
             size=11, color=C["ink2"])

    # ------------------------------------------------------------------ 32 supply response 2026/27
    s = d.content_slide("04 · Supply response",
                        f"High prices are bringing supply back: USDA sees a record {f1(mw['prod_2026f'])}m bags in 2026/27 (+{f1(mw['prod_2026f'] - mw['prod_2025'])}m)",
                        "Production, million bags: 2025/26 (as implied by the July-2026 report or attaché estimate) vs 2026/27 forecast; *attaché (GAIN) figures",
                        src("USDA Coffee: World Markets and Trade (Jul-2026)", "USDA GAIN attaché reports (Colombia, Indonesia, Ethiopia, Uganda)"))
    # 2025/26 base = value implied by the July-2026 report (2026/27 forecast minus the stated change) or the attaché estimate
    orig = [("Brazil", 63.0, 71.9), ("Vietnam", 31.7, 32.5), ("Colombia*", 12.5, 13.4), ("Indonesia*", 12.37, 11.38),
            ("Ethiopia*", 11.56, 12.1), ("Uganda*", 7.1, 7.2), ("Honduras", 5.5, 6.0)]
    category_chart(s, "col", L, CT, 8.5, 4.8, [o[0] for o in orig],
                   [dict(name="2025/26", values=[o[1] for o in orig], color="9FDCC6"),
                    dict(name="2026/27F", values=[o[2] for o in orig], color=C["supply"],
                         labels={i: f"{o[2]:.1f}" for i, o in enumerate(orig)}, label_pos="out", label_size=9)],
                   vmin=0, vmax=80, major=20, gap=60, overlap=-5, plot=(0.07, 0.12, 0.91, 0.76))
    side_panel(s, 9.25, CT, 3.53, 4.8, "2026/27 set-up", [
        f"World output {f1(mw['prod_2026f'])}m (+{W.prod_yoy[2026]:.0f}%), arabica record 105.9m; consumption {f1(mw['cons_2026f'])}m (+3.6%).",
        "Stocks rebuild +1.9m to 26.3m — first rise after five draws.",
        "Brazil +8.9m (arabica +9.5m to 47.5m); Vietnam record 32.5m; Ethiopia overtakes Indonesia.",
        f"Prices already eased: arabica {M['prices']['arabica_last']:.0f} c/lb, robusta {M['prices']['robusta_last']:.0f} (Aug-26) vs peaks {M['prices']['arabica_peak']:.0f}/{M['prices']['robusta_peak']:.0f}.",
        "*attaché forecasts; Indonesia down on excess rain.",
    ], size=10.5)

    # ================================================================== SECTION 5
    d.section_slide(5, "Tracker & trading implications", "Which countries are increasing, steady or decreasing — and what to watch next")

    # ------------------------------------------------------------------ 33 consumption tracker
    tr = ctry.drop(index=["World", "European Union", "United Kingdom"]).sort_values("c2025", ascending=False).head(22)
    rws, fills, colors = [], {}, {}
    cls_map = {c: k for k, lst in cls.items() for c, _ in lst}
    for r_i, (c, rr) in enumerate(tr.iterrows()):
        k = cls_map.get(c, "steady")
        arrow = {"grow": "↑ growing", "steady": "→ steady", "cut": "↓ cutting"}[k]
        rws.append([c.replace("Korea, South", "South Korea"), f"{rr.c2025:.1f}", f"{rr.share2025:.1f}%", f"{sg(rr.cagr_05_15, 1)}%",
                    f"{sg(rr.cagr_15_20, 1)}%", f"{sg(rr.cagr_20_25, 1)}%", f"{sg(rr.chg_spike_3yavg, 0)}%", f"{sg(rr.yoy_2025, 1)}%", arrow])
        colors[(r_i, 8)] = {"grow": C["green"], "steady": C["ink2"], "cut": C["decline"]}[k]
        for j, v in ((3, rr.cagr_05_15), (4, rr.cagr_15_20), (5, rr.cagr_20_25)):
            if not np.isnan(v):
                fills[(r_i, j)] = heat(v)
    s = d.content_slide("05 · Consumption tracker",
                        "Consumption tracker: who is increasing, steady or decreasing",
                        "Top 22 consuming countries/blocs, USDA; CAGR by period, change in 3-yr average through the price spike, latest y/y (2025/26 vs 2024/25)",
                        src(USDA))
    table(s, L, CT - 0.2, CW, 0.2 * 23, ["Country", "2025/26 m bags", "Share", "CAGR 05→15", "CAGR 15→20", "CAGR 20→25", "Spike Δ (3-yr avg)",
                                         "y/y 25/26", "Trend"], rws,
          col_widths=[2.1, 1.25, 0.9, 1.3, 1.3, 1.3, 1.5, 1.1, 1.48], font_size=9, align=["l", "r", "r", "r", "r", "r", "r", "r", "l"],
          cell_fills=fills, cell_colors=colors, row_height=0.2)

    # ------------------------------------------------------------------ 34 production tracker
    pt = PR.drop(index=["World", "EU-27 + UK", "European Union"], errors="ignore").sort_values("p2025", ascending=False).head(20)
    rws, fills, colors = [], {}, {}
    for r_i, (c, rr) in enumerate(pt.iterrows()):
        k = producer_class(pt.loc[[c]])[c]
        rws.append([c, f"{rr.p2025:.1f}", f"{rr.share2025:.1f}%", f"{rr.robusta_share2025:.0f}%", f"{sg(rr.cagr_05_25, 1)}%",
                    f"{sg(rr.low_price_resp, 0)}%", f"{sg(rr.high_price_resp, 0)}%", f"{rr.p2026f:.1f}" if not np.isnan(rr.p2026f) else "–", k])
        colors[(r_i, 8)] = ccol[k] if k != "Cut when low" else "B07800"
        for j, v in ((4, rr.cagr_05_25),):
            fills[(r_i, j)] = heat(v)
    s = d.content_slide("05 · Production tracker",
                        "Production tracker: who is expanding, who is stuck, who is shrinking",
                        "Top 20 producers, USDA; responses measured on 3-yr averages around the 2018–19 low and the 2022–25 boom",
                        src(USDA))
    table(s, L, CT - 0.2, CW, 0.22 * 21, ["Origin", "2025/26 m bags", "Share", "Robusta %", "CAGR 05→25", "After low", "In boom", "2026/27F", "Type"], rws,
          col_widths=[2.2, 1.3, 0.95, 1.05, 1.25, 1.1, 1.1, 1.1, 2.18], font_size=9.5, align=["l", "r", "r", "r", "r", "r", "r", "r", "l"],
          cell_fills=fills, cell_colors=colors, row_height=0.22)

    # ------------------------------------------------------------------ 35 what to watch
    s = d.content_slide("05 · What to watch", "Trading implications: demand is the anchor, supply and the arbitrage are the triggers",
                        None, src(USDA, ICO, IMF, "ABIC"))
    items = [
        ("Demand baseline", f"Pencil in +2.4m bags/yr (+1.4–1.7%). USDA 2026/27F {f1(mw['cons_2026f'])}m; ICO 2025/26 180.6m (−0.8%, lower US)."),
        ("Stocks-to-use", f"The 2021–25 spike happened below ~16%. 2026/27F {W.stocks_to_use[2026]:.1f}% — still tight; a second big crop is needed to normalise."),
        ("Arbitrage", f"Ratio {M['prices']['ratio_last']:.1f}× (Aug-26). Above ~1.8× roasters add robusta; below ~1.5× they go back to arabica."),
        ("Marginal buyers", "Watch Brazil retail (IPCA café moído), Japan (AJCA), North Africa/Russia imports: they give first signs of demand loss."),
        ("Growth buyers", "China/SE Asia/Turkey/Gulf absorb ~1m extra bags a year even at high prices — a floor under demand."),
        ("Producer response", "Record 2026/27 crop = high-price response from Brazil, Vietnam, East Africa; Central America will not add much."),
    ]
    for i, (hd, body) in enumerate(items):
        col, row = i % 2, i // 2
        x, y = L + col * 6.2, 1.8 + row * 1.6
        add_rect(s, x, y, 6.0, 1.45, C["panel"])
        add_text(s, x + 0.2, y + 0.12, 5.6, 0.35, hd, size=15, bold=True, color=C["espresso"])
        add_text(s, x + 0.2, y + 0.52, 5.6, 0.9, body, size=13, color=C["ink"])

    # ------------------------------------------------------------------ 36 appendix sources
    s = d.content_slide("Appendix · Sources", "Sources, vintages and how each number was obtained", None,
                        "Full URLs and per-value provenance: research/coffee-demand/data (raw/*.csv, source_files/MANIFEST) and the Word guide")
    rows = [
        ["USDA FAS PSD — coffee (all countries, 1960–2025/26)", "Official bulk file psd_coffee_csv.zip (Dec-2025 release), read from a public mirror that downloaded it on 21-Jun-2026; "
         "98% of values identical to a second mirror (Jun-2024 release); world totals match the Dec-2025 report", "apps.fas.usda.gov/psdonline/downloads"],
        ["USDA Coffee: World Markets and Trade, Jul-2026", "2026/27 forecasts (world, Brazil, Vietnam, EU, US, China) — verified through web search of the report and trade press",
         "fas.usda.gov/data/coffee-world-markets-and-trade"],
        ["IMF Primary Commodity Prices", "Monthly ICO Other Milds & Robustas, 1990–Sep-2025, from the IMF source file (external-data.xls, Mar-2026)",
         "imf.org/en/Research/commodity-prices"],
        ["ICO Coffee Market Reports", "Monthly indicator prices Oct-2025–Aug-2026 and exports by coffee group Sep-2015–Jul-2026 (report tables); balance & regions",
         "ico.org/documents/cy2025-26/cmr-0826-e.pdf"],
        ["ABIC / IBGE / BLS", "Brazil consumption (ABIC), ground-coffee IPCA index (IBGE), US CPI coffee (BLS)", "abic.com.br · ibge.gov.br · bls.gov"],
        ["World Bank WDI", "Population (SP.POP.TOTL) and GDP per capita (NY.GDP.PCAP.CD)", "data.worldbank.org"],
        ["Company filings", "Starbucks 10-K store counts; Luckin 20-F (as quoted)", "sec.gov"],
    ]
    table(s, L, CT - 0.3, CW, 4.5, ["Dataset", "What was used and how", "Official home"], rows, col_widths=[3.2, 6.4, 2.63],
          font_size=9.5, bold_cols=(0,))

    # ------------------------------------------------------------------ 37 appendix gaps
    s = d.content_slide("Appendix · Limits & refresh", "What is not in this version, and how to refresh everything from the official files",
                        None, "Script: research/coffee-demand/scripts/fetch_official_data.py → analysis.py → build_deck.py / build_doc.py")
    side_panel(s, L, CT - 0.3, 6.0, 4.9, "Known limits", [
        "The sandbox blocked direct downloads from usda.gov, ico.org, worldbank.org, eurostat, census, comtrade; official files were read from public mirrors and cross-checked.",
        "USDA consumption = disappearance: importers' y/y moves include stock changes.",
        "No official channel split (home vs café) outside Brazil; café chains used as a proxy.",
        "Import-origin data (Eurostat, US Census, Comtrade) not pulled — the script does it.",
        "Cost-of-production surveys (CONAB, FNC, ICO) not included; producer thresholds are inferred from observed output.",
    ], size=12.5)
    side_panel(s, 6.78, CT - 0.3, 6.0, 4.9, "Refresh in 3 commands", [
        "python scripts/fetch_official_data.py  — USDA PSD, World Bank Pink Sheet, IMF, FRED, US Census, UN Comtrade, Eurostat",
        "python scripts/analysis.py  — rebuilds every table in data/clean and output/metrics.json",
        "python scripts/build_deck.py  and  python scripts/build_doc.py  — regenerate this deck and the Word guide",
        "Every downloaded file is logged with URL, time and SHA-256 in data/source_files/MANIFEST.csv.",
    ], size=12.5)

    d.save(OUT)
    print("saved", OUT, "slides:", len(d.prs.slides))
    return OUT


# ============================================================================ helpers used above
def heat(v):
    """Diverging fill for growth rates: red below 0, grey near 0, violet above."""
    if v <= -2:
        return "F6C9C8"
    if v < -0.5:
        return "FBE3E2"
    if v < 0.5:
        return "F0EFEC"
    if v < 2:
        return "E3E0F4"
    if v < 5:
        return "CFC9EE"
    return "B6AEE6"


def classify(ctry):
    """Consumer classes from the 3-yr average change through the spike (see slide notes)."""
    t = ctry.drop(index=["World", "European Union", "United Kingdom"]).sort_values("c2025", ascending=False).head(30)
    grow, steady, cut = [], [], []
    for c, r in t.iterrows():
        v = r.chg_spike_3yavg
        if c == "Venezuela":
            continue            # collapse is macro-economic, not a coffee price response
        if c == "Brazil":
            cut.append((c, v)); continue
        if v > 10:
            grow.append((c, v))
        elif v < -5:
            cut.append((c, v))
        else:
            steady.append((c, v))
    key = lambda x: -abs(x[1])
    return {"grow": sorted(grow, key=lambda x: -x[1]), "steady": sorted(steady, key=lambda x: -ctry.loc[x[0], "c2025"]),
            "cut": sorted(cut, key=lambda x: x[1])}


def producer_class(PRr):
    """Producer types from the output response after the 2018-19 low (lo) and during the 2022-25 boom (hi), 3-yr averages."""
    out = {}
    for c, r in PRr.iterrows():
        lo, hi = r.low_price_resp, r.high_price_resp
        if hi <= -8:
            out[c] = "Decline regardless"
        elif lo <= -5 and hi < 5:
            out[c] = "Cut when low"
        elif hi >= 5 and lo < 0:
            out[c] = "Expand when high"
        else:
            out[c] = "Produce regardless"
    return out


def episodes(cons, cyp, ctry):
    top = ctry.drop(index=["World", "European Union", "United Kingdom", "Venezuela"]).sort_values("c2025", ascending=False).head(30).index
    out = []
    for c in top:
        for y in range(2016, 2026):
            a, b = cons.loc[c, y - 1], cons.loc[c, y]
            if np.isnan(a) or np.isnan(b):
                continue
            ch = (b / a - 1) * 100
            if ch <= -3.0 and cons.loc[c, 2025] >= 1.0:
                p_same = cyp.blend_yoy.get(y)
                p_prev = cyp.blend_yoy.get(y - 1)
                nxt = (cons.loc[c, y + 1] / b - 1) * 100 if y < 2025 else np.nan
                if c == "Japan":
                    read = "Structural decline, deepened by price"
                elif not np.isnan(nxt) and nxt >= abs(ch) * 0.4:
                    read = f"Reversed next year ({sg(nxt, 1)}%): inventory swing"
                elif p_same is not None and p_same > 15:
                    read = "Price-driven (same year)"
                elif (p_prev or 0) > 15:
                    read = "Price-driven, 1-year lag"
                else:
                    read = "Not price-driven"
                out.append({"country": c.replace("Korea, South", "South Korea"), "year": an.my(y), "cons_yoy": ch,
                            "p_same": p_same, "p_prev": p_prev, "level": cyp.blend.get(y), "read": read})
    out.sort(key=lambda e: (e["year"], e["cons_yoy"]), reverse=True)
    return out


def switch_buckets(ex, m):
    sh = ex.set_index("export_month")["rob_share_12m"].dropna()
    r = dict(zip(m.period, m.ratio))
    idx = list(sh.index)
    rows = []
    for i, t in enumerate(idx[:-12]):
        if t in r:
            rows.append((r[t], sh[idx[i + 12]] - sh[t]))
    d = pd.DataFrame(rows, columns=["ratio", "d"])
    out = []
    for lo, hi, lab in [(0, 1.5, "below 1.5×"), (1.5, 1.8, "1.5–1.8×"), (1.8, 2.2, "1.8–2.2×"), (2.2, 9, "above 2.2×")]:
        sub = d[(d.ratio > lo) & (d.ratio <= hi)]
        out.append({"bucket": lab, "mean": sub.d.mean(), "n": len(sub)})
    return out


def switch_stats(excy):
    e = excy[excy.months >= 8].copy()
    e["d_share"] = e.rob_share.diff()
    e["ratio_prev"] = e.ratio.shift(1)
    hi = e[e.ratio_prev >= 2.0].d_share.mean()
    lo = e[e.ratio_prev < 1.7].d_share.mean()
    return {"after_high": hi, "after_low": lo}


def price_card(s, x, y, w, h, country, ctry, cons, cyp, cy_years, EL, gcolr, first=False):
    """One consumer card: prices on top, consumption bars (with y/y labels) underneath."""
    nm = country.replace("Korea, South", "South Korea")
    chg = ctry.loc[country, "chg_spike_3yavg"]
    add_rect(s, x, y, w, h, "FAFAF8")
    add_text(s, x + 0.12, y + 0.06, w - 0.24, 0.32, [{"runs": [{"text": nm, "bold": True, "size": 14, "color": C["espresso"]},
                                                               {"text": f"   3-yr avg {sg(chg, 0)}%", "bold": True, "size": 11, "color": gcolr}]}])
    cats = [short(yy) for yy in cy_years]
    category_chart(s, "line", x, y + 0.36, w, 1.45, cats,
                   [dict(name="Arabica", values=[cyp.arabica[yy] for yy in cy_years], color=C["arabica"], width=1.75),
                    dict(name="Robusta", values=[cyp.robusta[yy] for yy in cy_years], color=C["robusta"], width=1.75)],
                   vmin=0, vmax=400, major=200, cat_label_skip=20, plot=(0.13, 0.08, 0.83, 0.62), val_font=8, cat_font=7,
                   legend=first, legend_pos="t")
    vals = [cons.loc[country, yy] for yy in cy_years]
    yoy = [None] + [(vals[i] / vals[i - 1] - 1) * 100 for i in range(1, len(vals))]
    pc_ = {i: C["decline"] for i, v in enumerate(yoy) if v is not None and v < 0}
    labs = {i: f"{sg(v, 0)}" for i, v in enumerate(yoy) if v is not None and i >= 5}
    mx = max(vals)
    vmin = 0.0
    step = 0.5 if mx < 3 else (1.0 if mx < 8 else (5.0 if mx < 30 else 10.0))
    vmax = float(np.ceil(mx * 1.2 / step) * step)
    category_chart(s, "col", x, y + 1.8, w, 2.35, cats,
                   [dict(name="Consumption", values=vals, color=C["demand"], point_colors=pc_, labels=labs, label_pos="out",
                         label_size=8, label_bold=False)],
                   vmin=vmin, vmax=vmax, major=step if mx < 30 else 10.0, gap=35, cat_label_skip=2, plot=(0.13, 0.06, 0.83, 0.76),
                   val_font=8, cat_font=7, legend=False, num_fmt='0.0' if mx < 8 else '0')
    e = EL.loc[country] if country in EL.index else None
    txt = (f"2025/26: {vals[-1]:.2f}m bags · elasticity {sg(e.e_total, 2)} (±{1.96 * e.se_total:.2f})" if e is not None
           else f"2025/26: {vals[-1]:.2f}m bags")
    add_text(s, x + 0.12, y + h - 0.42, w - 0.24, 0.36, txt, size=9, color=C["ink2"])


if __name__ == "__main__":
    build()
