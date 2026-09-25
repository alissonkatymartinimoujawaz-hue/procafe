# ihcafe_docs4 — notes

Fetched 2026-09-25 (UTC). Full request log: `FETCH_LOG.md`.

## A. IHCAFE upload folders — no listings available

- All 105 month folders `https://www.ihcafe.hn/wp-content/uploads/YYYY/MM/` (2018/01–2026/09) were requested once each.
  Every one answered **403** ("403 Forbidden: Direct access to this file is not allowed.", i.e. directory listing disabled) or
  **301** (WordPress redirect to bare `ihcafe.hn`, which the egress proxy blocks). Raw responses: `listings/`.
- `listing.csv` therefore holds only the header: no file names could be read from any folder.
- Static PDFs on `www.ihcafe.hn` are still served when the exact name is known, but the names already known from earlier logs
  (Boletín Estadístico de Comercialización 2021–2023, Resumen-Informe-2020-2021, MEMORIA-IHCAFE-COSECHA-21-22,
  Propuesta-Memoria-2021-2022, Decreto-93-2018) are already downloaded in `../ihcafe_docs2/`, so they were not fetched again.
- 8 guessed names (other MEMORIA / Propuesta-Memoria / Resumen-Informe years) were probed: all redirect (301) to `ihcafe.hn`,
  i.e. they do not exist under those names. **No IHCAFE PDF/XLSX was downloaded in this batch.**

## B. Files obtained

| File | Title (JSON-LD headline) | datePublished |
|---|---|---|
| `021_www.elheraldo.hn_economia_departamentos-mayor-incidencia-roya-cafe-honduras-HF25753400.{html,txt}` | ¿Cuáles son los departamentos con mayor incidencia de la roya del café? | 2025-05-13 |
| `022_www.elheraldo.hn_economia_avance-74-exportacion-cafe-honduras-cosecha-2023-2024-JI19998908.{html,txt}` | Más de un millón de sacos de café faltan por exportar de meta 2023-2024 | 2024-06-23 |
| `023_www.elheraldo.hn_honduras_mas-de-85-000-productores-cafe-recibiran-bono-cafetalero-anuncia.{html,txt}` | Más de 85,000 productores de café recibirán el bono cafetalero, anuncian en la SAG | 2026-02-14 |
| `024_www.laprensa.hn_economia_83-000-productores-recibiran-bono-cafetalero-honduras-BJ9308982.{html,txt}` | Más de 83,000 productores recibirán Bono Cafetalero | 2022-07-27 |
| `025_www.laprensa.hn_honduras_crisis-climatica-roya-bajos-precios-afectan-caficultura-honduras-.{html,txt}` | La crisis climática, roya y bajos precios afectan la caficultura en Honduras | 2022-11-01 |
| `026_www.laprensa.hn_economia_credito-caficultores-cafe-honduras-cafe-HXLP1219718.{html,txt}` | Crédito para caficultores estará listo en dos meses | 2018-09-25 |
| `027_www.elheraldo.hn_economia_fondos-de-pensiones-y-bancos-darian-credito-para-los-caficultore.{html,txt}` | Fondos de pensiones y bancos darían crédito para los caficultores | 2018-09-05 |
| `028_www.elheraldo.hn_elheraldoplus_investigaciones_miseria-fiebre-del-cafe-entre-productores-C.{html,txt}` | Una miseria oculta deja fiebre del café entre productores | 2024-01-04 |

Not obtained (one attempt each, see FETCH_LOG): temp.ine.gob.hn (proxy 403), latribuna.hn (redirects to a3.latribuna.hn, proxy 403),
tnh.gob.hn (proxy 403), gobiernosolidario.sgjd.gob.hn (proxy 403; second URL skipped), sag.gob.hn (proxy 403),
banadesa.hn (origin 403; second URL skipped), www.bch.hn (timeout after 60 s).

## C. Exact quotes by topic

### Rust (roya) — national average incidence

**2025 (Jan–Mar)** — `021_…HF25753400.txt` (El Heraldo, 2025-05-13, citing an IHCAFE bulletin):
> "De 5.71% fue la incidencia promedio nacional de esta enfermedad durante el primer trimestre de 2025, reflejando una reducción de 0.69%, por lo que se mantiene en un nivel medio, constató EL HERALDO con base a un boletín elaborado por el Instituto Hondureño del Café (Ihcafé)."

> "La roya sigue siendo un problema en la caficultura con afectaciones en 13 de los 15 departamentos productores del aromático."

> "Siete son los grados de riesgo contemplados para este hongo que perjudica al cafeto con alertas que van desde la azul cuando la incidencia oscila entre 0% a 5% y roja que implica arriba del 15%."

By departamento (same file, Q1 2025):
> "Santa Bárbara fue el lugar del país con un 9.29% de incidencia promedio de la roya del café, siendo la más elevada."

> "Mientras que en El Paraíso y Comayagua las afectaciones fueron del 7.91% y 7.20%, respectivamente."

> "Con un 6.88% figuró Yoro como otro sitio con una considerable incidencia del hongo no así Intibucá que reportó 5.52 puntos porcentuales que significó una afectación media, pero por debajo del promedio nacional."

