# ihcafe_docs2: IHCAFE, variety, decree and press downloads (2026-09-25, environment Honduras)

Every URL in `../varieties_finance/sources_to_fetch.csv` and in the per-URL table of `../ihcafe_docs/FETCH_LOG.md` was tried (max 2 tries, 40 MB cap). The per-URL result is in `FETCH_LOG.md`. **52 files were saved.** Each has a `.txt` extraction next to it with the same name.

## How the text was extracted

- `pypdf` could not be installed because PyPI is blocked by the egress proxy (HTTP 403). LibreOffice has no PDF import filter here, so PDFs were read with `pdf2txt.py`, a small extractor written with the Python standard library only. It uses ToUnicode CMaps and the Tj/TJ operators.
- **What the extractor can't do:**
  - Scanned pages give no text. This affects `016` (Decreto 93-2018) and nearly all of `042`.
  - The two-column pages of *La Gaceta* (`019`, `020`, `024`) come out with the columns interleaved.
  - The 2021/22 harvest memoir `041` has letter-spaced text ("pr oduct or es").
  - Tables come out as runs of numbers.
  - The originals are the reference. Quotes below were checked against the `.txt` files.
- HTML pages were converted with `html2txt.py`. Press articles also keep the JSON-LD `datePublished` and `articleBody`.
- The XLSX file was converted with `zipfile` and XML parsing. Dates are Excel serial numbers (36528 = 2000-01-03).

## What could not be fetched (HTTP 000 = the proxy refused the host)

- **`ihcafe.hn` is blocked.** `www.ihcafe.hn` only returns a 301 redirect to `ihcafe.hn`, except for direct `/wp-content/uploads/…` files, which it serves. So none of the following could be read:
  - every `?mdocs-file=` document (5360 Boletín SAT, 4163, 4173, 4268, 4337, 4333, 4413, 4331, 4347, 4219, 5603, 6940);
  - the `/publicaciones/`, `/leyes-y-reglamentos-del-sector/`, `/investigacion-y-desarrollo/` and `/preguntas-frecuentes/` pages;
  - the REST API, which answers 401 (login required).
- **Other blocked or failed URLs:**
  - Blocked hosts: anacafe.org, yumpu.com, researchgate.net, d-nb.info (Avelino et al. 2015), bdigital.zamorano.edu, sag.gob.hn, ceniss.gob.hn, aecid.hn (cost guide), laccei.org, temp.ine.gob.hn, apps.fas.usda.gov, api.worldbank.org, a1/archivos.latribuna.hn, revistahibueras.hn, perfectdailygrind.com and www.ico.org (prices paid to growers).
  - banadesa.hn returned 403.
  - WCR pages `obata-rojo`, `geisha`, `icatu` and `ihcatu` returned 404. The Obatá page exists as `obata-red` and was saved.
- **IHCAFE statistical PDFs from 'publicaciones':** the listing page is unreachable. Instead, direct `wp-content` links were found by web search and downloaded (`040`–`052`, 13 files, under the 25-file cap):
  - Informe Estadístico 2020-21;
  - Memoria de cosecha 2021-22 (two versions);
  - ten "Boletín Estadístico de Comercialización" issues, Aug 2021 – Feb 2023.

  No other Anuario, Informe or Memoria links were found.

## Files and what they contain

Letters mark the six topics:
- (a) release year of IHCAFE 90, Lempira, Parainema, Ihcatú 75, Anacafé 14 and Obatá
- (b) share of coffee area or farms by variety
- (c) rust resistance status by variety
- (d) credit programme amounts
- (e) production cost per quintal
- (f) prices paid to producers

"—" means the file has nothing on that topic.

### Varieties and rust

