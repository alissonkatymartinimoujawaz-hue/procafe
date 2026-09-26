# Mexico – SIAP (SADER/DGSIAP), café cereza

Output: `mexico_siap.csv` (69 rows). Raw files are in `raw/mexico_siap/`.

## What was obtained
All values are for **café cereza**, which is coffee cherry before processing (arabica + robusta total, about 95% arabica). The period is the coffee cycle, October to September. SIAP labels a cycle with its **ending** year: "ciclo 2022" starts in October 2021, as the Escenario reports state. So the CSV uses `crop_year` with period `2021/22` = SIAP año agrícola 2022.

| Period | planted | harvested | production | yield | Source (latest edition used) |
|---|---|---|---|---|---|
| 2004/05–2014/15 | yes | yes | yes | yes | FIRA *Panorama Agroalimentario Café 2016*, statistical annex (data SIAP) |
| 2015/16 | yes | yes (prelim) | yes | yes (prelim) | SAGARPA *Planeación Agrícola Nacional 2017-2030 – Café* (planted, production); FIRA 2016 (harvested, yield) |
| 2016/17–2018/19 | – | – | yes | – | SIAP *Expectativas Agroalimentarias* 2019/2020/2021 |
| 2019/20 | yes | yes | yes | – | SIAP *Escenario mensual – Café* (Oct 2021); production from Expectativas 2022 |
| 2020/21 | yes | yes | yes | yes | Escenario Café, Nov 2022 |
| 2021/22 | yes | yes | yes | – | Escenario Café, Nov 2023 |
| 2022/23 | yes | yes | yes | yes | Escenario Café, Aug 2024; production from Expectativas 2024 |
| 2023/24 | yes | yes | yes | yes | Escenario Café, Aug 2024 (cierre preliminar) |

**Missing:** 1998/99–2003/04 (no source was reachable), areas and yield for 2016/17–2018/19, yield for 2019/20 and 2021/22, and anything after 2023/24. None of the reachable sources gave superficie siniestrada (area_damaged).

## Caveats
- **The official cierre database could not be reached.** SIACON, the Anuario and the open-data CSVs were all unreachable. Every value comes from SIAP/SADER/FIRA publications that quote SIAP. Recent years are often labelled *preliminar*. Where a later edition revised a value, the CSV keeps the latest one, and `notes` gives the earlier values.
- **The FIRA 2016 annex contradicts itself.** Its national summary table and its state-table totals disagree for 2010/11 (harvested area 688,208 vs 689,208 ha) and for 2011/12 (695,350 ha / 1,336.9 kt vs 724,803 ha / 1,358,840 t). The CSV uses the summary table, which agrees with the published national yield. For 2012/13 the 2016 state table gives 1,257,983 t. The CSV instead uses 1,272,919 t from the 2014 edition, which matches the 1,272.9 kt in the 2016 summary.
- **2015/16:** Planeación gives 824.08 kt and 730,011 ha planted. The harvested area 644,963 ha and yield 1.30 are FIRA preliminaries based on 835 kt, so production divided by area here (1.28) differs from the published yield.
- **Unit conversions:** 1,336.9 kt (2011/12) and 824.08 kt (2015/16) were converted to t by multiplying by 1000. Both notes say so.
- **2022/23 production:** the Escenario report of 15 Aug 2024 gives 1,056,388 t. Expectativas 2024 and Expectativas Agosto 2024 give 1,058,862 t (1,058.9 kt). The CSV uses 1,058,862 t.
- **How the numbers were read:**
  - The Escenario tables are PDF form XObjects, extracted with `raw/mexico_siap/forms.py` (built on `tools/pdftext.py`).
  - The August 2024 table is a JPEG image. I read it visually, and it matches the report's own text.
  - The Planeación PDF is AES-encrypted with an empty password. It was decrypted locally with `raw/mexico_siap/decrypt.py`, which uses openssl.
- **Checks:** production ÷ harvested area agrees with the published yield to within rounding for every year with all three values, except 2015/16 (see above).

## URLs tried
- **Failed:**
  - `infosiap.siap.gob.mx`: http and https, including `:8080` (proxy CONNECT 502 / no response)
  - `nube.siap.gob.mx`, including `/cierreagricola/` and `/gobmx_publicaciones_siap/` (fail)
  - `www.siap.gob.mx`, `siap.gob.mx` (CONNECT 403)
  - `nube.agricultura.gob.mx`: `/cierre_agricola/`, `/datosAbiertos/`, `/panorama_siap/`, `/panorama_dgsiap/2025.pdf`, `infosiap.agricultura.gob.mx` (https fails; http gives proxy 403)
  - `www.datos.gob.mx`, `www.cedrssa.gob.mx`, `www.inegi.org.mx`, `internet.contenidos.inegi.org.mx`, `www.fira.gob.mx`, `amecafe.org.mx`, `sniim.economia.gob.mx`, `www.uv.mx` (observacafe), `ceieg.chiapas`/`veracruz`, `gaceta.diputados.gob.mx`, `drive.google.com` (hosts Panorama 2025), `scielo`, `redalyc`, `researchgate` (all fail)
  - `www.gob.mx/cms/uploads/attachment/file/166375/cafecereza_monograf_a.pdf` (404)
- **Worked:** `www.gob.mx/cms/uploads/attachment/file/...` is served directly, with no challenge. The `www.gob.mx` HTML pages sit behind an Akamai JS challenge, which a headless Chromium (Playwright, via the proxy) passes. That was used only to list document links on the DGSIAP and FIRA pages.
- **Checked but not useful:** Panorama Café 2014 and 2015 (superseded by the 2016 annex), Cierre de la Producción Agropecuaria 2017 (no coffee numbers), Panorama 2021 boletín, monografía café cereza 2023 (no numbers).

## URLs used
- https://www.gob.mx/cms/uploads/attachment/file/200636/Panorama_Agroalimentario_Caf__2016.pdf (also 99094 = Café 2014, 61949 = Café 2015)
- https://www.gob.mx/cms/uploads/attachment/file/256426/B_sico-Caf_.pdf (Planeación Agrícola Nacional 2017-2030, Café)
- Expectativas Agroalimentarias 2019–2024, attachment ids 723485, 723486, 723487, 723488, 819645, 921715 (plus 940838 = Expectativas Agosto 2024)
- Escenario mensual Café, 2021–2024: 31 PDFs in `raw/mexico_siap/escenarios/`. The key ones are 691976 (Sep 2021), 807064 (Oct 2022), 870879 (Oct 2023) and 938476 (Jul 2024).
- SIAP article "Café cereza cierra su ciclo productivo 2018": https://www.gob.mx/agricultura/dgsiap/articulos/cafe-cereza-cierra-su-ciclo-productivo-2018 (text saved)

## Possible future improvement
If `nube.agricultura.gob.mx/cierre_agricola/` or the SIAP open-data files become reachable, replace everything with the official cierre series for 1998 onward. That series has sembrada, cosechada, siniestrada, producción and rendimiento, by año agrícola.
