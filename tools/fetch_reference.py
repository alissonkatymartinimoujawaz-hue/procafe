#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Download NASA POWER and Open-Meteo daily series at the INMET stations (to measure
which source is closest to reality) and at the Sul de Minas towns (for the charts).

Runs in GitHub Actions (.github/workflows/fetch-reference.yml): each job has its own
IP, hence its own Open-Meteo quota. Results -> validation/grids/<job>.json
    python tools/fetch_reference.py --job om_stations|om_towns|om_best_match|nasa
"""
import argparse, json, os, re, sys, time, urllib.error, urllib.parse, urllib.request
from datetime import date, datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import openmeteo  # noqa: E402

OUT = os.path.join(ROOT, "validation", "grids")

# INMET automatic stations (id, lat, lon, elevation m) — coffee areas of Minas Gerais + São Mateus
STATIONS = [
    ("A515", "Varginha",     -21.56638888, -45.40416666, 949.78),
    ("A531", "Maria da Fé",  -22.31444444, -45.37305554, 1281.43),
    ("A529", "Passa Quatro", -22.39583333, -44.96194444, 1017.10),
    ("A524", "Formiga",      -20.45500000, -45.45388888, 878.14),
    ("A523", "Patrocínio",   -18.99666666, -46.98583333, 978.11),
    ("A556", "Manhuaçu",     -20.26333333, -42.18277777, 819.47),
    ("A616", "São Mateus",   -18.67611110, -39.86416666, 28.66),
]


def towns(region="sul_de_minas"):
    """Towns of a region from config.js (single source of truth for the site)."""
    src = open(os.path.join(ROOT, "config.js"), encoding="utf-8").read()
    block = src[src.index(f'id: "{region}"'):]
    block = block[:block.index("]")]
    out = []
    for m in re.finditer(r'\{\s*id:\s*"([^"]+)",\s*name:\s*"([^"]+)",\s*lat:\s*(-?[\d.]+),\s*lon:\s*(-?[\d.]+)'
                         r'(?:,\s*alt:\s*(\d+))?', block):
        out.append((m.group(1), m.group(2), float(m.group(3)), float(m.group(4)),
                    float(m.group(5)) if m.group(5) else None))
    return out


def save(name, payload):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name + ".json"), "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
    print("wrote", name, flush=True)


def columns(days, start, end, keys):
    """{date: {var: v}} -> {var: [v per consecutive day]}"""
    out = {k: [] for k in keys}
    d = start
    while d <= end:
        row = days.get(d.isoformat(), {})
        for k in keys:
            v = row.get(k)
            out[k].append(None if v is None else round(v, 3))
        d += timedelta(days=1)
    return out


# ------------------------------------------------------------ Open-Meteo ----
OM_DAILY = ["temperature_2m_mean", "temperature_2m_max", "temperature_2m_min",
            "precipitation_sum", "et0_fao_evapotranspiration"]
OM_HOURLY = ["relative_humidity_2m", "soil_moisture_0_to_7cm", "soil_moisture_7_to_28cm",
             "soil_moisture_28_to_100cm"]


def open_meteo(job, points, start, end, model, tz):
    client = openmeteo.Client(per_hour=4700)
    series, grids, notes = {}, {}, []
    try:
        _open_meteo_points(client, points, start, end, model, tz, series, grids, notes)
    except openmeteo.QuotaExceeded as e:             # keep what was received
        notes.append(f"stopped early: {e}")
        print("  ", e, flush=True)
    save(job, {
        "source": f"Open-Meteo Historical Weather API, models={model}",
        "url": openmeteo.ARCHIVE, "timezone": tz, "elevation": "station/town altitude (downscaling)",
        "retrieved_utc": datetime.now(timezone.utc).isoformat(), "notes": notes,
        "start": start.isoformat(), "end": end.isoformat(), "vars": OM_DAILY + OM_HOURLY,
        "points": [{"id": p[0], "name": p[1], "lat": p[2], "lon": p[3], "elev": p[4], "grid": grids.get(p[0])}
                   for p in points if p[0] in series],
        "series": series,
    })


def _open_meteo_points(client, points, start, end, model, tz, series, grids, notes):
    for pid, name, lat, lon, elev in points:          # one point per request: a failure loses little
        print(f"  {model} {pid} {name} {start}..{end}", flush=True)
        pt = [{"lat": lat, "lon": lon, "elevation": elev}]
        try:
            days, grid = openmeteo.fetch_daily(client, pt, start, end, OM_DAILY, OM_HOURLY,
                                               model=model, timezone=tz)
        except ValueError as e:                        # a variable not offered by this model
            print("   ", e, flush=True)
            notes.append(f"{pid}: {e}".splitlines()[0])
            days, grid = openmeteo.fetch_daily(client, pt, start, end, OM_DAILY, OM_HOURLY[:1],
                                               model=model, timezone=tz)
            soil, _ = openmeteo.fetch_daily(client, pt, start, end, (), OM_HOURLY[1:],
                                            model="era5_land", timezone=tz)
            for d, row in soil[0].items():
                days[0].setdefault(d, {}).update(row)
            notes.append(f"{pid}: soil moisture taken from models=era5_land")
        series[pid] = columns(days[0], start, end, OM_DAILY + OM_HOURLY)
        grids[pid] = grid[0]
        print(f"    calls used so far: {client.used:.0f}", flush=True)


# ------------------------------------------------------------ NASA POWER ----
NASA_PARAMS = ["PRECTOTCORR", "T2M", "T2M_MAX", "T2M_MIN", "RH2M", "GWETTOP", "GWETROOT"]


def nasa_point(lat, lon, start, end):
    last = None
    for ts in ("UTC", "LST"):
        q = {"parameters": ",".join(NASA_PARAMS), "community": "AG",
             "latitude": f"{lat:.4f}", "longitude": f"{lon:.4f}",
             "start": start.strftime("%Y%m%d"), "end": end.strftime("%Y%m%d"),
             "format": "JSON", "time-standard": ts}
        url = "https://power.larc.nasa.gov/api/temporal/daily/point?" + urllib.parse.urlencode(q)
        for k in range(6):
            try:
                with urllib.request.urlopen(url, timeout=300) as r:
                    data = json.load(r)
                return data, ts, url
            except urllib.error.HTTPError as e:
                last = f"HTTP {e.code} {e.read()[:300]!r}"
                if e.code in (400, 422):
                    break                                   # try the other time standard
            except Exception as e:
                last = repr(e)
            time.sleep(10 * (k + 1))
    raise RuntimeError(f"NASA POWER failed for {lat},{lon}: {last}")


def nasa(points, start, end):
    series, meta = {}, []
    for pid, name, lat, lon, elev in points:
        print(f"  NASA POWER {pid} {name}", flush=True)
        data, ts, url = nasa_point(lat, lon, start, end)
        p = data["properties"]["parameter"]
        days = {}
        for var in NASA_PARAMS:
            for k, v in p[var].items():
                days.setdefault(f"{k[:4]}-{k[4:6]}-{k[6:8]}", {})[var] = None if v == -999 else v
        series[pid] = columns(days, start, end, NASA_PARAMS)
        meta.append({"id": pid, "name": name, "lat": lat, "lon": lon, "elev": elev,
                     "time_standard": ts, "url": url, "grid": data.get("geometry")})
        time.sleep(2)
    return series, meta


def oni():
    """NOAA CPC Oceanic Niño Index (ENSO), for classifying seasons."""
    url = "https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt"
    for k in range(5):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return url, r.read().decode()
        except Exception as e:
            print("  ONI retry", repr(e), flush=True)
            time.sleep(10)
    return url, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--job", required=True, choices=["om_stations", "om_towns", "om_best_match", "nasa"])
    ap.add_argument("--force", action="store_true", help="download again even if the file exists")
    args = ap.parse_args()
    job = args.job
    if os.path.exists(os.path.join(OUT, job + ".json")) and not args.force:
        print(f"{job}.json already present — skipped (use --force to refresh)")
        return
    yesterday = date.today() - timedelta(days=1)
    st_start, st_end = date(2007, 1, 1), date(2026, 8, 31)
    tw_start = date(2006, 7, 1)
    sul = towns("sul_de_minas")

    if job == "om_stations":
        open_meteo(job, STATIONS, st_start, st_end, "era5_seamless", "GMT")
    elif job == "om_best_match":
        open_meteo(job, STATIONS, date(2017, 1, 1), st_end, "best_match", "GMT")
    elif job == "om_towns":
        open_meteo(job, sul, tw_start, yesterday, "era5_seamless", "America/Sao_Paulo")
    else:
        s_series, s_meta = nasa(STATIONS, st_start, st_end)
        t_series, t_meta = nasa(sul, tw_start, yesterday)
        url, txt = oni()
        save(job, {
            "source": "NASA POWER daily point API, community AG (MERRA-2 / GEOS)",
            "retrieved_utc": datetime.now(timezone.utc).isoformat(), "vars": NASA_PARAMS,
            "stations": {"start": st_start.isoformat(), "end": st_end.isoformat(),
                         "points": s_meta, "series": s_series},
            "towns": {"start": tw_start.isoformat(), "end": yesterday.isoformat(),
                      "points": t_meta, "series": t_series},
            "oni": {"url": url, "text": txt},
        })


if __name__ == "__main__":
    main()
