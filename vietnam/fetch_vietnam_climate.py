#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Monthly climate of the coffee areas of Đắk Lắk and Lâm Đồng (Vietnam) since
2009, from NASA POWER and Open-Meteo side by side, in one Excel workbook.

Towns (edit POINTS below) — Đắk Lắk: Buôn Ma Thuột, Buôn Hồ;
Lâm Đồng: Bảo Lộc, Di Linh (Robusta) and Đà Lạt (Arabica).

Monthly variables:
  rain            total rainfall (mm)          NASA PRECTOTCORR    Open-Meteo precipitation_sum
  tmax, tmin      mean daily max / min (°C)    NASA T2M_MAX/MIN    Open-Meteo temperature_2m_max/min
  soil surface    NASA GWETTOP  (0-5 cm)       Open-Meteo soil moisture 0-7 cm
  soil root zone  NASA GWETROOT (0-100 cm)     Open-Meteo 0-7, 7-28, 28-100 cm, weighted by thickness
  soil profile    NASA GWETPROF (to bedrock)   Open-Meteo 0-7 ... 100-255 cm, weighted by thickness
NASA soil "wetness" is a 0-1 index (1 = saturated) while Open-Meteo gives a
water volume (m³/m³): compare how they move, not their values.

Writes to vietnam/output/:
  vietnam_coffee_climate.xlsx  per province and source: years x months, with the
                               year total/mean and the average year as Excel
                               formulas; a comparison sheet per province; Data sheet
  vietnam_monthly.csv          monthly values per town and source
  vietnam_daily.csv            the daily values they are computed from

