"""NASA POWER daily point data for the Honduras coffee towns: same request as the Indonesia files
(research/indonesia/raw/nasa_power_daily_*.json): PRECTOTCORR, T2M, T2M_MAX, T2M_MIN, RH2M, community AG, from 1 Jan 1981
to the latest day available. Standard library only. Usage: python3 fetch_nasa.py  (run from this folder)."""
import urllib.request, json, datetime, time
TOWNS = [('comayagua', 'Comayagua', 14.4500, -87.6333),
         ('ocotepeque', 'Nueva Ocotepeque', 14.4333, -89.1833),
         ('copan', 'Santa Rosa de Copan', 14.7667, -88.7833)]
URL = ('https://power.larc.nasa.gov/api/temporal/daily/point?parameters=PRECTOTCORR,T2M,T2M_MAX,T2M_MIN,RH2M'
       '&community=AG&latitude={lat}&longitude={lon}&start=19810101&end={end}&format=JSON')
log = open('FETCH_LOG_nasa.jsonl', 'a')
for tid, name, lat, lon in TOWNS:
    end = datetime.date.today()
    for attempt in range(12):
        url = URL.format(lat=lat, lon=lon, end=end.strftime('%Y%m%d'))
        t = time.time()
        try:
            with urllib.request.urlopen(url, timeout=300) as r:
                body = r.read()
            d = json.loads(body)
            p = d['properties']['parameter']
            # drop trailing days that are fill values (-999) in every parameter
            days = sorted(p['T2M'])
            while days and all(p[k].get(days[-1]) == -999.0 for k in p):
                for k in p:
                    p[k].pop(days[-1], None)
                days.pop()
            json.dump(d, open('nasa_power_daily_%s.json' % tid, 'w'))
            log.write(json.dumps(dict(town=tid, url=url, status=200, bytes=len(body), first=days[0], last=days[-1], ndays=len(days),
                                      grid=d['geometry']['coordinates'], secs=round(time.time() - t, 1))) + '\n')
            print(tid, 'ok', days[0], days[-1], len(days), d['geometry']['coordinates'])
            break
        except urllib.error.HTTPError as e:
            log.write(json.dumps(dict(town=tid, url=url, status=e.code, msg=e.read()[:300].decode('utf-8', 'replace'))) + '\n')
            end -= datetime.timedelta(days=1)
            time.sleep(3)
        except Exception as e:
            log.write(json.dumps(dict(town=tid, url=url, status=repr(e)[:200])) + '\n')
            time.sleep(10)
    else:
        print(tid, 'FAILED, see FETCH_LOG_nasa.jsonl')
    time.sleep(3)
