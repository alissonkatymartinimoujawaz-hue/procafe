# NOTES — usda_ico fetch (2026-09-25)

## Reachability (see NETWORK.md)
Reachable: `ihcafe.hn`, `ico.org` (without www), `apps.fas.usda.gov`. Blocked by the egress proxy (CONNECT 403): www.ihcafe.hn, www.ico.org, icocoffee.org, www.icocoffee.org, fas.usda.gov, www.fas.usda.gov, perfectdailygrind.com, www.bch.hn, temp.ine.gob.hn, sag.gob.hn, tnh.gob.hn, exportadoresdecafe.com, www.latribuna.hn, drive.google.com. Step 4 was skipped entirely (all hosts blocked).

## Files obtained
- `ico/cmr-0826-e.pdf` (+ .txt), `ico/cmr-0925-e.pdf` (+ .txt), `ico/cmr-1025-e.pdf` (+ .txt) — ICO Coffee Market Reports (Aug 2026, Sep 2025, Oct 2025).
- `ico/MTS-0324_T1.pdf`, `ico/MTS-0324_T4.pdf`, `ico/MTS-0324_T6.pdf` — ICO monthly trade statistics tables (March 2024). **Text extraction returned nothing** (glyphs without a text layer / unmapped fonts); open the PDFs visually.
- `ico/Coffee_Report_and_Outlook_December_2023_ICO.pdf` — text extraction almost empty (1.2 kB).
- `ico/*.html` — ico.org listing pages (home, statistics section, statistics database, public market information, economics & statistics).
- `ico_honduras_lines.txt` — Honduras lines from all ICO texts (2 hits, both in cmr-0925-e).
- `ihcafe/Boletin-Estadistico-Comercializacion-07-02-2023.pdf` (+ .txt) — the only document listed on https://ihcafe.hn/publicaciones/ (wpdocs id 9640).
- `ihcafe/page_publicaciones.html/.txt`, `ihcafe/page_produccion-nacional.html/.txt`, `ihcafe/page_sat.png` (the /sat/ URL returns a PNG image, not a page).
- `ihcafe/mdocs_{5360,6940,4680,4163}_returns_homepage.html` — the `?mdocs-file=` links no longer work: each returns the IHCAFE homepage (the site now uses a "wpdocs" plugin).
- `mdocs_links.csv` — the only document links found on the three IHCAFE pages (2; no mdocs-file links exist any more).

## Not obtained
- ICO legacy statistics (po-production.pdf, m1-exports.pdf, pr-prices.pdf, historical 1990-onwards PDF/XLSX, new_historical.asp, trade_statistics.asp): www.ico.org is blocked; the same paths on ico.org return 404 (new WordPress site). The new site's "World coffee statistics database" page offers only an order form (ICO-Statistical-Publications-Order-Form.pdf, not downloaded).
- USDA 2019 Coffee Annual Honduras: all 5 file names tried (5-15-2019, 05-15-2019, 5-16-2019, 5-17-2019, 5-14-2019) return HTTP 500 `{"message":"An error has occurred."}` (the API's not-found answer). Control request with the known file `Coffee Annual_Tegucigalpa_Honduras_HO2026-0002.pdf` returned 200 + PDF, so the API itself works (control file not kept; it is already in ../usda_gain).
- USDA Coffee Semi-annual Honduras HO2019–HO2026, numbers 0001–0020: all 160 requests returned HTTP 500 (not found).
- Google Drive file "Producción Estratificada por Departamento Cosecha 2022-2023" linked from ihcafe.hn/produccion-nacional/: drive.google.com blocked.

## Exact quotes

### Varieties (% area/farms/plants, hectares by year)
None found in the files obtained here.

### Renovation (hectares/plants per year)
None found in the files obtained here.

### Rust national incidence by month/year
None found in the files obtained here.

### ICO Honduras production / exports / grower prices by crop year
No country table text could be extracted. Only narrative lines mention Honduras:
- cmr-0925-e.txt: "The main sources of the latest downturn were Guatemala and Honduras, whose combined exports decreased by 24.2% with a net loss of 0.13 million bags."
- cmr-0925-e.txt: "Costa Rica, Guatemala, Honduras and Nicaragua combined saw their exports fall by 17.6% to 0.7 million bags from 0.85 million bags in August 2024."

### IHCAFE statistical bulletin (Boletin-Estadistico-Comercializacion-07-02-2023.txt), cosecha 2022-2023 as of 7 Feb 2023
- "Las exportaciones a la fecha suman 1 . 28 Millones de sacos de 46 kg, mostrando una disminución del 14 % comparado a los 1 . 50 Millones de sacos de 46 kg registrados en el mismo periodo del año 2021 - 2022 ."
- "El precio promedio de exportación por saco de 46 kg a la fecha es de $ 196 . 70 comparado con el precio promedio a la misma fecha de la cosecha 2021 - 2022 de $ 221 . 02 existe una disminución del 11 % ."
- "El valor de las exportaciones es de 252 . 85 millones de dólares mostrando una disminución del 24 % comparado con 332 . 17 millones en 2021 - 2022 ."
- "Compras 972,707.35 143,119,556.96 147.14 3,518,676,106.38 3,617.40" (Volumen Scs.46Kg., Valor US$, Precio Prom. US$, Valor en Lempiras, Precio Prom. Lps.)
- "Exportaciones 1,285,467.87 252,850,977.22 196.70 6,220,113,827.13 4,838.79"
- "Pronóstico de Exportaciones 2022-2023 ... Pronóstico Inicial 7,200,000.00"
- "*Arrastre2021-2022: 508,615.18 Scs.46Kg."

### USDA 2019 report (production/area/rust)
Not obtained (see above).
