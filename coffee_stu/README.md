# Coffee stock-to-use vs KC/DF prices (2010/11 to 2026/27)

## Research: what defines the coffee price? (`Recherche_STU_prix_cafe.docx` + `Recherche_STU_prix_cafe.xlsx`)

Both are in French. They complement the balance-sheet pair below.

- **Word:** the answer (what is solid, what is not demonstrated, what to watch), then nine sections: does the STU define the price; the world balance year by year; what moves the world STU; long-run supply and demand trends; the 2021-2025 crisis and the recovery; robusta (Brazil conilon vs Vietnam); arabica; why KC and DF move together and which one moves first; method and limits. 16 charts.
- **Excel:** 10 sheets of computed values. 8_KC_DF holds the monthly KC/DF prices, with the ratio and the spread as live formulas, and a native chart. 9_Quotidien holds the daily prices, daily returns as formulas, and the lead-lag tests.
- **`graphiques_recherche/d01-d16.png`:** the report's charts as images.
- **`donnees_journalieres/`:** daily KC1, DF1 and USD/BRL (public copy of Yahoo Finance and Investing.com data, provenance and checks in `SOURCES.md`).
- **Main findings:**
  - Price and world STU move in opposite directions over the 2010-2026 cycle (r = −0.63 for KC, −0.72 for DF). With one cycle and 16 campaigns, this cannot be demonstrated statistically: autocorrelation-adjusted p is 0.13 to 0.41, no STU measure predicts the price out of sample without 2023/24-2025/26, and annual changes show no link.
  - The importers' STU fits the price level best, but it follows the price: it falls the year after a price rise (r = −0.75 with KC).
  - Year-to-year STU swings come from crops, Brazil arabica first (44 % of the variance, first in 90 % of bootstrap draws). The other ranks are not robust.
  - The consumption trend (+2.37 M bags a year) exceeds the production trend (+2.03). The trend balance went from +1.8 M bags in 2010/11 to −2.3 M in 2025/26.
  - 2021-2025: world stocks fell four years in a row, but production was below consumption only in 2021/22 and 2022/23. The 2022/23 fall is mostly EU destocking; the 2023/24 and 2024/25 falls come from the export-import statistical gap.
  - Robusta: since 2011/12, Brazil conilon drives growth (+0.75 M bags a year, against +0.22 for Vietnam) and 53 % of supply swings. Vietnam stays the largest robusta producer by volume. The analysis starts in 2011/12 because Vietnam jumped from 19.4 to 26.0 M bags between 2010/11 and 2011/12, a one-off level shift rather than a crop swing.
  - KC and DF: monthly correlation 0.70 (0.78 since 2021). It does not come from synchronized crops but from substitution in blends and common factors. The KC/DF ratio was 1.87 in August 2026 (mean 1.82).
  - Who moves first: neither, even day by day. On daily prices (June 2021 to May 2026), the two move the same day (r = 0.67) and neither predicts the other the next day (−0.03 both ways; Granger tests not significant). After a large shock on one market, the other moves about half as much the same day and nothing the next day. The one-hour gap between the London and New York closes creates no visible lead. The Brazilian real moves both prices (weekly r ≈ −0.2) but explains almost none of the KC/DF link.
- **Checks:** two independent reviewers recomputed about 200 figures from the raw files (no numerical error) and challenged the conclusions. The report was rewritten to follow their findings, and the new figures were recomputed again from the raw USDA file.

## Balance-sheet report: `Bilan_STU_Cafe_2010-2026.xlsx` + `Bilan_STU_Cafe_2010-2026.docx`

This pair replaces the earlier files below. Both are in French.

- **Excel:** 12 sheets, 23 native combo charts (STU or production as columns, KC1/DF1 as lines on a secondary axis), about 7,250 live formulas.
  - 1_Monde: world production, STU = ending stocks ÷ (domestic consumption + exports), and certified-stock STU (ICE New York + London), with KC1 and DF1.
  - 2_Arabica / 3_Robusta: the same for each species, built country by country over the 42 origin countries.
  - 4_STU_pays: STU of each origin country, year by year, with size, shock and stock-cushion weights.
  - 5_Analyse and 6_Situations: price reactions, certified stocks vs price, the price/STU curve, regimes, robustness checks, and what the price did when USDA and certified stocks diverged.
  - 8_Graphiques_pays: Brazil and Vietnam production, world STU (both definitions), Brazil and Vietnam STU, arabica origins (Brazil, Colombia, Ethiopia) and robusta origins (Vietnam, Brazil, India, Uganda, Indonesia) STU, certified-stock STU, and EU / US STU, each with its price (12 charts). EU and US also get the stocks ÷ consumption and stocks ÷ (consumption + imports) variants.
  - 7_Bresil_arabica: Brazil alone. Arabica production, Brazil STU and KC1. USDA publishes one Brazil stock figure for arabica and conilon together, so the arabica-share method gives an arabica STU equal to Brazil's total STU; an upper bound (all stocks arabica) is shown alongside.
  - Donnees_USDA, Prix_ICE, Stocks_certifies: all source data.
