# Network check 2

Run: 2026-09-25 15:26:38 UTC from the cloud session container (via agent proxy).

Command: `curl -s -o /dev/null -m 15 -w "%{http_code}" -A <browser UA> https://HOST/` (one try each).

| host | HTTP code | reachable |
|---|---|---|
| www.ncei.noaa.gov | 000 | no |
| iridl.ldeo.columbia.edu | 000 | no |
| data.chc.ucsb.edu | 000 | no |
| archive-api.open-meteo.com | 000 | no |
| psl.noaa.gov | 200 | yes |
| www.cpc.ncep.noaa.gov | 200 | yes |
| power.larc.nasa.gov | 200 | yes |
| ihcafe.hn | 000 | no |
| www.ihcafe.hn | 000 | no |
| varieties.worldcoffeeresearch.org | 000 | no |
| worldcoffeeresearch.org | 000 | no |
| promecafe.net | 000 | no |
| wikicafe.promecafe.net | 000 | no |
| www.ico.org | 000 | no |
| www.bch.hn | 000 | no |
| faolex.fao.org | 000 | no |
| www.tsc.gob.hn | 000 | no |
| banadesa.hn | 000 | no |
| www.laprensa.hn | 000 | no |
| www.elheraldo.hn | 000 | no |
| www.latribuna.hn | 000 | no |
| journals.ashs.org | 000 | no |
| apps.fas.usda.gov | 000 | no |
| bulks-faostat.fao.org | 403 | no (403, proxy or site block) |
| thedocs.worldbank.org | 301 | yes |
| api.worldbank.org | 000 | no |
| pypi.org | 200 | yes |
| files.pythonhosted.org | 403 | no (403, proxy or site block) |

Notes:
- `000` = the session's egress proxy refused the CONNECT (403 policy denial logged in `$HTTPS_PROXY/__agentproxy/status`), not a site-side timeout.
- Reachable: psl.noaa.gov, www.cpc.ncep.noaa.gov, power.larc.nasa.gov, thedocs.worldbank.org (301 redirect), pypi.org.
- Consequence: STEP 2 skipped (www.ncei.noaa.gov, data.chc.ucsb.edu, iridl.ldeo.columbia.edu and archive-api.open-meteo.com all blocked).
  STEP 3 skipped (ihcafe.hn, www.ihcafe.hn, promecafe.net, varieties.worldcoffeeresearch.org and all press hosts blocked).
