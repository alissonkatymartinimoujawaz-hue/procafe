import subprocess,json,time,csv,collections
from fetch import log
PTS=[('el_paraiso_danli',14.03,-86.57),('comayagua_siguatepeque',14.60,-87.83),('lapaz_marcala',14.16,-88.03),('santabarbara',14.92,-88.24),('lempira_gracias',14.59,-88.58),('copan_santarosa',14.77,-88.78),('ocotepeque',14.43,-89.18),('intibuca_laesperanza',14.31,-88.18),('olancho_campamento',14.55,-86.65),('yoro',15.14,-87.13)]
rows=[]
for k,la,lo in PTS:
    u=f'https://archive-api.open-meteo.com/v1/archive?latitude={la}&longitude={lo}&start_date=1981-01-01&end_date=2026-09-23&daily=precipitation_sum&models=era5&timezone=America%2FTegucigalpa'
    fn=f'era5_rain_{k}.json'
    r=subprocess.run(['curl','-sS','-m','90','-o',fn,'-w','%{http_code}',u],capture_output=True,text=True)
    code=r.stdout; log(u,code,u,'application/json',fn if code=='200' else open(fn).read()[:150] if code!='000' else r.stderr[:100])
    print(k,code,flush=True)
    if code!='200':
        subprocess.run(['rm','-f',fn]); 
        if code=='429': break
        time.sleep(5); continue
    d=json.load(open(fn))['daily']; agg=collections.defaultdict(lambda:[0.0,0])
    for t,p in zip(d['time'],d['precipitation_sum']):
        if p is None: continue
        a=agg[(int(t[:4]),int(t[5:7]))]; a[0]+=p; a[1]+=1
    for (y,m),(s,n) in sorted(agg.items()): rows.append((k,y,m,round(s,2),n))
    time.sleep(5)
w=csv.writer(open('monthly_rain.csv','w')); w.writerow(['key','year','month','rain_mm','n_days']); w.writerows(rows)
