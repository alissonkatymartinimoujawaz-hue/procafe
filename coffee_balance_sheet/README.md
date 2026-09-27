# Coffee balance sheet (USDA, June 2026)

`Coffee_Balance_Sheet_USDA_2026.xlsx` reproduces the layout of the user's corn balance sheet with coffee data.

## Sheets

- **Country sheets:** Brazil, Vietnam, Colombia, Ethiopia, Indonesia, Uganda and Honduras, plus Others (= World minus these seven).
  - Rows run from 2010/11 to 2025/26, then 2026/27 (USDA Jun 2026), 2026/27 (USDA attaché), and 2026/27 My Estimate.
  - Columns: Area Harvested, Yield, Beginning Stocks, Production, Imports, Total Supply, Roast & Ground and Soluble consumption (the coffee counterparts of Feed & Residual and FSI), Total Consumption, Exports, Ending Stocks, Total Distribution, and Stocks/Use.
- **World:** the World total for 2010/11 to 2024/25, then blocks by region for 2025/26, 2026/27 (USDA Jun 2026) and 2026/27 My Estimate.
  - Regions: World, Ex Brazil, Major Exporters (the seven countries and Others), Major Importers (EU, US, Japan, Philippines, Canada, UK, Russia, Korea and Others), and Selected Other (China).
  - Headers are bilingual Chinese/English, as in the corn sheet.

## Sources

- **Balance:** USDA FAS PSD Online coffee database (July 2026 update, which holds the June 2026 forecast), in 1,000 60-kg bags, for all 93 countries.
- **2026/27 attaché row:** the "New Post" column of each 2026 USDA GAIN Coffee Annual: BR2026-0025, VM2026-0016, CO2026-0008, ET2026-0005, ID2026-0021, UG2026-0001 and HO2026-0002.
- **Area harvested:** FAOSTAT item 656 (`national_data/faostat_coffee_all_countries.csv`).
  - Year mapping: calendar year Y goes to marketing year Y/Y+1, except Mexico and Uganda, which go to Y-1/Y.
  - Only countries with USDA production in that year are counted.
  - China is left out: FAO's imputed 32,000 ha against USDA production would give about 60 bags/ha.
  - FAO data end in 2024, so the last value is carried forward and shown in grey italics.
  - The USDA PSD has no coffee area.

## My Estimate

- **Inputs:** yellow cells with blue figures. They start at the USDA June values.
- **Calculated:**
  - Production = area × yield.
  - Beginning stocks = the previous year's ending stocks.
  - Ending stocks = supply − consumption − exports.
- **World sheet:** the seven exporters link to their country sheets. The other rows are inputs.

## Checks (27 Sep 2026)

- All 1,395 formulas were recomputed independently and match their cached values.
- 2,423 values were checked against the PSD file and FAOSTAT.
- Supply equals distribution on every row.
- World 2026/27 totals match the USDA circular: production 189.7, consumption 179.7 and ending stocks 26.3 million bags.
- Every sheet validates against the OOXML schema.
- A simulated edit flows through: a lower Brazil yield changes World production, ending stocks and the Others sheet as expected.
