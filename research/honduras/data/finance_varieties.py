"""Honduras coffee after the 2012-13 rust: varieties, rust surveys, financing programmes, costs and farm-gate prices.

Every item carries its source and a status:
  'USDA'  = read in a USDA FAS attaché report saved in research/honduras/raw/usda_gain/ (quote kept below)
  'FAO'   = read in the FAOSTAT bulk file saved in research/honduras/raw/faostat/
  'DOC'   = read in a downloaded document (IHCAFE study, World Coffee Research, press article, decree) in research/honduras/raw/ihcafe_docs2/
  'PRESS' = seen only in a web-search summary; the page could not be opened (network policy), NOT verified
Amounts in lempiras are converted with the FAOSTAT annual average exchange rate (honduras_exchange.csv, IMF-based)."""
import csv, os
HERE = os.path.dirname(os.path.abspath(__file__)) + '/'
RAW = HERE + '../raw/'

GAIN = {  # short name -> original file name of the USDA report
    'GAIN 2011': 'Coffee Annual_Tegucigalpa_Honduras_4-18-2011', 'GAIN 2012': 'Coffee Annual_Tegucigalpa_Honduras_5-9-2012',
    'GAIN 2013': 'Coffee Annual_Tegucigalpa_Honduras_6-20-2013', 'GAIN 2014': 'Coffee Annual_Tegucigalpa_Honduras_5-28-2014',
    'GAIN 2015': 'Coffee Annual_Tegucigalpa_Honduras_4-20-2015', 'GAIN 2016': 'Coffee Annual_Tegucigalpa_Honduras_4-26-2016',
    'GAIN 2017': 'Coffee Annual_Tegucigalpa_Honduras_5-24-2017', 'GAIN 2018': 'Coffee Annual_Tegucigalpa_Honduras_5-22-2018',
    'GAIN 2020': 'Coffee Annual_Tegucigalpa_Honduras_05-15-2020', 'GAIN 2021': 'Coffee Annual_Tegucigalpa_Honduras_05-15-2021',
    'GAIN 2022': 'Coffee Annual_Tegucigalpa_Honduras_HO2022-0005', 'GAIN 2023': 'Coffee Annual_Tegucigalpa_Honduras_HO2023-0003',
    'GAIN 2024': 'Coffee Annual_Tegucigalpa_Honduras_HO2024-0002', 'GAIN 2025': 'Coffee Annual_Tegucigalpa_Honduras_HO2025-0002',
    'GAIN 2026': 'Coffee Annual_Tegucigalpa_Honduras_HO2026-0002'}


def fx():
    """Lempiras per US$, annual average (FAOSTAT exchange-rate domain)."""
    out = {}
    for r in csv.DictReader(open(RAW + 'faostat/honduras_exchange.csv', encoding='utf-8-sig')):
        if r['Months'] == 'Annual value' and r['Element'] == 'Local currency units per USD':
            out[int(r['Year'])] = float(r['Value'])
    return out


def farmgate():
    """FAOSTAT producer price of green coffee, official figures only (flag A)."""
    rows = {}
    for r in csv.DictReader(open(RAW + 'faostat/honduras_prices.csv', encoding='utf-8-sig')):
        if r['Item'] == 'Coffee, green' and r['Flag'] == 'A' and r['Element'] in ('Producer Price (LCU/tonne)', 'Producer Price (USD/tonne)'):
            rows.setdefault(int(r['Year']), {})[r['Element'][16:19]] = float(r['Value'])
    return rows


