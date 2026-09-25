# Coffee zones fetch — notes (2026-09-25)

Everything below comes from the files in this folder. Nothing is estimated.

## A. ERA5-Land daily (Open-Meteo archive, models=era5_land) — PARTIAL

- **Only 10 of 13 points were obtained.** `intibuca_laesperanza`, `lempira_gracias` and `olancho_campamento` failed. They got HTTP 429 and SSL connection drops, and then the API answered `{"reason":"Daily API request limit exceeded. Please try again tomorrow.","error":true}` (saved as `era5_land_<key>.error.json`).
- **`precipitation_sum` is null for every day at every point.** Open-Meteo returned the field (units `mm`) with all values `null` when `models=era5_land`. So `monthly.csv` has an empty `rain_mm` and `n_days = 0` everywhere. Only the temperatures are usable.
- To get the rain, re-request after the daily quota resets, probably without `models=era5_land` (e.g. `models=era5` or the default model). This was not tried because the quota was exhausted.
- The temperature series run from 1981-01-01 to 2026-09-18 (16,697 non-null days; 2026-09-19..23 are null). Open-Meteo snaps each point to the nearest 0.1° grid cell.

| key | requested lat, lon | returned lat | returned lon | elevation_m (Open-Meteo) | tmax/tmin range | rain |
|---|---|---|---|---|---|---|
| el_paraiso_danli | 14.03, -86.57 | 14.00 | -86.60 | 764.0 | 1981-01-01 → 2026-09-18 | all null |
| el_paraiso_town | 13.87, -86.56 | 13.90 | -86.60 | 771.0 | 1981-01-01 → 2026-09-18 | all null |
| comayagua_siguatepeque | 14.6, -87.83 | 14.60 | -87.80 | 1089.0 | 1981-01-01 → 2026-09-18 | all null |
| comayagua_lalibertad | 14.72, -87.6 | 14.70 | -87.60 | 595.0 | 1981-01-01 → 2026-09-18 | all null |
| lapaz_marcala | 14.16, -88.03 | 14.20 | -88.00 | 1266.0 | 1981-01-01 → 2026-09-18 | all null |
| santabarbara | 14.92, -88.24 | 14.90 | -88.30 | 262.0 | 1981-01-01 → 2026-09-18 | all null |
| lempira_gracias | 14.59, -88.58 | – | – | – | NOT OBTAINED (daily limit) | – |
| copan_santarosa | 14.77, -88.78 | 14.80 | -88.80 | 1141.0 | 1981-01-01 → 2026-09-18 | all null |
| ocotepeque | 14.43, -89.18 | 14.40 | -89.20 | 801.0 | 1981-01-01 → 2026-09-18 | all null |
| intibuca_laesperanza | 14.31, -88.18 | – | – | – | NOT OBTAINED (daily limit) | – |
| olancho_campamento | 14.55, -86.65 | – | – | – | NOT OBTAINED (daily limit) | – |
| yoro | 15.14, -87.13 | 15.20 | -87.20 | 635.0 | 1981-01-01 → 2026-09-18 | all null |
| fmorazan_valledeangeles | 14.15, -87.04 | 14.20 | -87.00 | 1278.0 | 1981-01-01 → 2026-09-18 | all null |

## B. IHCAFE (www.ihcafe.hn) — BLOCKED / not obtained
- WordPress REST API `wp-json/wp/v2/media?search=...` (boletin, estadistic, exportaci, informe, cosecha, produccion): **HTTP 401** for all six, body: `{"code":"rest_api_authentication_required","message":"La API REST se ha restringido a solo usuarios identificados."}` (responses saved in `ihcafe/media_*.json`).
- `https://www.ihcafe.hn/produccion-nacional/`: curl followed a redirect and the proxy refused the tunnel (`CONNECT tunnel failed, response 403`), probably because it redirects to the blocked `ihcafe.hn` host without www. Not retried, and no file was saved.
- As a result **no IHCAFE PDFs were downloaded**. There is no table of exports by departamento or of production by departamento from IHCAFE itself. IHCAFE export figures quoted in the press are listed under D.

## C. ICO (www.ico.org) — BLOCKED
The proxy refused all five URLs (`CONNECT tunnel failed, response 403`). No PDFs were saved, so `ico_honduras_lines.txt` was not produced.

