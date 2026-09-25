# FETCH_LOG — ihcafe_docs

Run: 2026-09-25 (UTC), curl with a browser User-Agent, `-L`, 60 s timeout, max 2 tries per URL.

**Result: 0 files downloaded.** Every host on the list was refused by this session's egress proxy (`CONNECT tunnel failed, response 403`: the environment's network policy denied the host). Per the instructions, each blocked host was logged once and its remaining URLs were skipped without retrying.
The package registries (PyPI `files.pythonhosted.org` and `registry.npmjs.org`) were also refused with 403, so no PDF/XLSX text-extraction library could be installed. Only LibreOffice was available.

## Blocked hosts

| Host | Proxy response |
|---|---|
| `www.ihcafe.hn` | curl: (56) CONNECT tunnel failed, response 403 |
| `ihcafe.hn` | curl: (56) CONNECT tunnel failed, response 403 |
| `faolex.fao.org` | curl: (56) CONNECT tunnel failed, response 403 |
| `wikicafe.promecafe.net` | curl: (56) CONNECT tunnel failed, response 403 |
| `promecafe.net` | curl: (56) CONNECT tunnel failed, response 403 |
| `varieties.worldcoffeeresearch.org` | curl: (56) CONNECT tunnel failed, response 403 |
| `www.elheraldo.hn` | curl: (56) CONNECT tunnel failed, response 403 |
| `www.laprensa.hn` | curl: (56) CONNECT tunnel failed, response 403 |
| `a1.latribuna.hn` | curl: (56) CONNECT tunnel failed, response 403 |
| `banadesa.hn` | curl: (56) CONNECT tunnel failed, response 403 |
| `archivos.latribuna.hn` | curl: (56) CONNECT tunnel failed, response 403 |
| `revistahibueras.hn` | curl: (56) CONNECT tunnel failed, response 403 |
| `perfectdailygrind.com` | curl: (56) CONNECT tunnel failed, response 403 |
| `www.ico.org` | curl: (56) CONNECT tunnel failed, response 403 |

## Per-URL log

