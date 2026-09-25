import json, os, glob, csv
D = os.path.dirname(os.path.abspath(__file__))
rows = []
for fn in sorted(glob.glob(os.path.join(D, "era5_land_*.json"))):
    key = os.path.basename(fn)[10:-5]
    try: j = json.load(open(fn))
    except Exception: continue
    if "daily" not in j: continue
    d = j["daily"]; agg = {}
    for t, p, tx, tn in zip(d["time"], d["precipitation_sum"], d["temperature_2m_max"], d["temperature_2m_min"]):
        a = agg.setdefault((int(t[:4]), int(t[5:7])), [0.0, 0, [], []])
        if p is not None: a[0] += p; a[1] += 1
        if tx is not None: a[2].append(tx)
        if tn is not None: a[3].append(tn)
    for (y, m), (r, n, tx, tn) in sorted(agg.items()):
        rows.append([key, j["latitude"], j["longitude"], j.get("elevation"), y, m,
                     round(r, 1) if n else "", round(sum(tx)/len(tx), 2) if tx else "", round(sum(tn)/len(tn), 2) if tn else "", n])
with open(os.path.join(D, "monthly.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow("key,lat,lon,elev_m,year,month,rain_mm,tmax_mean_c,tmin_mean_c,n_days".split(",")); w.writerows(rows)
print(len(rows), "rows")
