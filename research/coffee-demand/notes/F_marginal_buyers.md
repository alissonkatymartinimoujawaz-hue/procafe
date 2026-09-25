# Workstream F: marginal buyers (who cut consumption when prices rose)

Status as of 2026-09-24: **PARTIAL. Only Brazil is covered in depth.**

- The web-search budget for the whole session (200 WebSearch calls, shared by all parallel workstreams) ran out after I had made only **14 searches**. Every search after that returned "Web search was not performed: this session has used its web search budget (200 of 200)". Direct downloads were already blocked by the egress policy. Nothing below comes from memory. Every number is in `data/raw/F_marginal_buyers.csv` (43 rows) with its URL.
- **Data-hygiene incident, needs fixing.** Another workstream's helper script at the shared scratchpad path `scratchpad/addrows.py` replaced mine, and that script writes to `G_switching.csv`. As a result, my first 25 Brazil rows were appended to `/home/user/procafe/research/coffee-demand/data/raw/G_switching.csv` **twice** (50 rows: `consumption_national`, `retail_price_change_pct` and similar; source_org ABIC or IBGE). When I checked, that file held a header plus only those 50 rows. The permission system blocked my attempt to remove them. The orchestrator or workstream G should delete them. The correct copies are in `F_marginal_buyers.csv`.

## 1. Summary by market

| Market | Classification | Volume evidence | Price context at the time | Threshold or lag | Status |
|---|---|---|---|---|---|
| **Brazil** (2nd-largest consumer) | **Declining, elastic (moderate, with a lag)**. Recovers fast when prices fall. | ABIC: 2022 **-1.01%** (21.33m bags); 2025 **-2.31%** (21.409m bags); per capita 2025 **-3.88%** (4.82 kg R&G). Recovery in 2026: Jan-Aug **+2.29%** (13.689m bags), May-Aug **+4.65%** | IPCA ground coffee (café moído): 2024 **+39.6%**; 12m to Mar-2025 **+77.78%**; peak 12m to May-2025 **+82.24%**; 2025 Dec/Dec +35.65% or +41.84% (sources conflict). 12m to Jul-2026 **-17.2%**, the largest fall since the 1994 Plano Real | Volume still grew **+1.11%** in 2024 even though retail prices rose 39.6%. Volume fell only once 12-month retail inflation reached about **+78-82%** (H1 2025). It rebounded within 1-2 quadrimesters once retail inflation turned negative | Covered |
| World (ICO) | Flat volumes at record prices | ICO CY2024/25 exports **138.66m bags, -0.3%** vs 139.01m. Brazilian Naturals exports -7.6%, which reflects supply. ICO consumption outlook for 2023/24 (made Dec-2023, before the spike): **177.0m, +2.2%**, with non-producing countries +2.1% | ICO composite annual average 2024 = 229.34 c/lb vs 165.23 in 2023, **+38.8%**. Monthly peak 354.32 in Feb-2025. See `B_prices.csv` | Not found: an ICO statement that 2024/25 consumption growth slowed because of prices | Thin |
| United States | Not assessed | None found | BLS import coffee price index **-2.6% y/y** in May-2023, "following large increases" | Tariffs on Brazil: only a news headline shows they were removed. **Dates and rates not captured** | Gap |
| Japan (AJCA), EU/Eurostat, Germany/Italy (DKV), Russia, China, South Korea, MENA (Algeria, Morocco, Egypt, Saudi Arabia, Turkey), SE Asia (Philippines, Indonesia, Vietnam), lower-income importers | **Not assessed** | Not searched (budget exhausted) | Not searched | n/a | **Gap** |
| Elasticity literature (ICO, ERS, FAO, World Bank, papers); green-coffee share of retail and café prices; pass-through lags | Not assessed | n/a | Only indirect Brazil pass-through evidence (see §2.4) | n/a | **Gap** |
| Earlier spikes: 2011 (>300 c/lb) and 2014 | Brazil only, via workstream D | `D_producer_consumption.csv` (ABIC): 2011 +3.11% (19.72m), 2012 20.33m, 2013 **-1.23%** (20.08m, "first fall in 10 years"), 2014 +1.24%, 2015 +0.86% | Not captured | Causes of the 2013 dip not established. No robusta-share evidence | Gap |

## 2. Brazil in detail (the one fully documented case of demand destruction)

### 2.1 Episode 1: the 2021 frost spike leads to a 2022 dip
- ABIC Nov-2021 to Oct-2022: **21.33m bags, -1.01%** (prior year 21.54m). ABIC blamed "o impacto da inflação acumulada e da diminuição do poder de compra" (accumulated inflation and lost purchasing power). Source: https://mercadoeconsumo.com.br/03/03/2023/economia/abic-consumo-brasileiro-de-cafe-cai-1-em-2022-ante-2021/
- Green prices, from `B_prices.csv` (ICO CMRs): ICO composite rose from 117.37 c/lb (Dec-2019) to 203.06 (Dec-2021). I did not capture the IPCA ground-coffee rate for 2021-22.
- Consumption recovered to +1.64% in 2023 (21.7m bags).

