# National coffee statistics (Ethiopia, Uganda, Mexico, Peru, Indonesia)

Official national and FAO statistics, collected 2026-09-26, for cross-checking and completing the USDA-based
balance sheets in `Balance_Sheet_weather_MI.xlsx`.

All data CSVs share one header:
`country,source,indicator,unit,period_type,period,value,source_url,notes`
Each row holds one value exactly as published. Missing values have no row. `notes` gives the basis
(cherry, parchment or green; arabica, robusta or total), the table and page, the flags, and any revisions.
Detailed per-source notes are in `notes_<source>.md`: every URL tried and used, definitions and edition conflicts.

## Files and coverage

| File | Source | Coverage | Status |
|---|---|---|---|
| `faostat.csv` | FAOSTAT QCL, Coffee, green (656) | 5 countries, 1998–2024: area_harvested (ha), production (t), yield (kg/ha) | Complete. FAO flag in notes (A/E/I/X). Production equals area × yield for all 135 country-years. |
| `mexico_siap.csv` | SIAP data as published in FIRA Panorama Café and SIAP Escenario/Expectativas | 2004/05–2023/24: area_planted, area_harvested, production (t, **cherry**), yield (t/ha) | Partial. See gaps below. |
| `peru_midagri.csv` | MIDAGRI (yearbooks, El Agro en Cifras), INEI yearbook reprints of MIDAGRI data | production 2000–2025 (t, **parchment**); area_harvested 2010–2024; yield 2010–2023 | Partial. Values mix editions. |
| `uganda_ucda.csv` | UCDA annual reports, MAAIF Statistical Abstract 2024, UCDA Coffee Sub-Sector Strategy, UCDA fact sheet | production (60-kg bags) 1998/99–2024/25, split robusta/arabica to 2019/20; area, trees, yield and households for scattered years | Partial for area and trees. |
| `indonesia_bps.csv` | BPS Statistik Indonesia 2026 | area_total and production 2024–2025 national; 2021–2025 split by ownership (PR vs PBN+PBS), in `1000_ha` and `1000_t` as published | Partial. |
| `indonesia_kementan.csv` | Kementan / Ditjenbun | header only | **Blocked** |
| `ethiopia_ess.csv` | ESS/CSA Meher reports, ECTA | header only | **Blocked** |

`raw/<source>/` holds the downloaded source files, each at most 25 MB. Four UCDA annual reports are larger:
2017/18, 2019/20, 2021/22 and 2022/23. They are not in `raw/`, and their URLs are in `notes_uganda_ucda.md`.

## Network reachability (curl through the session proxy, 2026-09-26)

- **Reachable:**
  - www.fao.org and bulks-faostat.fao.org (the FAOSTAT bulk zip)
  - www.gob.pe and cdn.www.gob.pe (MIDAGRI and INEI files)
  - ugandacoffee.go.ug and www.agriculture.go.ug
  - www.gob.mx/cms/uploads/... (file downloads; the HTML pages need a JS challenge, so a headless Chromium was used to list links)
  - webapi.bps.go.id/download.php?f=<token> (only with a token found through web search)
- **Blocked or failing:**
  - fenixservices.fao.org (the FAOSTAT API timed out, so the bulk file was used instead)
  - Mexico: infosiap.siap.gob.mx, nube.siap.gob.mx (502), www/siap.gob.mx, nube.agricultura.gob.mx, datos.gob.mx (403), fira.gob.mx, inegi
  - Indonesia: satudata.pertanian.go.id, ditjenbun.pertanian.go.id and www.bps.go.id (Cloudflare 403); www.pertanian.go.id; web-api.bps.go.id
  - Peru: siea.midagri.gob.pe (connection dropped, 503 over http), www.midagri.gob.pe, www.inei.gob.pe
  - Ethiopia: www.ess.gov.et ("Host not in allowlist" from the egress proxy), statsethiopia.gov.et and ecta.gov.et (502)
  - Uganda: www.new.ugandacoffee.go.ug, www.ubos.org
  - Other: apps.fas.usda.gov, ico.org, web.archive.org, worldbank/microdata, HDX

## Key caveats

- **FAOSTAT** values are green coffee on a calendar-year basis. Many area figures are imputed (flag I) or estimated (flag E), so check the flag in notes before using them as "official".
- **Mexico** production is **café cereza (cherry)**, not green. Crop year "2021/22" is SIAP "ciclo 2022" (Oct 2021–Sep 2022). Values for recent years are cierre preliminar. The FIRA 2016 annex contradicts itself for 2010/11 and 2011/12; the summary table was used, and the alternatives are in notes. There is no superficie siniestrada.
- **Peru** production is **café pergamino (parchment)**. Area for 2017 and 2018 comes from later INEI revisions (383,118 and 432,409 ha), while the published yields for those years use the earlier yearbook areas (424,129 and 447,426 ha). Production differs between editions for 2015, 2016, 2021 and 2023; the latest edition was kept and the others are in notes. MIDAGRI publishes no installed or bearing area series, only "460 mil ha installed in 2022" in the text of note 014-2023, which is left out of the CSV.
- **Uganda** production has two breaks:
  - It is by coffee year (Oct–Sep) up to 2014/15 and by fiscal year (Jul–Jun) from 2015/16.
  - Up to 2017/18 it measures **procurement** (deliveries to export graders). From 2018/19 it is a total estimate, e.g. 7.05 M bags in 2018/19 against 4.94 M procured.

  Area concepts vary by year (gross, net of Coffee Wilt Disease, etc.; see notes). The tree figures are one undated fact-sheet snapshot assigned to 2021/22, which is approximate.
- **Indonesia** production is kopi biji kering (green-bean basis), all species. 2025 is preliminary. The national total for 2021–2023 is not given directly and was not derived. Rows whose notes start with "SUBSET ONLY" are ownership subsets, not national totals.

## Gaps and how to fill them

- **Ethiopia:** everything is missing. To fill it, allowlist ess.gov.et, www.ess.gov.et and www.statsethiopia.gov.et, then take the coffee row from the permanent-crops table of each Meher Volume I report. The known PDF URLs for 2010–2014 E.C. are in `notes_ethiopia_ess.md`.
- **Indonesia:** there is no TBM/TM/TTM split, yield, holders or pre-2021 data. To fill it, get a free BPS WebAPI key (for Statistik Kopi Indonesia), use Ditjenbun "Statistik Perkebunan Unggulan Nasional" downloaded manually, or allowlist the hosts.
- **Mexico:** 1998–2003/04 is missing, areas are missing for 2016/17–2018/19, and there is nothing after 2023/24 and no siniestrada. Replace the series with the official SIAP cierre open data once nube.agricultura.gob.mx or infosiap is reachable.
- **Peru:** 1998–1999 is missing, area and yield are missing for 2000–2009, and there is no 2025 area. The historical series on siea.midagri.gob.pe is blocked.
- **Uganda:** there is no area time series, no trees series, no robusta/arabica split after 2019/20, and no UBOS data.

## Tools

- `tools/pdftext.py` is a stdlib PDF text extractor.
- `tools/pdftext2.py` is the same with decryption, for BPS PDFs.
- `tools/pdfimages.py` extracts images embedded in a PDF.
- `tools/xls_biff.py` reads old .xls (BIFF) files.
- `raw/mexico_siap/forms.py` and `raw/mexico_siap/decrypt.py` are helpers for the SIAP Escenario form tables and the encrypted Planeación PDF.