| # | URL | HTTP status / result | Final URL | File | Size (bytes) |
|---|---|---|---|---|---|
| 1 | <https://www.ihcafe.hn/wp-content/uploads/2021/06/Decreto-93-2018_Prestamo-L200_Leyes-IHCAFE-1.pdf> | curl 56: CONNECT tunnel failed, response 403 | same | - | - |
| 2 | <https://www.ihcafe.hn/?mdocs-file=4333> | skipped: host already blocked | - | - | - |
| 3 | <https://www.ihcafe.hn/?mdocs-file=4163> | skipped: host already blocked | - | - | - |
| 4 | <https://ihcafe.hn/?mdocs-file=4337> | curl 56: CONNECT tunnel failed, response 403 | same | - | - |
| 5 | <https://ihcafe.hn/?mdocs-file=4413> | skipped: host already blocked | - | - | - |
| 6 | <https://www.ihcafe.hn/?mdocs-file=4331> | skipped: host already blocked | - | - | - |
| 7 | <https://www.ihcafe.hn/?mdocs-file=4173> | skipped: host already blocked | - | - | - |
| 8 | <https://www.ihcafe.hn/?mdocs-file=4347> | skipped: host already blocked | - | - | - |
| 9 | <https://www.ihcafe.hn/?mdocs-file=4219> | skipped: host already blocked | - | - | - |
| 10 | <https://ihcafe.hn/?mdocs-file=4268> | skipped: host already blocked | - | - | - |
| 11 | <https://ihcafe.hn/?mdocs-file=5603> | skipped: host already blocked | - | - | - |
| 12 | <https://www.ihcafe.hn/?mdocs-file=6940> | skipped: host already blocked | - | - | - |
| 13 | <https://www.ihcafe.hn/?mdocs-posts=informe-estadistico-anual-14-15&mdocs-cat=> | skipped: host already blocked | - | - | - |
| 14 | <https://ihcafe.hn/publicaciones/> | skipped: host already blocked | - | - | - |
| 15 | <https://ihcafe.hn/investigacion-y-desarrollo/> | skipped: host already blocked | - | - | - |
| 16 | <https://ihcafe.hn/preguntas-frecuentes/> | skipped: host already blocked | - | - | - |
| 17 | <https://faolex.fao.org/docs/pdf/hon185597.pdf> | curl 56: CONNECT tunnel failed, response 403 | same | - | - |
| 18 | <https://wikicafe.promecafe.net/index.php/DURABILIDAD_DE_LA_RESISTENCIA_GEN%C3%89TICA_A_LA_ROYA_DEL_CAF%C3%89_(HEMILEIA_VASTATRIX)_EN_VARIEDADES_MEJORADAS_EN_HONDURAS_AL_2019> | curl 56: CONNECT tunnel failed, response 403 | same | - | - |
| 19 | <https://promecafe.net/wp-content/uploads/2019/XXIV_Simposio_Multimedia/Panel_V/7._Durabilidad_de_la_resistencia_a_la_roya_del_cafe%CC%81__en_Honduras_24_Simposio__Caficultura__04_09_2019-convertido.pdf> | curl 56: CONNECT tunnel failed, response 403 | same | - | - |
| 20 | <https://promecafe.net/wp-content/uploads/2019/XXIV_Simposio_Multimedia/Panel_II/1._DETERMINACIO%CC%81N_DEL_MEJOR_ARREGLO_ESPACIAL_PARA_VARIEDADES_DE_Coffea_ara%CC%81bica,_L_PROMISORIAS_LIBERADAS_POR_IHCAFE._HONDURAS._Jose_Arnold_Pineda-convertido.pdf> | skipped: host already blocked | - | - | - |
| 21 | <https://varieties.worldcoffeeresearch.org/varieties/ihcafe-90> | curl 56: CONNECT tunnel failed, response 403 | same | - | - |
| 22 | <https://varieties.worldcoffeeresearch.org/varieties/lempira> | skipped: host already blocked | - | - | - |
| 23 | <https://varieties.worldcoffeeresearch.org/varieties/parainema> | skipped: host already blocked | - | - | - |
| 24 | <https://varieties.worldcoffeeresearch.org/varieties/obata-red> | skipped: host already blocked | - | - | - |
| 25 | <https://varieties.worldcoffeeresearch.org/varieties/catuai> | skipped: host already blocked | - | - | - |
| 26 | <https://varieties.worldcoffeeresearch.org/varieties/caturra> | skipped: host already blocked | - | - | - |
| 27 | <https://varieties.worldcoffeeresearch.org/varieties/pacas> | skipped: host already blocked | - | - | - |
| 28 | <https://varieties.worldcoffeeresearch.org/varieties/ihcatu> | skipped: host already blocked | - | - | - |
| 29 | <https://varieties.worldcoffeeresearch.org/varieties/anacafe-14> | skipped: host already blocked | - | - | - |
| 30 | <https://www.elheraldo.hn/economia/honduras-dispone-de-tres-nuevas-variedades-de-cafe-IK17849302> | curl 56: CONNECT tunnel failed, response 403 | same | - | - |
| 31 | <https://www.laprensa.hn/honduras/honduras-ihcafe-prepara-liberar-4-variedades-resistentes-roya-KC15606396> | curl 56: CONNECT tunnel failed, response 403 | same | - | - |
| 32 | <https://a1.latribuna.hn/2013/04/09/reactivaran-sector-cafetalero-hondureno/> | curl 56: CONNECT tunnel failed, response 403 | same | - | - |
| 33 | <https://www.elheraldo.hn/economia/caficultura-tardara-tres-anos-para-recuperarse-de-estragos-de-la-roya-FKEH610243> | skipped: host already blocked | - | - | - |
| 34 | <https://www.elheraldo.hn/honduras/precios-bajos-y-ataque-de-la-roya-dejaran-perdidas-por-700-millones-GOEH566347> | skipped: host already blocked | - | - | - |
| 35 | <https://www.elheraldo.hn/honduras/caficultura-movio-prestamos-por-59-millones-de-lempiras-DCEH781103> | skipped: host already blocked | - | - | - |
| 36 | <https://www.elheraldo.hn/honduras/mas-de-1700-productores-llegaron-a-readecuar-deudas-con-banadesa-NA12219554> | skipped: host already blocked | - | - | - |
| 37 | <https://banadesa.hn/noticias-recientes/caf-realiza-primer-desembolso-a-banadesa-por-mas-de-12-9-millones-de-lempiras-para-el-financiamiento-al-sub-sector-cafe/> | curl 56: CONNECT tunnel failed, response 403 | same | - | - |
| 38 | <https://www.laprensa.hn/economia/habilitados-fondos-ayuda-productores-hondurenos-cafe-OXLP1213148> | skipped: host already blocked | - | - | - |
| 39 | <https://www.elheraldo.hn/honduras/aprueban-dos-formas-de-financiamiento-para-los-caficultores-FWEH1211602> | skipped: host already blocked | - | - | - |
| 40 | <https://www.laprensa.hn/economia/ihcafe-interes-a-prestamos-sistema-financiero-cafe-CWLP1220002> | skipped: host already blocked | - | - | - |
| 41 | <https://www.laprensa.hn/economia/precios-cafe-cubren-costo-produccion-caficultores-hondurenos-AGLP1299801> | skipped: host already blocked | - | - | - |
| 42 | <https://www.laprensa.hn/economia/cafe-precios-crisis-economia-honduras-EL29448185> | skipped: host already blocked | - | - | - |
| 43 | <https://www.elheraldo.hn/economia/ganancias-productores-exportadores-cafe-honduras-BI10186722> | skipped: host already blocked | - | - | - |
| 44 | <https://www.elheraldo.hn/economia/el-ihcafe-revela-que-los-corteros-ganan-entre-200-y-400-lempiras-LXEH1130856> | skipped: host already blocked | - | - | - |
| 45 | <https://www.elheraldo.hn/economia/aumento-precio-internacional-cafe-2024-DH22704025> | skipped: host already blocked | - | - | - |
| 46 | <https://archivos.latribuna.hn/2017/11/04/los-precios-del-cafe/> | curl 56: CONNECT tunnel failed, response 403 | same | - | - |
| 47 | <https://revistahibueras.hn/2026/01/22/cosecha-cafe-honduras-2025/> | curl 56: CONNECT tunnel failed, response 403 | same | - | - |
| 48 | <https://perfectdailygrind.com/es/2020/03/18/explorando-las-variedades-comunes-de-cafe-de-honduras/> | curl 56: CONNECT tunnel failed, response 403 | same | - | - |
| 49 | <https://www.ico.org/historical/1990%20onwards/Excel/2a%20-%20Prices%20paid%20to%20growers.xlsx> | curl 56: CONNECT tunnel failed, response 403 | same | - | - |

## Not attempted

- Download link inside `?mdocs-posts=informe-estadistico-anual-14-15` and the Informe Estadístico / Memoria de cosecha / Anuario PDFs linked from `ihcafe.hn/publicaciones/`: parent pages unreachable (host blocked).
- ICO fallback page `https://www.ico.org/new_historical.asp`: same host (`www.ico.org`) already blocked.

## To unblock

Add these domains to the allowed domains in the cloud environment's **Network access** setting (or pick a broader access level), then run the fetch again: `ihcafe.hn`, `www.ihcafe.hn`, `faolex.fao.org`, `promecafe.net`, `wikicafe.promecafe.net`, `varieties.worldcoffeeresearch.org`, `www.elheraldo.hn`, `www.laprensa.hn`, `a1.latribuna.hn`, `archivos.latribuna.hn`, `banadesa.hn`, `revistahibueras.hn`, `perfectdailygrind.com`, `www.ico.org`. Also allow `pypi.org`/`files.pythonhosted.org` so `pypdf`/`openpyxl` can be installed for text extraction.
