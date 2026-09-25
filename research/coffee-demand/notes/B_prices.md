# Workstream B - Coffee prices 2005-2026 (green coffee and retail)

*Research date: 2026-09-24. Data file: `data/raw/B_prices.csv` (2,055 rows, 32 datasets, standard schema). Units: ICO and futures prices in US cents/lb; World Bank in USD/kg (1 USD/kg = 45.3592 US cents/lb).*

## 0. How the data was obtained (read this first)

- **WebSearch ran out almost at once.** The whole session shares a cap of 200 WebSearch calls. This workstream got **14** of them before the cap was hit, because other workstreams running in parallel used the rest. Direct downloads from ico.org, worldbank.org, bls.gov, ibge.gov.br, eurostat and the press are blocked (403). Only about 32 CSV rows come from those 14 searches: ICO Coffee Market Report (CMR) figures such as the monthly I-CIP for 12/2019, 11-12/2021, 12/2022, 12/2023, 12/2024, 12/2025 and 01/2026, the ICO 2023 and 2024 annual averages, and the 2019 lows.
- **Everything else came from GitHub code search.** This is a read-only search API that returns indexed file fragments. No repositories were added to the session. I used it to find public copies of official files, then took numbers from the returned fragments:
  - **World Bank:** CMO Historical Data (Pink Sheet). Annual file "Updated on March 03, 2026" covers 1960-2025. Monthly files are the Dec-2024 and "Updated on January 03, 2025" vintages, so monthly data ends at 12/2024. The header row was checked: column 12 is "Coffee, Arabica" and column 13 is "Coffee, Robusta".
  - **ICO historical dataset** `indicator-prices.csv`, monthly 1990-2018. The file stores values as (US cents/lb)/45.3. Multiplying by 45.3 gives back the exact 2-decimal ICO values.
  - **ICO CMR price tables for 10/2014-08/2026**, parsed by the `BMR-Com/coffee-analytics` project, plus the full CMR text for Feb, Mar, May, Jun and Aug 2026.
  - **US BLS:** a saved API response for CPI-U coffee (CUUR0000SEFP01), with annual averages (M13) for 2004-2024.
  - **Brazil IBGE:** SIDRA IPCA subitem 7392 (café moído), monthly % changes and a chained index from 2019 to 08/2026.
  - **News-archive copies** of AP, The Center Square, CNN and InfoMoney articles, used for 2026 retail y/y figures and some price drivers.
- **Checks that passed:**
  - (a) All **48** monthly figures quoted in ICO CMR text match the table values exactly.
  - (b) The ICO dataset and the CMR-table parse agree exactly on the 9 months where they overlap.
  - (c) ICO Other Milds and Robustas agree with the World Bank Arabica and Robusta series to within 1.5% in every month of 2019-2024, except the garbled 02/2019 row.
  - (d) A plain average of the 12 monthly I-CIP values gives exactly ICO's official **2023 = 165.23** and **2024 = 229.34**. Rows marked `_calc` use this same method.
  - (e) The ICO calc annual averages for Other Milds and Robustas equal the official World Bank annual Arabica and Robusta averages to within 0.52 c/lb in every year from 2005 to 2025. The small gap is WB rounding to 2 decimals.
- **Confidence labels.** `high` means an ICO CMR statement I actually saw, or a table value that a CMR statement confirms. `medium` means an official figure taken from a mirror copy, or a simple calculation (`_calc`) from official figures, or the press quoting an official figure. `low` means a garbled or indirect value.

## 1. Summary tables

### 1a. Annual average green-coffee prices, 2005-2026 (ICO in US cents/lb; World Bank in USD/kg)

| Year | I-CIP (calc) | ICO official | Col. Milds | Other Milds | Braz. Nat. | Robustas | WB Arabica $/kg | WB Robusta $/kg | WB Arabica c/lb eq. | WB Robusta c/lb eq. | I-CIP y/y |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2005 | 89.36 |  | 115.73 | 114.86 | 102.29 | 50.55 | 2.53 | 1.11 | 114.8 | 50.3 |  |
| 2006 | 95.75 |  | 116.80 | 114.40 | 103.92 | 67.55 | 2.52 | 1.49 | 114.3 | 67.6 | +7.2% |
| 2007 | 107.68 |  | 125.57 | 123.55 | 111.79 | 86.60 | 2.72 | 1.91 | 123.4 | 86.6 | +12.5% |
| 2008 | 124.25 |  | 144.32 | 139.78 | 126.59 | 105.28 | 3.08 | 2.32 | 139.7 | 105.2 | +15.4% |
| 2009 | 115.67 |  | 177.43 | 143.84 | 115.32 | 74.58 | 3.17 | 1.64 | 143.8 | 74.4 | -6.9% |
| 2010 | 147.24 |  | 225.46 | 195.96 | 153.68 | 78.74 | 4.32 | 1.74 | 196.0 | 78.9 | +27.3% |
| 2011 | 210.39 |  | 283.84 | 271.07 | 247.62 | 109.21 | 5.98 | 2.41 | 271.2 | 109.3 | +42.9% |
| 2012 | 156.34 |  | 202.08 | 186.47 | 174.97 | 102.82 | 4.11 | 2.27 | 186.4 | 103.0 | -25.7% |
| 2013 | 119.51 |  | 147.87 | 139.53 | 122.23 | 94.16 | 3.08 | 2.08 | 139.7 | 94.3 | -23.6% |
| 2014 | 155.26 |  | 197.95 | 200.39 | 171.59 | 100.43 | 4.42 | 2.22 | 200.5 | 100.7 | +29.9% |
| 2015 | 124.67 |  | 151.80 | 159.94 | 132.45 | 88.05 | 3.53 | 1.94 | 160.1 | 88.0 | -19.7% |
| 2016 | 127.31 |  | 155.29 | 163.80 | 137.78 | 88.59 | 3.61 | 1.95 | 163.7 | 88.5 | +2.1% |
| 2017 | 126.69 |  | 152.39 | 150.74 | 131.91 | 100.95 | 3.32 | 2.23 | 150.6 | 101.2 | -0.5% |
| 2018 | 109.03 |  | 136.70 | 132.72 | 113.63 | 84.79 | 2.93 | 1.87 | 132.9 | 84.8 | -13.9% |
| 2019 | n/a | 100.52 | 133.60 | 130.66 | 101.53 | 73.56 | 2.88 | 1.62 | 130.6 | 73.5 | -7.8% |
| 2020 | 107.94 |  | 157.66 | 150.76 | 106.42 | 68.73 | 3.32 | 1.52 | 150.6 | 68.9 | +7.4% |
| 2021 | 151.28 |  | 218.84 | 204.62 | 161.73 | 89.88 | 4.51 | 1.98 | 204.6 | 89.8 | +40.2% |
| 2022 | 190.62 |  | 279.40 | 255.41 | 213.28 | 103.72 | 5.63 | 2.29 | 255.4 | 103.9 | +26.0% |
| 2023 | 165.23 | 165.23 | 209.31 | 205.96 | 174.09 | 119.15 | 4.54 | 2.63 | 205.9 | 119.3 | -13.3% |
| 2024 | 229.34 | 229.34 | 256.35 | 255.28 | 234.76 | 200.55 | 5.62 | 4.41 | 254.9 | 200.0 | +38.8% |
| 2025 | 318.33 |  | 383.71 | 384.09 | 362.29 | 220.33 | 8.47 | 4.86 | 384.2 | 220.4 | +38.8% |
| 2026* | 272.99 |  | 349.17 | 336.76 | 311.92 | 176.87 |  |  |  |  | -14.2% |

