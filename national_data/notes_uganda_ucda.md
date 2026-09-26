# Uganda – UCDA / MAAIF Coffee Department official coffee statistics

Output: `national_data/uganda_ucda.csv` (103 rows). Raw files: `national_data/raw/uganda_ucda/`.
All numbers were transcribed from PDFs downloaded with curl and parsed locally (tools/pdftext.py). No numbers were taken from WebFetch.

## Coverage
| indicator | periods | basis |
|---|---|---|
| production (60-kg bags, total/robusta/arabica) | 1998/99–2014/15 | coffee year Oct–Sep, **marketed production** (UCDA procurement) |
| production (total/robusta/arabica) | 2015/16–2017/18 | fiscal year Jul–Jun, marketed production |
| production (total, R/A for 2019/20) | 2018/19–2024/25 | fiscal year Jul–Jun, **total production estimate** (UCDA 2018/19–2022/23; MAAIF Statistical Abstract 2024 for 2020/21, 2023/24, 2024/25) |
| area_total (ha) | 2000/01 (with R/A split), 2001/02, 2005/06, 2019/20, 2020/21, 2021/22, 2022/23 | varying concepts, see notes column |
| trees_total / bearing / non-bearing | one undated fact-sheet value (assigned to 2021/22) | 1 bn / 710 m / 300 m |
| yield | kg/tree R & A: 2014/15 baseline, 2019/20–2022/23; kg/ha: 2014/15, 2019/20 (improved farmers only); MAAIF t/ha 2020 | green coffee |
| holders (million households) | 2007/08, 2008/09, 2019/20–2022/23 | loose definitions, see notes |

## Definitions and caveats
- **Marketed production vs. total production.** Up to FY2017/18, UCDA's "production" is coffee procurement: FAQ + Arabica parchment delivered to export grading factories, in 60-kg bags green equivalent. From 2004/05 on the stock-movement tables say in a footnote that "Total Production" "represents mainly coffee procurement or marketed production". Starting with FY2018/19, UCDA reports a regional **total production estimate** (new + old trees), which is much higher: FY2018/19 was 7,049,049 bags, against marketed production of 4,941,955. The series therefore has a break between 2017/18 and 2018/19. The AR 2019/20 Fig. 2 puts both concepts on one chart without saying so.
- **Coffee year vs. fiscal year.** Up to 2014/15, UCDA annual reports use the coffee year (Oct–Sep). From 2015/16 they use the FY (Jul–Jun). AR 2015/16 and 2016/17 restated 2011/12–2014/15 on an FY basis: 2011/12 3,158,268; 2012/13 3,753,057; 2013/14 3,996,186; 2014/15 3,266,182. These are **not** in the CSV, which keeps one value per period. The CSV keeps Oct–Sep for ≤2014/15 and FY for ≥2015/16, and the notes column says which basis each row uses.
- **Alternative estimates and revisions** (kept only in the notes column):
  - 2000/01: production estimate 3.75 m bags (Table 3.1: 3,748,356) against procurement of 3,233,349.
  - 1999/2000: production estimate 3.6 m.
  - Stock-table production for 2001/02 (3.5 m), 2002/03 (2.75 m), 2003/04 (2.75 m printed; R+A = 2.66 m) and 2004/05 (2,441,626).
  - 2008/09 Arabica: first published as 725,649, revised to 650,029.
  - 2020/21: UCDA gave 8.1 and MAAIF gave 8.06. The CSV uses MAAIF as the latest edition. UCDA AR 2021/22 and 2022/23 print 7.05 as "Actual FY2020/21", which is a copy of the FY19/20 strategy baseline.
- **Area.** The concepts differ from year to year:
  - 2000/01: gross area (text 307,101 ha; the district table total of 331,619 is inconsistent).
  - 2001/02: net of Coffee Wilt Disease losses (225,494).
  - 2005/06: net area after CWD in the production-outlook table (196,000).
  - 2019/20–2022/23: UCDA KPI "total acreage under coffee" (583k → 609.8k ha).
  - The Strategy says area rose from 270,000 ha (undated, before the 2014–2018 replanting) to 583,000 ha.
  - No national area was found for 2002/03–2004/05 or 2006/07–2018/19. The 2003/04 CWD table (net robusta 117,600 ha of the "initial" 240,000 ha in the traditional robusta districts only) is not included.