## D. Press / outlook pages
| # | Source | Status | datePublished (JSON-LD) |
|---|---|---|---|
| 01 | laprensa.hn IN28070778 "Envíos de café alcanzan récord en la cosecha 2025-2026" | OK | 2025-11-05T18:40-06:00 |
| 02 | laprensa.hn MJ29575933 "Crece la exportación de café en los primeros meses de la nueva cosecha" | OK | 2026-03-04T15:56-06:00 |
| 03 | laprensa.hn AJ31298329 "Honduras perfila récord de más de $2,200 millones…" | OK | 2026-07-03T06:00-06:00 |
| 04 | laprensa.hn BH31414270 "Café hondureño rompe récord y supera los $2,158 millones…" | OK | 2026-07-15T11:35-06:00 |
| 05 | elheraldo.hn MM30870851 "El 42.8% de las exportaciones de café se registraron en febrero y marzo" | OK | 2026-05-30T10:08-06:00 |
| 06 | elheraldo.hn ID30448347 "¿Cuánto falta para lograr meta exportable de café de cosecha 2025-2026?" | OK | 2026-05-04T15:52-06:00 |
| 07 | elheraldo.hn MI29305180 "A 8.44% se elevó promedio de incidencia de la roya del café en Honduras" | OK | 2026-02-15T11:20-06:00 |
| 08 | hondudiario.com (7.5 M sacos 2026-27) | BLOCKED (proxy CONNECT 403) | – |
| 09 | icndigital.com (7.5 M sacos 2026-27) | BLOCKED (proxy CONNECT 403) | – |
| 10 | proceso.hn (sequía hasta 2027) | BLOCKED (proxy CONNECT 403) | – |
| 11 | stonex.digital (sequía, cosecha 2026-27) | BLOCKED (proxy CONNECT 403) | – |
| 12 | latribuna.hn (El Niño resurge, 2026-03-21) | HTTP 403 from site (block page discarded) | – |
| 13 | exportadoresdecafe.com/cifras | BLOCKED (proxy CONNECT 403) | – |
| 14 | dailycoffeenews.com 2026-05-19 | BLOCKED (proxy CONNECT 403) | – |
| 15 | CPC ENSO Diagnostic Discussion | OK | issued 10 September 2026 |
| 16 | IRI ENSO current forecast | BLOCKED (proxy CONNECT 403) | – |
| – | CPC oni.ascii.txt | OK | last row JJA 2026 |

**Note:** the page for the MI29305180 URL redirected from `/portada/` to `/economia/`.

### Exact quotes (from the saved .txt files)
**01 — La Prensa, 2025-11-05**
- "Los envíos del aromático sumaron 51,183.91 sacos de 46 kilogramos durante octubre, lo que representa un alza interanual del 126.7%, equivalente a 28,603.67 sacos más, según las estadísticas del Instituto Hondureño del Café (Ihcafé)."
- "Al cierre de la cosecha 2024-2025, los envíos de 6.1 millones de sacos de café generaron 2,142.9 millones de dólares en divisas, una cifra histórica para la caficultura hondureña."
- "La generación de divisas alcanzó 17.8 millones de dólares, con un precio promedio de venta de 348.26 dólares por saco."

**02 — La Prensa, 2026-03-04**
- "Hasta el 3 de marzo de 2026, según cifras del Instituto Hondureño del Café (Ihcafe), el país registró 3,023,652 sacos (de 46 kilogramos) exportados en los primeros cinco meses del ciclo actual; representa un significativo aumento del 57.6% en comparación con el mismo período de la cosecha anterior 2024-2025, cuando envió al exterior 1,918,225 sacos."
- "…un avance importante hacia la meta proyectada para esta cosecha, estimada inicialmente en 6.5 millones de sacos."
- "Hasta el momento, el sector exportador ha cumplido aproximadamente el 46.5% del pronóstico, tiene pendientes 3,476,348 sacos por exportar en los meses restantes (hasta septiembre de 2026)."
- "…una generación de divisas de $1,060.75 millones, lo cual representa un alza del 67.24% respecto a los $634.25 millones obtenidos en el ciclo previo…"
- "…el precio promedio de exportación logrado por Honduras ha sido de $350.82 por saco, lo que equivale a un incremento del 6.1% frente a los $330.64 registrados en la temporada pasada."

**06 — El Heraldo, 2026-05-04**
- "Transcurridos siete meses de la cosecha 2025-2026 se avanzó en 76.6% de envíos del aromático equivalente a 4.97 millones de sacos de 46 kilogramos, faltando 1.5 millones de sacos de la meta exportable establecida para este ciclo…"
- "En 38% se elevaron las exportaciones de café, es decir 1.37 millones de sacos adicionales comparado a los 3.60 millones de sacos registrados durante el período 2024-2025."
- "De los casi cinco millones de sacos exportados del 1 de octubre al 30 de abril pasado se obtuvieron 1,638 millones de dólares, mostrando un incremento interanual del 30% que implican $374.42 millones."
- "El Instituto Hondureño del Café (Ihcafé) pronosticó que para el presente año cafetero se exportarían 6.5 millones de sacos, menor en medio millón de sacos respecto a lo proyectado inicialmente para la pasada temporada."
- "…en marzo se vendieron 1.26 millones de sacos por $389 millones, una cifra histórica."

**05 — El Heraldo, 2026-05-30**
- "De los 6.5 millones de sacos del commodity que se definieron como meta exportable para esta temporada se alcanzó el 89.4% previo a la culminación de mayo."
- "Para los cuatro meses que restan se deberán enviar 690,487.19 sacos de 46 kilogramos, por lo que sobrepasaría el pronóstico de exportaciones."
- "…al 26 de mayo el valor de los envíos de café fue de 1,875 millones de dólares, mostrando un incremento interanual del 20% equivalente a $308.33 millones."
- "Al cierre del octavo mes de este ciclo las ventas del aromático ascendieron a 5.80 millones de sacos de 46 kilogramos…"
- "El precio promedio de exportación de café por saco se ha reducido en 9%, siendo a la fecha de $322.91…"

