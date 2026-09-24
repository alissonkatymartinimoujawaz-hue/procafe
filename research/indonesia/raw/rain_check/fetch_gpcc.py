import urllib.request, datetime, csv, re, json, time, sys
BASE = "https://psl.noaa.gov/thredds/dodsC/Datasets/gpcc/"
TOWNS = [("pagar_alam",-4.0217,103.2528),("lahat",-3.7864,103.5428),("muaradua",-4.5330,104.0700),
         ("liwa",-5.0333,104.0667),("kepahiang",-3.6500,102.5800)]
DSETS = [("gpcc_full_v2020","full_v2020/precip.mon.total.0.25x0.25.v2020.nc","GPCC Full Data Monthly v2020 0.25deg (PSL)",60),
         ("gpcc_monitor_v2020","monitor/precip.monitor.mon.total.1x1.v2020.nc","GPCC Monitoring Product v2020 1deg (PSL)",120),
         ("gpcc_first_guess","first_guess/precip.first.mon.total.1x1.nc","GPCC First Guess Monthly 1deg (PSL)",120)]
only = sys.argv[2:] or [d[0] for d in DSETS]
LOGF = open(sys.argv[1], "a")
def log(**k): LOGF.write(json.dumps(k) + "\n"); LOGF.flush()
def get(url):
    for attempt in (1, 2):
        t = time.time()
        try:
            with urllib.request.urlopen(url, timeout=110) as r:
                body = r.read().decode()
            log(url=url, status=r.status, bytes=len(body), secs=round(time.time()-t, 1)); return body
        except Exception as e:
            log(url=url, status=repr(e)[:200], secs=round(time.time()-t, 1))
            if attempt == 1: time.sleep(5)
    raise RuntimeError(url)
def arr(text, name):
    m = re.search(r"^%s\[\d+\]\n(.*?)(\n\n|\Z)" % re.escape(name), text, re.S | re.M)
    return [float(x) for x in m.group(1).replace("\n", ",").split(",") if x.strip()]
day0 = datetime.date(1800, 1, 1)
for key, path, label, chunk in DSETS:
    if key not in only: continue
    url = BASE + path + ".ascii?"
    coord = get(url + "lat,lon,time")
    lats, lons, times = arr(coord, "lat"), arr(coord, "lon"), arr(coord, "time")
    dates = [day0 + datetime.timedelta(days=t) for t in times]
    idx = [i for i, d in enumerate(dates) if d.year >= 1981]
    t0, t1 = idx[0], idx[-1]
    near = {}
    for town, la, lo in TOWNS:
        near[town] = (min(range(len(lats)), key=lambda i: abs(lats[i]-la)),
                      min(range(len(lons)), key=lambda j: abs(lons[j]-lo % 360)))
    i0, i1 = min(v[0] for v in near.values()), max(v[0] for v in near.values())
    j0, j1 = min(v[1] for v in near.values()), max(v[1] for v in near.values())
    grid = {}  # (time_value, ilat, ilon) -> value
    for a in range(t0, t1 + 1, chunk):
        b = min(a + chunk - 1, t1)
        body = get(url + "precip[%d:%d][%d:%d][%d:%d]" % (a, b, i0, i1, j0, j1))
        sect = body.split("precip.precip[")[1].split("\n\n")[0].splitlines()[1:]
        ts = arr(body, "precip.time"); bl = arr(body, "precip.lat"); bo = arr(body, "precip.lon")
        assert bl == lats[i0:i1+1] and bo == lons[j0:j1+1] and len(ts) == b - a + 1
        for line in sect:
            m = re.match(r"\[(\d+)\]\[(\d+)\], (.*)", line)
            ti, li = int(m.group(1)), int(m.group(2))
            for lj, v in enumerate(float(x) for x in m.group(3).split(",")):
                grid[(ts[ti], i0 + li, j0 + lj)] = v
        time.sleep(2)
    rows, cells = [], {}
    for town, la, lo in TOWNS:
        il, jl = near[town]; nmiss = 0; yrs = set()
        for t in times[t0:t1+1]:
            v = grid[(t, il, jl)]; d = day0 + datetime.timedelta(days=t)
            if v < -1e30 or v != v or v > 1e30: nmiss += 1; continue
            rows.append((town, d.year, d.month, round(v, 2), lats[il], lons[jl], label)); yrs.add(d.year)
        cells[town] = dict(ilat=il, ilon=jl, grid_lat=lats[il], grid_lon=lons[jl], first=str(dates[t0])[:7],
                           last=str(dates[t1])[:7], months_valid=t1-t0+1-nmiss, months_missing=nmiss)
    with open("%s_monthly.csv" % key, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["town","year","month","rain_mm","grid_lat","grid_lon","source"]); w.writerows(rows)
    log(dataset=key, path=path, ntime_total=len(times), box=[i0, i1, j0, j1], cells=cells)
