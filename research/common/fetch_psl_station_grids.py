"""Station-based gridded data from NOAA PSL (THREDDS OPeNDAP ASCII), nearest 0.5° cell to each town. Standard library only.
  - CPC Global Unified Gauge-Based Analysis of Daily Precipitation, 0.5°: Datasets/cpc_global_precip/precip.YYYY.nc (mm/day)
  - CPC Global Daily Temperature, 0.5°: Datasets/cpc_global_temp/tmax.YYYY.nc and tmin.YYYY.nc (°C)
  - GHCN_CAMS gridded 2 m temperature, monthly, 0.5°: Datasets/ghcncams/air.mon.mean.nc (K)
Usage: python3 fetch_psl_station_grids.py honduras|indonesia OUTDIR [first_year]"""
import urllib.request, datetime, csv, re, json, time, sys, os
REGIONS = {
    'honduras': [('comayagua', 14.4500, -87.6333), ('ocotepeque', 14.4333, -89.1833), ('copan', 14.7667, -88.7833)],
    'indonesia': [('pagar_alam', -4.0217, 103.2528), ('lahat', -3.7864, 103.5428), ('muaradua', -4.5330, 104.0700),
                  ('liwa', -5.0333, 104.0667), ('kepahiang', -3.6500, 102.5800)]}
region, outdir = sys.argv[1], sys.argv[2]
Y0 = int(sys.argv[3]) if len(sys.argv) > 3 else 1981
TOWNS = REGIONS[region]
os.makedirs(outdir, exist_ok=True)
BASE = 'https://psl.noaa.gov/thredds/dodsC/Datasets/'
LOG = open(os.path.join(outdir, 'fetch_log.jsonl'), 'a')


def log(**k):
    LOG.write(json.dumps(k) + '\n')
    LOG.flush()


def get(url):
    for attempt in (1, 2, 3):
        t = time.time()
        try:
            with urllib.request.urlopen(url, timeout=150) as r:
                body = r.read().decode()
            log(url=url, status=r.status, bytes=len(body), secs=round(time.time() - t, 1))
            return body
        except Exception as e:
            log(url=url, status=repr(e)[:200], secs=round(time.time() - t, 1))
            if hasattr(e, 'code') and e.code == 404:
                return None
            time.sleep(5 * attempt)
    return None


def arr(text, name):
    m = re.search(r'^%s\[\d+\]\n(.*?)(\n\n|\Z)' % re.escape(name), text, re.S | re.M)
    return [float(x) for x in m.group(1).replace('\n', ',').split(',') if x.strip()]


def box(lats, lons):
    near = {t: (min(range(len(lats)), key=lambda i: abs(lats[i] - la)), min(range(len(lons)), key=lambda j: abs(lons[j] - lo % 360))) for t, la, lo in TOWNS}
    return near, min(v[0] for v in near.values()), max(v[0] for v in near.values()), min(v[1] for v in near.values()), max(v[1] for v in near.values())


def grab(path, var, t0, t1, i0, i1, j0, j1):
    body = get(BASE + path + '.ascii?%s[%d:%d][%d:%d][%d:%d]' % (var, t0, t1, i0, i1, j0, j1))
    if body is None:
        return None
    sect = body.split('%s.%s[' % (var, var))[1].split('\n\n')[0].splitlines()[1:]
    out = {}
    for line in sect:
        m = re.match(r'\[(\d+)\]\[(\d+)\], (.*)', line)
        ti, li = int(m.group(1)), int(m.group(2))
        for lj, v in enumerate(float(x) for x in m.group(3).split(',')):
            out[(ti, i0 + li, j0 + lj)] = v
    return out


def bad(v):
    return v != v or abs(v) > 1e20 or v < -900


