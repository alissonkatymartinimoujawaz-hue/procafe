# Workstream A - World coffee supply/demand balance, 2005/06 -> 2026/27

Research date: 2026-09-24. Dataset: `data/raw/A_world_balance.csv` (517 rows, schema per `data/raw/SCHEMA.md`).
All volumes are million 60-kg bags. "MY" = USDA marketing year (world total = sum of each country's local marketing year);
"CY" = ICO coffee year (Oct-Sep). USDA and ICO series are **not directly comparable** (different year bases, coverage and consumption definitions).

## How the data were obtained (read this first)

* **WebSearch**: about 27 queries were run for this workstream. The session-wide cap (200 searches, shared with the parallel workstreams) then ran out,
  and every later search was refused. Everything that came from search results (USDA report headlines as quoted by Comunicaffe, Barchart,
  Perfect Daily Grind, Food Institute, Ecofin, Fresh Cup, DatamarNews, and statements from USDA PDFs) is recorded with its URL.
* **USDA full history (2005/06-2025/26)**: taken from the official USDA FAS PSD bulk file (`psd_coffee_csv.zip`) as downloaded on 2026-06-21 and
  aggregated to a World total (sum of 88-93 reporting countries) by the public GitHub project `andenick/Foodberg`
  (file `Outputs/Data/WASDE_PSD/wasde_psd_coffee_green__world.csv`, commit 7b5333b; its PROVENANCE.md documents the download).
  That file is the **December 2025 release vintage**. It matches the USDA December 2025 report headlines exactly:
  MY2025/26 production 178.848 (report: 178.8), consumption 173.852 (173.9), ending stocks 20.148 (20.1), bean exports 123.825 (123.8), and MY2024/25 production 175.316 (175.3).
  Confidence is `medium`: official data taken from a secondary copy.
* **ICO 2020/21-2025/26**: taken from the text and tables of the ICO Coffee Market Reports for February, March, May, June and August 2026. The PDF and
  text copies sit in the public repo `BMR-Com/coffee-analytics`, whose pipeline downloads the CMR PDFs from ico.org. Rows cite the official ico.org URL.
* **ICO before 2020/21**: only the ICO historical country tables (crop-year basis, about 2020 vintage) could be reached, through the Kaggle "Coffee dataset" mirrored
  on GitHub (`ConnorMoss02/Brewing-Insights`). The world and exporting-country totals are sums I computed, flagged `low` confidence.
* Rows marked "DERIVED" are simple arithmetic on official numbers: production minus consumption, stock change, and sums of countries.
  Nothing was interpolated or taken from memory.

## 1. Summary table (latest vintage per year)

USDA columns: Dec-2025 PSD vintage for 2005/06-2024/25. For 2025/26, production and bean exports use the Jul-2026 report and the other columns the Dec-2025 vintage.
2026/27 is the Jul-2026 forecast.
ICO columns: coffee-year series from the 10-Sep-2026 update (CMR August 2026). The last two columns are low-confidence crop-year ICO historical sums.

| MY / CY | USDA prod | Arabica | Robusta | USDA cons | USDA end stocks | USDA stock chg (derived) | USDA P-C (derived) | USDA bean exports | ICO prod (CY) | ICO cons (CY) | ICO balance (CY) | ICO hist. prod (crop yr, low) | ICO exporting-ctry cons (crop yr, low) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2005/06 | 117.9 | 70.8 | 47.0 | 125.2 | 32.6 | -8.5 | -7.3 | 84.8 |  |  |  | 111.2 | 33.1 |
| 2006/07 | 134.1 | 84.1 | 49.9 | 124.4 | 35.7 | 3.1 | 9.7 | 95.6 |  |  |  | 135.4 | 35.0 |
| 2007/08 | 124.4 | 74.8 | 49.6 | 128.9 | 31.4 | -4.3 | -4.5 | 88.4 |  |  |  | 121.8 | 36.9 |
| 2008/09 | 136.8 | 85.7 | 51.1 | 125.9 | 39.6 | 8.2 | 10.9 | 91.7 |  |  |  | 134.8 | 38.4 |
| 2009/10 | 129.8 | 77.8 | 52.0 | 139.2 | 28.8 | -10.7 | -9.4 | 92.3 |  |  |  | 127.9 | 39.7 |
| 2010/11 | 141.4 | 87.9 | 53.5 | 135.5 | 28.6 | -0.2 | 5.9 | 100.4 |  |  |  | 140.1 | 41.6 |
| 2011/12 | 144.8 | 84.5 | 60.3 | 142.8 | 25.7 | -2.9 | 2.0 | 101.1 |  |  |  | 141.3 | 43.2 |
| 2012/13 | 158.0 | 92.9 | 65.1 | 143.4 | 35.4 | 9.6 | 14.6 | 105.0 |  |  |  | 151.2 | 44.7 |
| 2013/14 | 160.1 | 92.5 | 67.6 | 143.9 | 41.2 | 5.8 | 16.2 | 110.0 |  |  |  | 153.9 | 45.3 |
| 2014/15 | 153.8 | 86.7 | 67.1 | 147.2 | 43.1 | 1.9 | 6.6 | 103.8 |  |  |  | 150.3 | 46.5 |
| 2015/16 | 152.4 | 86.1 | 66.3 | 153.2 | 35.0 | -8.2 | -0.8 | 112.4 |  |  |  | 156.1 | 47.3 |
| 2016/17 | 161.1 | 101.1 | 59.9 | 155.1 | 36.5 | 1.5 | 6.0 | 112.7 |  |  |  | 162.3 | 48.3 |
| 2017/18 | 159.8 | 95.2 | 64.6 | 160.6 | 32.0 | -4.5 | -0.8 | 112.9 |  |  |  | 163.7 | 49.7 |
| 2018/19 | 175.9 | 104.9 | 70.9 | 166.0 | 36.9 | 5.0 | 9.9 | 121.3 |  |  |  | 172.5 | 50.2 |
| 2019/20 | 169.0 | 94.9 | 74.1 | 162.4 | 35.8 | -1.1 | 6.7 | 116.3 |  |  |  | 165.1 | 50.0 |
| 2020/21 | 176.5 | 102.1 | 74.4 | 162.1 | 37.5 | 1.7 | 14.5 | 121.2 | 171.3 | 170.9 | 0.4 |  |  |
| 2021/22 | 165.0 | 87.1 | 78.0 | 167.9 | 31.9 | -5.6 | -2.8 | 119.0 | 168.4 | 176.8 | -8.4 |  |  |
| 2022/23 | 164.4 | 87.8 | 76.6 | 168.8 | 26.9 | -5.0 | -4.4 | 110.9 | 170.0 | 173.7 | -3.7 |  |  |
| 2023/24 | 169.3 | 97.2 | 72.1 | 164.0 | 23.1 | -3.8 | 5.4 | 119.2 | 171.6 | 174.6 | -3.0 |  |  |
| 2024/25 | 175.3 | 100.2 | 75.1 | 171.6 | 21.3 | -1.8 | 3.8 | 121.5 | 175.9 | 182.2 | -6.3 |  |  |
| 2025/26 (P & bean exp: Jul-26 vintage; rest Dec-25) | 178.8 | 95.5 | 83.3 | 173.9 | 20.1 | -1.2 | 5.0 | 119.5 | 183.6 | 180.6 | 3.0 |  |  |
| 2026/27 (forecast, Jul-26) | 189.7 | 105.9 | 83.8 | 179.7 | 26.3 | +1.9 (stated) |  |  |  |  |  |  |  |

Other vintages recorded in the CSV (for revision analysis):
* 2026/27, USDA July 2026: production 189.667 (+10.8m, +6.0%), Arabica 105.867 (record, +12.1%), Robusta 83.8 (-0.7%), consumption 179.7 (record, +3.6%),
  exports all forms 158.874 (+8.9%), ending stocks 26.3 (+1.9m).
* 2025/26: Jun-2025 first forecast = production 178.7, consumption 169.4, stocks 22.8. Dec-2025 = 178.8 / 173.9 / 20.1, bean exports 123.8.
  Jul-2026 = production unchanged at 178.8, bean exports cut 4.3m to 119.5, bean imports cut 1.3m to 118.6.
  The Jul-2026 forecasts also imply revised 2025/26 figures: consumption about 173.5 (from 179.7 being +3.6%) and ending stocks about 24.4 (from 26.3 being +1.9m).
  These were not found stated explicitly, so they are **not** recorded as values.
* 2024/25: Jun-2024 = production 176.235, consumption 170.634. Dec-2024 = 174.855 / 168.071, stocks 20.9 (press: 20.867, -6.6%, called a "25-year low").
  Jun-2025 = production 174.395 (Arabica 98.692, Robusta 75.703), exports all forms 147.161. Dec-2025 = 175.316.
* 2023/24: Jun-2023 first forecast = production 174.3. Jun-2025 and Dec-2025 = 169.345.
* 2022/23: Dec-2022 = production 172.8, consumption 167.9. Dec-2025 = 164.389 / 168.754.
* ICO Feb/Mar-2026 vintage (thousand bags), coffee years 2021/22 to 2024/25:
  * Production: 165.092 / 165.785 / 168.707 / 177.513.
  * Consumption: 170.500 / 176.855 / 172.578 / 175.071.
  * Exporting countries: 54.438 / 55.664 / 56.344 / 57.742.
  * Importing countries: 116.062 / 121.191 / 116.233 / 117.329.
  * BALANCE: -5.407 / -11.070 / -3.871 / **+2.443**.
  * The 10-Sep-2026 update replaced all of these (see section 4).

## 2. Latest state (2026)

**USDA, "June" 2026 edition. It was actually released on 22 July 2026; the file is at fas.usda.gov/sites/default/files/2026-07/coffee.pdf**
* Record world production for 2026/27: **189.7m (+10.8m, +6%)**. The gain comes from record crops in Brazil (71.9m; Arabica 47.5m, Robusta 24.4m), Vietnam (32.5m), Ethiopia and Uganda.
  These more than offset lower crops in Indonesia and India.
  Sources: https://www.comunicaffe.com/usda-world-coffee-production-6-exports-9-and-global-consumption-3-6-set-to-reach-record-levels-in-2026-27 ,
  https://perfectdailygrind.com/2026/07/coffee-news-recap-24-july-2026/
* Consumption is forecast at a record **179.7m (+3.6%)**, with the largest gains in the EU and the US
  (Fresh Cup: US +5.7%, China +5.1%; Ecofin: China 6.9m in 2026/27, +37% on five years earlier).
  Sources: https://freshcup.com/usda-global-coffee-production-consumption-to-reach-record-levels/ , https://www.ecofinagency.com/news/2407-57677-coffee-production-and-consumption-head-for-new-records
* Ending stocks are forecast to rise **1.9m to 26.3m**. This is the first increase after five straight declines (2021/22 to 2025/26), though stocks stay below their historical average.
  Press described the implied surplus as "roughly 10 million bags" (Perfect Daily Grind).
  Source: https://www.barchart.com/story/news/3431105/coffee-prices-fall-as-usda-predicts-6-increase-in-global-coffee-production
* Revisions to 2025/26: production unchanged at 178.8. Bean exports cut 4.3m to 119.5m. Bean imports cut 1.3m to 118.6m; the EU was cut 0.5m to 46.5m and the US 0.7m to 23.1m, both "on lower consumption".
  Source: https://apps.fas.usda.gov/psdonline/circulars/coffee.pdf

**USDA December 2025**
* 2025/26 production at a record 178.8m (+2%). Consumption at a record 173.9m (+1.3%). "Ending stocks are expected to drop for a fifth-consecutive year to just 20.1 million bags."
  Bean exports 123.8m (+2.3m).
  Sources: https://www.fas.usda.gov/sites/default/files/2025-12/coffee.pdf , https://www.comunicaffe.com/usda-sees-world-coffee-production-for-2025-26-at-an-all-time-high-of-178-8-million-bags-2-consumption-at-a-record-173-9-million-1-3/

**ICO, statistics update of 10 Sep 2026, published in CMR August 2026 (https://www.ico.org/documents/cy2025-26/cmr-0826-e.pdf)**
* Production: 175.9m in 2024/25 (+2.5%), and an estimated **183.6m (+4.4%)** in 2025/26. Arabica 104.4m (+2.8%), Robusta 79.2m (+6.5%).
* Consumption: **182.2m (+4.3%)** in 2024/25, driven by North America and Europe, and an estimated **180.6m (-0.8%)** in 2025/26.
  ICO calls the 2025/26 dip "a normalization following the unusually strong growth recorded in 2024/25", with a reduction estimated for the US, the largest consuming country.
* Balance: "Following four consecutive coffee years of deficit, from 2021/22 to 2024/25, the global coffee market is projected to record a **surplus of 3.0 million bags in 2025/26**."
  Derived deficits from ICO Table 3: 2021/22 -8.4, 2022/23 -3.7, 2023/24 -3.0, 2024/25 -6.3. 2020/21 was a +0.4 surplus.
* ICO does not publish its own 2026/27 balance forecast in these reports. It quotes private forecasts: Rabobank +8.64m (Feb/Mar 2026) and +8.9m (30 Aug 2026), and Marex +10.5m (Aug 2026).
  NB: some search summaries wrongly credit the 8.64m surplus to the ICO; it is Rabobank's.
* Certified stocks: "ICE-certified Arabica stocks ... closing at **223,976 bags on 31 August [2026], the lowest level since 1999**". This is about 68% below a year earlier.
  Combined ICE-certified Arabica and Robusta stocks were 1.09m on 30 Jun 2026, the lowest since Feb 2024 (CMR June 2026).
  Monthly NY and London levels for Mar-2025 to Aug-2026 from ICO Table 5 are in the CSV. The NY low in 2025 was 0.44m at end-Nov 2025.
  London Robusta rose to 0.83m in Aug 2026, a nine-month high.

## 3. Insights for the demand story (all figures from the CSV; derived ratios are labelled)

1. **Steady long-run demand growth.** USDA world consumption rose from 125.2m (2005/06) to 173.9m (2025/26), +38.9%. That is about **1.7% a year CAGR** (derived).
   It is forecast at 179.7m in 2026/27. Consumption fell year on year only in 2006/07, 2008/09, 2010/11, 2019/20 and 2020/21 (COVID), and 2023/24.
2. **Stocks were drawn down to multi-decade lows.** USDA world ending stocks peaked at 43.1m in 2014/15 and fell five years in a row to 20.1m in 2025/26 (Dec-2025 vintage).
   That is the lowest in the comparable PSD series (importing-country stocks are included from 2002/03).
   Stocks-to-use (derived) fell from 29.3% to **11.6%**. The Jul-2026 report expects the first rebuild (26.3m) in 2026/27.
   On the ICO side, ICE-certified Arabica stocks hit a 27-year low (Aug 2026).
3. **Deficit years ended in 2025/26.** ICO shows four straight deficits (2021/22-2024/25; cumulative about -21.4m, derived) and a surplus of 3.0m in 2025/26.
   USDA and private forecasters (Rabobank, Marex) expect a larger surplus of about 8.6-10.5m in 2026/27.
   The USDA stock-change series tells the same story: -5.6, -5.0, -3.8, -1.8 and -1.2m in 2021/22-2025/26, then +1.9m forecast for 2026/27.
4. **Demand is shifting to Asia and to producing countries.** ICO regional consumption, 2020/21 to 2025/26:
   * Asia & Oceania: 42.6 to 48.5m (+13.8%). Its share rose from 24.9% to 26.9%.
   * Europe: 52.4 to 55.1m (+5.2%). Its share was steady at about 30.5%.
   * North America: 30.2 to 28.5m (-5.6%). Its share fell from 17.7% to 15.8%.
   * South America: 26.9 to 28.8m. It is set to overtake North America as the #3 consuming region in 2025/26 (ICO text).
   * Exporting (producing) countries' share of consumption was 31.9% in 2021/22 and 33.0% in 2024/25 (Feb-2026 ICO vintage, derived).
   * Longer run, from ICO historical country tables (low confidence, crop years): exporting-country domestic consumption grew from 19.5m (1990/91) to 33.1m (2005/06) to 50.0m (2019/20), +51% since 2005/06.
     Consumption in the 35 importing ICO members (EU, UK, US, Japan, Russia, Switzerland, Norway, Tunisia; calendar years) grew only +19%, from 73.2m in 2005 to 87.1m in 2019.
5. **The two agencies disagree on the level of demand.** ICO's apparent consumption for 2024/25 (182.2m) is about 10.6m above USDA (171.6m). For 2025/26 the gap is about 6.7m (180.6m vs 173.9m).
   Production levels are closer (ICO 175.9m vs USDA 175.3m in 2024/25). Pick one source per chart and footnote it.
6. **The Arabica/Robusta mix is changing.** USDA Robusta output rose from 47.0m (2005/06) to 83.3m (2025/26 Dec-25 vintage; record). Arabica is volatile (biennial Brazil cycle) and only reaches a record of 105.9m in the 2026/27 forecast.

## 4. ICO methodology and series revisions (document these on slides)

* **Coffee-year basis.** The CMR supply/demand tables use the coffee year (1 Oct-30 Sep). Producer crop years (commencing 1 Apr, 1 Jul or 1 Oct) are converted to coffee years by splitting each crop across coffee years (ICO "Explanatory Note for Table 3").
  ICO says these figures "may therefore differ from estimates published by market analysts on a crop-year basis". Crop-year data are available only to subscribers.
* **Apparent consumption.** In the Sep-2026 update, consumption "is calculated as apparent consumption (production plus net trade and changes in stocks, where applicable) and, as such, is subject to yearly fluctuations" (CMR Aug 2026, footnote 5).
  This footnote does not appear in the Feb, Mar, May or Jun 2026 CMRs, which suggests the definition was introduced or made explicit with the 10-Sep-2026 update.
* **Big revisions in Sep 2026.** Between the Feb/Mar-2026 table and the Sep-2026 table:
  * 2024/25 production went from 177.5 to 175.9 and consumption from 175.1 to 182.2. The balance flipped from a +2.4 surplus to a -6.3 deficit.
  * 2021/22 production went from 165.1 to 168.4 and consumption from 170.5 to 176.8.
  * The Feb-2026 consumption values labelled 2021/22-2024/25 closely match the Sep-2026 values labelled 2020/21-2023/24. For example, North America reads 30.228 / 31.324 / 28.694 / 27.745 in Feb-2026 and 30.2 / 31.3 / 28.7 / 27.8 in Sep-2026, and the world totals are 170.5 / 176.9 / 172.6 / 175.1 vs 170.9 / 176.8 / 173.7 / 174.6.
    This points to a **one-year re-alignment of the consumption series** in the new vintage, alongside the new apparent-consumption definition.
  * **Use only the Sep-2026 vintage for time series. Do not splice the two vintages.**
* **Older ICO series are not comparable.** The historical ICO country tables to 2019/20 are on a crop-year basis. Importing-country data there cover ICO members only (calendar years) and exclude non-members such as China and Korea.
  They are not comparable with the 2020/21+ coffee-year series.

## 5. Gaps and caveats

* **ICO world production and consumption by coffee year for 2005/06-2019/20 are not captured.** The search budget ran out before the older CMR and CDR tables could be searched.
  The only stand-ins are crop-year sums from ICO historical country tables (production and exporting-country consumption, `low` confidence).
  There is no ICO world-consumption proxy before 2020/21.
* **ICO regional breakdown for an early year**: only 2020/21 onward (Sep-2026 vintage) and 2021/22 onward (Feb-2026 vintage, which also has the importing/exporting split). A 2005-era regional split was not found.
* **USDA Jul-2026 vintage**: stated values for 2025/26 consumption and ending stocks were not found (implied figures are in section 1 only). The July edition's revisions to years before 2025/26 are unknown.
  The rest of the history is the Dec-2025 vintage.
* **USDA older years (2005/06-2021/22)** come only from the Dec-2025 PSD aggregate. They were not individually re-checked against report text.
  An older, less complete PSD copy (Kaggle `psd_coffee.csv`, about Dec-2023 vintage) has identical production and ending stocks for 2005/06-2014/15.
  Its world consumption is 0.04-0.71m higher in every year 2005/06-2022/23. The per-row notes give the difference; the later vintage is used.
* **Conflicting search summary**: one summary said the Dec-2025 report "lowered" 2024/25 production 0.9m to 175.3m. The PSD shows 175.316 vs 174.395 in Jun-2025, which is a **raise** of about 0.9m. The value is recorded and the wording is ignored.
* **USDA "balance"**: production minus consumption is positive in 2023/24-2025/26 even though stocks fell, because world bean exports exceed imports (a statistical residual).
  Use `balance_usda_stock_change` (ending minus beginning stocks) as the USDA-implied surplus or deficit.
* **Report timing**: USDA's mid-year 2026 coffee report came out on 22 Jul 2026, not in June. The ICO "August 2026" CMR was published on 10 Sep 2026.
* **Units**: all values are in million 60-kg bags. The PSD source is in 1000 bags (divided by 1000). The ICO Feb/Mar-2026 table is in thousand bags (divided by 1000). The ICO historical mirror is in kg (divided by 60e6).

## 6. Main sources

* USDA FAS, Coffee: World Markets and Trade:
  * Jul 2026: https://www.fas.usda.gov/sites/default/files/2026-07/coffee.pdf ; https://apps.fas.usda.gov/psdonline/circulars/coffee.pdf
  * Dec 2025: https://www.fas.usda.gov/sites/default/files/2025-12/coffee.pdf
  * Jun 2025: https://www.fas.usda.gov/sites/default/files/2025-06/coffee.pdf
* USDA PSD (Dec-2025 vintage, world aggregate): https://github.com/andenick/Foodberg/blob/7b5333b1066caceaef075a4c66b480507235a571/Outputs/Data/WASDE_PSD/wasde_psd_coffee_green__world.csv (official source https://apps.fas.usda.gov/psdonline/downloads/)
* Trade press quoting USDA:
  * Comunicaffe: Jul 2026, Dec 2025, Jun 2025, Dec 2024, Jun 2024, Jun 2023 and Dec 2022 articles (URLs in CSV).
  * Barchart 3431105.
  * Perfect Daily Grind, 24 Jul 2026.
  * Fresh Cup; Ecofin; Food Institute; DatamarNews.
* ICO Coffee Market Reports:
  * Aug 2026: https://www.ico.org/documents/cy2025-26/cmr-0826-e.pdf
  * Jun 2026: https://www.ico.org/documents/cy2025-26/cmr-0626-e.pdf
  * Mar 2026: https://www.ico.org/documents/cy2025-26/cmr-0326-e.pdf
  * Feb 2026: https://www.ico.org/documents/cy2025-26/cmr-0226-e.pdf
  * All read from the mirror https://github.com/BMR-Com/coffee-analytics
* ICO historical country tables (Kaggle mirror): https://github.com/ConnorMoss02/Brewing-Insights/tree/9aaf5291bf43a9ca5c4958902819cfff222b3803/data/raw
