# Workstream E: demand channels and drivers (2005 to 2026)

Data file: `research/coffee-demand/data/raw/E_drivers.csv` (221 rows, 176 with values; 24 high, 126 medium and 26 low confidence among the valued rows; the other 45 rows are blank: mostly explicit "NOT FOUND" placeholders for must-have series, plus 2 qualitative-only rows).
Status as of 2026-09-24: **PARTIAL.**

## 0. Read this first: coverage and provenance

* **The WebSearch budget for the session ran out early.** Its cap is 200 calls, shared across all parallel workstreams. This workstream got 23 searches (all spent on Starbucks) before every further call returned "session has used its web search budget (200 of 200)". The caller had planned for 60 to 150 searches. Direct downloads (sec.gov, starbucks.com, ncausa.org, worldbank.org, nestle.com, news sites) are egress-blocked, as expected.
* To fill what I could without memory, I used two other routes. Both are labelled in the CSV `source_title`/`notes`:
  * **Tier A (official, via WebSearch):** the Starbucks store counts in the CSV marked `high`. They come from Starbucks earnings releases and SEC filings that the search summary attributed explicitly.
  * **Tier B (official data, via a copy):** World Bank WDI bulk CSV files ("Last Updated Date 2025-07-01") and the datahub.io mirror of WB `SP.POP.TOTL` (updated 2026-07-27). I read them from public GitHub repositories with `git clone`; github.com is reachable, worldbank.org is not. The file headers are intact. These rows are marked `medium`.
  * **Tier C (third-party relays, found with GitHub code search):** quotes from research compilations, news corpora and Wikipedia copies. Examples are Luckin 20-F figures quoted in a research pack, the FoodTalks store ranking, and the NCA 2024 figure via Wikipedia. **All are marked `low`, and the primary URL is given in `notes` where the relay names it.** Verify these before they go on a slide.
* The auto-mode classifier stopped me from parsing notebooks in one external repo (a Starbucks 10-K NLP corpus). I did not pursue it further. Two values seen before the block (FY2008 16,680 and FY2025 40,576) are recorded as `low`.

## 1. Coffee shops

### 1a. Starbucks store count at fiscal year-end (FY ends on the Sunday nearest 30 Sep)

| FY | Total stores | US | China | Source (see CSV for URL and quote) | Conf. |
|---|---:|---:|---:|---|---|
| 2005 | 10,241 | | | 10-K FY2005: 6,000 company-operated + 2,435 US licensed + 1,806 international licensed | medium (sum) |
| 2006 | 12,440 | | | 10-K FY2006 ("12,440 Starbucks stores worldwide"; 2,199 opened) | medium |
| 2007 | "over 15,000" | | | 10-K FY2007 (2,571 new stores); exact total not surfaced | blank |
| 2008 | 16,680 | | | Search summary of 10-K FY2008 (year label muddled) plus a third-party 10-K extraction | low |
| 2009 | n/f | | | Not found. Third-party extraction says FY2009 was the only year of net decline (~ -0.3%); CBS/Chain Store Age: "Starbucks to close 600 US stores" | gap |
| 2010 | 16,858 | | | 10-K FY2010: 11,131 company-operated + 5,727 licensed | high |
| 2011 to 2013 | n/f | | | Not found (budget exhausted) | gap |
| 2014 | 21,366 | | | Daily Mail, Apr 2015 ("21,366 locations in 65 countries last year"); corroborated by SNU SMIC note of May 2015 | medium |
| 2015 | 23,043 | | | Q4 FY15 release: "ending the year with 23,043 stores in 68 countries" | high |
| 2016 | 25,085 | | | Q4 FY16 release (75 countries) | high |
| 2017 | 27,339 | | | Q4 FY17 release (75 countries) | high |
| 2018 | 29,324 | | | Q4 FY18 release (78 markets) | high |
| 2019 | 31,256 | | | Q4 FY19 release (+7% y/y) | high |
| 2020 | 32,660 | 15,337 | 4,706 | Q4 FY20 release | high |
| 2021 | 33,833 | 15,450 | 5,360 | Q4 FY21 release | high |
| 2022 | 35,711 | 15,878 | >6,000 | Q4 FY22 release (China "surpassed 6,000") | high / China lower bound |
| 2023 | 38,038 | 16,352 | 6,806 | Q4 FY23 release | high |
| 2024 | 40,199 | 16,941 | 7,596 | Q4 FY24 release (China comps -14%) | high |
| 2025 | 40,990 | 16,864 | 8,011 | Q4 FY25 release, SEC 8-K Ex. 99.1 (107 net closures in Q4) | high |
| Q3 FY2026 (28 Jun 2026) | 41,304 | n/f | n/f | Q3 FY26 release, 29 Jul 2026 (175 net new; FY26 guide ~600 to 650 net new; revenue affected by the "Starbucks China Transaction") | high |

