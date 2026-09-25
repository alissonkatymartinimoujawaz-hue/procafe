# Network check 3 — environment Honduras

Date/time (UTC): 2026-09-25 15:27:58

Note: environment Honduras. One try per host, `curl -s -o /dev/null -m 15 -w '%{http_code}' https://HOST/` with a browser User-Agent. Code 000 = no connection/timeout.

| host | HTTP code | reachable |
|---|---|---|
| www.ncei.noaa.gov | 200 | yes |
| iridl.ldeo.columbia.edu | 200 | yes |
| data.chc.ucsb.edu | 200 | yes |
| archive-api.open-meteo.com | 400 | yes |
| psl.noaa.gov | 200 | yes |
| www.cpc.ncep.noaa.gov | 200 | yes |
| power.larc.nasa.gov | 000 | no |
| ihcafe.hn | 000 | no |
| www.ihcafe.hn | 301 | yes |
| varieties.worldcoffeeresearch.org | 200 | yes |
| worldcoffeeresearch.org | 200 | yes |
| promecafe.net | 200 | yes |
| wikicafe.promecafe.net | 301 | yes |
| www.ico.org | 302 | yes |
| www.bch.hn | 000 | no |
| faolex.fao.org | 200 | yes |
| www.tsc.gob.hn | 200 | yes |
| banadesa.hn | 403 | yes |
| www.laprensa.hn | 200 | yes |
| www.elheraldo.hn | 200 | yes |
| www.latribuna.hn | 403 | yes |
| journals.ashs.org | 000 | no |
| apps.fas.usda.gov | 000 | no |
| bulks-faostat.fao.org | 403 | yes |
| thedocs.worldbank.org | 301 | yes |
| api.worldbank.org | 000 | no |
| pypi.org | 403 | yes |
| files.pythonhosted.org | 404 | yes |

A 403 may come from the site itself or from the environment's egress proxy; codes are recorded as returned.