**001 — PROMECAFE WikiCafe, "Durabilidad de la resistencia genética a la roya del café … en variedades mejoradas en Honduras al 2019"** (IHCAFE authors; data to 2019).
- (a) "…identificación de los híbridos de Timor 832/1 y 832/2 de donde Honduras liberó el IHCAFE 90 (1990), Lempira (1998) y Parainema (2004)."
  - Cuadro "Durabilidad de resistencia a roya en variedades mejoradas", columns *Liberada | Resistente | Tolerante | Susceptible a razas emergentes | Resistencia efectiva (años)*:

    | Variedad | Liberada | Resistente | Tolerante | Susceptible | Años |
    |---|---|---|---|---|---|
    | IHCAFE 90 | 1990 | 1990-2015 | | 2016 (20%) | 25 |
    | Lempira | 1998 | 1998-2001 | 2002-2015 | 2016 | 17 |
    | Parainema* | 2004 | 2004-2019 | | | +15 |
    | F1 Milenio | 2007 | 2007-2015 | | 2016 | 8 |
    | Icatu 48 | 2007 | 2007-2015 | | 2016 | 8 |
    | Icatu 75 | 2007 | 2007-2015 | | 2016 | 8 |
    | Centroamericano | 2007 | 2007-2018 | | 2019 | 11 |
    | H27** | | 2000-2017 | | 2018 | 17 |
    | Obatá** | | 2006-2015 | | 2016 (20%) | 9 |

    "* Variedades mejoradas que aún conservan su resistencia."
  - Icatu 75 appears here with a 2007 date. The text also says Icatu 48 and 75 "aún se encuentran en su fase de evaluación de estabilidad previo a su liberación", so 2007 is when evaluation started, not a commercial release.
- (b) "Estos materiales resistentes reemplazaron los susceptibles y constituyen el 65% del área cultivada desde 2012 dominada por Lempira."
- (c)
  - "…logrando en 2007 identificar la pérdida progresiva de la resistencia en Lempira, hasta volverse susceptible en 2015 junto con el F1 Milenio, Icatu 48 e Icatu 75."
  - "…genotipos que afectan 20 % del IHCAFE 90 y que el H27, Parainema, Centroamericano, Anacafe 14 y Batian son resistentes hasta 2018 y 2019 donde el H27 y el Centroamericano se vuelven susceptibles."
  - "…variedades parcialmente afectadas como IHCAFE-90 y Obatá donde solo el 80% de su progenie es susceptible, y genotipos completamente resistentes como la variedad Parainema, híbrido F1 centroamericano, H27, Batian…"
  - "…en 2016 en la comunidad de Las Vegas de Jalan, Juticalpa, Olancho, se reporta y verifica en campo que la variedad Lempiras se volvió susceptible a la roya presentando 100% de defoliación…"
  - "…la resistencia a la roya dura entre 8 y 25 años en Honduras…"
- (d)–(f) —

**025 — PROMECAFE XXIV Simposio (4 Sep 2019), slides "Durabilidad de la resistencia a la roya del café en Honduras".** These are the same authors and data as 001.
- (a)(c) The same table as 001, with the release years 1990 / 1998 / 2004 / 2007×4. In the slide, IHCAFE 90's durability reads "+25", and the Obatá row shows 2002-2015 tolerant and 2016 (20%).
- (c) The inoculation results list:
  - "Variedades Resistentes: 1. Parainema T5296-184 · 2. Línea T5296-170 · 3. Anacafe-14 · … 9. Batian · 10./11. Híbrido de Timor 832/1, 832/2 · 12. Diferenciales con SH3"
  - "Variedades Susceptibles: 1. Ruiru II · 2. Caturra · 3. Líneas de Lempira · 4. H27 y otros"
- (b)(d)(e)(f) —

**026 — PROMECAFE XXIV Simposio (2019), J. A. Pineda, "Determinación del mejor arreglo espacial para variedades … liberadas por IHCAFE".**
- Planting-density trials, 2014–2018, for Lempira, Parainema and IHCATU. Yields are given in qq pergamino seco (p.s.) per manzana (Mz) and per hectare, e.g.
  - "Lempira 2.00 X 1.00 3500 5,000 73.68 49.24 25.12 70.49"
  - "Parainema 2.00 X 0.75 4666 6,666 61.82 49.29 46.13 74.87"
- Cuadro 1 lists "las variedades comerciales más utilizadas en Honduras hasta 1996": Caturra, Pacas, Villa Sarchí, Catuaí, IHCAFE-90, Lempira, Parainema, Típica, Bourbon, Mundo Novo, Pacamara, Java.
- (a)–(f): none directly.

**002–014, 027 — World Coffee Research variety catalogue pages** (published 2023-04-06; Pacamara 2023-04-13). The "Coffee leaf rust" field gives:

| Variety | Rust (WCR) |
|---|---|
| Parainema | Highly resistant |
| Centroamericano | Highly resistant |
| Lempira | Intermediate resistance |
| Anacafé 14 | Intermediate resistance |
| Marsellesa | Intermediate resistance |
| Obatá Red | Intermediate resistance |
| IHCAFE 90, Caturra, Catuaí, Costa Rica 95, Pacas, Bourbon, Typica, Pacamara | Low resistance/susceptible |