### 2.2 Episode 2: the 2024-25 spike leads to a 2025 decline. "Consumption fell 2.3% after retail prices rose about 40% a year for two years"
- 2024: retail ground coffee **+39.60%** (IPCA, Dec/Dec) while ABIC volume still grew **+1.11%** to 21.916m bags. Demand did not respond in the first year.
- H1 2025: 12-month retail coffee inflation reached **+77.78%** (March) and peaked at **+82.24%** (May). Year-to-date inflation was +30.04% by March and +42.10% by May. Monthly inflation slowed from +4.59% in May to +0.56% in June.
- ABIC 2025 (Nov-24 to Oct-25): **21.409m bags, -2.31%**; per capita **-3.88%** (6.02 kg green / 4.82 kg R&G). Industry revenue rose **+25.6% to R$46.24bn**: value up, volume down.
- Monthly retail volumes in workstream D's file (ABIC via Agência Brasil): Jan-25 +1.26%, Feb-25 +0.89%, Mar-25 **-4.87%**, Apr-25 **-15.96%** y/y. Jan-Aug 2025 year to date: **-5.4%**. The volume break coincided with 12-month retail inflation above about 75%.
- Retail price measures differ. ABIC's retail survey (average R&G price in the Southeast) shows **+5.8%** end-2024 to end-2025 (R$59.96/kg at end-2025, peak R$70.52/kg in July). IPCA Dec/Dec 2025 shows **+35.65%** in one source and **+41.84%** in another. Both IPCA figures are low confidence; check them against IBGE SIDRA table 7060.
- Illustrative arithmetic only, **not a published elasticity**: a -2.3% (total) or -3.9% (per capita) volume change set against retail inflation of roughly +36-82% implies a ratio of about -0.05 to -0.1. Brazilian home consumption is price-inelastic but not zero. The response came with a 6-12 month lag.

### 2.3 Episode 3: the 2026 unwind. "Consumption +4.65% once retail prices fell 17-21%"
- ABIC: Jan-Apr 2026 **+2.44%** (4.9m bags); May-Aug 2026 **+4.65%**; Jan-Aug 2026 **13.689m bags, +2.29%**. ABIC forecasts **+2.5%** for 2026.
- IPCA ground coffee: 12m to Apr-2026 **-5.99%** (April m/m -2.30%); 12m to Jul-2026 **-17.2%** (São Paulo -18.38%, Belo Horizonte -23.51%). Workstream D: ABIC traditional R&G price was R$49.50/kg in Aug-2026 vs R$62.83 in Aug-2025, **-21.22%**.
- Demand in Brazil is **symmetric and fast to recover**. That makes it a swing factor for Brazil's exportable surplus: 1% of Brazilian consumption is about 0.21m bags.

### 2.4 Pass-through (indirect, from workstream D)
- ABIC, 2021-2025: retail R&G price **+116%**, while green costs rose **+201% (conilon)** and **+212% (arabica)** (Agência Brasil, Jan-2026). In percentage terms, retail rose about half as much as green, consistent with a non-coffee cost share of roughly half the retail price. I did not independently re-verify this. The source URL is in `D_producer_consumption.csv`.

## 3. Everything else: gaps and a ready-to-run query list
Once the session search cap is raised (`CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION`), rerun workstream F for these queries. They are phrased so the number appears in the page text.
1. Japan: `全日本コーヒー協会 日本のコーヒー需要 2025年 トン` and `コーヒー需要 2024年 前年比 減少 全日本コーヒー協会`. Also Japan CPI コーヒー豆 前年同月比 2025.
2. EU: USDA GAIN "Coffee Annual" European Union 2025 (allowed_domains fas.usda.gov / apps.fas.usda.gov); Eurostat "green coffee" imports 2025 vs 2024; HICP coffee y/y 2025 (ec.europa.eu).
3. Germany/Italy: "Deutscher Kaffeeverband" Kaffeemarkt 2025 Pro-Kopf Liter / Tonnen; Italy "consumi caffè" 2025 calo prezzi.
4. US: USDA "Coffee: World Markets and Trade" June 2026 US consumption/imports; "U.S. green coffee imports 2025" tariffs Brazil 50% (dates of imposition and removal, Nov-2025 executive order); BLS CPI "coffee" 12-month 2025; NCA NCDT 2025/2026 "past-day".
5. Russia `импорт кофе 2025 тонн снизился`; China `中国 咖啡 进口 2025 吨 海关`; Korea `커피 수입량 2025 톤 관세청`.
6. MENA: Algeria `importations café Algérie 2025 tonnes`; Morocco `importations café Maroc 2025 Office des changes`; Egypt, Saudi Arabia and Turkey import volumes (USDA GAIN posts).
7. SE Asia: USDA GAIN Coffee Annual Philippines, Indonesia and Vietnam 2025 (domestic consumption, instant coffee).
8. Elasticity: "price elasticity of demand for coffee" ICO / ERS / meta-analysis; "green coffee share of retail price"; "pass-through" green to retail coffee lag months.
9. 2011/2014: ICO "consumption" 2011/12 growth slowed prices; "robusta share" blends 2011 2014.

## 4. Files
- Data: `/home/user/procafe/research/coffee-demand/data/raw/F_marginal_buyers.csv` (43 rows). Datasets: `consumption_national`, `consumption_national_change_pct`, `consumption_national_ytd`, `consumption_per_capita(_change_pct)`, `consumption_forecast_change_pct`, `industry_revenue`, `retail_price_change_pct`, `exports_world_ico(_change_pct)`, `exports_ico_group`, `consumption_world_ico(_change_pct)`, `import_price_change_pct`, `tariff_event`.
- Cross-referenced, not duplicated: `B_prices.csv` (ICO composite and group prices) and `D_producer_consumption.csv` (ABIC 2003-2026 series, ABIC monthly retail volumes and prices, pass-through).
