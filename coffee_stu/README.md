# Coffee stock-to-use vs KC/DF prices (2010/11 to 2026/27)

`Cafe_STU_vs_Prix_2010-2026.xlsx` compares USDA stock-to-use ratios with ICE arabica (KC) and robusta (DF) prices. It has 13 native Excel combo charts: STU as columns, prices as lines on a secondary axis. `stu_prix_analyse.html` holds the same charts plus a written market analysis (in French).

## Sheets

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

## Definitions

- **Country STU:** Ending stocks ÷ (domestic consumption + exports). This is the corn sheet's "Stocks / Use Domestic + Exports".
- **World STU:** Ending stocks ÷ consumption (the USDA/ICO definition). Adding exports would count the same bags twice. The (consumption + exports) version is also shown; the two correlate at 0.999.
- **Prices:** Each marketing year uses the October–September average. 2025/26 covers October 2025 to August 2026 only.

## Sources

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

## Production, stocks and certified stocks vs price

- `production_stocks_prix.html`: the page that answers whether price follows production or stocks, in French. It shows production, consumption, exports, STU, ending stocks and ICE certified stocks against KC and DF, plus the role of each country.
- `ice_stocks_certifies_ico.csv`: ICE certified stocks in million bags, June 2012 to August 2026.
  - New York (arabica) and London (robusta), from ICO Coffee Market Report Table 5.
  - The table's columns are the consecutive months ending in the report month. Where months overlap between reports, the latest report is kept.

- `arabica_production_stocks_certifies.html`: three aligned arabica charts, each with KC.
  - Arabica production.
  - Ending-stock STU.
  - New York certified stocks ÷ (domestic consumption + exports).
  - Also EU / US / Japan STU against price.
