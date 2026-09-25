# Workstream D: domestic consumption in producing countries, 2005 to 2026

Data file: `data/raw/D_producer_consumption.csv` (121 rows, schema per `data/raw/SCHEMA.md`). Compiled 2026-09-24.

> **Status: partial.** The Brazil ABIC annual series is complete for 2005–2025 except 2016, which was not directly retrieved (see below). It comes with per-capita data, prices, the 2025 decline, the "−15.96%" clarification and 2026 year-to-date data. **No other country and no ICO exporting-vs-importing data could be collected.**
>
> **Why:** the WebSearch budget of 200 calls is shared by every workstream in the session. It ran out after about 34 Workstream D searches (message: "this session has used its web search budget (200 of 200)"). The egress proxy also blocks direct fetches (403 policy denial, confirmed in the proxy status). Section 6 has a ready-to-run search plan for when the budget is raised with `CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION`.

## 0. Method and reliability conventions

- Every value comes from a WebSearch result, and each CSV row carries the URL. The ABIC PDFs and news pages could not be opened, so the `quote` field holds the search engine's summary of the page text. It is marked "Quote = WebSearch summary" or "Quote = page title" in `notes`.
- Confidence:
  - `high`: an ABIC or Embrapa page or PDF was named in the result and the number is explicit.
  - `medium`: reputable press quoting ABIC (Agrolink, Safras, Agência Brasil, Forbes Brasil, Notícias Agrícolas and similar).
  - `low`: the result named no clear page, the number was inferred from context, or it conflicts with another source.
- Three rows (Jan–Apr 2026 = 4.9 mn bags, the Jul-2025 peak price of R$70.52/kg, and the "Southeast" label on the R$59.96 price) are **cross-referenced from sibling workstreams F and G** in this same session. They are flagged `CROSS-REF` in notes.
- Derived figures such as CAGRs are computed by D from retrieved values and labelled "computed". Missing years were **not** interpolated.

---

## 1. Brazil (ABIC)

### 1.1 Period convention (important)

