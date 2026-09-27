#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Daily observations of INMET automatic stations, read straight from the official
yearly archives (portal.inmet.gov.br/dadoshistoricos/<year>.zip, several hundred MB
each) with HTTP range requests: only the zip directory and the station's CSV are
downloaded. Same rules as tools/extract_inmet.py (UTC days, 24 valid hourly values
per day, rain and extremes assigned to the preceding hour).
    python tools/fetch_inmet.py A614 A632 A631   ->  validation/stations/<code>.json
"""
import csv, datetime as dt, hashlib, io, json, os, sys, time, urllib.request, zipfile
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "validation", "stations")
URL = "https://portal.inmet.gov.br/uploads/dadoshistoricos/{year}.zip"
START, END = dt.date(2006, 7, 1), dt.date(2026, 8, 31)
UA = {"User-Agent": "Mozilla/5.0 (procafe-weather)"}


class RemoteZip(io.RawIOBase):
    """Seekable file over HTTP range requests, enough for zipfile.ZipFile."""

    def __init__(self, url):
        self.url, self.pos = url, 0
        with urllib.request.urlopen(urllib.request.Request(url, method="HEAD", headers=UA), timeout=90) as r:
            self.size = int(r.headers["Content-Length"])

    def seekable(self):
        return True

    def readable(self):
        return True

    def seek(self, n, whence=0):
        self.pos = n if whence == 0 else self.pos + n if whence == 1 else self.size + n
        return self.pos

    def tell(self):
        return self.pos

    def read(self, n=-1):
        if n < 0:
            n = self.size - self.pos
        if n == 0 or self.pos >= self.size:
            return b""
        end = min(self.size, self.pos + n) - 1
        for k in range(6):
            try:
                req = urllib.request.Request(self.url, headers={**UA, "Range": f"bytes={self.pos}-{end}"})
                with urllib.request.urlopen(req, timeout=120) as r:
                    if r.status != 206:
                        raise RuntimeError("server ignored the byte range")
                    data = r.read()
                break
            except Exception:
                if k == 5:
                    raise
                time.sleep(3 * (k + 1))
        self.pos += len(data)
        return data

    def readinto(self, b):
        data = self.read(len(b))
        b[:len(data)] = data
        return len(data)


def num(s):
    s = s.strip()
    if not s:
        return None
    x = float(s.replace(",", "."))
    return None if x <= -999 else x


def main(codes):
    hours = {c: {} for c in codes}            # code -> iso hour -> [rain, t, tmin, tmax, rh]
    meta = {c: {"requests": [], "name": None, "lat": None, "lon": None, "elev": None} for c in codes}
    for year in range(START.year, END.year + 1):
        url = URL.format(year=year)
        try:
            archive = zipfile.ZipFile(RemoteZip(url))
        except Exception as e:
            print(year, "archive unavailable:", e, flush=True)
            continue
        for name in archive.namelist():
            code = next((c for c in codes if f"_{c}_" in name), None)
            if not code or not name.lower().endswith(".csv"):
                continue
            raw = archive.read(name)
            lines = raw.decode("latin-1").splitlines()
            head = {r.split(";")[0].strip(":").upper(): r.split(";")[1] for r in lines[:8] if ";" in r}
            m = meta[code]
            m["name"] = head.get("ESTACAO", head.get("ESTAÇÃO", m["name"])) or m["name"]
            m["lat"], m["lon"], m["elev"] = num(head.get("LATITUDE", "")), num(head.get("LONGITUDE", "")), num(head.get("ALTITUDE", ""))
            m["requests"].append({"url": url, "member": name, "sha256": hashlib.sha256(raw).hexdigest()})
            h = next(i for i, l in enumerate(lines) if l.upper().startswith(("DATA;", "DATA (YYYY-MM-DD);")))
            for r in csv.reader(lines[h + 1:], delimiter=";"):
                if len(r) < 16:
                    continue
                t = dt.datetime.fromisoformat(r[0].replace("/", "-")) + dt.timedelta(hours=int(r[1][:2]))
                hours[code][t.isoformat()] = [num(r[2]), num(r[7]), num(r[10]), num(r[9]), num(r[15])]
            print(year, code, name, flush=True)
    os.makedirs(OUT, exist_ok=True)
    n = (END - START).days + 1
    dates = [(START + dt.timedelta(i)).isoformat() for i in range(n)]
    for code in codes:
        days = defaultdict(lambda: [{}, {}, {}, {}, {}])
        for stamp, vals in hours[code].items():
            t = dt.datetime.fromisoformat(stamp)
            for j, v in enumerate(vals):
                # rain and extremes concern the preceding hour; T and RH are instantaneous
                at = t if j in (1, 4) else t - dt.timedelta(hours=1)
                if v is not None and not (j == 4 and not 1 <= v <= 100):
                    days[at.date().isoformat()][j][at.hour] = v
        series = {"rain": [], "tmean": [], "tmin": [], "tmax": [], "rh": []}
        for d in dates:
            a = days.get(d)
            full = [a is not None and len(a[j]) == 24 for j in range(5)]
            series["rain"].append(round(sum(a[0].values()), 2) if full[0] else None)
            series["tmean"].append(round(sum(a[1].values()) / 24, 2) if full[1] else None)
            series["tmin"].append(round(min(a[2].values()), 2) if full[2] else None)
            series["tmax"].append(round(max(a[3].values()), 2) if full[3] else None)
            series["rh"].append(round(sum(a[4].values()) / 24, 2) if full[4] else None)
        m = meta[code]
        payload = {"id": code, "name": (m["name"] or code).strip(), "lat": m["lat"], "lon": m["lon"], "elev": m["elev"],
                   "source": "INMET automatic station · official hourly archive", "start": dates[0], "end": dates[-1],
                   "rules": {"time": "UTC days; rain and extremes assigned to the preceding hour",
                             "rain": "24 valid hourly reports per day", "extremes": "hourly reported extrema, 24 hours",
                             "rh": "daily mean of the 24 hourly readings"},
                   "raw_files": m["requests"], "series": series}
        with open(os.path.join(OUT, code + ".json"), "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
        print(code, payload["name"], {k: sum(v is not None for v in s) for k, s in series.items()}, flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