# ---------------------------------------------------------------- varieties (rust-resistant releases by IHCAFE)
VARIETIES = [
    dict(name='IHCAFE 90', family='Catimor (Timor Hybrid 832/1 × Caturra)', released='1990', year=1990, year_status='DOC',
         resistance='Resistant 1990–2015; from 2016 about 20 % of plants susceptible to the new rust races (IHCAFE, 2019); 80 % resistance to the new strain (IHCAFE via La Prensa, 24 Aug 2017). USDA 2018: still resistant. World Coffee Research: "recently confirmed susceptible in Honduras"',
         broke=None, partial=2016,
         src='Morales & Grajeda (IHCAFE), PROMECAFE 24th symposium 2019, table "Durabilidad de resistencia"; GAIN 2018; WCR variety page',
         note='Effective resistance 25 years (IHCAFE).', status='DOC'),
    dict(name='Lempira', family='Catimor (Timor Hybrid 832/1 × Caturra)', released='1998', year=1998, year_status='DOC',
         resistance='Resistant 1998–2001; tolerant 2002–2015 (rust already on 100 % of plants, low severity, in seed plots in July 2007); susceptible in 2016 (Olancho, full defoliation), spread over the whole country 2017–2019. USDA: IHCAFE confirmed the loss in April 2017',
         broke=2016, weakening=2002,
         src='Morales & Grajeda (IHCAFE), PROMECAFE 2019; GAIN 2017; WCR variety page',
         note='Effective resistance 17 years (IHCAFE).', status='DOC'),
    dict(name='Parainema', family='Sarchimor, selection of T5296', released='2004', year=2004, year_status='DOC',
         resistance='Resistant 2004–2019 in IHCAFE tests (fully resistant to the new races); USDA 2018, 2020, 2021: still resistant. Nothing later found',
         broke=None, last_confirmed=2021, src='Morales & Grajeda (IHCAFE), PROMECAFE 2019; WCR ("released in 2004"); GAIN 2018, 2020, 2021, 2025',
         note='', status='DOC'),
    dict(name='Ihcatú 75, Anacafé 14 SHN, Obatá SHN', family='bred abroad (Brazil: Icatu, Obatá by IAC; Guatemala: Anacafé 14), released by IHCAFE',
         released='Feb 2024', year=2024, year_status='DOC',
         resistance='Presented as more rust resistant and productive; seed for at least 1 500 manzanas in 2024. Caution: IHCAFE\'s 2019 study listed the Icatu 75 line as susceptible since 2016 and Obatá as 20 % susceptible',
         broke=None, src='El Heraldo, 29 Feb 2024 (read); La Prensa, 29 Sep 2023 (read: "at least 4" to be released in 2024; last release Parainema 2004); PROMECAFE 2019',
         note='First releases 20 years after Parainema.', status='DOC'),
]

# ---------------------------------------------------------------- how much is planted with resistant varieties
ADOPTION = [
    dict(when='Jun 2013', scope='national, % of coffee AREA', resistant=50, status='USDA', src='GAIN 2013',
         quote='IHCAFE reports that 50 percent of the total area of coffee production is planted with rust susceptible varieties.'),
    dict(when='since 2012', scope='cultivated area, dominated by Lempira', resistant=65, status='DOC', src='Morales & Grajeda (IHCAFE), PROMECAFE 2019 (read)',
         quote='Estos materiales resistentes reemplazaron los susceptibles y constituyen el 65% del área cultivada desde 2012 dominada por Lempira.'),
    dict(when='Apr 2014', scope='national, % of PRODUCERS', resistant=60, status='USDA', src='GAIN 2014',
         quote='the number of coffee producers, growing coffee rust resistant varieties, is moving up to 60 percent and 40 percent of them are still using non-resistant types.'),
    dict(when='2014', scope='5 departments (60 % of area), % of FARMS', resistant=62, status='USDA', src='GAIN 2014 (USDA/TechnoServe baseline)',
         quote='62 percent of the coffee farms had resistant varieties to coffee leaf rust and 38 percent had varieties susceptible'),
    dict(when='24 Aug 2017', scope='national coffee park (plants)', resistant=60, status='DOC', src='La Prensa, 24 Aug 2017 (read, ihcafe_docs3)',
         quote='En la actualidad, el 60% del parque cafetalero nacional está conformado por plantas mejoradas y resistentes a la roya y otras enfermedades.'),
    dict(when='Oct 2017', scope='farms sampled by the rust early-warning system', resistant=round(100 - 56.08 / 67.74 * 100, 1), lempira=56.08,
         lempira_of_susceptible=67.74, status='PRESS',
         src='IHCAFE SAT bulletin No 8 (search snippet)', quote='Lempira = 56.08 % of sampled farms, 67.74 % of farms classed as susceptible'),
    dict(when='~2020', scope='national, % of cultivation', resistant=60, status='PRESS', src='Perfect Daily Grind, Mar 2020 (search extract)',
         quote='about 60 % of Honduran coffee is planted with resistant varieties (Lempira, IHCAFE 90, Parainema)'),
]
# Resistance of the three IHCAFE varieties to the new rust strain (IHCAFE via La Prensa, Aug 2017; search extract)
NEW_STRAIN_RESISTANCE = dict(when='24 Aug 2017', status='DOC', src='La Prensa, 24 Aug 2017 (read, ihcafe_docs3)',
                             values={'Lempira': 0, 'IHCAFE 90': 80, 'Parainema': 100},
                             quote='se descubrió que la Lempira no es inmune a la nueva roya ... mientras que el Ihcafé-90 tiene un 80% de resistencia a la nueva cepa y el Parainema, un 100%.')