**Key reads**
* Starbucks grew **4.0x, from 10,241 (FY2005) to 40,990 (FY2025)**, a **7.2% CAGR**. Growth ran at 8.4% a year over FY05 to FY15 and 5.9% a year over FY15 to FY25.
* Growth has moved to China and the rest of the world. From FY2020 to FY2025, China added **+3,305 stores (+70%)** and the US **+1,527 (+10%)**. China's share of the global estate rose from **14.4% to 19.5%**.
* The US store count **fell** for the first time in the series in FY2025 (16,941 to 16,864).
* **Conflict:** a third-party 10-K text extraction gives FY2025 = 40,576, against 40,990 in the earnings release (SEC 8-K). Both rows are kept; use 40,990 unless the 10-K says otherwise.

### 1b. China: value chains versus Starbucks

| Entity | Date | Stores | Source | Conf. |
|---|---|---:|---|---|
| Luckin | 31 Dec 2021 | 6,024 (4,397 self-operated + 1,627 partnership; excludes 1,102 EXPRESS machines) | Company description derived from the 20-F (FMP-style JSON copy) | low |
| Luckin | 31 Dec 2024 | 22,340 (14,591 self-operated + 7,749 partnership) | Research pack quoting Luckin 20-F FY2024 (sec.gov .../lk-20241231x20f.htm) | low |
| Luckin | 13 Nov 2025 | 27,930 | FoodTalks, citing the Narrow Door tracker | low |
| Cotti | Oct 2024 | >10,000 | CoffeeTalk (lower bound) | low |
| Cotti | 13 Nov 2025 | 15,323 | FoodTalks / Narrow Door | low |
| Starbucks China | 13 Nov 2025 | 8,283 (tracker; the company reported 8,011 at 28 Sep 2025) | FoodTalks / Narrow Door | low |
| Lucky Coffee / Nova / Manner | 13 Nov 2025 | 5,784 / 4,252 / 2,234 | FoodTalks / Narrow Door | low |
| Shanghai, all coffee shops | end-2023 / 2025 | 9,553 / 10,336 | Shanghai Govt report, "Shanghai tops over 10,000 coffee shops in 2025" (english.shanghai.gov.cn, 30 Apr 2026) | low (relay) |

* Luckin went from about 6.0k to 22.3k stores between end-2021 and end-2024, **3.7x in three years (about 55% a year)**. By end-2024 it had about **2.9x Starbucks China's store count** (7,596 at FY2024). On the November 2025 tracker, Luckin had about 3.4x and Cotti about 1.85x Starbucks China's count.
* **Not found (gaps):** Luckin 2017 to 2020, 2022, 2023, 2025 year-end and Q2 2026; Cotti 2022 and 2023; total China coffee-shop count (World Coffee Portal, Meituan, CCFA); US branded outlets (Project Café USA); global branded outlets; Tim Hortons, Costa, Dutch Bros, McCafé; Korea (KB/KOSIS).
* **Indonesia:** Kopi Kenangan had 1,136 Indonesian and 188 overseas outlets in 2025, with a target of 4,000 by 2030 (Forbes via relay, low).

## 2. Who drinks, and where (US NCA)

| Metric | Year | Value | Source | Conf. |
|---|---|---:|---|---|
| % of US adults who drank coffee in the past day | 2024 | 67% ("20-year high") | NCA April 2024 survey, as cited in Wikipedia "Coffee" | low |
| same | 2004 | "fewer than half" | same | qualitative |
| % of coffee drinkers aged 18 to 24 who had cold coffee in the past day | Jul 2024 | 45% | NCA, via a blog | low |
| Starbucks cold drinks as % of beverage sales | 2013 → FY24 Q3 | 37% → ~75% | CNBC Nov 2024, via a blog | low |

**Not found (gaps):** the NCA past-day series for 2005 to 2023, 2025 and 2026; past-day specialty %; at home versus away from home; cohort splits; espresso-drink growth; out-of-home share of volume or value (ECF, ICO, Euromonitor).

