# Workstream H: marginal producers (supply side)

Status as of 2026-09-24: **incomplete, blocked by the search budget.**
The session-wide WebSearch budget (200 of 200 calls, shared with the other workstreams) ran out after this workstream had made 13 searches. All later calls returned "Web search was not performed". Direct downloads are blocked by egress policy. Under the rule that every value must come from a search result, the only data captured is the **June 2026 vintage** (USDA WM&T June 2026 plus the May–June 2026 GAIN Coffee Annuals). **No historical series (2005/06 to 2023/24), cost-of-production, hectare or crop-switch data was captured.** No value in this file or the CSV comes from memory.

- Data: `research/coffee-demand/data/raw/H_producers.csv` (38 rows: 31 numeric, 7 qualitative evidence rows)
- Dataset names used:
  - `production_usda`: USDA official figures (WM&T or PSD), sometimes via press.
  - `production_usda_gain`: FAS post (attaché) figures, which are not USDA official.
  - `production_{arabica,robusta}_usda[_gain]`: arabica and robusta splits.
  - `producer_response_event`: qualitative evidence.
  - `area_share`, `production_share_*`: shares.
- Rows marked "IMPLIED" are simple arithmetic on a single source sentence, for example "rise 8.9 million to 71.9 million" gives 63.0 for the previous year. They carry medium or low confidence. Nothing is interpolated.

## 1. Country table (million 60 kg bags, USDA marketing years)

| Country | 2024/25 | 2025/26 | 2026/27 (fcst) | Source / note |
|---|---|---|---|---|
| World | – | 178.8 (med.) | **189.7** record | WM&T Jun-2026; comunicaffe 189.667 |
| World arabica / robusta | – | – | 105.867 / 83.8 | comunicaffe quoting WM&T |
| Brazil total | – | 63.0 (implied) | **71.9** record | WM&T Jun-2026 |
| Brazil arabica | – | 38.0 (implied) | **47.5** | WM&T: "ending a 5-year period of underperformance" |
| Brazil robusta (conilon) | – | 25.0 (implied, record) | **24.4** | WM&T |
| Vietnam | 29 (low conf.) | 31.7 | **32.5** record (R 31.4 / A 1.1) | WM&T + GAIN VM2026-0016 |
| Colombia | – | 12.5 (implied, low) | **13.4** (post) | GAIN May-2026; USDA official not captured |
| Indonesia | – | 12.4 (implied) | **11.4** WM&T / 11.38 post | comunicaffe + GAIN |
| Ethiopia | – | – | **12.1** record | GAIN ET2026-0005 (12.10) + press (WM&T) |
| Uganda | – | 7.1 (post) | **7.2 post / 7.1 WM&T?** record | CONFLICT, see CSV notes |
| Honduras | – | 5.5 (implied) | **6.0** | WM&T |
| Central America + Mexico | – | – | **17.7** | WM&T; rebound in CR, GT, HN, MX, PA |
| India | – | – | – | WM&T says output falls in 2026/27; no number captured |
| Peru, Mexico, Guatemala, Nicaragua, Costa Rica, El Salvador, Côte d'Ivoire, Kenya, Tanzania, Laos, PNG, Ecuador, China | – | – | – | **not captured** |

All years 2005/06 to 2023/24 are gaps for every country.

## 2. Producer classification (evidence captured so far)

| Class | Origins with captured evidence | Evidence (USDA wording) | Price threshold evidence |
|---|---|---|---|
| **Expands when prices are high** | Vietnam | "Recent high prices allowed coffee growers to increase expenditures on fertilizers and other inputs"; "expansion driven by 2024-2025 price peaks". 31.7 → 32.5 Mbags, record | none captured |
| | Uganda | "expansion in area under production, supported by sustained high prices in recent years". 7.1 → 7.2 Mbags, about 85% robusta | none captured |
| | Ethiopia | "gradual yield improvements, better farm management... rehabilitation of aging tree stock". Record 12.1 Mbags, overtakes Indonesia as #4 | none captured |
| | Brazil conilon | Record robusta harvest in 2025/26 (implied 25.0), easing to 24.4 in 2026/27 | none captured |
| **Weather-driven, not price-driven (2026/27)** | Brazil arabica (+9.5 Mbags rebound), Colombia (+7.2%, dry weather), Indonesia (−8%, excess rain in robusta areas) | Sources quoted in the CSV | n/a |
| **Cuts when prices are low (2018–19 low)** | none captured | — | ICO composite / arabica < 100 c/lb evidence not captured |
| **Keeps producing whatever the price** | none captured | — | — |
| **Declines even at high prices** | none captured | Honduras and Central America are forecast to *rebound* in 2026/27 (HN 5.5 → 6.0; region 17.7) | — |

