#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ENSO phase of each coffee crop year.

ONI_SEASONS: NOAA Climate Prediction Center list of El Nino / La Nina episodes
(Oceanic Nino Index, 3-month running mean of Nino-3.4 SST anomalies,
threshold +/-0.5 degC for 5 consecutive seasons).  Each entry is the
"ENSO season" running from mid-year Y to mid-year Y+1, keyed by Y, with the
approximate peak ONI and the CPC strength class.  Values are reproduced from
the CPC table as known when this was written (NOAA sites were not reachable
from the environment); re-check against
https://origin.cpc.ncep.noaa.gov/products/analysis_monitoring/ensostuff/ONI_v5.php
before publishing.  2026/27: El Nino conditions expected to persist to
about March 2027 (user input, September 2026).

CROP_SEASON says which ENSO season drives crop year Y/Y+1 of each origin:
  "prev"  -> season (Y-1)/Y  : the crop harvested in calendar year Y grew during
             the (Y-1)/Y event peak (Brazil, Peru: harvest Apr-Sep; Indonesia:
             Apr-Sep; Vietnam: dry season Jan-Apr of Y and wet season of Y
             feed the Nov Y - Jan Y+1 harvest).
  "same"  -> season Y/Y+1    : flowering/growth in Y and harvest Oct Y - Mar Y+1
             happen while the Y/Y+1 event develops and peaks (Colombia,
             Honduras, Ethiopia, Uganda).
"""
ONI_SEASONS = {
    # year: (peak ONI, phase, strength)
    1994: (1.1, "El Nino", "moderate"),
    1995: (-1.0, "La Nina", "moderate"),
    1996: (-0.5, "neutral", ""),
    1997: (2.4, "El Nino", "very strong"),
    1998: (-1.6, "La Nina", "strong"),
    1999: (-1.7, "La Nina", "strong"),
    2000: (-0.7, "La Nina", "weak"),
    2001: (-0.3, "neutral", ""),
    2002: (1.3, "El Nino", "moderate"),
    2003: (0.4, "neutral", ""),
    2004: (0.7, "El Nino", "weak"),
    2005: (-0.9, "La Nina", "weak"),
    2006: (0.9, "El Nino", "weak"),
    2007: (-1.6, "La Nina", "strong"),
    2008: (-0.8, "La Nina", "weak"),
    2009: (1.6, "El Nino", "moderate"),
    2010: (-1.6, "La Nina", "strong"),
    2011: (-1.1, "La Nina", "moderate"),
    2012: (-0.2, "neutral", ""),
    2013: (-0.4, "neutral", ""),
    2014: (0.7, "El Nino", "weak"),
    2015: (2.6, "El Nino", "very strong"),
    2016: (-0.7, "La Nina", "weak"),
    2017: (-1.0, "La Nina", "weak"),
    2018: (0.9, "El Nino", "weak"),
    2019: (0.5, "neutral", ""),
    2020: (-1.3, "La Nina", "moderate"),
    2021: (-1.0, "La Nina", "moderate"),
    2022: (-1.0, "La Nina", "weak"),
    2023: (2.0, "El Nino", "strong"),
    2024: (-0.6, "La Nina", "weak"),
    2025: (-0.6, "La Nina", "weak"),
    2026: (1.0, "El Nino", "expected (to Mar 2027)"),
}

# Optional official table: timeseries/data/oni.csv with columns
#   year, DJF, JFM, FMA, MAM, AMJ, MJJ, JJA, JAS, ASO, SON, OND, NDJ
# (copy of the CPC ONI or RONI table).  When present it replaces ONI_SEASONS:
# season Y = JJA(Y) .. MJJ(Y+1), phase = El Nino / La Nina when 5 consecutive
# overlapping seasons are >= +0.5 / <= -0.5, peak = extreme value of the season.
import os as _os, csv as _csv
_ONI_FILE = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "data", "oni.csv")
_COLS = ["DJF", "JFM", "FMA", "MAM", "AMJ", "MJJ", "JJA", "JAS", "ASO", "SON", "OND", "NDJ"]


def _load_oni_table(path):
    rows = {}
    with open(path, newline="", encoding="utf-8") as f:
        for r in _csv.DictReader(f):
            try:
                rows[int(r["year"])] = [float(r[c]) if r.get(c, "").strip() not in ("", "NA") else None for c in _COLS]
            except (KeyError, ValueError):
                continue
    seq = []                                                   # chronological list of (year, season, value)
    for y in sorted(rows):
        for i, c in enumerate(_COLS):
            seq.append((y, c, rows[y][i]))
    vals = [v for _, _, v in seq]
    flag = [None] * len(seq)                                   # episode flags by the 5-consecutive rule
    for sign, name in ((1, "El Nino"), (-1, "La Nina")):
        run = 0
        for i, v in enumerate(vals):
            run = run + 1 if (v is not None and sign * v >= 0.5) else 0
            if run >= 5:
                for k in range(i - run + 1, i + 1):
                    flag[k] = name
    out = {}
    for y in sorted(rows):
        idx = [i for i, (yy, c, v) in enumerate(seq) if (yy == y and c in _COLS[6:]) or (yy == y + 1 and c in _COLS[:6])]
        if len(idx) < 6:
            continue
        v = [vals[i] for i in idx if vals[i] is not None]
        names = [flag[i] for i in idx if flag[i]]
        if not v:
            continue
        peak = max(v, key=abs)
        phase = max(set(names), key=names.count) if names else "neutral"
        a = abs(peak)
        strength = "" if phase == "neutral" else ("weak" if a < 1 else "moderate" if a < 1.5 else "strong" if a < 2 else "very strong")
        out[y] = (peak, phase, strength)
    return out


if _os.path.exists(_ONI_FILE):
    ONI_SEASONS.update(_load_oni_table(_ONI_FILE))
    ONI_SOURCE = f"official ONI/RONI table {_ONI_FILE}"
else:
    ONI_SOURCE = "NOAA CPC episode list reproduced from memory (peak ONI approximate); drop the CPC table in data/oni.csv to replace it"

CROP_SEASON = {
    "Brazil": "prev", "Peru": "prev", "Indonesia": "prev", "Vietnam": "prev",
    "Colombia": "same", "Colombia (Fedecafe)": "same", "Honduras": "same",
    "Ethiopia": "same", "Uganda": "same",
}


def enso_for_crop_year(country, year):
    """(season_year, peak ONI, phase, strength) driving crop year `year`/`year+1`."""
    s = year - 1 if CROP_SEASON.get(country, "same") == "prev" else year
    oni, phase, strength = ONI_SEASONS.get(s, (None, "unknown", ""))
    return s, oni, phase, strength


# Thresholds on the peak index: strong >= 1.6, ordinary 0.6-1.6, weak < 0.6.
# 2023/24 is kept as an ordinary El Nino on the user's assessment (ONI peak 2.0,
# but relative ONI (RONI) peak only about 1.3): NOT_STRONG lists such seasons.
STRONG, WEAK = 1.6, 0.6
NOT_STRONG = {2023}


def intensity_class(oni, phase, season=None):
    """Three levels per phase: fort (|peak| >= 1.6), ordinaire (0.6-1.6), faible (< 0.6)."""
    a = abs(oni)
    strong = a >= STRONG and season not in NOT_STRONG
    if phase == "El Nino":
        return "El Nino fort" if strong else ("El Nino faible" if a < WEAK else "El Nino ordinaire")
    if phase == "La Nina":
        return "La Nina forte" if strong else ("La Nina faible" if a < WEAK else "La Nina ordinaire")
    return "neutre"
