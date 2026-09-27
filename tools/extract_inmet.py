#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Ground truth for the source comparison: daily INMET automatic-station observations.

Reads the station archive already verified in the WeatherRecord repository
(official INMET hourly CSVs, portal.inmet.gov.br/dadoshistoricos, with SHA-256):
  * rain / Tmean / Tmin / Tmax : WeatherRecord daily rows (UTC days, 24 valid hours
    required, rain and extremes assigned to the preceding hour)
  * relative humidity          : recomputed here from the raw hourly CSVs
    ("UMIDADE RELATIVA DO AR, HORARIA"), daily mean of the 24 UTC hours, all 24
    hours required
Output -> validation/stations/<code>.json
    python tools/extract_inmet.py <path to WeatherRecord clone>
"""
import csv, datetime as dt, gzip, json, os, sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODES = ["A515", "A531", "A529", "A524", "A523", "A556", "A616"]
START, END = dt.date(2006, 7, 1), dt.date(2026, 8, 31)


def num(s):
    s = s.strip()
    if not s:
        return None
    x = float(s.replace(",", "."))
    return None if x <= -999 else x


def hourly_rh(raw_paths):
    by_day = defaultdict(dict)
    for path in raw_paths:
        lines = gzip.decompress(open(path, "rb").read()).decode("latin-1").splitlines()
        head = next(i for i, l in enumerate(lines) if l.upper().startswith(("DATA;", "DATA (YYYY-MM-DD);")))
        cols = [c.upper() for c in lines[head].split(";")]
        k = next(i for i, c in enumerate(cols) if c.startswith("UMIDADE RELATIVA DO AR, HORARIA"))
        for r in csv.reader(lines[head + 1:], delimiter=";"):
            if len(r) <= k:
                continue
            day, hour = r[0].replace("/", "-"), int(r[1][:2])
            v = num(r[k])
            if v is not None and 1 <= v <= 100:
                by_day[day][hour] = v
    return {d: round(sum(h.values()) / 24, 2) for d, h in by_day.items() if len(h) == 24}


def main(wr):
    out_dir = os.path.join(ROOT, "validation", "stations")
    os.makedirs(out_dir, exist_ok=True)
    n = (END - START).days + 1
    dates = [(START + dt.timedelta(i)).isoformat() for i in range(n)]
    for code in CODES:
        st = json.load(open(os.path.join(wr, "site", "data", "stations", code + ".json"), encoding="utf-8"))
        rows = {r[0]: r for r in st["rows"]}
        raws = [os.path.join(wr, "site", q["raw_path"]) for q in st["requests"]]
        rh = hourly_rh(raws)
        series = {"rain": [], "tmean": [], "tmin": [], "tmax": [], "rh": []}
        for d in dates:
            r = rows.get(d)
            for j, var in enumerate(("rain", "tmean", "tmin", "tmax"), start=1):
                series[var].append(None if r is None or r[j] is None else round(r[j], 2))
            series["rh"].append(rh.get(d))
        payload = {
            "id": code, "name": st["name"], "lat": st["latitude"], "lon": st["longitude"],
            "elev": st["elevation_m"], "source": st["source"], "start": dates[0], "end": dates[-1],
            "rules": {"time": st["time_note"], "rain": st["rain_rule"], "extremes": st["extreme_rule"],
                      "rh": "Daily mean of the 24 hourly UTC readings; all 24 required."},
            "raw_files": [{k: q[k] for k in ("url", "member", "sha256")} for q in st["requests"]],
            "series": series,
        }
        with open(os.path.join(out_dir, code + ".json"), "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
        have = {k: sum(v is not None for v in s) for k, s in series.items()}
        print(code, st["name"], have, flush=True)


if __name__ == "__main__":
    main(sys.argv[1])
