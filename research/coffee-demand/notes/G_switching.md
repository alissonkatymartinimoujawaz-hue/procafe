# G: Bean switching (arabica ↔ robusta) and origin switching, 2010–2026

*Workstream G · compiled 2026-09-24 · data file: `data/raw/G_switching.csv` (118 rows)*

## 0. Status: partial coverage

- **Web-search budget ran out after 19 searches in this workstream.** The session-wide WebSearch cap (200 calls, shared with the other workstream agents) was reached. Every later call returned "Web search was not performed: this session has used its web search budget (200 of 200)". Direct downloads are blocked by egress policy. I also tested icocoffee.org, teaandcoffee.net and comunicaffe.com, and all failed. **So targets 2 (blend shares), 3 (imports by origin, tariffs) and most of 5 are NOT covered, and target 1 covers only CY2019/20 and CY2022/23 to 2025/26, not 2010/11 onwards.** A prioritised search plan for when the budget is raised is in §6.
- **File hygiene.** When I started, `G_switching.csv` already held 50 rows written by another agent: 25 Brazil ABIC/IPCA consumption rows, written twice. All 50 were verbatim copies of rows in `F_marginal_buyers.csv`. I backed them up to the session scratchpad (`G_switching_preexisting_backup.csv`) and rebuilt `G_switching.csv` with switching data only. No information was lost, because F still holds those rows.
- **How to read values.** Each value is taken from a WebSearch result summary. The URL is the page the summary attributed it to. Rows marked **DERIVED** in `notes` are plain arithmetic on sourced values: complements, sums, differences, ratios. Some of these use ICO group prices recorded by workstream B (`B_prices.csv`) or USDA production numbers recorded by workstream A (`A_world_balance.csv`). No values were estimated or interpolated.
- **Two bases for exports; do not mix them.** ICO reports exports of *all forms* (green + roasted + soluble, in green-bean equivalent) and exports of *green beans only*. The all-forms Robusta share is higher: 38.65% in CY2023/24 vs 36.3% for green beans. This suggests that soluble exports lean towards robusta. That last point is an inference.
- **Vintages.** ICO revises heavily. For example, CY2023/24 all-forms exports were 137.273 in the Nov-2024 vintage and 139.015 in the Nov-2025 vintage. Green-bean exports were 125.44 in Oct-2024, but the Oct-2025 wording implies about 122.2. Both vintages are kept as separate rows.

## 1. ICO world exports by coffee group, all forms (million 60-kg bags; coffee year Oct–Sep)

