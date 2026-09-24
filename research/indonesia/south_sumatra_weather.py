#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
South Sumatra robusta weather vs ENSO / IOD vs USDA crop — standalone report.

Fetches (all public, verifiable):
  * NASA POWER daily PRECTOTCORR, T2M, T2M_MAX for the main robusta towns of
    southern Sumatra (1981 -> latest day available)
  * NOAA CPC ONI (ENSO)            https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt
  * NOAA PSL DMI (Indian Ocean Dipole, HadISST)
                                    https://psl.noaa.gov/gcos_wgsp/Timeseries/Data/dmi.had.long.data
  * USDA PSD coffee (Indonesia robusta production by marketing year Apr-Mar)
                                    https://apps.fas.usda.gov/psdonline/downloads/psd_coffee_csv.zip

and writes, next to this script:
  output/south_sumatra_weather.html   charts (inline SVG, opens in any browser)
  output/monthly_<city>.csv           monthly rain / temperature per town
  output/crop_vs_weather.csv          one row per USDA crop year with its weather windows

Run (stdlib only, no pip install needed):
  python research/indonesia/south_sumatra_weather.py
  python research/indonesia/south_sumatra_weather.py --city pagar_alam --window 8-11

Crop-year convention: USDA MY N/N+1 (Market_Year = N) is the harvest of
April N - March N+1. Southern Sumatra robusta is harvested roughly Apr-Aug of
year N (lowland first, highland June-August). The flowers of that crop open
in the second half of year N-1 (USDA FAS Jakarta cites May-Sept flowering in
2014 and Oct-Nov flowering in its 2017 and 2025 reports), and the cherries fill
from about December N-1 to March N. So the weather of year N-1 drives crop N.
"""
import argparse, csv, io, json, math, os, statistics, sys, time, urllib.request, zipfile
from collections import defaultdict
from datetime import date, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "output")

CITIES = [
    # id, name, province, lat, lon, note
    ("pagar_alam", "Pagar Alam", "South Sumatra", -4.0217, 103.2528, "highland robusta"),
    ("lahat",      "Lahat",      "South Sumatra", -3.7864, 103.5428, "highland/lowland edge"),
    ("muaradua",   "Muaradua",   "South Sumatra (OKU Selatan)", -4.5330, 104.0700, "robusta belt"),
    ("liwa",       "Liwa",       "Lampung (Lampung Barat)", -5.0333, 104.0667, "largest robusta district"),
    ("kepahiang",  "Kepahiang",  "Bengkulu", -3.6500, 102.5800, "highland robusta"),
]
SOUTH_SUMATRA = ["pagar_alam", "lahat", "muaradua"]

BASE_START, BASE_END = 1991, 2020          # WMO normal period
FILL = -999.0
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
ONI_URL = "https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt"
DMI_URL = "https://psl.noaa.gov/gcos_wgsp/Timeseries/Data/dmi.had.long.data"
PSD_URL = "https://apps.fas.usda.gov/psdonline/downloads/psd_coffee_csv.zip"
ONI_SEASONS = ["DJF", "JFM", "FMA", "MAM", "AMJ", "MJJ", "JJA", "JAS", "ASO", "SON", "OND", "NDJ"]


# ----------------------------------------------------------------- fetching
def _get(url, tries=4, timeout=180):
    last = None
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "procafe-research/1.0"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except Exception as e:  # noqa
            last = e
            time.sleep(3 * (k + 1))
    raise RuntimeError(f"fetch failed: {url}: {last!r}")


def fetch_power(lat, lon, end):
    url = ("https://power.larc.nasa.gov/api/temporal/daily/point"
           "?parameters=PRECTOTCORR,T2M,T2M_MAX&community=AG"
           f"&latitude={lat}&longitude={lon}&start=19810101&end={end}&format=JSON")
    return json.loads(_get(url))["properties"]["parameter"]


def fetch_oni():
    """{(year, month): anomaly} — month = centre month of the 3-month season."""
    out = {}
    for line in _get(ONI_URL).decode().splitlines():
        p = line.split()
        if len(p) == 4 and p[0] in ONI_SEASONS:
            out[(int(p[1]), ONI_SEASONS.index(p[0]) + 1)] = float(p[3])
    return out


def fetch_dmi():
    """{(year, month): DMI degC}. Missing values (-9999) skipped."""
    out = {}
    for line in _get(DMI_URL).decode().splitlines():
        p = line.split()
        if len(p) == 13 and p[0].isdigit():
            y = int(p[0])
            for m, v in enumerate(p[1:], start=1):
                v = float(v)
                if v > -99:
                    out[(y, m)] = v
    return out


def fetch_usda_robusta():
    """{market_year: robusta production, 1000 60-kg bags} for Indonesia."""
    z = zipfile.ZipFile(io.BytesIO(_get(PSD_URL)))
    name = [n for n in z.namelist() if n.endswith(".csv")][0]
    out = {}
    for r in csv.DictReader(io.TextIOWrapper(z.open(name), encoding="utf-8")):
        if r["Country_Name"] == "Indonesia" and r["Attribute_Description"] == "Robusta Production":
            out[int(r["Market_Year"])] = float(r["Value"])
    return out


# ----------------------------------------------------------------- processing
def monthly_from_daily(param):
    """Aggregate daily NASA POWER dicts -> {(y,m): {rain, t2m, tmax, days, complete}}."""
    rain = defaultdict(float); t = defaultdict(list); tx = defaultdict(list); nd = defaultdict(int)
    for k, v in param["PRECTOTCORR"].items():
        y, m = int(k[:4]), int(k[4:6])
        if v != FILL:
            rain[(y, m)] += v; nd[(y, m)] += 1
        tv, txv = param["T2M"].get(k, FILL), param["T2M_MAX"].get(k, FILL)
        if tv != FILL: t[(y, m)].append(tv)
        if txv != FILL: tx[(y, m)].append(txv)
    out = {}
    for ym in nd:
        y, m = ym
        dim = (date(y + (m == 12), m % 12 + 1, 1) - date(y, m, 1)).days
        out[ym] = {
            "rain": rain[ym],
            "t2m": statistics.mean(t[ym]) if t[ym] else None,
            "tmax": statistics.mean(tx[ym]) if tx[ym] else None,
            "days": nd[ym], "complete": nd[ym] >= dim - 1,
        }
    return out


def climatology(mon, key):
    clim = []
    for m in range(1, 13):
        vals = [mon[(y, m)][key] for y in range(BASE_START, BASE_END + 1)
                if (y, m) in mon and mon[(y, m)]["complete"] and mon[(y, m)][key] is not None]
        clim.append(statistics.mean(vals) if vals else None)
    return clim


def regional_mean(monthlies, ids):
    keys = set.intersection(*[set(monthlies[i]) for i in ids])
    out = {}
    for ym in keys:
        rows = [monthlies[i][ym] for i in ids]
        out[ym] = {
            "rain": statistics.mean(r["rain"] for r in rows),
            "t2m": statistics.mean(r["t2m"] for r in rows if r["t2m"] is not None),
            "tmax": statistics.mean(r["tmax"] for r in rows if r["tmax"] is not None),
            "days": min(r["days"] for r in rows),
            "complete": all(r["complete"] for r in rows),
        }
    return out


def window_rain_pct(mon, clim, year, m0, m1):
    """Rain in months m0..m1 of `year` (m1 may exceed 12 -> next year) as % of normal."""
    tot = norm = 0.0
    for mm in range(m0, m1 + 1):
        y, m = year + (mm - 1) // 12, (mm - 1) % 12 + 1
        r = mon.get((y, m))
        if r is None or not r["complete"]:
            return None
        tot += r["rain"]; norm += clim[m - 1]
    return 100.0 * tot / norm if norm else None


def phase_enso(oni, year, months=(7, 8, 9, 10, 11)):
    v = [oni[(year, m)] for m in months if (year, m) in oni]
    if len(v) < 3:
        return None, None
    a = statistics.mean(v)
    return a, ("El Niño" if a >= 0.5 else "La Niña" if a <= -0.5 else "Neutral")


def phase_iod(dmi, year, months=(9, 10, 11)):
    v = [dmi[(year, m)] for m in months if (year, m) in dmi]
    if len(v) < 2:
        return None, None
    a = statistics.mean(v)
    return a, ("Positive" if a >= 0.4 else "Negative" if a <= -0.4 else "Neutral")


def crop_anomaly(prod):
    """% deviation of each crop from the median of the surrounding 7 crops (itself excluded)."""
    years = sorted(prod); out = {}
    for y in years:
        nb = [prod[x] for x in years if x != y and abs(x - y) <= 3]
        if len(nb) >= 3:
            out[y] = 100.0 * (prod[y] / statistics.median(nb) - 1)
    return out


def pearson(xs, ys):
    n = len(xs)
    if n < 5:
        return None
    mx, my = statistics.mean(xs), statistics.mean(ys)
    sxy = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    sx = math.sqrt(sum((a - mx) ** 2 for a in xs)); sy = math.sqrt(sum((b - my) ** 2 for b in ys))
    return sxy / (sx * sy) if sx and sy else None


# ----------------------------------------------------------------- SVG charts
INK, MUTED, GRID = "#1d2320", "#6b716c", "#e3e5e1"
C_CLIM, C_A, C_B, C_C = "#b9c2bb", "#2a78d6", "#eb6834", "#1baf7a"
C_NINO, C_NINA = "#d0542a", "#2a78d6"


def _nice(lo, hi, n=5):
    if hi == lo:
        hi = lo + 1
    raw = (hi - lo) / n
    mag = 10 ** math.floor(math.log10(raw))
    step = min((s * mag for s in (1, 2, 2.5, 5, 10) if s * mag >= raw), default=raw)
    a = math.floor(lo / step) * step; b = math.ceil(hi / step) * step
    ticks, v = [], a
    while v <= b + step / 2:
        ticks.append(round(v, 6)); v += step
    return a, b, ticks


def svg_frame(w, h, body, title):
    return (f'<figure><figcaption>{title}</figcaption>'
            f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="{title}" '
            f'style="width:100%;max-width:{w}px;height:auto;font:12px system-ui,sans-serif">'
            f'{body}</svg></figure>')


def chart_months(series, title, unit, bars=None, bands=None, zero=False):
    """12-month chart: optional bar series (e.g. climatology) + line series.
    series: [(label, color, [12 values or None])]; bars: (label, color, [12]);
    bands: [(m0, m1, label, fill)] shaded month ranges (1-based, inclusive)."""
    W, H, L, R, T, B = 760, 330, 56, 150, 18, 40
    pw, ph = W - L - R, H - T - B
    vals = [v for _, _, s in series for v in s if v is not None]
    if bars:
        vals += [v for v in bars[2] if v is not None]
    lo = min(vals + ([0] if zero or bars else [])); hi = max(vals)
    a, b, ticks = _nice(lo, hi)
    x = lambda i: L + pw * (i + 0.5) / 12
    y = lambda v: T + ph * (1 - (v - a) / (b - a))
    s = []
    for m0, m1, lab, fill in bands or []:
        x0, x1 = L + pw * (m0 - 1) / 12, L + pw * m1 / 12
        s.append(f'<rect x="{x0:.1f}" y="{T}" width="{x1 - x0:.1f}" height="{ph}" fill="{fill}"/>'
                 f'<text x="{(x0 + x1) / 2:.1f}" y="{T + 12}" text-anchor="middle" fill="{MUTED}" font-size="11">{lab}</text>')
    for t in ticks:
        s.append(f'<line x1="{L}" x2="{L + pw}" y1="{y(t):.1f}" y2="{y(t):.1f}" stroke="{GRID}"/>'
                 f'<text x="{L - 6}" y="{y(t) + 4:.1f}" text-anchor="end" fill="{MUTED}">{t:g}</text>')
    s.append(f'<text x="12" y="{T + ph / 2}" transform="rotate(-90 12 {T + ph / 2})" text-anchor="middle" fill="{MUTED}">{unit}</text>')
    if bars:
        bw = pw / 12 * 0.62
        for i, v in enumerate(bars[2]):
            if v is None: continue
            y0, y1 = y(max(a, 0)), y(v)
            s.append(f'<rect x="{x(i) - bw / 2:.1f}" y="{min(y0, y1):.1f}" width="{bw:.1f}" height="{abs(y1 - y0):.1f}" fill="{bars[1]}" rx="3"><title>{bars[0]} {MONTHS[i]}: {v:.0f}</title></rect>')
    for lab, col, vs in series:
        pts = [(x(i), y(v)) for i, v in enumerate(vs) if v is not None]
        if len(pts) > 1:
            s.append(f'<polyline points="{" ".join(f"{p:.1f},{q:.1f}" for p, q in pts)}" fill="none" stroke="{col}" stroke-width="2"/>')
        for i, v in enumerate(vs):
            if v is not None:
                s.append(f'<circle cx="{x(i):.1f}" cy="{y(v):.1f}" r="3.5" fill="{col}"><title>{lab} {MONTHS[i]}: {v:.1f}</title></circle>')
    for i, mname in enumerate(MONTHS):
        s.append(f'<text x="{x(i):.1f}" y="{T + ph + 18}" text-anchor="middle" fill="{MUTED}">{mname}</text>')
    s.append(f'<line x1="{L}" x2="{L + pw}" y1="{y(max(a, 0)):.1f}" y2="{y(max(a, 0)):.1f}" stroke="#aab0ab"/>')
    leg = ([(bars[0], bars[1])] if bars else []) + [(l, c) for l, c, _ in series]
    for k, (lab, col) in enumerate(leg):
        yy = T + 10 + k * 20
        s.append(f'<rect x="{L + pw + 14}" y="{yy - 8}" width="12" height="10" rx="2" fill="{col}"/>'
                 f'<text x="{L + pw + 32}" y="{yy + 1}" fill="{INK}">{lab}</text>')
    return svg_frame(W, H, "".join(s), title)


def chart_diverging(groups, title, unit):
    """Monthly anomaly bars for 2-3 groups side by side. groups: [(label, color, [12])]."""
    W, H, L, R, T, B = 760, 320, 56, 150, 18, 40
    pw, ph = W - L - R, H - T - B
    vals = [v for _, _, s in groups for v in s if v is not None] + [0]
    a, b, ticks = _nice(min(vals), max(vals))
    y = lambda v: T + ph * (1 - (v - a) / (b - a))
    s = []
    for t in ticks:
        s.append(f'<line x1="{L}" x2="{L + pw}" y1="{y(t):.1f}" y2="{y(t):.1f}" stroke="{GRID}"/>'
                 f'<text x="{L - 6}" y="{y(t) + 4:.1f}" text-anchor="end" fill="{MUTED}">{t:g}</text>')
    s.append(f'<text x="12" y="{T + ph / 2}" transform="rotate(-90 12 {T + ph / 2})" text-anchor="middle" fill="{MUTED}">{unit}</text>')
    gw = pw / 12; bw = gw * 0.8 / len(groups)
    for g, (lab, col, vs) in enumerate(groups):
        for i, v in enumerate(vs):
            if v is None: continue
            x0 = L + gw * i + gw * 0.1 + g * bw
            y0, y1 = y(0), y(v)
            s.append(f'<rect x="{x0 + 1:.1f}" y="{min(y0, y1):.1f}" width="{bw - 2:.1f}" height="{abs(y1 - y0):.1f}" fill="{col}" rx="2"><title>{lab} {MONTHS[i]}: {v:+.0f}{unit[:1] if unit.startswith("%") else ""}</title></rect>')
    for i, mname in enumerate(MONTHS):
        s.append(f'<text x="{L + gw * (i + 0.5):.1f}" y="{T + ph + 18}" text-anchor="middle" fill="{MUTED}">{mname}</text>')
    s.append(f'<line x1="{L}" x2="{L + pw}" y1="{y(0):.1f}" y2="{y(0):.1f}" stroke="#8d938e"/>')
    for k, (lab, col, _) in enumerate(groups):
        yy = T + 10 + k * 20
        s.append(f'<rect x="{L + pw + 14}" y="{yy - 8}" width="12" height="10" rx="2" fill="{col}"/>'
                 f'<text x="{L + pw + 32}" y="{yy + 1}" fill="{INK}">{lab}</text>')
    return svg_frame(W, H, "".join(s), title)


def chart_scatter(points, title, xlab, ylab):
    """points: [(x, y, label, color)]"""
    W, H, L, R, T, B = 760, 380, 60, 30, 18, 46
    pw, ph = W - L - R, H - T - B
    xa, xb, xt = _nice(min(p[0] for p in points), max(p[0] for p in points))
    ya, yb, yt = _nice(min(p[1] for p in points + [(0, 0)]), max(p[1] for p in points + [(0, 0)]))
    X = lambda v: L + pw * (v - xa) / (xb - xa); Y = lambda v: T + ph * (1 - (v - ya) / (yb - ya))
    s = []
    for t in yt:
        s.append(f'<line x1="{L}" x2="{L + pw}" y1="{Y(t):.1f}" y2="{Y(t):.1f}" stroke="{GRID}"/>'
                 f'<text x="{L - 6}" y="{Y(t) + 4:.1f}" text-anchor="end" fill="{MUTED}">{t:g}</text>')
    for t in xt:
        s.append(f'<text x="{X(t):.1f}" y="{T + ph + 18}" text-anchor="middle" fill="{MUTED}">{t:g}</text>')
    if xa <= 100 <= xb:
        s.append(f'<line x1="{X(100):.1f}" x2="{X(100):.1f}" y1="{T}" y2="{T + ph}" stroke="#aab0ab" stroke-dasharray="4 3"/>')
    s.append(f'<line x1="{L}" x2="{L + pw}" y1="{Y(0):.1f}" y2="{Y(0):.1f}" stroke="#8d938e"/>')
    for xv, yv, lab, col in points:
        s.append(f'<circle cx="{X(xv):.1f}" cy="{Y(yv):.1f}" r="5" fill="{col}" stroke="#fff" stroke-width="1.5"><title>{lab}: rain {xv:.0f}% of normal, crop {yv:+.1f}%</title></circle>')
        if abs(yv) >= 8 or xv < 70 or xv > 135:
            s.append(f'<text x="{X(xv) + 7:.1f}" y="{Y(yv) + 4:.1f}" fill="{INK}" font-size="11">{lab}</text>')
    s.append(f'<text x="{L + pw / 2}" y="{H - 6}" text-anchor="middle" fill="{MUTED}">{xlab}</text>'
             f'<text x="14" y="{T + ph / 2}" transform="rotate(-90 14 {T + ph / 2})" text-anchor="middle" fill="{MUTED}">{ylab}</text>')
    return svg_frame(W, H, "".join(s), title)


def chart_corr_strip(labels, rs, title):
    W, H, L, T = 760, 150, 10, 30
    cw = (W - 2 * L) / len(labels)
    s = []
    for i, (lab, r) in enumerate(zip(labels, rs)):
        if r is None:
            col = "#eee"
        else:
            k = min(1, abs(r) / 0.5)
            base = (208, 84, 42) if r < 0 else (42, 120, 214)
            col = "#%02x%02x%02x" % tuple(int(255 - (255 - c) * k) for c in base)
        s.append(f'<rect x="{L + i * cw + 1:.1f}" y="{T}" width="{cw - 2:.1f}" height="54" rx="3" fill="{col}"><title>{lab}: r = {"n/a" if r is None else f"{r:+.2f}"}</title></rect>'
                 f'<text x="{L + (i + 0.5) * cw:.1f}" y="{T + 32}" text-anchor="middle" font-size="11" fill="{INK}">{"" if r is None else f"{r:+.2f}"}</text>'
                 f'<text x="{L + (i + 0.5) * cw:.1f}" y="{T + 74}" text-anchor="middle" font-size="10" fill="{MUTED}">{lab}</text>')
    s.append(f'<text x="{L}" y="{T - 10}" fill="{MUTED}" font-size="11">Orange = more rain that month goes with a SMALLER crop; blue = with a BIGGER crop. |r| above ~0.3 is worth a look (n ≈ 40 crops).</text>')
    return svg_frame(W, H, "".join(s), title)


# ----------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--city", default="south_sumatra",
                    help="city id for the crop analysis, or 'south_sumatra' (mean of Pagar Alam, Lahat, Muaradua)")
    ap.add_argument("--window", default="8-11",
                    help="flowering window in year N-1 for the scatter, months 'a-b' (default 8-11 = Aug-Nov)")
    args = ap.parse_args()
    w0, w1 = (int(v) for v in args.window.split("-"))
    os.makedirs(OUT_DIR, exist_ok=True)
    end = (date.today() - timedelta(days=5)).strftime("%Y%m%d")

    print("NASA POWER ...")
    monthlies = {}
    for cid, name, prov, lat, lon, _ in CITIES:
        monthlies[cid] = monthly_from_daily(fetch_power(lat, lon, end))
        print(f"  {name}: {len(monthlies[cid])} months")
    monthlies["south_sumatra"] = regional_mean(monthlies, SOUTH_SUMATRA)
    print("ONI / DMI / USDA ...")
    oni, dmi, prod = fetch_oni(), fetch_dmi(), fetch_usda_robusta()

    # monthly CSVs
    for cid, mon in monthlies.items():
        with open(os.path.join(OUT_DIR, f"monthly_{cid}.csv"), "w", newline="") as f:
            wr = csv.writer(f); wr.writerow(["year", "month", "rain_mm", "t2m_c", "tmax_c", "days", "complete"])
            for (y, m) in sorted(mon):
                r = mon[(y, m)]
                wr.writerow([y, m, round(r["rain"], 1), None if r["t2m"] is None else round(r["t2m"], 2),
                             None if r["tmax"] is None else round(r["tmax"], 2), r["days"], r["complete"]])

    sel = monthlies[args.city]
    clim_r, clim_t, clim_tx = climatology(sel, "rain"), climatology(sel, "t2m"), climatology(sel, "tmax")
    last_year = max(y for y, _ in sel)
    years_all = sorted({y for y, _ in sel})
    enso = {y: phase_enso(oni, y) for y in years_all}
    iod = {y: phase_iod(dmi, y) for y in years_all}

    # composites: monthly rain anomaly (% of normal) by phase of the SAME year (Jul-Nov ONI / Sep-Nov DMI)
    def composite(phases, wanted):
        out = []
        for m in range(1, 13):
            v = [100 * sel[(y, m)]["rain"] / clim_r[m - 1] - 100 for y in years_all
                 if phases[y][1] == wanted and (y, m) in sel and sel[(y, m)]["complete"]]
            out.append(statistics.mean(v) if v else None)
        return out

    # year-lines for the monthly charts: latest year + the most recent El Niño and La Niña years
    def latest(phases, wanted):
        c = [y for y in years_all if y < last_year and phases[y][1] == wanted]
        return c[-1] if c else None
    show = [y for y in dict.fromkeys([latest(enso, "El Niño"), latest(enso, "La Niña"), last_year - 1, last_year]) if y]
    cols = [C_NINO, C_NINA, C_C, "#111"]

    def yline(y, key):
        return [sel[(y, m)][key] if (y, m) in sel and (sel[(y, m)]["complete"] or y == last_year) else None
                for m in range(1, 13)]

    def ylab(y):
        e, i = enso[y][1], iod[y][1]
        tag = ", ".join(t for t in [e if e and e != "Neutral" else None,
                                    {"Positive": "IOD+", "Negative": "IOD−"}.get(i)] if t)
        return f"{y}{' (' + tag + ')' if tag else ''}{' – partial' if y == last_year else ''}"

    bands = [(6, 9, "dry season", "#f3efe4"), (10, 11, "flowering", "#e6f0e8")]
    city_name = "South Sumatra (mean of Pagar Alam, Lahat, Muaradua)" if args.city == "south_sumatra" else \
        next(c[1] for c in CITIES if c[0] == args.city)

    charts = []
    charts.append(chart_months([(ylab(y), cols[k % len(cols)], yline(y, "rain")) for k, y in enumerate(show)],
                               f"{city_name} — monthly rainfall vs {BASE_START}–{BASE_END} normal", "mm / month",
                               bars=(f"Normal {BASE_START}–{BASE_END}", C_CLIM, clim_r), bands=bands))
    charts.append(chart_months([(f"Normal {BASE_START}–{BASE_END}", "#8d938e", clim_tx)] +
                               [(ylab(y), cols[k % len(cols)], yline(y, "tmax")) for k, y in enumerate(show)],
                               f"{city_name} — mean daily maximum temperature", "°C", bands=bands))
    charts.append(chart_diverging([("El Niño years", C_NINO, composite(enso, "El Niño")),
                                   ("La Niña years", C_NINA, composite(enso, "La Niña"))],
                                  f"What ENSO does to {city_name} rainfall (mean anomaly, years classified on Jul–Nov ONI, 1981–{last_year - 1})",
                                  "% vs normal"))
    charts.append(chart_diverging([("Positive IOD", "#b8860b", composite(iod, "Positive")),
                                   ("Negative IOD", "#5b6bd6", composite(iod, "Negative"))],
                                  f"What the Indian Ocean Dipole does to {city_name} rainfall (years classified on Sep–Nov DMI)",
                                  "% vs normal"))

    # crop link
    anom = crop_anomaly(prod)
    labels, rs = [], []
    for k in range(18):                       # Jan N-1 .. Jun N
        mm = k + 1
        xs, ys = [], []
        for N in sorted(anom):
            y_, m_ = N - 1 + (mm - 1) // 12, (mm - 1) % 12 + 1
            r = sel.get((y_, m_))
            if r and r["complete"]:
                xs.append(100 * r["rain"] / clim_r[m_ - 1]); ys.append(anom[N])
        labels.append(f"{MONTHS[(mm - 1) % 12]} {'N-1' if mm <= 12 else 'N'}")
        rs.append(pearson(xs, ys))
    charts.append(chart_corr_strip(labels, rs, f"Which months' rain moves the USDA robusta crop? Correlation of monthly rain (% of normal, {city_name}) with crop N vs its neighbours"))

    rows, pts = [], []
    for N in sorted(prod):
        wp = window_rain_pct(sel, clim_r, N - 1, w0, w1)
        dry = window_rain_pct(sel, clim_r, N - 1, 6, 9)
        dev = window_rain_pct(sel, clim_r, N - 1, 12, 15)
        e, i = enso.get(N - 1, (None, None)), iod.get(N - 1, (None, None))
        rows.append([N, f"{N}/{str(N + 1)[2:]}", prod[N], None if N not in anom else round(anom[N], 1),
                     None if dry is None else round(dry), None if wp is None else round(wp), None if dev is None else round(dev),
                     None if e[0] is None else round(e[0], 2), e[1], None if i[0] is None else round(i[0], 2), i[1]])
        if wp is not None and N in anom:
            col = C_NINO if e[1] == "El Niño" else C_NINA if e[1] == "La Niña" else "#8d938e"
            pts.append((wp, anom[N], f"{N}/{str(N + 1)[2:]}", col))
    with open(os.path.join(OUT_DIR, "crop_vs_weather.csv"), "w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["market_year", "crop", "usda_robusta_1000bags", "crop_vs_neighbours_pct",
                     "rain_jun_sep_N-1_pct_normal", f"rain_{MONTHS[w0 - 1]}-{MONTHS[w1 - 1]}_N-1_pct_normal",
                     "rain_dec_N-1_mar_N_pct_normal", "oni_jul_nov_N-1", "enso_N-1", "dmi_sep_nov_N-1", "iod_N-1"])
        wr.writerows(rows)
    if pts:
        r = pearson([p[0] for p in pts], [p[1] for p in pts])
        charts.append(chart_scatter(pts, f"Flowering-window rain ({MONTHS[w0 - 1]}–{MONTHS[w1 - 1]} of year N-1) vs USDA robusta crop N — r = {r:+.2f}. Red = El Niño year, blue = La Niña year",
                                    f"Rain {MONTHS[w0 - 1]}–{MONTHS[w1 - 1]} N-1, % of normal", "Crop vs neighbours, %"))

    # current-season box
    fmt = lambda v: "–" if v is None else f"{v:+.2f}"
    cur = [(m, sel[(last_year, m)]) for m in range(1, 13) if (last_year, m) in sel]
    cur_txt = "".join(f"<tr><td>{MONTHS[m - 1]} {last_year}{'' if r['complete'] else ' (partial)'}</td>"
                      f"<td>{r['rain']:.0f} mm</td><td>{100 * r['rain'] / clim_r[m - 1]:.0f}%</td>"
                      f"<td>{fmt(oni.get((last_year, m)))}</td><td>{fmt(dmi.get((last_year, m)))}</td></tr>"
                      for m, r in cur)

    html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>South Sumatra Robusta Weather</title>
<style>
body{{font:15px/1.5 system-ui,sans-serif;color:{INK};background:#fbfbf9;max-width:960px;margin:0 auto;padding:24px 16px}}
h1{{font-size:24px;margin:0 0 4px}} h2{{font-size:18px;margin:32px 0 8px}}
figure{{margin:18px 0;background:#fff;border:1px solid #e6e8e4;border-radius:8px;padding:12px}}
figcaption{{font-weight:600;margin-bottom:6px}} table{{border-collapse:collapse;font-variant-numeric:tabular-nums}}
td,th{{border-bottom:1px solid #e6e8e4;padding:4px 10px;text-align:right}} td:first-child,th:first-child{{text-align:left}}
.muted{{color:{MUTED};font-size:13px}}
</style></head><body>
<h1>South Sumatra robusta — weather, ENSO/IOD and the USDA crop</h1>
<p class="muted">Generated {date.today()} · NASA POWER daily (PRECTOTCORR, T2M, T2M_MAX) to {end} · NOAA CPC ONI · NOAA PSL DMI (HadISST) · USDA PSD robusta production (Market_Year N = Apr N–Mar N+1).
Normal = {BASE_START}–{BASE_END}. ENSO phase of a year = mean ONI Jul–Nov (±0.5); IOD phase = mean DMI Sep–Nov (±0.4 °C).
Crop anomaly = USDA crop N vs the median of the 6 surrounding crops.</p>
{''.join(charts)}
<h2>{last_year} so far ({city_name})</h2>
<table><tr><th>Month</th><th>Rain</th><th>% of normal</th><th>ONI</th><th>DMI</th></tr>{cur_txt}</table>
<p class="muted">Tables per town: output/monthly_*.csv · one row per crop: output/crop_vs_weather.csv</p>
</body></html>"""
    out = os.path.join(OUT_DIR, "south_sumatra_weather.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote", out)


if __name__ == "__main__":
    sys.exit(main())