API answers are cached in vietnam/cache/, so a second run only downloads what
is missing (handy with Open-Meteo's daily quota); --refresh ignores the cache.
Standard library only, nothing to install.

Run:
  python vietnam/fetch_vietnam_climate.py
  python vietnam/fetch_vietnam_climate.py --source nasa        # or openmeteo
"""
import argparse
import csv
import hashlib
import http.client
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from calendar import monthrange
from collections import defaultdict
from datetime import date, timedelta
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "output")
CACHE_DIR = os.path.join(HERE, "cache")
XLSX_NAME = "vietnam_coffee_climate.xlsx"

START_YEAR = 2009
LATENCY_DAYS = 7          # both APIs publish with a few days' delay

# Coffee towns: approximate town centres, in the provinces as they were before
# the July 2025 mergers.
POINTS = [
    # id               town             province    coffee     lat       lon
    ("buon_ma_thuot", "Buôn Ma Thuột", "Đắk Lắk",  "Robusta", 12.6667, 108.0500),
    ("buon_ho",       "Buôn Hồ",       "Đắk Lắk",  "Robusta", 12.9167, 108.2667),
    ("bao_loc",       "Bảo Lộc",       "Lâm Đồng", "Robusta", 11.5480, 107.8077),
    ("di_linh",       "Di Linh",       "Lâm Đồng", "Robusta", 11.5833, 108.0667),
    ("da_lat",        "Đà Lạt",        "Lâm Đồng", "Arabica", 11.9404, 108.4583),
]
PROVINCES = [("Đắk Lắk", "Dak Lak"), ("Lâm Đồng", "Lam Dong")]   # name, ASCII name for sheet tabs

NASA, OM = "NASA POWER", "Open-Meteo"
NASA_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
OM_URL = "https://archive-api.open-meteo.com/v1/archive"
OM_PAUSE = 65     # s between Open-Meteo downloads: each one uses most of the per-minute quota
RETRY_WAIT = 65   # s to wait after a per-minute rate-limit answer

NASA_PARAMS = {"rain": "PRECTOTCORR", "tmax": "T2M_MAX", "tmin": "T2M_MIN",
               "soil_surface": "GWETTOP", "soil_root": "GWETROOT", "soil_profile": "GWETPROF"}
OM_DAILY = {"rain": "precipitation_sum", "tmax": "temperature_2m_max", "tmin": "temperature_2m_min"}
OM_LAYERS = [  # key, Open-Meteo hourly variable, layer thickness (cm)
    ("sm_0_7", "soil_moisture_0_to_7cm", 7),
    ("sm_7_28", "soil_moisture_7_to_28cm", 21),
    ("sm_28_100", "soil_moisture_28_to_100cm", 72),
    ("sm_100_255", "soil_moisture_100_to_255cm", 155),
]

# unit and fmt: (NASA POWER, Open-Meteo)
VARIABLES = [
    dict(key="rain", title="Rainfall", agg="sum", unit=("mm", "mm"), fmt=("0", "0")),
    dict(key="tmax", title="Maximum temperature, mean of daily max", agg="mean",
         unit=("°C", "°C"), fmt=("0.0", "0.0")),
    dict(key="tmin", title="Minimum temperature, mean of daily min", agg="mean",
         unit=("°C", "°C"), fmt=("0.0", "0.0")),
    dict(key="soil_surface", title="Soil moisture, surface", agg="mean",
         unit=("GWETTOP, wetness 0-1, 0-5 cm", "m³/m³, 0-7 cm"), fmt=("0.00", "0.000")),
    dict(key="soil_root", title="Soil moisture, root zone", agg="mean",
         unit=("GWETROOT, wetness 0-1, 0-100 cm", "m³/m³, 0-100 cm"), fmt=("0.00", "0.000")),
    dict(key="soil_profile", title="Soil moisture, profile", agg="mean",
         unit=("GWETPROF, wetness 0-1, surface to bedrock", "m³/m³, 0-255 cm"), fmt=("0.00", "0.000")),
]
MAIN_KEYS = [v["key"] for v in VARIABLES]
LAYER_KEYS = [k for k, _, _ in OM_LAYERS]
DIGITS = {"rain": 1, "tmax": 2, "tmin": 2}       # stored precision; soil moisture: 4
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
CSV_FIELDS = [("rain", "rain_mm"), ("tmax", "tmax_c"), ("tmin", "tmin_c"),
              ("soil_surface", "soil_surface"), ("soil_root", "soil_root_zone"),
              ("soil_profile", "soil_profile"), ("sm_0_7", "om_soil_0_7cm"),
              ("sm_7_28", "om_soil_7_28cm"), ("sm_28_100", "om_soil_28_100cm"),
              ("sm_100_255", "om_soil_100_255cm")]


# ---------------------------------------------------------------- download --

class QuotaError(Exception):
    """The API refuses more requests for now (daily or hourly quota)."""


_last_download = {}


def _reason(body):
    try:
        data = json.loads(body)
    except ValueError:
        return " ".join(body.split())[:300]
    if isinstance(data, dict):
        for k in ("reason", "messages", "message", "detail", "errors"):
            if data.get(k):
                return str(data[k])[:300]
    return str(data)[:300]


def get_json(url, params, refresh=False, pause=0.0):
    full = url + "?" + urllib.parse.urlencode(params)
    cache = os.path.join(CACHE_DIR, hashlib.sha1(full.encode("utf-8")).hexdigest()[:16] + ".json")
    if os.path.exists(cache) and not refresh:
        with open(cache, encoding="utf-8") as f:
            return json.load(f)
    wait = _last_download.get(url, -1e9) + pause - time.monotonic()
    if wait > 0:
        print(f"    waiting {wait:.0f} s (per-minute quota) ...", flush=True)
        time.sleep(wait)
    last = None
    for attempt in range(1, 5):
        try:
            req = urllib.request.Request(full, headers={"User-Agent": "procafe-climate/1.0"})
            with urllib.request.urlopen(req, timeout=300) as r:
                data = json.loads(r.read().decode("utf-8"))
            break
        except urllib.error.HTTPError as e:
            reason = _reason(e.read().decode("utf-8", "replace"))
            if e.code == 429 and ("daily" in reason.lower() or "hourly" in reason.lower()):
                raise QuotaError(reason)
            if e.code != 429 and e.code < 500:
                raise RuntimeError(f"HTTP {e.code}: {reason}")
            last = f"HTTP {e.code}: {reason}"
            if e.code == 429:
                print(f"    rate limited, waiting {RETRY_WAIT} s ...", flush=True)
                time.sleep(RETRY_WAIT)
                continue
        except (OSError, ValueError, http.client.HTTPException) as e:   # network, timeout, bad JSON
            last = repr(e)
        time.sleep(5 * attempt)
    else:
        raise RuntimeError(f"no valid answer after 4 tries ({last})")
    _last_download[url] = time.monotonic()
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(cache + ".tmp", "w", encoding="utf-8") as f:
        json.dump(data, f)
    os.replace(cache + ".tmp", cache)
    return data


def fetch_nasa(pt, end, refresh):
    data = get_json(NASA_URL, {
        "parameters": ",".join(NASA_PARAMS.values()), "community": "AG",
        "latitude": pt["lat"], "longitude": pt["lon"],
        "start": f"{START_YEAR}0101", "end": end.strftime("%Y%m%d"), "format": "JSON",
    }, refresh, pause=1)
    fill = (data.get("header") or {}).get("fill_value", -999)
    days = defaultdict(dict)
    for key, name in NASA_PARAMS.items():
        for d, v in data["properties"]["parameter"][name].items():
            if v is not None and v != fill and v > -990:          # -999 = no data
                days[date(int(d[:4]), int(d[4:6]), int(d[6:8]))][key] = float(v)
    coords = (data.get("geometry") or {}).get("coordinates") or []
    return days, coords[2] if len(coords) > 2 else None


def fetch_openmeteo(pt, end, refresh):
    data = get_json(OM_URL, {
        "latitude": pt["lat"], "longitude": pt["lon"],
        "start_date": f"{START_YEAR}-01-01", "end_date": end.isoformat(),
        "daily": ",".join(OM_DAILY.values()),
        "hourly": ",".join(name for _, name, _ in OM_LAYERS),
        "timezone": "auto",
    }, refresh, pause=OM_PAUSE)
    days = defaultdict(dict)
    daily = data["daily"]
    for i, t in enumerate(daily["time"]):
        for key, name in OM_DAILY.items():
            v = daily[name][i]
            if v is not None:
                days[date.fromisoformat(t)][key] = float(v)
    # hourly soil moisture -> daily mean per layer (days with at least 20 hours)
    hourly = data["hourly"]
    hours = defaultdict(lambda: defaultdict(list))
    for i, t in enumerate(hourly["time"]):
        for key, name, _ in OM_LAYERS:
            v = hourly[name][i]
            if v is not None:
                hours[t[:10]][key].append(v)
    for t, layers in hours.items():
        rec = days[date.fromisoformat(t)]
        for key, vals in layers.items():
            if len(vals) >= 20:
                rec[key] = sum(vals) / len(vals)
        for key, used in (("soil_surface", OM_LAYERS[:1]), ("soil_root", OM_LAYERS[:3]),
                          ("soil_profile", OM_LAYERS)):
            if all(k in rec for k, _, _ in used):
                rec[key] = sum(rec[k] * cm for k, _, cm in used) / sum(cm for _, _, cm in used)
    return days, data.get("elevation")


# ------------------------------------------------------------- aggregation --

def data_window(today):
    """Last day to download, and last complete month to report."""
    end = min(today.replace(day=1) - timedelta(days=1), today - timedelta(days=LATENCY_DAYS))
    if (end + timedelta(days=1)).day == 1:
        return end, (end.year, end.month)
    prev = end.replace(day=1) - timedelta(days=1)
    return end, (prev.year, prev.month)


def month_list(last_ym):
    y, m = START_YEAR, 1
    while (y, m) <= last_ym:
        yield y, m
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)


def rnd(key, v):
    return None if v is None else round(v, DIGITS.get(key, 4))


def to_monthly(days, last_ym):
    """Rainfall: sum, kept only when every day has a value. Others: mean, kept with >= 80 % of days."""
    out = {}
    for y, m in month_list(last_ym):
        n = monthrange(y, m)[1]
        recs = [days.get(date(y, m, d), {}) for d in range(1, n + 1)]
        row = {}
        for key in MAIN_KEYS + LAYER_KEYS:
            vals = [r[key] for r in recs if key in r]
            if key == "rain":
                v = sum(vals) if len(vals) == n else None
            else:
                v = sum(vals) / len(vals) if vals and len(vals) >= 0.8 * n else None
            row[key] = rnd(key, v)
        out[(y, m)] = row
    return out


def downloaded(points, results):
    for pt in points:
        for source in (NASA, OM):
            if (source, pt["id"]) in results:
                yield pt, source, results[(source, pt["id"])]


def write_csvs(points, results):
    blank = lambda v: "" if v is None else v    # noqa: E731
    with open(os.path.join(OUT_DIR, "vietnam_monthly.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["province", "town", "source", "year", "month"] + [c for _, c in CSV_FIELDS])
        for pt, source, res in downloaded(points, results):
            for (y, m), row in sorted(res["monthly"].items()):
                w.writerow([pt["province"], pt["town"], source, y, m] + [blank(row[k]) for k, _ in CSV_FIELDS])
    with open(os.path.join(OUT_DIR, "vietnam_daily.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["province", "town", "source", "date"] + [c for _, c in CSV_FIELDS])
        for pt, source, res in downloaded(points, results):
            for d in sorted(res["daily"]):
                row = res["daily"][d]
                w.writerow([pt["province"], pt["town"], source, d.isoformat()]
                           + [blank(rnd(k, row.get(k))) for k, _ in CSV_FIELDS])


# ------------------------------------------------ minimal .xlsx writer ------
# Standard library only. Formulas are stored without results and Excel
# computes them when the file opens (fullCalcOnLoad).

def col_letter(n):
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


class Sheet:
    def __init__(self, name):
        self.name, self.cells, self.widths = name, {}, {}
        self.freeze = None        # (columns, rows) kept visible when scrolling
        self.autofilter = None    # e.g. "A1:O200"

    def put(self, row, col, value, style=0):
        self.cells[(row, col)] = (value, style)


class Workbook:
    FONTS = {
        "normal": '<font><sz val="10"/><name val="Arial"/><family val="2"/></font>',
        "bold": '<font><b/><sz val="10"/><name val="Arial"/><family val="2"/></font>',
        "title": '<font><b/><sz val="14"/><name val="Arial"/><family val="2"/></font>',
        "h2": '<font><b/><sz val="11"/><name val="Arial"/><family val="2"/></font>',
        "note": '<font><i/><sz val="9"/><color rgb="FF595959"/><name val="Arial"/><family val="2"/></font>',
        "alert": '<font><b/><sz val="10"/><color rgb="FFC00000"/><name val="Arial"/><family val="2"/></font>',
    }
    FILLS = {"head": "FFE7E6E6", "avg": "FFF2F2F2"}
    BUILTIN_FORMATS = {"General": 0, "0": 1, "0.00": 2, "0%": 9}
    ALIGNMENTS = {"center": '<alignment horizontal="center" vertical="center" wrapText="1"/>',
                  "wrap": '<alignment vertical="top" wrapText="1"/>'}
    NS = ('xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
          'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"')
    HEAD = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'

    def __init__(self):
        self.sheets = []
        self.xfs = [("normal", None, "General", None)]

    def add_sheet(self, name):
        self.sheets.append(Sheet(name))
        return self.sheets[-1]

    def style(self, font="normal", fill=None, fmt="General", align=None):
        key = (font, fill, fmt, align)
        if key not in self.xfs:
            self.xfs.append(key)
        return self.xfs.index(key)

    def _styles_xml(self):
        fonts = list(self.FONTS)
        fills = list(self.FILLS)
        custom = sorted({x[2] for x in self.xfs} - set(self.BUILTIN_FORMATS))
        fmt_id = {**self.BUILTIN_FORMATS, **{f: 164 + i for i, f in enumerate(custom)}}
        x = [self.HEAD, f'<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">']
        if custom:
            x.append(f'<numFmts count="{len(custom)}">' + "".join(
                f'<numFmt numFmtId="{fmt_id[f]}" formatCode="{escape(f, {chr(34): "&quot;"})}"/>'
                for f in custom) + "</numFmts>")
        x.append(f'<fonts count="{len(fonts)}">' + "".join(self.FONTS[f] for f in fonts) + "</fonts>")
        x.append(f'<fills count="{len(fills) + 2}"><fill><patternFill patternType="none"/></fill>'
                 '<fill><patternFill patternType="gray125"/></fill>' + "".join(
                     f'<fill><patternFill patternType="solid"><fgColor rgb="{self.FILLS[f]}"/>'
                     '<bgColor indexed="64"/></patternFill></fill>' for f in fills) + "</fills>")
        x.append('<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>')
        x.append('<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>')
        x.append(f'<cellXfs count="{len(self.xfs)}">')
        for font, fill, fmt, align in self.xfs:
            fill_id = fills.index(fill) + 2 if fill else 0
            attrs = (f'numFmtId="{fmt_id[fmt]}" fontId="{fonts.index(font)}" fillId="{fill_id}" '
                     'borderId="0" xfId="0" applyNumberFormat="1" applyFont="1" applyFill="1"')
            if align:
                x.append(f'<xf {attrs} applyAlignment="1">{self.ALIGNMENTS[align]}</xf>')
            else:
                x.append(f"<xf {attrs}/>")
        x.append('</cellXfs><cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/>'
                 "</cellStyles></styleSheet>")
        return "".join(x)

    def _sheet_xml(self, sheet, selected):
        x = [self.HEAD, f"<worksheet {self.NS}><sheetViews>"]
        sel = ' tabSelected="1"' if selected else ""
        x.append(f'<sheetView workbookViewId="0"{sel}>')
        if sheet.freeze:
            xs, ys = sheet.freeze
            pane = "bottomRight" if xs and ys else ("topRight" if xs else "bottomLeft")
            split = (f' xSplit="{xs}"' if xs else "") + (f' ySplit="{ys}"' if ys else "")
            x.append(f'<pane{split} topLeftCell="{col_letter(xs + 1)}{ys + 1}" activePane="{pane}" '
                     f'state="frozen"/><selection pane="{pane}"/>')
        x.append("</sheetView></sheetViews>")
        if sheet.widths:
            x.append("<cols>" + "".join(f'<col min="{c}" max="{c}" width="{w}" customWidth="1"/>'
                                        for c, w in sorted(sheet.widths.items())) + "</cols>")
        rows = defaultdict(list)
        for (r, c), cell in sheet.cells.items():
            rows[r].append((c, cell))
        x.append("<sheetData>")
        for r in sorted(rows):
            x.append(f'<row r="{r}">')
            for c, (v, s) in sorted(rows[r], key=lambda item: item[0]):
                ref = f"{col_letter(c)}{r}"
                st = f' s="{s}"' if s else ""
                if v is None:
                    x.append(f'<c r="{ref}"{st}/>')
                elif isinstance(v, (int, float)) and not isinstance(v, bool):
                    x.append(f'<c r="{ref}"{st}><v>{v!r}</v></c>')
                elif isinstance(v, str) and v.startswith("="):
                    x.append(f'<c r="{ref}"{st}><f>{escape(v[1:])}</f></c>')
                else:
                    x.append(f'<c r="{ref}"{st} t="inlineStr"><is><t>{escape(str(v))}</t></is></c>')
            x.append("</row>")
        x.append("</sheetData>")
        if sheet.autofilter:
            x.append(f'<autoFilter ref="{sheet.autofilter}"/>')
        x.append('<pageMargins left="0.7" right="0.7" top="0.75" bottom="0.75" header="0.3" footer="0.3"/>'
                 "</worksheet>")
        return "".join(x)

    def save(self, path):
        n = len(self.sheets)
        names = "".join(f'<sheet name="{escape(s.name)}" sheetId="{i}" r:id="rId{i}"/>'
                        for i, s in enumerate(self.sheets, 1))
        filters = "".join(
            f'<definedName name="_xlnm._FilterDatabase" localSheetId="{i}" hidden="1">'
            f"'{escape(s.name)}'!{absolute(s.autofilter)}</definedName>"
            for i, s in enumerate(self.sheets) if s.autofilter)
        workbook = (f"{self.HEAD}<workbook {self.NS}><workbookPr/><bookViews><workbookView activeTab=\"0\"/>"
                    f"</bookViews><sheets>{names}</sheets>"
                    + (f"<definedNames>{filters}</definedNames>" if filters else "")
                    + '<calcPr calcId="191029" fullCalcOnLoad="1"/></workbook>')
        rel = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
        workbook_rels = (f'{self.HEAD}<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/'
                         'relationships">' + "".join(
                             f'<Relationship Id="rId{i}" Type="{rel}/worksheet" Target="worksheets/sheet{i}.xml"/>'
                             for i in range(1, n + 1))
                         + f'<Relationship Id="rId{n + 1}" Type="{rel}/styles" Target="styles.xml"/>'
                         "</Relationships>")
        root_rels = (f'{self.HEAD}<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/'
                     f'relationships"><Relationship Id="rId1" Type="{rel}/officeDocument" '
                     'Target="xl/workbook.xml"/></Relationships>')
        ct = "application/vnd.openxmlformats-officedocument.spreadsheetml"
        content_types = (
            f'{self.HEAD}<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            f'<Override PartName="/xl/workbook.xml" ContentType="{ct}.sheet.main+xml"/>'
            f'<Override PartName="/xl/styles.xml" ContentType="{ct}.styles+xml"/>'
            + "".join(f'<Override PartName="/xl/worksheets/sheet{i}.xml" ContentType="{ct}.worksheet+xml"/>'
                      for i in range(1, n + 1)) + "</Types>")
        tmp = path + ".tmp"
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("[Content_Types].xml", content_types)
            z.writestr("_rels/.rels", root_rels)
            z.writestr("xl/workbook.xml", workbook)
            z.writestr("xl/_rels/workbook.xml.rels", workbook_rels)
            z.writestr("xl/styles.xml", self._styles_xml())
            for i, s in enumerate(self.sheets, 1):
                z.writestr(f"xl/worksheets/sheet{i}.xml", self._sheet_xml(s, i == 1))
        os.replace(tmp, path)


def absolute(ref):
    """'A1:O200' -> '$A$1:$O$200'"""
    out = []
    for part in ref.split(":"):
        letters = part.rstrip("0123456789")
        out.append(f"${letters}${part[len(letters):]}")
    return ":".join(out)


# ------------------------------------------------------------- workbook -----

def build_workbook(points, results, last_ym, problems, generated):
    wb = Workbook()
    S = wb.style
    years = list(range(START_YEAR, last_ym[0] + 1))
    full_years = [y for y in years if (y, 12) <= last_ym] or years
    period = f"{START_YEAR}–{full_years[-1]}"

    data_rows = [[pt["province"], pt["town"], source, y, m] + [row[k] for k in MAIN_KEYS + LAYER_KEYS]
                 for pt, source, res in downloaded(points, results)
                 for (y, m), row in sorted(res["monthly"].items())]
    last = max(2, len(data_rows) + 1)
    var_col = {k: col_letter(6 + i) for i, k in enumerate(MAIN_KEYS)}      # Data!F..K

    def rng(c):
        return f"Data!${c}$2:${c}${last}"

    readme = wb.add_sheet("README")

    # Province sheets: towns averaged by COUNTIFS/AVERAGEIFS over the Data sheet.
    pos = {}
    for prov, prov_ascii in PROVINCES:
        towns = [p for p in points if p["province"] == prov]
        for si, source in enumerate((NASA, OM)):
            sh = wb.add_sheet(f"{prov_ascii} - {'NASA' if source == NASA else OM}")
            sh.widths = {1: 24, **{c: 8 for c in range(2, 14)}, 14: 11, 15: 8}
            sh.freeze = (1, 0)
            sh.put(1, 1, f"{prov} — {source}", S("title"))
            sh.put(2, 1, "Monthly values. Each cell averages the towns below, read from the Data sheet; "
                         "it stays blank when one of them has no value for that month. The year total "
                         "or mean needs all 12 months.", S("note"))
            sh.put(3, 1, "Province", S("bold"))
            sh.put(3, 2, prov)
            sh.put(4, 1, "Source", S("bold"))
            sh.put(4, 2, source)
            sh.put(5, 1, "Towns averaged", S("bold"))
            sh.put(5, 2, len(towns), S(fmt="0"))
            sh.put(5, 3, ", ".join(f"{t['town']} ({t['coffee']})" for t in towns), S("note"))
            r = 7
            for var in VARIABLES:
                key, fmt, v = var["key"], var["fmt"][si], var_col[var["key"]]
                sh.put(r, 1, f"{var['title']} ({var['unit'][si]})", S("h2"))
                r += 1
                head = ["Year"] + MONTHS + ["Year total" if var["agg"] == "sum" else "Year mean",
                                            "Months with data"]
                for c, h in enumerate(head, 1):
                    sh.put(r, c, h, S("bold", "head", align="center"))
                r += 1
                first = r
                for y in years:
                    sh.put(r, 1, y, S("bold", fmt="0"))
                    for m in range(1, 13):
                        crit = f'{rng("A")},$B$3,{rng("C")},$B$4,{rng("D")},$A{r},{rng("E")},{m}'
                        sh.put(r, 1 + m, f'=IF(COUNTIFS({crit},{rng(v)},"<>")=$B$5,'
                                         f'AVERAGEIFS({rng(v)},{crit}),"")', S(fmt=fmt))
                    fn = "SUM" if var["agg"] == "sum" else "AVERAGE"      # only for complete years
                    sh.put(r, 14, f'=IF(O{r}=12,{fn}(B{r}:M{r}),"")', S("bold", fmt=fmt))
                    sh.put(r, 15, f"=COUNT(B{r}:M{r})", S(fmt="0"))
                    r += 1
                last_full = first + len(full_years) - 1
                sh.put(r, 1, f"Average {period}", S("bold", "avg"))
                for c in range(2, 15):
                    col = col_letter(c)
                    sh.put(r, c, f'=IFERROR(AVERAGE({col}{first}:{col}{last_full}),"")', S("bold", "avg", fmt))
                sh.put(r, 15, None, S("bold", "avg"))
                pos[(prov, source, key)] = dict(first=first, last_full=last_full, avg=r,
                                                row={y: first + i for i, y in enumerate(years)})
                r += 2

        # Comparison sheet: formulas reading the two province sheets.
        sh = wb.add_sheet(f"{prov_ascii} - Compare")
        ref = {NASA: f"'{prov_ascii} - NASA'", OM: f"'{prov_ascii} - {OM}'"}
        sh.widths = {1: 44, **{c: 14 for c in range(2, 12)}}
        sh.freeze = (1, 0)
        sh.put(1, 1, f"{prov} — NASA POWER vs Open-Meteo", S("title"))
        sh.put(2, 1, "Every number is a formula reading the two province sheets. The sources measure soil "
                     "moisture differently (NASA: wetness 0-1, Open-Meteo: m³/m³), so for soil only the "
                     "correlation compares them.", S("note"))
        r = 4
        sh.put(r, 1, f"Agreement over {period}", S("h2"))
        r += 1
        for c, h in enumerate(["Variable", NASA, OM, "Difference (Open-Meteo − NASA)", "Difference %",
                               "Correlation of monthly values (r)"], 1):
            sh.put(r, c, h, S("bold", "head", align="center"))
        r += 1
        labels = {"rain": "Rainfall, average year total (mm)", "tmax": "Maximum temperature, average (°C)",
                  "tmin": "Minimum temperature, average (°C)"}
        for var in VARIABLES:
            key = var["key"]
            pn, po = pos[(prov, NASA, key)], pos[(prov, OM, key)]
            sh.put(r, 1, labels.get(key, f"{var['title']} (NASA 0-1 · Open-Meteo m³/m³)"), S("bold"))
            sh.put(r, 2, f"={ref[NASA]}!N{pn['avg']}", S(fmt=var["fmt"][0]))
            sh.put(r, 3, f"={ref[OM]}!N{po['avg']}", S(fmt=var["fmt"][1]))
            if key in labels:
                sh.put(r, 4, f'=IF(OR(B{r}="",C{r}=""),"",C{r}-B{r})',
                       S(fmt="+0;-0;0" if key == "rain" else "+0.0;-0.0;0.0"))
            else:
                sh.put(r, 4, "different units", S("note"))
            if key == "rain":
                sh.put(r, 5, f'=IF(OR(B{r}="",C{r}="",B{r}=0),"",C{r}/B{r}-1)', S(fmt="+0%;-0%;0%"))
            sh.put(r, 6, f"=IFERROR(CORREL({ref[NASA]}!B{pn['first']}:M{pn['last_full']},"
                         f"{ref[OM]}!B{po['first']}:M{po['last_full']}),\"\")", S(fmt="0.00"))
            r += 1

        r += 1
        sh.put(r, 1, f"Year by year, {period}", S("h2"))
        r += 1
        head = ["Year", "Rainfall NASA (mm)", "Rainfall Open-Meteo (mm)", "Difference (mm)", "Difference %",
                "Tmax NASA (°C)", "Tmax Open-Meteo (°C)", "Difference (°C)",
                "Tmin NASA (°C)", "Tmin Open-Meteo (°C)", "Difference (°C)"]
        for c, h in enumerate(head, 1):
            sh.put(r, c, h, S("bold", "head", align="center"))
        r += 1
        for y in full_years:
            sh.put(r, 1, y, S("bold", fmt="0"))
            c = 2
            for key in ("rain", "tmax", "tmin"):
                fmt, dfmt = ("0", "+0;-0;0") if key == "rain" else ("0.0", "+0.0;-0.0;0.0")
                a, b = col_letter(c), col_letter(c + 1)
                sh.put(r, c, f"={ref[NASA]}!N{pos[(prov, NASA, key)]['row'][y]}", S(fmt=fmt))
                sh.put(r, c + 1, f"={ref[OM]}!N{pos[(prov, OM, key)]['row'][y]}", S(fmt=fmt))
                sh.put(r, c + 2, f'=IF(OR({a}{r}="",{b}{r}=""),"",{b}{r}-{a}{r})', S(fmt=dfmt))
                c += 3
                if key == "rain":
                    sh.put(r, c, f'=IF(OR({a}{r}="",{b}{r}="",{a}{r}=0),"",{b}{r}/{a}{r}-1)', S(fmt="+0%;-0%;0%"))
                    c += 1
            r += 1

        r += 1
        sh.put(r, 1, f"Average year {period}, month by month", S("h2"))
        r += 1
        head = ["Month", "Rainfall NASA (mm)", "Rainfall Open-Meteo (mm)", "Tmax NASA (°C)",
                "Tmax Open-Meteo (°C)", "Tmin NASA (°C)", "Tmin Open-Meteo (°C)"]
        for c, h in enumerate(head, 1):
            sh.put(r, c, h, S("bold", "head", align="center"))
        r += 1
        for m in range(1, 14):                      # 12 months, then the year
            col = col_letter(1 + m)                 # B..M in the province sheets, N = year
            fill = "avg" if m == 13 else None
            sh.put(r, 1, MONTHS[m - 1] if m <= 12 else "Year", S("bold", fill))
            for i, key in enumerate(("rain", "tmax", "tmin")):
                fmt = "0" if key == "rain" else "0.0"
                sh.put(r, 2 + 2 * i, f"={ref[NASA]}!{col}{pos[(prov, NASA, key)]['avg']}", S("normal", fill, fmt))
                sh.put(r, 3 + 2 * i, f"={ref[OM]}!{col}{pos[(prov, OM, key)]['avg']}", S("normal", fill, fmt))
            r += 1

    # Data sheet: the monthly values every formula reads.
    ds = wb.add_sheet("Data")
    ds.freeze = (0, 1)
    ds.widths = {1: 11, 2: 15, 3: 12, 4: 7, 5: 7, **{c: 13 for c in range(6, 16)}}
    head = ["Province", "Town", "Source", "Year", "Month", "Rainfall (mm)", "Tmax (°C)", "Tmin (°C)",
            "Soil surface (NASA 0-1 / OM m³/m³)", "Soil root zone (NASA 0-1 / OM m³/m³)",
            "Soil profile (NASA 0-1 / OM m³/m³)", "OM soil 0-7 cm (m³/m³)", "OM soil 7-28 cm (m³/m³)",
            "OM soil 28-100 cm (m³/m³)", "OM soil 100-255 cm (m³/m³)"]
    for c, h in enumerate(head, 1):
        ds.put(1, c, h, S("bold", "head", align="center"))
    for r, row in enumerate(data_rows, 2):
        soil = "0.00" if row[2] == NASA else "0.000"
        for c, value in enumerate(row, 1):
            fmt = {1: "General", 2: "General", 3: "General", 4: "0", 5: "0", 6: "0.0", 7: "0.0", 8: "0.0"}.get(c, soil)
            ds.put(r, c, value, S(fmt=fmt))
    ds.autofilter = f"A1:{col_letter(len(head))}{last}"

    # README, written last because it lists what was downloaded.
    rd = readme
    rd.widths = {1: 30, 2: 44, 3: 44, 4: 46, 5: 16, 6: 16}
    rd.put(1, 1, "Coffee-area climate — Đắk Lắk and Lâm Đồng, Vietnam", S("title"))
    rd.put(2, 1, f"Monthly data {START_YEAR}-01 to {last_ym[0]}-{last_ym[1]:02d}. "
                 f"Generated {generated} by vietnam/fetch_vietnam_climate.py.", S("note"))
    r = 4
    for source in (NASA, OM):
        n = sum(1 for pt in points if (source, pt["id"]) in results)
        rd.put(r, 1, f"{source}: {n} of {len(points)} towns downloaded", S("bold" if n == len(points) else "alert"))
        r += 1
    for p in problems:
        rd.put(r, 1, p, S("alert"))
        r += 1
    if problems or len(results) < 2 * len(points):
        rd.put(r, 1, "Run the script again to fill the gaps: what is already downloaded is kept.", S("alert"))
        r += 1

    def table(r, title, head, rows, align="wrap"):
        rd.put(r, 1, title, S("h2"))
        r += 1
        for c, h in enumerate(head, 1):
            rd.put(r, c, h, S("bold", "head", align="center"))
        r += 1
        for row in rows:
            for c, value in enumerate(row, 1):
                fmt = "0" if isinstance(value, int) else "General"
                rd.put(r, c, value, S("bold" if c == 1 else "normal", fmt=fmt, align=align))
            r += 1
        return r + 1

    r = table(r + 1, "Sheets", ["Sheet", "Content"], [
        ["Dak Lak - NASA, Dak Lak - Open-Meteo", "Province average of the towns: one table per variable, "
                                                 "years × months, with the year total or mean and the average year."],
        ["Dak Lak - Compare", "NASA POWER vs Open-Meteo: averages, differences and correlation, "
                              "year by year, then month by month."],
        ["Lam Dong - …", "Same for Lâm Đồng."],
        ["Data", "Monthly values per town and source: the input of every formula. Filter it to see one town."],
    ])
    r = table(r, "Sources", ["Source", "Data", "Grid", "Terms"], [
        [NASA, "NASA POWER daily API (community AG), from the MERRA-2 reanalysis.",
         "0.5° × 0.625° (about 55 × 68 km): values are grid-cell averages.",
         "Free, no key. Credit: NASA Langley Research Center (LaRC) POWER Project."],
        [OM, "Open-Meteo Historical Weather API, default model: ECMWF ERA5 and ERA5-Land reanalyses.",
         "0.25° and 0.1° (about 25 and 9 km); temperatures adjusted to the town's elevation.",
         "Free for non-commercial use only (paid plan otherwise). Licence CC BY 4.0: "
         "credit “Weather data by Open-Meteo.com”."],
    ])
    def elev(source, pt):
        value = (results.get((source, pt["id"])) or {}).get("elevation")
        return None if value is None else int(round(value))

    r = table(r, "Towns", ["Province", "Town", "Coffee", "Coordinates (approximate)",
                           "NASA grid elevation (m)", "Open-Meteo elevation (m)"],
              [[pt["province"], pt["town"], pt["coffee"], f"{pt['lat']:.4f}° N, {pt['lon']:.4f}° E",
                elev(NASA, pt), elev(OM, pt)] for pt in points], align=None)
    r = table(r, "Variables", ["Variable", NASA, OM, "Monthly value"], [
        ["Rainfall", "PRECTOTCORR (bias-corrected precipitation)", "precipitation_sum",
         "Sum of the daily values; blank unless every day of the month has data."],
        ["Maximum temperature", "T2M_MAX", "temperature_2m_max", "Mean of the daily maxima (80 % of days needed)."],
        ["Minimum temperature", "T2M_MIN", "temperature_2m_min", "Mean of the daily minima (80 % of days needed)."],
        ["Soil moisture, surface", "GWETTOP, 0-5 cm", "soil_moisture_0_to_7cm", "Mean of the daily values."],
        ["Soil moisture, root zone", "GWETROOT, 0-100 cm",
         "0-7, 7-28 and 28-100 cm layers, weighted by thickness", "Mean of the daily values."],
        ["Soil moisture, profile", "GWETPROF, surface to bedrock",
         "0-7, 7-28, 28-100 and 100-255 cm layers, weighted by thickness", "Mean of the daily values."],
    ])
    notes = [
        "NASA soil wetness goes from 0 (dry) to 1 (saturated). Open-Meteo soil moisture is the volume of water "
        "per volume of soil (m³/m³). Compare how they move, not their values.",
        "NASA values are averages over a cell of about 55 × 68 km. In the hills its elevation can be far from "
        "the town's (see Towns), which shifts temperatures by several °C. Open-Meteo adjusts temperatures to "
        "the town's elevation.",
        "Both sources are reanalyses (weather models corrected with observations), not rain-gauge readings: "
        "local rainfall can differ.",
        "Towns are in the coffee areas of the provinces as they were before the July 2025 mergers "
        "(Đắk Lắk with Phú Yên; Lâm Đồng with Đắk Nông and Bình Thuận). Coordinates are approximate.",
        "A month appears once both sources have published all of its days (a few days' delay).",
    ]
    rd.put(r, 1, "Read before using", S("h2"))
    r += 1
    for note in notes:
        rd.put(r, 1, "• " + note)
        r += 1
    return wb


# ------------------------------------------------------------------- main ---

def main(argv=None):
    try:
        sys.stdout.reconfigure(errors="replace")      # Vietnamese names on Windows consoles
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(description="Monthly climate since 2009 for the coffee areas of "
                                                 "Dak Lak and Lam Dong (Vietnam): NASA POWER vs Open-Meteo.")
    parser.add_argument("--source", choices=["both", "nasa", "openmeteo"], default="both")
    parser.add_argument("--refresh", action="store_true", help="download again instead of using the cache")
    args = parser.parse_args(argv)

    today = date.today()
    end, last_ym = data_window(today)
    points = [dict(zip(("id", "town", "province", "coffee", "lat", "lon"), p)) for p in POINTS]
    sources = [(s, f) for s, f in ((NASA, fetch_nasa), (OM, fetch_openmeteo))
               if args.source == "both" or (s == NASA) == (args.source == "nasa")]
    print(f"Monthly data {START_YEAR}-01 -> {last_ym[0]}-{last_ym[1]:02d}, {len(points)} towns", flush=True)

    results, problems = {}, []
    for source, fetch in sources:
        print(f"\n{source}", flush=True)
        for pt in points:
            print(f"  {pt['town']} ({pt['province']}) ...", flush=True)
            try:
                days, elevation = fetch(pt, end, args.refresh)
            except QuotaError as e:
                problems.append(f"{source}: quota reached ({e})")
                print(f"    stopped: {e}", flush=True)
                break
            except Exception as e:      # noqa: BLE001 — report it and go on with the other towns
                problems.append(f"{source}, {pt['town']}: {type(e).__name__}: {e}")
                print(f"    failed: {e}", flush=True)
                continue
            results[(source, pt["id"])] = dict(daily=days, monthly=to_monthly(days, last_ym), elevation=elevation)

    if not results:
        print("\nNothing downloaded, no file written:")
        for p in problems:
            print("  - " + p)
        return 1
    os.makedirs(OUT_DIR, exist_ok=True)
    xlsx = os.path.join(OUT_DIR, XLSX_NAME)
    try:
        write_csvs(points, results)
        build_workbook(points, results, last_ym, problems, today.isoformat()).save(xlsx)
    except PermissionError as e:
        print(f"\nCould not write {e.filename}: close it (Excel?) and run again; downloads are cached.")
        return 1
    print(f"\nWrote {xlsx}\n  and vietnam_monthly.csv, vietnam_daily.csv in {OUT_DIR}")
    if problems:
        print("\nIncomplete, run the script again later to fill the gaps:")
        for p in problems:
            print("  - " + p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