- (a)
  - Parainema: "Pedigree selection of T5296, made by Instituto Hondureño del Café (IHCAFE); released in 2004."
  - Anacafé 14: "…released as a commercial variety in 2014" (by ANACAFÉ, Guatemala).
  - Obatá: "Released in Brazil in 2000, and brought to Costa Rica for commercial release in 2014 by the Costa Rican Coffee Institute (ICAFE)."
  - Centroamericano: "It was released in 2010 for farmers in Central America."
  - Lempira and IHCAFE 90: "A cross between Timor Hybrid 832/1 and Caturra. Pedigree selection made by … IHCAFE". No release year is given.
- There is no page for Ihcatú or Icatu (404).
- (b)(d)(e)(f) —

**015 — El Heraldo, 29 Feb 2024, "Honduras dispone de tres nuevas variedades de café".**
- (a)
  - "Autoridades del Instituto Hondureño del Café (Ihcafé) presentaron ayer estas variedades mejoradas, las que han sido denominadas Ihcatú 75, Anacafé 14 SHN al igual que Obatá SHN." That dates the Honduran release of all three to 28 Feb 2024.
  - "Luego de 20 años de la liberación de la variedad Parainema…"
  - "…capacidad de poder producir una semilla de las tres variedades para al menos 1,500 manzanas…"
- (c) "…se destaca que son más resistentes a la roya, con una alta tolerancia…"

**028 — La Prensa, 29 Sep 2023, "Ihcafé se prepara para liberar 4 variedades más resistentes a roya".**
- (a)
  - "La última vez que Ihcafé libero una variedad fue la Parainema, en el año 2004."
  - "…se preparan para liberar, el próximo año, al menos 4 variedades de café que son más resistentes a la roya."
- The article also says "250,000 plantas certificadas de café se producen al año" at the Corquín centre.

**041 — IHCAFE, Memoria Cosecha 2021-2022** (uploaded Nov 2024; 11 MB; letter-spaced text).
- (a)(b) A research-centre table lists the varieties planted at each centre: "Parainema, IHCAFE 90, Catuai 311 y 313, Obata, Ihcatu, Anacafe 14, Lempira" (Corquín), "Parainema y Anacafe 14", "Lempira, Catuai y Pacamara", and so on. It gives no shares.
- (d)
  - Fideicomiso cafetalero 2021-22: "LIQUIDADO L.1,356,087,446.10 · POR LIQUIDAR L.9,562,909.51 · CAPTACIÓN DE APORTACIONES L.1,365,650,355.61 · 93.3%".
  - Renovation with the municipality of Maraita: "50 Mz de café en beneficio de 75 productores con insumos por un valor de un millón de lempiras".
  - "…accesar a fondo capital semilla por un valor de 20.5 millones de lempiras, beneficiando a 379 productores."
- (f) The 2021-22 statistics page shows "$1,451" (export value, million US$) and "US$ 236.68" (average export price per 46 kg sack). These are export figures, not producer prices.
- It also has production by municipality for 2021/22, in qq.

**042 — IHCAFE, "Propuesta Memoria 2021-2022"** (a design draft of 041, 10.5 MB). It is almost entirely images, so almost no text came out.

### Statistics and prices

**040 — IHCAFE, Informe Estadístico 2020-2021** (uploaded Feb 2022).
- Background:
  - "…más de 120,000 familias productoras de café de las cuales el 95% son calificadas como pequeños productores (con producción menor a 50 quintales/oro)".
  - "…una producción superior a 7.9 millones de quintales, mostrando un incremento del 8% comparado a … 7.3 millones … 2019-2020."
- (f) Page 31, "Registro Mensual de Compras … Sacos de 46Kg y Valor en Lempiras". These are exporters' purchases from producers, with the average price in Lps per 46 kg sack.
  - Total 2019-20: 7,260,115.39 sacos, L16,530,898,205.15, **L2,276.95 per sack**.
  - Total 2020-21: 7,909,087.88 sacos, L21,853,402,608.89, **L2,763.07 per sack**.
  - Monthly averages run from L1,500.00 (Oct 2019) to L3,411.90 (Aug 2021).
- Pages 28–29: exports 1970/71–2020/21, giving sacks, US$ and Lps values, and the average export price per sack in Lps and US$. For example "1998/99 2,720,247 269,853,610 3,780,489,975 1389.76 99.20" and "2001/02 … 839.00 51.20".
- (a)–(e) —