**03 — La Prensa, 2026-07-03**
- "…entre el 1 de octubre de 2025 y el 1 de julio de 2026 se exportaron 6,663,920 sacos de 46 kilogramos, con un valor de 2,107.5 millones de dólares."
- "El resultado supera el registrado en el mismo período de la temporada 2024-2025, cuando se exportaron 5,773,579 sacos por un valor de 1,887 millones de dólares."
- "Con ese desempeño, Honduras superaría el pronóstico inicial de exportación de 6.7 millones de sacos al cierre de la presente cosecha."  *(Note: articles 02, 05 and 06 give the target as 6.5 million.)*
- "Otro dato relevante es que los contratos de venta suman 7.03 millones de sacos, por lo que aún estarían pendientes de exportarse alrededor de 430,000 quintales."
- "Se estima que durante julio y agosto, los dos últimos meses de la cosecha, las exportaciones oscilarán entre 310,000 y 340,000 sacos…"
- "…el precio promedio de exportación se ubicó en 316.26 dólares por saco durante la actual cosecha, inferior a los 356.20 dólares registrados en la temporada anterior…"

**04 — La Prensa, 2026-07-15** (latest export figure found)
- "Según el informe de comercialización del Instituto Hondureño del Café (Ihcafé), entre el 1 de septiembre de 2025 y el 14 de julio de 2026 se exportaron 6,853,390.59 quintales de 46 kilogramos, por un valor de 2,158.5 millones de dólares. Aún restan 47 días para el cierre de la cosecha 2025-2026."  *(Note: the article says "1 de septiembre", but the other articles start the crop year on 1 October.)*
- "…las exportaciones sumaron 6.85 millones de sacos de 46 kilogramos, mostrando un incremento de 24%, comparado con 5.51 millones registrados en igual período de 2024-2025."
- "En la temporada anterior, Honduras exportó 6,117,313.13 quintales, que generaron 2,148 millones de dólares en divisas, con un precio promedio de 351.14 dólares por quintal…"
- "…los contratos de venta alcanzan 7.14 millones de quintales de 46 kilogramos, un incremento de 23% frente a los 5.81 millones registrados a la misma fecha de la cosecha 2024-2025."
- "Honduras tiene pendiente la exportación de alrededor de 290,000 quintales, con una proyección de ingresos de entre 85 y 90 millones de dólares durante lo que resta de la temporada 2025-2026."

**Summary of 2025/26 exports (46-kg bags) from the press quotes above:** 51,183.91 (October 2025) → 3,023,652 (to 3 Mar 2026) → 4.97 M (to 30 Apr) → 5.80 M (to 26 May) → 6,663,920 (to 1 Jul) → 6,853,390.59 (to 14 Jul 2026). 2024/25 full season: 6,117,313.13 quintales (6.1 M sacos).

**07 — El Heraldo, 2026-02-15 (roya)**
- "…al cierre de enero pasado el promedio nacional de incidencia pasó de 7.57% a 8.44%, un incremento de 0.57%, revisó EL HERALDO en un reporte del Instituto Hondureño del Café (Ihcafé)."  *(Note: 8.44 − 7.57 = 0.87; the article says 0.57.)*
- "Por departamento la incidencia de la roya del café va desde un 14.08% a un 2.06%, siendo Comayagua, Cortés, Santa Bárbara y Yoro los que registraron el nivel más alto."
- "Casi un 30% de las fincas muestreadas por el Ihcafé presentan niveles altos o muy altos de roya superiores al 10%."
- "El nivel de riesgo se ubica en 4 que representa alerta amarilla…"
- "Para febrero se proyecta una disminución de la enfermedad … asociada a la reducción de las precipitaciones, el descenso de las temperaturas y, principalmente, a la caída natural de las hojas infectadas…"

**15 — NOAA CPC ENSO Diagnostic Discussion, issued 10 September 2026**
- "ENSO Alert System Status: El Niño Advisory"
- "El Niño is strengthening, with a greater than 90% chance of a very strong event during the Northern Hemisphere fall and winter 2026-27."
- "…reaching +1.8°C in Niño-3.4, +2.5°C in Niño-3, and +3.4°C in Niño-1+2…"
- "During the October-December 2026 season, there is a 75% chance of a historic event that would exceed the strength of previous El Niño events dating back to 1950 (+2.5°C or more for a 3-month RONI value)."

**oni.ascii.txt (CPC)** — last rows: FMA 2026 0.11, MAM 2026 0.46, AMJ 2026 0.95, MJJ 2026 1.39, JJA 2026 1.80.

None of the fetched pages (the sequía/floración articles were blocked) gave quotes on lluvia, sequía or floración for 2026-27, and none gave the 7.5 M sacos 2026-27 projection.
