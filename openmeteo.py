#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Open-Meteo client — Python standard library only.

Free API (https://open-meteo.com/en/terms): non-commercial use, per IP address
600 calls/minute, 5 000/hour, 10 000/day, 300 000/month. A request is weighted:
    calls = max(1, days / 14) * max(1, variables / 10) * locations
so 1981 -> today for ONE town is ~1 200 calls. History must therefore be fetched
once and cached; afterwards only the last days are re-requested.

"Daily API request limit exceeded" (HTTP 429) means the quota of the current IP is
spent — typical on shared cloud machines (CI runners, hosted notebooks). Run from
your own connection, or wait for the next day: the cache keeps what was received.

Models (Historical Weather API, https://open-meteo.com/en/docs/historical-weather-api):
  era5_seamless  ERA5-Land (0.1°) temperature/humidity + ERA5 (0.25°) wind/radiation,
                 1950 -> ~5 days ago, one consistent series (used for the site)
  best_match     default: blends ECMWF IFS 9 km (2017+) with ERA5 / ERA5-Land
Temperature is downscaled to the `elevation` given (station/town altitude), else
to a 90 m terrain model.
"""
import json, time, urllib.error, urllib.parse, urllib.request
from datetime import date, timedelta

ARCHIVE = "https://archive-api.open-meteo.com/v1/archive"
FORECAST = "https://api.open-meteo.com/v1/forecast"
HEADERS = {"User-Agent": "procafe-weather/1.0 (Open-Meteo client)"}


class QuotaExceeded(RuntimeError):
    """The free-API quota of this IP is used up (daily, or hourly without waiting)."""


def weight(days, n_vars, n_locations):
    return max(1.0, days / 14.0) * max(1.0, n_vars / 10.0) * n_locations


class Client:
    """Paces requests under the free limits and understands Open-Meteo's 429 replies."""

    def __init__(self, per_minute=500, per_hour=4500, wait_hourly=True, log=print):
        self.per_minute, self.per_hour = per_minute, per_hour
        self.wait_hourly, self.log = wait_hourly, log
        self.history = []                       # [(timestamp, weight)]
        self.used = 0.0

    def _pace(self, w):
        while True:
            now = time.time()
            self.history = [(t, x) for t, x in self.history if now - t < 3600]
            minute = sum(x for t, x in self.history if now - t < 60)
            hour = sum(x for _, x in self.history)
            if hour + w > self.per_hour and self.history:
                if not self.wait_hourly:
                    raise QuotaExceeded("hourly budget reached — run again in an hour (cache is kept)")
                pause = 3600 - (now - self.history[0][0]) + 5
                self.log(f"    Open-Meteo: hourly budget reached, waiting {pause / 60:.0f} min ...")
                time.sleep(pause)
            elif minute + w > self.per_minute and minute > 0:
                time.sleep(61)
            else:
                return

    def get(self, url, params, w, tries=6):
        self._pace(w)
        full = url + "?" + urllib.parse.urlencode(params, safe=",")
        last = None
        for k in range(tries):
            try:
                with urllib.request.urlopen(urllib.request.Request(full, headers=HEADERS), timeout=180) as r:
                    data = json.load(r)
                self.history.append((time.time(), w))
                self.used += w
                return data
            except urllib.error.HTTPError as e:
                body = e.read().decode("utf-8", "replace")
                try:
                    reason = json.loads(body).get("reason", body)
                except ValueError:
                    reason = body[:200]
                if e.code == 429:
                    if "Minutely" in reason:
                        self.log("    Open-Meteo: minutely limit, waiting 65 s ...")
                        time.sleep(65)
                        continue
                    if "Hourly" in reason and self.wait_hourly:
                        pause = 3660 - time.time() % 3600
                        self.log(f"    Open-Meteo: hourly limit, waiting {pause / 60:.0f} min ...")
                        time.sleep(pause)
                        continue
                    raise QuotaExceeded(f"Open-Meteo 429: {reason}")
                if e.code == 400:
                    raise ValueError(f"Open-Meteo rejected the request: {reason}\n{full}")
                last = f"HTTP {e.code}: {reason}"
            except Exception as e:              # network errors, resets, timeouts
                last = repr(e)
            time.sleep(min(60, 3 * 2 ** k))
        raise RuntimeError(f"Open-Meteo request failed after {tries} tries: {last}\n{full}")


def _chunks(start, end, days=366):
    a = start
    while a <= end:
        b = min(end, a + timedelta(days=days - 1))
        yield a, b
        a = b + timedelta(days=1)


def fetch_daily(client, points, start, end, daily_vars=(), hourly_vars=(), model=None,
                timezone="America/Sao_Paulo", api=ARCHIVE, chunk_days=366, min_hours=20):
    """Daily values for several points in one request per chunk of time.

    points: [{"lat": .., "lon": .., "elevation": .. or None}]
    hourly_vars are averaged to daily means (days with < min_hours valid hours -> None).
    Returns ([{ "YYYY-MM-DD": {var: value} } per point], [grid info per point])."""
    out = [dict() for _ in points]
    grid = [None] * len(points)
    for a, b in _chunks(start, end, chunk_days):
        params = {
            "latitude": ",".join(f"{p['lat']:.5f}" for p in points),
            "longitude": ",".join(f"{p['lon']:.5f}" for p in points),
            "start_date": a.isoformat(), "end_date": b.isoformat(), "timezone": timezone,
        }
        if daily_vars:
            params["daily"] = ",".join(daily_vars)
        if hourly_vars:
            params["hourly"] = ",".join(hourly_vars)
        if model:
            params["models"] = model
        if any(p.get("elevation") is not None for p in points):
            params["elevation"] = ",".join("nan" if p.get("elevation") is None else f"{p['elevation']:.0f}"
                                           for p in points)
        w = weight((b - a).days + 1, len(daily_vars) + len(hourly_vars), len(points))
        data = client.get(api, params, w)
        data = data if isinstance(data, list) else [data]
        for i, d in enumerate(data):
            grid[i] = {"latitude": d.get("latitude"), "longitude": d.get("longitude"),
                       "elevation": d.get("elevation")}
            for var in daily_vars:
                for t, v in zip(d["daily"]["time"], d["daily"][var]):
                    out[i].setdefault(t, {})[var] = v
            for var in hourly_vars:
                acc = {}
                for t, v in zip(d["hourly"]["time"], d["hourly"][var]):
                    if v is not None:
                        acc.setdefault(t[:10], []).append(v)
                day = a
                while day <= b:
                    vals = acc.get(day.isoformat(), [])
                    out[i].setdefault(day.isoformat(), {})[var] = (
                        round(sum(vals) / len(vals), 4) if len(vals) >= min_hours else None)
                    day += timedelta(days=1)
    return out, grid


def recent_daily(client, points, daily_vars, past_days=31, timezone="America/Sao_Paulo"):
    """Provisional last days from the forecast API (no 5-day ERA5 delay)."""
    params = {
        "latitude": ",".join(f"{p['lat']:.5f}" for p in points),
        "longitude": ",".join(f"{p['lon']:.5f}" for p in points),
        "daily": ",".join(daily_vars), "past_days": past_days, "forecast_days": 1,
        "timezone": timezone,
    }
    if any(p.get("elevation") is not None for p in points):
        params["elevation"] = ",".join("nan" if p.get("elevation") is None else f"{p['elevation']:.0f}"
                                       for p in points)
    data = client.get(FORECAST, params, weight(past_days + 1, len(daily_vars), len(points)))
    data = data if isinstance(data, list) else [data]
    today = date.today().isoformat()
    return [{t: {v: d["daily"][v][k] for v in daily_vars}
             for k, t in enumerate(d["daily"]["time"]) if t < today} for d in data]