- **ABIC's annual domestic-consumption figure uses a November-to-October 12-month period in every year from 2005 to 2025.** For example, "2025" means Nov-2024 to Oct-2025. Releases quoting "novembro … a outubro" were found for 2005, 2006, 2007, 2008, 2010, 2011, 2012, 2014, 2015, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024 and 2025. The Jan-2026 Agência Brasil report says: "coffee consumption fell 2.31% between November 2024 and October 2025". So the annual figure did **not** switch to calendar years.
- **The new ABIC retail panel is calendar-based**, with monthly and four-month ("quadrimestral") data from 2025. Examples are Jan–Apr 2026 and Jan–Aug 2026. It covers the **retail channel only, which ABIC puts at 73–78% of domestic consumption**. Do not mix retail YTD figures with the Nov–Oct total.
- **Methodology break in 2018.** From the 2018 release (Nov-2017 to Oct-2018), ABIC stopped including volumes previously attributed to unregistered companies such as farms, cafeterias and informal retailers. Under the old method 2018 "would have reached about 23 million bags"; the new method gives 21.0. The +4.80% growth for 2018 is on a comparable (restated) basis. 2017 per capita was restated to 5.81 kg green. Levels before and after 2018 are **not strictly comparable**: the old method is roughly 2 mn bags higher. Source: [Agrolink – Abic registra aumento de 4,8%…; revê metodologia](https://www.agrolink.com.br/noticias/abic-registra-aumento-de-4-8--no-consumo-de-cafe-no-brasil--reve-metodologia_415679.html).
- **Population rebasing in 2024.** The IBGE population revision cut 2024 per capita by 2.22% even though volume rose 1.11%.

### 1.2 ABIC annual series (million 60-kg bags, Nov–Oct)

| Year | Period | Mn bags | y/y % (ABIC) | kg green/cap | kg roasted/cap | Conf. | Source |
|---|---|---|---|---|---|---|---|
| 2003 (context) | Nov02–Oct03 | 13.7 | – | – | – | med | [Agrolink 2007](https://www.agrolink.com.br/noticias/consumo-de-cafe-supera-17-milhoes-de-sacas-em-2007_62199.html) |
| 2005 | Nov04–Oct05 | **15.53** | – | – | – | med | [Agrolink](https://www.agrolink.com.br/noticias/consumo-interno-de-cafe-chega-a-16-33-milhoes-de-sacas_50932.html) |
| 2006 | Nov05–Oct06 | **16.33** | +5.10 | – | – | med | same |
| 2007 | Nov06–Oct07 | **17.1** | +4.74 | – | – | med | [Agrolink](https://www.agrolink.com.br/noticias/consumo-de-cafe-supera-17-milhoes-de-sacas-em-2007_62199.html) |
| 2008 | Nov07–Oct08 | **17.66** | +3.2 | – | – | med | [Agrolink](https://www.agrolink.com.br/noticias/contra-crise--industria-de-cafe-encolhe_86565.html) |
| 2009 | Nov08–Oct09 | **18.39** | (computed +4.1)¹ | – | 4.65 | med | [Agrolink](https://www.agrolink.com.br/noticias/consumo-interno-de-cafe-cresce-em-2009_90021.html) |
| 2010 | Nov09–Oct10 | **19.13** | (computed +4.0) | – | 4.81 (record; 1965 = 4.72) | med | [Agrolink](https://www.agrolink.com.br/noticias/brasileiros-nunca-consumiram-tanto-cafe-como-em-2010_127528.html) |
| 2011 | Nov10–Oct11 | **19.72** | +3.11 | 6.10 | 4.88 | med | [Agrolink](https://www.agrolink.com.br/noticias/consumo-de-cafe-no-brasil-chega-a-19-72-mi-de-sacas-em-2011_143222.html) |
| 2012 | Nov11–Oct12 | **20.33** | ~+3 | 6.23 | 4.98 | med | [Agrolink](https://www.agrolink.com.br/noticias/consumo-de-cafe-no-brasil-crescera-ate-3--em-2013--preve-abic_165266.html) |
| 2013 | Nov12–Oct13 | **20.08** | −1.23 | 6.09 | 4.87 | med | [Agrolink](https://www.agrolink.com.br/noticias/consumo-de-cafe-no-brasil-cai-pela-1a-vez-em-10-anos--diz-abic_191811.html) |
| 2014 | Nov13–Oct14 | **20.333** | +1.24 | 6.12 | 4.89 | med | [Olhar Direto](https://www.olhardireto.com.br/agro-e-negocios/noticias/consumo-de-cafe-no-brasil-cresce-1-24-em-12-meses-diz-abic) |
| 2015 | Nov14–Oct15 | **20.508** | +0.86 | 6.12 | 4.90 | med | [Agrolink](https://www.agrolink.com.br/noticias/apesar-da-crise--consumo-de-cafe-no-brasil-em-2015-manteve-ligeiro-crescimento_345917.html) |
| 2016 | Nov15–Oct16 | **not retrieved**² | – | – | – | – | – |
| 2017 | Nov16–Oct17 | **21.99** (old method) | +3.6 (3.5 in some press) | 5.81 (restated, new method) | – | high | [ABIC Indicadores 2017](https://www.abic.com.br/estatisticas/indicadores-da-industria/indicadores-da-industria-de-cafe-2017/) |
| 2018 | Nov17–Oct18 | **21.0** (new method; ~23 old) | +4.80 (comparable) | 6.02 | – | high | [ABIC Indicadores 2018 PDF](https://www.abic.com.br/wp-content/uploads/2025/03/Indicadores-da-Industria-2018_-Site.pdf) |
| 2019 | Nov18–Oct19 | **20.9** | (fall)³ | – | – | low | [Hub do Café](https://hubdocafe.cooxupe.com.br/abic-divulga-dados-do-consumo-de-cafe-no-brasil/) |
| 2020 | Nov19–Oct20 | **21.2** | +1.34 | – | – | med | [Notícias Agrícolas](https://www.noticiasagricolas.com.br/noticias/cafe/282330-abic-divulga-dados-de-consumo-e-perfil-da-industria-do-cafe-no-brasil.html), [Conexão Safra](https://conexaosafra.com/cafeicultura/consumo-cafe-volta-crescer-no-brasil-durante-pandemia/) |
| 2021 | Nov20–Oct21 | **21.5** | +1.71 | – | – | high | [ABIC Indicadores 2021 PDF](https://www.abic.com.br/wp-content/uploads/2025/03/Indicadores-da-Industria-2021_-Site.pdf) |
| 2022 | Nov21–Oct22 | **21.3** | −1.01 | – | – | med | [Mercado&Consumo](https://mercadoeconsumo.com.br/03/03/2023/economia/abic-consumo-brasileiro-de-cafe-cai-1-em-2022-ante-2021/) |
| 2023 | Nov22–Oct23 | **21.67** | +1.64 | 6.4 (basis not stated) | – | high | [Agência Gov/Embrapa](https://agenciagov.ebc.com.br/noticias/202402/artigo-consumo-interno-dos-cafes-do-brasil-atinge-21-7-milhoes-de-sacas-no-periodo-acumulado-de-doze-meses) |
| 2024 | Nov23–Oct24 | **21.916** | +1.11 | 6.26 | 5.01 | high | [ABIC Indicadores 2024](https://estatisticas.abic.com.br/estatisticas/indicadores-da-industria/indicadores-da-industria-de-cafe-2024/), [StoneX](https://www.stonex.com/pt-br/insights/abic-em-2024,-o-consumo-de-cafe-no-brasil-aumentou-1,11pct,-totalizando-21,916-milhoes-de-sacas-1556454/) |
| 2025 | Nov24–Oct25 | **21.41** | **−2.31** (confirmed) | 6.02 | 4.82 (−3.88%) | high | [Safras](https://safras.com.br/consumo-total-de-cafe-no-brasil-cai-231-e-soma-214-milhoes-de-sacas-em-2025-aponta-abic/), [Agência Brasil](https://agenciabrasil.ebc.com.br/economia/noticia/2026-01/precos-altos-derrubam-consumo-de-cafe-no-brasil-em-2025), [ABIC 2025 PDF](https://www.abic.com.br/wp-content/uploads/2026/01/2026.02.Indicadores-da-Industria-2025_-Site.pdf) |
| 2026 YTD (retail) | Jan–Apr 2026 | 4.9 | +2.44 | – | – | med | [Forbes BR May-26](https://forbes.com.br/forbes-agro/2026/05/consumo-de-cafe-no-brasil-sobe-244-no-1o-quadrimestre-indica-abic/) (4.9 is a cross-ref from F) |
| 2026 YTD (retail) | Jan–Aug 2026 | **13.69** | **+2.29** (Jan–Aug 2025 was −5.4) | – | – | high | [Forbes BR Sep-26](https://forbes.com.br/forbes-agro/2026/09/consumo-de-cafe-no-brasil-avanca-229-no-ano-ate-agosto-diz-abic/), [Reuters/Investing](https://br.investing.com/news/commodities-news/consumo-de-cafe-no-varejo-do-brasil-avanca-229-no-ano-ate-agosto-diz-abic-2072166) |
| 2026 forecast | full year | – | **+2.5** (ABIC) | – | – | med | [AF News](https://afnews.com.br/consumo-de-cafe-deve-crescer-25-em-2026-preve-abic/) |

Footnotes:

1. One summary said "+4.5%" for 2009, but 18.39/17.66 = +4.13%. The ABIC growth rate is not recorded.
2. **2016 is not retrieved.** Two indirect ABIC statements point to about 21.2 mn. The 2020 release said 21.2 mn was "similar to what was recorded in 2016", and 21.99 for 2017 at +3.6% implies about 21.2. The CSV value is left blank under the no-interpolation rule.
3. The 2019 figure of 20.9 comes from a summary with weak page attribution. It is consistent with 2020 = 21.2 at +1.34%, which implies 20.92. Press said numbers "had fallen in 2018 and 2019" in levels, meaning 2017 at 22.0 (old method), then 21.0, then 20.9.

Other points:

- **Share of the Brazilian crop consumed at home** (ABIC, using Conab crops): 50.8% in 2007, 45.3% in 2021, 39.4% in 2023, 40.4% in 2024 and 37.9% in 2025 (crop 56.54 mn).
- **Composition in 2023:** roast and ground coffee was 20.62 mn bags (95.1%) and soluble 1.05 mn (4.9%).
- **Regions in 2023:**

  | Region | Mn bags | Share |
  |---|---|---|
  | Southeast | 9.0 | 41.8% |
  | Northeast | 5.82 | 26.9% |
  | South | 3.18 | |
  | North | 1.86 | |
  | Center-West | 1.73 | |

- **Brazil's place in the world:** 14% of world demand in 2007, per ABIC president Guivan Bueno. The gap to the US, the largest consumer, was about 4.5 mn bags in 2021 and about 5 mn in 2025.
- **Growth trend (computed from the table):**
  - 2005–2012 CAGR: +3.9%/yr.
  - 2005–2017 (old method): +2.9%/yr.
  - 2018–2025 (new method): +0.3%/yr.
  - The Brazilian demand-growth engine was essentially flat from about 2012, well before the 2024–25 price spike.
- **Record of ABIC forecasts** (ABIC forecasts tend to run high):

  | Year | Forecast | Actual |
  |---|---|---|
  | 2013 | up to +3% | −1.23% |
  | 2016 | 21 mn | – |
  | 2018 | 22.8 mn (old method) | 21.0 new method (about 23 old) |
  | 2019 | 21.7 mn | 20.9 |
  | 2021 | 23.3 mn | 21.5 |
  | 2026 | +2.5% | pending (would be about 21.95 mn, computed) |

### 1.3 Prices (ABIC retail survey and ABIC cost statements)

| Item | Period | Value | Source |
|---|---|---|---|
| Avg R&G retail price, Southeast, end of year | Dec-2025 | **R$59.96/kg** (+5.8% end-2024 to end-2025) | ABIC 2025 PDF via [Safras](https://safras.com.br/consumo-total-de-cafe-no-brasil-cai-231-e-soma-214-milhoes-de-sacas-em-2025-aponta-abic/) (Southeast label per F/G quote of the PDF) |
| Peak monthly avg, Southeast | Jul-2025 | **R$70.52/kg** | ABIC 2025 PDF (cross-ref F/G) |
| Traditional/extra-strong R&G | Aug-2026 vs prior-year base | **R$49.50/kg**, −21.22% (from R$62.83) | [Forbes BR](https://forbes.com.br/forbes-agro/2026/09/consumo-de-cafe-no-brasil-avanca-229-no-ano-ate-agosto-diz-abic/) |
| Soluble | Aug-2026 vs prior-year base | **R$203.64/kg**, −19.31% (from R$252.36) | same |
| Retail price increase over 5 years | 2021–2025 | +116% (vs green conilon +201%, arabica +212%) | [Agência Brasil](https://agenciabrasil.ebc.com.br/economia/noticia/2026-01/precos-altos-derrubam-consumo-de-cafe-no-brasil-em-2025) |
| Green cost / retail price change | 2021 | green +155%, retail +52% | [CNN Brasil](https://www.cnnbrasil.com.br/agro/preco-da-materia-prima-do-cafe-tem-alta-de-155-em-2021-diz-abic/) (title) |
| Industry revenue | 2025 | R$46.24 bn (+25.6%) | [Agência Brasil](https://agenciabrasil.ebc.com.br/economia/noticia/2026-01/precos-altos-derrubam-consumo-de-cafe-no-brasil-em-2025) |

Official CPI for context, from IBGE's IPCA sub-item "café moído" (collected by workstream F, see `F_marginal_buyers.csv`):

- Calendar 2024: +39.6% Dec/Dec.
- 12 months to Mar-2025: +77.8%.
- 12 months to May-2025: +82.2% (peak).
- Calendar 2025: +35.65% Dec/Dec (a conflicting 41.84% is flagged by F).
- 12 months to Apr-2026: −5.99%.
- 12 months to Jul-2026: **−17.2%**, the largest 12-month fall since the Plano Real.

**Gap:** ABIC's annual average R$/kg series for 2005–2024 was not retrieved. The source page is `abic.com.br/estatisticas/preco-no-varejo/`.

Note the pass-through pattern: retail prices rose far less than green costs (retail +116% vs green +201–212% over 5 years; retail +52% vs green +155% in 2021). Roasters absorbed margin and, per press, adjusted blends (not verified, see 1.6).

### 1.4 The 2025 decline and ABIC's explanation

- **Volume:** −2.31% to 21.41 mn bags (Nov-2024 to Oct-2025), confirmed by ABIC's PDF, Agência Brasil and Safras.
- **Per capita:** −3.88% to 6.02 kg green / 4.82 kg roasted. Part of the fall comes from IBGE population growth.
- **Why:** ABIC said the decline is "largely explained by increased prices". The retail R&G price rose 5.8% during 2025 and roughly doubled over two years. Over five years green coffee rose 201% (conilon) and 212% (arabica) against a 116% rise at retail.
- **Revenue:** despite lower volume, industry revenue rose 25.6% to R$46.24 bn.
- **Outlook (Jan 2026):** ABIC expected no significant price decrease in 2026, only more stability from a promising harvest. It said consumer prices would fall only after "two more harvests" because of low global stocks. See [Agência Brasil](https://agenciabrasil.ebc.com.br/economia/noticia/2026-01/precos-altos-derrubam-consumo-de-cafe-no-brasil-em-2025) and [Exame](https://exame.com/agro/cafe-deve-ter-precos-mais-estaveis-em-2026-diz-industria-brasileira/). In practice, prices fell faster in 2026 (see 1.5).
- **Mix:** specialty coffee is still under 1% of the market, while certified sustainable coffees grew 31%.
- **Unresolved headline:** [CNN Brasil](https://www.cnnbrasil.com.br/economia/cnn-money/consumo-de-cafe-no-brasil-cai-quase-3-em-2025-diz-industria/) wrote "cai quase 3%" (falls almost 3%), which conflicts with −2.31%. The basis is probably different, perhaps the retail panel or member firms.

### 1.5 What the "−15.96%" (Agência Brasil, May 2025) measured

It is **a single-month retail comparison: bags sold in April 2025 vs April 2024.** It comes from ABIC's new monthly retail panel, and retail is 73–78% of domestic consumption. It is **not** an annual or YTD figure. Source: [Agência Brasil 2025-05](https://agenciabrasil.ebc.com.br/economia/noticia/2025-05/consumo-de-cafe-cai-1596-diz-abic).

Monthly retail sales, 2025 vs 2024:

| Month | y/y |
|---|---|
| Jan | +1.26% |
| Feb | +0.89% |
| Mar | −4.87% |
| Apr | −15.96% |

Retail Jan–Aug 2025 ended at −5.4%, and the full Nov–Oct 2025 total at −2.31%. ABIC attributed the price rise to climate events, stronger world demand and China's entry into the market.

### 1.6 Blend changes (conilon share) and substitutes: **GAP**

Nothing was retrieved on:

- the conilon/robusta share in domestic roasters' blends over time (ABIC, Cecafé, Embrapa or Conab statements);
- lower-grade coffee ("cafés de menor qualidade");
- 2025 "bebida sabor café" (coffee-flavoured drink) products.

Workstream G (`G_switching.csv`) may hold related switching evidence. This was not checked in depth.

### 1.7 USDA PSD Brazil domestic consumption: **GAP**

Not retrieved. H_producers.csv has only USDA *production* data: Brazil 2026/27 at 71.9 mn bags, 2025/26 at 63.0 implied, robusta/conilon at 25.0 in 2025/26 and 24.4 in 2026/27.

### 1.8 Other Brazil history notes

- **2013:** the first fall since 2003. ABIC blamed new breakfast options such as juices, chocolate drinks and soy drinks.
- **2020:** +1.34% during the pandemic.
- **2022:** −1.01%, blamed on "accumulated inflation and the reduction in the population's purchasing power".
- **2024:** ABIC member firms grew +1.77% while non-member firms fell −0.66%.
- **Data-quality caveat:** an Agrolink headline "OIC questiona estatística brasileira" (c. 2007) shows the ICO questioned ABIC's numbers. This fits the 2018 downward methodology revision.

---

## 2. Other producing countries: **NOT COLLECTED (search budget exhausted)**

| Country | Target | Status | Production context available elsewhere |
|---|---|---|---|
| Indonesia | USDA GAIN Coffee Annual consumption, ICO, BPS/AEKI | not searched | H: 2026/27 production 11.38–11.4 mn (GAIN / WM&T) |
| Ethiopia | USDA GAIN (consumption about half of output) | not searched | H: 2026/27 production 12.1 mn |
| Philippines | USDA / PCA | not searched | – |
| Vietnam | USDA GAIN VM2026-0016 domestic consumption | not searched | H: 2026/27 production 32.5 mn |
| Mexico | USDA GAIN / AMECAFE | not searched | H: C. America + Mexico 17.7 mn |
| Colombia | FNC / USDA GAIN | not searched | H: 2026/27 13.4 mn (GAIN) |
| India | Coffee Board / USDA GAIN | not searched | – |
| Peru, Honduras, Uganda, Kenya | USDA / ICO | not searched | H: Uganda 7.1–7.2 mn, Honduras 6.0 mn |

## 3. ICO: exporting vs importing countries' consumption: **NOT COLLECTED**

## 4. Trading down during the 2024–25 spike and recovery in 2026

Evidence found for Brazil only.

**Cutting during the spike:**

- Retail volumes turned negative in Mar-2025 (−4.87%) and reached −15.96% in April 2025, when IPCA ground-coffee inflation was about +78–82% over 12 months.
- Jan–Aug 2025 retail was −5.4% and the full year −2.31%. This was the largest annual fall among the ABIC y/y rates retrieved for 2005–2025 (2016's rate was not retrieved); earlier falls were −1.23% in 2013 and −1.01% in 2022.
- Per capita fell −3.88%, and revenue rose 25.6%, which means value up and volume down.
- Headline: ["Alta de 80% no preço derruba consumo de café no Brasil" (Mercado&Consumo, 22 May 2025)](https://mercadoeconsumo.com.br/22/05/2025/economia/alta-de-80-no-preco-derruba-consumo-de-cafe-no-brasil/).
- Direct evidence of trading down (a switch to lower grades, conilon-heavy blends, or coffee-flavoured drinks) was **not retrieved** (gap 1.6).

**Recovery in 2026 as prices eased:**

- Jan–Apr 2026: +2.44%.
- Jan–Aug 2026: +2.29% to 13.69 mn bags.
- May–Aug 2026: +4.65%. The comparison basis is unclear: my arithmetic from the Jan–Apr and Jan–Aug data implies about +2.2% y/y, so treat 4.65% as low confidence.
- Retail prices: traditional R&G −21.2% y/y to R$49.50/kg in Aug-2026; IPCA −17.2% over the 12 months to Jul-2026.
- Headlines, from search-result titles:
  - ["Queda de preços estimula o consumo de café, diz Abic" (The AgriBiz)](https://www.theagribiz.com/cafe/queda-de-precos-estimula-o-consumo-de-cafe-diz-abic)
  - ["Preço do café cai, consumo aumenta: brasileiros voltam a encher a xícara em 2026" (Seu Dinheiro)](https://www.seudinheiro.com/2026/economia/preco-cafe-cai-consumo-aumenta-brasileiros-voltam-encher-xicara-rsgp/)
  - ["Café fica mais barato nos mercados e consumo volta a crescer no Brasil; setor prevê safra histórica" (BNews RN)](https://www.bnewsrn.com.br/noticias/negocios/cafe-fica-mais-barato-nos-mercados-e-consumo-volta-a-crescer-no-brasil-setor-preve-safra-historica.html)
  - ["Consumo de café volta a crescer no Brasil após queda nos preços" (agro2)](https://agro2.com.br/agronegocio/consumo-de-cafe-volta-a-crescer-no-brasil/)

**Other countries** (Colombia, Vietnam, Indonesia, Ethiopia, India): not searched.

## 5. Discarded or conflicting data (not used)

- **Year-misaligned summaries of the ABIC "Indicadores" page.**
  - Two summaries labelled 6.4, 8.2, 10.1, 13.2, 13.6, 14.0, 13.7 and 14.9 as 2005–2012. These contradict contemporaneous ABIC releases (for example 2005 = 15.53 and 2012 = 20.33), and "13.7" matches the ABIC-quoted 2003 level. The summarizer evidently shifted years on a table that starts in the 1980s–2000s. Discarded.
  - Similarly, "2015: 20.1 … 2019: 22.0" is shifted about two years (it matches 2013 = 20.08, 2014 = 20.33, 2015 = 20.51, [2016 ≈ 21.2], 2017 = 21.99). Discarded, though it corroborates about 21.2 for 2016.
- **Cecafé summary** ("2015: 20.3, 2016: 20.5"): off by one year against ABIC (2014 = 20.33, 2015 = 20.51). Discarded.
- **ABIC interim (May–Apr) surveys**, headlines "Consumo de café no Brasil já é de 16,9 milhões de sacas" and "Consumo anual … atinge 17,45 mi sacas" (2008 interim survey): the periods were not confirmed, so these are not in the CSV.
- **2017 Embrapa/"Tendências 2017" estimate of 21.5 mn vs ABIC final 21.99:** both are in the CSV under different dataset names.
- **2017 growth:** 3.6% (ABIC page summary) vs 3.5% (Agrolink headline). **2018 forecast:** 22.7 vs 22.8.

## 6. Search plan for the gaps (run when the budget is raised)

Use `allowed_domains` as indicated and run the searches in parallel batches.

1. **Brazil 2016:** `"consumo de café" 2016 Abic "milhões de sacas" "novembro de 2015" outubro 2016` (agrolink.com.br, noticiasagricolas.com.br).
2. **Brazil USDA:** `Brazil Coffee Annual domestic consumption million bags 2025/26` (fas.usda.gov, apps.fas.usda.gov). Also `Brazil Coffee Semi-annual domestic consumption forecast` for 2015, 2020 and 2023.
3. **Brazil blends:** `ABIC blend conilon participação indústria torrefação percentual 2025`, `Cecafé conilon consumo interno indústria percentual`, `"bebida sabor café" 2025 Anvisa MAPA ABIC`, `"pó para preparo de bebida sabor café" supermercado`.
4. **Brazil ABIC prices by year:** `ABIC preço médio varejo café torrado e moído R$/kg 2020 2021 2022 2023 2024` (abic.com.br).
5. **Indonesia:** `Indonesia Coffee Annual domestic consumption million bags` (fas.usda.gov); `konsumsi kopi domestik Indonesia juta karung AEKI 2024`; `ICO Indonesia domestic consumption`.
6. **Ethiopia:** `Ethiopia Coffee Annual domestic consumption half of production million bags` (fas.usda.gov).
7. **Vietnam:** `Vietnam Coffee Annual domestic consumption million bags 2025/26` (fas.usda.gov); `tiêu thụ cà phê nội địa triệu bao 2025`.
8. **Philippines, Mexico, India:** `<country> Coffee Annual consumption million bags` (fas.usda.gov); `Coffee Board of India domestic consumption tonnes 2024`.
9. **Colombia:** `consumo interno de café Colombia millones de sacos FNC 2025`, `consumo per cápita café Colombia tazas FNC`.
10. **ICO exporting vs importing:** `ICO "exporting countries" domestic consumption coffee year 2023/24 million bags share` (ico.org, icocoffee.org); `ICO coffee market report consumption exporting countries 2005/06`.
11. **Trading down elsewhere:** `Colombia consumo café cae precios 2025`, `Vietnam coffee shop prices 2025 consumption slows`, `India coffee consumption price hike 2025 chicory`.
