#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Figures for the per-origin Word reports (crop calendar, causal chain, history, ENSO effect)."""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

C_BLUE, C_ORANGE, C_AQUA, C_YELLOW, C_MAG, C_GREEN, C_VIOLET, C_RED = \
    "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"
C_TEXT, C_MUTED, C_GRID, C_SURF = "#0b0b0b", "#52514e", "#e6e5e1", "#fcfcfb"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": C_GRID, "axes.labelcolor": C_MUTED, "xtick.color": C_MUTED,
                     "ytick.color": C_MUTED, "axes.grid": True, "grid.color": C_GRID, "grid.linewidth": 0.6,
                     "axes.spines.top": False, "axes.spines.right": False, "figure.facecolor": C_SURF,
                     "axes.facecolor": C_SURF, "legend.frameon": False, "axes.titlecolor": C_TEXT})
MONTHS = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]
PHASE_COLORS = {"floraison": C_MAG, "développement du fruit": C_AQUA, "récolte": C_ORANGE, "saison sèche": C_YELLOW,
                "saison des pluies": C_BLUE, "risque gel": C_VIOLET, "irrigation": C_BLUE, "séchage": C_YELLOW}


def crop_calendar(title, rows, path):
    """rows: list of (label, [month numbers 1..12], phase_kind)."""
    fig, ax = plt.subplots(figsize=(9, 0.42 * len(rows) + 1.2))
    for i, (label, months, kind) in enumerate(rows):
        y = len(rows) - 1 - i
        for m in months:
            ax.barh(y, 1, left=m - 1, height=0.62, color=PHASE_COLORS.get(kind, C_MUTED), alpha=0.85, lw=0)
        ax.text(-0.3, y, label, ha="right", va="center", fontsize=9, color=C_TEXT)
    ax.set_xlim(0, 12); ax.set_ylim(-0.6, len(rows) - 0.4)
    ax.set_xticks(np.arange(12) + 0.5); ax.set_xticklabels(MONTHS)
    ax.set_yticks([]); ax.grid(False)
    for m in range(1, 12):
        ax.axvline(m, color=C_GRID, lw=0.6)
    ax.set_title(title, loc="left", fontsize=11, fontweight="bold")
    for s in ("left", "bottom"):
        ax.spines[s].set_visible(False)
    fig.savefig(path, dpi=160, bbox_inches="tight"); plt.close(fig)


def causal_chain(title, weather_items, path):
    """Production = bearing area x yield, with the drivers of each."""
    fig, ax = plt.subplots(figsize=(10, 4.6)); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 4.6)

    def box(x, y, w, h, text, fc, fs=9, bold=False):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fc, ec=C_GRID, lw=1))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=C_TEXT,
                fontweight="bold" if bold else "normal", wrap=True)

    def arrow(x0, y0, x1, y1):
        ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=12, color=C_MUTED, lw=1.2))

    box(7.4, 3.5, 2.4, 0.8, "PRODUCTION\n(sacs de 60 kg)", "#fde9df", 10, True)
    box(4.0, 3.5, 2.4, 0.8, "SURFACE EN PRODUCTION\n(bearing area, ha)", "#e3eefb", 9, True)
    box(4.0, 1.9, 2.4, 0.8, "RENDEMENT\n(sacs / ha)", "#e3eefb", 9, True)
    ax.text(6.9, 3.9, "×", ha="center", va="center", fontsize=16, color=C_TEXT)
    arrow(6.4, 3.9, 7.4, 3.9); arrow(6.4, 2.3, 7.4, 3.6)
    box(0.2, 3.5, 3.2, 0.8, "Stock d'arbres : plantations − arrachages\nnon-bearing → bearing après 3-4 ans", "#f1f0ec", 8)
    arrow(3.4, 3.9, 4.0, 3.9)
    box(0.2, 2.35, 3.2, 0.75, "Âge des arbres, variétés, densité,\nrénovation, intrants (engrais, prix)", "#f1f0ec", 8)
    arrow(3.4, 2.7, 4.0, 2.4)
    box(0.2, 1.25, 3.2, 0.95, "Météo de la campagne :\n" + weather_items, "#f1f0ec", 8)
    arrow(3.4, 1.7, 4.0, 2.2)
    box(0.2, 0.15, 3.2, 0.95, "Cycle biennal (ON/OFF), maladies\n(roya), ENSO (El Niño / La Niña)\nvia pluie et température", "#f1f0ec", 8)
    arrow(3.4, 0.6, 4.0, 2.0)
    box(4.0, 0.3, 2.4, 0.8, "Rendement de l'année\n= tendance + choc météo", "#fff6e0", 8)
    arrow(5.2, 1.1, 5.2, 1.9)
    ax.set_title(title, loc="left", fontsize=11, fontweight="bold")
    fig.savefig(path, dpi=160, bbox_inches="tight"); plt.close(fig)