**043–052 — IHCAFE, "Boletín Estadístico de Comercialización"**: 12 Aug 2021, 30 Sep 2021 (preliminary), 23 Nov, 29 Nov, 30 Nov and 1 Dec 2021, 9 Feb, 30 Jun and 30 Aug 2022, 7 Feb 2023.
- They cover exports by destination, contracts, average **export** price and the New York futures.
- Example (9 Feb 2022): "El precio promedio de exportación por saco de 46 kg a la fecha es de $222.47 comparado con … $138.67 [2020-2021] existe un incremento del 60%."
- None of them gives a producer price, cost, credit or variety figure.

**023 — BCH, "Precio Promedio Diario del Dólar", 2000–2026** (XLSX). Daily buying and selling rates, in Lempiras per US$. Useful for converting (d)–(f).

### Decrees (credit)

**016 — Decreto 93-2018, IHCAFE copy ("Préstamo L200").** This is a scanned PDF, so no text came out. Its content is summarised by 022, 033, 034 and 024.

**017 — FAOLEX hon94834 = Decreto 143-2008** (*La Gaceta*, 6 Dec 2008). This is not Decreto 152-2003 as the sources list expected, although it amends it.
- (d)
  - "…la Secretaría de Estado en el Despacho de Finanzas otorgó al … IHCAFE un Préstamo por SEISCIENTOS CINCUENTA Y TRES MILLONES DE LEMPIRAS (L653,000,000.00)" (under Decreto 124-2001).
  - From 1 Oct 2008, buyers "retendrán la cantidad de UN DÓLAR … (US$1.00) por cada quintal de café oro adquirido de los productores" to repay it.
  - It also adds Article 1-A, "Programa de Reactivación y Readecuación Financiera del pequeño, mediano y grande productor de café". The programme funds "1) La renovación y mantenimiento de fincas cafetaleras; 2) La diversificación de cultivos…" through bond issues "colocados en el Sistema Financiero Nacional para otorgar créditos a los productores".

**018 — FAOLEX hon123550, national phytosanitary emergency for rust** (Decreto Ejecutivo, 13 Feb 2013).
- (c) "…el IHCAFE ha realizado un estudio sobre el porcentaje de daño de la Roya … en el año 2012, encontrando que el 25% del total del parque cafetalero del país ha sido afectado".
- Background: 2011-12 exports were US$1,440 million and 7.2 million qq.

**019 — PCM-031-2021 (TSC).** "Bono Cafetalero para la Fertilización en Apoyo a Pequeños y Medianos Productores" for fiscal year 2021, paid through IICA and the "Fideicomiso del Fondo de Solidaridad…". The amounts are garbled in the two-column extraction; see the PDF.

**020 — PCM-048-2018 (TSC).** Concerns BANADESA's financial non-viability (BANHPROVI manages its assets and liabilities). It gives no coffee amounts.

**024 — FAOLEX hon185597.** Regulations ("Reglamento") for the financing under Decreto 93-2018. The extraction is garbled; see the PDF.

### Press: credit, costs and prices

**021 — El Heraldo, 10 Apr 2013, "Bancos prestarán L 900 millones a los caficultores".**
- (d)
  - "…línea de crédito por 900 millones de lempiras para financiar la lucha en contra de la roya … plazo de siete años, con tres de gracia y a una tasa de interés del 10%."
  - Loans are capped per purpose: "…renovación … hasta un máximo de 150,000 lempiras, o sea, unos 30,000 por manzana"; "hasta 20,000 lempiras por manzana para … la recepa"; "rehabilitación … hasta 75,000 lempiras, o sea, 15,000 por manzana".
  - "Ihcafé estimó … que se requerían unos 1,600 millones de lempiras".
  - The loans are guaranteed by the "retención de 9 dólares por quintal".
- (c) "La roya afectó un 25% de las 280,000 hectáreas cultivadas con café".

**022 — El Heraldo, 29 Aug 2018, "Aprueban dos formas de financiamiento para los caficultores".**
- (d)
  - "…préstamos de 200 lempiras por cada quintal de café oro producido, tomando como base … la cosecha 2016-2017."
  - "…financiamiento de hasta 1,900 millones de lempiras".
  - "…retendrán 1.50 dólares … por cada quintal oro adquirido de los productores".
  - "Fondo para el Sector Cafetero … 300 millones de lempiras" (from BANHPROVI).
  - "…un instrumento de casi 6,900 millones de lempiras".