`*` 2026 = Jan-Aug 2026 average (8 months). I-CIP y/y for 2020 uses the Statista 2019 figure (low confidence).
Sources:
- ICO monthly data: 2005-2018 from the ICO dataset ([mirror](https://github.com/IgorKolodziej/a_sip_of_luxury/blob/f045d8908382b2a09f8948815ad16baf6d5fc318/data/ICO_Coffee_Dataset/indicator-prices.csv)); 2019-2026 from the ICO CMR tables ([parsed copy](https://github.com/BMR-Com/coffee-analytics/blob/b7111c975eeb533ce26977496205be5303c71732/data/csv/prices.csv)).
- ICO official annual averages: [CMR Dec-2023](https://www.icocoffee.org/documents/cy2023-24/cmr-1223-e.pdf) and [CMR Dec-2024](https://www.ico.org/documents/cy2024-25/cmr-1224-e.pdf) ("I-CIP closes 2024 up 40%, averaging 229.34 US cents/lb").
- The 2019 figure comes from [Statista](https://www.statista.com/statistics/300565/global-coffee-market-ico-composite-price-trend-of-green-coffee/) (low confidence; the search summary put a 2020 label on it).
- World Bank Pink Sheet annual averages, March 2026 vintage: [CSV copy of CMO-Historical-Data-Annual](https://github.com/Sanjula19/Ewaste-Recycling-system-02/blob/411d11c6974a841da49eb93216e3c1fa679a693e/component-4/backend/data/CMO-Historical-Data-Annual.csv).

Reading the table:
- The WB "Arabica" series is the ICO Other Milds indicator, and "Robusta" is the ICO Robustas indicator. That is why the c/lb-equivalent columns track the ICO columns.
- In 2025 the WB Arabica average was +51% y/y (8.47 vs 5.62 USD/kg) and Robusta was +10% (4.86 vs 4.41). The 2024 surge was led by Robusta: +68% (2.63 to 4.41 USD/kg).

### 1b. Monthly I-CIP and Robustas: lowest and highest month of each year (US cents/lb)

| Year | I-CIP low (month) | I-CIP high (month) | Robustas low | Robustas high |
|---|---|---|---|---|
| 2005 | 78.79 (09) | 101.44 (03) | 36.96 (01) | 60.02 (06) |
| 2006 | 86.04 (06) | 108.01 (12) | 59.60 (03) | 77.11 (09) |
| 2007 | 99.30 (04) | 118.16 (12) | 77.00 (03) | 92.78 (09) |
| 2008 | 103.07 (12) | 138.82 (02) | 82.51 (12) | 121.92 (03) |
| 2009 | 105.87 (03) | 124.96 (12) | 69.48 (11) | 82.74 (01) |
| 2010 | 123.37 (02) | 184.26 (12) | 67.25 (03) | 94.09 (12) |
| 2011 | 189.02 (12) | 231.24 (04) | 97.24 (11) | 121.98 (05) |
| 2012 | 131.31 (12) | 188.90 (01) | 96.59 (12) | 107.06 (07) |
| 2013 | 100.99 (11) | 135.38 (01) | 79.71 (11) | 106.26 (03) |
| 2014 | 110.75 (01) | 172.88 (10) | 87.73 (01) | 105.55 (04) |
| 2015 | 113.14 (09) | 148.24 (01) | 79.28 (12) | 98.36 (02) |
| 2016 | 110.89 (01) | 145.82 (11) | 74.04 (02) | 103.72 (11) |
| 2017 | 114.00 (12) | 139.07 (01) | 87.59 (12) | 108.32 (01) |
| 2018 | 98.17 (09) | 115.60 (01) | 76.70 (09) | 89.24 (02) |
| 2019 | 93.33 (05) | 117.37 (12) | 68.63 (10) | 78.65 (02) |
| 2020 | 99.05 (06) | 116.25 (09) | 63.97 (04) | 72.77 (09) |
| 2021 | 115.73 (01) | 203.06 (12) | 70.71 (01) | 112.76 (12) |
| 2022 | 156.66 (11) | 210.89 (02) | 92.59 (11) | 111.36 (09) |
| 2023 | 151.94 (10) | 178.57 (04) | 95.98 (01) | 135.47 (12) |
| 2024 | 176.41 (01) | 299.61 (12) | 148.47 (01) | 241.93 (09) |
| 2025 | 259.31 (07) | 354.32 (02) | 167.19 (07) | 263.08 (02) |
| 2026 | 248.90 (06) | 296.89 (01) | 164.64 (04) | 192.52 (01) |

The full monthly series is in the CSV, 2005-01 to 2026-08, for I-CIP and all four groups. World Bank monthly USD/kg covers 2019-01 to 2024-12. ICO New York and London futures averages cover 2014-10 to 2015-03, 2018-03 to 2018-05, and 2019-01 to 2026-08.

### 1c. Monthly detail 2024 to 08/2026 (US cents/lb; ICO CMR tables; arbitrage = NY minus London)

| Month | I-CIP | Col. Milds | Other Milds | Braz. Nat. | Robustas | NY futures | London futures (c/lb) | Arbitrage NY-London |
|---|---|---|---|---|---|---|---|---|
| 2024-01 | 176.41 | 205.62 | 203.30 | 179.32 | 148.47 | 183.06 | 135.84 | 47.22 |
| 2024-02 | 182.04 | 209.53 | 208.78 | 186.74 | 153.23 | 185.37 | 142.43 | 42.94 |
| 2024-03 | 186.38 | 210.26 | 208.85 | 185.76 | 165.84 | 184.59 | 148.53 | 36.06 |
| 2024-04 | 216.89 | 241.80 | 239.73 | 218.77 | 193.65 | 217.97 | 176.04 | 41.93 |
| 2024-05 | 208.38 | 233.50 | 232.11 | 209.78 | 184.97 | 208.86 | 165.11 | 43.75 |
| 2024-06 | 226.83 | 250.39 | 248.39 | 229.25 | 204.30 | 226.47 | 182.82 | 43.65 |
| 2024-07 | 236.54 | 257.82 | 257.10 | 239.70 | 214.72 | 235.15 | 193.93 | 41.22 |
| 2024-08 | 238.89 | 263.67 | 261.38 | 242.15 | 214.69 | 239.29 | 197.81 | 41.48 |
| 2024-09 | 258.84 | 279.27 | 278.52 | 257.24 | 241.93 | 254.43 | 225.13 | 29.30 |
| 2024-10 | 250.56 | 277.10 | 276.82 | 255.85 | 221.93 | 250.62 | 207.11 | 43.51 |
| 2024-11 | 270.72 | 306.21 | 304.98 | 285.59 | 226.11 | 277.04 | 214.43 | 62.61 |
| 2024-12 | 299.61 | 341.00 | 343.34 | 326.97 | 236.73 | 317.00 | 226.28 | 90.72 |
| 2025-01 | 310.12 | 351.93 | 354.47 | 339.18 | 245.29 | 328.94 | 234.33 | 94.61 |
| 2025-02 | 354.32 | 410.64 | 409.48 | 401.10 | 263.08 | 388.18 | 253.48 | 134.70 |
| 2025-03 | 347.85 | 404.97 | 404.02 | 392.48 | 257.61 | 382.75 | 247.63 | 135.12 |
| 2025-04 | 335.76 | 394.14 | 392.84 | 378.27 | 246.39 | 370.37 | 235.69 | 134.68 |
| 2025-05 | 334.41 | 395.59 | 397.84 | 380.02 | 237.76 | 368.21 | 224.63 | 143.58 |
| 2025-06 | 295.06 | 360.08 | 363.16 | 338.53 | 196.21 | 329.56 | 183.21 | 146.35 |
| 2025-07 | 259.31 | 322.37 | 325.50 | 297.04 | 167.19 | 289.17 | 153.43 | 135.74 |
| 2025-08 | 297.05 | 366.72 | 366.32 | 336.88 | 199.13 | 328.57 | 181.43 | 147.14 |
| 2025-09 | 324.62 | 403.77 | 400.21 | 374.91 | 210.85 | 366.31 | 197.56 | 168.75 |
| 2025-10 | 326.38 | 403.25 | 403.79 | 373.47 | 215.06 | 366.00 | 202.16 | 163.84 |
| 2025-11 | 330.44 | 408.75 | 410.31 | 380.17 | 214.91 | 373.57 | 202.33 | 171.24 |
| 2025-12 | 304.68 | 382.32 | 381.14 | 355.38 | 190.53 | 347.71 | 178.87 | 168.84 |
| 2026-01 | 296.89 | 371.59 | 363.94 | 343.77 | 192.52 | 334.99 | 180.23 | 154.76 |
| 2026-02 | 267.57 | 330.89 | 321.35 | 308.62 | 179.73 | 288.76 | 166.06 | 122.70 |
| 2026-03 | 273.70 | 337.45 | 334.34 | 320.51 | 176.77 | 290.18 | 161.91 | 128.27 |
| 2026-04 | 266.24 | 334.56 | 331.22 | 313.76 | 164.64 | 284.63 | 150.65 | 133.98 |
| 2026-05 | 256.05 | 323.45 | 315.42 | 293.73 | 166.51 | 268.18 | 151.79 | 116.39 |
| 2026-06 | 248.90 | 324.60 | 307.83 | 272.01 | 169.39 | 256.75 | 155.90 | 100.85 |
| 2026-07 | 287.26 | 383.39 | 358.65 | 320.69 | 184.78 | 310.34 | 172.73 | 137.61 |
| 2026-08 | 287.29 | 387.46 | 361.31 | 322.24 | 180.63 | 313.20 | 167.63 | 145.57 |

ICO statements agree with the calculated arbitrage in the last column: Feb-26 **122.70**, Mar-26 **128.27**, May-26 **116.39**, Jun-26 **100.86**, Aug-26 **145.56** US cents/lb ([CMR text copies](https://github.com/BMR-Com/coffee-analytics/tree/b7111c975eeb533ce26977496205be5303c71732/data/report-text)).

### 1d. Records and extremes

| Period | Value | Unit | What | Source | Conf. |
|---|---|---|---|---|---|
| 2025-02 | 354.32 | US cents/lb | ICO composite (I-CIP) - highest monthly average on record (nominal) | [ICO](https://www.ico.org/documents/cy2025-26/cmr-0126-e.pdf) | high |
| 2025-02/2025-05 | 343.08 | US cents/lb | ICO composite (I-CIP) - Feb-May 2025 average, highest nominal level on record | [ICO](https://github.com/BMR-Com/coffee-analytics/blob/b7111c975eeb533ce26977496205be5303c71732/data/report-text/2026-06.txt) | high |
| 2024-12 | 299.61 | US cents/lb | ICO composite (I-CIP) - Dec-2024 monthly avg, highest since April 1977 | [ICO](https://www.comunicaffe.com/ico-composite-indicator-price-close-to-the-3-dollar-mark-up-by-70-from-january-to-december/) | high |
| 1977-04 | 314.96 | US cents/lb | ICO composite (I-CIP) - April 1977 monthly avg (previous nominal high) | [ICO](https://www.comunicaffe.com/ico-composite-indicator-price-close-to-the-3-dollar-mark-up-by-70-from-january-to-december/) | medium |
| 2024-12-10 | 312.77 | US cents/lb | ICO composite (I-CIP) - daily peak Dec 2024 | [ICO](https://www.comunicaffe.com/ico-composite-indicator-price-close-to-the-3-dollar-mark-up-by-70-from-january-to-december/) | medium |
| 2024-06 | 226.83 | US cents/lb | ICO composite (I-CIP) - June 2024, 13-year high | [ICO (via CNN)](https://www.comunicaffe.com/ico-composite-indicator-price-reaches-13-year-high-says-monthly-report/) | medium |
| 2021-12 | 203.06 | US cents/lb | ICO composite (I-CIP) - Dec 2021, broke 200 c/lb (decade-long high) | [ICO](https://www.ico.org/documents/cmr-1221-e.pdf) | high |
| 2019-03 | 97.50 | US cents/lb | ICO composite (I-CIP) - Mar 2019, lowest since Oct 2006 | [ICO](https://www.ico.org/documents/cy2018-19/cmr-0419-e.pdf) | high |
| 2019-04 | 94.42 | US cents/lb | ICO composite (I-CIP) - Apr 2019, lowest since Jul 2006 | [ICO](https://www.ico.org/documents/cy2018-19/cmr-0419-e.pdf) | medium |
| 2019-05 | 93.33 | US cents/lb | ICO composite (I-CIP) - lowest monthly average 2015-2026 (cycle low) | [ICO (calc)](https://github.com/BMR-Com/coffee-analytics/blob/b7111c975eeb533ce26977496205be5303c71732/data/csv/prices.csv) | medium |
| 2005-09 | 78.79 | US cents/lb | ICO composite (I-CIP) - lowest monthly average 2005-2026 | [ICO (calc)](https://github.com/IgorKolodziej/a_sip_of_luxury/blob/f045d8908382b2a09f8948815ad16baf6d5fc318/data/ICO_Coffee_Dataset/indicator-prices.csv) | medium |
| 2011-04 | 231.24 | US cents/lb | ICO composite (I-CIP) - 2011 cycle peak monthly average | [ICO (calc)](https://github.com/IgorKolodziej/a_sip_of_luxury/blob/f045d8908382b2a09f8948815ad16baf6d5fc318/data/ICO_Coffee_Dataset/indicator-prices.csv) | medium |
| 2025-02 | 263.08 | US cents/lb | ICO Robustas - highest monthly average 2005-2026 | [ICO (calc)](https://github.com/BMR-Com/coffee-analytics/blob/b7111c975eeb533ce26977496205be5303c71732/data/csv/prices.csv) | medium |
| 2020-04 | 63.97 | US cents/lb | ICO Robustas - lowest monthly average 2015-2026 | [ICO (calc)](https://github.com/BMR-Com/coffee-analytics/blob/b7111c975eeb533ce26977496205be5303c71732/data/csv/prices.csv) | medium |
| 2025-11 | 410.31 | US cents/lb | ICO Other Milds - highest monthly average 2005-2026 | [ICO (calc)](https://github.com/BMR-Com/coffee-analytics/blob/b7111c975eeb533ce26977496205be5303c71732/data/csv/prices.csv) | medium |
| 2019-05 | 120.55 | US cents/lb | ICO Other Milds - lowest monthly average 2015-2026 | [ICO (calc)](https://github.com/BMR-Com/coffee-analytics/blob/b7111c975eeb533ce26977496205be5303c71732/data/csv/prices.csv) | medium |
| 2025-02 | 410.64 | US cents/lb | ICO Colombian Milds - highest monthly average 2005-2026 | [ICO (calc)](https://github.com/BMR-Com/coffee-analytics/blob/b7111c975eeb533ce26977496205be5303c71732/data/csv/prices.csv) | medium |
| 2019-05 | 124.40 | US cents/lb | ICO Colombian Milds - lowest monthly average 2015-2026 | [ICO (calc)](https://github.com/BMR-Com/coffee-analytics/blob/b7111c975eeb533ce26977496205be5303c71732/data/csv/prices.csv) | medium |
| 2025-02 | 401.10 | US cents/lb | ICO Brazilian Naturals - highest monthly average 2005-2026 | [ICO (calc)](https://github.com/BMR-Com/coffee-analytics/blob/b7111c975eeb533ce26977496205be5303c71732/data/csv/prices.csv) | medium |
| 2019-05 | 91.95 | US cents/lb | ICO Brazilian Naturals - lowest monthly average 2015-2026 | [ICO (calc)](https://github.com/BMR-Com/coffee-analytics/blob/b7111c975eeb533ce26977496205be5303c71732/data/csv/prices.csv) | medium |
| 2025-02 | 388.18 | US cents/lb | ICE New York Arabica futures (ICO monthly avg) - highest monthly average 2019-2026 | [ICO (calc)](https://github.com/BMR-Com/coffee-analytics/blob/b7111c975eeb533ce26977496205be5303c71732/data/csv/prices.csv) | medium |
| 2019-05 | 94.86 | US cents/lb | ICE New York Arabica futures (ICO monthly avg) - lowest monthly average 2019-2026 | [ICO (calc)](https://github.com/BMR-Com/coffee-analytics/blob/b7111c975eeb533ce26977496205be5303c71732/data/csv/prices.csv) | medium |
| 2025-02 | 253.48 | US cents/lb | ICE London Robusta futures (ICO monthly avg, c/lb) - highest monthly average 2019-2026 | [ICO (calc)](https://github.com/BMR-Com/coffee-analytics/blob/b7111c975eeb533ce26977496205be5303c71732/data/csv/prices.csv) | medium |
| 2020-04 | 54.40 | US cents/lb | ICE London Robusta futures (ICO monthly avg, c/lb) - lowest monthly average 2019-2026 | [ICO (calc)](https://github.com/BMR-Com/coffee-analytics/blob/b7111c975eeb533ce26977496205be5303c71732/data/csv/prices.csv) | medium |
| 2024-09 | 29.30 | US cents/lb | Arabica-Robusta arbitrage (NY-London) - narrowest monthly 2019-2026 | [ICO (calc)](https://github.com/BMR-Com/coffee-analytics/blob/b7111c975eeb533ce26977496205be5303c71732/data/csv/prices.csv) | medium |
| 2025-11 | 171.24 | US cents/lb | Arabica-Robusta arbitrage (NY-London) - widest monthly 2019-2026 | [ICO (calc)](https://github.com/BMR-Com/coffee-analytics/blob/b7111c975eeb533ce26977496205be5303c71732/data/csv/prices.csv) | medium |
| 2024-09 | 29.30 | US cents/lb | Arabica-Robusta arbitrage - narrowest month of 2024 | [ICO (calc)](https://github.com/BMR-Com/coffee-analytics/blob/b7111c975eeb533ce26977496205be5303c71732/data/csv/prices.csv) | medium |
| 2026-06-09 | 231.96 | US cents/lb | ICO composite (I-CIP) - daily low 9 June 2026 (lowest in nearly two years) | [ICO](https://github.com/BMR-Com/coffee-analytics/blob/b7111c975eeb533ce26977496205be5303c71732/data/report-text/2026-06.txt) | high |
| 2026-06-30 | 272.39 | US cents/lb | ICO composite (I-CIP) - end-June 2026 two-month high | [ICO](https://github.com/BMR-Com/coffee-analytics/blob/b7111c975eeb533ce26977496205be5303c71732/data/report-text/2026-06.txt) | high |
| 2026-08 | 279.38 | US cents/lb | ICO composite (I-CIP) - August 2026 daily range low | [ICO](https://github.com/BMR-Com/coffee-analytics/blob/b7111c975eeb533ce26977496205be5303c71732/data/report-text/2026-08.txt) | high |
| 2026-08 | 301.97 | US cents/lb | ICO composite (I-CIP) - August 2026 daily range high | [ICO](https://github.com/BMR-Com/coffee-analytics/blob/b7111c975eeb533ce26977496205be5303c71732/data/report-text/2026-08.txt) | high |

Notes on the records:
- **Intraday and settlement records on ICE are not verified.** This covers the ICE NY "KC" all-time high in 2025, the 2019 low, and the ICE London Robusta record. Only ICO **monthly averages** of the futures are recorded here.
- On those monthly averages, NY futures peaked at **388.18 c/lb in Feb-2025** and bottomed at **94.86 in May-2019**. London Robusta peaked at **253.48 c/lb in Feb-2025** (about USD 5,590/t) and bottomed at **54.40 in Apr-2020**.

### 1e. Retail and consumer prices

| Year | US CPI coffee index (BLS annual avg, 1982-84=100) | US CPI coffee % y/y (annual avg) | Brazil IPCA cafe moido % Dec/Dec |
|---|---|---|---|
| 2004 | 145.3 |  |  |
| 2005 | 161.2 | 10.9 |  |
| 2006 | 165.3 | 2.5 |  |
| 2007 | 175.647 | 6.3 |  |
| 2008 | 188.027 | 7.0 |  |
| 2009 | 186.317 | -0.9 |  |
| 2010 | 186.418 | 0.1 |  |
| 2011 | 213.824 | 14.7 |  |
| 2012 | 217.441 | 1.7 |  |
| 2013 | 204.712 | -5.9 |  |
| 2014 | 200.984 | -1.8 |  |
| 2015 | 205.540 | 2.3 |  |
| 2016 | 199.307 | -3.0 |  |
| 2017 | 199.156 | -0.1 |  |
| 2018 | 194.876 | -2.1 |  |
| 2019 | 193.237 | -0.8 |  |
| 2020 | 194.177 | 0.5 | 7.71 |
| 2021 | 199.263 | 2.6 | 50.24 |
| 2022 | 227.887 | 14.4 | 13.52 |
| 2023 | 237.245 | 4.1 | -9.07 |
| 2024 | 235.159 | -0.9 | 39.60 |
| 2025 |  |  | 35.64 |
| 2026 |  |  | -15.27 (YTD Aug) |

Sources:
- US index levels are BLS annual averages (M13), from a [copy of the BLS API response](https://github.com/v4lue4dded/inflation_by_income_percentile/blob/d9e8f8f0eaa38735a964b3fa10c7eeb17666c12a/data/raw/requests/CUUR0000SEFP01_2004_2023.json). The % changes are calculated from them.
- Brazil Dec/Dec changes are compounded from IBGE monthly changes ([IPCA 7392 extract](https://github.com/leonardotteixeira/custava-quanto/blob/c808a48a6e0a9f7a9e1bddfc186cd4842b348603/data/processed/ibge_itens_cesta_mensal.csv)). The 12-month change to Jul-2026 calculated this way is -17.21%. IBGE's own table 7060 gives **-17.20%** ([extract](https://github.com/maraferpaga-hash/Economizei-bot/blob/57ce0480169840a187c34b5f082b4f916368719d/conteudo/dados/2026-09-03_ipca_jul2026_alimentacao_domicilio.json)).

Latest consumer-price readings:

| Series | Period | Value | Source |
|---|---|---|---|
| US CPI coffee y/y | Jun-2025 | +13.4% (calc; NSA 264.989 vs 233.741) | BLS API copy |
| US CPI coffee y/y | Jan-2026 | +18.3%; +47% over 5 years | [AP via news archive](https://github.com/ora-commons/msi-corpus/blob/904e00f0f05c442aca915dc8cbcb8045fb2c72ce/news/articles/2026-02-16-rising-coffee-costs-push-some-americans-to-give-up-caf-brews.md) |
| US CPI coffee y/y | Apr-2026 | +18.5% | [news archive](https://github.com/ora-commons/msi-corpus/blob/904e00f0f05c442aca915dc8cbcb8045fb2c72ce/news/articles/2026-05-14-grocery-prices-surge-2-9-in-april-full-iran-war-impact-still-months-away.md) |
| US CPI coffee y/y | **Jul-2026 (latest)** | **+10.3%** | [The Center Square / BIZ Magazine, 12-Aug-2026](https://bizmagsb.com/consumer-prices-up-0-1-in-july-annual-rate-slips-to-3-4) |
| Brazil IPCA café moído, 12-month | Apr-2025 | about +80%, the largest since the Plano Real | [InfoMoney 09-May-2025](https://www.infomoney.com.br/economia/preco-do-cafe-moido-sobe-80-em-12-meses-e-tem-maior-alta-desde-inicio-do-plano-real/) |
| Brazil IPCA café moído, m/m | Jan / Feb / Mar 2025 | +8.56% / +10.77% / +8.14% | IBGE extract |
| Brazil IPCA café moído, 12-month | Jul-2026 / Aug-2026 | -17.20% / -16.95% (calc) | IBGE |
| Brazil IPCA café moído, YTD | Dec-25 to Aug-26 | -15.27% (calc); retail price index peaked in Jun-2025 | IBGE extract |

## 2. Price regimes, 2005-2026: what moved prices

Every level below comes from the CSV. Drivers are given **only where a source was found in this session**. Where none was found, the regime is described from the data and the driver is marked *not verified*.

1. **2005-2009: low but rising.** The I-CIP stayed in a 79-139 c/lb band. The low was **78.79 in Sep-2005** and the high **138.82 in Feb-2008**. Annual averages rose from 89.4 (2005) to 124.3 (2008), then eased to 115.7 in 2009. In 2009-10 a large Colombian Milds premium opened up (2009 average: CM 177.4 vs Other Milds 143.8). Consistent with this, J.M. Smucker said in early 2011 that "Colombia has been under pressure for a couple of years" ([Q3 FY2011 call](https://github.com/personal-coding/Stock-Earnings-Call-Transcript-Natural-Language-Processing/blob/92bede825857fd49d78f740b00241d301004a8b1/article/253549-the-j-m-smuckers-ceo-discusses-q3-2011-results-earnings-call-transcript.txt)). Other drivers: *not verified*.
2. **2010-2011 spike.** The I-CIP rose from **123.4 (Feb-2010) to 231.24 (Apr-2011)**, the peak for 2005-2023. The 2011 average was 210.4 (+43%), and WB Arabica averaged 5.98 USD/kg. Drivers cited by roasters:
   - Smucker listed a Brazilian "off-year", Colombian shortfalls, stronger demand in Brazil and other developing countries, and speculation ("hard to put a percent on how much is driven by fundamentals versus speculation"). It said its green costs were "up nearly 50%" y/y by Q4 FY2011 ([Q4 call](https://github.com/personal-coding/Stock-Earnings-Call-Transcript-Natural-Language-Processing/blob/92bede825857fd49d78f740b00241d301004a8b1/article/274180-the-j-m-smuckers-ceo-discusses-q4-2011-results-earnings-call-transcript.txt)).
   - Starbucks said higher coffee costs took about 800 bp off its CPG margin ([Q2 FY2011 call](https://github.com/personal-coding/Stock-Earnings-Call-Transcript-Natural-Language-Processing/blob/92bede825857fd49d78f740b00241d301004a8b1/article/266065-starbucks-ceo-discusses-q2-2011-results-earnings-call-transcript.txt)).
   - US retail CPI for coffee rose **+14.7%** in 2011.
3. **2012-2013 slump.** Prices fell to **100.99 (Nov-2013)**, 56% below the peak. Averages: 2012 156.3 (-26%), 2013 119.5 (-24%). US retail CPI fell 5.9% in 2013. Drivers: *not verified*.
4. **2014 spike.** The I-CIP rose from 110.75 (Jan) to **172.88 (Oct-2014)**, and the 2014 average was 155.3 (+30%). The rally was Arabica-led: Other Milds averaged 200.4 while Robustas averaged 100.4. Drivers: *not verified in-session*; Brazil weather is the usual explanation and should be checked.
5. **2015-2018: long decline.** Prices fell from 148.2 (Jan-2015) to **98.17 (Sep-2018)**, with a brief rebound to 145.8 in Nov-2016. The ICO described surplus years: "Coffee market ends 2017/18 in surplus" ([CMR Sep-2018](https://www.ico.org/documents/cy2017-18/cmr-0918-e.pdf)) and "2018/19 expected to be the second year of surplus" ([CMR Dec-2018](https://www.ico.org/documents/cy2018-19/cmr-1218-e.pdf)). It also noted "Arabica/Robusta divergence" ([CMR Dec-2016](https://www.ico.org/documents/cy2016-17/cmr-1216-e.pdf)).
6. **2019-2020 trough.** Prices hit 97.50 in Mar-2019, the lowest since Oct-2006, and 94.42 in Apr-2019, the lowest since Jul-2006 ([CMR](https://www.ico.org/documents/cy2018-19/cmr-0419-e.pdf)). The **cycle low was 93.33 in May-2019**, when the NY futures monthly average was 94.86. Prices recovered to 117.37 in Dec-2019. The ICO attributed that recovery to slower Brazilian exports and delayed harvests, "as well as strong demand" ([CMR Dec-2019](https://www.ico.org/documents/cy2019-20/cmr-1219-e.pdf)). In 2020 the I-CIP stayed between 99 and 116 while Robusta was weak: ICO Robustas hit 63.97 and London futures 54.40 c/lb in Apr-2020.
7. **2021-2022: frost spike.** The I-CIP rose from 115.7 (Jan-2021) to **203.06 (Dec-2021)**, the first month above 200 c/lb in a decade. The ICO said this marked "a return to the higher levels experienced in 2011" ([CMR Dec-2021](https://www.ico.org/documents/cmr-1221-e.pdf)). Prices peaked at **210.89 in Feb-2022**. The trigger was an "unusually strong frost [that] decimated [Brazil's] crops in the summer of 2021" (CNN, Aug-2024, [copy](https://github.com/M-Mehdi-M/HW_1_APD/blob/fc7e234ed554e4289c25f88a8c2400e67cc79d5c/checker/input/articles/articles_13370.json)). Averages: 2021 151.3, 2022 190.6. The **arbitrage widened to 135-145 c/lb** in Jan-Feb 2022 (144.80 in Feb-2022). Retail response: US CPI coffee **+14.4%** in 2022; Brazil café moído **+50.2%** in 2021 and +13.5% in 2022.
8. **2023: Arabica eases, Robusta firms.** The I-CIP fell to 151.9 by Oct-2023; the ICO's official 2023 average is **165.23**. ICO Robustas rose from 96 to 135 c/lb over the year, so the arbitrage fell from 74 c/lb in Jan-2023 (145 in Feb-2022) to **46 c/lb (Jul-2023)**. Retail: Brazil café moído -9.1%; US CPI coffee +4.1%.
9. **2024: Robusta-led surge.** ICO Robustas rose from 148.5 (Jan) to **241.9 (Sep-2024)**, and the **arbitrage fell to 29.3 c/lb in Sep-2024**, its narrowest level of 2019-2026. Milestones:
   - The I-CIP reached a 13-year high of 226.83 in Jun-2024.
   - It reached **299.61 in Dec-2024, the highest since Apr-1977 (314.96)**, with a daily peak of 312.77 on 10-Dec ([comunicaffe/ICO](https://www.comunicaffe.com/ico-composite-indicator-price-close-to-the-3-dollar-mark-up-by-70-from-january-to-december/)).
   - The 2024 average was **229.34**; the ICO headline was "I-CIP closes 2024 up 40%".

   Drivers:
   - Vietnam's adverse weather cut its exports by 7% (USDA, cited by CNN).
   - Climate change, and buyers switching between Arabica and Robusta.
   - Lavazza's "perfect storm": poor harvests, climate change, the Ukraine war, the Red Sea, speculators and a strong dollar (all per CNN, [copy](https://github.com/M-Mehdi-M/HW_1_APD/blob/fc7e234ed554e4289c25f88a8c2400e67cc79d5c/checker/input/articles/articles_13370.json)).
   - Arabica futures were "up nearly 69% so far this year ... weather concerns in Brazil, including an extended drought and high temperatures" (A. Harrup, "Arabica Coffee at Highest Price Since 1977", [copy](https://github.com/andrewruler/ai/blob/03cb517b4dc4726064236f6487d6b8360ed2f2ba/bloomberg/ya2.txt); date not shown).

   **US retail lagged:** CPI coffee was **-0.9%** in 2024. Brazil retail did not: café moído rose **+39.6%** Dec/Dec.
10. **2025: record year.** The **Feb-2025 I-CIP of 354.32 is the highest monthly nominal average on record** ([CMR Jan-2026](https://www.ico.org/documents/cy2025-26/cmr-0126-e.pdf)). Feb-May 2025 averaged **343.08**, "the highest nominal level on record" ([CMR Jun-2026 text](https://github.com/BMR-Com/coffee-analytics/blob/b7111c975eeb533ce26977496205be5303c71732/data/report-text/2026-06.txt)). In Feb-2025, NY futures averaged 388.18 and London 253.48 c/lb.
    - Prices fell to 259.31 in Jul-2025 (-27% from Feb), then rebounded to 330.44 in Nov-2025. During the rebound Arabica outran Robusta and the **arbitrage reached about 171 c/lb (Nov-2025)**, the widest of 2019-2026.
    - The **2025 average was 318.33** (calc, +39%). WB Arabica averaged **8.47 USD/kg** (+51%).
    - Context from the ICO: the world market ran **four consecutive deficit years, 2021/22 to 2024/25** ([CMR Aug-2026](https://github.com/BMR-Com/coffee-analytics/blob/b7111c975eeb533ce26977496205be5303c71732/data/report-text/2026-08.txt)). The ICO also names "increased US tariffs in 2025" as a likely factor in Brazil's weaker exports (CMR Mar-2026 text).
    - Retail caught up: Brazil café moído rose about **+80% y/y by Apr-2025**, with m/m rises of +8.6%, +10.8% and +8.1% in Jan-Mar 2025, and **+35.6%** Dec/Dec for 2025. US CPI coffee was +13.4% y/y in Jun-2025 and **+18.3% in Jan-2026**.
11. **2026: supply-led easing, with weather scares.** I-CIP monthly path, with the reasons the ICO gave:
    - **Jan-2026: 296.89.**
    - **Feb-2026: 267.57 (-9.9%).** Improved supply outlook: CONAB's record Brazilian crop forecast, good rain in Minas Gerais and Vietnam.
    - **Mar-2026: 273.70.** A geopolitical premium from the Middle East conflict and the Strait of Hormuz closure, then a correction on Marex (75.9 Mbags) and Sucafina (75.4 Mbags) forecasts of a record 2026/27 Brazil crop.
    - **Apr-2026: 266.24.**
    - **May-2026: 256.05.** CONAB raised its 2026/27 estimate to a record 66.7 Mbags, with Arabica at 45.8 Mbags (+28% y/y).
    - **Jun-2026: 248.90.** A daily low of 231.96 on 9-Jun, the lowest in nearly two years, then a 17.4% rebound on weather news.
    - **Jul-2026: 287.26.**
    - **Aug-2026: 287.29.** An El Niño risk premium built and then faded as Brazil got rain.

    CMR text sources: [Feb](https://github.com/BMR-Com/coffee-analytics/blob/b7111c975eeb533ce26977496205be5303c71732/data/report-text/2026-02.txt), [Mar](https://github.com/BMR-Com/coffee-analytics/blob/b7111c975eeb533ce26977496205be5303c71732/data/report-text/2026-03.txt), [May](https://github.com/BMR-Com/coffee-analytics/blob/b7111c975eeb533ce26977496205be5303c71732/data/report-text/2026-05.txt), [Jun](https://github.com/BMR-Com/coffee-analytics/blob/b7111c975eeb533ce26977496205be5303c71732/data/report-text/2026-06.txt), [Aug](https://github.com/BMR-Com/coffee-analytics/blob/b7111c975eeb533ce26977496205be5303c71732/data/report-text/2026-08.txt).

    Where things stand:
    - The 2026 YTD average is **272.99** (-14% vs 2025).
    - The ICO projects a **3.0 Mbag surplus in 2025/26**.
    - The arbitrage widened again to **145.56** in Aug-2026.
    - Retail is moving the other way in the two markets. **Brazil café moído is down 17.2% y/y (Jul-2026)**, but **US CPI coffee is still up 10.3% y/y (Jul-2026)**, easing from +18.5% in Apr-2026.

**What this means for demand.** Consumer prices follow green prices late and only partly:
- From 2020 to 2024, the I-CIP annual average more than doubled (+112%), while the US CPI coffee index rose only **21%** (194.2 to 235.2).
- The US retail increase came mostly in 2025-26, about 12 months behind the green-price rise. CNN notes that large roasters buy forward and hedge.
- Brazil, the producing country, passes changes through faster and further: the café moído index rose **+194% from Dec-2020 to Dec-2025**, then fell 15% in 2026 YTD.

## 3. Gaps and caveats

- **Where the numbers came from.** Only a few numbers came directly from WebSearch or ICO statements, because the search budget ran out. Most values come from **mirror copies of official files on GitHub**. Those copies are traceable and were validated, but they are not official downloads. Before publishing, re-download:
  - the WB CMO xlsx,
  - ICO CMR tables and `I-CIP.pdf`,
  - BLS CUUR0000SEFP01,
  - IBGE SIDRA table 7060.
- **ICO annual composite.** Only 2023 and 2024 are official ICO values. Every other year is a `_calc` average of the 12 monthly values, the same method that reproduces ICO's official 2023 and 2024 figures. **2019 has no calc value**: the 02/2019 I-CIP row is garbled ("100.0,67.0", probably 100.67) and is left blank. The 2019 value of 100.52 comes from Statista (low confidence).
- **World Bank monthly** stops at 12/2024 (latest mirror is the Jan-2025 vintage); 2025-26 monthly WB values were not retrieved. The ICO Other Milds and Robustas monthly series are the same underlying indicators. WB annual 2025 is the Mar-2026 vintage and may be revised.
- **ICE records.** The intraday and settlement all-time highs (NY in 2025, London in 2024-25) and the 2019 low were **not verified**. Only ICO monthly futures averages are recorded.
- **Arbitrage.** The official ICO figures here cover 2026 only (Feb, Mar, May, Jun, Aug). The other months are NY minus London, calculated from ICO tables; this matches ICO's own figures within 0.01. Futures coverage before 2019 is sparse: 2014-10 to 2015-03 and 2018-03 to 2018-05 only.
- **US CPI.** The 2025 annual average was not retrieved; the latest BLS observation in the copy is Jun-2025. The 2026 y/y figures (+18.3% Jan, +18.5% Apr, +10.3% Jul) come from press reports of BLS releases (medium confidence). The series used is CPI-U "Coffee" (SEFP01). "Roasted coffee" (SS17031) was not retrieved.
- **Brazil.** The IPCA café moído series is only complete from 2020; 2015-2019 annual changes and **ABIC average retail prices (R$/kg)** were not retrieved.
- **Not retrieved at all:** **EU/euro-area HICP coffee** (Eurostat CP01211), Japan, UK (ONS) and Germany (Destatis). These are marked NOT FOUND or omitted.
- **Units.** Converting WB USD/kg to c/lb uses 45.3592. The ICO historical file used a 45.3 divisor; that was reversed exactly. London Robusta futures are in c/lb as the ICO reports them (x22.0462 for USD/t).
- **Vintages.** Parsed ICO tables carry a `report_period` column: the month of the CMR each row came from, possibly a revised value (given in the notes column). The 2026 YTD figures cover Jan-Aug only.
- **Unused cross-check.** IMF/FRED PCOFFOTMUSDM and PCOFFROBUSDM monthly data (to Feb-2026) were checked but not added to the CSV. They track ICO Other Milds and Robustas closely, except Jul-2025 Other Milds: IMF 316.73 vs ICO 325.50.
