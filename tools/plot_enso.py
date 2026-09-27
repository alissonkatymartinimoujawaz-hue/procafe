#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Chart images in the style of the "Sul de Minas | Temperature and rainfall" slide:
one column per ENSO phase, one line per coffee season (Jul -> Jun), dotted line =
average of the phase. Same data as the Excel workbook (tools/build_enso_workbook.py).
    python tools/plot_enso.py [--region ...|all]  ->  exports/<Region>_ENSO_charts.png (+ one per variable)
Needs matplotlib.
"""
import argparse, os, sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_enso_workbook as wb  # noqa: E402

OUT = os.path.join(wb.ROOT, "exports")
NAVY = "#1f2a44"
COLORS = ["#1f77b4", "#ff7f0e", "#2ca02c", "#e377c2", "#7b3fa0", "#222222", "#17becf", "#bcbd22", "#8c564b"]
ROWS = [("tmean", "Mean temperature", "°C"), ("tmin", "Min temperature", "°C"),
        ("tmax", "Max temperature", "°C"), ("rain", "Monthly rainfall", "mm"),
        ("rh", "Relative humidity", "%"), ("soil", "Soil moisture 0–100 cm", "% vol.")]
PHASES = ["El Niño", "La Niña", "Neutral"]
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": "#bbbbbb",
                     "axes.titleweight": "bold", "axes.titlecolor": NAVY})


def plot_region():
    region, phases, oni, best, last_month, months, seasons, s_label = wb.prepare()
    name, prefix = wb.R["name"], wb.R["file"]
    town_names = ", ".join(t[1] for t in wb.towns(wb.RID))
    by_phase = {ph: [y for y in seasons if phases.get(y, (0, ""))[1].rstrip("*") == ph] for ph in PHASES}
    done = {ph: [y for y in ys if not phases[y][1].endswith("*")] for ph, ys in by_phase.items()}
    x = list(range(12))

    def ylim(var):
        vals = [v for m, v in best[var].items() if m in months]
        step = {"tmean": 2, "tmin": 2, "tmax": 2, "rain": 100, "rh": 10, "soil": 5}[var]
        return step * int(min(vals) // step), step * int(-(-max(vals) // step))

    def panel(ax, var, ph, unit, label, first_row):
        for k, y in enumerate(by_phase[ph]):
            vals = wb.season_values(best[var], y)
            current = phases[y][1].endswith("*")
            ax.plot(x, [float("nan") if v is None else v for v in vals],
                    color="#d62728" if current else COLORS[k % len(COLORS)],
                    lw=2.6 if current else 1.5, label=s_label[y] + (" (in progress)" if current else ""))
        avg = []
        for i in range(12):
            vs = [wb.season_values(best[var], y)[i] for y in done[ph]]
            vs = [v for v in vs if v is not None]
            avg.append(sum(vs) / len(vs) if vs else float("nan"))
        ax.plot(x, avg, color=NAVY, lw=2.4, ls=(0, (1, 1.6)), label=f"{ph} average")
        ax.set_xticks(x, wb.MONTHS)
        ax.set_ylim(*ylim(var))
        ax.grid(axis="y", color="#e6e6e6")
        ax.tick_params(length=0)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        ax.set_title(label, loc="left", fontsize=10)
        ax.text(1.0, 1.02, unit, transform=ax.transAxes, ha="right", va="bottom", color="#666666", fontsize=8)
        if first_row:
            ax.text(0.0, 1.22, f"{ph} ({len(done[ph])} seasons)", transform=ax.transAxes,
                    fontsize=13, fontweight="bold", color=NAVY)

    rain_src = "CHIRPS v3" if wb.BEST["rain"] == "CHIRPS" else wb.BEST["rain"]
    adjusted = " and ".join(n for v, n in (("tmin", "min"), ("tmax", "max")) if wb.BEST[v] == wb.OMC) + " temperatures"
    note = ("Seasons Jul–Jun. ENSO phase: NOAA ONI (Dec–Feb) ≥ +0.5 El Niño, ≤ −0.5 La Niña. Region = average of "
            f"{town_names}.\nSources (closest to INMET stations): "
            f"rainfall {rain_src}; temperatures, humidity, soil moisture Open-Meteo ERA5-Land (0.1°, altitude-corrected; "
            f"{adjusted} adjusted to INMET stations). Data through {last_month}. 2026/27 = season in progress, "
            f"El Niño developing (provisional).")

    # --- full dashboard
    fig, axes = plt.subplots(len(ROWS), 3, figsize=(17, 4.0 * len(ROWS) + 2.2))
    for i, (var, label, unit) in enumerate(ROWS):
        for j, ph in enumerate(PHASES):
            panel(axes[i][j], var, ph, unit, label, i == 0)
    for j, ph in enumerate(PHASES):
        h, l = axes[-1][j].get_legend_handles_labels()
        axes[-1][j].legend(h, l, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=3, frameon=False, fontsize=9)
    fig.suptitle(f"{name} | Temperature, rainfall, humidity and soil moisture by ENSO phase",
                 x=0.01, ha="left", fontsize=17, fontweight="bold", color=NAVY)
    fig.text(0.01, 0.005, note, fontsize=8.5, color="#444444", va="bottom")
    fig.tight_layout(rect=(0, 0.035, 1, 0.975), h_pad=3.2)
    os.makedirs(OUT, exist_ok=True)
    fig.savefig(os.path.join(OUT, f"{prefix}_ENSO_charts.png"), dpi=110)
    plt.close(fig)

    # --- one image per variable (readable on a phone)
    for var, label, unit in ROWS:
        fig, axes = plt.subplots(1, 3, figsize=(17, 5.6))
        for j, ph in enumerate(PHASES):
            panel(axes[j], var, ph, unit, label, True)
            h, l = axes[j].get_legend_handles_labels()
            axes[j].legend(h, l, loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=3, frameon=False, fontsize=9)
        fig.suptitle(f"{name} | {label} by ENSO phase", x=0.01, ha="left", fontsize=15,
                     fontweight="bold", color=NAVY)
        fig.tight_layout(rect=(0, 0, 1, 0.93))
        fig.savefig(os.path.join(OUT, f"{prefix}_ENSO_{var}.png"), dpi=110)
        plt.close(fig)
    print("charts written to", OUT)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--region", default="all", choices=["all"] + list(wb.REGIONS))
    a = ap.parse_args().region
    for rid in (list(wb.REGIONS) if a == "all" else [a]):
        if not wb.ready(rid):
            print(f"{rid}: data not complete yet — skipped")
            continue
        wb.set_region(rid)
        plot_region()


if __name__ == "__main__":
    main()
