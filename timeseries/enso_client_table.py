#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Brazil ENSO table in the client's convention (English, Excel output).

Index of crop year Y/Y+1 = the growing-season value of the NOAA relative ONI
(RONI, table data/oni.csv provided by the user): the extreme of the seven
3-month seasons SON(Y-1) .. FMA(Y), i.e. flowering (Sep-Nov of Y-1) to the end
of fruit development (Apr of Y), harvest May-Sep of Y.
Classes (client's thresholds):
    El Nino strong   index >= 1.6
    El Nino normal   0.7 <= index < 1.6
    El Nino weak     0.5 <= index < 0.7
    Neutral          -0.7 < index < 0.5
    La Nina          index <= -0.7
Production change = crop year Y/Y+1 vs Y-1/Y, robusta and arabica separately.
Weather: the balance sheet only has state averages; Espirito Santo stands in
for Sao Mateus / Linhares (robusta), Minas Gerais for arabica, until the NASA
POWER regional file is built.

Outputs: output/enso/brazil_enso_client.xlsx (sheets Robusta, Arabica, Index,
Weather) and brazil_enso_client_summary.csv.
"""
import os
import numpy as np
import pandas as pd
from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.chart.label import DataLabelList
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "output", "enso")
COLS = ["DJF", "JFM", "FMA", "MAM", "AMJ", "MJJ", "JJA", "JAS", "ASO", "SON", "OND", "NDJ"]
CLASSES = [("El Nino strong", ">= 1.6"), ("El Nino normal", "0.7 to 1.5"), ("El Nino weak", "0.5 to 0.7"),
           ("Neutral", "-0.7 to 0.5"), ("La Nina", "<= -0.7")]


def season_index(oni, y):
    """extreme RONI over SON(y-1), OND(y-1), NDJ(y-1), DJF(y), JFM(y), FMA(y)."""
    vals = []
    for yy, cols in ((y - 1, ["SON", "OND", "NDJ"]), (y, ["DJF", "JFM", "FMA"])):
        if yy in oni.index:
            vals += [v for v in oni.loc[yy, cols].tolist() if pd.notna(v)]
    if not vals:
        return np.nan
    return max(vals, key=abs)


def classify(x):
    if np.isnan(x):
        return "n/a"
    if x >= 1.6:
        return "El Nino strong"
    if x >= 0.7:
        return "El Nino normal"
    if x >= 0.5:
        return "El Nino weak"
    if x <= -0.7:
        return "La Nina"
    return "Neutral"


def main():
    os.makedirs(OUT, exist_ok=True)
    oni = pd.read_csv(os.path.join(HERE, "data", "oni.csv")).set_index("year")
    d = pd.read_csv(os.path.join(HERE, "data", "coffee_series.csv"))
    ex = pd.read_csv(os.path.join(HERE, "data", "exog_brazil.csv")).set_index("year")
    ser = {k: d[(d.country == "Brazil") & (d.series == v)].set_index("year")["value"].sort_index()
           for k, v in [("Robusta", "Production Robusta"), ("Arabica", "Production Arabica")]}
    years = [y for y in range(2008, 2027) if y in ser["Robusta"].index]
    rows = []
    for y in years:
        idx = season_index(oni, y)
        rec = dict(crop_year=f"{y}/{str(y + 1)[2:]}", year=y, index=idx, enso_class=classify(idx),
                   status="USDA estimate" if y >= 2026 else "historical")
        for sp in ("Robusta", "Arabica"):
            s = ser[sp]
            rec[f"{sp}_prod"] = s.get(y); rec[f"{sp}_prev"] = s.get(y - 1)
            rec[f"{sp}_change_pct"] = (s[y] / s[y - 1] - 1) * 100 if y in s.index and (y - 1) in s.index else np.nan
        rec["ES_rain_mm"] = ex.loc[y, "rain_es"] if y in ex.index else np.nan
        rec["ES_temp_c"] = ex.loc[y, "temp_es"] if y in ex.index else np.nan
        rec["MG_rain_mm"] = ex.loc[y, "rain_mg"] if y in ex.index else np.nan
        rec["MG_temp_c"] = ex.loc[y, "temp_mg"] if y in ex.index else np.nan
        rows.append(rec)
    df = pd.DataFrame(rows)
    hist = df[df.status == "historical"]
    base = ex.loc[1998:2025, ["rain_es", "temp_es", "rain_mg", "temp_mg"]].mean()

    summ = []
    for cls, rng in CLASSES:
        g = hist[hist.enso_class == cls]
        rec = dict(enso_class=cls, index_range=rng, n=len(g), crop_years=", ".join(g.crop_year))
        for sp in ("Robusta", "Arabica"):
            rec[f"{sp}_avg_change_pct"] = g[f"{sp}_change_pct"].mean() if len(g) else np.nan
            rec[f"{sp}_min_pct"] = g[f"{sp}_change_pct"].min() if len(g) else np.nan
            rec[f"{sp}_max_pct"] = g[f"{sp}_change_pct"].max() if len(g) else np.nan
        rec["ES_rain_dev_mm"] = g.ES_rain_mm.mean() - base.rain_es if len(g) else np.nan
        rec["ES_temp_dev_c"] = g.ES_temp_c.mean() - base.temp_es if len(g) else np.nan
        rec["MG_rain_dev_mm"] = g.MG_rain_mm.mean() - base.rain_mg if len(g) else np.nan
        rec["MG_temp_dev_c"] = g.MG_temp_c.mean() - base.temp_mg if len(g) else np.nan
        summ.append(rec)
    summ = pd.DataFrame(summ)
    df.to_csv(os.path.join(OUT, "brazil_enso_client_years.csv"), index=False, float_format="%.2f")
    summ.to_csv(os.path.join(OUT, "brazil_enso_client_summary.csv"), index=False, float_format="%.2f")

    # ---------------- Excel
    wb = Workbook()
    head = Font(bold=True, color="FFFFFF"); fill = PatternFill("solid", fgColor="2A78D6")
    def write(ws, r0, header, data, widths=None):
        for j, h in enumerate(header, 1):
            c = ws.cell(row=r0, column=j, value=h); c.font = head; c.fill = fill; c.alignment = Alignment(wrap_text=True, vertical="center")
        for i, row in enumerate(data, 1):
            for j, v in enumerate(row, 1):
                c = ws.cell(row=r0 + i, column=j, value=(None if (isinstance(v, float) and np.isnan(v)) else v))
                if isinstance(v, float):
                    c.number_format = "0.0"
        if widths:
            for j, w in enumerate(widths, 1):
                ws.column_dimensions[get_column_letter(j)].width = w
        return r0 + len(data)

    for sp, wcols, wlab in (("Robusta", ("ES_rain_mm", "ES_temp_c"), "Espirito Santo (proxy for Sao Mateus / Linhares)"),
                            ("Arabica", ("MG_rain_mm", "MG_temp_c"), "Minas Gerais (proxy for Cerrado / Sul de Minas)")):
        ws = wb.active if sp == "Robusta" else wb.create_sheet()
        ws.title = sp
        ws["A1"] = f"Brazil {sp}: production change by ENSO class (client convention)"; ws["A1"].font = Font(bold=True, size=13)
        ws["A2"] = ("Index = RONI (NOAA relative ONI, table provided) over the growing season SON(Y-1) to FMA(Y) of crop year Y/Y+1; "
                    "change = production Y/Y+1 vs Y-1/Y (1000 60-kg bags). Weather: " + wlab + ", annual, balance sheet.")
        # summary
        hdr = ["ENSO class", "Index range", "Occurrences", f"Avg {sp} change %", "Min %", "Max %", "Rain dev. (mm)", "Temp dev. (°C)", "Crop years"]
        wr = "ES" if sp == "Robusta" else "MG"
        data = [[r.enso_class, r.index_range, int(r.n), r[f"{sp}_avg_change_pct"], r[f"{sp}_min_pct"], r[f"{sp}_max_pct"],
                 r[f"{wr}_rain_dev_mm"], r[f"{wr}_temp_dev_c"], r.crop_years] for _, r in summ.iterrows()]
        end = write(ws, 4, hdr, data, [16, 12, 12, 16, 9, 9, 14, 14, 60])
        # chart: average change per class
        ch = BarChart(); ch.type = "col"; ch.title = f"{sp}: average production change by ENSO class (%)"
        ch.y_axis.title = "% vs previous crop year"; ch.x_axis.title = None; ch.legend = None; ch.height, ch.width = 8, 16
        ch.add_data(Reference(ws, min_col=4, min_row=4, max_row=end), titles_from_data=True)
        ch.set_categories(Reference(ws, min_col=1, min_row=5, max_row=end))
        ch.dataLabels = DataLabelList(); ch.dataLabels.showVal = True
        ws.add_chart(ch, f"A{end + 3}")
        # detail
        r0 = end + 21
        ws.cell(row=r0 - 1, column=1, value="Year by year").font = Font(bold=True)
        hdr2 = ["Crop year", "Status", "Index (RONI)", "ENSO class", f"{sp} previous", f"{sp} production", "Change %", f"Rain {wr} (mm)", f"Temp {wr} (°C)"]
        data2 = [[r.crop_year, r.status, r["index"], r.enso_class, r[f"{sp}_prev"], r[f"{sp}_prod"], r[f"{sp}_change_pct"],
                  r[wcols[0]], r[wcols[1]]] for _, r in df.iterrows()]
        end2 = write(ws, r0, hdr2, data2)
        ch2 = BarChart(); ch2.type = "col"; ch2.title = f"{sp}: change vs previous crop year (%)"; ch2.legend = None; ch2.height, ch2.width = 8, 22
        ch2.add_data(Reference(ws, min_col=7, min_row=r0, max_row=end2), titles_from_data=True)
        ch2.set_categories(Reference(ws, min_col=1, min_row=r0 + 1, max_row=end2))
        ws.add_chart(ch2, f"K{r0}")
    ws = wb.create_sheet("Index")
    ws["A1"] = "NOAA relative ONI (RONI) table as provided; season index = extreme of SON(Y-1)..FMA(Y)"; ws["A1"].font = Font(bold=True)
    write(ws, 3, ["year"] + COLS, [[y] + [None if pd.isna(v) else v for v in oni.loc[y].tolist()] for y in oni.index])
    ws = wb.create_sheet("Weather")
    ws["A1"] = "Annual rainfall (mm) and mean temperature (°C) by state, balance sheet (crop year). Sao Mateus / Linhares points: run build_region_weather.py (NASA POWER)."; ws["A1"].font = Font(bold=True)
    write(ws, 3, ["Crop year", "ENSO class", "Index", "ES rain", "ES temp", "MG rain", "MG temp"],
          [[r.crop_year, r.enso_class, r["index"], r.ES_rain_mm, r.ES_temp_c, r.MG_rain_mm, r.MG_temp_c] for _, r in df.iterrows()])
    ws.cell(row=len(df) + 5, column=1, value="Mean 1998/99-2025/26"); 
    for j, v in enumerate([base.rain_es, base.temp_es, base.rain_mg, base.temp_mg], 4):
        ws.cell(row=len(df) + 5, column=j, value=round(float(v), 1))
    path = os.path.join(OUT, "brazil_enso_client.xlsx")
    wb.save(path)
    pd.set_option("display.width", 250)
    print(df[["crop_year", "index", "enso_class", "Robusta_prev", "Robusta_prod", "Robusta_change_pct", "Arabica_change_pct", "ES_rain_mm", "ES_temp_c"]].round(1).to_string(index=False))
    print(); print(summ[["enso_class", "index_range", "n", "Robusta_avg_change_pct", "Arabica_avg_change_pct", "ES_rain_dev_mm", "ES_temp_dev_c", "crop_years"]].round(1).to_string(index=False))
    print("written", path)


if __name__ == "__main__":
    main()
