# Workstream C: coffee consumption in importing countries, 2005 to 2026

Compiled 2026-09-24 for the coffee-demand research pack.
Data file: `research/coffee-demand/data/raw/C_importers.csv` (1,812 rows; schema in `data/raw/SCHEMA.md`).

## 0. Read this first: where the numbers come from

**Web search stopped early.** The session-wide WebSearch cap (200 calls shared with the other workstreams) ran out after about 33 of my queries. Web-search results supplied only the newest USDA figures (the December 2025 report and the June 2026 edition, released 22 July 2026) and a few GAIN, ECF and press items. The long history comes from public GitHub copies of official datasets, fetched with `git clone`. Each CSV row links to the exact file, pinned to a commit:

| Source used | What it gives | Vintage | CSV datasets |
|---|---|---|---|
| USDA PSD bulk file `psd_coffee.csv` ([GitHub copy](https://github.com/Mal303/Interactive-Coffee-Bean-Origin-Map/blob/a1577e64b4a2a0a5a6fdab415ea8fb7ae0bdb118/homepage_css/Data/CoffeeDataRaw/Coffee_Data/psd_coffee.csv)), plus PSD Online tables "Table 04 Coffee Consumption" and "Coffee Summary Continued" | Domestic consumption, bean imports and total imports for all 18 countries/blocs, MY 2005/06 to 2024/25F | **June 2024 release.** The latest update stamp in the file is 2024-06. Its world total for 2024/25 (170,634) matches Comunicaffe's report of the USDA June 2024 figure (170.634M). | `consumption_usda`, `imports_green_usda`, `imports_total_gbe_usda`, `ending_stocks_usda`, `exports_roast_ground_usda` |
| Older USDA PSD extract ([GitHub copy](https://github.com/Abood991B/tableau-coffee-market-analysis/blob/3b2951257f38b388df47510914fd7534d93f9bb3/data/psd_coffee.csv)) | Used only to show how much USDA revised figures | Before June 2024 (probably December 2023) | `consumption_usda_prior_vintage` (superseded) |
| ICO historical data, 1990 to 2019 (Kaggle "Coffee dataset" [copy](https://github.com/dryzrlbs/coffeedata/blob/b012ab8b3d077ce144e9efa7e8d7f0e9f06dbd03/Coffee_importers_consumption.csv); stored in kg, divided by 60,000 to get thousand bags) | Consumption ("disappearance") and gross imports of ICO importing members: 27 EU countries, UK, US, Japan, Russia, Switzerland, Norway, Tunisia | Calendar years 2005 to 2019 | `consumption_ico`, `imports_total_gbe_ico` |
| UN Comtrade monthly extracts ([GitHub copy](https://github.com/Tatiana-ZC/Final.Project_Coffee/tree/ed009d18642877701e94dcf6b43c317a608d3f22/source/datasets/UN_Comtrade_All_Datasets)) | Green coffee imports (HS 090111 + 090112, all partners). US, Japan, Switzerland, Germany, Italy, Spain, Netherlands, Belgium, Poland | Calendar years 2017 to 2023. Each year is the sum of 12 monthly records. Partial 2024 data looked incomplete and was not used. | `imports_green_comtrade` |
| World Bank population (SP.POP.TOTL) ([GitHub copy](https://github.com/datasets/population/blob/075cd0da5b7268daa466c84b3b2ff109bf3aea7e/data/population.csv)) | Denominator for per-capita figures | 1960 to 2024 | `per_capita_kg_derived_*` |
| Web search: USDA FAS reports, GAIN, ECF, Comunicaffe, Food Business MEA, Daily Coffee News | USDA figures for 2024/25 to 2026/27, and qualitative drivers | December 2025 and July 2026 | Rows with source_org "USDA FAS (via ...)", GAIN, ECF |

**Blocked newer data.** A USDA PSD bulk download dated 2026-06-21 sits in the public repo `andenick/Foodberg` (`Outputs/Data/WASDE_PSD/wasde_psd_full.parquet`; see its PROVENANCE.md). It would supply December 2025 vintage levels for 2024/25 and 2025/26 for every country. Reading it needed a freshly installed parquet library, and the session's permission check refused that (reason: "Code from External"). I did not work around the refusal. If you allow it, that file fills most of the 2024/25 to 2025/26 gaps below.

**Confidence levels.**
- `medium`: official data taken from a mirror copy, or trade press quoting USDA.
- `high`: only the June 2020 USDA PDF rows read directly from fas.usda.gov.
- `low`: summary attribution was unclear, the data is superseded, or the aggregator is not official.

**Derived rows.** Rows computed by me (sums, EU-28 equivalents, per-capita) are labelled `derived` in the dataset name or notes. Nothing was interpolated.

## 1. Conventions

- **USDA periods.** Marketing-year labels as used by USDA (for example 2023/24). The PSD `Market_Year` value 2023 means 2023/24. The file does not define each country's local marketing-year months, so I did not assume Oct–Sep. The ICO coffee year runs Oct–Sep, but the ICO series used here is calendar-year.
- **EU coverage.** In the PSD, "European Union" **includes the UK up to 2015/16 (EU-28) and excludes it from 2016/17 (EU-27)**, when a separate UK series begins. The data show this break: EU consumption falls 44,095 → 39,045 in 2016/17 while UK = 4,260; EU bean imports fall 46,150 → 43,425 while UK = 2,650. For like-for-like comparisons use `consumption_usda_eu28_equiv_derived` (EU + UK).
  - The June 2020 USDA figure for EU imports (49.5M bags forecast for 2020/21, implying 47.5M in 2019/20) is evidently EU-28: PSD EU-27 + UK for 2019/20 is 47.1M.
  - The December 2025 and July 2026 figures are EU-27.
- **Units.** Thousand or million 60-kg bags in green-bean equivalent (GBE). Comtrade figures are in tonnes of green coffee.
- **Imports: gross vs net.** ICO and Comtrade figures for EU members are gross and include intra-EU trade, so they must not be summed across members. ICO *consumption* can be summed.
- **Residual caveat.** USDA importer "domestic consumption" is a balance-sheet residual: imports minus re-exports minus stock change. It swings with stocks. Example: EU ending stocks fell from 14.0M (2021/22) to 9.3M bags (2022/23), and in that year EU "consumption" jumped to 44.5M before falling back to 41.6M. Read trends from multi-year averages, not single years.

## 2. Consumption by country (USDA PSD, thousand 60-kg bags; June 2024 vintage unless stated)

The CAGR column compares the 3-year average for 2005/06–2007/08 with the 3-year average for 2021/22–2023/24, a 16-year gap. The EU-28-equivalent row adds the PSD EU and UK series from 2016/17 onward.

| Entity | 2005/06 | 2010/11 | 2015/16 | 2019/20 | 2020/21 | 2021/22 | 2022/23 | 2023/24 | 2024/25F (Jun-24) | Later USDA vintages | CAGR 3y-avg 05-07 to 21-23 | Trend |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| European Union | 43,675 | 41,350 | 44,095 | 40,264 | 41,271 | 41,867 | 44,482 | 41,613 | 41,800 | 41,870 (2025/26, Dec-25); 42,500 (2026/27F, Jul-26) | see EU-28 equiv. | steady (series break 2016/17: EU-28 -> EU-27) |
| EU-28 equiv. | 43,675 | 41,350 | 44,095 | 44,069 | 44,226 | 45,852 | 48,462 | 45,588 | 45,850 | n/a | +0.6%/yr | growing |
| United States | 22,066 | 22,383 | 25,083 | 26,049 | 25,922 | 26,723 | 24,623 | 25,125 | 26,050 | 26,950 (2026/27F, Jul-26) | +1.0%/yr | growing |
| Japan | 7,275 | 7,015 | 8,060 | 7,610 | 7,354 | 7,210 | 6,886 | 7,300 | 7,300 | +3.7% y/y (2026/27F, Jul-26) | -0.1%/yr | steady |
| Russia | 3,585 | 4,355 | 4,395 | 4,625 | 4,165 | 4,055 | 4,250 | 4,250 | 4,250 | n/a | +0.3%/yr | steady |
| Canada | 3,205 | 4,245 | 4,545 | 4,830 | 4,995 | 5,330 | 5,110 | 4,920 | 5,200 | n/a | +2.3%/yr | growing |
| United Kingdom | - | - | - | 3,805 | 2,955 | 3,985 | 3,980 | 3,975 | 4,050 | n/a | - | n/a (series from 2016/17) |
| Switzerland | 900 | 1,060 | 1,095 | 1,055 | 1,180 | 1,185 | 1,160 | 1,020 | 1,100 | n/a | +1.1%/yr | growing |
| South Korea | 1,455 | 1,910 | 2,465 | 2,980 | 2,995 | 3,405 | 3,175 | 3,160 | 3,275 | n/a | +4.9%/yr | growing fast |
| China | 198 | 1,109 | 3,455 | 3,800 | 4,600 | 5,000 | 5,400 | 5,800 | 6,200 | 6,750 (2026/27F, Jul-26) | +22.7%/yr | growing fast |
| Australia | 1,130 | 1,445 | 1,785 | 1,960 | 2,055 | 2,305 | 2,135 | 2,150 | 2,200 | n/a | +4.0%/yr | growing fast |
| Algeria | 2,085 | 1,815 | 2,320 | 2,040 | 2,240 | 2,090 | 2,050 | 1,950 | 1,950 | n/a | +0.1%/yr | steady |
| Saudi Arabia | 545 | 565 | 785 | 1,040 | 1,200 | 1,140 | 1,380 | 1,300 | 1,350 | n/a | +5.2%/yr | growing fast |
| Turkey | 200 | 340 | 710 | 1,215 | 1,165 | 1,285 | 1,590 | 1,605 | 1,625 | n/a | +12.4%/yr | growing fast |
| Egypt | 80 | 250 | 525 | 750 | 400 | 450 | 350 | 400 | 425 | n/a | +6.9%/yr | volatile: peaked 2018/19, roughly halved since |
| Ukraine | 1,630 | 1,685 | 970 | 1,270 | 1,235 | 1,300 | 1,080 | 1,060 | 1,120 | n/a | -3.3%/yr | declining (fell 2008-2016, flat since) |
| Morocco | 530 | 555 | 670 | 710 | 880 | 990 | 805 | 795 | 775 | n/a | +2.7%/yr | growing |
| Taiwan | 175 | 305 | 535 | 690 | 660 | 695 | 690 | 710 | 720 | n/a | +8.1%/yr | growing fast |
| Norway | 695 | 795 | 785 | 795 | 815 | 750 | 725 | 765 | 795 | n/a | +0.1%/yr | steady |

**Cross-check with ICO (calendar years, thousand bags).** ICO shows the same broad picture to 2019. Two gaps between the sources are worth noting:
- The US grew faster in ICO (+30% from 2005 to 2019) than in USDA (+18% from 2005/06 to 2019/20).
- For Russia, ICO shows +51%. The USDA series is flatter, and USDA holds Russia at 4,250 for three years in a row (2022/23 to 2024/25).

| Entity (ICO consumption, 1000 bags, calendar yr) | 2005 | 2010 | 2015 | 2018 | 2019 | change 2005-2019 |
|---|---|---|---|---|---|---|
| EU-28 (EU-27 + UK, ICO sum) | 39,875 | 41,196 | 41,799 | 45,132 | 45,032 | +13% |
| EU-27 (ICO members sum) | 37,195 | 38,062 | 38,208 | 41,344 | 41,262 | +11% |
| United States | 20,998 | 21,783 | 24,438 | 26,514 | 27,310 | +30% |
| Germany | 8,665 | 9,292 | 8,421 | 8,461 | 8,670 | +0% |
| Japan | 7,128 | 7,192 | 7,695 | 7,834 | 7,551 | +6% |
| Italy | 5,552 | 5,781 | 5,660 | 5,955 | 5,469 | -1% |
| France | 4,787 | 5,713 | 5,591 | 5,986 | 6,192 | +29% |
| Russia | 3,185 | 3,700 | 3,846 | 4,234 | 4,820 | +51% |
| United Kingdom | 2,680 | 3,134 | 3,591 | 3,788 | 3,770 | +41% |
| Spain | 3,007 | 3,232 | 3,524 | 3,095 | 3,253 | +8% |
| Poland | 2,267 | 2,156 | 1,420 | 2,436 | 2,501 | +10% |
| Netherlands | 1,927 | 1,347 | 1,696 | 2,145 | 2,030 | +5% |
| Sweden | 1,170 | 1,221 | 1,623 | 1,683 | 1,769 | +51% |
| Finland | 1,102 | 1,080 | 1,110 | 1,106 | 1,348 | +22% |
| Switzerland | 1,099 | 1,012 | 1,096 | 1,170 | 1,073 | -2% |
| Denmark | 795 | 806 | 731 | 739 | 778 | -2% |
| Norway | 743 | 746 | 788 | 734 | 771 | +4% |

## 3. Rankings: largest consumers and fastest growth

- **Largest bloc: the EU.**
  - USDA EU-27: 41.6M bags in 2023/24, 24.8% of world consumption (167.5M). The US was 25.1M (15.0%), so the EU is about **1.66× the US**.
  - Latest official figures: EU 41.87M for 2025/26 (USDA December 2025). The July 2026 forecast for 2026/27 is **EU 42.5M against US 26.95M** (1.58×; shares of the 179.7M world total: 23.6% and 15.0%).
  - The ECF, citing USDA, puts the EU at about 24% of world consumption in 2025/26.
  - Adding back the UK (EU-28 equivalent) gives 45.6M in 2023/24.
- **Largest single country: the United States.**
  - 25.1M bags in 2023/24 and 26.05M forecast for 2024/25 (June 2024), ahead of Brazil (22.6M, a producer).
  - After them come Japan (7.3M), the Philippines (6.95M), China (5.8M), Canada (4.9M), Russia (4.25M), the UK (3.98M) and South Korea (3.16M).
  - If EU members are counted separately, Germany (ICO 2019: 8.67M bags) ranks above Japan.
  - Vivid Maps (low confidence) also names the US as the largest market in 2023 (1,431 thousand tonnes).
- **Fastest growth.**
  - Rate: **China**, +22.7% a year on 3-year averages. Volume rose from 0.2M to 5.8M bags in 2023/24; USDA forecasts 6.75M for 2026/27 (+5.1%). Next come Turkey (+12.4%/yr), Taiwan (+8.1%), Saudi Arabia (+5.2%), South Korea (+4.9%) and Australia (+4.0%).
  - Absolute bags added (3-year averages, 2005–07 to 2021–23): China +5.2M, EU-28 equivalent +4.0M, US +3.6M, South Korea +1.7M, Canada +1.6M, Turkey +1.3M.
  - For 2026/27, USDA's growth rates among the big markets are US +5.7%, China +5.1%, Japan +3.7% and EU +2.2%.
- **Flat or declining.**
  - Flat: Japan (−0.1%/yr), Russia on USDA figures (+0.3%), Algeria (+0.1%) and Norway (+0.1%).
  - Declining: Ukraine (−3.3%/yr).
  - Volatile: Egypt, which peaked at 825 thousand bags in 2018/19 and has run at 350–450 since.

## 4. Imports and signs of a slowdown under record prices (2023 to 2026)

USDA green-bean imports, thousand 60-kg bags (June 2024 vintage), with later revisions:

| Entity | 2019/20 | 2020/21 | 2021/22 | 2022/23 | 2023/24 | 2024/25F (Jun-24) | Later USDA vintages |
|---|---|---|---|---|---|---|---|
| European Union | 44,460 | 43,875 | 46,600 | 44,490 | 45,500 | 47,500 | 46.2M (2024/25, Dec-25 rev. +0.8M "on higher consumption"); 47.0M (2025/26F, Dec-25) -> 46.5M (Jul-26 rev. -0.5M "on lower consumption") |
| United States | 23,900 | 24,320 | 25,225 | 22,540 | 23,600 | 24,500 | 23.4M (2024/25, Dec-25 rev. +0.6M); 23.1M (2025/26, Jul-26 rev. -0.7M "on lower consumption") |
| Japan | 6,550 | 6,520 | 6,800 | 5,860 | 6,160 | 6,500 | n/a |
| China | 900 | 1,675 | 1,665 | 1,965 | 3,200 | 3,000 | 3.6M (2024/25F per GAIN Jan-26, low conf.) |
| South Korea | 2,660 | 2,635 | 3,015 | 2,820 | 2,800 | 2,900 | n/a |
| Russia | 3,180 | 3,390 | 3,400 | 3,500 | 3,500 | 3,500 | n/a |
| Canada | 2,835 | 2,860 | 2,940 | 2,700 | 2,700 | 2,900 | n/a |
| United Kingdom | 2,640 | 2,270 | 2,725 | 2,285 | 2,375 | 2,450 | n/a |
| Switzerland | 3,030 | 3,450 | 3,400 | 3,290 | 3,220 | 3,300 | n/a |
| World | 110,603 | 112,102 | 118,478 | 111,790 | 115,646 | 119,382 | 118.6M (2025/26, Jul-26 rev. -1.3M) |

**UN Comtrade green-coffee imports (HS 090111 + 090112; thousand tonnes; calendar years):**

| Reporter | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2023 vs 2022 | 2023 vs 2019 |
|---|---|---|---|---|---|---|---|---|---|
| United States | 1,531 | 1,493 | 1,592 | 1,337 | 1,362 | 1,493 | 1,276 | -14.5% | -19.9% |
| Japan | 406 | 401 | 437 | 392 | 402 | 390 | 356 | -8.8% | -18.5% |
| Germany | 1,042 | 1,084 | 1,091 | 1,081 | 1,073 | 1,101 | 915 | -16.9% | -16.1% |
| Italy | 518 | 552 | 615 | 569 | 621 | 675 | 646 | -4.3% | +5.0% |
| Spain | 274 | 289 | 300 | 317 | n/a (11 months) | 295 | 269 | -8.9% | -10.6% |
| Netherlands | 190 | 202 | 205 | 188 | 190 | 239 | 196 | -18.1% | -4.2% |
| Belgium | 94 | 132 | 149 | 146 | 137 | 135 | 124 | -7.9% | -16.8% |
| Poland | 114 | 123 | 123 | 129 | 130 | 120 | 123 | +2.0% | -0.5% |
| Switzerland | 143 | 156 | 175 | 177 | 205 | 211 | 177 | -16.3% | +0.7% |

What the evidence shows:
1. **Calendar 2023 was a weak import year.**
   - Falls from 2022: US −14.5%, Germany −16.9%, Japan −8.8%, Switzerland −16.3%, Netherlands −18.1% (Comtrade).
   - USDA MY 2022/23 agrees: EU bean imports 44.5M (down from 46.6M), US 22.5M (from 25.2M), Japan 5.9M (from 6.8M). In the same year EU ending stocks fell by 4.7M bags, so importers drew on stocks rather than buying.
2. **2024/25 was revised up.** USDA's December 2025 report raised 2024/25 bean imports: EU +0.8M to 46.2M and US +0.6M to 23.4M, both "on higher consumption".
3. **2025/26 is the first official sign of demand cutback.**
   - The July 2026 report cut 2025/26 EU imports by 0.5M to 46.5M and US imports by 0.7M to 23.1M, both "on lower consumption". World bean imports were cut 1.3M to 118.6M.
   - The period is inferred: the December 2025 table forecast EU 2025/26 at 47.0M, and 47.0 − 0.5 = 46.5.
   - Consistent with this, the EU consumption level implied for 2025/26 by the July 2026 +2.2% growth rate is about 41.6M, slightly below the December figure of 41.87M.
4. **USDA expects a rebound in 2026/27** alongside a record crop of 189.667M bags: US +5.7% to 26.95M, EU +2.2% to 42.5M, China +5.1% to 6.75M, Japan +3.7%.
5. **China is the exception.** Its bean imports rose from 0.9M (2019/20) to 3.2M (2023/24), and total imports from 2.9M to 5.2M bags. A January 2026 GAIN report (low confidence) cites about 3.6M green and 5.6M total for 2024/25.
6. **Not obtained (search budget exhausted):**
   - 2024, 2025 and 2026 year-to-date imports from customs or national sources for Japan (MOF/AJCA), China (GACC), Korea (KCS/KITA), Russia and the EU (Eurostat).
   - Any published statement of the form "EU imports fell X% in 2024/25".

## 5. Per-capita consumption (kg green-bean equivalent per person per year)

Most per-capita figures here are **derived by me**: USDA or ICO volume × 60 kg, divided by World Bank population. They are not published figures.
- The EU row uses EU-27 + UK population through 2015/16 and EU-27 population from 2019/20, to match the PSD series break.
- Single years carry the residual noise described in section 1.

From USDA PSD:

| Entity | 2005/06 | 2010/11 | 2015/16 | 2019/20 | 2023/24 |
|---|---|---|---|---|---|
| Norway | 9.02 | 9.76 | 9.08 | 8.92 | 8.32 |
| Canada | 5.96 | 7.49 | 7.64 | 7.70 | 7.36 |
| Switzerland | 7.26 | 8.13 | 7.93 | 7.38 | 6.89 |
| European Union | 5.28 | 4.91 | 5.20 | 5.41 | 5.56 |
| Australia | 3.36 | 3.94 | 4.50 | 4.64 | 4.84 |
| United States | 4.48 | 4.34 | 4.68 | 4.73 | 4.48 |
| South Korea | 1.81 | 2.31 | 2.90 | 3.45 | 3.67 |
| Japan | 3.42 | 3.29 | 3.80 | 3.61 | 3.52 |
| United Kingdom | - | - | - | 3.43 | 3.48 |
| Algeria | 3.78 | 3.01 | 3.48 | 2.83 | 2.53 |
| Saudi Arabia | 1.59 | 1.41 | 1.58 | 2.08 | 2.31 |
| Russia | 1.50 | 1.83 | 1.82 | 1.91 | 1.77 |
| Ukraine | 2.06 | 2.18 | 1.27 | 1.69 | 1.69 |
| Morocco | 1.05 | 1.03 | 1.16 | 1.18 | 1.26 |
| Turkey | 0.17 | 0.28 | 0.54 | 0.88 | 1.13 |
| China | 0.01 | 0.05 | 0.15 | 0.16 | 0.25 |
| Egypt | 0.06 | 0.17 | 0.32 | 0.42 | 0.21 |

From ICO data (calendar years). This shows the Nordic and EU-member detail that USDA does not have:

| Entity (ICO, calendar yr) | 2005 | 2010 | 2015 | 2019 |
|---|---|---|---|---|
| Finland | 12.60 | 12.08 | 12.15 | 14.65 |
| Sweden | 7.77 | 7.81 | 9.94 | 10.33 |
| Norway | 9.64 | 9.15 | 9.11 | 8.65 |
| Denmark | 8.80 | 8.72 | 7.72 | 8.03 |
| Switzerland | 8.87 | 7.76 | 7.94 | 7.51 |
| Germany | 6.30 | 6.82 | 6.19 | 6.26 |
| EU-27 (ICO members sum) | 5.12 | 5.17 | 5.17 | 5.54 |
| France | 4.55 | 5.27 | 5.04 | 5.51 |
| Italy | 5.73 | 5.80 | 5.64 | 5.49 |
| United States | 4.26 | 4.22 | 4.56 | 4.96 |
| Spain | 4.13 | 4.16 | 4.55 | 4.14 |
| Japan | 3.35 | 3.37 | 3.63 | 3.58 |
| United Kingdom | 2.66 | 3.00 | 3.31 | 3.39 |
| Russia | 1.33 | 1.55 | 1.60 | 1.99 |

Published per-capita figures that were found:
- South Korea: **416 cups per person in 2024** (USDA GAIN, Seoul, low confidence on which report) and 341 cups per adult in 2014, +23.1% since 2009 (GAIN 2015).
- EU: 5.7 kg per person (Vivid Maps, low confidence). This agrees with the derived USDA-based EU-27 figure of 5.56 kg for 2023/24.

Not found: ECF European Coffee Report per-capita tables, ICO published per-capita figures, and AJCA per-capita figures (see section 7).

Highlights:
- Finland is the highest per-capita consumer (14.7 kg in 2019 on ICO data). Other Nordic countries run at 8–10 kg.
- Canada (about 7.4 kg) and Switzerland (6.9–7.5 kg) are above the EU average (about 5.5 kg). The US (about 4.5–5.0 kg) and Japan (about 3.5 kg) are below it.
- South Korea has doubled, from 1.8 to 3.7 kg.
- China, at about 0.25 kg, is still more than 10× below Japan or Korea, so it has the most room to grow.

## 6. Country notes

Where no source for the reasons behind a trend was retrieved, the note says so. I have not filled those gaps from memory.

- **European Union: steady (EU-27 about 41–42M bags). The largest bloc.**
  - The EU-28-equivalent series rose only about 0.6% a year, from 43.7M (2005/06) to 45.6M (2023/24).
  - ICO EU-27: +11% from 2005 to 2019.
  - The ECF describes EU volumes as "broadly stable since 2020 at around 1.9 million tonnes per year". For 2025 it splits EU+ consumption into about 1.49 Mt retail and 0.43 Mt foodservice (low confidence on attribution) ([ECF](https://www.ecf-coffee.org/wp-content/uploads/2026/06/ECF_Economic-Impact-of-Coffee-in-Europe.pdf), [Daily Coffee News](https://dailycoffeenews.com/2026/07/08/coffee-generates-e84-4-billion-in-direct-value-across-the-eu-report-says/)).
  - Largest members on ICO 2019 data: Germany 8.67M bags (flat since 2005), France 6.19M (+29%), Italy 5.47M (flat), Spain 3.25M, Poland 2.50M.
  - Latest USDA: 41.87M for 2025/26 (December 2025), about 41.6M implied by the July 2026 report, and 42.5M forecast for 2026/27 ([Comunicaffe](https://www.comunicaffe.com/usda-world-coffee-production-6-exports-9-and-global-consumption-3-6-set-to-reach-record-levels-in-2026-27)).
  - Imports: the 2025/26 cut "on lower consumption" and the 2023 fall in German imports (−17%) are the main softness signals.
- **United States: growing about 1% a year. The largest single country.**
  - USDA: 22.1M (2005/06) to 25.1M (2023/24), with a 27.2M peak in 2018/19. ICO: 21.0M (2005) to 27.3M (2019).
  - USDA cut 2025/26 bean imports to 23.1M "on lower consumption", then forecast 26.95M consumption for 2026/27 (+5.7%).
  - Comtrade green imports were 1.28 Mt in 2023, −14.5% on 2022.
  - Drivers (retail vs out-of-home, prices, tariffs) were not researched because the search budget ran out. The NCA's National Coffee Data Trends were not retrieved.
- **Japan: flat, with a plateau and dip.**
  - USDA: 7.3M (2005/06), rising to 8.2M (2016/17–2017/18), falling to 6.9M (2022/23), then 7.3M (2023/24 and 2024/25F). USDA forecasts +3.7% for 2026/27.
  - ICO: 7.1M (2005) to 7.9M (2016) to 7.55M (2019).
  - Drivers from GAIN: coffee demand was boosted by high-quality convenience-store coffee from 2015, and coffee has risen while green tea declined. The same GAIN reports over 400,000 t of bean imports in 2018 ([GAIN 2020](https://apps.fas.usda.gov/newgainapi/api/Report/DownloadReportByFileName?fileName=USJTA+Treatment+for+Coffee+Tea+and+Spices_Tokyo_Japan_02-29-2020)); Comtrade shows 401 kt.
  - Comtrade green imports fell 18.5% from 2019 to 2023.
  - Gap: the AJCA "total domestic demand" series in tonnes was not retrieved.
- **China: the fastest-growing market.**
  - USDA: 0.2M (2005/06) to 1.1M (2010/11) to 3.8M (2019/20) to 5.8M (2023/24), 6.2M forecast for 2024/25 and 6.75M for 2026/27. China is now 5th among single-country consumers in the USDA table.
  - The January 2026 GAIN report estimates the 2024 market at $42bn with consumption "exceeding 240,000 metric tons", up about 150% in a decade, and expects about 15% a year growth ([GAIN](https://www.fas.usda.gov/data/gain/2026/01/china-brewing-momentum-chinas-coffee-market-and-emerging-opportunities-us-exporters)). The tonnage basis differs from USDA's PSD figure.
  - The June 2024 PSD revised China up (for example 2023/24 from 5,000 to 5,800) and kept revising it upward, so expect more revisions.
- **South Korea: growing fast, but plateauing since 2021/22.**
  - USDA: 1.46M to 3.41M (2021/22), then 3.16–3.28M. Derived per-capita rose from 1.8 to 3.7 kg.
  - GAIN: per-capita consumption is five times the rest of Asia-Pacific. There were about 12,000 specialty coffee shops in 2014, up 140% since 2009. Consumption reached 416 cups per person in 2024 ([GAIN 2015](https://apps.fas.usda.gov/newgainapi/api/report/downloadreportbyfilename?filename=Coffee+Market+Brief+Update_Seoul+ATO_Korea+-+Republic+of_12-31-2015.pdf)).
  - Total coffee imports were 134,000 t in 2014 (+17%).
- **Russia: modest growth.**
  - USDA: 3.6M to 4.3–4.9M, held flat at 4.25M for 2022/23 to 2024/25. ICO: 3.2M (2005) to 4.8M (2019), +51%.
  - Rusteacoffee import data were not retrieved, and post-2022 drivers are unsourced.
- **Canada: growing about 2.3% a year.** 3.2M to 4.9–5.3M bags. Per-capita about 7.4 kg, among the highest outside the Nordics and Switzerland.
- **United Kingdom: growing.** ICO: 2.68M (2005) to 3.77M (2019), +41%. The USDA series (from 2016/17) is 3.8–4.05M bags apart from a COVID-year low of 2.96M in 2020/21. Per-capita is about 3.4–3.5 kg.
- **Switzerland: steady at about 1.0–1.2M bags of domestic use.**
  - It is a large processing hub: bean imports run at 3.0–3.5M bags against 1.6–1.9M bags a year of roast-and-ground exports (USDA summary table).
  - USDA revised the whole Swiss consumption series down 25–30% in June 2024 (for example 2019/20 from 1,470 to 1,055), so treat Swiss per-capita figures with care.
- **Australia: growing fast (about 4% a year).** 1.13M to 2.15–2.3M bags. Per-capita rose from 3.4 to 4.8 kg.
- **Algeria: flat volume of about 2.0M bags.** Derived per-capita fell from 3.8 to 2.5 kg as population grew. Drivers not researched.
- **Saudi Arabia: growing fast (about 5% a year).** 0.55M to 1.30–1.38M bags. Per-capita rose from 1.6 to 2.3 kg.
- **Turkey: growing fast (about 12% a year).** 0.2M to 1.6M bags. Per-capita rose from 0.17 to 1.13 kg. Drivers not researched.
- **Egypt: volatile.** It rose to 0.83M bags in 2018/19 and has run at 0.35–0.45M since 2020/21. Drivers not researched.
- **Ukraine: declining.** 1.6–2.4M bags (2005/06–2008/09) fell to 0.96–0.97M in 2015/16–2016/17 and has run at 1.06–1.30M since 2017/18. Drivers not researched.
- **Morocco: growing about 2.7% a year.** 0.53M to 0.8–1.0M bags.
- **Taiwan: growing fast (about 8% a year).** 0.18M to 0.71M bags. Taiwan is not in the World Bank data, so no per-capita figure was derived.
- **Norway: steady at about 0.7–0.8M bags.** Derived per-capita is 8.3–9.8 kg, the highest in the USDA set.

## 7. Gaps and caveats

**Not obtained.** The search budget ran out, and direct downloads were blocked:
- AJCA (Japan) annual demand in tonnes.
- NCA (US) survey data.
- ECF European Coffee Report per-country and per-capita tables.
- Eurostat green-coffee imports.
- Korea Customs (KCS/KITA), China customs (GACC) and Rusteacoffee imports.
- UK and Swiss statistics offices.
- ICO consumption after 2019.
- USDA levels for 2024/25 and 2025/26 for everyone except the EU (and the EU/US import revisions).
- Japan's 2026/27 consumption level (only +3.7% is known).
- The USDA 2025/26 levels for the US and China are only implied by the 2026/27 growth rates (about 25.5M and about 6.4M) and were not recorded as data.

**Vintage risk.**
- The 2024/25 values in the full series are June 2024 forecasts.
- USDA revisions can be large: the whole Swiss series (−25–30%), China (+16% for 2023/24), EU 2023/24 (−3.5%).
- Superseded values are kept in `consumption_usda_prior_vintage`.

**Mirrors.** The PSD, ICO, Comtrade and World Bank files were read from third-party GitHub copies of official downloads.
- The June 2024 PSD vintage is confirmed two ways: the file's update stamps, and its world total of 170,634 matching Comunicaffe's June 2024 report.
- The ICO origin of the Kaggle dataset is inferred from its ICO-member country list.

**Search-summary rows.**
- Several rows came from the search engine's summaries of PDFs (for example the December 2025 EU table values 41,870 and 47,000).
- Two periods (the July 2026 revisions assigned to 2025/26, and the December 2025 revisions to 2024/25) were inferred from the revision arithmetic.

**Low-confidence rows.**
- Vivid Maps tonnages for Germany, Italy, France and the US in 2010 and 2023 have no stated source and use a different basis from ICO. They are indicative only.
- One summary said the largest importers "will remain the EU with 2.7 million tonnes, the US (1.4 million), Japan (372,000), Russia (228,000)". It could not be pinned to a page, so it was not entered in the CSV.

## 8. Key URLs

- USDA Coffee: World Markets and Trade, June 2026 edition (released 22 July 2026): https://www.fas.usda.gov/sites/default/files/2026-07/coffee.pdf ; coverage: https://www.comunicaffe.com/usda-world-coffee-production-6-exports-9-and-global-consumption-3-6-set-to-reach-record-levels-in-2026-27 and https://www.foodbusinessmea.com/usda-forecasts-record-global-coffee-production-and-exports-in-2026-27/
- USDA December 2025: https://www.fas.usda.gov/sites/default/files/2025-12/coffee.pdf ; coverage: https://www.comunicaffe.com/usda-sees-world-coffee-production-for-2025-26-at-an-all-time-high-of-178-8-million-bags-2-consumption-at-a-record-173-9-million-1-3/
- USDA June 2020: https://www.fas.usda.gov/sites/default/files/2024-08/coffee-June2020.pdf
- USDA PSD, June 2024 release (copy): https://github.com/Mal303/Interactive-Coffee-Bean-Origin-Map/tree/a1577e64b4a2a0a5a6fdab415ea8fb7ae0bdb118/homepage_css/Data/CoffeeDataRaw/Coffee_Data ; official download: https://apps.fas.usda.gov/psdonline/downloads/psd_coffee_csv.zip
- ICO 1990–2019 (copy): https://github.com/dryzrlbs/coffeedata
- UN Comtrade extracts (copy): https://github.com/Tatiana-ZC/Final.Project_Coffee
- World Bank population (copy): https://github.com/datasets/population
- ECF Economic Impact of Coffee in Europe: https://www.ecf-coffee.org/wp-content/uploads/2026/06/ECF_Economic-Impact-of-Coffee-in-Europe.pdf ; https://dailycoffeenews.com/2026/07/08/coffee-generates-e84-4-billion-in-direct-value-across-the-eu-report-says/
- GAIN China (January 2026): https://www.fas.usda.gov/data/gain/2026/01/china-brewing-momentum-chinas-coffee-market-and-emerging-opportunities-us-exporters
- GAIN Korea (2015): https://apps.fas.usda.gov/newgainapi/api/report/downloadreportbyfilename?filename=Coffee+Market+Brief+Update_Seoul+ATO_Korea+-+Republic+of_12-31-2015.pdf ; (2025): https://apps.fas.usda.gov/newgainapi/api/Report/DownloadReportByFileName?fileName=Coffee+and+Tea+Market+Brief_Seoul+ATO_Korea+-+Republic+of_KS2025-0033
- GAIN Japan (2020): https://apps.fas.usda.gov/newgainapi/api/Report/DownloadReportByFileName?fileName=USJTA+Treatment+for+Coffee+Tea+and+Spices_Tokyo_Japan_02-29-2020