**029 — El Heraldo, 20 Apr 2013.**
- (c) "…25% de las 400,000 manzanas cultivadas … están afectadas", which means about 100,000 Mz and a loss of 1.5 million qq and US$200 million.
- (d) "…más de 30,000 manzanas totales, para renovarlas se necesita una inversión mínima de 900 millones de lempiras … El resto de las 70,000 manzanas … necesitan 2,000 millones de lempiras".

**030 — El Heraldo, 7 Apr 2014.**
- (d) "Fuentes financieras destinaron alrededor de 1,715 millones de lempiras para enfrentar [la roya]".
- (f) The New York price is 112.55 US$/qq, against more than 140 earlier. Exports were 5.5 million qq in 2012-13 (5.7 million expected).

**031 — El Heraldo, 30 Dec 2014, "Caficultura movió préstamos por 59 millones de lempiras".**
- (d)
  - "…la banca colocó 59 millones de lempiras a unos 800 productores". The article covers two departments, which the extraction does not name.
  - BANADESA lent "28 millones de lempiras" to 360 producers hit by rust.
  - Small producers (1 Mz, under 30 qq) got "25 mil lempiras y con Ihcafé hasta 30 mil"; producers with 20 Mz got "hasta 200 mil lempiras".
  - "Las tasas de interés oscilaron en un 15 por ciento".

**032 — El Heraldo, 18 Feb 2023.**
- (d) Decreto 47-2018 lets BANADESA reschedule loans "con plazos de hasta 20 años con una tasa de interés del 2%".
  - More than 1,700 producers rescheduled their debts.
  - L29,387,592.76 was recovered in 90-day interest payments.
  - L2,131,052,606.30 was recovered in 2018–2022.

**033 — La Prensa, 4 Sep 2018, "Aprueban L6,700 millones en préstamos para caficultores".**
- (d) "L200 per quintal oro" (base: the 2016-17 harvest), IHCAFE financing "hasta 1,900 millones".
- A guarantee fund was set up with "300 millones de lempiras del Banhprovi, que habilitan L2,400 millones en garantías recíprocas … (4,800 millones de lempiras)". Confianza SA-FGR guarantees "hasta un 50% de estos créditos".

**034 — La Prensa, 26 Sep 2018.**
- (d) "IHCAFE podrá adicionar hasta 2.5% a la tasa de interés … por el crédito de 1,900 millones … si el préstamo se adquiere a 12%, el Ihcafé puede incrementar a 14.5%".
- The guarantee is "una retención de 1.50 dólares, equivalente a 36 lempiras, por quintal".

**035 — La Prensa, 7 Jul 2019, "Precios de café no cubren costo de producción".**
- (e) "Producir un quintal de café de 46 kilogramos le cuesta más de 2,000 lempiras al caficultor…"
- (f) "…pero solo recibe un poco más de L1,000 en el mercado interno, según cifras oficiales."
- The international price moved "de 90 a 110 dólares", and producers need "al menos un mercado internacional a $135".

**036 — La Prensa, 24 Feb 2026, "Baja el precio del café; sube el costo de producción".**
- (e) Harvest labour rose "Mientras el año pasado se pagaban alrededor de 60 lempiras por lata de café cortado, actualmente el costo ha subido hasta 100 lempiras."
- (f) "…en octubre de 2025 el quintal del aromático rondaba los 400 dólares, mientras que ayer se cotizaba en 278.05 dólares". Exports in 2024-25 were 6.2 million qq and more than US$2,000 million.

**037 — El Heraldo, 23 Sep 2022, "¿Cuánto reciben los productores y exportadores por quintal de café?"**
- (f)
  - "Las compras registradas a los productores de café alcanzan 5,980,908 sacos por un valor de 27,420.5 millones de lempiras. De acuerdo con el Ihcafé, cada cafetalero ha recibido, en promedio, 4,584.61 lempiras, que equivale a 187.85 dólares." (harvest 2021-22)
  - The exporter's average was US$236.93, or L5,777.57 per sack.

**038 — El Heraldo, 29 Nov 2017.**
- (e) Pickers are paid "40 lempiras por lata cortada", which means "entre 200 y 400 lempiras diarios". The article also says "el costo de producción es muy alto", without a figure.
- (f) Export price was "129 dólares por quintal … el promedio es alrededor de 121 dólares".

**039 — El Heraldo, 16 Nov 2024.**
- (f) The New York price was 281.80 US$/qq. The export target for 2024-25 is 7 million sacks.