## 3. Formats

* Nespresso: sales were "in excess of CHF 3 billion" by 2011 (Wikipedia-derived lower bound, low). Nestlé's Powdered & Liquid Beverages sales were **CHF 21.6 bn in 2018**, a category that includes Nescafé and Nespresso (CNN Business quoting Nestlé, medium).
* **Not found (gaps):** the Nespresso annual series for 2005 to 2025; Nestlé coffee sales; Keurig pods and brewer penetration; RTD growth; soluble share (USDA PSD / ICO); capsule share in Europe.

## 4. Roasters / industry

* Nothing with numbers was collected (Luckin roasting plants and green-coffee purchase volumes; JDE Peet's volumes; roaster counts). One relay notes that the number of coffee "market entities" in China "roughly doubled between 2021 and 2025", but it gives no figure and no clear source, so it is not recorded.

## 5. Macro drivers (World Bank WDI, vintage 2025-07-01)

| Country | GDP per capita 2005 (current US$) | GDP per capita 2024 | Multiple | Urban % 2005 | Urban % 2024 | Pop. growth 2005 to 2024 |
|---|---:|---:|---:|---:|---:|---:|
| China | 1,778 | 13,303 | 7.5x | 42.5 | 65.5 | +8.1% |
| Viet Nam | 711 | 4,717 | 6.6x | 27.3 | 40.2 | +24.5% |
| Indonesia | 1,238 | 4,925 | 4.0x | 45.9 | 59.2 | +22.8% |
| India | 710 | 2,697 | 3.8x | 29.2 | 36.9 | +25.7% |
| Philippines | 1,220 | 3,985 | 3.3x | 45.7 | 48.6 | +31.6% |
| Brazil | 4,828 | 10,280 | 2.1x | 82.8 | 88.0 | +14.8% |
| Korea, Rep. | 19,402 | 33,121 (2023; no 2024 value in this vintage) | 1.7x | 81.3 | 81.5 | +7.4% |
| United States | 44,123 | 85,810 | 1.9x | 79.9 | 83.5 | +15.1% |
| East Asia & Pacific | 4,893 | 13,349 | 2.7x | 46.8 | 63.7 | |
| World | 7,276 | 13,673 | 1.9x | 49.0 | 57.7 | +23.8% |

* World population (WB SP.POP.TOTL): **6.576 bn (2005), 7.001 bn (2010), 7.442 bn (2015), 7.855 bn (2020), 8.142 bn (2024)**, adding +1.57 bn over 2005 to 2024. The 2025 value (UN WPP 2024) was **not retrieved**.
* China per-capita cups: **16.74 (2023) → 28.57 (2025)**, from an unattributed industry figure via relay (low). The 2016 and 2020 values were not found.
* **Not found (gaps):** middle-class size in Asia (Brookings/OECD) and evidence on Gen Z and the tea-to-coffee shift in Asia.

## 6. Why demand grew: narrative

1. **More outlets, in more places.** The café channel has kept adding capacity. Starbucks alone quadrupled its estate between FY2005 and FY2025 (10,241 to 40,990; Starbucks releases and 10-Ks). Since 2020 the marginal store has been in China and other international markets, not the US: China +70% against US +10% over FY2020 to FY2025. A café opening adds regular, routine out-of-home cups rather than just moving the same demand from one channel to another.
2. **China's price-led café boom.** App-first, pick-up-format value chains scaled far faster than Starbucks. Luckin went from about 6k stores (end-2021) to 22.3k (end-2024, per its 20-F as quoted), and third-party trackers put Luckin at about 28k and Cotti at about 15k by November 2025. On that tracker Luckin's count was about 3.4x Starbucks China's. Shanghai alone passed 10,000 coffee shops in 2025 (Shanghai Govt). Relayed per-capita consumption rose from 16.7 to 28.6 cups a year between 2023 and 2025, still tiny against Western levels. This is the clearest example of *new* drinkers being created, not existing ones being shifted. Starbucks China's -14% comps in Q4 FY24 show the competitive (price) side of the same trend.
3. **Income and urbanisation in emerging Asia.** Between 2005 and 2024, GDP per capita (current US$) rose **7.5x in China, 6.6x in Viet Nam, 4.0x in Indonesia and 3.8x in India**. China's urban share rose from **42.5% to 65.5%**, Viet Nam's from 27.3% to 40.2% and Indonesia's from 45.9% to 59.2% (World Bank WDI). Urban, higher-income consumers are the café and RTD customer base, which is why these markets lead store growth.
4. **Population.** The world added about **1.57 bn people** between 2005 and 2024 (+23.8%), with the fastest gains in India, the Philippines, Viet Nam and Indonesia (+23% to +32%). That is baseline volume growth even at flat per-capita use.
5. **A mature market still deepening (US).** The NCA reports past-day coffee drinking among US adults at a **20-year high of 67% in 2024**, against "fewer than half" in 2004 (via Wikipedia; low). Format innovation, especially cold and iced drinks, is doing the work. Cold drinks rose from about 37% to about 75% of Starbucks beverage sales between 2013 and FY24 Q3 (CNBC via relay), and 45% of 18 to 24 year-old coffee drinkers had cold coffee in the past day (NCA, July 2024, via relay). Younger cohorts take up coffee through cold, sweet, customised drinks.
6. **Premium at-home formats.** Capsules (Nespresso had passed CHF 3 bn in sales by 2011) and Nestlé's CHF 21.6 bn Powdered & Liquid Beverages business (2018) show that at-home convenience formats also grew. The time series for this driver still needs to be built.
7. **Watch-outs for the desk.** Starbucks' US estate is now shrinking (FY2025 closures), China is a price war, and Starbucks' Q3 FY26 revenue line "reflect[s] the Starbucks China Transaction" (check how China stores are counted from FY2026). Store growth is still positive (41,304 at Q3 FY26, guidance of about 600 to 650 net new in FY26). Mature-market store growth has slowed, however, and the demand upside sits in Asian value chains and the RTD and at-home formats.

## 7. Gaps and exact follow-up plan (needs the WebSearch budget raised: `CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION`)

These queries worked well while the budget lasted. The press-release phrasing "ending the period with N stores" works best.
* Starbucks FY2007, FY2009, FY2011, FY2012, FY2013, plus verification of FY2008 and FY2014: try `Starbucks fiscal 2012 fourth quarter "18,066" stores` and similar (allowed_domains sec.gov, investor.starbucks.com). Starbucks China FY2005 to FY2019 comes from the 10-K "store data" tables (the China/Asia Pacific segment) or Starbucks Stories China milestones.
* Starbucks Q3 FY26 US and China counts come from the 29 Jul 2026 release at investor.starbucks.com.
* Luckin: search `"Luckin Coffee" "total number of stores" "self-operated" fourth quarter 2023` on investor.lkcoffee.com, prnewswire.com and globenewswire.com, repeating for each year from 2018 to 2025 and for Q2 2026. The 2019 prospectus (F-1) gives 2017 and 2018.
* Cotti (company announcements and press), and China total coffee shops (World Coffee Portal "China coffee shop market", Meituan/CCFA reports).
* NCA NCDT: one query per year of the form `NCA National Coffee Data Trends 20XX "past day" percent` on ncausa.org, prnewswire.com or dailycoffeenews.com.
* Nespresso: Nestlé full-year results `"Nespresso" "organic growth" sales CHF billion 20XX` on nestle.com, reuters.com, comunicaffe.com.
* UN WPP 2024, world population 2025: `World Population Prospects 2024 world population 2025 8.2 billion` on population.un.org.
* Middle class: Brookings (Kharas) "Asia middle class 2030". Gen Z / tea-to-coffee: allegra, WCP China reports.

## 8. Provenance of key GitHub-hosted copies used (read-only)
* WB GDP per capita: github.com/javamercy/GDP-analysis @cad0968, `data/API_NY.GDP.PCAP.CD_DS2_en_csv_v2_122367.csv` (WDI, 2025-07-01)
* WB urban %: github.com/NSAPH-Projects/causal-inference-co2 @9f2c6e7, `data/API_SP.URB.TOTL.IN.ZS_DS2_en_csv_v2_22447.csv` (WDI, 2025-07-01)
* WB population: github.com/datasets/population @075cd0d, `data/population.csv` (source http://data.worldbank.org/indicator/SP.POP.TOTL)
* Research relays: github.com/vibewatch/startup (Manner Coffee and Kopi Kenangan packs, Aug and Jul 2026), github.com/Necksus/TradingData (LKNCY profile), and Wikipedia and news-text copies. Exact file URLs are in the CSV.