The brief's hypotheses have **not** been tested and must not go into the deck until evidenced:

- Central America and Mexico cut output after rust and low prices.
- Vietnam shifted area from coffee to durian and pepper.
- Côte d'Ivoire shifted to cocoa and rubber.
- Kenya lost coffee land to real estate.
- El Salvador, Côte d'Ivoire, Mexico, Tanzania and Kenya are in structural decline.
- Brazil conilon (ES, RO, BA), Laos and Indonesia expanded in 2021–26.

## 3. Cost of production / breakeven: GAP

Nothing was captured on CONAB custos (arábica or conilon, R$/saca), FNC costs, ICO CDR 2019 profitability, Vietnam VND/kg, Uganda, Ethiopia, Kenya, Honduras or Guatemala. The 2018–19 "prices below cost" statement with its numbers was not captured either.

## 4. Area: GAP (one item)

GAIN VM2026-0016 (citing MARD) states that robusta is about 90% of Vietnam's coffee area. Hectare totals were not captured for:

- Vietnam 2015–2025
- CONAB area for Brazil arabica and conilon
- Honduras
- Colombia renovation hectares
- Uganda planting programmes

## 5. Source URLs found (numbers not yet extracted), for the rerun

- WM&T June 2026: https://www.fas.usda.gov/sites/default/files/2026-07/coffee.pdf
- Current circular: https://apps.fas.usda.gov/psdonline/circulars/coffee.pdf
- ESMIS archive of all past WM&T issues: https://esmis.nal.usda.gov/publication/coffee-world-markets-and-trade
- GAIN Coffee Annuals 2026:
  - Brazil BR2026-0025: https://www.fas.usda.gov/data/gain-report/2026/06/Coffee%20Annual_Brasilia_Brazil_BR2026-0025.pdf
  - Honduras HO2026-0002: https://apps.fas.usda.gov/newgainapi/api/Report/DownloadReportByFileName?fileName=Coffee+Annual_Tegucigalpa_Honduras_HO2026-0002.pdf
  - Guatemala: https://www.fas.usda.gov/data/gain/2026/04/guatemala-coffee-annual
- Brazil Semi-annual BR2025-0048: https://apps.fas.usda.gov/newgainapi/api/Report/DownloadReportByFileName?fileName=Coffee+Semi-annual_Brasilia_Brazil_BR2025-0048.pdf
- Vietnam Semi-annual VM2025-0051: https://apps.fas.usda.gov/newgainapi/api/Report/DownloadReportByFileName?fileName=Coffee+Semi-Annual_Ho+Chi+Minh+City_Vietnam_VM2025-0051.pdf
- Vietnam Annual VM2025-0018: https://apps.fas.usda.gov/newgainapi/api/Report/DownloadReportByFileName?fileName=Coffee+Annual_Hanoi_Vietnam_VM2025-0018.pdf
- StoneX, "USDA Attaché Reports Reveal a Fragile New Phase for Global Coffee Supply": https://www.stonex.com/en/insights/usda-attache-reports-reveal-a-fragile-new-phase-for-global-coffee-supply/
- IndexMundi (a USDA PSD mirror) is **not usable**: its table values are not in the indexed text.

## 6. Rerun plan (for when CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION is raised)

Priority order:

1. Summary tables from WM&T are not indexed, so pull figures from the narrative text instead. Use one query per vintage, for example `"Coffee: World Markets and Trade" June 2019 Vietnam Colombia Honduras production`. Vintages: Dec-2005, Jun-2006, Jun/Dec-2010, Jun/Dec-2012, Jun-2013, Jun/Dec-2015, Jun/Dec-2017 to 2025. Also use comunicaffe's write-ups of each release, which list many countries.
2. GAIN Coffee Annuals per country and year: Honduras, Guatemala, Mexico, Nicaragua, Costa Rica, El Salvador, Peru, Ecuador, India, Kenya, Tanzania, China. Use `allowed_domains` fas.usda.gov / apps.fas.usda.gov. Laos, PNG and Côte d'Ivoire have no GAIN coffee report, so use ICO or national sources.
3. Costs:
   - `CONAB custo de produção café arábica Sul de Minas R$/saca 2025` and `conilon Espírito Santo`
   - `FNC costo de producción carga café 2024`
   - `ICO Coffee Development Report 2019 cost of production Brazil Colombia Honduras`
   - `giá thành sản xuất cà phê đồng/kg`
4. Behaviour:
   - `diện tích sầu riêng thay thế cà phê ha`
   - `IHCAFE producción quintales 2012-13 roya`
   - `Kenya AFA coffee production tonnes 2019/20`
   - `Côte d'Ivoire production café tonnes baisse cacao hévéa`
   - `El Salvador producción café quintales CSC`
   - `Espírito Santo conilon recorde Conab 2025`
