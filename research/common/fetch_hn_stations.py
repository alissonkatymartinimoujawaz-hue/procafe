"""Fetch weather-station records and high-resolution grids for the Honduran coffee towns (standard library only).

Usage: python3 research/common/fetch_hn_stations.py research/honduras/raw/stations

What it saves (each URL tried at most twice; a host that refuses the connection is logged once and skipped):
 1. isd_stations_honduras.csv      NOAA ISD station list, Honduran stations (CTRY HO) with distance to each town.
 2. gsod/<USAF-WBAN>.csv           NOAA Global Summary of the Day for every ISD station within RADIUS_KM of a town,
                                   1981 -> now, converted to degC and mm, with the number of hourly reports behind each value.
 3. ghcnd_stations_honduras.csv    NOAA GHCN-Daily station list (IDs starting HO) with distance to each town.
    ghcnd/<ID>.csv                 GHCN-Daily PRCP, TMAX, TMIN (mm, degC) with quality flags, for stations within RADIUS_KM.
 4. chirps_daily_<town>.csv        CHIRPS v2.0 daily rainfall at 0.05 deg (~5 km), nearest pixel (IRI Data Library).
 5. openmeteo_<model>_<town>.json  Open-Meteo archive, daily Tmax/Tmin/Tmean/rain; era5_land (0.1 deg, elevation-corrected
                                   to the town) and era5 (0.25 deg), with the elevation used.
 6. FETCH_LOG.md, fetch_log.jsonl  every request with HTTP status and size.
"""
import csv, gzip, io, json, math, os, sys, time, datetime, urllib.request, urllib.error

OUT = sys.argv[1] if len(sys.argv) > 1 else 'research/honduras/raw/stations'
TOWNS = {'comayagua': (14.45, -87.6333, 'Comayagua'), 'ocotepeque': (14.4333, -89.1833, 'Nueva Ocotepeque'),
         'copan': (14.7667, -88.7833, 'Santa Rosa de Copán')}
RADIUS_KM = 60
FIRST_YEAR = 1981
TODAY = datetime.date.today()
END = TODAY - datetime.timedelta(days=7)
UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) research-fetch/1.0'}
BLOCKED = set()
LOG = []


def log(url, status, size=0, note=''):
    LOG.append(dict(t=datetime.datetime.utcnow().isoformat(timespec='seconds'), url=url, status=status, bytes=size, note=note))
    print(status, size, url[:150], note, flush=True)


def get(url, tries=2, timeout=90):
    host = url.split('/')[2]
    if host in BLOCKED:
        log(url, 'skipped', note='host blocked earlier')
        return None
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
                b = r.read()
                log(url, r.status, len(b))
                return b
        except urllib.error.HTTPError as e:
            log(url, e.code, note=str(e.reason)[:80])
            if e.code in (403, 407) and 'proxy' in str(e).lower():
                BLOCKED.add(host)
            if e.code in (400, 403, 404, 407):
                return None
        except Exception as e:           # proxy CONNECT refusal, reset, timeout
            msg = str(e)[:120]
            log(url, 'error', note=msg)
            if 'Tunnel connection failed' in msg or '403' in msg or 'Forbidden' in msg:
                BLOCKED.add(host)
                return None
        time.sleep(4)
    return None


def km(lat1, lon1, lat2, lon2):
    p = math.pi / 180
    a = math.sin((lat2 - lat1) * p / 2) ** 2 + math.cos(lat1 * p) * math.cos(lat2 * p) * math.sin((lon2 - lon1) * p / 2) ** 2
    return 12742 * math.asin(math.sqrt(a))


def near(lat, lon):
    return {t: round(km(lat, lon, la, lo), 1) for t, (la, lo, _) in TOWNS.items()}


def f2c(v, missing=9999.9):
    v = float(v)
    return None if abs(v - missing) < 0.01 else round((v - 32) * 5 / 9, 2)