| Period | Colombian Milds | Other Milds | Brazilian Naturals | Arabicas (total) | Robustas | World | Robusta share | Source |
|---|---|---|---|---|---|---|---|---|
| CY2019/20 | – | – | – | – | – | **126.9** (−4.9%) | – | [ICO CMR Oct 2020](https://ico.org/documents/cy2020-21/cmr-1020-e.pdf) |
| CY2022/23 (Nov-24 vintage) | – | – | – | – | – | **122.92** | 39.1% (ICO statement) | [Comunicaffe/ICO](https://www.comunicaffe.com/ico-report-shows-biggest-annual-increase-on-record-for-world-coffee-exports/) |
| CY2023/24 (Nov-24 vintage) | – | – | **45.283** (+22.8%, record) | **84.678** (+15.2%) | **52.595** (+6.5%, record) | **137.273** (+11.7%) | 38.31% (derived) | [Comunicaffe/ICO](https://www.comunicaffe.com/ico-report-shows-biggest-annual-increase-on-record-for-world-coffee-exports/) |
| CY2023/24 (Nov-25 vintage) | – | – | – | **85.28** | **53.735** | **139.015** | 38.65% (derived) | [Comunicaffe/ICO](https://www.comunicaffe.com/coffee-futures-prices-soared-in-the-first-session-of-november-world-coffee-exports-flat-in-2024-25/) |
| CY2024/25 | "almost 15" (+13.5%) | "close to 27" (+2.6%) | **42.217** (−7.9%) | **84.137** (−1.3%) | **54.521** (+1.5%) | **138.658** (−0.3%) | **39.32%** (derived) | [Comunicaffe/ICO](https://www.comunicaffe.com/coffee-futures-prices-soared-in-the-first-session-of-november-world-coffee-exports-flat-in-2024-25/) |
| 12 m to Jul-2025 | – | – | – | **86.37** | **54.67** | 141.04 (derived) | 38.76% (derived) | [ICO CMR Aug 2026](https://www.ico.org/documents/cy2025-26/cmr-0826-e.pdf) |
| **12 m to Jul-2026** | – | – | – | **80.96** (−6.3%) | **60.01** (+9.8%) | 140.97 (derived) | **42.57%** (derived) | [ICO CMR Aug 2026](https://www.ico.org/documents/cy2025-26/cmr-0826-e.pdf) |
| 12 m to Oct-2020 / Oct-2021 | – | – | – | – | 49.05 / 47.19 | – | – | [ICO Trade Statistics Oct 2021](https://ico.org/show_news.asp?id=770) |

**ICO's own statement on the Robusta share:** "The share of Robustas in world coffee exports increased steadily … from **33.8% in 2020/21** to **39.1% in 2022/23** and to an estimated **39.3% in 2023/24**." Two searches returned this, but I could not confirm the exact page. The most likely source is the [ICO Coffee Report & Outlook, Dec 2023](https://icocoffee.org/documents/cy2023-24/Coffee_Report_and_Outlook_December_2023_ICO.pdf). Confidence is low for that reason.

### Green-bean exports only

| Coffee year | Colombian Milds | Brazilian Naturals | Arabicas | Robustas | World | Arabica share (ICO) | Source |
|---|---|---|---|---|---|---|---|
| 2021/22 | – | – | 74.63 | – | – | – | [ICO CMR Oct 2023](https://ico.org/documents/cy2023-24/cmr-1023-e.pdf) |
| 2022/23 | – | 34.16 (low) | **67.05 (−10.1%)** | 43.84 (low) | **110.81 (−5.5%)** | – | [ICO CMR Oct 2023](https://ico.org/documents/cy2023-24/cmr-1023-e.pdf), [TCTJ](https://www.teaandcoffee.net/news/33154/global-green-coffee-exports-drop-5-5-for-cy-2022-23/) |
| 2023/24 | – | 42.5 (F file) | – | – | 125.44 (record, Oct-24 vintage) | **63.7%** (Robusta 36.3%, derived) | [ICO CMR Oct 2024](https://www.icocoffee.org/documents/cy2024-25/cmr-1024-e.pdf) |
| 2024/25 | **13.9** (Colombia 12.39) | 39.31 (F file) | – | – | 121.26 (low; see caveat) | **63.4%** (Robusta 36.6%, derived) | [ICO CMR Oct 2025](https://www.ico.org/documents/cy2025-26/cmr-1025-e.pdf) |

## 2. Arbitrage: arabica minus robusta (ICO group indicators, US cents/lb, monthly averages)

| Month | CM − R | OM − R | BN − R | OM / R | BN / R | What ICO said | Source |
|---|---|---|---|---|---|---|---|
| 2022-11 | – | – | **73.95** (−17.2% m/m) | – | – | – | [CMR Nov 2022](https://www.ico.org/documents/cy2022-23/cmr-1122-e.pdf) |
| 2023-06 | – | – | – | – | – | "Robustas reach 28-year high amid further narrowing of the …" | [CMR Jun 2023](https://icocoffee.org/documents/cy2022-23/cmr-0623-e.pdf) |
| 2023-08 | – | – | – | – | – | "Arabica-Robusta price movements recouple in August" | [CMR Aug 2023](https://ico.org/documents/cy2022-23/cmr-0823-e.pdf) |
| 2023-10 | – | – | – | – | – | "Arabica and Robusta arbitrage remains low" | [CMR Oct 2023](https://ico.org/documents/cy2023-24/cmr-1023-e.pdf) |
| 2023-12 | – | – | – | – | – | Robustas averaged 135.47 (25-year high) | [TCTJ](https://www.teaandcoffee.net/news/33498/robustas-hit-a-25-year-high-averaging-135-47-us-cents-lb-in-december-2023/) |
| 2024-04 / 2024-08 | – | – | – | – | – | "Robustas reach 45-year high" / "47-year high for two consecutive months" | [CMR Apr 2024](https://www.icocoffee.org/documents/cy2023-24/cmr-0424-e.pdf), [CMR Aug 2024](https://www.icocoffee.org/documents/cy2023-24/cmr-0824-e.pdf) |
| **2024-10** | **55.17** (+48.3% m/m) | **54.89** (+50.6% m/m) | 33.92 (derived) | – | – | spread starts widening again | [CMR Oct 2024](https://www.icocoffee.org/documents/cy2024-25/cmr-1024-e.pdf) |
| **2025-12** | 191.79 | **190.61** | 164.85 | **2.00** | 1.87 | derived from group prices | [CMR Dec 2025](https://www.ico.org/documents/cy2025-26/cmr-1225-e.pdf) (via B_prices.csv) |
| **2026-08** | 206.83 | **180.68** | 141.61 | **2.00** | 1.78 | derived from group prices | [CMR Aug 2026](https://www.ico.org/documents/cy2025-26/cmr-0826-e.pdf) (via B_prices.csv) |

(CM = Colombian Milds, OM = Other Milds, BN = Brazilian Naturals, R = Robustas.)

**Missing:** the 2011 wide spread, the 2019 narrow spread and the peak of the 2021–22 widening were not captured.

## 3. Supply side of switching: robusta origins (ICO monthly green exports, million bags)

| Month | Brazil (conilon) | Vietnam | Indonesia | All Robustas | Brazilian Naturals | Other Milds | Source |
|---|---|---|---|---|---|---|---|
| 2024-03 | **0.85** (vs 0.11; **+686%**) | 3.22 (−10.2%) | 0.31 (−33.5%) | 5.04 (+7.8%) | – | – | [CMR Apr 2024](https://www.icocoffee.org/documents/cy2023-24/cmr-0424-e.pdf) |
| Oct-23 to Mar-24 (first half of CY) | – | – | 3.04 (−21.8%, lowest since 2018/19) | 25.16 (+8.9%) | – | – | same |
| 2024-09 | – | – | – | 3.1 (+15.4%) | 3.68 (+37.3%) | 1.92 (+22.9%) | [CMR Oct 2024](https://www.icocoffee.org/documents/cy2024-25/cmr-1024-e.pdf) |
| 2025-02 | – | 3.12 (+22.8%) | 0.39 (+170%) | 4.71 (+10.7%) | – | – | [CMR Mar 2025](https://www.ico.org/documents/cy2024-25/cmr-0325-e.pdf) |
| 2025-07 | – | – | – | 3.92 (+5.2%) | 2.69 (−16.8%) | 2.52 (+7.3%) | [CMR Aug 2025](https://www.ico.org/documents/cy2024-25/cmr-0825-e.pdf) |
| 2025-09 | – | – | – | 3.67 (+23.0%) | – | – | [CMR Oct 2025](https://www.ico.org/documents/cy2025-26/cmr-1025-e.pdf) |

Other supply-side figures:

- **Brazil:** exports reached a record 50.44 million bags in calendar 2024 ([Cecafé via Comunicaffe](https://www.comunicaffe.com/cecafe-brazils-coffee-exports-reached-a-new-all-time-high-of-50-44-million-bags-in-2024/)). Conilon exports were 5.07 million bags (+27.8%) in Jul–Dec 2024 (low confidence; page not confirmed).
- **Production by type:**
  - ICO CY2019/20: Arabica 95.68, Robusta 71.72, a 42.8% robusta share (derived; [Comunicaffe/ICO](https://www.comunicaffe.com/ico-report-world-coffee-production-to-decrease-in-2019-20-small-deficit-expected/), low).
  - USDA world robusta share (derived from workstream A rows): **43.4% in 2024/25** (75.703 of 174.395) and **44.2% in 2026/27F** (83.8 of 189.667). USDA calls 2025/26 robusta output an all-time high.
  - Workstream H has Brazil robusta at about 25.0 m in 2025/26 (implied; USDA calls it a record) and 24.4 m in 2026/27F, against arabica at 38.0 (implied) and 47.5.
  - Vietnam robusta is 31.4 m in 2026/27F, and Uganda is about 85% robusta.

## 4. Narrative: who switches, when, and at what spread

The evidence gathered here fits a two-way switching cycle. Relative supply is a confounder throughout, and this data cannot separate it from demand-side switching.

1. **2021–22: arabica shock and a wide arbitrage, followed by switching to robusta.** After the 2021 Brazil frost, arabica stayed far above robusta. The Brazilian Naturals–Robusta differential was still **73.95 c/lb in Nov 2022**, even after a 17% monthly fall. In CY2022/23, ICO green Arabica exports fell **10.1% to 67.05 M bags** (from 74.63). ICO explicitly named "**substitution towards the Robustas**" as one of two main causes; the other was consumer-country stock drawdown ([CMR Oct 2023](https://ico.org/documents/cy2023-24/cmr-1023-e.pdf)). ICO puts the Robusta share of world exports at **33.8% (2020/21) → 39.1% (2022/23)**. This is the clearest documented case of buyers switching.
2. **2023 to mid-2024: robusta demand pull closes the arbitrage.** Switching demand met Vietnamese and Indonesian shortfalls: Indonesia's first-half CY2023/24 exports were the lowest since 2018/19. Robusta prices hit a 28-year high (Jun 2023), a headlined 25-year high (Dec 2023, 135.47 c/lb), a 45-year high (Apr 2024) and a 47-year high (Aug 2024). ICO described the arbitrage as "further narrowing" (Jun 2023) and "remains low" (Oct 2023). **Brazil conilon became the swing supplier**, with March 2024 exports up 686% y/y to 0.85 M bags. Robusta exports set records of 52.6–53.7 M bags in CY2023/24, depending on vintage.
3. **Late 2024 to 2026: the arbitrage blows out again and the robusta share climbs.** In Oct 2024 the arabica–robusta spread was only about 55 c/lb, but it rose about 50% in that month alone. By Dec 2025 it was about 191 c/lb (Other Milds ≈ **2.0×** Robustas), and in Aug 2026 it was about 181 c/lb, still 2.0×. Robusta exports rose to 54.5 M in CY2024/25 while Arabica fell (Brazilian Naturals −7.9%). In the **12 months to July 2026, Robusta exports rose 9.8% to 60.01 M while Arabica fell 6.3% to 80.96 M**. That is a Robusta share of about **42.6%, up from 38.8%** a year earlier, and the highest in the data gathered here. The caveat is that part of this is supply: Brazil had a short arabica crop in 2025/26 and a record conilon crop, and Vietnam recovered.
4. **Who switches.** No roaster-level figures were captured. Brands, European roasters' robusta blend shares, Nestlé/soluble plants and US/Japanese importers are all gaps. Two structural hints:
   - The all-forms Robusta share is above the green-bean share (38.65% vs 36.3% in CY2023/24), which points to soluble/processed exports being robusta-heavy. This is an inference.
   - Brazil's domestic industry uses conilon. Workstream D records ABIC's figure of conilon costs up 201% vs arabica up 212% over 2021–2025.
5. **At what spread.** The data points are too few to estimate a threshold. What is documented: substitution was flagged when BN–R was at or above about 74 c/lb (2022). An arbitrage of about 55 c/lb (Oct 2024) was described as low. At about 180–190 c/lb (ratio about 2.0), the robusta share of exports jumped by about 4 percentage points year on year.

## 5. Gaps (not found; the search budget was exhausted)

- ICO exports by group for **CY2010/11–2018/19, 2020/21 and 2021/22**. Only an Arabica green figure exists for 2021/22. Exact all-forms levels for Colombian Milds and Other Milds are also missing.
- ICO production by type for any year other than 2019/20. USDA arabica/robusta splits for 2010–2023.
- **Robusta share of blends/consumption:** ECF, CBI, the USDA EU Coffee Annual, ABIC/Embrapa conilon share, US/Japan roasters and soluble makers. **None captured.**
- **Imports by origin:** EU, US, Japan, China. **None captured.**
- **2025 US tariffs on Brazil:** dates, rates, the Nov-2025 removal and origin switching. Not captured here. Workstream F has a title-only row ("global coffee prices plunge after trump removes tariffs on brazil", marketscreener, low), and workstream C notes mention 50% without a source.
- **Arbitrage history for 2010–2022** (2011, 2019, the 2021–22 peak).
- Conab conilon series, and Vietnam/Uganda export series by year.

## 6. Leads surfaced but not read, and a search plan

**Leads (URLs returned by searches):**

- USITC, *Is Robusta on the Rise? Trends in Coffee Species Trade*: <https://www.usitc.gov/publications/332/executive_briefings/ebot_robusta_on_the_rise.pdf>. Likely has US imports by species.
- ICO, *Growing divergence between Arabica and Robusta exports*: <https://dev.ico.org/show_news.asp?id=659>
- ICO Trade Statistics pages: Aug 2016 <https://www.ico.org/show_news.asp?id=564>, Aug 2017 <https://ico.org/show_news.asp?id=621>, Jul 2020 <http://www.ico.org/show_news.asp?id=737>. Tables: <https://ico.org/resources/trade-statistics-tables/>, <https://ico.org/documents/prices/MTS-0324_T1.pdf>
- CEPEA, *Supply reduction limits exports of robusta coffee*: <https://www.cepea.org.br/en/brazilian-agribusiness-news/supply-reduction-limits-exports-of-robusta-coffee.aspx>
- Daily Coffee News, *Brazil Coffee Report: Robusta Filling In for Lower Expected Arabica Output* (Dec 2025): <https://dailycoffeenews.com/2025/12/09/brazil-coffee-report-robusta-filling-in-for-lower-expected-arabica-output/>
- Comunicaffe, *Cecafé: Brazilian exports in July rose by 10% to 3 million bags, but Arabica shipments were at their lowest for the month since 2018*. The year is not confirmed, so it was not recorded: <https://www.comunicaffe.com/cecafe-brazillian-exports-in-july-rose-by-10-3-million-bags-but-arabica-shipments-were-at-their-lowest-level-since-2018/>
- Mintec, *Robusta coffee output and exports increase in 2018*: <https://www.mintecglobal.com/top-stories/robusta-coffee-output-and-exports-increase-in-2018>
- USDA Brazil Coffee Annual 2025 and 2026: <https://apps.fas.usda.gov/newgainapi/api/Report/DownloadReportByFileName?fileName=Coffee+Annual_Brasilia_Brazil_BR2025-0013.pdf>, <https://www.fas.usda.gov/data/gain-report/2026/06/Coffee%20Annual_Brasilia_Brazil_BR2026-0025.pdf>
- UCDA monthly reports: <https://ugandacoffee.go.ug/file-download/download/public/1168>, <https://ugandacoffee.go.ug/index.php/file-download/download/public/978>

**Next queries, in priority order.** Each needs about one search.

1. ICO coffee-year totals, using the ICO standard phrase: `"coffee year 20XX/YY" "exports of Arabica totalled" "Robusta exports amounted to"`. Run it for each year 2010/11–2021/22, or use `"twelve months ending September 20XX"` on the ico.org show_news pages.
2. `USDA "EU Coffee Annual" imports Brazil Vietnam Uganda Honduras share percent 20XX`
3. `"robusta" share blend Italy OR Germany roasters percent 20XX` (ECF, CBI)
4. `US coffee imports Brazil tariff 50% August 2025 Colombia Vietnam imports rose` and `Trump removes tariffs Brazil coffee November 2025 executive order`
5. `arabica robusta arbitrage cents record wide 2011` / `narrowest 2019` / `2022`
6. `Conab café conilon produção safra 20XX milhões de sacas`, and `Vietnam coffee exports 20XX tonnes customs`
