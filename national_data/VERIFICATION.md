# Verification of the national data (26 Sep 2026)

Before the data went into `Balance_Sheet_weather_MI` (version 2), every value in the CSVs was checked against
the downloaded source files in `raw/`. `tools/verify_sources.py` repeats the automatic part: it compares FAOSTAT
value by value and searches every other value in the text of its source files. The values it cannot match were
checked by hand. Small numbers (yields, households) were also checked on their cited pages, because an automatic
match can be a coincidence:

| File | Result | Values checked by hand |
|---|---|---|
| `faostat.csv` | 405/405 values and flags identical to `raw/faostat/` | none |
| `mexico_siap.csv` | 69/69 | 3 values. 2015/16 production 824.08 kt and planted area 730,011 ha are in the decrypted Planeación PDF (`raw/mexico_siap/decrypt.py`). 2020/21 yield 1.48 t/ha is in the Escenario Oct-2022 text ("1.4 8 ton/ha en el ciclo 2021"). 2023/24 harvested area is in the Escenario Jul-2024 text ("660 mil 167"). |
| `peru_midagri.csv` | 55/55 | All 55 are found by `tools/verify_sources.py` (text or spreadsheet cells). Also checked by hand: production 2000–2025 equals *El Agro en Cifras* Dec-2025, table C.7, cell by cell; areas and yields 2010–2024 are in INEI cuadro 13.7 (editions 2021, 2023, 2025) or in the compendio sheets; yields 2015–2018 are the compendio values rounded (C.147 0.664251 and 0.723386; Cuadro 372 795.348 and 826.108). |
| `uganda_ucda.csv` | 93/103 | Found automatically or on the cited pages: production 1998/99–2016/17, 2019/20 (Coffee Sub-Sector Strategy, table 4) and 2020/21–2024/25 (MAAIF Statistical Abstract 2024, table 11). The 2017/18 total (4.71 million bags, AR 2018/19 p.33) and 2018/19 total (7.05 million, AR 2020/21 p.13) were found in rounded form. Also found: areas 2000/01–2020/21, trees (saved fact sheet), yields per tree 2014/15, 2019/20 (strategy table 4) and 2020/21 (AR 2020/21 p.13), yields per ha, and households up to 2020/21. **Not re-checkable (10 rows)**, because their source reports (UCDA AR 2017/18, 2021/22, 2022/23; 33–43 MB) are not archived: the 2017/18 robusta/arabica split (its sum equals the 4.71 million total), areas 2021/22–2022/23 (589.1 and 609.8 thousand ha), yields per tree 2021/22–2022/23, and households 2021/22–2022/23. The automatic check reports 97/103, but some small numbers only matched by coincidence elsewhere, so the count above comes from the page-by-page review. |
| `indonesia_bps.csv` | 24/24 | All 24 are on the cited pages of Statistik Indonesia 2026 (pp. 428, 431, 434–437). |

## Year mapping to the USDA marketing years (checked on the data)

- **FAOSTAT Mexico.** FAO year Y is SIAP ciclo Y (Oct Y-1 to Sep Y), so it goes to MY (Y-1)/Y. FAO harvested area equals SIAP harvested area in 13 of the 17 cycles that have both. The other four are 2012/13, 2015/16, 2022/23 and 2023/24, where SIAP's value is preliminary or from another edition. FAO green production equals SIAP cherry production × 0.1841, except 2012/13, where FAO used the SIAP state-table total of 1,257,983 t.
- **FAOSTAT Uganda.** FAO year Y is UCDA fiscal year (Y-1)/Y, so it goes to MY (Y-1)/Y. FAO 2022 is 507,000 t = 8.45 M bags (FY2021/22), and FAO 2023 is 468,000 t = 7.8 M bags (FY2022/23).
- **Calendar-year data** (FAOSTAT Peru, Indonesia and Ethiopia; MIDAGRI; BPS): year Y goes to MY Y/(Y+1).
  - The Indonesia BPS rows already in the workbook follow this convention. They equal FAO (Ditjenbun data) within 1%, except area in 2010, 2011 and 2016 and production in 2016.

## Use in the workbook

Each country tab has an "Official national & FAO data" block below the notes:
- For every country: FAO area, production and yield, the FAO flags, and USDA-vs-FAO differences.
- Mexico: SIAP series.
- Peru: MIDAGRI series, plus a green equivalent at parchment × 0.8 (ICO factor).
- Uganda: UCDA series.

Other changes:
- **Mexico:** the USDA area gap 2013/14–2022/23 is filled in rows 3 and 5 in blue italics, from SIAP. Harvested area for 2016/17–2018/19 comes from FAO, which republishes SIAP data.
- **Indonesia:** BPS 2024–2025 was appended to the user's BPS rows 32–33.
- **Ethiopia:** no national data could be downloaded (ESS/CSA and ECTA are blocked).