def isd_and_gsod():
    b = get('https://www.ncei.noaa.gov/pub/data/noaa/isd-history.csv')
    if not b:
        return
    rows = list(csv.DictReader(io.StringIO(b.decode('latin1'))))
    hn = []
    for r in rows:
        if r['CTRY'] != 'HO' or not r['LAT'] or not r['LON']:
            continue
        d = near(float(r['LAT']), float(r['LON']))
        hn.append(dict(usaf=r['USAF'], wban=r['WBAN'], name=r['STATION NAME'], icao=r['ICAO'], lat=r['LAT'], lon=r['LON'],
                       elev_m=r['ELEV(M)'], begin=r['BEGIN'], end=r['END'], **{'km_' + t: v for t, v in d.items()}))
    with open(os.path.join(OUT, 'isd_stations_honduras.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(hn[0].keys()))
        w.writeheader()
        w.writerows(sorted(hn, key=lambda x: min(x['km_' + t] for t in TOWNS)))
    keep = [s for s in hn if min(s['km_' + t] for t in TOWNS) <= RADIUS_KM and s['end'][:4] >= str(FIRST_YEAR)]
    print('ISD stations kept:', [(s['usaf'], s['name'], s['elev_m']) for s in keep], flush=True)
    os.makedirs(os.path.join(OUT, 'gsod'), exist_ok=True)
    for s in keep:
        sid = s['usaf'] + s['wban']
        out = []
        y0 = max(FIRST_YEAR, int(s['begin'][:4]))
        y1 = min(END.year, int(s['end'][:4]))
        for y in range(y0, y1 + 1):
            b = get('https://www.ncei.noaa.gov/data/global-summary-of-the-day/access/%d/%s.csv' % (y, sid), tries=2, timeout=60)
            if not b:
                continue
            for r in csv.DictReader(io.StringIO(b.decode('latin1'))):
                pr = float(r['PRCP'])
                out.append(dict(date=r['DATE'], tmean_c=f2c(r['TEMP']), tmean_n=r['TEMP_ATTRIBUTES'].strip(),
                                tmax_c=f2c(r['MAX']), tmax_flag=r['MAX_ATTRIBUTES'].strip(), tmin_c=f2c(r['MIN']), tmin_flag=r['MIN_ATTRIBUTES'].strip(),
                                prcp_mm=None if pr >= 99.98 else round(pr * 25.4, 1), prcp_flag=r['PRCP_ATTRIBUTES'].strip()))
        if out:
            with open(os.path.join(OUT, 'gsod', sid + '.csv'), 'w', newline='') as f:
                w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
                w.writeheader()
                w.writerows(out)
            print('GSOD', sid, s['name'], len(out), 'days', flush=True)


def ghcnd():
    b = get('https://www.ncei.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt')
    if not b:
        return
    hn = []
    for line in b.decode('latin1').splitlines():
        if not line.startswith('HO'):
            continue
        lat, lon, el = float(line[12:20]), float(line[21:30]), line[31:37].strip()
        d = near(lat, lon)
        hn.append(dict(id=line[0:11], name=line[41:71].strip(), lat=lat, lon=lon, elev_m=el, **{'km_' + t: v for t, v in d.items()}))
    if not hn:
        return
    with open(os.path.join(OUT, 'ghcnd_stations_honduras.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(hn[0].keys()))
        w.writeheader()
        w.writerows(sorted(hn, key=lambda x: min(x['km_' + t] for t in TOWNS)))
    os.makedirs(os.path.join(OUT, 'ghcnd'), exist_ok=True)
    for s in hn:
        if min(s['km_' + t] for t in TOWNS) > RADIUS_KM:
            continue
        b = get('https://www.ncei.noaa.gov/pub/data/ghcn/daily/by_station/%s.csv.gz' % s['id'])
        if not b:
            continue
        rows = []
        for r in csv.reader(io.StringIO(gzip.decompress(b).decode('latin1'))):
            if r[2] in ('PRCP', 'TMAX', 'TMIN', 'TAVG') and int(r[1][:4]) >= FIRST_YEAR:
                rows.append([r[1], r[2], int(r[3]) / 10.0, r[4], r[5], r[6]])
        with open(os.path.join(OUT, 'ghcnd', s['id'] + '.csv'), 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(['date', 'element', 'value', 'mflag', 'qflag', 'sflag'])
            w.writerows(rows)
        print('GHCN-D', s['id'], s['name'], len(rows), 'values', flush=True)


def chirps():
    for t, (la, lo, _) in TOWNS.items():
        base = 'https://iridl.ldeo.columbia.edu/SOURCES/.UCSB/.CHIRPS/.v2p0/.daily-improved/.global/.0p05/.prcp/X/%s/VALUE/Y/%s/VALUE/T/(1%%20Jan%%20%d)/(%s)/RANGE/' % (
            lo, la, FIRST_YEAR, END.strftime('%d%%20%b%%20%Y'))
        for suffix in ('data.csv', 'T+exch/table:/text/text/:table/.csv'):
            b = get(base + suffix, tries=1, timeout=300)
            if b and len(b) > 1000:
                open(os.path.join(OUT, 'chirps_daily_%s.csv' % t), 'wb').write(b)
                break


def openmeteo():
    for model in ('era5_land', 'era5'):
        for t, (la, lo, _) in TOWNS.items():
            url = ('https://archive-api.open-meteo.com/v1/archive?latitude=%s&longitude=%s&start_date=%d-01-01&end_date=%s'
                   '&daily=temperature_2m_max,temperature_2m_min,temperature_2m_mean,precipitation_sum&timezone=America%%2FTegucigalpa&models=%s') % (
                la, lo, FIRST_YEAR, END.isoformat(), model)
            b = get(url, timeout=300)
            if b:
                open(os.path.join(OUT, 'openmeteo_%s_%s.json' % (model, t)), 'wb').write(b)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for step in (isd_and_gsod, ghcnd, chirps, openmeteo):
        try:
            step()
        except Exception as e:
            log(step.__name__, 'crash', note=repr(e)[:200])
    with open(os.path.join(OUT, 'fetch_log.jsonl'), 'w') as f:
        for x in LOG:
            f.write(json.dumps(x) + '\n')
    ok = [x for x in LOG if x['status'] == 200]
    with open(os.path.join(OUT, 'FETCH_LOG.md'), 'w') as f:
        f.write('# Station and high-resolution fetch, %s\n\n' % TODAY)
        f.write('Requests: %d, OK: %d. Hosts refused by the network policy: %s\n\n' % (len(LOG), len(ok), ', '.join(sorted(BLOCKED)) or 'none'))
        f.write('Files: %s\n' % ', '.join(sorted(os.listdir(OUT))))
    print('done; blocked hosts:', BLOCKED)
