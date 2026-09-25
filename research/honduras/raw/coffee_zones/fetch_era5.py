import subprocess, time, json, os, sys
D = os.path.dirname(os.path.abspath(__file__))
PTS = [("el_paraiso_danli",14.03,-86.57),("el_paraiso_town",13.87,-86.56),("comayagua_siguatepeque",14.60,-87.83),
("comayagua_lalibertad",14.72,-87.60),("lapaz_marcala",14.16,-88.03),("santabarbara",14.92,-88.24),("lempira_gracias",14.59,-88.58),
("copan_santarosa",14.77,-88.78),("ocotepeque",14.43,-89.18),("intibuca_laesperanza",14.31,-88.18),("olancho_campamento",14.55,-86.65),
("yoro",15.14,-87.13),("fmorazan_valledeangeles",14.15,-87.04)]
log = open(os.path.join(D, "fetch_era5.log"), "a")
for k, la, lo in PTS:
    url = ("https://archive-api.open-meteo.com/v1/archive?latitude=%s&longitude=%s&start_date=1981-01-01&end_date=2026-09-23"
           "&daily=precipitation_sum,temperature_2m_max,temperature_2m_min&models=era5_land&timezone=America%%2FTegucigalpa") % (la, lo)
    out = os.path.join(D, "era5_land_%s.json" % k)
    for attempt in range(4):
        r = subprocess.run(["curl","-sS","-m","120","-o",out,"-w","%{http_code}",url],capture_output=True,text=True)
        code = r.stdout.strip()
        log.write("%s\t%s\t%s\n" % (url, code, r.stderr.strip())); log.flush()
        if code == "429" and attempt < 3:
            time.sleep(60); continue
        break
    time.sleep(3)
log.write("DONE\n"); log.close()
