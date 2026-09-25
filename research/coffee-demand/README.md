# Coffee demand research pack (September 2026)

Deep-dive on the **demand side** of the world coffee market, 2005 → 2026, with a look at the supply-side marginal producer.

| Deliverable | File |
|---|---|
| PowerPoint deck (42 slides, native editable charts) | `output/Coffee_Demand_Research_2026.pptx` |
| Word learning guide (concepts, every chart explained, full tables, sources) | `output/Coffee_Demand_Learning_Guide_2026.docx` |
| Chart images used in the guide | `output/charts/*.png` |
| Every headline number (machine-readable) | `output/metrics.json` |

## What the pack answers

1. **Global picture** – world demand year by year since 2005/06, growth vs supply, stocks-to-use and prices, who consumes the most, where the growth came from, why it grows (population vs per-capita, income, headroom).
2. **Demand segments & drivers** – buyer groups (traditional importers / emerging importers / producing countries), formats (roast & ground vs instant), coffee-shop chains, income and urbanisation.
3. **Marginal buyers** – arabica & robusta prices 2010–2026, three kinds of buyer (keep growing / inelastic / cut back) with nine country cards, measured elasticities, retail pass-through, Brazil's threshold, the price increase at which demand cracks, and arabica↔robusta switching.
4. **Marginal producers** – who keeps producing at low prices, who cuts, who declines even at high prices, who expands; 2026/27 supply response.
5. **Trackers** – consumption and production by country: increasing, steady or decreasing.

## Data and provenance

All numbers are computed by `scripts/analysis.py` from:

| Source | File | Notes |
|---|---|---|
| USDA FAS PSD coffee, all countries, 1960–2025/26 (Dec-2025 release) | `data/source_files/usda_psd_coffee_dec2025vintage_via_foodberg.csv.gz` | Official `psd_coffee_csv.zip` as downloaded on 21-Jun-2026 by the public project andenick/Foodberg; 98% of values identical to an independent copy of the Jun-2024 release (`..._2024vintage_via_mal303.csv.gz`); world totals match USDA's Dec-2025 report |
| USDA Coffee: World Markets and Trade, Jul-2026 | `data/raw/A_world_balance.csv`, `C_importers.csv`, `H_producers.csv` | 2026/27 forecasts, verified through web search (URLs per row) |
| IMF Primary Commodity Prices (ICO Other Milds, Robustas) | `data/source_files/imf_pcps_external-data_2026-03.xls` | Monthly 1990-01 → 2025-09; annual averages match the World Bank Pink Sheet |
| ICO Coffee Market Reports (prices Oct-2025→Aug-2026, exports by group Sep-2015→Jul-2026) | `data/source_files/ico_cmr_mirror/` | Tables parsed by BMR-Com/coffee-analytics; 22/22 values found independently by web search match |
| ICO historical importing-country data (to 2019) | `data/source_files/Coffee_*.csv` | Used for the EU member-state breakdown |
| ABIC (Brazil consumption), IBGE IPCA, BLS CPI | `data/raw/D_*.csv`, `F_*.csv`, `B_prices.csv` | Per-row URLs and confidence |
| World Bank population & GDP per capita | `data/source_files/wb_*.csv` | WDI series |
| Starbucks / Luckin store counts | `data/raw/E_drivers.csv` | 10-K / 20-F; low-confidence rows are not charted |

`data/raw/*.csv` hold every value collected by the research agents with its source URL, a short quote and a confidence level (see `data/raw/SCHEMA.md`); `notes/*.md` hold the narrative findings and the gaps of each workstream. `data/clean/*.csv` are the analysis tables.

## Rebuild

```bash
pip install pandas numpy matplotlib python-pptx python-docx xlrd pyarrow
python research/coffee-demand/scripts/fetch_official_data.py   # optional: re-download the official files (needs open internet)
python research/coffee-demand/scripts/build_all.py             # analysis -> charts -> deck -> Word guide
```

`fetch_official_data.py` downloads USDA PSD, the World Bank Pink Sheet, IMF, FRED, US Census (imports by origin), UN Comtrade and Eurostat Comext, and logs URL, timestamp and SHA-256 of every file in `data/source_files/MANIFEST.csv`. It could not be run in the sandbox that produced this version (those hosts were blocked), so its URLs are documented but untested here.

## Known limits

- USDA consumption for importing countries is *disappearance* (imports − re-exports ± stocks): single years include inventory swings; the analysis reads trends on 3-year averages.
- No official home-vs-café split exists outside Brazil (ABIC: retail 73–78% of volume); café chains are used as a proxy.
- Import-origin data (Eurostat, US Census, Comtrade) and cost-of-production surveys (CONAB, FNC, ICO) are not yet included.