summary = {}
# ---- daily files, one per year ----
for key, folder, var in (('cpc_precip', 'cpc_global_precip', 'precip'), ('cpc_tmax', 'cpc_global_temp', 'tmax'), ('cpc_tmin', 'cpc_global_temp', 'tmin')):
    rows, cells, near = [], None, None
    this_year = datetime.date.today().year
    for y in range(Y0, this_year + 1):
        path = '%s/%s.%d.nc' % (folder, var, y)
        coord = get(BASE + path + '.ascii?lat,lon,time')
        if coord is None:
            log(dataset=key, year=y, note='file missing')
            continue
        lats, lons, times = arr(coord, 'lat'), arr(coord, 'lon'), arr(coord, 'time')
        if near is None:
            near, i0, i1, j0, j1 = box(lats, lons)
            cells = {t: (lats[near[t][0]], lons[near[t][1]]) for t, _, _ in TOWNS}
        g = None
        n = len(times)
        g = {}
        for a in range(0, n, 120):
            part = grab(path, var, a, min(a + 119, n - 1), i0, i1, j0, j1)
            if part is None:
                g = None
                break
            g.update({(k[0] + a, k[1], k[2]): v for k, v in part.items()})
            time.sleep(1)
        if g is None:
            log(dataset=key, year=y, note='data request failed')
            continue
        for ti in range(n):
            d = datetime.date(y, 1, 1) + datetime.timedelta(days=ti)
            for t, _, _ in TOWNS:
                v = g[(ti, near[t][0], near[t][1])]
                rows.append((t, d.isoformat(), None if bad(v) else round(v, 3)))
        print(key, y, n, 'days')
    with open(os.path.join(outdir, '%s_daily.csv' % key), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['town', 'date', var + ('_mm' if var == 'precip' else '_c'), 'grid_lat', 'grid_lon'])
        for t, d, v in rows:
            w.writerow([t, d, '' if v is None else v, cells[t][0], cells[t][1]])
    summary[key] = dict(rows=len(rows), missing=sum(1 for r in rows if r[2] is None), first=rows[0][1] if rows else None, last=rows[-1][1] if rows else None, cells=cells)
    log(dataset=key, **summary[key])

# ---- GHCN_CAMS monthly ----
path = 'ghcncams/air.mon.mean.nc'
das = get(BASE + path + '.das') or ''
coord = get(BASE + path + '.ascii?lat,lon,time')
if coord:
    lats, lons, times = arr(coord, 'lat'), arr(coord, 'lon'), arr(coord, 'time')
    m = re.search(r'time \{.*?units "(\w+) since (\d+)-(\d+)-(\d+)', das, re.S)
    unit, oy, om, od = m.group(1), int(m.group(2)), int(m.group(3)), int(m.group(4))
    origin = datetime.datetime(oy, om, od)
    tdate = [origin + (datetime.timedelta(hours=t) if unit == 'hours' else datetime.timedelta(days=t)) for t in times]
    idx = [k for k, d in enumerate(tdate) if d.year >= Y0]
    near, i0, i1, j0, j1 = box(lats, lons)
    g = {}
    for a in range(idx[0], idx[-1] + 1, 120):
        part = grab(path, 'air', a, min(a + 119, idx[-1]), i0, i1, j0, j1)
        g.update({(k[0] + a, k[1], k[2]): v for k, v in part.items()})
        time.sleep(1)
    with open(os.path.join(outdir, 'ghcncams_tmean_monthly.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['town', 'year', 'month', 'tmean_c', 'grid_lat', 'grid_lon'])
        for k in idx:
            for t, _, _ in TOWNS:
                v = g[(k, near[t][0], near[t][1])]
                w.writerow([t, tdate[k].year, tdate[k].month, '' if bad(v) else round(v - 273.15 if v > 150 else v, 3), lats[near[t][0]], lons[near[t][1]]])
    summary['ghcncams'] = dict(first=str(tdate[idx[0]])[:7], last=str(tdate[idx[-1]])[:7], units=unit, cells={t: (lats[near[t][0]], lons[near[t][1]]) for t, _, _ in TOWNS})
    log(dataset='ghcncams', **summary['ghcncams'])
json.dump(summary, open(os.path.join(outdir, 'summary.json'), 'w'), indent=1)
print(json.dumps(summary, indent=1))