- **Trees.** The UCDA fact sheet is undated. It says "1 billion trees (in Production 710 million, immature 300 million)" and "~504,000 tons" production. I assigned it to 2021/22 because it refers to CY2021/22 and 2022 figures. An older block on the same page says "330 million trees (Robusta 240,000; Arabica 40,244)", which is garbled and not used. The CWD tree-loss estimates (e.g. 136 m robusta trees lost by 2003/04, of an initial 300 m) are not included.
- **Yields.** The kg/tree and kg/ha values are UCDA strategy KPIs for green coffee. The 2019/20 kg/ha values cover improved farmers only (per the footnote), so they are not national averages. The Strategy also cites an "estimated 10 bags of green coffee per hectare" (not in the CSV).
- **Holders.** The definitions differ:
  - 1.2 m households "involved in coffee production, processing and marketing" (2007/08).
  - More than 1.3 m households employed (2008/09).
  - 1.7 m households growing coffee (2019/20).
  - 1.8 m households "which consider coffee as main source of livelihood" (2020/21–2022/23).
  - Not included: Arabica grown by 544,000 households (UCDA 2012, cited in AR 2013/14 p.51), and replanting-beneficiary counts.
- UCDA was mainstreamed into MAAIF (Coffee Department) around 2024–25, so MAAIF is the source for FY2023/24 onwards.

## URLs used
- UCDA annual reports index: https://ugandacoffee.go.ug/resource-center/reports/annual-reports. Files follow `https://ugandacoffee.go.ug/sites/default/files/2022-03/UCDA%20Annual%20Report_<YYYY-YYYY>[_0].pdf` for 2000-01…2019-20, plus:
  - https://ugandacoffee.go.ug/sites/default/files/2023-07/UCDA%20ANNUAL%20REPORT%202020-2021.pdf
  - https://ugandacoffee.go.ug/sites/default/files/2025-03/UCDA%20AR%202021_22.pdf (43 MB, not in raw/; identical to file-download/download/public/1069)
  - https://ugandacoffee.go.ug/sites/default/files/2025-03/UCDA%20AR%202022_23%20.pdf (42 MB, not in raw/; identical to public/1070)
  - The 2017-2018 (33 MB) and 2019-2020_0 (45 MB) reports are also too big for raw/. Use the URLs above for them.
- Coffee Sub-Sector Strategy FY2020/21–2024/25: https://ugandacoffee.go.ug/sites/default/files/2023-06/Coffee%20Sub-Sector%20Strategy%20FY%202020-2021%20to%202024-2025.pdf
- UCDA fact sheet: https://ugandacoffee.go.ug/resource-center/fact-sheet (saved as UCDA_fact_sheet_2026-09-26.html)
- MAAIF Statistical Abstract 2024: https://www.agriculture.go.ug/wp-content/uploads/2026/02/MAAIF-Statistical-Abstract-2024_-1.pdf. The host without www returns a proxy 403; the www host works.

## URLs tried, no usable data
- `.../Resource_center/UCDA%20Annual%20Report_2004-2005.pdf` returned 404 (the correct path is under 2022-03).
- UCDA AR 2010/11 is a scanned PDF with no text layer, and no OCR tool is available. Its 2010/11 values are taken from later editions.
- UCDA@30 magazine (public/397) is narrative only.
- `2026-09/Uganda_Coffee.pdf` (MAAIF "A guide to Uganda's coffees") is an image-only brochure with no statistics seen in the pages checked.
- UCDA statistics page: .xls files cover exports and prices only.
- MAAIF Annual Performance Reports 2016/17, 2017/18 and 2019/20: no national area series. MAAIF press brief on coffee prices (Jun 2025): exports only.
- The MAAIF /Statistics/ page lists no files, and the wp-json media search found no other statistical abstracts.
- www.ubos.org and ubos.org: blocked by the proxy (403); not reachable.

## Gaps
- Area: 2002/03–2004/05 and 2006/07–2018/19; no robusta/arabica split after 2000/01; no 2023/24+ values.
- Trees: only one undated snapshot. No bearing/non-bearing time series.
- Production R/A split: missing for 2018/19 and for 2020/21 onwards.
- Tonnes are not given separately (bags × 0.06 t). A few are quoted in the reports (e.g. FY2015/16 242,183 t; FY2016/17 279,183 t).
