# Ethiopia – ESS (ex-CSA) Agricultural Sample Survey / ECTA (coffee)

**Result: no data collected. `ethiopia_ess.csv` has only the header row.** Every host that serves the reports is blocked by this environment's egress proxy. Most return `000` or a CONNECT 403/502 from the proxy. `http://www.ess.gov.et/` returns the plain-text message "Host not in allowlist: www.ess.gov.et". The ESS host itself is not refusing the connection. Tested 2026-09-26 with curl (-L, Mozilla UA, -m 40..120).

## Target publication
CSA/ESS *Agricultural Sample Survey, Volume I: Report on Area and Production of Major Crops (Private Peasant Holdings, Meher Season)*, one per Ethiopian year (E.C. N ↔ G.C. (N+7)/(N+8)). Coffee is in the table of permanent/tree crops (stimulant crops). The table gives the number of holders, area (ha), production (qt) and yield (qt/ha).

## Direct PDF URLs found (via WebSearch), all unreachable here
| Year | URL | Result |
|---|---|---|
| 2010 E.C. (2017/18) | https://www.statsethiopia.gov.et/wp-content/uploads/2020/02/Area-and-Production-for-Major-Crops-Private-Peasant-Holdings-Meher-Season-2017-18-2010-E.C..pdf | 000 (proxy 502) |
| 2010 E.C. (2017/18) | https://ess.gov.et/wp-content/uploads/2010/09/Area-and-Production-for-Major-Crops-Private-Peasant-Holdings-Meher-Season-2017-18-2010-E.C.pdf | 000; http://www. variant 403 "not in allowlist" |
| 2011 E.C. (2018/19) | https://www.statsethiopia.gov.et/wp-content/uploads/2019/09/Report-on-Area-and-production-of-major-crops-2011-Meher-season.pdf | 000 |
| 2011 E.C. (2018/19) | https://ess.gov.et/wp-content/uploads/2011/09/Area-and-Production-for-Major-Crops-Private-Peasant-Holdings-Meher-Season-2018-19-2011-E.C.pdf | 000 |
| 2012 E.C. (2019/20) | https://www.statsethiopia.gov.et/wp-content/uploads/2020/04/Report-on-Area-and-production-of-major-crops-2012-E.C-Meher-season.pdf | 000 |
| 2013 E.C. (2020/21) | http://www.statsethiopia.gov.et/wp-content/uploads/2021/05/2013-MEHER-REPORT.FINAL_.pdf | 000 |
| 2014 E.C. (2021/22) | https://www.statsethiopia.gov.et/wp-content/uploads/2023/05/The-2014-EC-Meher-Season-Report-on-Area-and-Production-of-Major-Crops_Final-1.pdf | 000 |
| 2014 E.C. (2021/22) | https://www.scribd.com/document/750357972/ (copy) | 000 |
| 2008 E.C. (2015/16) | https://www.statsethiopia.gov.et/wp-content/uploads/2019/06/Agricultural-Sample-Survey-Product-Utilization-Meher-Season-2015.pdf (search-result title "Area and production of major crops"; actually Vol. VII utilization?) | 000 |
| 2009 E.C. (2016/17) | https://ess.gov.et/wp-content/uploads/2016/09/Agricultural-Sample-Survey-Product-Utilization-Meher-Season-2016.pdf (Vol. VII) | 000 |
| — | https://ess.gov.et/agriculture/ (ESS agriculture publications index) | 000 |

The ESS WordPress uploads appear to follow the pattern `ess.gov.et/wp-content/uploads/<G.C. year>/09/...`. If the host is allow-listed, look for the other years' reports under the same pattern.

## Other hosts tried (all failed: 000 / proxy 403/502 unless noted)
www.ess.gov.et (http 403 "Host not in allowlist"), ess.gov.et (http/https), statsethiopia.gov.et (www / no-www, http/https), csa.gov.et (www / no-www), ecta.gov.et (www / no-www, http/https), nada.ess.gov.et, microdata.ess.gov.et, catalog.ihsn.org (403), microdata.fao.org, openknowledge.fao.org, essp.ifpri.info, ebrary.ifpri.org, www.ifpri.org, ageconsearch.umn.edu, scribd.com, researchgate, academia.edu, core.ac.uk, data.humdata.org, countrystat.org, dataverse.harvard.edu, zenodo, figshare, osf.io, archive.org / web.archive.org, archive.ph, arquivo.pt, fas.usda.gov / apps.fas.usda.gov (GAIN Coffee Annual, which quotes ECTA/CSA), aigaforum.com (ECTA "Economic Benefit of Ethiopian Coffee" PDF, 403), teaandcoffee.net, allafrica.com, moa.gov.et, ata.gov.et, nbe.gov.et, ecx.com.et, NCBI/PMC, arXiv, MDPI, ScienceDirect, Springer, AJOL, IISTE, scirp, sciepub, cdn.jsdelivr.net, gitlab, huggingface, kaggle, S3/GCS.
GitHub: api.github.com responds, but anonymous code search returns 403. A GitHub MCP code search for "Meher" coffee quintals, "Private Peasant Holdings" pdf and "Agricultural Sample Survey" coffee found no mirrored CSA reports or extracted tables.

## Reachable host: www.fao.org. Nothing usable there
- https://www.fao.org/in-action/agrisurvey/access-to-data/ethiopia/en only links to http://www.csa.gov.et/ (blocked).
- FAO/MAFAP technical note, https://www.fao.org/fileadmin/templates/mafap/documents/technical_notes/Ethiopia/2005-2013/Ethiopia-Coffee_web.pdf, was downloaded to the scratchpad but **not used**. It is secondary. Its only CSA figure is "In 2011 ... 3.8 percent of Ethiopia's cultivation area, corresponding to 515,882 hectares (CSA, 2012)", and the text does not say which E.C. report or which area concept that figure comes from. Its other series are FAOSTAT.
- The FAO country profile (fao.org/3/i9732en) redirects to openknowledge.fao.org, which is blocked.

## Gaps
All years from 1998 onward for all indicators (area, production, yield and holders) are missing. ECTA data is also missing.

## How to fill
Allow-list `ess.gov.et`, `www.ess.gov.et` and `www.statsethiopia.gov.et` (or run from an unrestricted network), download the Vol. I PDFs above, and read the coffee row of the permanent/tree-crops table. Row format: country=Ethiopia, source=ESS/CSA, period_type=ethiopian_year, period `YYYY EC (YYYY/YY)`, indicators holders, area_total (ha, area under coffee), production (qt), yield (qt/ha). Also check whether production is recorded as fresh cherry or clean coffee. In CSA reports production is normally in quintals of clean/dried coffee; verify this in each report's definitions section.
