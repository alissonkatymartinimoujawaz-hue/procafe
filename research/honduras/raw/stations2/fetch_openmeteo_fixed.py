"""Re-fetch Open-Meteo ERA5 (0.25 deg) daily series that failed with HTTP 429 in fetch_hn_stations.py.
Same request as the original, but the 1981->END range is split in two calls and the halves are merged.
Usage: python3 research/honduras/raw/stations2/fetch_openmeteo_fixed.py research/honduras/raw/stations2 [town ...]"""
import json, os, sys, time, datetime, urllib.request, urllib.error

OUT = sys.argv[1]
TOWNS = {'comayagua': (14.45, -87.6333), 'ocotepeque': (14.4333, -89.1833), 'copan': (14.7667, -88.7833)}
END = datetime.date.today() - datetime.timedelta(days=7)
RANGES = [('1981-01-01', '2003-12-31'), ('2004-01-01', END.isoformat())]
UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) research-fetch/1.0'}


def get(url):
    for k in range(2):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=300) as r:
                b = r.read(); print(r.status, len(b), url[:140], flush=True); return json.loads(b)
        except urllib.error.HTTPError as e:
            print(e.code, url[:140], e.read()[:200], flush=True)
        except Exception as e:               # reset / TLS EOF through the proxy
            print('error', url[:140], str(e)[:120], flush=True)
        time.sleep(60)
    return None


for t in (sys.argv[2:] or TOWNS):
    la, lo = TOWNS[t]
    parts = []
    for a, b in RANGES:
        parts.append(get('https://archive-api.open-meteo.com/v1/archive?latitude=%s&longitude=%s&start_date=%s&end_date=%s'
                         '&daily=temperature_2m_max,temperature_2m_min,temperature_2m_mean,precipitation_sum'
                         '&timezone=America%%2FTegucigalpa&models=era5' % (la, lo, a, b)))
        time.sleep(20)
    if all(parts):
        m = parts[0]
        for k in m['daily']:
            m['daily'][k] = m['daily'][k] + parts[1]['daily'][k]
        m['note'] = 'merged from two calls: %s' % RANGES
        json.dump(m, open(os.path.join(OUT, 'openmeteo_era5_%s.json' % t), 'w'))
        print('saved', t, len(m['daily']['time']), 'days')