RENOVATION_VARIETIES = dict(when='2024-2026', status='PRESS', src='La Prensa / El Heraldo, IHCAFE seed programme (search extract)',
                            varieties=['Parainema', 'Obatá SHN', 'Ihcatú 75', 'IHCAFE 90', 'Anacafé 14 SHN'],
                            quote='varieties distributed for renovation: Parainema, Obatá, IHCATU 75, IHCAFE 90 and Anacafé 14')

# ---------------------------------------------------------------- rust surveys
RUST = [
    dict(when='2012/13', value=25, unit='% of coffee area affected', status='USDA', src='GAIN 2014',
         quote='affected by the coffee leaf rust in about 25 percent of the cultivated coffee acreage (71,000 hectares) in MY 2012/2013'),
    dict(when='2012/13', value=None, unit='damage', status='USDA', src='GAIN 2015',
         quote='About 22,000 hectares (10,000 families) had a total loss of their farms; 58,000 ha. (20,000 families) saw a decrease of their coffee production by 50 percent.'),
    dict(when='Apr 2014', value=12, unit='national average incidence, %', status='USDA', src='GAIN 2014',
         quote='a low national average incidence of coffee rust with 12 percent and an average of severely affected coffee farms of one percent'),
    dict(when='Apr 2017', value=3, unit='% of Lempira plants with rust', status='USDA', src='GAIN 2017',
         quote='As of April 2017, rust was present on three percent of Lempira variety plants.'),
    dict(when='Apr 2018', value=None, unit='new strains', n=4, status='USDA', src='GAIN 2018',
         quote='in April 2018, studies done by IHCAFE identified four new coffee rust strains'),
    dict(when='Apr 2019', value=None, unit='new strains', n=16, status='USDA', src='GAIN 2020',
         quote='In April 2019, studies done by IHCAFE identified 16 new coffee rust strains.'),
    dict(when='end 2020', value=20, lo=15, hi=25, unit='incidence in 5 departments after hurricanes Eta and Iota, %', status='USDA', src='GAIN 2021',
         quote='favored a 15 - 25% incidence of leaf rust in five departments of Honduras by the end of 2020'),
    dict(when='Apr 2022', value=5.42, unit='national average incidence, %', status='USDA', src='GAIN 2022',
         quote='an average coffee rust incidence of 5.42% ... 66% of them showed a low-level presence of coffee rust, 29% a medium presence and 5% with a high presence'),
    dict(when='May 2023', value=5.8, unit='national average incidence, %', status='USDA', src='GAIN 2023',
         quote='an average coffee rust incidence of 5.8%'),
    dict(when='2024/25', value=2.9, unit='national average incidence (forecast Jul 2024–Aug 2025), %', status='USDA', src='GAIN 2025',
         quote='national incidence levels forecast to remain low through August 2025, averaging 2.9 percent'),
    dict(when='Mar 2026', value=8.44, unit='national average incidence, %', status='USDA', src='GAIN 2026',
         quote='As of March 2026, national average incidence increased from 7.57 percent to 8.44 percent'),
]
RUST_RULE = ('IHCAFE rule of thumb: rust damage of 15 % means about 20 % less production (GAIN 2017: '
             '"if the damage from rust reaches 15 percent, there could be a 20 percent reduction in production").')