def history(country, data, path, enso_years=None, label=None):
    """3 panels: production (by species), area (total / bearing), yield; ENSO years shaded."""
    d = data[data.country == country]
    panels = [("production", "Production (1000 sacs de 60 kg)"), ("area", "Surface (1000 ha)"), ("yield", "Rendement")]
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.6))
    cols = [C_BLUE, C_ORANGE, C_AQUA, C_YELLOW]
    for ax, (var, ttl) in zip(axes, panels):
        g = d[d.variable == var]
        k = 0
        for s, sg in g.groupby("series", sort=False):
            if "BPS" in s or "Non-bearing" in s and var == "trees":
                continue
            sg = sg.sort_values("year")
            ax.plot(sg.year, sg.value, color=cols[k % 4], lw=1.8, marker="o", ms=3, label=s)
            k += 1
        if enso_years is not None:
            for yr, ph in enso_years.items():
                if ph == "El Nino":
                    ax.axvspan(yr - 0.5, yr + 0.5, color=C_RED, alpha=0.07, lw=0)
                elif ph == "La Nina":
                    ax.axvspan(yr - 0.5, yr + 0.5, color=C_BLUE, alpha=0.07, lw=0)
        ax.set_title(ttl, loc="left", fontsize=10)
        if k:
            ax.legend(fontsize=7, loc="upper left")
    axes[0].text(0.0, -0.22, "Fond rouge = campagne El Niño, bleu = La Niña (phase ENSO qui pilote la campagne)",
                 transform=axes[0].transAxes, fontsize=7.5, color=C_MUTED)
    fig.suptitle(f"{label or country} : historique de la balance sheet", x=0.01, ha="left", fontsize=12, fontweight="bold")
    fig.tight_layout(); fig.savefig(path, dpi=150, bbox_inches="tight"); plt.close(fig)


def enso_bars(country, eff, series_list, path, label=None):
    """Mean anomaly (% vs neighbouring years) by ENSO phase, one group per series."""
    phases = ["El Nino fort (ONI >= 2)", "El Nino modere (1-2)", "El Nino faible (< 1)", "neutral",
              "La Nina faible (> -1)", "La Nina moderee (-1.5 a -1)", "La Nina forte (<= -1.5)"]
    labels = ["El Niño fort\n(ONI ≥ 2)", "El Niño modéré\n(1 à 2)", "El Niño faible\n(< 1)", "neutre",
              "La Niña faible\n(> −1)", "La Niña modérée\n(−1,5 à −1)", "La Niña forte\n(≤ −1,5)"]
    colors = [C_RED, "#ec7a79", "#f4b0af", C_MUTED, "#a9c8ee", "#6ea3e3", C_BLUE]
    e = eff[(eff.country == country) & (eff.series.isin(series_list))]
    fig, axes = plt.subplots(1, len(series_list), figsize=(6.2 * len(series_list), 4.0), squeeze=False)
    for ax, s in zip(axes[0], series_list):
        g = e[e.series == s].set_index("phase")
        vals = [g.loc[p, "mean_anomaly_pct"] if p in g.index else np.nan for p in phases]
        ns = [int(g.loc[p, "n"]) if p in g.index else 0 for p in phases]
        ax.bar(range(len(phases)), vals, color=colors, width=0.7)
        ax.axhline(0, color=C_MUTED, lw=0.8)
        for i, (v, n) in enumerate(zip(vals, ns)):
            if np.isfinite(v):
                ax.text(i, v + (0.4 if v >= 0 else -0.4), f"{v:+.1f} %\n(n={n})", ha="center",
                        va="bottom" if v >= 0 else "top", fontsize=7.5, color=C_TEXT)
        ax.set_xticks(range(len(phases))); ax.set_xticklabels(labels, fontsize=6.5, rotation=25, ha="right")
        ax.set_title(s, loc="left", fontsize=10)
        lim = max(3, np.nanmax(np.abs(vals)) * 1.6)
        ax.set_ylim(-lim, lim)
        ax.set_ylabel("écart à la moyenne des campagnes voisines (%)", fontsize=7.5)
    fig.suptitle(f"{label or country} : effet mesuré des phases ENSO dans la balance sheet", x=0.01, ha="left", fontsize=11, fontweight="bold")
    fig.tight_layout(); fig.savefig(path, dpi=150, bbox_inches="tight"); plt.close(fig)


def brazil_weather_phase(w, path, phases=None, colors=None, labels=None):
    """Rainfall / temperature deviation by ENSO phase (or intensity class) for the coffee states."""
    phases = phases or ["El Nino", "neutral", "La Nina"]; colors = colors or [C_RED, C_MUTED, C_BLUE]
    labels = labels or phases
    states = [("mg", "Minas Gerais"), ("es", "Espírito Santo"), ("sp", "São Paulo"), ("pr", "Paraná")]
    fig, axes = plt.subplots(1, 2, figsize=(12, 3.8))
    for ax, (kind, ttl, unit) in zip(axes, [("rain", "Pluie annuelle : écart à la moyenne 1998-2025", "mm"),
                                            ("temp", "Température moyenne : écart à la moyenne", "°C")]):
        x = np.arange(len(states)); wdt = 0.8 / len(phases)
        for k, (ph, col, lab) in enumerate(zip(phases, colors, labels)):
            if not (w.phase == ph).any():
                continue
            r = w[w.phase == ph].iloc[0]
            vals = [r[f"{kind}_{st}_dev"] for st, _ in states]
            xs = x + (k - (len(phases) - 1) / 2) * wdt
            ax.bar(xs, vals, wdt, color=col, label=f"{lab} (n={int(r.n)})")
            for xi, v in zip(xs, vals):
                ax.text(xi, v + (2 if kind == "rain" else 0.02) * (1 if v >= 0 else -1), f"{v:+.0f}" if kind == "rain" else f"{v:+.2f}",
                        ha="center", va="bottom" if v >= 0 else "top", fontsize=7)
        ax.axhline(0, color=C_MUTED, lw=0.8); ax.set_xticks(x); ax.set_xticklabels([n for _, n in states])
        ax.set_title(ttl, loc="left", fontsize=10); ax.set_ylabel(unit); ax.legend(fontsize=7.5)
    fig.suptitle("Brésil : météo des États caféiers pendant la campagne qui suit chaque épisode (balance sheet, 1998/99-2025/26)",
                 x=0.01, ha="left", fontsize=11, fontweight="bold")
    fig.tight_layout(); fig.savefig(path, dpi=150, bbox_inches="tight"); plt.close(fig)