> "Sin embargo, hubo departamentos con menos del 2% de casos nuevos de roya del café en específico Ocotepeque, Choluteca y Olancho."

Varieties most affected (same file):
> "Dos variedades del café específicamente Obata al igual que Catuaí son las que reportan mayores casos de la referida enfermedad."

**2022-23 crop year** — `025_…crisis-climatica-roya….txt` (La Prensa/EFE, 2022-11-01) — share of production, not an incidence %:
> "El sector cafetalero de Honduras está en alerta debido al alto nivel de incidencia de la roya que ha afectado el 20 % de la producción de café, precisó Matute, quien indicó además que las secuelas de los fenómenos climáticos disminuyeron las exportaciones del grano."

**2024 (BCH)** — `022_…JI19998908.txt`:
> "“Para 2024 se proyecta una disminución alrededor de 165 millones de dólares en el valor exportado, como resultado de la reducción en el volumen de aproximadamente 500 mil sacos de 46 kilogramos en comparación a los niveles registrados en 2023, atribuido a la alta incidencia de la roya y la escasez de mano de obra, así como por la disminución de 5% en el precio internacional […]”, subrayó el Banco Central de Honduras (BCH) en el Programa Monetario correspondiente al 2024 y 2025."
(the "[…]" replaces the Brazil-frost clause; full sentence in the file)

### Broca (berry borer)

No incidence figure in any file. Only qualitative mentions, `028_…CJ16797612.txt` (2024-01-04):
> "Igualmente, el productor Rony Duarte, también aseguró que la enfermedad de la roya y la broca están afectando la producción y la calidad del café."

### Varieties with a % of area or farms

None found. Only qualitative, `025_….txt` (2022-11-01):
> "La caficultura de Honduras, según el directivo del Ihcafé, está establecida con las variedades catimor y sarchimor, que son “altamente susceptibles” al hongo conocido popularmente como “ojo de gallo”."

### Number of producers

- 2018 — `027_….txt` (2018-09-05): "De los casi 130,000 caficultores, unos 110,000 están registrados en el Ihcafé, detalló Asterio Reyes."
- 2022 — `025_….txt` (2022-11-01): "En Honduras existen más de 100,000 productores que se dedican a la caficultura, en su mayoría en pequeña escala, con una generación de un millón de empleos directos e indirectos."
- 2022 — `024_….txt`: see Bono Cafetalero 2022 (83,273 beneficiaries).
- 2026 — `023_….txt`: "También regresa el programa presidencial Bono Cafetalero, con la que entregará fertilizante a más de 85,600 productores registrados en la base de datos del Instituto Hondureño del Café (IHCAFE)."

### Area

- 2020 (Eta/Iota) — `025_….txt`: "Las tormentas tropicales Eta e Iota, que en noviembre de 2020 azotaron a Honduras, afectaron más de 4,200 hectáreas de fincas de café y provocaron una reducción de más de 150,000 quintales (sacos de 46 kilos), agregó."
- No national area figure in these files.

### Production / exports (quintales / sacos) by crop year

- 2017-18 (the "cosecha anterior" for the 2018 credit) — `026_….txt` (2018-09-25): "Para definir el monto del crédito se tomó en cuenta la cifra de quintales de la cosecha anterior, la que fue de 9.5 millones de quintales."
- 2020-21 — `024_….txt` (2022-07-27): "5.5 Millones de sacos de 46 kilos han sido exportados por Honduras hasta el 25 de julio, un 19% menos que los 6.80 millones de sacos del mismo período de 2020-2021."
- 2021-22 — `024_….txt`: "238.57 Dólares es el precio promedio de exportación de cada saco de 46 kilogramos. El valor de los envíos suma $1,317.44, un incremento de 29% respecto a la cosecha 2020-2021."
- 2021-22 — `025_….txt`: "Honduras vendió 6,1 millones de sacos de 46 kilos del grano al cierre de la cosecha 2021-2022, lo que representa una disminución de 18,7 % en comparación con los 7,5 millones previstos a exportar a inicio del ciclo pasado y un 19,7 % con relación con el periodo 2020-2021, según cifras del Ihcafé."
- 2022-23 — `025_….txt`: "Honduras tiene una capacidad de producción de 8,5 millones de quintales de café, la más alta de Centroamérica, pero las exportaciones de la cosecha 2022-2023, previstas en 7,2 millones de sacos, podrían disminuir un 25 % debido a los factores climáticos, plagas y enfermedades, subrayó Matute."
- 2022-23 — `022_….txt`: "El año cafetero pasado comprendido entre el 1 de octubre de 2022 al 30 de septiembre de 2023 cerró con 6.9 millones de sacos del aromático exportados que dejaron 1,390 millones de dólares en ingresos."
- 2023-24 — `022_….txt` (2024-06-23): "EL HERALDO tuvo acceso al más reciente boletín estadístico de comercialización del Instituto Hondureño del Café (Ihcafé) en el que se indica que este avance en la meta exportable equivale al 74.2% de 6.5 millones de sacos del aromático a venderse a los distintos destinos del extranjero."
- 2023-24 — `022_….txt`: "Hasta el pasado 18 de junio las exportaciones del grano producido en territorio hondureño reportan una disminución del 9% (482,536 sacos) al compararse con los 5.3 millones de sacos enviados en el mismo período del ciclo 2022-2023."
- 2023-24 — `022_….txt`: "El valor de los envíos de este commodity también registra un descenso del 11% y suman 949.5 millones de dólares generados en divisas para la economía nacional."
- 2023-24 — `022_….txt`: "Pese al pronóstico del Ihcafé, los exportadores del grano catracho consideraron que los envíos podrían llegar a los 6,250,000 sacos a causa de las mermas de la comercialización en las regiones cafeteras, sostuvo Pon."
- 2023-24 — `028_….txt` (2024-01-04): "Debido a sus penurias una gran cantidad de productores han descuidado sus fincas, como consecuencia la cosecha 2023-2024 experimentará una reducción entre un 20 y 40 por ciento."
- 2024-25 — `023_….txt` (2026-02-14): "Las autoridades de la SAG manifestaron que durante la cosecha 2024-2025, el café superó los 2,150 millones de dólares, tras la exportación de seis millones de quintales, lo que permitió una significativa dinamización de la economía hondureña y la generación de miles de empleos en el área rural."
- By departamento: none in these files (El Paraíso local only, `028_….txt`: "Son más de 3,000 productores solo en esta zona. Solo la parte de Las Selvas está reportando más de 18 mil quintales de café; igual que la comunidad de Las Dificultades.").