# ---------------------------------------------------------------- financing
# usd_m: US$ million as stated, or lempiras / FAOSTAT rate of that year (conv=True)
FINANCE = [
    dict(lab='2002 · crisis loan', year=2002, name='Government loan to all growers (coffee crisis)', usd_m=20, conv=False, who='all producers', terms='20 years',
         status='USDA', src='GAIN 2011', quote='the GOH obtained a loan for US$20 million to be paid over 20 years. Through the loan, funds supported all coffee producers in 2002.'),
    dict(year=2004, name='Coffee trust fund (Law of Financial Reactivation, 2003)', usd_m=None, conv=False,
         who='87,000 producers take part (2011)', terms='US$13.25/qq deducted at sale: US$9 trust fund (returned if no debt), US$1 for 1999–2001 loans, US$3.25 (US$0.50 to the 2002 loan; rest 36 % IHCAFE, 64 % National Coffee Fund)',
         status='USDA', src='GAIN 2011, GAIN 2015', quote='deduction of US$ 13.25 per quintal ... distributed in blocks of US$ 9.00, US $ 1.00 and US$ 3.25'),
    dict(lab='2013 · rust credit*', year=2013, name='Rust credit made available (banks, BCH, BANHPROVI, BANADESA, IHCAFE)', lps_m=1715, conv=True,
         who='L335 M actually used by April 2014; BANADESA loans up to L25,000, banks up to L150,000',
         terms='10 % interest, 7 years; to be repaid by 2019 (USDA)', status='DOC', src='El Heraldo, 7 Apr 2014 (read); GAIN 2017 for the 2019 repayment date',
         quote='se ha puesto a disposición de los caficultores alrededor de 1,715 millones de lempiras ... Del total de estos recursos se han utilizado unos 335 millones de lempiras'),
    dict(lab='2015 · fertiliser line', year=2015, name='IHCAFE fertiliser credit line', lps_m=370, usd_m=17, conv=False, who='coffee producers', terms='fertiliser at cost, 1 year, interest-free',
         status='USDA', src='GAIN 2015', quote='IHCAFE maintains a credit line for 370 million Lempiras (about US$ 17 million) to buy fertilizer'),
    dict(year=2015, name='PAPP (IHCAFE + National Coffee Fund) and PEPP (BANADESA)', usd_m=None, conv=False, who='about 23,000 small producers',
         terms='replant 1 manzana (0.7 ha), no interest; aim 5 → 45 qq per manzana', status='USDA', src='GAIN 2015–2017',
         quote='This program supports about 23,000 small producers ... The program aims to increase production from 5 to 45 quintals per manzana ... No interest is charged.'),
    dict(year=2018, name='Decreto 93-2018: IHCAFE loan to growers (low prices, rust)', usd_m=77, lps_m=1900, conv=False, who='all growers who ask',
         terms='L200 per quintal oro produced in 2016/17 (≈ 8,4 $, not the "25 $" in USDA 2020); up to L1 900 M; repaid by 1,50 $ per qq retained at export',
         status='DOC', src='El Heraldo, 29 Aug 2018 (read); GAIN 2020 (about 77 M$, 5 Sep 2018)', lab='2018 · Decree 93',
         quote='Todos los caficultores que lo soliciten podrán obtener préstamos de 200 lempiras por cada quintal de café oro producido ... hasta 1,900 millones de lempiras ... retendrán 1.50 dólares ... por cada quintal oro'),
    dict(year=2018, name='Fondo para el Sector Cafetero (BANHPROVI)', lps_m=300, conv=True, who='backs refinancing and debt readjustment of growers',
         terms='L300 M in three instalments', status='DOC', src='El Heraldo, 29 Aug 2018 (read)', lab='2018 · BANHPROVI fund',
         quote='El Fondo para el Sector Cafetero ... por la cantidad de 300 millones de lempiras ... para respaldar operaciones de refinanciamiento y readecuación'),
    dict(lab='2020 · bono', year=2020, name='Bono Cafetalero (PCM 030-2020): free fertiliser', usd_m=12, conv=False, who='91,778 small and medium producers (87 %)',
         terms='25,188 t of fertiliser, producers up to 6.8 t', status='USDA', src='GAIN 2021',
         quote='In 2020, The GOH (via this program) distributed about $12million in fertilizer (25,188 MT) to 91,778 small and medium sized coffee producers'),
    dict(lab='2021 · bono', year=2021, name='Bono Cafetalero extension (PCM 031-2021)', usd_m=12.5, conv=False, who='over 91,500 producers', terms='fertiliser; plus state credit at 5 % and guarantees',
         status='USDA', src='GAIN 2021', quote='On April 13, 2021, the GOH extended the Coffee Bonus Program via Presidential decree PCM 031-2021 with an additional $12.5 million investment'),
    dict(year=2023, name='IHCAFE renovation programme 2023–2027', usd_m=None, conv=False, who='33,000 producers, 250,000 manzanas (63 % of the coffee park)',
         terms='target 7.0–7.5 million 46-kg bags', status='USDA', src='GAIN 2024',
         quote='support to 33 thousand producers, covering an area of 250 thousand blocks (63 percent of the total coffee park)'),
    dict(lab='2025 · bono ⚠', year=2025, name='Bono Cafetalero 2025', lps_m=350, conv=True, who='119,803 producers', terms='300,000 qq of fertiliser',
         status='PRESS', src='TNH (search snippet)', quote='L350 million, 119,803 producers, 300,000 qq fertiliser'),
]
DEBT = dict(when='Jun 2021', lps_m=5565, status='PRESS', src='La Tribuna, 25 Jun 2021 (search snippet)',
            quote='Growers owe banks, cooperatives and IHCAFE about L5,565 million')

