# NOTES: ihcafe_docs5 (2026-09-25)

## What was reachable (see NETWORK.md)
- The proxy blocked (CONNECT 403) these hosts: ihcafe.hn, perfectdailygrind.com, www.ico.org (redirects to ico.org), temp.ine.gob.hn, tnh.gob.hn, sag.gob.hn, exportadoresdecafe.com, www.hondudiario.com, icndigital.com, stonex.digital. www.ihcafe.hn answers 301 and redirects to ihcafe.hn, which is blocked.
- www.latribuna.hn: the homepage returned 403. The article redirected to a3.latribuna.hn, which the proxy blocked. Not obtained.
- banadesa.hn: 403 (not needed by any step).
- www.bch.hn: reachable, but it stalls often. It returned timeouts (curl 28) for some requests, and the long Chrome UA string ("AppleWebKit ... KHTML, like Gecko") timed out every time. The short UA worked intermittently.
- archive-api.open-meteo.com: the first test returned 429, and the one retry returned 200. Step 5 downloaded 1 of 10 points (el_paraiso_danli), then got 429 "Daily API request limit exceeded. Please try again tomorrow." and stopped as instructed.

## Step 1: IHCAFE documents. NOT OBTAINED
ihcafe.hn is blocked by the proxy, so none of the mdocs files (5360, 6940, 4680, 4163) or listing pages could be fetched. mdocs_links.csv only has a header. No variety, rust, broca, renovation, seed or producer quotes could be taken from IHCAFE files in this run.

## Step 2: Perfect Daily Grind. NOT OBTAINED (host blocked).

## Step 3: BCH credit (obtained)
BCH statistics pages are SharePoint pages whose menus and lists load through JavaScript. I found the files through
`/_api/navigation/menustate` (saved as bch_nav.json and bch_nav_tree.txt) and the SharePoint REST API of the web `/estadisticos/EF`
(library list: bch_EF_lists.json; file listing: bch_files.csv, with library, name, URL and last-modified).
BCH has no coffee-specific series. The finest breakdown is "Agropecuaria" (loans) or "Agricultura, Ganadería, Silvicultura y Pesca" (interest rates).

| file | BCH title / content | sheets |
|---|---|---|
| bch_Préstamos_de_las_Otras_Sociedades.xlsx (modified 2026-09-22) | "Préstamos sobre Saldos de las Otras Sociedades de Dépositos al Sector Privado por Actividad"; "Saldos en millones de lempiras y variaciones interanuales"; columns Fecha, Agropecuaria, Industria, Servicios, Propiedad Raíz, Comercio, Consumo, Total, Variación...; monthly 2017-01 to 2026-07. The second sheet is "Préstamos Nuevos de las Otras Sociedades de Dépositos al Sector Privado por Actividad" | Pres sobre saldos; Pres Nuevos |
| bch_Préstamos_de_BC_Porcentaje_PIB.xlsx | "Préstamos de los Bancos Comerciales por Actividad Económica como porcentaje del PIB" (Agropecuaria, Industria, ...) | Pres-saldos % PIB |
| bch_Tasas_Saldos_Sistema_Financiero_por_AE.xlsx | "Tasa de Interés Promedio Ponderado sobre Saldos del Sistema Financiero por Actividad Económica", including "Agricultura, Ganadería, Silvicultura y Pesca" | Moneda Nacional; Moneda Extranjera |
| bch_Agregados_Monetarios.xlsx | monetary aggregates | Datos |
| bch_Captación_de_los_Bancos_Comerciales.xlsx | commercial bank deposits | Datos |
| bch_comunicado_credito_sector_privado_2026.pdf (+ .txt) | BCH COMUNICADO "El crédito al sector privado se acelera, respaldado por menores tasas de interés y mayor financiamiento a las empresas" (June 2026) | – |

These failed twice with timeouts: "Crédito al Sector Privado.xlsx" and "Captación de las Otras Sociedades.xlsx". The listing of library "LIBAGREGADOS CREDITO Y CAPTACIN" also failed (see FETCH_LOG.md).

I extracted a series to bch_prestamos_agropecuaria.csv (sheet, date, Agropecuaria, Total; millions of lempiras, values exactly as stored in the xlsx; dates converted from Excel serials).
December values (Agropecuaria / Total), as stored:
- Pres sobre saldos: 2017-12 20610.3 / 264246; 2018-12 24314.800000000003 / 303555.09999999998; 2019-12 25923.5 / 329322.40000000008; 2020-12 23787.4 / 336756; 2021-12 25569.699999999997 / 380303; 2022-12 27310.5 / 456129.4; 2023-12 27976.065749959998 / 542408.17346388777; 2024-12 30700.613323690002 / 608604.94304626586; 2025-12 31109.749884659999 / 642953.32718419016; latest 2026-07 32548.219908250001 / 677619.07312350324.
- Pres Nuevos: 2017-12 10924.8; 2018-12 16237; 2019-12 15389.3; 2020-12 14129.4; 2021-12 14373.699999999999; 2022-12 15012.9; 2023-12 15346.5; 2024-12 17038.595666469999; 2025-12 19080.13470844; 2026-07 19250.337870039999. The values rise through each year, so they look cumulative year-to-date. I have not verified this.

Exact quotes from bch_comunicado_credito_sector_privado_2026.txt:
- "Al 4 de junio de 2026, el saldo del crédito al sector privado registró un crecimiento interanual de 6.3%, equivalente a L41,855.9 millones"
- "el saldo del crédito alcanzó L705,244.4 millones, superior en L22,410.3 millones respecto al cierre de 2025."
- "En MN, al 29 de mayo de 2026, la tasa de interés activa promedio ponderado sobre operaciones nuevas se ubicó en 12.89%, registrando una reducción de 3.79 puntos porcentuales (pp), destacando disminuciones particularmente en actividades de industria, agricultura y comercio."

## Step 4: Press. NOT OBTAINED (all hosts blocked; La Tribuna redirected to a blocked host).

## Step 5: ERA5 rain (partial)
- era5_rain_el_paraiso_danli.json (14.03,-86.57; 1981-01-01 to 2026-09-23 requested). Open-Meteo returned the grid cell and elevation shown in the JSON.
- monthly_rain.csv: el_paraiso_danli only (key,year,month,rain_mm,n_days). The last month (2026-09) has n_days=18, so ERA5 data end before the requested end date.
- The other 9 points were not fetched because of the 429 daily limit.

## Step 6 topics without sources in this run
There are no quotes on varieties (Lempira, Parainema, IHCAFE 90, Catuai, ...), renovation, seed or nursery numbers, rust or broca incidence, producers and area, Bono Cafetalero, or coffee debt, because every source for them was blocked.