### Credit / debt (lempiras / US$)

**2018** — `026_….txt` (La Prensa, 2018-09-25):
> "El decreto autoriza al Ihcafé para que gestione y obtenga un crédito por 1,900 millones de lempiras, del cual le prestará a los productores 200 lempiras por cada quintal (46 kilos) de café producido en la cosecha anterior."

> "Los productores que quieran acceder a los fondos deben haber registrado la cosecha en el Ihcafé. El productor pagará el préstamo en cerca de 12 años a través de una retención de 1.50 dólares (36 lempiras a cambio actual) por quintal (46 kilos) producido y exportado."

> "También se aprobó que el Banco Hondureño para la Producción y la Vivienda (Banhprovi) aporte 300 millones de lempiras a la sociedad de garantía recíproca Confianza S. A para que esta institución avale los préstamos que los caficultores soliciten a los bancos, cooperativas o financieras a nivel nacional."

`027_….txt` (El Heraldo, 2018-09-05):
> "TEGUCIGALPA, HONDURAS.- Las pláticas comenzaron para concretar un crédito de 1,900 millones de lempiras para los productores de café."

> "El productor pagará el préstamo en un plazo de entre 8 y 12 años a través de una retención de 1.50 dólares (36 lempiras) por quintal. El que no se endeude recibirá el reembolso de la retención."

(The 2021 "L5,565 millones" debt article on latribuna.hn could not be fetched.)

### Bono Cafetalero

**2022** — `024_….txt` (La Prensa, 2022-07-27):
> "Laura Elena Suazo, titular de la SAG, informó que son 83,273 productores de café a nivel nacional los beneficiados con el Bono Cafetalero en la segunda quincena de agosto, en alianza con el Instituto Hondureño del Café (Ihcafé)."

> "Detalló que en el presente año se entregarán 216,223 quintales de fertilizantes y una fórmula mínima de 17-3-17 a los productores, lo que va a permitir el aumento en la producción del sector café y, por ende, un mayor beneficio para el sector productor."

> "De los 83,273 productores beneficiados con la entrega, 60,642 producen entre 1 y 50 quintales del grano y se les asignará dos quintales de fertilizantes; 18,216 son medianos, que producen entre 51 a 100 quintales del grano y recibirán cuatro quintales de fertilizante, y los productores que reportaron entre 101 y 125 quintales de café recibirán 5 sacos del abono."

> "La titular de la SAG puntualizó que en esta acción del Bono Cafetalero se invertirán L 250 millones y que los productores favorecidos también recibirán asistencia técnica y capacitación."

**2026** — `023_….txt` (El Heraldo, 2026-02-14):
> "\"El Gobierno trabaja en la asignación presupuestaria para incrementar la entrega de fertilizantes a pequeños productores, pasando de 300 mil quintales a cerca de 400 mil quintales, con el propósito de mejorar la productividad y la calidad del grano\", indicó Ordoñez."

> "También regresa el programa presidencial Bono Cafetalero, con la que entregará fertilizante a más de 85,600 productores registrados en la base de datos del Instituto Hondureño del Café (IHCAFE)."

(2023 and 2024 Bono figures: sources on tnh.gob.hn / gobiernosolidario.sgjd.gob.hn / sag.gob.hn were blocked.)

### Fertiliser prices

None in the fetched files. Closest price quote (farm-gate cherry price, 2024-01-04, `028_….txt`):
> "Según los cálculos, el quintal de café uva- que equivale a 20 libras de grano en oro e igual cantidad de café molido- al productor hondureño se lo pagan entre 550 y 600 lempiras (22.79 y 24.70 dólares)."