# ---------------------------------------------------------------- cost benchmarks (US$ per quintal oro of 46 kg)
COSTS = [
    dict(year=2012, usd_qq=150, kind='price IHCAFE calls "favourable" (a threshold, not a cost)', status='USDA', src='GAIN 2012',
         quote='there is still an incentive to the producer since a price over US$150 per quintal (hundred pounds) is favorable'),
    dict(year=2018, usd_qq=160.5, kind='total cost, conventional coffee (PROMECAFE 2018 study: 3.49 $/kg)', status='PRESS',
         src='PROMECAFE 2018 as cited in Carpio et al., HortTechnology 33(1), 2023 (search snippet)',
         quote='A 2018 study by PROMECAFE estimated that the total cost of producing 1 kg of conventional coffee in Honduras is $3.49'),
    dict(year=2019, usd_qq=127, lo=120, kind='cost implied: producers "20 dollars below" cost at a 100–107 $/qq price', status='PRESS',
         src='La Prensa 2019, "Precios de café no cubren costo de producción"; hondurasensusmanos.info, 2 Oct 2019 (search snippets)',
         quote='the 2018-2019 season closed at 107 dollars average per quintal oro ... producers were 20 dollars below the production cost of a quintal'),
    dict(year=2019, usd_qq=135, kind='minimum price growers said they needed', status='PRESS', src='La Prensa 2019 (search snippet)',
         quote='growers needed an international price of at least US$135/qq'),
    dict(year=None, usd_qq=117, kind='average cost; margin only at 130–140 $/qq (year not given)', status='PRESS', src='El Heraldo (search snippet, undated)',
         quote='a coffee producer invests the equivalent of 117 dollars to produce a single quintal of coffee, and to obtain a profit margin requires market prices between 130 and 140 dollars per quintal'),
    dict(year=2023, usd_qq=130, kind='production cost', status='PRESS', src='La Prensa, Jan 2023 (search snippet)', quote='production cost about US$130 per quintal'),
]
# Honduran average export price, US$ per 46-kg quintal, as printed by USDA (read)
EXPORT_PRICE = [
    dict(crop='2010/11', usd_qq=248, src='GAIN 2012', quote='The average export price in the 2010/2011 harvest was US$248 per 46 kg bag'),
    dict(crop='2011/12', usd_qq=197, src='GAIN 2013', quote='The average export price in the 2011/2012 harvest was US $197 per 46-kg bag'),
    dict(crop='2012/13', usd_qq=140, src='GAIN 2014', quote='The average export price for MY 2012/2013 harvest was US $140 per 46-kg bag compared to the average price of US $201 in MY 2011/2012'),
    dict(crop='2018/19', usd_qq=106.89, src='GAIN 2020', quote='During MY 2018/19, Honduras exported to 60 countries at an average price of $106.89 per bag',
         note='bag size not stated; 106.89 $/46 kg = 2.32 $/kg matches the ~107 $/qq press figure, so read as per quintal'),
]

# ---------------------------------------------------------------- IHCAFE registry by farm size (USDA tables)
REGISTRY = {  # crop year: (farmers, ha harvested, 60-kg bags) for small, medium, large
    '2022/23': dict(small=(90522, 209202, 2907394), medium=(6126, 79764.38, 1820667), large=(629, 26764.73, 848578), src='GAIN 2024, table 1'),
    '2023/24': dict(small=(87136, 193092, 2502386), medium=(4746, 62494, 1400613), large=(539, 24511, 747355), src='GAIN 2025, table 1'),
    '2024/25': dict(small=(86895, 179271, 2627164), medium=(6359, 85040, 1661733), large=(374, 21246, 515533), src='GAIN 2026, table 1'),
}