- **`Graphiques_STU_pays_2010-2026.pdf`** and `graphiques/g01-g12.png`: the same 12 charts as images, two per page.
- **Word:** the written report with 14 charts (including Brazil alone), tables, and a landscape annex of country STUs.
- **Checks:** every figure was recomputed independently from the raw files (no mismatch on about 15,000 values). An adversarial review then tested each conclusion, and the text keeps only what the data support.

Changes from the earlier files:

- **Net-importing producers excluded.** The United States, the Philippines, China, Panama and Venezuela produce some coffee but import more than they export. They are now excluded from the arabica and robusta STU (they stay in the world total). Arabica STU is 1.9 to 4.6 points lower as a result; the correlations barely move.
- **World STU definition.** World STU now uses ending stocks ÷ (consumption + exports), as requested.
- **Weaker claims, stated as such.** The convexity of the price/STU curve, the certified-stock "rules" and the certified-stock timing effects are fragile. They rest on 16 autocorrelated campaigns and mostly on 2023/24–2025/26.

The earlier files below are kept for reference and still contain the old arabica STU (with the US).

## Earlier files

`Cafe_STU_vs_Prix_2010-2026.xlsx` compares USDA stock-to-use ratios with ICE arabica (KC) and robusta (DF) prices. It has 13 native Excel combo charts: STU as columns, prices as lines on a secondary axis. `stu_prix_analyse.html` holds the same charts plus a written market analysis (in French).

### Sheets

- **1_Monde:** World STU (ending stocks ÷ consumption) with KC and DF.
- **2_Arabica_Robusta:** Arabica and robusta STU across all 47 producing countries, each country weighted by that species' share of its production.
- **3_Groupes_pays:** The same ratios built from country lists.
  - Arabica: Brazil, Colombia, Honduras, Ethiopia, Peru, Mexico, Guatemala, Costa Rica.
  - Robusta: Brazil, Vietnam, Indonesia, Uganda.
  - Brazil is split by its arabica/conilon production share. Two extra columns give the plain sum, with Brazil counted in full in both lists.
- **4_Deux_pays:** Two columns per year: Brazil + Colombia with KC, and Vietnam + Brazil with DF.
- **5_Bresil_Vietnam:** Brazil alone with KC, and Vietnam alone with DF.
- **6_Surplus:** (production + imports − consumption − exports) ÷ (consumption + exports).
  - Groups: Brazil, arabica 6 (Brazil, Colombia, Honduras, Mexico, Peru, Nicaragua), Vietnam, and robusta 4 (Vietnam, Brazil, Uganda, Indonesia).
- **Tableau_STU:** Countries and aggregates as rows, marketing years as columns, colour-scaled by row.
- **Analyse:** The analysis sheet. All formulas stay live.
  - Correlations (CORREL).
  - The fitted curve ln(price) = a + b ÷ STU (INTERCEPT, SLOPE, RSQ).
  - Its application to 2026/27.
  - Price regimes, supply-volatility shares and conclusions.
- **Prix_ICE:** Monthly prices from October 2010 to August 2026 and their October–September averages.
- **Donnees_USDA:** All 93 PSD countries.
  - Blocks for production, arabica, robusta, stocks, imports, consumption and exports.
  - Species shares.

### Definitions

- **Country STU:** Ending stocks ÷ (domestic consumption + exports). This is the corn sheet's "Stocks / Use Domestic + Exports".
- **World STU:** Ending stocks ÷ consumption (the USDA/ICO definition). Adding exports would count the same bags twice. The (consumption + exports) version is also shown; the two correlate at 0.999.
- **Prices:** Each marketing year uses the October–September average. 2025/26 covers October 2025 to August 2026 only.

### Sources

- **Volumes:** USDA FAS PSD Online coffee file, July 2026 update. 2026/27 is the June 2026 forecast.
- **Prices:** ICO Coffee Market Report, Table 1.
  - Monthly averages for ICE New York and ICE London, taken as the average of the 2nd and 3rd positions: a proxy for KC1/DF1.
  - ICO converts London to US cents/lb; US$/t = cents/lb × 22.0462.
  - 81 reports were downloaded from ico.org and 62 of them contain the table. Together they cover every month.
  - Months that appear in several reports agree, except for small later revisions; the latest report is kept.
  - Recomputed calendar averages for 2011–2013 match the ICO's published values exactly.
- **CSV files:**
  - `ice_prix_mensuels_ico.csv`: the monthly prices, with the source report for each month.
  - `stu_series.csv`: all ratio series and the price averages.

### Production, stocks and certified stocks vs price

- `production_stocks_prix.html`: the page that answers whether price follows production or stocks, in French. It shows production, consumption, exports, STU, ending stocks and ICE certified stocks against KC and DF, plus the role of each country.
- `ice_stocks_certifies_ico.csv`: ICE certified stocks in million bags, June 2012 to August 2026.
  - New York (arabica) and London (robusta), from ICO Coffee Market Report Table 5.
  - The table's columns are the consecutive months ending in the report month. Where months overlap between reports, the latest report is kept.

- `arabica_production_stocks_certifies.html`: three aligned arabica charts, each with KC.
  - Arabica production.
  - Ending-stock STU.
  - New York certified stocks ÷ (domestic consumption + exports).
  - Also EU / US / Japan STU against price.
