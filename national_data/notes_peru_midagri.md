# Peru – MIDAGRI coffee statistics (café pergamino)

Collected 2026-09-26. Output: `peru_midagri.csv` (55 rows, source = `MIDAGRI`). Raw files are in `raw/peru_midagri/`.

## Basis
All MIDAGRI (DGESEP/DEIA, ex-DGSEP/DEA, SIEA) coffee figures are **café pergamino (parchment coffee)**. Every table says "Café pergamino", and production is in t pergamino. The rows are national totals. No arabica/robusta split is published; Peru's coffee is essentially all arabica. Periods are calendar years (Jan–Dec harvest).

## Coverage in the CSV
| indicator | years | source used |
|---|---|---|
| production (t) | 2000–2025 (2023–2025 marked "p", preliminary) | *El Agro en Cifras* Dec-2025 Excel, sheet `c-7` (C.7, 2000–2025, thousand t ×1000). This is the most recent vintage and one consistent series. |
| area_harvested (ha) | 2010–2024 | MIDAGRI *Compendio anual Producción Agrícola* Excel (2016, 2019, 2020, 2022, 2023). The other years use MIDAGRI data as reproduced in the INEI *Compendio Estadístico Perú*, tomo 2, cuadro 13.7: the 2025 edition (data at 28-May-2025) for 2014, 2015, 2017, 2018, 2021 and 2024 (2024 = E/ estimate), the 2023 edition for 2012–2013, and the 2021 edition for 2010–2011. |
| yield | 2010–2023 | kg/ha for 2017–2023, from the Compendio anual (Cuadro 372 or 354 of each edition). t/ha for 2015–2016, from the 2016 Compendio C.147. t/ha for 2010–2014, from INEI cuadro 13.7, rounded to 1 decimal. |

**Missing:**
- 1998–1999 for everything.
- area_harvested and yield for 2000–2009.
- area_harvested and yield for 2025. The MIDAGRI 2024 compendio is not yet posted.
- area_total / area_bearing / area_planted: no MIDAGRI table exists. Superficie sembrada is published only for transitory crops. "Superficie cosechada" is effectively area in production.
- The only installed-area figure found is text in MIDAGRI Nota Técnica N.°014-2023 (`raw/.../midagri_nota_tecnica_014_2023_...pdf`, p.1): "área instalada de 460 mil hectáreas al año 2022", 0.2% more than 2021, against 423.8 thousand ha harvested. Cuadro 1 of the note is an image. This figure is rounded, so it is **not** in the CSV.

## Revisions: several editions disagree, and the latest was kept
The CSV notes cite the superseded values for each row. The main differences:
- **Area 2017 / 2018.**
  - Compendio 2017: 424,129.35 ha. Compendio 2018: 447,425.519 ha. INEI 2021 has the same figures (2018 as 446,137 P/).
  - INEI 2023 and 2025 revised them to 383,118 and 432,409 ha.
  - The CSV uses the revised values. The kg/ha yields for these years come from the compendio, so they reflect the old area.
- **Area 2021.** Compendio 427,433.1 ha; INEI 2025 429,717 P/ (used).
- **Area 2015.** Compendio 2016 C.147: 379,281.909 (marked r); INEI: 379,187 (used).
- **Area 2022.** INEI 2023 had 423,854 E/. Compendio 2022 and INEI 2025 have 418,807.2 (used).
- **Area 2023.** Compendio 2023: 428,269.1 (used). INEI 2025: 429,338 E/.
- **Production.** The C.7 series (Dec-2025) differs from the compendia in some years:
  - 2015: 258,044.419 against 251,938.419 in Compendio 2016 / INEI.
  - 2016: 280,978.397 against 277,760.397 in Compendio 2016.
  - 2021: 363,996.831 against 365,220.565 in Compendio 2021.
  - 2023: 368,868.075 against 368,757.069 in Compendio 2023 and 366,940.029 in the Dec-2024 bulletin.
  - 2024: 358,910.142 against 358,994 in INEI 2025.
  - The CSV production rows use C.7 throughout.
- **Consistency checks.** production/area in the CSV gives the published yield exactly for 2019 (829.2), 2020 (819.8) and 2022 (852.9 kg/ha), and gives 861.3 against 861.0 for 2023. The other years mix editions and differ from the published yield by 1–11%. The largest gap is 2017: 880.5 against 795.3, because the 2017 area was later revised down.

## URLs used
- Compendio page: https://www.gob.pe/institucion/midagri/informes-publicaciones/2730325-compendio-anual-de-produccion-agricola. It lists Excel files for 2016–2023 and compendio PDFs for 2016–2018. The CSV rows give the individual `cdn.www.gob.pe/uploads/document/file/{2803230,2803228,2803226,3754199,3748650,3748735,6770784,9547451}/…` links. The 2016 file is xlsx, 2017–2021 are legacy .xls (read with the new `tools/xls_biff.py`, a stdlib BIFF8 reader), and 2022–2023 are xlsx.
- El Agro en Cifras 2025 page: https://www.gob.pe/institucion/midagri/informes-publicaciones/6573082-boletin-estadistico-mensual-el-agro-en-cifras-2025. The Dec-2025 Excel zip is https://cdn.www.gob.pe/uploads/document/file/9450129/6573082-cuadros-en-excel-del-boletin-el-agro-en-cifras-diciembre-2025%282%29.zip. The Dec-2024 (file 7542309) and Dec-2019 (file 536472) zips were downloaded for vintage comparison. Pages for other years: 353677 (2019), 558835 (2020), 1763886 (2021), 2826318 (2022), 4024332 (2023), 5380407 (2024) and 7910469 (2026, Jan–Jun only).
  - C.7 covers only 2000 onward. C.19 gives monthly production for the last 2 years.
  - The bulletins have **no** harvested area for coffee; their area tables cover transitory crops only.
- INEI Compendio Estadístico Perú, tomo 2 (cuadro 13.7 "Café – superficie cosechada, producción, rendimiento…", source MIDAGRI):
  - 2021 edition: https://cdn.www.gob.pe/uploads/document/file/3117982/… (2010–2020)
  - 2023 edition: https://cdn.www.gob.pe/uploads/document/file/5547450/4932612-tomo-2-compendio-estadistico-peru-2023.pdf (2012–2022)
  - 2025 edition: https://cdn.www.gob.pe/uploads/document/file/9006041/7264121-tomo-2-peru-compendio-estadistico-2025.pdf (2014–2024)
  - The 2024 edition is at https://www.gob.pe/institucion/inei/informes-publicaciones/6284790 (file 7366941). It was not downloaded.

## Tried, not useful or not reachable
- siea.midagri.gob.pe: https fails and http returns 503. The www.midagri.gob.pe, sistemas.midagri.gob.pe and www.inei.gob.pe hosts are proxy-rejected. The historical SIEA anuarios and series are therefore unreachable.
- MIDAGRI Nota Técnica N.°014-2023 (café convencional y orgánico): text only, plus image tables.
- Observatorio de Commodities Café N.°01-2024 (https://cdn.www.gob.pe/uploads/document/file/6461268/…) and the ene-mar 2023 issue: 2023 production in text only, with a garbled font.
- Plan Nacional de Acción del Café Peruano (DS 010-2019-MINAGRI, file 1867050): 2016–2017 only, with different vintages.
- The Compendio PDFs for 2016, 2017 and 2018 (8–21 MB) are single-year and duplicate the Excel files, so they were not kept.
